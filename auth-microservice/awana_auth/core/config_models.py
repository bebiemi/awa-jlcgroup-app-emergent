"""
Configuration Models for Dynamic Forms and Workflow
Allows complete customization of forms, statuses, and reference data
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class FieldType(str, Enum):
    """Field types for dynamic forms"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    EMAIL = "email"
    PHONE = "phone"
    FILE = "file"


class ValidationRule(BaseModel):
    """Validation rule for a field"""
    type: str  # "required", "min_length", "max_length", "pattern", "min", "max"
    value: Optional[Union[str, int, bool]] = None
    message: Union[str, Dict[str, str]]  # Error message (string or i18n dict)


class FieldOption(BaseModel):
    """Option for select/multi-select fields"""
    value: str
    label: Dict[str, str]  # {"fr": "CDI", "en": "Permanent contract"}
    description: Optional[Dict[str, str]] = None
    active: bool = True


class FormField(BaseModel):
    """Dynamic form field configuration"""
    key: str  # Unique identifier (e.g., "titre", "description")
    type: FieldType
    label: Dict[str, str]  # i18n labels {"fr": "Titre", "en": "Title"}
    placeholder: Optional[Dict[str, str]] = None
    help_text: Optional[Dict[str, str]] = None
    required: bool = False
    default_value: Optional[Any] = None
    validations: List[ValidationRule] = Field(default_factory=list)
    options: List[FieldOption] = Field(default_factory=list)  # For select fields
    depends_on: Optional[str] = None  # Conditional display based on another field
    depends_condition: Optional[Dict[str, Any]] = None  # Condition to show field
    order: int = 0  # Display order
    group: Optional[str] = None  # Field group (e.g., "basic_info", "requirements")
    active: bool = True


class FormSchema(BaseModel):
    """Complete form schema"""
    form_type: str  # "besoin", "mission", etc.
    version: str = "1.0"
    fields: List[FormField]
    groups: Optional[List[Dict[str, Any]]] = None  # Group definitions
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class StatusConfig(BaseModel):
    """Status configuration for workflow"""
    key: str  # "brouillon", "soumis", etc.
    label: Dict[str, str]  # i18n labels
    description: Optional[Dict[str, str]] = None
    color: str = "#6B7280"  # Hex color for UI
    icon: Optional[str] = None  # Icon name
    allowed_transitions: List[str] = Field(default_factory=list)  # Next possible statuses
    permissions_required: List[str] = Field(default_factory=list)  # Permissions to set this status
    notifications: List[str] = Field(default_factory=list)  # Who to notify on transition
    order: int = 0
    is_terminal: bool = False  # Cannot transition from this status
    active: bool = True


class WorkflowConfig(BaseModel):
    """Complete workflow configuration"""
    entity_type: str  # "besoin", "mission", etc.
    version: str = "1.0"
    statuses: List[StatusConfig]
    initial_status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ReferenceDataItem(BaseModel):
    """Single reference data item"""
    key: str
    label: Dict[str, str]  # i18n
    description: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    order: int = 0
    active: bool = True
    parent_key: Optional[str] = None  # For hierarchical data


class ReferenceData(BaseModel):
    """Reference data collection (types de poste, compétences, etc.)"""
    reference_type: str  # "type_poste", "competences", "duree_options", etc.
    version: str = "1.0"
    items: List[ReferenceDataItem]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


# ==================== API Request/Response Models ====================

class FormFieldCreate(BaseModel):
    """Create or update a form field"""
    key: str
    type: FieldType
    label: Dict[str, str]
    placeholder: Optional[Dict[str, str]] = None
    help_text: Optional[Dict[str, str]] = None
    required: bool = False
    default_value: Optional[Any] = None
    validations: List[ValidationRule] = Field(default_factory=list)
    options: List[FieldOption] = Field(default_factory=list)
    depends_on: Optional[str] = None
    depends_condition: Optional[Dict[str, Any]] = None
    order: int = 0
    group: Optional[str] = None
    active: bool = True


class FormSchemaCreate(BaseModel):
    """Create or update form schema"""
    form_type: str
    fields: List[FormFieldCreate]
    groups: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FormSchemaResponse(BaseModel):
    """Form schema response"""
    id: str
    form_type: str
    version: str
    fields: List[FormField]
    groups: Optional[List[Dict[str, Any]]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class StatusConfigCreate(BaseModel):
    """Create or update status"""
    key: str
    label: Dict[str, str]
    description: Optional[Dict[str, str]] = None
    color: str = "#6B7280"
    icon: Optional[str] = None
    allowed_transitions: List[str] = Field(default_factory=list)
    permissions_required: List[str] = Field(default_factory=list)
    notifications: List[str] = Field(default_factory=list)
    order: int = 0
    is_terminal: bool = False
    active: bool = True


class WorkflowConfigCreate(BaseModel):
    """Create or update workflow"""
    entity_type: str
    statuses: List[StatusConfigCreate]
    initial_status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowConfigResponse(BaseModel):
    """Workflow configuration response"""
    id: str
    entity_type: str
    version: str
    statuses: List[StatusConfig]
    initial_status: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ReferenceDataItemCreate(BaseModel):
    """Create reference data item"""
    key: str
    label: Dict[str, str]
    description: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    order: int = 0
    active: bool = True
    parent_key: Optional[str] = None


class ReferenceDataCreate(BaseModel):
    """Create or update reference data"""
    reference_type: str
    items: List[ReferenceDataItemCreate]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReferenceDataResponse(BaseModel):
    """Reference data response"""
    id: str
    reference_type: str
    version: str
    items: List[ReferenceDataItem]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ConfigListResponse(BaseModel):
    """List of configurations"""
    items: List[Union[FormSchemaResponse, WorkflowConfigResponse, ReferenceDataResponse]]
    total: int
    config_type: str  # "forms", "workflows", "references"
