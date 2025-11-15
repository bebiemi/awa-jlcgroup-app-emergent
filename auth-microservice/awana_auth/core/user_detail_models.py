"""
User Detail Models
Extended models for user management features
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Document types"""
    ID_CARD = "id_card"
    PASSPORT = "passport"
    CV = "cv"
    DIPLOMA = "diploma"
    CONTRACT = "contract"
    PROOF_OF_ADDRESS = "proof_of_address"
    SOCIAL_SECURITY = "social_security"
    WORK_PERMIT = "work_permit"
    OTHER = "other"


class UserDocument(BaseModel):
    """User document model"""
    id: str
    user_id: str
    type: str
    name: str
    file_name: str
    file_size: int
    mime_type: str
    url: str
    verified: bool = False
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    uploaded_at: str
    metadata: Optional[Dict[str, Any]] = None


class UserDocumentCreate(BaseModel):
    """Create user document"""
    type: str
    name: str
    file_name: str
    file_size: int
    mime_type: str
    url: str
    metadata: Optional[Dict[str, Any]] = None


class UserActivity(BaseModel):
    """User activity log"""
    id: str
    user_id: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: str


class UserDetailResponse(BaseModel):
    """Extended user detail response"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    provider: str
    status: str
    roles: List[str] = []
    groups: List[Dict[str, Any]] = []
    profiles: List[Dict[str, Any]] = []
    permissions: List[str] = []
    mfa_enabled: bool = False
    mfa_method: Optional[str] = None
    is_verified: bool = False  # Email verification status
    phone: Optional[str] = None
    location: Optional[str] = None
    location_label: Optional[str] = None
    created_at: str
    updated_at: str
    last_login_at: Optional[str] = None
    last_activity_at: Optional[str] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    metadata: Optional[Dict[str, Any]] = None


class GroupAssignment(BaseModel):
    """Assign group to user"""
    group_id: str
    notes: Optional[str] = None


class ProfileAssignment(BaseModel):
    """Assign profile to user"""
    profile_id: str
    notes: Optional[str] = None


class NotificationRequest(BaseModel):
    """Send notification to user"""
    title: str
    message: str
    type: Optional[str] = "info"


class ActivityQueryParams(BaseModel):
    """Activity query parameters"""
    page: int = 1
    page_size: int = 20


class ActivityResponse(BaseModel):
    """Activity response with pagination"""
    activities: List[UserActivity]
    total: int
    page: int
    page_size: int
