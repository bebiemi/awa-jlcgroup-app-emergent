"""
Archive/Restore Models for User Management
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ArchiveUserRequest(BaseModel):
    """Request to archive a user"""
    reason: Optional[str] = Field(None, description="Reason for archiving the user")
    

class ArchiveUserResponse(BaseModel):
    """Response after archiving a user"""
    user_id: str
    status: str
    archived_at: str
    deletion_scheduled_at: str
    retention_days: int
    message: str


class RestoreUserRequest(BaseModel):
    """Request to restore an archived user"""
    reason: Optional[str] = Field(None, description="Reason for restoring the user")


class RestoreUserResponse(BaseModel):
    """Response after restoring a user"""
    user_id: str
    status: str
    restored_at: str
    message: str


class PurgeExpiredUsersResponse(BaseModel):
    """Response after purging expired users"""
    purged_count: int
    purged_user_ids: list[str]
    message: str


class RetentionConfigResponse(BaseModel):
    """Retention configuration"""
    retention_days: int
    source: str  # 'database' or 'yaml'
    can_override: bool
