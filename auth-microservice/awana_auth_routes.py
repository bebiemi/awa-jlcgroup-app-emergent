"""
FastAPI routes for AWANA Auth System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

from awana_auth.core.iam_constants import (
    IAMGroups,
    IAMProfiles,
    UserRoles,
    get_validation_type_for_role,
)
from awana_auth.core.models import User, UserStatus, AuthProvider as AuthProviderEnum
from awana_auth.core.location_models import Validation, ValidationStatus
from awana_auth.core.config import auth_config
from awana_auth.core.dependencies import (
    get_current_user,
    get_database,
    get_jwt_manager,
    get_session_storage,
    get_rbac_manager
)
from awana_auth.core.iam_constants import IAMGroups, UserRoles, get_validation_type_for_role
from awana_auth.dependencies.permission_dependencies import (
    require_permission,
    require_any_permission,
    require_all_permissions
)
from awana_auth.providers.entraid import EntraIDProvider
from awana_auth.session.jwt import JWTManager
from awana_auth.session.storage import SessionStorage
from awana_auth.rbac.manager import RBACManager
from awana_auth.rbac.models import Role, Permission, UserRole
from awana_auth.audit.logger import AuditLogger
from awana_auth.audit.models import AuditAction
from awana_auth.utils.helpers import get_client_ip, get_user_agent
from awana_auth.utils.config_helpers import cfg
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

# Config-driven constants
USER_STATUS_PENDING = cfg.get_pending_status()
VALIDATION_STATUS_PENDING = cfg.get_validation_status("pending")
VALIDATION_STATUS_APPROVED = cfg.get_validation_status("approved")
VALIDATION_TYPE_COMPANY = cfg.get_validation_type("company")
VALIDATION_TYPE_COLLABORATOR = cfg.get_validation_type("collaborator")


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
    Supports interim, company, and collaborator types
    """
    import uuid
    
    # Determine validation type based on registration data
    # Priority: 1) company_name provided → company validation type
    #           2) collaborator email → collaborator validation type
    #           3) assigned role → use role
    if register_data.company_name:
        # Company registration takes priority even if email is @jlcgroup.com
        validation_type = VALIDATION_TYPE_COMPANY
    elif user.is_collaborator:
        validation_type = VALIDATION_TYPE_COLLABORATOR
    else:
        # For non-collaborators, use the assigned role mapped to a validation type
        base_role = user.roles[0] if user.roles else UserRoles.CANDIDAT
        validation_type = get_validation_type_for_role(base_role)
    
    # Extraire les informations du représentant légal pour les entreprises
    representant_legal_nom = ""
    representant_legal_email = ""
    has_existing_representant = False
    existing_representant_user_id = None
    existing_representant_entreprises = []
    
    if validation_type == VALIDATION_TYPE_COMPANY:
        # Le représentant légal peut être fourni explicitement ou c'est l'utilisateur lui-même
        representant_legal_nom = register_data.legal_representative or register_data.full_name
        representant_legal_email = register_data.email
        
        # Détecter si ce représentant existe déjà
        from services.representant_detection_service import detect_existing_representant
        detection = await detect_existing_representant(
            nom=representant_legal_nom,
            email=representant_legal_email,
            db=db,
            exclude_user_id=user.id
        )
        
        if detection["found"]:
            has_existing_representant = True
            existing_representant_user_id = detection["user_id"]
            existing_representant_entreprises = [e["id"] for e in detection["entreprises"]]
            logger.warning(f"⚠️ Représentant légal existant détecté: {representant_legal_nom} ({representant_legal_email})")
            logger.warning(f"   Entreprises liées: {len(existing_representant_entreprises)}")
    
    user_status_value = user.status.value if isinstance(user.status, UserStatus) else user.status

    validation_status = (
        VALIDATION_STATUS_PENDING
        if user_status_value == cfg.get_pending_status()
        else VALIDATION_STATUS_APPROVED
    )

    validation = {
        "id": str(uuid.uuid4()),
        "user_id": user.id,
        "user_email": user.email,
        "user_full_name": register_data.full_name,
        "validation_type": validation_type,
        "status": VALIDATION_STATUS_PENDING if user_status_value == USER_STATUS_PENDING else VALIDATION_STATUS_APPROVED,
        "has_location_warning": False,
        "location_warning_message": None,
        "missing_country": None,
        "country_name": None,
        "province_name": None,
        "city_name": None,
        "district_name": None,
        "neighborhood_name": None,
        # Nouveaux champs Phase 1
        "representant_legal_nom": representant_legal_nom,
        "representant_legal_email": representant_legal_email,
        "has_existing_representant": has_existing_representant,
        "existing_representant_user_id": existing_representant_user_id,
        "existing_representant_entreprises": existing_representant_entreprises,
        "contact_confirmation": False,
        "rattachement_status": None,
        "rattachement_to_entreprise_id": None,
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

    # Mirror validation into main application DB so the admin center sees pending requests
    try:
        jlc_db = db.client.get_database("jlc_db")
        account_validation = {
            "id": validation["id"],
            "user_id": user.id,
            "user_email": user.email,
            "user_name": register_data.full_name,
            "validation_type": VALIDATION_TYPE_COMPANY if validation_type == VALIDATION_TYPE_COMPANY else validation_type,
            "status": VALIDATION_STATUS_PENDING if user_status_value == USER_STATUS_PENDING else VALIDATION_STATUS_APPROVED,
            "comment": None,
            "reviewed_by": None,
            "reviewed_by_email": None,
            "reviewed_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        await jlc_db.account_validations.insert_one(account_validation)
        logger.info(f"✅ account_validations record mirrored in jlc_db for user {user.email}")
    except Exception as mirror_error:
        logger.error(f"❌ Failed to mirror validation to jlc_db.account_validations: {mirror_error}", exc_info=True)

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
    
    admin_role = cfg.get_admin_role()
    super_admin_role = cfg.get_super_admin_role()

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
    elif profile_type in [admin_role, super_admin_role]:
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
        access_token = await jwt_manager.create_access_token(user, session_id="temp")
        refresh_token = await jwt_manager.create_refresh_token(user, session_id="temp")
        
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
        access_token = await jwt_manager.create_access_token(user, session.id)
        refresh_token = await jwt_manager.create_refresh_token(user, session.id)
        
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
            if email in admin_emails and cfg.get_admin_role() not in user.roles:
                user.roles.append(cfg.get_admin_role())
            
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
            user_roles = [cfg.get_admin_role()] if email in admin_emails else ["user"]
            
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
        access_token = await jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = await jwt_manager.create_refresh_token(
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
        
        # Verify admin credentials first
        username_match = secrets.compare_digest(login_data.username, admin_username)
        password_match = secrets.compare_digest(login_data.password, admin_password)
        
        is_admin_login = username_match and password_match
        user = None
        
        if is_admin_login:
            # Admin login - continue with existing admin logic
            pass
        else:
            # Check database for regular user
            import bcrypt
            
            # Try to find user by username or email
            user_doc = await db.users.find_one({
                "$or": [
                    {"username": login_data.username},
                    {"email": login_data.username}
                ],
                "provider": AuthProviderEnum.LOCAL.value
            }, {"_id": 0})
            
            logger.info(f"🔍 Searching for user: {login_data.username}")
            logger.info(f"👤 User found: {bool(user_doc)}")
            if user_doc:
                logger.info(f"📧 Email: {user_doc.get('email')}, Status: {user_doc.get('status')}")
            
            if user_doc and user_doc.get("password_hash"):
                logger.info(f"🔍 User found: {login_data.username}, checking password...")
                logger.info(f"📋 User status: {user_doc.get('status')}")
                logger.info(f"👥 User roles: {user_doc.get('roles')}")
                
                # Verify password
                try:
                    password_valid = bcrypt.checkpw(
                        login_data.password.encode('utf-8'),
                        user_doc["password_hash"].encode('utf-8')
                    )
                    logger.info(f"🔐 Password valid: {password_valid}")
                except Exception as e:
                    logger.error(f"❌ Password verification error: {str(e)}")
                    password_valid = False
                
                if password_valid:
                    # Check if user is active
                    user_status = user_doc.get("status")
                    active_status = cfg.get_active_status()
                    logger.info(f"👤 User status: {user_status} (expecting: {active_status})")

                    if user_status != active_status:
                        logger.warning(f"Login attempt for inactive user: {login_data.username} (status: {user_status})")
                        audit_logger = AuditLogger(db, auth_config)
                        await audit_logger.log(
                            action=AuditAction.LOGIN_FAILED,
                            actor_email=user_doc.get("email", login_data.username),
                            ip_address=get_client_ip(request),
                            user_agent=get_user_agent(request),
                            metadata={"reason": "account_inactive", "provider": "local"}
                        )
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Account is not active"
                        )
                    
                    # Valid database user login
                    user = User(**user_doc)
                    user.last_login_at = datetime.now(timezone.utc)
                    user.updated_at = datetime.now(timezone.utc)
                    
                    # Update last login time
                    await db.users.update_one(
                        {"id": user.id},
                        {"$set": {
                            "last_login_at": user.last_login_at.isoformat(),
                            "updated_at": user.updated_at.isoformat()
                        }}
                    )
                    
                    logger.info(f"Local user {user.email} logged in (database user)")
                    
                    # Load user permissions from profiles
                    user_permissions = set()
                    profile_ids = user_doc.get("profile_ids", []) or user_doc.get("profiles", [])
                    
                    if profile_ids:
                        logger.info(f"Loading permissions for {len(profile_ids)} profile(s)...")
                        
                        for profile_id in profile_ids:
                            # Find profile by ID or code
                            profile_doc = await db.profiles.find_one(
                                {"$or": [{"id": profile_id}, {"code": profile_id}]},
                                {"_id": 0, "permissions": 1, "bundles": 1}
                            )
                            
                            if profile_doc:
                                # Add direct permissions
                                direct_perms = profile_doc.get("permissions", [])
                                if direct_perms == "*":
                                    # Wildcard - get all permissions
                                    all_perms = await db.permissions.find({}, {"_id": 0, "code": 1}).to_list(1000)
                                    user_permissions.update([p["code"] for p in all_perms])
                                elif isinstance(direct_perms, list):
                                    user_permissions.update(direct_perms)
                                
                                # Add permissions from bundles
                                bundles = profile_doc.get("bundles", [])
                                if bundles:
                                    # Check permission_bundles collection (config-driven)
                                    async for bundle in db.permission_bundles.find(
                                        {"code": {"$in": bundles}},
                                        {"_id": 0, "permissions": 1}
                                    ):
                                        bundle_perms = bundle.get("permissions", [])
                                        user_permissions.update(bundle_perms)
                                    
                                    # Check capability_bundles collection (legacy)
                                    async for bundle in db.capability_bundles.find(
                                        {"$or": [{"id": {"$in": bundles}}, {"code": {"$in": bundles}}]},
                                        {"_id": 0, "permissions": 1, "permission_ids": 1}
                                    ):
                                        if "permissions" in bundle:
                                            user_permissions.update(bundle.get("permissions", []))
                                        elif "permission_ids" in bundle:
                                            # Resolve IDs to codes
                                            perm_ids = bundle.get("permission_ids", [])
                                            async for perm in db.permissions.find(
                                                {"id": {"$in": perm_ids}},
                                                {"_id": 0, "code": 1}
                                            ):
                                                user_permissions.add(perm["code"])
                        
                        # Update user object with permissions
                        user.permissions = list(user_permissions)
                        user.profile_ids = profile_ids
                        logger.info(f"✅ Loaded {len(user_permissions)} permissions for {user.email}")
                    else:
                        logger.warning(f"⚠️ No profiles assigned to user {user.email}")
                        user.permissions = []
                        user.profile_ids = []
            
            if not user:
                # Neither admin nor valid database user
                logger.warning(f"Failed login attempt for username: {login_data.username}")
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
        
        # Handle admin login if it's admin
        if is_admin_login:
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
                if cfg.get_admin_role() not in user.roles:
                    user.roles.append(cfg.get_admin_role())
                
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
                    roles=[cfg.get_admin_role()]
                )
                
                user_dict = user.dict()
                user_dict['created_at'] = user.created_at.isoformat()
                user_dict['updated_at'] = user.updated_at.isoformat()
                user_dict['last_login_at'] = user.last_login_at.isoformat() if user.last_login_at else None
                
                await db.users.insert_one(user_dict)
                
                # Grant admin role in RBAC system
                try:
                    await rbac_manager.grant_role(user.id, cfg.get_admin_role(), granted_by="system")
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
        access_token = await jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = await jwt_manager.create_refresh_token(
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
        access_token = await jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = await jwt_manager.create_refresh_token(
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
    Automatically assigns IAM groups based on email domain:
    - Collaborator domains (@jlcgroup.*) -> grp.collaborateur (requires validation)
    - Public domains -> grp.candidat (immediate access)
    """
    import bcrypt
    from awana_auth.services.email_domain_service import EmailDomainService
    
    try:
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
        
        # Verify email domain using our new service
        email_service = EmailDomainService(db)
        is_collaborator = await email_service.is_collaborator_email(register_data.email)
        
        # Hash password
        password_hash = bcrypt.hashpw(
            register_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Detect company intent even if company_name is whitespace or only supporting fields are provided
        raw_company_name = (register_data.company_name or "").strip()
        is_company_registration = bool(raw_company_name or register_data.legal_representative or register_data.nif)

        # Determine user status and role based on registration type
        if is_company_registration:
            # Company registration -> needs validation
            user_status = UserStatus.PENDING
            assigned_role = UserRoles.COMPANY
            iam_group_code = IAMGroups.COMPANY
            register_data.company_name = raw_company_name or register_data.full_name  # ensure a non-empty value is persisted
            logger.info(f"Company registration detected for {register_data.email} ({register_data.company_name}) - validation required")
        elif is_collaborator:
            # Collaborator email -> needs validation
            user_status = UserStatus.PENDING
            assigned_role = UserRoles.COLLABORATEUR
            iam_group_code = IAMGroups.COLLABORATEUR
            logger.info(f"Collaborator registration detected for {register_data.email} - validation required")
        else:
            # Public email -> candidat with immediate access
            user_status = UserStatus.ACTIVE
            assigned_role = UserRoles.CANDIDAT
            iam_group_code = IAMGroups.CANDIDAT
            logger.info(f"Candidat registration detected for {register_data.email} - immediate access granted")
        
        # Create new user
        user = User(
            username=register_data.username,
            email=register_data.email,
            full_name=register_data.full_name,
            provider=AuthProviderEnum.LOCAL,
            provider_user_id=f"local_{register_data.username}",
            password_hash=password_hash,
            status=user_status,
            roles=[assigned_role],  # Assign role based on email domain
            is_collaborator=is_collaborator,
        )
        
        # Save user to database
        user_dict = user.dict()
        user_dict['created_at'] = user.created_at.isoformat()
        user_dict['updated_at'] = user.updated_at.isoformat()
        user_dict['last_login_at'] = user.last_login_at.isoformat() if user.last_login_at else None
        
        await db.users.insert_one(user_dict)
        logger.info(f"✅ User created: {user.email} with status {user_status}")
        
        # Assign to appropriate IAM group
        target_group = await db.iam_groups.find_one({"code": iam_group_code})
        if target_group:
            # Check if user is already in the group
            existing_membership = await db.iam_groups.find_one({
                "id": target_group["id"],
                "user_ids": user.id
            })
            
            if not existing_membership:
                # Add user to group's user_ids array
                await db.iam_groups.update_one(
                    {"id": target_group["id"]},
                    {
                        "$addToSet": {"user_ids": user.id},
                        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                    }
                )
                logger.info(f"✅ User {user.email} assigned to IAM group: {iam_group_code}")
            else:
                logger.info(f"ℹ️ User {user.email} already in group {iam_group_code}")
        else:
            logger.warning(f"⚠️ IAM group '{iam_group_code}' not found! User has no group assignment.")
        
        # Grant legacy role in RBAC system (for backward compatibility)
        try:
            await rbac_manager.grant_role(user.id, assigned_role, granted_by="system")
            logger.info(f"✅ Legacy RBAC role '{assigned_role}' granted to {user.email}")
        except ValueError as e:
            logger.warning(f"Could not grant legacy role {assigned_role}: {e}")
        
        # Create session
        session = await session_storage.create_session(
            user=user,
            access_token="",
            refresh_token="",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={
                "provider": "local", 
                "registration": True,
                "role": assigned_role,
                "is_collaborator": is_collaborator
            }
        )
        
        # Create JWT tokens (company/collaborator stay restricted)
        access_token = await jwt_manager.create_access_token(
            user=user,
            session_id=session.id
        )
        
        refresh_token = await jwt_manager.create_refresh_token(
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
            metadata={
                "provider": "local", 
                "role": assigned_role,
                "is_collaborator": is_collaborator,
                "iam_group": iam_group_code,
                "status": user_status.value
            }
        )
        
        # Auto-create profile in jlc_db (align with IAM profiles instead of legacy roles)
        profile_type = cfg.get_profile_type("company") if register_data.company_name else assigned_role
        await create_user_profile_if_not_exists(
            db=db,
            user_id=user.id,
            email=user.email,
            full_name=register_data.full_name,
            profile_type=profile_type,
            picture=None
        )
        
        # Create validation record (keeps status pending for company/collaborator)
        await create_validation_record(
            db=db,
            user=user,
            register_data=register_data
        )
        
        logger.info(f"✅ Registration completed for {user.email} - Role: {assigned_role}, Status: {user_status}")
        
        # Log status message
        if user_status_value == cfg.get_active_status():
            logger.info("✅ Candidat account active - immediate access granted")
        else:
            logger.info("⚠️ Collaborator/Company account pending - manual validation required")
        
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


@auth_router.post("/promote-to-interimaire/{user_id}")
async def promote_candidat_to_interimaire(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission('users.manage'))
):
    """
    Promote a candidat to intérimaire status after contract signature
    This transitions the user from grp.candidat to grp.interimaire
    Requires: users.manage permission
    """
    try:
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is currently a candidat
        candidat_group = await db.iam_groups.find_one({"code": IAMGroups.CANDIDAT})
        if candidat_group and user_id in candidat_group.get("user_ids", []):
            # Remove from candidat group
            await db.iam_groups.update_one(
                {"id": candidat_group["id"]},
                {
                    "$pull": {"user_ids": user_id},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            logger.info(f"✅ User {user_id} removed from {IAMGroups.CANDIDAT}")
        
        # Add to interimaire group (or create if doesn't exist)
        interimaire_group = await db.iam_groups.find_one({"code": IAMGroups.INTERIMAIRE})
        if not interimaire_group:
            # Create interimaire group if doesn't exist
            import uuid
            interimaire_profile = await db.iam_profiles.find_one({"code": IAMProfiles.INTERIM_USER})
            
            interimaire_group_id = str(uuid.uuid4())
            interimaire_group = {
                "id": interimaire_group_id,
                "code": IAMGroups.INTERIMAIRE,
                "name": "Intérimaires",
                "description": "Groupe des intérimaires (après signature de contrat)",
                "profile_ids": [interimaire_profile["id"]] if interimaire_profile else [],
                "user_ids": [],
                "is_system_group": True,
                "is_protected": False,
                "parent_group_id": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.iam_groups.insert_one(interimaire_group)
            logger.info(f"✅ Created {IAMGroups.INTERIMAIRE} group")
        
        # Add user to interimaire group
        if user_id not in interimaire_group.get("user_ids", []):
            await db.iam_groups.update_one(
                {"id": interimaire_group["id"]},
                {
                    "$addToSet": {"user_ids": user_id},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            logger.info(f"✅ User {user_id} added to {IAMGroups.INTERIMAIRE}")
        
        # Update user's roles array
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "roles": [UserRoles.INTERIM],  # Update legacy role
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.ROLE_GRANTED,
            actor_id=current_user.id,
            actor_email=current_user.email,
            target_id=user_id,
            target_email=user.get("email"),
            metadata={
                "action": "promote_candidat_to_interimaire",
                "from_group": IAMGroups.CANDIDAT,
                "to_group": IAMGroups.INTERIMAIRE
            }
        )

        logger.info(f"✅ User {user_id} promoted from candidat to intérimaire")
        
        return {
            "success": True,
            "message": "User promoted to intérimaire successfully",
            "user_id": user_id,
            "new_group": IAMGroups.INTERIMAIRE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Promotion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Promotion failed: {str(e)}"
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
        new_access_token = await jwt_manager.create_access_token(user, session.id)
        new_refresh_token = await jwt_manager.create_refresh_token(user, session.id)
        
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
    current_user: User = Depends(require_permission("admin.dashboard")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get dashboard statistics for admin"""
    try:
        # Total users by status
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"status": cfg.get_active_status()})
        pending_users = await db.users.count_documents({"status": cfg.get_pending_status()})
        suspended_users = await db.users.count_documents({"status": cfg.get_suspended_status()})
        
        # Users by role
        admin_users = await db.users.count_documents({"roles": cfg.get_admin_role()})
        super_admin_users = await db.users.count_documents({"roles": cfg.get_super_admin_role()})
        interim_users = await db.users.count_documents({"roles": cfg.get_interim_role()})
        company_users = await db.users.count_documents({"roles": cfg.get_company_role()})
        agency_users = await db.users.count_documents({"roles": cfg.get_agency_role()})
        
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
                cfg.get_active_status(): active_users,
                USER_STATUS_PENDING: pending_users,
                cfg.get_suspended_status(): suspended_users
            },
            "users_by_role": {
                cfg.get_admin_role(): admin_users,
                cfg.get_super_admin_role(): super_admin_users,
                cfg.get_interim_role(): interim_users,
                cfg.get_company_role(): company_users,
                cfg.get_agency_role(): agency_users
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
    include_super_admin: bool = Query(False, description="Include super-admin users (super-admin only)"),
    current_user: User = Depends(require_permission("users.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all users (admin only)
    
    By default, super-admin users are hidden from regular admins.
    Only super-admins can see all users by setting include_super_admin=true.
    """
    query = {}
    
    if status:
        query["status"] = status.value
    
    if provider:
        query["provider"] = provider.value

    # Filter out super-admins unless caller is super-admin AND explicitly requests them
    super_admin_role = cfg.get_super_admin_role()
    is_super_admin = cfg.user_has_role(current_user.roles, super_admin_role)

    if not is_super_admin or not include_super_admin:
        # Get hidden roles from system_references
        hidden_roles = await db.system_references.find(
            {"category": "roles", "is_hidden_from_admins": True},
            {"_id": 0, "code": 1}
        ).to_list(length=None)
        
        hidden_role_codes = [role["code"] for role in hidden_roles]
        
        if hidden_role_codes:
            # Exclude users who have ANY hidden role
            query["roles"] = {"$not": {"$elemMatch": {"$in": hidden_role_codes}}}
    
    users_docs = await db.users.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(length=None)
    return [User(**doc) for doc in users_docs]


@users_router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_permission("users.read")),
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
    current_user: User = Depends(require_permission("users.edit")),
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
    
    # Auto-sync company profile if user is a company
    from awana_auth.services.company_profile_sync_service import CompanyProfileSyncService
    await CompanyProfileSyncService.sync_profile_from_user(db, user_id, update_fields)
    
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
    current_user: User = Depends(require_permission("users.delete")),
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
    
    # Archive user instead of deleting (soft delete)
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "status": cfg.get_archived_status(),
                "archived_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Delete user sessions (for archived users)
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
        user_agent=get_user_agent(request),
        details={"note": "User archived (soft delete)"}
    )
    
    return {"message": "User archived successfully"}


@auth_router.post("/admin/users/{user_id}/mfa/reset")
async def reset_user_mfa(
    user_id: str,
    request: Request,
    current_user: User = Depends(require_permission("users.reset_mfa")),
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
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all roles (DEPRECATED: Use IAM profiles instead)"""
    roles_docs = await db.roles.find({}, {"_id": 0}).to_list(length=None)
    return [Role(**doc) for doc in roles_docs]


@roles_router.post("/{user_id}/roles")
async def assign_role_to_user(
    user_id: str,
    role_data: RoleAssignRequest,
    request: Request,
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """Assign role to user (DEPRECATED: Use IAM profiles instead)"""
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
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """Revoke role from user (DEPRECATED: Use IAM profiles instead)"""
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
    sort_by: Optional[str] = Query("username", description="Field to sort by (username, email, roles, status, created_at)"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    include_super_admin: bool = Query(False, description="Include super-admin users (super-admin only)"),
    current_user: User = Depends(require_permission("users.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List all users with pagination and filters (Admin only)
    
    By default, super-admin users are hidden from regular admins.
    Only super-admins can see all users by setting include_super_admin=true.
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
        
        # Filter out super-admins unless caller is super-admin AND explicitly requests them
        super_admin_role = cfg.get_super_admin_role()
        is_super_admin = cfg.user_has_role(current_user.roles, super_admin_role)

        # Build roles filter with both role filter and hidden roles exclusion
        roles_conditions = []

        # Add role filter if specified
        if role:
            roles_conditions.append(role)

        if not is_super_admin or not include_super_admin:
            # Get hidden roles from system_references
            hidden_roles = await db.system_references.find(
                {"category": "roles", "is_hidden_from_admins": True},
                {"_id": 0, "code": 1}
            ).to_list(length=None)

            hidden_role_codes = [r["code"] for r in hidden_roles]

            if hidden_role_codes:
                # Combine role filter with hidden roles exclusion
                if role:
                    # User wants to filter by a specific role AND exclude hidden roles
                    # Check if the role is visible, then add it
                    query["roles"] = {
                        "$all": [role],  # Must contain the filtered role
                        "$not": {"$elemMatch": {"$in": hidden_role_codes}}  # Must not contain hidden roles
                    }
                else:
                    # No specific role filter, just exclude hidden roles
                    query["roles"] = {"$not": {"$elemMatch": {"$in": hidden_role_codes}}}
        elif role:
            # Super admin with role filter and include_super_admin=true
            query["roles"] = role
        
        # Count total
        total = await users_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        
        # Determine sort direction
        sort_direction = 1 if sort_order == "asc" else -1
        
        # Validate sort_by field (prevent injection)
        valid_sort_fields = ["username", "email", "status", "created_at", "roles"]
        if sort_by not in valid_sort_fields:
            sort_by = "username"
        
        # Fetch users with sorting
        cursor = users_collection.find(query, {"_id": 0, "password_hash": 0}).sort(sort_by, sort_direction).skip(skip).limit(page_size)
        users = await cursor.to_list(length=page_size)
        
        # Enrich users with their effective permissions from profiles
        for user in users:
            user_permissions = set()
            profile_ids = user.get("profile_ids", []) or user.get("profiles", [])
            
            if profile_ids:
                for profile_id in profile_ids:
                    # Find profile by ID or code
                    profile_doc = await db.profiles.find_one(
                        {"$or": [{"id": profile_id}, {"code": profile_id}]},
                        {"_id": 0, "permissions": 1, "bundles": 1, "name": 1, "code": 1}
                    )
                    
                    if profile_doc:
                        # Add direct permissions
                        direct_perms = profile_doc.get("permissions", [])
                        if direct_perms == "*":
                            # Wildcard - get all permissions
                            all_perms = await db.permissions.find({}, {"_id": 0, "code": 1}).to_list(1000)
                            user_permissions.update([p["code"] for p in all_perms])
                        elif isinstance(direct_perms, list):
                            user_permissions.update(direct_perms)
                        
                        # Add permissions from bundles
                        bundles = profile_doc.get("bundles", [])
                        if bundles:
                            # Check permission_bundles collection (config-driven)
                            async for bundle in db.permission_bundles.find(
                                {"code": {"$in": bundles}},
                                {"_id": 0, "permissions": 1}
                            ):
                                bundle_perms = bundle.get("permissions", [])
                                user_permissions.update(bundle_perms)
                            
                            # Check capability_bundles collection (legacy)
                            async for bundle in db.capability_bundles.find(
                                {"$or": [{"id": {"$in": bundles}}, {"code": {"$in": bundles}}]},
                                {"_id": 0, "permissions": 1, "permission_ids": 1}
                            ):
                                if "permissions" in bundle:
                                    user_permissions.update(bundle.get("permissions", []))
                                elif "permission_ids" in bundle:
                                    # Resolve IDs to codes
                                    perm_ids = bundle.get("permission_ids", [])
                                    async for perm in db.permissions.find(
                                        {"id": {"$in": perm_ids}},
                                        {"_id": 0, "code": 1}
                                    ):
                                        user_permissions.add(perm["code"])
            
            # Add permissions to user object
            user["effective_permissions"] = list(user_permissions)
            user["effective_permissions_count"] = len(user_permissions)
        
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
    current_user: User = Depends(require_permission("users.manage_status")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update user status (Admin only)
    Possible statuses: active, pending, suspended, deleted
    """
    try:
        new_status = status_update.get("status")
        
        valid_statuses = cfg.get_all_user_statuses()
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status invalide. Valeurs autorisées: {', '.join(valid_statuses)}"
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


@auth_router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: dict,
    request: Request,
    current_user: User = Depends(require_permission("users.edit")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update user information (Admin only)
    Allowed fields: full_name, email, roles
    """
    try:
        users_collection = db.users
        user = await users_collection.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Build update dictionary with only allowed fields
        update_data = {}
        
        if "full_name" in user_update:
            update_data["full_name"] = user_update["full_name"]
        
        if "email" in user_update:
            # Check if email already exists for another user
            new_email = user_update["email"]
            if new_email != user["email"]:
                existing = await users_collection.find_one({
                    "email": new_email,
                    "id": {"$ne": user_id}
                })
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cet email est déjà utilisé par un autre utilisateur"
                    )
            update_data["email"] = new_email
        
        if "phone" in user_update:
            update_data["phone"] = user_update["phone"]
        
        if "phone_number" in user_update:
            update_data["phone_number"] = user_update["phone_number"]
        
        if "roles" in user_update:
            # Validate roles
            valid_roles = cfg.get_all_roles()
            roles = user_update["roles"]
            if not isinstance(roles, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Les rôles doivent être une liste"
                )
            for role in roles:
                if role not in valid_roles:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Rôle invalide: {role}. Valeurs autorisées: {', '.join(valid_roles)}"
                    )
            update_data["roles"] = roles
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucune donnée à mettre à jour"
            )
        
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update user
        await users_collection.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        # Auto-sync company profile if user is a company
        from awana_auth.services.company_profile_sync_service import CompanyProfileSyncService
        await CompanyProfileSyncService.sync_profile_from_user(db, user_id, update_data)
        
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
                "updated_fields": list(update_data.keys())
            }
        )
        
        logger.info(f"User {user_id} updated by admin {current_user.id}")
        
        return {"message": "Utilisateur mis à jour avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de l'utilisateur"
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



# ============================================================================
# User Profile View Tracking
# ============================================================================

@users_router.post("/{user_id}/mark-as-viewed")
async def mark_user_as_viewed(
    user_id: str,
    current_user: User = Depends(require_permission("users.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mark a user profile as viewed (removes 'new' badge)
    Sets first_profile_view_at timestamp
    """
    users_collection = db.users
    
    # Find the user
    user = await users_collection.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    # Only update if not already viewed
    if not user.get("first_profile_view_at"):
        await users_collection.update_one(
            {"id": user_id},
            {
                "$set": {
                    "first_profile_view_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        logger.info(f"User {user_id} marked as viewed by {current_user.username}")
    
    return {
        "success": True,
        "message": "User marked as viewed",
        "user_id": user_id
    }
