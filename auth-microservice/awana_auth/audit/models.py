"""
Audit log data models
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class AuditAction(str, Enum):
    """Audit action types"""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    
    # User management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_SUSPENDED = "user_suspended"
    USER_ACTIVATED = "user_activated"
    
    # Role management
    ROLE_GRANTED = "role_granted"
    ROLE_REVOKED = "role_revoked"
    ROLE_CREATED = "role_created"
    ROLE_UPDATED = "role_updated"
    ROLE_DELETED = "role_deleted"
    
    # Permission management
    PERMISSION_CREATED = "permission_created"
    PERMISSION_UPDATED = "permission_updated"
    PERMISSION_DELETED = "permission_deleted"
    
    # Access control
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    
    # Security events
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    
    # System events
    CONFIG_CHANGED = "config_changed"
    SYSTEM_ERROR = "system_error"


class AuditLog(BaseModel):
    """Audit log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Action details
    action: AuditAction
    resource_type: Optional[str] = None  # e.g., "user", "role", "permission"
    resource_id: Optional[str] = None
    
    # Actor (who performed the action)
    actor_id: Optional[str] = None  # User ID
    actor_email: Optional[str] = None
    
    # Target (who/what was affected)
    target_id: Optional[str] = None  # User ID or resource ID
    target_email: Optional[str] = None
    
    # Request metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Result
    success: bool = True
    error_message: Optional[str] = None
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
