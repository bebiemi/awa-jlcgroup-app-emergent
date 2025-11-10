"""
Core data models for the authentication system
"""
from datetime import datetime, timezone, timedelta
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
    ARCHIVED = "archived"  # Soft delete - scheduled for deletion


class PresenceStatus(str, Enum):
    """User presence/availability status"""
    ONLINE = "online"           # 🟢 Active and available
    AWAY = "away"              # 🟡 Inactive (15+ min no activity)
    DO_NOT_DISTURB = "do_not_disturb"  # 🔴 Do not disturb (manual)
    OFFLINE = "offline"        # ⚪ Offline (manual or 30+ min)
    INVISIBLE = "invisible"    # Hidden status


class User(BaseModel):
    """User model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    
    # Authentication
    provider: AuthProvider = AuthProvider.LOCAL
    provider_user_id: Optional[str] = None  # ID from external provider (e.g., EntraID)
    password_hash: Optional[str] = None  # Hashed password for local authentication
    
    # Status
    status: UserStatus = UserStatus.ACTIVE
    is_verified: bool = False
    
    # Roles (list of role names)
    roles: List[str] = Field(default_factory=list)
    
    # Collaborator flag
    is_collaborator: bool = False
    
    # Collaborator fields (only for collaborators)
    employee_number: Optional[str] = None  # Matricule
    department: Optional[str] = None
    job_title: Optional[str] = None
    
    # MFA Settings
    mfa_enabled: bool = False
    mfa_methods: List[str] = Field(default_factory=list)  # ['totp', 'email', 'sms']
    mfa_required: bool = False  # Forced by admin
    phone_number: Optional[str] = None
    
    # Presence/Availability Status
    presence_status: str = "online"  # PresenceStatus value
    presence_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
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



# ===== MFA Models =====

class MFAMethod(str, Enum):
    """MFA method types"""
    TOTP = "totp"
    EMAIL = "email"
    SMS = "sms"
    BACKUP = "backup"


class MFASecret(BaseModel):
    """MFA secrets storage (encrypted in DB)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    totp_secret: Optional[str] = None  # Base32 encoded secret
    backup_codes: List[str] = Field(default_factory=list)  # Hashed codes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MFASession(BaseModel):
    """Temporary session after first factor authentication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str  # Temporary token valid for 5 minutes
    available_methods: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
    verified: bool = False


class SetupTOTPRequest(BaseModel):
    """Request to setup TOTP"""
    pass  # No data needed, returns QR code


class VerifyTOTPSetupRequest(BaseModel):
    """Verify TOTP setup with code"""
    code: str = Field(min_length=6, max_length=6)


class SetupEmailOTPRequest(BaseModel):
    """Request to setup Email OTP"""
    pass  # User email already known


class SetupSMSOTPRequest(BaseModel):
    """Request to setup SMS OTP"""
    phone_number: str = Field(min_length=10, max_length=20)


class VerifySMSSetupRequest(BaseModel):
    """Verify SMS setup with code"""
    code: str = Field(min_length=6, max_length=6)


class VerifyMFARequest(BaseModel):
    """Verify MFA code during login"""
    mfa_session_token: str
    method: MFAMethod
    code: str = Field(min_length=6, max_length=6)


class MFASetupResponse(BaseModel):
    """Response after MFA setup"""
    success: bool
    method: str
    qr_code: Optional[str] = None  # Base64 image for TOTP
    secret: Optional[str] = None  # Manual entry for TOTP
    backup_codes: Optional[List[str]] = None
    message: str


class MFAStatusResponse(BaseModel):
    """User MFA status"""
    enabled: bool
    required: bool
    methods: List[str]
    phone_number: Optional[str] = None



# ============================================================================
# Presence/Status Models
# ============================================================================

class UserPresenceUpdate(BaseModel):
    """Update user presence status"""
    status: PresenceStatus
    
    
class UserPresenceResponse(BaseModel):
    """User presence status response"""
    user_id: str
    username: str
    full_name: Optional[str] = None
    presence_status: str
    presence_updated_at: datetime
    last_activity_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OnlineUsersResponse(BaseModel):
    """List of online users with their presence status"""
    users: List[UserPresenceResponse]
    total: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    permissions: List[str] = Field(default_factory=list)
