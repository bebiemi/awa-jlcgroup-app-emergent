"""
Audit & Activity Tracking Models
Comprehensive audit trail for all important actions in the system
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    """Types of auditable actions"""
    # Besoin actions
    BESOIN_CREATED = "besoin.created"
    BESOIN_UPDATED = "besoin.updated"
    BESOIN_SUBMITTED = "besoin.submitted"
    BESOIN_ANALYSED = "besoin.analysed"
    BESOIN_CONVERTED = "besoin.converted_to_mission"
    BESOIN_PUBLISHED = "besoin.published"
    BESOIN_CLOSED = "besoin.closed"
    BESOIN_COMMENT_ADDED = "besoin.comment_added"
    
    # Mission actions
    MISSION_CREATED = "mission.created"
    MISSION_UPDATED = "mission.updated"
    MISSION_PUBLISHED = "mission.published"
    MISSION_CLOSED = "mission.closed"
    
    # User actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_ARCHIVED = "user.archived"
    USER_RESTORED = "user.restored"
    
    # Config actions
    CONFIG_UPDATED = "config.updated"
    FORM_SCHEMA_UPDATED = "form.schema_updated"
    
    # Entreprise actions
    ENTREPRISE_CREATED = "entreprise.created"
    ENTREPRISE_UPDATED = "entreprise.updated"


class AuditSeverity(str, Enum):
    """Severity level for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEvent(BaseModel):
    """Audit event record"""
    id: str
    
    # Action details
    action: AuditAction
    severity: AuditSeverity = AuditSeverity.INFO
    
    # Entity information
    entity_type: str  # "besoin", "mission", "user", "entreprise", etc.
    entity_id: str
    entity_label: Optional[str] = None  # Human-readable identifier
    
    # Actor information
    actor_id: str
    actor_name: str
    actor_role: str
    actor_type: str  # "user", "system", "api"
    
    # Context
    description: str  # Human-readable description
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional context
    
    # Changes tracking
    changes: Optional[Dict[str, Any]] = None  # Before/after values
    
    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEventCreate(BaseModel):
    """Create audit event"""
    action: AuditAction
    entity_type: str
    entity_id: str
    entity_label: Optional[str] = None
    actor_id: str
    actor_name: str
    actor_role: str
    description: str
    severity: AuditSeverity = AuditSeverity.INFO
    metadata: Dict[str, Any] = Field(default_factory=dict)
    changes: Optional[Dict[str, Any]] = None


class AuditEventResponse(BaseModel):
    """Audit event response"""
    id: str
    action: str
    severity: str
    entity_type: str
    entity_id: str
    entity_label: Optional[str] = None
    actor_id: str
    actor_name: str
    actor_role: str
    description: str
    metadata: Dict[str, Any]
    changes: Optional[Dict[str, Any]] = None
    created_at: datetime


class AuditEventListResponse(BaseModel):
    """Paginated audit events"""
    items: List[AuditEventResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditSearchFilters(BaseModel):
    """Filters for audit event search"""
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    actor_id: Optional[str] = None
    action: Optional[str] = None
    severity: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    page_size: int = 50
