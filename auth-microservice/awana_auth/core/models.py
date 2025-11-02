"""
Core data models for the authentication system
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
import uuid


class AuthProvider(str, Enum):
    """Supported authentication providers"""
    ENTRAID = "entraid"
    WEBAUTHN = "webauthn"
    TOTP = "totp"
    LOCAL = "local"
    GOOGLE = "google"
    CUSTOM = "custom"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(BaseModel):
    """User model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    
    # Authentication
    provider: AuthProvider = AuthProvider.LOCAL
    provider_user_id: Optional[str] = None  # ID from external provider (e.g., EntraID)
    
    # Status
    status: UserStatus = UserStatus.ACTIVE
    is_verified: bool = False
    
    # Roles (list of role names)
    roles: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None
    
    # Additional user data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Session(BaseModel):
    """User session model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    
    # Session metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Session data
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        now = datetime.now(timezone.utc)
        expires_at = self.expires_at
        
        # Handle timezone-naive datetime from MongoDB
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        return now > expires_at
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuthResult(BaseModel):
    """Result of an authentication attempt"""
    success: bool
    user: Optional[User] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    session_id: Optional[str] = None
    error_message: Optional[str] = None
    provider: AuthProvider
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # User ID
    email: str
    roles: List[str] = Field(default_factory=list)
    session_id: str
    exp: datetime
    iat: datetime
    type: str = "access"  # access or refresh



# ===== Security Models: Permissions, Profiles, Groups =====

class PermissionModule(str, Enum):
    """Modules for permission organization"""
    ADMIN = "admin"
    VALIDATIONS = "validations"
    INTERIMAIRES = "interimaires"
    ENTREPRISES = "entreprises"
    RAPPORTS = "rapports"
    DASHBOARD = "dashboard"


class Permission(BaseModel):
    """Permission model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "gestion_utilisateurs"
    label: str  # e.g., "Gestion des utilisateurs"
    description: Optional[str] = None
    module: PermissionModule
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Profile(BaseModel):
    """Profile model - defines a set of permissions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "Admin Complet", "Lecture Seule"
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)  # List of permission IDs
    is_system: bool = False  # True for built-in profiles that cannot be deleted
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # User ID who created this profile


class Group(BaseModel):
    """Group model - users can belong to groups which have profiles"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    profile_id: Optional[str] = None  # Profile assigned to this group
    member_ids: List[str] = Field(default_factory=list)  # List of user IDs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # User ID who created this group


class CreateUserRequest(BaseModel):
    """Request model for creating a new user"""
    email: EmailStr
    username: Optional[str] = None  # Auto-generated from email if not provided
    full_name: Optional[str] = None
    password: Optional[str] = None  # If None, generate random and send email
    roles: List[str] = Field(default_factory=list)
    group_ids: List[str] = Field(default_factory=list)
    profile_id: Optional[str] = None  # Direct profile assignment
    send_invitation: bool = True  # Send email with credentials


class CreateGroupRequest(BaseModel):
    """Request model for creating a new group"""
    name: str
    description: Optional[str] = None
    profile_id: Optional[str] = None
    member_ids: List[str] = Field(default_factory=list)


class CreateProfileRequest(BaseModel):
    """Request model for creating a new profile"""
    name: str
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
