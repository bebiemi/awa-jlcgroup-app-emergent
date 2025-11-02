"""Notification DTOs for requests and responses"""
from typing import Optional, Dict, Any
from pydantic import BaseModel
from src.domain.entities.notification import NotificationChannel, NotificationPriority


class NotificationResponse(BaseModel):
    """Notification response DTO"""
    id: str
    user_id: str
    channel: NotificationChannel
    title: str
    body: str
    priority: NotificationPriority
    is_read: bool
    action_url: Optional[str]
    metadata: Dict[str, Any]
    read_at: Optional[str]
    created_at: str


class CreateNotificationRequest(BaseModel):
    """Create notification request DTO"""
    user_id: str
    channel: NotificationChannel
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MarkNotificationsReadRequest(BaseModel):
    """Mark notifications as read request DTO"""
    notification_ids: list[str]


class NotificationListResponse(BaseModel):
    """Paginated notification list response"""
    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
