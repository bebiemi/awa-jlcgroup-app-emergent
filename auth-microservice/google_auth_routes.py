"""
Google OAuth Routes for AWANA Auth
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import secrets
from datetime import datetime, timedelta, timezone

from awana_auth.core.models import User, AuthProvider as AuthProviderEnum
from awana_auth.core.config import auth_config
from awana_auth.core.dependencies import (
    get_database,
    get_jwt_manager,
    get_session_storage,
    get_rbac_manager
)
from awana_auth.providers.google import GoogleAuthProvider
from awana_auth.session.jwt import JWTManager
from awana_auth.session.storage import SessionStorage
from awana_auth.rbac.manager import RBACManager
from awana_auth.audit.logger import AuditLogger
from awana_auth.audit.models import AuditAction
from awana_auth.utils.helpers import get_client_ip, get_user_agent
import os

logger = logging.getLogger(__name__)

# Create router
google_router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])


# ===== Pydantic Models =====

class GoogleLoginRequest(BaseModel):
    """Request to initiate Google OAuth login"""
    redirect_uri: str


class GoogleCallbackRequest(BaseModel):
    """Request for Google OAuth callback"""
    code: str
    state: str
    redirect_uri: str


# ===== Helper: Get Google Provider =====

def get_google_provider() -> GoogleAuthProvider:
    """Get configured Google OAuth provider"""
    config = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
    }
    
    if not config["client_id"] or not config["client_secret"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
        )
    
    return GoogleAuthProvider(config)


# ===== Helper: State Storage in MongoDB =====

async def save_state(db: AsyncIOMotorDatabase, state: str, data: dict):
    """Save OAuth state in MongoDB with TTL"""
    await db.oauth_states.insert_one({
        "state": state,
        "data": data,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
    })
    
    # Create TTL index if not exists
    await db.oauth_states.create_index("expires_at", expireAfterSeconds=0)


async def get_and_delete_state(db: AsyncIOMotorDatabase, state: str) -> dict:
    """Get and delete OAuth state from MongoDB"""
    doc = await db.oauth_states.find_one_and_delete({"state": state})
    if not doc:
        return None
    return doc.get("data")


# ===== Helper: Auto-create Profile in JLC DB =====

async def create_user_profile(
    db: AsyncIOMotorDatabase,
    user_id: str,
    email: str,
    full_name: str,
    profile_type: str,
    picture: str = None
):
    """
    Auto-create user profile in jlc_db if it doesn't exist
    This ensures Google OAuth users have a profile in the main application
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


# ===== Routes =====

@google_router.post("/login")
async def google_login(
    request: Request,
    login_request: GoogleLoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Initiate Google OAuth login flow
    
    Returns the authorization URL to redirect the user to
    """
    try:
        provider = get_google_provider()
        
        # Generate CSRF state token
        state = secrets.token_urlsafe(32)
        
        # Store state in MongoDB (with 10 min expiry)
        await save_state(db, state, {
            "redirect_uri": login_request.redirect_uri,
            "ip": get_client_ip(request),
            "user_agent": get_user_agent(request)
        })
        
        # Get authorization URL
        auth_url = provider.get_authorization_url(
            state=state,
            redirect_uri=login_request.redirect_uri
        )
        
        logger.info(f"Google OAuth login initiated from IP: {get_client_ip(request)}")
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    
    except ValueError as e:
        logger.error(f"Google OAuth configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error initiating Google login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )


@google_router.post("/callback")
async def google_callback(
    request: Request,
    callback_request: GoogleCallbackRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """
    Handle Google OAuth callback
    
    Exchanges authorization code for tokens and creates/updates user
    """
    try:
        # Verify state (CSRF protection)
        state_data = await get_and_delete_state(db, callback_request.state)
        if not state_data:
            logger.error(f"Invalid state parameter: {callback_request.state}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter"
            )
        
        logger.info(f"State verified successfully for state: {callback_request.state[:20]}...")
        
        # Get Google provider
        provider = get_google_provider()
        
        # Authenticate with Google
        auth_result = await provider.authenticate({
            "code": callback_request.code,
            "redirect_uri": callback_request.redirect_uri
        })
        
        # Check if user exists
        users_collection = db.users
        existing_user = await users_collection.find_one({
            "provider": "google",
            "provider_user_id": auth_result.metadata["google_id"]
        })
        
        if existing_user:
            # Update existing user
            user_id = existing_user["id"]
            await users_collection.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "full_name": auth_result.user.full_name,
                        "email": auth_result.user.email,
                        "is_verified": auth_result.user.is_verified,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Load user roles
            user_roles = await rbac_manager.get_user_roles(user_id)
            roles = [role.name for role in user_roles]
            
            logger.info(f"Existing Google user logged in: {auth_result.user.email}")
            
            # Ensure profile exists for existing users too
            await create_user_profile(
                db=db,
                user_id=user_id,
                email=auth_result.user.email,
                full_name=auth_result.user.full_name,
                profile_type=roles[0] if roles else "interim",
                picture=auth_result.metadata.get("picture")
            )
        
        else:
            # Create new user
            user_id = auth_result.user.id or secrets.token_urlsafe(16)
            
            new_user = {
                "id": user_id,
                "username": auth_result.user.username,
                "email": auth_result.user.email,
                "full_name": auth_result.user.full_name,
                "provider": "google",
                "provider_user_id": auth_result.metadata["google_id"],
                "password_hash": None,
                "is_verified": auth_result.user.is_verified,
                "status": "pending",  # Requires validation for interim/company
                "roles": [],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_login_at": None
            }
            
            await users_collection.insert_one(new_user)
            
            # Assign default role (interim by default for new Google users)
            try:
                await rbac_manager.grant_role(user_id, "interim", granted_by="system")
            except ValueError as e:
                logger.warning(f"Could not grant interim role: {e}")
            
            roles = ["interim"]
            
            logger.info(f"New Google user registered: {auth_result.user.email}")
            
            # Auto-create profile in jlc_db
            await create_user_profile(
                db=db,
                user_id=user_id,
                email=auth_result.user.email,
                full_name=auth_result.user.full_name,
                profile_type=roles[0] if roles else "interim",
                picture=auth_result.metadata.get("picture")
            )
        
        # Update last login
        await users_collection.update_one(
            {"id": user_id},
            {"$set": {"last_login_at": datetime.now(timezone.utc)}}
        )
        
        # Get full user document for session creation
        user_doc = await users_collection.find_one({"id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User not found after creation"
            )
        
        # Create User object
        user_obj = User(
            id=user_id,
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            provider=user_doc["provider"],
            provider_user_id=user_doc.get("provider_user_id"),
            is_verified=user_doc.get("is_verified", False),
            status=user_doc.get("status", "pending"),
            roles=roles
        )
        
        # Create session (with empty tokens initially)
        session = await session_storage.create_session(
            user=user_obj,
            access_token="",
            refresh_token="",
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={"provider": "google"}
        )
        
        # Generate JWT tokens with real session_id
        access_token = jwt_manager.create_access_token(
            user=user_obj,
            session_id=session.id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user=user_obj,
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
            actor_id=user_id,
            actor_email=user_obj.email,
            action=AuditAction.LOGIN_SUCCESS,
            resource_type="auth",
            resource_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={
                "provider": "google",
                "method": "oauth",
                "session_id": session.id
            }
        )
        
        # Return tokens and user info
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 minutes
            "user": {
                "id": user_id,
                "username": auth_result.user.username,
                "email": auth_result.user.email,
                "full_name": auth_result.user.full_name,
                "provider": "google",
                "provider_user_id": auth_result.metadata["google_id"],
                "status": existing_user["status"] if existing_user else "pending",
                "is_verified": auth_result.user.is_verified,
                "roles": roles,
                "picture": auth_result.metadata.get("picture"),
                "created_at": existing_user["created_at"].isoformat() if existing_user else datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_login_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google callback error: {e}", exc_info=True)
        
        # Audit log failed login
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            action=AuditAction.LOGIN_FAILED,
            actor_id=None,
            actor_email=None,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={
                "provider": "google",
                "error": str(e)
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )


@google_router.get("/status")
async def google_oauth_status():
    """Check if Google OAuth is configured"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    return {
        "configured": bool(client_id and client_secret),
        "client_id": client_id[:20] + "..." if client_id else None
    }


class CompleteRegistrationRequest(BaseModel):
    """Request to complete Google OAuth registration with role selection"""
    role: str


@google_router.post("/complete-registration")
async def complete_google_registration(
    request: Request,
    registration_data: CompleteRegistrationRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    session_storage: SessionStorage = Depends(get_session_storage),
    rbac_manager: RBACManager = Depends(get_rbac_manager)
):
    """
    Complete Google OAuth registration by selecting a role
    Called after new user authenticates with Google and selects their role
    """
    try:
        # Get current user from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.replace("Bearer ", "")
        
        # Decode token to get user_id
        try:
            payload = jwt_manager.decode_token(token)
            user_id = payload.get("sub")
        except Exception as e:
            logger.error(f"Token decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Validate role
        if registration_data.role not in ['interim', 'company']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'interim' or 'company'"
            )
        
        # Get user from database
        users_collection = db.users
        user_doc = await users_collection.find_one({"id": user_id})
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user role
        await users_collection.update_one(
            {"id": user_id},
            {
                "$set": {
                    "roles": [registration_data.role],
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Grant role in RBAC system
        try:
            # Remove old interim role if it exists
            try:
                await rbac_manager.revoke_role(user_id, "interim")
            except:
                pass
            
            # Assign new role
            await rbac_manager.grant_role(user_id, registration_data.role, granted_by="system")
        except Exception as e:
            logger.warning(f"Could not update RBAC role: {e}")
        
        # Fetch updated user
        updated_user_doc = await users_collection.find_one({"id": user_id})
        
        # Create or update profile with selected role
        await create_user_profile(
            db=db,
            user_id=user_id,
            email=updated_user_doc.get("email"),
            full_name=updated_user_doc.get("full_name"),
            profile_type=registration_data.role,
            picture=updated_user_doc.get("picture")
        )
        
        # Audit log
        audit_logger = AuditLogger(db, auth_config)
        await audit_logger.log(
            actor_id=user_id,
            actor_email=updated_user_doc.get("email"),
            action=AuditAction.USER_UPDATED,
            resource_type="user",
            resource_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            metadata={
                "provider": "google",
                "role_selected": registration_data.role
            }
        )
        
        logger.info(f"Google user {user_id} completed registration with role: {registration_data.role}")
        
        # Fetch updated user and create User object
        from awana_auth.core.models import User as UserModel
        
        # Update user object roles
        updated_user = UserModel(
            id=updated_user_doc["id"],
            username=updated_user_doc["username"],
            email=updated_user_doc["email"],
            full_name=updated_user_doc.get("full_name"),
            provider=updated_user_doc["provider"],
            provider_user_id=updated_user_doc.get("provider_user_id"),
            is_verified=updated_user_doc.get("is_verified", False),
            status=updated_user_doc.get("status", "pending"),
            roles=[registration_data.role]
        )
        
        # Get session
        session = await session_storage.get_session_by_access_token(token)
        session_id = session.id if session else secrets.token_urlsafe(32)
        
        # Generate new JWT tokens with updated role
        access_token = jwt_manager.create_access_token(
            user=updated_user,
            session_id=session_id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user=updated_user,
            session_id=session_id
        )
        
        # Return updated tokens and user info
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": user_id,
                "username": updated_user.username,
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "provider": "google",
                "provider_user_id": updated_user.provider_user_id,
                "status": updated_user.status,
                "is_verified": updated_user.is_verified,
                "roles": [registration_data.role],
                "picture": updated_user_doc.get("picture"),
                "created_at": updated_user.created_at.isoformat() if updated_user.created_at else None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_login_at": updated_user.last_login_at.isoformat() if updated_user.last_login_at else None
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete registration: {str(e)}"
        )
