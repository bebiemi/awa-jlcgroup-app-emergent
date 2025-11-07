"""
User Presence and Status Management Routes
Handles user availability status (online, away, do not disturb, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from awana_auth.core.models import (
    User,
    UserPresenceUpdate,
    UserPresenceResponse,
    OnlineUsersResponse,
    PresenceStatus
)
from awana_auth.core.dependencies import get_current_user, get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users/presence", tags=["presence"])


@router.get("/me", response_model=UserPresenceResponse)
async def get_my_presence(
    current_user: User = Depends(lambda: get_auth_manager().get_current_user)
):
    """
    Get current user's presence status
    """
    return UserPresenceResponse(
        user_id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        presence_status=current_user.presence_status,
        presence_updated_at=current_user.presence_updated_at,
        last_activity_at=current_user.last_activity_at
    )


@router.patch("/me", response_model=UserPresenceResponse)
async def update_my_presence(
    presence_update: UserPresenceUpdate,
    auth_manager: AuthManager = Depends(get_auth_manager),
    current_user: User = Depends(lambda am=Depends(get_auth_manager): am.get_current_user)
):
    """
    Update current user's presence status
    Allows users to manually set: online, do_not_disturb, offline, invisible
    """
    try:
        users_collection = auth_manager.auth_config.auth_db.users
        
        # Update user presence
        now = datetime.now(timezone.utc)
        update_data = {
            "presence_status": presence_update.status.value,
            "presence_updated_at": now,
            "updated_at": now
        }
        
        # If setting to online, also update last_activity_at
        if presence_update.status == PresenceStatus.ONLINE:
            update_data["last_activity_at"] = now
        
        result = await users_collection.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No update made for user {current_user.id}")
        
        # Fetch updated user
        updated_user_doc = await users_collection.find_one({"id": current_user.id})
        if not updated_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"User {current_user.username} changed presence to {presence_update.status.value}")
        
        return UserPresenceResponse(
            user_id=updated_user_doc["id"],
            username=updated_user_doc["username"],
            full_name=updated_user_doc.get("full_name"),
            presence_status=updated_user_doc.get("presence_status", "online"),
            presence_updated_at=updated_user_doc.get("presence_updated_at", now),
            last_activity_at=updated_user_doc.get("last_activity_at", now)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user presence: {e}")
        raise HTTPException(status_code=500, detail="Failed to update presence status")


@router.post("/activity")
async def update_activity(
    auth_manager: AuthManager = Depends(get_auth_manager),
    current_user: User = Depends(lambda am=Depends(get_auth_manager): am.get_current_user)
):
    """
    Update user's last activity timestamp
    Called periodically by frontend to track user activity
    """
    try:
        users_collection = auth_manager.auth_config.auth_db.users
        
        now = datetime.now(timezone.utc)
        update_data = {
            "last_activity_at": now,
            "updated_at": now
        }
        
        # If user was away, set back to online automatically
        if current_user.presence_status == PresenceStatus.AWAY.value:
            update_data["presence_status"] = PresenceStatus.ONLINE.value
            update_data["presence_updated_at"] = now
        
        await users_collection.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
        
        return {"success": True, "timestamp": now}
        
    except Exception as e:
        logger.error(f"Error updating user activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to update activity")


@router.get("/online", response_model=OnlineUsersResponse)
async def get_online_users(
    auth_manager: AuthManager = Depends(get_auth_manager),
    current_user: User = Depends(lambda am=Depends(get_auth_manager): am.get_current_user)
):
    """
    Get list of online/active users with their presence status
    Excludes users with 'invisible' status
    """
    try:
        users_collection = auth_manager.auth_config.auth_db.users
        
        # Get all users except those who are invisible or suspended
        users_cursor = users_collection.find({
            "status": "active",
            "presence_status": {"$ne": PresenceStatus.INVISIBLE.value}
        })
        
        users_list = []
        async for user_doc in users_cursor:
            # Calculate if user should be considered away or offline based on activity
            last_activity = user_doc.get("last_activity_at")
            presence_status = user_doc.get("presence_status", "online")
            
            # Auto-detect away/offline based on last activity
            if last_activity:
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                elif not last_activity.tzinfo:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                inactive_duration = (now - last_activity).total_seconds() / 60  # minutes
                
                # Override status based on inactivity if not manually set to do_not_disturb
                if presence_status not in [PresenceStatus.DO_NOT_DISTURB.value, PresenceStatus.OFFLINE.value]:
                    if inactive_duration >= 30:
                        presence_status = PresenceStatus.OFFLINE.value
                    elif inactive_duration >= 15:
                        presence_status = PresenceStatus.AWAY.value
            
            users_list.append(UserPresenceResponse(
                user_id=user_doc["id"],
                username=user_doc["username"],
                full_name=user_doc.get("full_name"),
                presence_status=presence_status,
                presence_updated_at=user_doc.get("presence_updated_at", datetime.now(timezone.utc)),
                last_activity_at=user_doc.get("last_activity_at", datetime.now(timezone.utc))
            ))
        
        return OnlineUsersResponse(
            users=users_list,
            total=len(users_list)
        )
        
    except Exception as e:
        logger.error(f"Error fetching online users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch online users")


@router.get("/{user_id}", response_model=UserPresenceResponse)
async def get_user_presence(
    user_id: str,
    auth_manager: AuthManager = Depends(get_auth_manager),
    current_user: User = Depends(lambda am=Depends(get_auth_manager): am.get_current_user)
):
    """
    Get a specific user's presence status
    """
    try:
        users_collection = auth_manager.auth_config.auth_db.users
        
        user_doc = await users_collection.find_one({"id": user_id})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't show invisible users
        if user_doc.get("presence_status") == PresenceStatus.INVISIBLE.value:
            return UserPresenceResponse(
                user_id=user_doc["id"],
                username=user_doc["username"],
                full_name=user_doc.get("full_name"),
                presence_status=PresenceStatus.OFFLINE.value,
                presence_updated_at=user_doc.get("presence_updated_at", datetime.now(timezone.utc)),
                last_activity_at=user_doc.get("last_activity_at", datetime.now(timezone.utc))
            )
        
        return UserPresenceResponse(
            user_id=user_doc["id"],
            username=user_doc["username"],
            full_name=user_doc.get("full_name"),
            presence_status=user_doc.get("presence_status", "online"),
            presence_updated_at=user_doc.get("presence_updated_at", datetime.now(timezone.utc)),
            last_activity_at=user_doc.get("last_activity_at", datetime.now(timezone.utc))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user presence: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user presence")
