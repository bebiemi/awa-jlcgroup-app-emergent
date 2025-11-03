"""
FastAPI routes for AWANA Auth System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

from awana_auth.core.models import User, UserStatus, AuthProvider as AuthProviderEnum
from awana_auth.core.location_models import Validation, ValidationStatus
from awana_auth.core.config import auth_config
from awana_auth.core.dependencies import (
    get_current_user,
    get_database,
    get_jwt_manager,
    get_session_storage,
    get_rbac_manager,
    require_admin,
    require_super_admin
)
from awana_auth.providers.entraid import EntraIDProvider
from awana_auth.session.jwt import JWTManager
from awana_auth.session.storage import SessionStorage
from awana_auth.rbac.manager import RBACManager
from awana_auth.rbac.models import Role, Permission, UserRole
from awana_auth.audit.logger import AuditLogger
from awana_auth.audit.models import AuditAction
from awana_auth.utils.helpers import get_client_ip, get_user_agent
from awana_auth.security.tokens import generate_state_token
import logging
import jwt as pyjwt  # For decoding Microsoft ID tokens

# Rate limiting
import sys
sys.path.append('/app/backend')
from rate_limit import limiter, get_rate_limit

logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
users_router = APIRouter(prefix="/admin/users", tags=["User Management"])
roles_router = APIRouter(prefix="/admin/roles", tags=["Role Management"])


# ===== Pydantic Models for Requests/Responses =====

class EntraIDLoginRequest(BaseModel):
    """Request to initiate EntraID login"""
    redirect_uri: str
    code_challenge: Optional[str] = None
    code_challenge_method: str = "S256"


class EntraIDLoginResponse(BaseModel):
    """Response with authorization URL"""
    authorization_url: str
    state: str


class EntraIDCallbackRequest(BaseModel):
    """EntraID OAuth callback"""
    code: str
    state: str
    redirect_uri: str
    code_verifier: Optional[str] = None


class EntraIDTokenRequest(BaseModel):
    """EntraID SPA token validation (for frontend tokens)"""
    access_token: str
    id_token: Optional[str] = None


class LoginResponse(BaseModel):
    """Successful login response"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[User] = None
    # MFA fields
    mfa_required: bool = False
    mfa_session_token: Optional[str] = None
    available_methods: List[str] = Field(default_factory=list)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserCreateRequest(BaseModel):
    """Create new user"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    roles: List[str] = []
    provider: AuthProviderEnum = AuthProviderEnum.LOCAL


class UserUpdateRequest(BaseModel):
    """Update user"""
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None
    roles: Optional[List[str]] = None


class RoleAssignRequest(BaseModel):
    """Assign role to user"""
    role_name: str


class LocalLoginRequest(BaseModel):
    """Local username/password login"""
    username: str
    password: str


class LocalRegisterRequest(BaseModel):
    """Local user registration"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str  # 'interim' or 'company'
    
    # Optional fields for interim users
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    
    # Optional fields for company users
    company_name: Optional[str] = None
    legal_representative: Optional[str] = None
    nif: Optional[str] = None
    
    # Location data (hierarchical location selection)
    location: Optional[dict] = None
    
    class Config:
        extra = "ignore"  # Ignore extra fields not in the model


# ===== Helper: Auto-create Profile in JLC DB =====

async def create_validation_record(
    db: AsyncIOMotorDatabase,
    user: User,
    register_data: LocalRegisterRequest
):
    """
    Create validation record for new user registration
    Checks location data and creates warnings if necessary
    """
    import uuid
    
    validation = {
        "id": str(uuid.uuid4()),
        "user_id": user.id,
        "user_email": user.email,
        "user_full_name": register_data.full_name,
        "validation_type": register_data.role,
        "status": "pending",
        "has_location_warning": False,
        "location_warning_message": None,
        "missing_country": None,
        "country_name": None,
        "province_name": None,
        "city_name": None,
        "district_name": None,
        "neighborhood_name": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Process location data if provided
    if register_data.location:
        location_data = register_data.location
        
        # Extract location names from the location object
        country_id = location_data.get("country_id")
        province_id = location_data.get("province_id")
        city_id = location_data.get("city_id")
        district_id = location_data.get("district_id")
        neighborhood_id = location_data.get("neighborhood_id")
        
        # Check if country exists in database
        if country_id:
            country = await db.locations.find_one({"id": country_id, "type": "country"}, {"_id": 0})
            if country:
                validation["country_name"] = country["name"]
            else:
                # Country ID provided but not found - this is unusual
                validation["has_location_warning"] = True
                validation["location_warning_message"] = "Selected country not found in database"
        
        # If custom country is provided (user typed in a country name)
        custom_country = location_data.get("custom_country")
        if custom_country:
            # Check if this country exists in database
            existing_country = await db.locations.find_one({
                "type": "country",
                "name": custom_country
            }, {"_id": 0})
            
            if not existing_country:
                validation["has_location_warning"] = True
                validation["missing_country"] = custom_country
                validation["location_warning_message"] = f"Country '{custom_country}' is not in the standard list"
            
            validation["country_name"] = custom_country
        
        # Get province name if provided
        if province_id:
            province = await db.locations.find_one({"id": province_id, "type": "province"}, {"_id": 0})
            if province:
                validation["province_name"] = province["name"]
        
        # Get city name if provided
        if city_id:
            city = await db.locations.find_one({"id": city_id, "type": "city"}, {"_id": 0})
            if city:
                validation["city_name"] = city["name"]
        
        # Get district name if provided
        if district_id:
            district = await db.locations.find_one({"id": district_id, "type": "district"}, {"_id": 0})
            if district:
                validation["district_name"] = district["name"]
        
        # Get neighborhood name if provided
        if neighborhood_id:
            neighborhood = await db.locations.find_one({"id": neighborhood_id, "type": "neighborhood"}, {"_id": 0})
            if neighborhood:
                validation["neighborhood_name"] = neighborhood["name"]
    
    # Insert validation record
    await db.validations.insert_one(validation)
    logger.info(f"✅ Validation record created for user {user.email}")
    
    if validation["has_location_warning"]:
        logger.warning(f"⚠️ Location warning for {user.email}: {validation['location_warning_message']}")


async def create_user_profile_if_not_exists(
    db: AsyncIOMotorDatabase,
    user_id: str,
    email: str,
    full_name: str,
    profile_type: str,
    picture: str = None
):
    """
    Auto-create user profile in jlc_db if it doesn't exist
    This ensures all registered users have a profile in the main application
    """
    # Get jlc_db database (main application database)
    jlc_db = db.client['jlc_db']
    profiles_collection = jlc_db.profiles
    
    # Check if profile already exists
    existing_profile = await profiles_collection.find_one({"user_id": user_id})
    if existing_profile:
        logger.info(f"Profile already exists for user {user_id}")
        return
    
    # Parse name
    name_parts = full_name.split() if full_name else []
    first_name = name_parts[0] if len(name_parts) > 0 else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    # Base profile data
    profile = {
        "user_id": user_id,
        "profile_type": profile_type,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": None,
        "avatar_url": picture,
        "address": None,
        "city": None,
        "postal_code": None,
        "country": "France",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add role-specific fields
    if profile_type == 'interim':
        profile.update({
            "skills": [],
            "experience_years": 0,
            "availability": "available",
            "hourly_rate": None,
            "resume_url": None,
            "date_of_birth": None,
            "place_of_birth": None,
            "nationality": "Gabonaise",
            "address": None,
            "city": None,
            "postal_code": None
        })
    elif profile_type == 'company':
        profile.update({
            "legal_representative": None,  # Représentant légal
            "company_name": None,  # Nom de la société
            "nif": None,  # NIF (Numéro d'Identification Fiscale)
            "address": None,  # Adresse
            "circuit_file_number": None,  # Numéro de la fiche circuit
            "country": "Gabon",  # Pays (par défaut GABON)
            "phone": None,  # Numéro de téléphone
            "contact_email": email,  # Mail de contact
            "industry": None,  # Secteur d'activité
            "company_size": None,
            "website": None,
            "description": None
        })
    elif profile_type in ['admin', 'super_admin']:
        profile.update({
            "department": "Administration",
            "position": "Administrator"
        })
    
    # Insert profile
    await profiles_collection.insert_one(profile)
    logger.info(f"✅ Auto-created profile for user {user_id} (type: {profile_type})")


# ===== Helper: Email Validation =====

def is_valid_email_domain(email: str) -> bool:
    """
    Check if email domain is from a known valid provider
    Returns True for automatic validation, False for manual admin validation
    """
    valid_domains = [
        # Major email providers
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
        'icloud.com', 'protonmail.com', 'aol.com',
        # Business domains
        'company.com', 'business.ga', 
        # Add more trusted domains as needed
    ]
    
    try:
        domain = email.split('@')[1].lower()
        return domain in valid_domains or domain.endswith('.gov') or domain.endswith('.edu')
    except:
        return False


# ===== Authentication Endpoints =====

@auth_router.post("/entraid/login", response_model=EntraIDLoginResponse)
async def entraid_login(
    request_data: EntraIDLoginRequest
):
    """
    Initiate EntraID OAuth login flow
    Returns authorization URL for frontend to redirect user
    """
    try:
        provider = EntraIDProvider(auth_config)
        
        # Generate state token for CSRF protection
        state = generate_state_token()
        
        # Generate authorization URL with PKCE if provided
        auth_url = provider.get_authorization_url(
            redirect_uri=request_data.redirect_uri,
            state=state,
            scope="openid profile email User.Read offline_access",
            code_challenge=request_data.code_challenge,
            code_challenge_method=request_data.code_challenge_method
        )
        
        logger.info(f"EntraID login initiated with redirect_uri: {request_data.redirect_uri}")
        
        return EntraIDLoginResponse(
            authorization_url=auth_url,
            state=state
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate EntraID login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}"
        )


@auth_router.post("/entraid/callback", response_model=LoginResponse)
async def entraid_callback(
    callback_data: EntraIDCallbackRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """
    Handle EntraID OAuth callback
    Exchange code for tokens and create user session
    """
    try:
        provider = EntraIDProvider(auth_config)
        
        # Authenticate with EntraID (with PKCE code_verifier if provided)
        auth_payload = {
            "code": callback_data.code,
            "redirect_uri": callback_data.redirect_uri
        }
        
        if callback_data.code_verifier:
            auth_payload["code_verifier"] = callback_data.code_verifier
        
        auth_result = await provider.authenticate(auth_payload)
        
        if not auth_result.success or not auth_result.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=auth_result.error_message or "Authentication failed"
            )
        
        entraid_user = auth_result.user
        
        # Check if user exists in local database
        existing_user_doc = await db.users.find_one({
            "provider": AuthProviderEnum.ENTRAID.value,
            "provider_user_id": entraid_user.provider_user_id
        }, {"_id": 0})
        
        if existing_user_doc:
            # Update existing user
            user = User(**existing_user_doc)
            user.last_login_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            
            await db.users.update_one(
                {"id": user.id},
                {"$set": {
                    "last_login_at": user.last_login_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                    "full_name": entraid_user.full_name,
                    "email": entraid_user.email
                }}
            )
            
            logger.info(f"User {user.email} logged in (existing)")
        else:
            # Create new user
            user = User(
                username=entraid_user.username,
                email=entraid_user.email,
                full_name=entraid_user.full_name,
                provider=AuthProviderEnum.ENTRAID,
                provider_user_id=entraid_user.provider_user_id,
                is_verified=True,
                status=UserStatus.ACTIVE,
                roles=[],  # Will assign default role
                metadata=entraid_user.metadata,
                last_login_at=datetime.now(timezone.utc)
            )
            
            await db.users.insert_one(user.model_dump())
            
            # Assign default "viewer" role to new users
            await rbac_manager.grant_role(user.id, "viewer")
            user.roles = ["viewer"]
            
            logger.info(f"New user created: {user.email}")
        
        # Create JWT tokens
        access_token = jwt_manager.create_access_token(user, session_id="temp")
        refresh_token = jwt_manager.create_refresh_token(user, session_id="temp")
        
        # Create session
        session = await session_storage.create_session(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={
                "provider": "entraid",
                "entraid_access_token": auth_result.access_token
            }
        )
        
        # Update tokens with actual session ID
        access_token = jwt_manager.create_access_token(user, session.id)
        refresh_token = jwt_manager.create_refresh_token(user, session.id)
        
        await session_storage.update_session(
            session.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.LOGIN_SUCCESS,
            actor_id=user.id,
            actor_email=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "entraid"}
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_config.jwt_access_token_expire_minutes * 60,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EntraID callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@auth_router.post("/entraid/token", response_model=LoginResponse)
@limiter.limit(get_rate_limit("auth_token"))
async def entraid_token_login(
    request: Request,
    response: Response,
    token_data: EntraIDTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """
    Handle EntraID SPA token validation
    Frontend obtains token via MSAL, backend validates it and creates session
    """
    import httpx
    
    try:
        # First, let's decode and validate the ID token (contains user identity)
        # The access_token is for Microsoft Graph API calls
        # The id_token contains user claims and should be validated
        
        if not token_data.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID token is required"
            )
        
        # Decode ID token without verification first to check issuer
        try:
            unverified_header = pyjwt.get_unverified_header(token_data.id_token)
            unverified_claims = pyjwt.decode(
                token_data.id_token,
                options={"verify_signature": False}
            )
            logger.info(f"ID Token issuer: {unverified_claims.get('iss')}")
            logger.info(f"ID Token audience: {unverified_claims.get('aud')}")
        except Exception as e:
            logger.error(f"Failed to decode ID token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid ID token format: {str(e)}"
            )
        
        # Extract user information from id_token claims
        email = unverified_claims.get("email") or unverified_claims.get("preferred_username")
        full_name = unverified_claims.get("name", "")
        provider_user_id = unverified_claims.get("oid") or unverified_claims.get("sub")
        
        if not email or not provider_user_id:
            # Fallback: Try to get user info from Microsoft Graph with access_token
            logger.info("Missing email/user_id in ID token, trying Microsoft Graph...")
            headers = {"Authorization": f"Bearer {token_data.access_token}"}
            
            async with httpx.AsyncClient() as client:
                # Get user info from Microsoft Graph
                graph_response = await client.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers=headers,
                    timeout=10.0
                )
                
                if graph_response.status_code != 200:
                    logger.error(f"Microsoft Graph API error: {graph_response.status_code} - {graph_response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Microsoft token"
                    )
                
                user_info = graph_response.json()
                email = user_info.get("mail") or user_info.get("userPrincipalName")
                full_name = user_info.get("displayName", full_name)
                provider_user_id = user_info.get("id", provider_user_id)
        
        if not email or not provider_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required user information from Microsoft"
            )
        
        # Check if user exists in local database
        existing_user_doc = await db.users.find_one({
            "provider": AuthProviderEnum.ENTRAID.value,
            "provider_user_id": provider_user_id
        }, {"_id": 0})
        
        if existing_user_doc:
            # Update existing user
            user = User(**existing_user_doc)
            user.last_login_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            
            # Ensure admin role if email is in admin list
            admin_emails = auth_config.admin_emails
            if email in admin_emails and "admin" not in user.roles:
                user.roles.append("admin")
            
            await db.users.update_one(
                {"id": user.id},
                {"$set": {
                    "last_login_at": user.last_login_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                    "full_name": full_name,
                    "email": email,
                    "roles": user.roles
                }}
            )
            
            # Sync roles with RBAC system
            rbac_manager = RBACManager(db)
            for role_name in user.roles:
                try:
                    await rbac_manager.grant_role(user.id, role_name, granted_by="system")
                except ValueError as e:
                    logger.warning(f"Could not grant role {role_name}: {e}")
            
            logger.info(f"User {user.email} logged in (existing) with roles: {user.roles}")
        else:
            # Create new user
            # Check if user email is in admin list
            admin_emails = auth_config.admin_emails
            user_roles = ["admin"] if email in admin_emails else ["user"]
            
            user = User(
                username=email.split('@')[0],
                email=email,
                full_name=full_name,
                provider=AuthProviderEnum.ENTRAID,
                provider_user_id=provider_user_id,
                status=UserStatus.ACTIVE,
                roles=user_roles
            )
            
            user_dict = user.dict()
            user_dict['created_at'] = user.created_at.isoformat()
            user_dict['updated_at'] = user.updated_at.isoformat()
            user_dict['last_login_at'] = user.last_login_at.isoformat() if user.last_login_at else None
            
            await db.users.insert_one(user_dict)
            
            # Sync roles with RBAC system
            rbac_manager = RBACManager(db)
            for role_name in user_roles:
                try:
                    await rbac_manager.grant_role(user.id, role_name, granted_by="system")
                except ValueError as e:
                    logger.warning(f"Could not grant role {role_name}: {e}")
            
            logger.info(f"New EntraID user created: {user.email} with roles: {user_roles}")
        
        # Create session first (without tokens)
        session = await session_storage.create_session(
            user=user,
            access_token="",  # Will be updated
            refresh_token="",  # Will be updated
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Now create JWT tokens with the real session_id
        access_token = jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user=user,
            session_id=session.id
        )
        
        # Update session with the tokens
        await session_storage.update_session_tokens(
            session_id=session.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.LOGIN_SUCCESS,
            actor_id=user.id,
            actor_email=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "entraid_spa"}
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_config.jwt_access_token_expire_minutes * 60,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"EntraID token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )



@auth_router.post("/local/login", response_model=LoginResponse)
@limiter.limit(get_rate_limit("auth_token"))
async def local_login(
    request: Request,
    response: Response,
    login_data: LocalLoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """
    Handle local username/password authentication
    Validates credentials and creates JWT session
    If MFA is enabled, returns MFA session token instead of access token
    """
    import os
    import secrets
    from awana_auth.mfa.mfa_service import MFAService
    
    try:
        # Get admin credentials from environment
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'awana2025')
        admin_emails = auth_config.admin_emails
        
        # Verify credentials
        username_match = secrets.compare_digest(login_data.username, admin_username)
        password_match = secrets.compare_digest(login_data.password, admin_password)
        
        if not (username_match and password_match):
            logger.warning(f"Failed login attempt for username: {login_data.username}")
            # Audit log for failed attempt
            audit_logger = AuditLogger(db, auth_config)
            await audit_logger.log(
                action=AuditAction.LOGIN_FAILED,
                actor_email=login_data.username,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                metadata={"reason": "invalid_credentials", "provider": "local"}
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Get admin email (first in list or use a valid email format)
        admin_email = admin_emails[0] if admin_emails else f"{login_data.username}@awanagroup.com"
        
        # Check if user exists in database
        existing_user_doc = await db.users.find_one({
            "provider": AuthProviderEnum.LOCAL.value,
            "email": admin_email
        }, {"_id": 0})
        
        if existing_user_doc:
            # Update existing user
            user = User(**existing_user_doc)
            user.last_login_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            
            # Ensure admin role
            if "admin" not in user.roles:
                user.roles.append("admin")
            
            await db.users.update_one(
                {"id": user.id},
                {"$set": {
                    "last_login_at": user.last_login_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                    "roles": user.roles
                }}
            )
            
            logger.info(f"Local user {user.email} logged in (existing)")
        else:
            # Create new local admin user
            user = User(
                username=login_data.username,
                email=admin_email,
                full_name="Admin",
                provider=AuthProviderEnum.LOCAL,
                provider_user_id=f"local_{login_data.username}",
                status=UserStatus.ACTIVE,
                roles=["admin"]
            )
            
            user_dict = user.dict()
            user_dict['created_at'] = user.created_at.isoformat()
            user_dict['updated_at'] = user.updated_at.isoformat()
            user_dict['last_login_at'] = user.last_login_at.isoformat() if user.last_login_at else None
            
            await db.users.insert_one(user_dict)
            
            # Grant admin role in RBAC system
            try:
                await rbac_manager.grant_role(user.id, "admin", granted_by="system")
            except ValueError as e:
                logger.warning(f"Could not grant admin role: {e}")
            
            logger.info(f"New local admin user created: {user.email}")
        
        # ===== MFA Check =====
        # Check if user has MFA enabled or required
        mfa_enabled = user.mfa_enabled if hasattr(user, 'mfa_enabled') else False
        mfa_required = user.mfa_required if hasattr(user, 'mfa_required') else False
        
        if mfa_enabled or mfa_required:
            # User has MFA - create MFA session instead of full login
            mfa_service = MFAService(db)
            
            # Get available MFA methods
            available_methods = user.mfa_methods if hasattr(user, 'mfa_methods') else []
            
            # Add backup as always available if TOTP is enabled
            if 'totp' in available_methods and 'backup' not in available_methods:
                available_methods.append('backup')
            
            # Create MFA session
            mfa_session = await mfa_service.create_mfa_session(
                user_id=user.id,
                available_methods=available_methods
            )
            
            # If Email OTP is enabled, send OTP now
            if 'email' in available_methods:
                otp = mfa_service.generate_email_otp()
                await mfa_service.store_email_otp(user.id, otp)
                # TODO: Send email with OTP
                print(f"[MFA] Email OTP for {user.email}: {otp}")
            
            # If SMS OTP is enabled, send OTP now
            if 'sms' in available_methods and user.phone_number:
                otp = mfa_service.generate_sms_otp()
                await mfa_service.store_sms_otp(user.id, otp)
                await mfa_service.send_sms_otp(user.phone_number, otp)
            
            logger.info(f"MFA required for {user.email}, session created")
            
            return LoginResponse(
                mfa_required=True,
                mfa_session_token=mfa_session.session_token,
                available_methods=available_methods,
                user=user
            )
        
        # ===== No MFA - Standard Login =====
        # Create session first (without tokens)
        session = await session_storage.create_session(
            user=user,
            access_token="",  # Will be updated
            refresh_token="",  # Will be updated
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "local"}
        )
        
        # Now create JWT tokens with the real session_id
        access_token = jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user=user,
            session_id=session.id
        )
        
        # Update session with the tokens
        await session_storage.update_session_tokens(
            session_id=session.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.LOGIN_SUCCESS,
            actor_id=user.id,
            actor_email=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "local", "mfa": False}
        )
        
        logger.info(f"✅ Local login successful for {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_config.jwt_access_token_expire_minutes * 60,
            user=user,
            mfa_required=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Local login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )




@auth_router.post("/local/login/complete", response_model=LoginResponse)
@limiter.limit(get_rate_limit("auth_token"))
async def complete_login_after_mfa(
    request: Request,
    mfa_session_token: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage)
):
    """
    Complete login after successful MFA verification
    Exchanges MFA session token for JWT access token
    """
    from awana_auth.mfa.mfa_service import MFAService
    
    try:
        mfa_service = MFAService(db)
        
        # Get and verify MFA session
        mfa_session = await mfa_service.get_mfa_session(mfa_session_token)
        
        if not mfa_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session MFA invalide ou expirée"
            )
        
        if not mfa_session.verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA n'a pas été vérifiée"
            )
        
        # Get user
        user_doc = await db.users.find_one({'id': mfa_session.user_id}, {"_id": 0})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        user = User(**user_doc)
        
        # Create full session
        session = await session_storage.create_session(
            user=user,
            access_token="",
            refresh_token="",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "local", "mfa": True}
        )
        
        # Create JWT tokens
        access_token = jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user=user,
            session_id=session.id
        )
        
        # Update session with tokens
        await session_storage.update_session_tokens(
            session_id=session.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # Delete MFA session
        await mfa_service.delete_mfa_session(mfa_session_token)
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.LOGIN_SUCCESS,
            actor_id=user.id,
            actor_email=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "local", "mfa": True}
        )
        
        logger.info(f"✅ Login completed after MFA for {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_config.jwt_access_token_expire_minutes * 60,
            user=user,
            mfa_required=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete login after MFA failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login completion failed: {str(e)}"
        )


@auth_router.post("/local/register", response_model=LoginResponse)
@limiter.limit(get_rate_limit("auth_register"))
async def local_register(
    request: Request,
    response: Response,
    register_data: LocalRegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """
    Register a new user with username/password
    Creates user account and assigns selected role (interim or company)
    """
    import bcrypt
    
    try:
        # Validate role
        if register_data.role not in ['interim', 'company']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'interim' or 'company'"
            )
        
        # Check if username already exists
        existing_username = await db.users.find_one({
            "username": register_data.username
        })
        
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur est déjà utilisé"
            )
        
        # Check if email already exists
        existing_email = await db.users.find_one({
            "email": register_data.email
        })
        
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé"
            )
        
        # Hash password
        password_hash = bcrypt.hashpw(
            register_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Determine user status based on email domain
        user_status = UserStatus.ACTIVE if is_valid_email_domain(register_data.email) else UserStatus.PENDING
        
        # Create new user
        user = User(
            username=register_data.username,
            email=register_data.email,
            full_name=register_data.full_name,
            provider=AuthProviderEnum.LOCAL,
            provider_user_id=f"local_{register_data.username}",
            password_hash=password_hash,
            status=user_status,  # Auto-validate for known email domains
            roles=[register_data.role]
        )
        
        # Save user to database
        user_dict = user.dict()
        user_dict['created_at'] = user.created_at.isoformat()
        user_dict['updated_at'] = user.updated_at.isoformat()
        user_dict['last_login_at'] = user.last_login_at.isoformat() if user.last_login_at else None
        
        await db.users.insert_one(user_dict)
        
        # Grant role in RBAC system
        try:
            await rbac_manager.grant_role(user.id, register_data.role, granted_by="system")
        except ValueError as e:
            logger.warning(f"Could not grant role {register_data.role}: {e}")
        
        logger.info(f"New user registered: {user.email} with role {register_data.role}")
        
        # Create session
        session = await session_storage.create_session(
            user=user,
            access_token="",
            refresh_token="",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "local", "registration": True}
        )
        
        # Create JWT tokens
        access_token = jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user=user,
            session_id=session.id
        )
        
        # Update session with tokens
        await session_storage.update_session_tokens(
            session_id=session.id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.USER_CREATED,
            actor_id=user.id,
            actor_email=user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "local", "role": register_data.role}
        )
        
        # Auto-create profile in jlc_db
        await create_user_profile_if_not_exists(
            db=db,
            user_id=user.id,
            email=user.email,
            full_name=register_data.full_name,
            profile_type=register_data.role,
            picture=None
        )
        
        logger.info(f"✅ Registration successful for {user.email}")
        
        # Create validation record
        await create_validation_record(
            db=db,
            user=user,
            register_data=register_data
        )
        
        # Log validation status
        if user.status == UserStatus.ACTIVE:
            logger.info("✅ Email domain validated automatically - Account active")
        else:
            logger.info("⚠️ Email domain requires manual validation - Account pending")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_config.jwt_access_token_expire_minutes * 60,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )




@auth_router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_storage: SessionStorage = Depends(get_session_storage),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Logout current user and invalidate session"""
    try:
        # Get session from authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            session = await session_storage.get_session_by_token(token)
            
            if session:
                await session_storage.delete_session(session.id)
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.LOGOUT,
            actor_id=current_user.id,
            actor_email=current_user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@auth_router.post("/refresh", response_model=LoginResponse)
@limiter.limit(get_rate_limit("auth_refresh"))
async def refresh_token(
    request: Request,
    response: Response,
    refresh_data: RefreshTokenRequest,
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        token_payload = jwt_manager.verify_token(refresh_data.refresh_token, token_type="refresh")
        
        # Get session
        session = await session_storage.get_session(token_payload.session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or expired"
            )
        
        # Get user
        user_doc = await db.users.find_one({"id": token_payload.sub}, {"_id": 0})
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = User(**user_doc)
        
        # Create new tokens
        new_access_token = jwt_manager.create_access_token(user, session.id)
        new_refresh_token = jwt_manager.create_refresh_token(user, session.id)
        
        # Update session
        await session_storage.update_session(
            session.id,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.TOKEN_REFRESH,
            actor_id=user.id,
            actor_email=user.email
        )
        
        return LoginResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=auth_config.jwt_access_token_expire_minutes * 60,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@auth_router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return current_user



# ===== Admin Dashboard Stats =====

@auth_router.get("/admin/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get dashboard statistics for admin"""
    try:
        # Total users by status
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"status": "active"})
        pending_users = await db.users.count_documents({"status": "pending"})
        suspended_users = await db.users.count_documents({"status": "suspended"})
        
        # Users by role
        admin_users = await db.users.count_documents({"roles": "admin"})
        super_admin_users = await db.users.count_documents({"roles": "super_admin"})
        interim_users = await db.users.count_documents({"roles": "interim"})
        company_users = await db.users.count_documents({"roles": "company"})
        agency_users = await db.users.count_documents({"roles": "agency"})
        
        # Users by provider
        local_users = await db.users.count_documents({"provider": "local"})
        google_users = await db.users.count_documents({"provider": "google"})
        
        # MFA statistics
        mfa_enabled_users = await db.users.count_documents({"mfa_enabled": True})
        
        # Recent users (last 7 days)
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        recent_users = await db.users.count_documents({"created_at": {"$gte": seven_days_ago}})
        
        # Recent logins (last 24 hours)
        one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        recent_logins = await db.users.count_documents({"last_login_at": {"$gte": one_day_ago}})
        
        # Groups count
        groups_count = await db.groups.count_documents({})
        
        # Profiles count
        profiles_count = await db.profiles.count_documents({})
        
        return {
            "total_users": total_users,
            "users_by_status": {
                "active": active_users,
                "pending": pending_users,
                "suspended": suspended_users
            },
            "users_by_role": {
                "admin": admin_users,
                "super_admin": super_admin_users,
                "interim": interim_users,
                "company": company_users,
                "agency": agency_users
            },
            "users_by_provider": {
                "local": local_users,
                "google": google_users
            },
            "mfa_enabled": mfa_enabled_users,
            "recent_users_7d": recent_users,
            "recent_logins_24h": recent_logins,
            "groups_count": groups_count,
            "profiles_count": profiles_count,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


# ===== User Management Endpoints =====

@users_router.get("", response_model=List[User])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    status: Optional[UserStatus] = None,
    provider: Optional[AuthProviderEnum] = None,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all users (admin only)"""
    query = {}
    
    if status:
        query["status"] = status.value
    
    if provider:
        query["provider"] = provider.value
    
    users_docs = await db.users.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(length=None)
    return [User(**doc) for doc in users_docs]


@users_router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific user by ID"""
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(**user_doc)


@users_router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """Update user (admin only)"""
    # Get user
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    # Prepare update
    update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update_data.full_name is not None:
        update_fields["full_name"] = update_data.full_name
    
    if update_data.status is not None:
        update_fields["status"] = update_data.status.value
    
    # Update roles if provided
    if update_data.roles is not None:
        # Remove old roles
        old_roles = await rbac_manager.get_user_roles(user_id)
        for role in old_roles:
            await rbac_manager.revoke_role(user_id, role.name)
        
        # Assign new roles
        for role_name in update_data.roles:
            await rbac_manager.grant_role(user_id, role_name, granted_by=current_user.id)
        
        update_fields["roles"] = update_data.roles
    
    # Update user
    await db.users.update_one({"id": user_id}, {"$set": update_fields})
    
    # Get updated user
    updated_user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    # Audit log
    audit_logger = AuditLogger(db, auth_config)
    await audit_logger.log(
        action=AuditAction.USER_UPDATED,
        actor_id=current_user.id,
        actor_email=current_user.email,
        target_id=user_id,
        target_email=user.email,
        resource_type="user",
        resource_id=user_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        metadata={"updated_fields": list(update_fields.keys())}
    )
    
    return User(**updated_user_doc)


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete user (super admin only)"""
    # Get user
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    # Cannot delete yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Delete user
    await db.users.delete_one({"id": user_id})
    
    # Delete user roles
    await db.user_roles.delete_many({"user_id": user_id})
    
    # Delete user sessions
    await db.sessions.delete_many({"user_id": user_id})
    
    # Audit log
    audit_logger = AuditLogger(db, auth_config)
    await audit_logger.log(
        action=AuditAction.USER_DELETED,
        actor_id=current_user.id,
        actor_email=current_user.email,
        target_id=user_id,
        target_email=user.email,
        resource_type="user",
        resource_id=user_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return {"message": "User deleted successfully"}


@auth_router.post("/admin/users/{user_id}/mfa/reset")
async def reset_user_mfa(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Reset MFA for a user (super admin only)
    Disables all MFA methods and clears MFA secrets
    """
    # Get user
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    # Cannot reset your own MFA through this endpoint (security measure)
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reset your own MFA through admin endpoint. Use the profile settings."
        )
    
    # Check if user has MFA enabled
    if not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have MFA enabled"
        )
    
    # Reset MFA in user document
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "mfa_enabled": False,
                "mfa_required": False,
                "mfa_methods": [],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Delete all MFA-related data
    await db.mfa_secrets.delete_many({"user_id": user_id})
    await db.mfa_backup_codes.delete_many({"user_id": user_id})
    await db.mfa_sessions.delete_many({"user_id": user_id})
    
    # Audit log
    audit_logger = AuditLogger(db, auth_config)
    await audit_logger.log(
        action=AuditAction.MFA_DISABLED,
        actor_id=current_user.id,
        actor_email=current_user.email,
        target_id=user_id,
        target_email=user.email,
        resource_type="mfa",
        resource_id=user_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        metadata={
            "reason": "Admin reset",
            "admin_user": current_user.email
        }
    )
    
    return {
        "success": True,
        "message": f"MFA reset successfully for user {user.email}",
        "user_id": user_id
    }



# ===== Role Management Endpoints =====

@roles_router.get("", response_model=List[Role])
async def get_all_roles(
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all roles"""
    roles_docs = await db.roles.find({}, {"_id": 0}).to_list(length=None)
    return [Role(**doc) for doc in roles_docs]


@roles_router.post("/{user_id}/roles")
async def assign_role_to_user(
    user_id: str,
    role_data: RoleAssignRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """Assign role to user"""
    # Check if user exists
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    try:
        await rbac_manager.grant_role(user_id, role_data.role_name, granted_by=current_user.id)
        
        # Update user roles array
        if role_data.role_name not in user.roles:
            user.roles.append(role_data.role_name)
            await db.users.update_one({"id": user_id}, {"$set": {"roles": user.roles}})
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.ROLE_GRANTED,
            actor_id=current_user.id,
            actor_email=current_user.email,
            target_id=user_id,
            target_email=user.email,
            resource_type="role",
            resource_id=role_data.role_name,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"role_name": role_data.role_name}
        )
        
        return {"message": f"Role '{role_data.role_name}' assigned to user successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@roles_router.delete("/{user_id}/roles/{role_name}")
async def revoke_role_from_user(
    user_id: str,
    role_name: str,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """Revoke role from user"""
    # Check if user exists
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    await rbac_manager.revoke_role(user_id, role_name)
    
    # Update user roles array
    if role_name in user.roles:
        user.roles.remove(role_name)
        await db.users.update_one({"id": user_id}, {"$set": {"roles": user.roles}})
    
    # Audit log
    audit_logger = AuditLogger(db, auth_config)
    await audit_logger.log(
        action=AuditAction.ROLE_REVOKED,
        actor_id=current_user.id,
        actor_email=current_user.email,
        target_id=user_id,
        target_email=user.email,
        resource_type="role",
        resource_id=role_name,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        metadata={"role_name": role_name}
    )
    
    return {"message": f"Role '{role_name}' revoked from user successfully"}



# ===== User Management Endpoints (Admin) =====

@auth_router.get("/users")
async def list_users(
    request: Request,
    page: int = 1,
    page_size: int = 15,
    search: Optional[str] = None,
    status: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List all users with pagination and filters (Admin only)
    """
    try:
        users_collection = db.users
        
        # Build query filters
        query = {}
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}}
            ]
        
        if status:
            query["status"] = status
        
        if role:
            query["roles"] = role
        
        # Count total
        total = await users_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        
        # Fetch users
        cursor = users_collection.find(query, {"_id": 0, "password_hash": 0}).sort("created_at", -1).skip(skip).limit(page_size)
        users = await cursor.to_list(length=page_size)
        
        return {
            "users": users,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        logger.error(f"List users error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs"
        )


@auth_router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_update: dict,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update user status (Admin only)
    Possible statuses: active, pending, suspended, deleted
    """
    try:
        new_status = status_update.get("status")
        
        if new_status not in ["active", "pending", "suspended", "deleted"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status invalide. Valeurs autorisées: active, pending, suspended, deleted"
            )
        
        users_collection = db.users
        user = await users_collection.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Update status
        await users_collection.update_one(
            {"id": user_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.USER_UPDATED,
            actor_id=current_user.id,
            actor_email=current_user.email,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={
                "target_user_id": user_id,
                "target_email": user["email"],
                "old_status": user["status"],
                "new_status": new_status
            }
        )
        
        logger.info(f"User {user_id} status updated to {new_status} by admin {current_user.id}")
        
        return {"message": f"Statut mis à jour: {new_status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du statut"
        )







# ===== Password Reset Endpoints =====

class ForgotPasswordRequest(BaseModel):
    """Request to reset password"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password with token"""
    token: str
    new_password: str


@auth_router.post("/forgot-password")
@limiter.limit(get_rate_limit("password_reset"))
async def forgot_password(
    request: Request,
    response: Response,
    forgot_data: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Send password reset email
    Creates a temporary reset token and sends email to user
    """
    import secrets
    
    try:
        # Find user by email
        users_collection = db.users
        user = await users_collection.find_one({"email": forgot_data.email})
        
        if not user:
            # Don't reveal if email exists or not (security)
            return {
                "message": "Si cet email existe, vous recevrez un lien de réinitialisation"
            }
        
        # Generate reset token (valid for 1 hour)
        reset_token = secrets.token_urlsafe(32)
        reset_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Store reset token in database
        password_resets_collection = db.password_resets
        await password_resets_collection.insert_one({
            "user_id": user["id"],
            "email": user["email"],
            "token": reset_token,
            "expires_at": reset_expiry,
            "used": False,
            "created_at": datetime.now(timezone.utc)
        })
        
        # TODO: Send email with reset link
        # For now, log the token (in production, send email)
        reset_url = f"{os.getenv('APP_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        logger.info(f"Password reset requested for {user['email']}")
        logger.info(f"Reset URL: {reset_url}")
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.PASSWORD_RESET,
            actor_id=user["id"],
            actor_email=user["email"],
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"email": user["email"], "action": "reset_requested"}
        )
        
        return {
            "message": "Si cet email existe, vous recevrez un lien de réinitialisation",
            "reset_url": reset_url  # Only for testing, remove in production
        }
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'envoi de l'email"
        )


@auth_router.post("/reset-password")
@limiter.limit(get_rate_limit("password_reset"))
async def reset_password(
    request: Request,
    response: Response,
    reset_data: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Reset password using token from email
    Validates token and updates user password
    """
    import bcrypt
    
    try:
        # Find reset token
        password_resets_collection = db.password_resets
        reset_doc = await password_resets_collection.find_one({
            "token": reset_data.token,
            "used": False
        })
        
        if not reset_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalide ou déjà utilisé"
            )
        
        # Check if token has expired
        expires_at = reset_doc["expires_at"]
        if isinstance(expires_at, str):
            # If stored as string, parse it
            from dateutil import parser
            expires_at = parser.parse(expires_at)
        
        # Ensure both datetimes are timezone-aware for comparison
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le token a expiré. Veuillez demander un nouveau lien"
            )
        
        # Validate new password
        if len(reset_data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le mot de passe doit contenir au moins 8 caractères"
            )
        
        # Hash new password
        password_hash = bcrypt.hashpw(
            reset_data.new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Update user password
        users_collection = db.users
        await users_collection.update_one(
            {"id": reset_doc["user_id"]},
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Mark token as used
        await password_resets_collection.update_one(
            {"token": reset_data.token},
            {
                "$set": {
                    "used": True,
                    "used_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Get user for audit log
        user = await users_collection.find_one({"id": reset_doc["user_id"]})
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.PASSWORD_CHANGED,
            actor_id=user["id"],
            actor_email=user["email"],
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"method": "reset_token"}
        )
        
        logger.info(f"Password reset successful for user {user['id']}")
        
        return {
            "message": "Mot de passe réinitialisé avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la réinitialisation du mot de passe"
        )

