"""
RBAC data models
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class Permission(BaseModel):
    """Permission model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "users:read", "blog:write", "admin:access"
    description: Optional[str] = None
    resource: str  # e.g., "users", "blog", "admin"
    action: str  # e.g., "read", "write", "delete", "access"
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Role(BaseModel):
    """Role model with hierarchical support"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "super_admin", "admin", "editor", "viewer"
    display_name: str  # e.g., "Super Administrator"
    description: Optional[str] = None
    
    # Permissions (list of permission names)
    permissions: List[str] = Field(default_factory=list)
    
    # Hierarchy: roles that this role inherits from
    inherits_from: List[str] = Field(default_factory=list)
    
    # Priority (higher priority = more powerful, for conflict resolution)
    priority: int = Field(default=0)
    
    # System role (cannot be deleted or modified)
    is_system: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserRole(BaseModel):
    """User-Role association"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role_name: str
    
    # Optional: role can be scoped to specific resources
    scope: Optional[Dict[str, Any]] = None  # e.g., {"organization_id": "123"}
    
    # Timestamps
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    granted_by: Optional[str] = None  # User ID who granted this role
    expires_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if role assignment is expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Default system roles
DEFAULT_ROLES = [
    Role(
        name="super_admin",
        display_name="Super Administrator",
        description="Full system access with all permissions",
        permissions=["*:*"],  # Wildcard: all permissions
        priority=1000,
        is_system=True
    ),
    Role(
        name="admin",
        display_name="Administrator",
        description="Administrative access to manage users and content",
        permissions=[
            "users:read", "users:write", "users.delete",
            "roles:read", "roles:write",
            "content:read", "content:write", "content:delete",
            "analytics:read",
            "audit:read"
        ],
        priority=100,
        is_system=True
    ),
    Role(
        name="editor",
        display_name="Editor",
        description="Can create and edit content",
        permissions=[
            "content:read", "content:write",
            "users:read"
        ],
        priority=50,
        is_system=True
    ),
    Role(
        name="viewer",
        display_name="Viewer",
        description="Read-only access to content",
        permissions=[
            "content:read"
        ],
        priority=10,
        is_system=True
    )
]


# Default system permissions
DEFAULT_PERMISSIONS = [
    # User management
    Permission(name="users:read", code="users.read", resource="users", action="read", description="View users"),
    Permission(name="users:write", code="users.write", resource="users", action="write", description="Create/edit users"),
Permission(name="users.delete", code="users.delete", resource="users", action="delete", description="Delete users"),
    
    # Role management
    Permission(name="roles:read", code="roles.read", resource="roles", action="read", description="View roles"),
    Permission(name="roles:write", code="roles.write", resource="roles", action="write", description="Create/edit roles"),
    Permission(name="roles:delete", code="roles.delete", resource="roles", action="delete", description="Delete roles"),
    
    # Content management
    Permission(name="content:read", code="content.read", resource="content", action="read", description="View content"),
    Permission(name="content:write", code="content.write", resource="content", action="write", description="Create/edit content"),
    Permission(name="content:delete", code="content.delete", resource="content", action="delete", description="Delete content"),
    
    # Analytics
    Permission(name="analytics:read", code="analytics.read", resource="analytics", action="read", description="View analytics"),
    
    # Audit logs
    Permission(name="audit:read", code="audit.read", resource="audit", action="read", description="View audit logs"),
    
    # Wildcard (for super admin)
    Permission(name="*:*", code="*.*", resource="*", action="*", description="All permissions"),
]
