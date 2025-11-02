"""Notification domain entities"""
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class NotificationChannel(str, Enum):
    """Notification delivery channel"""
    INAPP = "inapp"
    EMAIL = "email"
    PUSH = "push"


class NotificationPriority(str, Enum):
    """Notification priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Notification entity"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    channel: NotificationChannel
    title: str
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    is_read: bool = False
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
