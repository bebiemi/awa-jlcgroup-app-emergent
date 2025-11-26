"""Notification routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from src.presentation.dependencies import get_database, get_current_user, require_admin
from src.application.dtos.notification_dtos import (
    NotificationResponse,
    CreateNotificationRequest,
    MarkNotificationsReadRequest,
    NotificationListResponse
)
from src.domain.entities.notification import Notification
from src.infrastructure.repositories.notification_repository import NotificationRepository
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["Notifications"])


def notification_to_response(notification: Notification) -> NotificationResponse:
    """Convert notification entity to response DTO"""
    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        channel=notification.channel,
        title=notification.title,
        body=notification.body,
        priority=notification.priority,
        is_read=notification.is_read,
        action_url=notification.action_url,
        metadata=notification.metadata,
        read_at=notification.read_at.isoformat() if notification.read_at else None,
        created_at=notification.created_at.isoformat()
    )


@router.get("", response_model=NotificationListResponse)
async def get_my_notifications(
    is_read: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's notifications"""
    repo = NotificationRepository(db)

    skip = (page - 1) * page_size
    notifications, total, unread_count = await repo.list_by_user(
        user_id=current_user['id'],
        is_read=is_read,
        skip=skip,
        limit=page_size
    )

    return NotificationListResponse(
        items=[notification_to_response(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size
    )


@router.post("/mark-read")
async def mark_notifications_read(
    request_data: MarkNotificationsReadRequest,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mark notifications as read"""
    repo = NotificationRepository(db)

    # Verify ownership of notifications
    for notif_id in request_data.notification_ids:
        notif = await repo.get_by_id(notif_id)
        if notif and notif.user_id != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark your own notifications as read"
            )

    count = await repo.mark_as_read(request_data.notification_ids)

    return {
        "message": f"{count} notifications marked as read",
        "count": count
    }


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: CreateNotificationRequest,
    current_user=Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a notification (admin only)"""
    repo = NotificationRepository(db)

    notification = Notification(
        user_id=notification_data.user_id,
        channel=notification_data.channel,
        title=notification_data.title,
        body=notification_data.body,
        priority=notification_data.priority,
        action_url=notification_data.action_url,
        metadata=notification_data.metadata
    )

    created_notification = await repo.create(notification)

    return notification_to_response(created_notification)
