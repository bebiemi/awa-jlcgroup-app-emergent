"""
Besoin (Need/Job Posting) Models
Represents a company's hiring need before it becomes an operational mission
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class DureeType(str, Enum):
    """Duration type for a need"""
    INDETERMINEE = "indeterminee"
    PERIODE_PRECISE = "periode_precise"


class BesoinStatus(str, Enum):
    """Status workflow for besoin"""
    BROUILLON = "brouillon"  # Draft - editable by company
    SOUMIS = "soumis"  # Submitted to JLC - locked for company
    ANALYSE = "analyse"  # Under analysis by JLC
    MISSION_CREEE = "mission_creee"  # Mission(s) created
    PUBLICATION = "publication"  # Looking for candidates
    POURVU = "pourvu"  # Closed - need fulfilled


class StatusHistoryEntry(BaseModel):
    """History entry for status changes"""
    from_status: Optional[str] = None
    to_status: str
    changed_by: str  # User ID
    changed_by_name: str  # User display name
    changed_at: datetime
    comment: Optional[str] = None


class BesoinComment(BaseModel):
    """Comment/message on a besoin"""
    id: str
    besoin_id: str
    author_type: str  # "entreprise" or "jlc"
    author_id: str
    author_name: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class BesoinCreate(BaseModel):
    """Schema for creating a new besoin"""
    titre: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    duree: DureeType
    date_debut_souhaitee: Optional[date] = None
    date_fin_souhaitee: Optional[date] = None
    type_poste: str  # From dynamic config
    competences_attendues: List[str] = Field(default_factory=list)
    responsable_besoin_id: Optional[str] = None  # Defaults to creator
    pieces_jointes: List[str] = Field(default_factory=list)  # File IDs/URLs
    
    # Dynamic fields stored as JSON
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('date_fin_souhaitee')
    def validate_dates(cls, v, values):
        """Ensure end date is after start date"""
        if v and 'date_debut_souhaitee' in values and values['date_debut_souhaitee']:
            if v < values['date_debut_souhaitee']:
                raise ValueError("Date de fin doit être après la date de début")
        return v


class BesoinUpdate(BaseModel):
    """Schema for updating a besoin (only in draft status)"""
    titre: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    duree: Optional[DureeType] = None
    date_debut_souhaitee: Optional[date] = None
    date_fin_souhaitee: Optional[date] = None
    type_poste: Optional[str] = None
    competences_attendues: Optional[List[str]] = None
    responsable_besoin_id: Optional[str] = None
    pieces_jointes: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class BesoinStatusUpdate(BaseModel):
    """Schema for updating besoin status (workflow)"""
    new_status: BesoinStatus
    comment: Optional[str] = None


class BesoinJLCAnalysis(BaseModel):
    """JLC internal analysis fields"""
    observations: Optional[str] = None
    estimated_budget: Optional[float] = None
    estimated_duration_days: Optional[int] = None
    assigned_to_jlc_user_id: Optional[str] = None
    priority: Optional[str] = None  # "haute", "moyenne", "basse"
    tags: List[str] = Field(default_factory=list)


class BesoinResponse(BaseModel):
    """Full besoin response"""
    id: str
    entreprise_id: str
    entreprise_name: str
    
    # Core fields
    titre: str
    description: str
    duree: DureeType
    date_debut_souhaitee: Optional[date] = None
    date_fin_souhaitee: Optional[date] = None
    type_poste: str
    competences_attendues: List[str]
    responsable_besoin_id: str
    responsable_besoin_name: Optional[str] = None
    pieces_jointes: List[str]
    
    # Dynamic fields
    custom_fields: Dict[str, Any]
    
    # Workflow
    status: BesoinStatus
    status_history: List[StatusHistoryEntry] = Field(default_factory=list)
    
    # JLC internal (only visible to JLC)
    jlc_analysis: Optional[BesoinJLCAnalysis] = None
    
    # Related missions
    mission_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: str
    created_by_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Stats
    comments_count: int = 0


class BesoinListResponse(BaseModel):
    """Paginated list of besoins"""
    items: List[BesoinResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CommentCreate(BaseModel):
    """Create a comment on a besoin"""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """Comment response"""
    id: str
    besoin_id: str
    author_type: str
    author_id: str
    author_name: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ConvertToMissionRequest(BaseModel):
    """Request to convert besoin to mission(s)"""
    mission_titre: Optional[str] = None  # Override besoin titre if needed
    mission_description: Optional[str] = None  # Override description
    internal_notes: Optional[str] = None
    copy_all_fields: bool = True  # Copy all besoin fields to mission
