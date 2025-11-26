"""
Location Management Models
Hierarchical structure: Country → Province → City (Chef-lieu) → District (Arrondissement) → Neighborhood (Quartier)
"""
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from awana_auth.utils.config_helpers import cfg


# Config-driven validation statuses and validator roles
VALIDATION_STATUS_PENDING = cfg.get_validation_status("pending") or "pending"
VALIDATION_STATUS_APPROVED = cfg.get_validation_status("approved") or "approved"
VALIDATION_STATUS_REJECTED = cfg.get_validation_status("rejected") or "rejected"

VALIDATOR_ROLE_COMMERCIAL = cfg.get_commercial_role() or "commercial"
VALIDATOR_ROLE_ADMIN = cfg.get_admin_role() or "admin"
VALIDATOR_ROLE_SUPER_ADMIN = cfg.get_super_admin_role() or "super_admin"


class LocationType(str, Enum):
    """Location type hierarchy"""
    COUNTRY = "country"          # Pays
    PROVINCE = "province"        # Province
    CITY = "city"               # Chef-lieu (Ville)
    DISTRICT = "district"       # Arrondissement
    NEIGHBORHOOD = "neighborhood" # Quartier


class Location(BaseModel):
    """Location model with hierarchical structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: LocationType
    name: str
    parent_id: Optional[str] = None
    is_visible: bool = True
    is_required: bool = False  # Only true for country, city, neighborhood
    
    # Phone code (for countries)
    phone_code: Optional[str] = None  # e.g., "+241" for Gabon, "+33" for France
    
    # Standard custom fields
    postal_code: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    
    # Additional custom text fields (can be used for anything)
    custom_field_1: Optional[str] = None
    custom_field_2: Optional[str] = None
    custom_field_3: Optional[str] = None
    custom_field_4: Optional[str] = None
    custom_field_5: Optional[str] = None
    
    # Custom field labels (to know what each field represents)
    custom_field_1_label: Optional[str] = None
    custom_field_2_label: Optional[str] = None
    custom_field_3_label: Optional[str] = None
    custom_field_4_label: Optional[str] = None
    custom_field_5_label: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: Optional[str] = None
    
    class Config:
        use_enum_values = True


class LocationCreate(BaseModel):
    """Model for creating a location"""
    type: LocationType
    name: str
    parent_id: Optional[str] = None
    postal_code: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    custom_field_1: Optional[str] = None
    custom_field_2: Optional[str] = None
    custom_field_3: Optional[str] = None
    custom_field_4: Optional[str] = None
    custom_field_5: Optional[str] = None
    custom_field_1_label: Optional[str] = None
    custom_field_2_label: Optional[str] = None
    custom_field_3_label: Optional[str] = None
    custom_field_4_label: Optional[str] = None
    custom_field_5_label: Optional[str] = None


class LocationUpdate(BaseModel):
    """Model for updating a location"""
    name: Optional[str] = None
    is_visible: Optional[bool] = None
    postal_code: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    custom_field_1: Optional[str] = None
    custom_field_2: Optional[str] = None
    custom_field_3: Optional[str] = None
    custom_field_4: Optional[str] = None
    custom_field_5: Optional[str] = None
    custom_field_1_label: Optional[str] = None
    custom_field_2_label: Optional[str] = None
    custom_field_3_label: Optional[str] = None
    custom_field_4_label: Optional[str] = None
    custom_field_5_label: Optional[str] = None


class LocationTree(BaseModel):
    """Location with children for tree view"""
    id: str
    type: LocationType
    name: str
    parent_id: Optional[str] = None
    is_visible: bool
    is_required: bool
    children: List['LocationTree'] = []
    
    class Config:
        use_enum_values = True


# For recursive model
LocationTree.model_rebuild()


class ValidatorRole(str, Enum):
    """Roles that can validate registrations"""
    COMMERCIAL = VALIDATOR_ROLE_COMMERCIAL
    ADMIN = VALIDATOR_ROLE_ADMIN
    SUPER_ADMIN = VALIDATOR_ROLE_SUPER_ADMIN
    # Can be extended dynamically


class ValidationStatus(str, Enum):
    """Validation status"""
    PENDING = VALIDATION_STATUS_PENDING
    APPROVED = VALIDATION_STATUS_APPROVED
    REJECTED = VALIDATION_STATUS_REJECTED


class Validation(BaseModel):
    """Validation request model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    user_full_name: str
    validation_type: str  # "company", "interim", etc.
    status: ValidationStatus = ValidationStatus.PENDING
    
    # Location info
    country_name: Optional[str] = None
    province_name: Optional[str] = None
    city_name: Optional[str] = None
    district_name: Optional[str] = None
    neighborhood_name: Optional[str] = None
    
    # Warning flags
    has_location_warning: bool = False
    location_warning_message: Optional[str] = None
    missing_country: Optional[str] = None  # If user entered a country not in DB
    
    # Représentant légal (pour détection doublons)
    representant_legal_nom: Optional[str] = None
    representant_legal_email: Optional[str] = None
    
    # Détection représentant existant
    has_existing_representant: bool = False
    existing_representant_user_id: Optional[str] = None
    existing_representant_entreprises: Optional[list] = Field(default_factory=list)
    
    # Workflow rattachement
    contact_confirmation: bool = False
    rattachement_status: Optional[str] = None  # "pending", "approved", "rejected"
    rattachement_to_entreprise_id: Optional[str] = None
    
    # Validation metadata
    assigned_to: Optional[str] = None  # User ID of validator
    validated_by: Optional[str] = None
    validated_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UserLocation(BaseModel):
    """User's location information"""
    country_id: Optional[str] = None
    province_id: Optional[str] = None
    city_id: Optional[str] = None
    district_id: Optional[str] = None
    neighborhood_id: Optional[str] = None
    
    # If user entered custom values not in DB
    custom_country: Optional[str] = None
    custom_province: Optional[str] = None
    custom_city: Optional[str] = None
    custom_district: Optional[str] = None
    custom_neighborhood: Optional[str] = None
    
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
