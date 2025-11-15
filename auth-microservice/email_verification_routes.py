"""
Email Verification Routes
Handles email verification for new users (especially postulants/candidats)
Feature Flag: feature.validation.email
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.services.feature_flag_service import FeatureFlagService
from awana_auth.core.feature_flag_models import FeatureFlagContext
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email-verification", tags=["email-verification"])


class SendVerificationRequest(BaseModel):
    """Request to send verification email"""
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """Request to verify email with token"""
    token: str


async def send_verification_email(email: str, token: str, user_name: str):
    """
    Send verification email (placeholder - to be replaced with real email service)
    For now, just log the token
    """
    verification_link = f"http://localhost:3000/verify-email?token={token}"
    
    logger.info(f"📧 Email Verification")
    logger.info(f"   To: {email}")
    logger.info(f"   User: {user_name}")
    logger.info(f"   Token: {token}")
    logger.info(f"   Link: {verification_link}")
    logger.info(f"   Expires: 24 hours")
    
    # TODO: Replace with actual email service
    # await email_service.send(
    #     to=email,
    #     subject="Vérifiez votre adresse email - JLC Group",
    #     template="email_verification",
    #     context={
    #         "user_name": user_name,
    #         "verification_link": verification_link
    #     }
    # )
    
    return True


@router.post("/send")
async def send_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Send email verification link to current user
    Only for unverified users
    """
    # Check feature flag
    # TODO: Fix feature flag service for ROLE type
    # service = FeatureFlagService(db)
    # context = FeatureFlagContext(
    #     user_id=current_user.id,
    #     roles=current_user.roles,
    #     environment="production"
    # )
    # 
    # if not await service.is_enabled("feature.validation.email", context):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Email verification feature is not enabled"
    #     )
    
    # Check if already verified
    if current_user.is_verified:
        return {
            "message": "Email already verified",
            "is_verified": True
        }
    
    # Generate verification token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Store token in database
    await db.email_verification_tokens.insert_one({
        "token": token,
        "user_id": current_user.id,
        "email": current_user.email,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc),
        "used": False
    })
    
    # Send email in background
    background_tasks.add_task(
        send_verification_email,
        current_user.email,
        token,
        current_user.full_name or current_user.username
    )
    
    return {
        "message": "Verification email sent successfully",
        "email": current_user.email,
        "expires_in_hours": 24
    }


@router.post("/verify")
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Verify email using token from email link
    Public endpoint (no auth required)
    """
    # Find token in database
    token_doc = await db.email_verification_tokens.find_one({
        "token": request.token,
        "used": False
    })
    
    if not token_doc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    # Check if expired
    expires_at = token_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    if not expires_at.tzinfo:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Verification token has expired. Please request a new one."
        )
    
    # Mark user as verified
    result = await db.users.update_one(
        {"id": token_doc["user_id"]},
        {
            "$set": {
                "is_verified": True,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Mark token as used
    await db.email_verification_tokens.update_one(
        {"token": request.token},
        {"$set": {"used": True, "used_at": datetime.now(timezone.utc)}}
    )
    
    logger.info(f"✅ Email verified for user {token_doc['user_id']}")
    
    return {
        "message": "Email verified successfully",
        "email": token_doc["email"],
        "is_verified": True
    }


@router.get("/status")
async def get_verification_status(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get email verification status for current user
    """
    # Check feature flag
    # TODO: Fix feature flag service for ROLE type
    feature_enabled = True  # Temporarily enabled for all users
    
    # Check if there's a pending token
    pending_token = await db.email_verification_tokens.find_one({
        "user_id": current_user.id,
        "used": False,
        "expires_at": {"$gte": datetime.now(timezone.utc)}
    })
    
    return {
        "is_verified": current_user.is_verified,
        "email": current_user.email,
        "feature_enabled": feature_enabled,
        "verification_required": feature_enabled and not current_user.is_verified,
        "pending_verification": pending_token is not None,
        "can_resend": pending_token is None or (
            datetime.now(timezone.utc) - pending_token["created_at"]
        ).total_seconds() > 300  # Can resend after 5 minutes
    }


@router.post("/resend")
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Resend verification email
    Throttled to prevent spam (5 minutes cooldown)
    """
    # Check feature flag
    # TODO: Fix feature flag service for ROLE type
    # Temporarily allowing all users
    
    # Check if already verified
    if current_user.is_verified:
        return {
            "message": "Email already verified",
            "is_verified": True
        }
    
    # Check for recent verification attempts (throttling)
    recent_token = await db.email_verification_tokens.find_one({
        "user_id": current_user.id,
        "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(minutes=5)}
    })
    
    if recent_token:
        raise HTTPException(
            status_code=429,
            detail="Please wait 5 minutes before requesting another verification email"
        )
    
    # Invalidate old tokens
    await db.email_verification_tokens.update_many(
        {"user_id": current_user.id, "used": False},
        {"$set": {"used": True}}
    )
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    await db.email_verification_tokens.insert_one({
        "token": token,
        "user_id": current_user.id,
        "email": current_user.email,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc),
        "used": False
    })
    
    # Send email
    background_tasks.add_task(
        send_verification_email,
        current_user.email,
        token,
        current_user.full_name or current_user.username
    )
    
    return {
        "message": "New verification email sent",
        "email": current_user.email,
        "can_resend_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    }
