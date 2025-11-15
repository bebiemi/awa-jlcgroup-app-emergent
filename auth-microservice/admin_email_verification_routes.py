"""
Admin Email Verification Management
Allows superadmins to manually verify/unverify users for testing purposes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from pydantic import BaseModel
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/email-verification", tags=["admin-email-verification"])


class ManualVerifyRequest(BaseModel):
    """Request to manually verify/unverify a user"""
    user_id: str
    is_verified: bool
    reason: str = "Manual verification by admin"


async def is_superadmin(current_user: User, db: AsyncIOMotorDatabase) -> bool:
    """Check if user is superadmin"""
    return "super_admin" in current_user.roles or "admin" in current_user.roles


@router.post("/manual-verify")
async def manual_verify_user(
    request: ManualVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Manually verify or unverify a user's email
    Only accessible to superadmins
    Useful for testing with non-existent email addresses
    """
    # Check if current user is superadmin
    if not await is_superadmin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmins can manually verify users"
        )
    
    # Find the target user
    user = await db.users.find_one({"id": request.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {request.user_id} not found"
        )
    
    # Update verification status
    update_data = {
        "is_verified": request.is_verified,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if request.is_verified:
        update_data["verified_at"] = datetime.now(timezone.utc).isoformat()
        update_data["manual_verification"] = True
        update_data["verified_by"] = current_user.id
    else:
        # Unverify user
        update_data["verified_at"] = None
        update_data["manual_verification"] = False
    
    result = await db.users.update_one(
        {"id": request.user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user verification status"
        )
    
    # Log the action
    await db.audit_trail.insert_one({
        "action": "manual_email_verification",
        "performed_by": current_user.id,
        "performed_by_username": current_user.username,
        "target_user_id": request.user_id,
        "target_user_email": user.get("email"),
        "is_verified": request.is_verified,
        "reason": request.reason,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    action = "verified" if request.is_verified else "unverified"
    logger.info(f"✅ User {request.user_id} manually {action} by {current_user.username}")
    
    return {
        "success": True,
        "message": f"User email manually {action}",
        "user_id": request.user_id,
        "email": user.get("email"),
        "is_verified": request.is_verified
    }


@router.get("/verification-status/{user_id}")
async def get_user_verification_status(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed verification status for a user
    Only accessible to admins
    """
    if not await is_superadmin(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view user verification details"
        )
    
    user = await db.users.find_one(
        {"id": user_id},
        {
            "_id": 0,
            "id": 1,
            "email": 1,
            "is_verified": 1,
            "verified_at": 1,
            "manual_verification": 1,
            "verified_by": 1
        }
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    # Check for pending tokens
    pending_token = await db.email_verification_tokens.find_one(
        {
            "user_id": user_id,
            "used": False,
            "expires_at": {"$gte": datetime.now(timezone.utc)}
        }
    )
    
    return {
        "user_id": user["id"],
        "email": user.get("email"),
        "is_verified": user.get("is_verified", False),
        "verified_at": user.get("verified_at"),
        "manual_verification": user.get("manual_verification", False),
        "verified_by": user.get("verified_by"),
        "has_pending_token": pending_token is not None
    }
