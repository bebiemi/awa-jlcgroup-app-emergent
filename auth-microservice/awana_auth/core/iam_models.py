"""
IAM (Identity and Access Management) Models
Complete RBAC system with Users, Groups, Profiles, and Permissions
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid
import re


class PermissionScope(str, Enum):
    """Scope of a permission"""
    SYSTEM = "system"           # System-level permissions
    ORGANIZATION = "organization"  # Organization-level
    TEAM = "team"               # Team-level
    PERSONAL = "personal"       # Personal data only
    GLOBAL = "global"           # Global scope
    OWN = "own"                 # User's own data only


class PermissionAction(str, Enum):
    """Standard CRUD + special actions"""
    ALL = "*"                   # Wildcard: All actions
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    WRITE = "write"             # Legacy: Create/Edit combined
    APPROVE = "approve"
    REJECT = "reject"
    ASSIGN = "assign"
    EXECUTE = "execute"
    EXPORT = "export"
    IMPORT = "import"
    # Extended actions for IAM migration
    MANAGE = "manage"           # Full management
    EDIT = "edit"               # Edit existing
    CONFIGURE = "configure"     # Configuration
    TEST = "test"               # Testing
    BROWSE = "browse"           # Browse/list
    PERFORM = "perform"         # Perform action
    REVIEW = "review"           # Review
    DASHBOARD = "dashboard"     # Dashboard access
    READ_CONFIG = "read_config" # Read configuration
    MANAGE_STATUS = "manage_status"  # Manage status
    RESET_MFA = "reset_mfa"     # Reset MFA
    MANAGE_TEMPLATES = "manage_templates"  # Manage templates
    READ_HISTORY = "read_history"  # Read history
    PUBLISH = "publish"         # Publish
    READ_OWN = "read_own"       # Read own data
    MANAGE_OWN = "manage_own"   # Manage own data
    # Besoins workflow actions
    SUBMIT = "submit"           # Submit besoin
    COMMENT = "comment"         # Add comment
    VALIDATE = "validate"       # Validate besoin (JLC)
    CONVERT = "convert"         # Convert (short form)
    CONVERT_TO_MISSION = "convert_to_mission"  # Convert besoin to mission


class Permission(BaseModel):
    """
    Atomic permission unit
    Format: resource:action:scope (e.g., "missions:create:organization")
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str = Field(..., min_length=3, max_length=100, description="Code unique (ex: missions.create, iam.profiles.manage)")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    scope: str = Field(default="organization", min_length=1, max_length=50)
    
    # Metadata
    is_system: bool = False  # Protected system permission
    category: str = "general"  # For UI grouping
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """
        Valide que le code respecte le pattern:
        - Caractères autorisés: a-z, 0-9, points, underscores
        - Format: resource.action ou resource.subresource.action
        - Exemples valides: missions.create, iam.profiles.manage, system.config.read
        """
        if not v or not v.strip():
            raise ValueError("Le code ne peut pas être vide")
        
        # Pattern: segments séparés par des points, chaque segment contient a-z, 0-9, underscores
        pattern = re.compile(r'^[a-z0-9_]+(\.[a-z0-9_]+)+$|^\*\.\*$')
        if not pattern.match(v):
            raise ValueError(
                f"Code invalide '{v}'. Format attendu: 'resource.action' ou 'resource.subresource.action'. "
                "Caractères autorisés: a-z, 0-9, underscore (_), point (.). Exemple: missions.create, iam.profiles.manage"
            )
        
        return v.strip().lower()
    
    @field_validator('resource', 'action')
    @classmethod
    def validate_resource_action(cls, v: str) -> str:
        """Valide que resource et action ne contiennent que des caractères valides"""
        if not v or not v.strip():
            raise ValueError("Le champ ne peut pas être vide")
        
        # Allow wildcard '*' for special permissions
        if v.strip() == '*':
            return v.strip()
        
        pattern = re.compile(r'^[a-z0-9_]+$')
        if not pattern.match(v):
            raise ValueError(
                f"Valeur invalide '{v}'. Caractères autorisés: a-z, 0-9, underscore (_), ou '*' pour wildcard"
            )
        
        return v.strip().lower()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Profile(BaseModel):
    """
    Profile = Collection of permissions grouped by business function
    Can be assigned to Users or Groups
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Unique identifier (e.g., "admin", "hr_manager")
    name: str  # Display name
    description: Optional[str] = None
    
    # Permissions
    permission_ids: List[str] = Field(default_factory=list)
    capability_bundle_ids: List[str] = Field(default_factory=list)  # Bundles de capacités
    
    # Computed fields (filled by API, not stored)
    effective_permission_count: Optional[int] = None
    bundle_permission_count: Optional[int] = None
    
    # System roles (built-in, protected)
    is_system_role: bool = False
    is_protected: bool = False  # Cannot be modified/deleted
    
    # Hierarchy
    priority: int = 0  # Higher = more permissive (for conflict resolution)
    
    # Metadata
    category: str = "custom"  # admin, user, custom
    color: Optional[str] = None  # For UI
    icon: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Group(BaseModel):
    """
    Group = Collection of users sharing common profiles
    Enables bulk permission management
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Unique identifier (e.g., "hr_team", "sales_department")
    name: str  # Display name
    description: Optional[str] = None
    
    # Profiles assigned to this group
    profile_ids: List[str] = Field(default_factory=list)
    
    # Members
    user_ids: List[str] = Field(default_factory=list)
    
    # System groups (protected)
    is_system_group: bool = False
    is_protected: bool = False
    
    # Hierarchy
    parent_group_id: Optional[str] = None  # For nested groups
    
    # Metadata
    organization_id: Optional[str] = None  # For multi-tenant
    team_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# Request/Response Models
# ============================================================================

class PermissionCreate(BaseModel):
    """Create new permission"""
    code: str
    name: str
    description: Optional[str] = None
    resource: str
    action: PermissionAction
    scope: PermissionScope = PermissionScope.ORGANIZATION
    category: str = "general"


class ProfileCreate(BaseModel):
    """Create new profile"""
    code: str
    name: str
    description: Optional[str] = None
    permission_ids: List[str] = Field(default_factory=list)
    category: str = "custom"
    color: Optional[str] = None
    icon: Optional[str] = None


class ProfileUpdate(BaseModel):
    """Update profile"""
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class GroupCreate(BaseModel):
    """Create new group"""
    code: str
    name: str
    description: Optional[str] = None
    profile_ids: List[str] = Field(default_factory=list)
    parent_group_id: Optional[str] = None


class GroupUpdate(BaseModel):
    """Update group"""
    name: Optional[str] = None
    description: Optional[str] = None
    profile_ids: Optional[List[str]] = None
    parent_group_id: Optional[str] = None


class UserProfileAssignment(BaseModel):
    """Assign profile directly to user"""
    profile_id: Optional[str] = None  # Single profile (for frontend compatibility)
    profile_ids: Optional[List[str]] = None  # Multiple profiles (for bulk assignment)
    notes: Optional[str] = None  # Optional notes


class UserGroupAssignment(BaseModel):
    """Assign user to groups"""
    group_id: Optional[str] = None  # Single group (for frontend compatibility)
    group_ids: Optional[List[str]] = None  # Multiple groups (for bulk assignment)
    notes: Optional[str] = None  # Optional notes


class PermissionCheckRequest(BaseModel):
    """Check if user has permission"""
    user_id: str
    permission_code: str
    resource_id: Optional[str] = None


class PermissionCheckResponse(BaseModel):
    """Permission check result"""
    has_permission: bool
    granted_by: List[str] = Field(default_factory=list)  # Profile/Group codes
    reason: Optional[str] = None


class UserPermissionsResponse(BaseModel):
    """All permissions for a user"""
    user_id: str
    direct_profiles: List[Profile] = Field(default_factory=list)
    group_profiles: List[Profile] = Field(default_factory=list)
    all_permissions: List[Permission] = Field(default_factory=list)
    groups: List[Group] = Field(default_factory=list)
