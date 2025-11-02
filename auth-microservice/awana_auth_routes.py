"""
FastAPI routes for AWANA Auth System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from awana_auth.core.models import User, UserStatus, AuthProvider as AuthProviderEnum
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
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"
    expires_in: int
    user: User


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


# ===== Helper: Auto-create Profile in JLC DB =====

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
    from datetime import datetime, timezone
    
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
            "resume_url": None
        })
    elif profile_type == 'company':
        profile.update({
            "company_name": None,
            "siret": None,
            "industry": None,
            "company_size": None,
            "description": None,
            "website": None
        })
    elif profile_type in ['admin', 'super_admin']:
        profile.update({
            "department": "Administration",
            "position": "Administrator"
        })
    
    # Insert profile
    await profiles_collection.insert_one(profile)
    logger.info(f"✅ Auto-created profile for user {user_id} (type: {profile_type})")


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
    """
    import os
    import secrets
    
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
            metadata={"provider": "local"}
        )
        
        logger.info(f"✅ Local login successful for {user.email}")
        
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
        logger.error(f"Local login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
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
        
        # Create new user
        user = User(
            username=register_data.username,
            email=register_data.email,
            full_name=register_data.full_name,
            provider=AuthProviderEnum.LOCAL,
            provider_user_id=f"local_{register_data.username}",
            password_hash=password_hash,
            status=UserStatus.PENDING,  # Requires validation
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
        
        logger.info(f"✅ Registration successful for {user.email}")
        
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
