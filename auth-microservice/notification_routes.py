"""
Notification Routes
User notifications management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.services.notification_service import NotificationService

router = APIRouter()


async def get_current_user_info(current_user: dict) -> tuple:
    """Extract user info from current_user"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    user_name = current_user.get("full_name") or current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "full_name", current_user.username)
    if isinstance(current_user, dict):
        user_role = current_user.get("roles", [])[0] if current_user.get("roles") else "user"
    else:
        user_role = current_user.roles[0] if current_user.roles else "user"
    return user_id, user_name, user_role


@router.get("/")
async def get_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("notifications.read"))
):
    """
    Get current user's notifications
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    notification_service = NotificationService(db)
    result = await notification_service.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        page=page,
        page_size=page_size
    )
    
    return result


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_as_read(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("notifications.read"))
):
    """
    Mark a notification as read
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    notification_service = NotificationService(db)
    success = await notification_service.mark_as_read(notification_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_notifications_as_read(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("notifications.read"))
):
    """
    Mark all notifications as read for current user
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    notification_service = NotificationService(db)
    count = await notification_service.mark_all_as_read(user_id)
    
    return {"message": f"{count} notifications marked as read"}
