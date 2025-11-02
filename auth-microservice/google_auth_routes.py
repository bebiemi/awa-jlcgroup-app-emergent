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


# ===== Temporary State Storage (should use Redis in production) =====

_state_storage = {}  # In-memory storage for demo


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
        
        # Store state temporarily (with expiry)
        _state_storage[state] = {
            "redirect_uri": login_request.redirect_uri,
            "created_at": datetime.utcnow(),
            "ip": get_client_ip(request),
            "user_agent": get_user_agent(request)
        }
        
        # Clean old states (older than 10 minutes)
        cutoff = datetime.utcnow() - timedelta(minutes=10)
        _state_storage.clear()  # Simple cleanup for now
        
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
        state_data = _state_storage.get(callback_request.state)
        if not state_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state parameter"
            )
        
        # Remove used state
        del _state_storage[callback_request.state]
        
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
            "provider_user_id": auth_result.provider_data["google_id"]
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
        
        else:
            # Create new user
            user_id = auth_result.user.id or secrets.token_urlsafe(16)
            
            new_user = {
                "id": user_id,
                "username": auth_result.user.username,
                "email": auth_result.user.email,
                "full_name": auth_result.user.full_name,
                "provider": "google",
                "provider_user_id": auth_result.provider_data["google_id"],
                "password_hash": None,
                "is_verified": auth_result.user.is_verified,
                "status": "pending",  # Requires validation for interim/company
                "roles": [],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_login_at": None
            }
            
            await users_collection.insert_one(new_user)
            
            # Assign default role (need to determine based on registration context)
            # For now, assign "interim" role by default
            default_role = await rbac_manager.get_role_by_name("interim")
            if default_role:
                await rbac_manager.assign_role_to_user(user_id, default_role.id)
            
            roles = ["interim"]
            
            logger.info(f"New Google user registered: {auth_result.user.email}")
        
        # Update last login
        await users_collection.update_one(
            {"id": user_id},
            {"$set": {"last_login_at": datetime.now(timezone.utc)}}
        )
        
        # Create session
        session_id = await session_storage.create_session(
            user_id=user_id,
            user_agent=get_user_agent(request),
            ip_address=get_client_ip(request)
        )
        
        # Generate JWT tokens
        access_token = jwt_manager.create_access_token(
            user_id=user_id,
            email=auth_result.user.email,
            roles=roles,
            session_id=session_id
        )
        
        refresh_token = jwt_manager.create_refresh_token(
            user_id=user_id,
            email=auth_result.user.email,
            roles=roles,
            session_id=session_id
        )
        
        # Audit log
        audit_logger = AuditLogger(db)
        await audit_logger.log(
            user_id=user_id,
            action=AuditAction.LOGIN_SUCCESS,
            resource_type="auth",
            resource_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "provider": "google",
                "method": "oauth",
                "session_id": session_id
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
                "provider_user_id": auth_result.provider_data["google_id"],
                "status": existing_user["status"] if existing_user else "pending",
                "is_verified": auth_result.user.is_verified,
                "roles": roles,
                "picture": auth_result.provider_data.get("picture"),
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
        audit_logger = AuditLogger(db)
        await audit_logger.log(
            user_id=None,
            action=AuditAction.LOGIN_FAILED,
            resource_type="auth",
            resource_id=None,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
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
