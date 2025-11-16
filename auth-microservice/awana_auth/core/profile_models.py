"""
Extended Profile Models for JLC Group
Supports different profile types: Interim, Company Manager, Collaborator
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date, time


# ==================== Enums ====================

class EducationLevel(str):
    """Education levels"""
    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BAC = "bac"
    LICENSE = "license"
    MASTER = "master"
    DOCTORAT = "doctorat"


class LanguageLevel(str):
    """Language proficiency levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    FLUENT = "fluent"
    NATIVE = "native"


class ExperienceType(str):
    """Types of professional experience"""
    INTERNAL_JLC = "internal_jlc"  # Mission via JLC
    EXTERNAL = "external"  # Expérience externe


# ==================== Sub-Models ====================

class ProfessionalExperience(BaseModel):
    """Model for a single professional experience"""
    id: Optional[str] = None  # Generated on creation
    type: str = ExperienceType.EXTERNAL  # internal_jlc or external
    
    # Basic Information
    job_title: str  # Intitulé du poste
    company_name: str  # Nom de l'entreprise
    location: Optional[str] = None  # Lieu
    
    # Dates
    start_date: str  # ISO date format (YYYY-MM-DD)
    end_date: Optional[str] = None  # ISO date, None if ongoing
    is_current: bool = False  # Poste actuel
    
    # Description
    description: Optional[str] = None  # Description des missions
    achievements: List[str] = Field(default_factory=list)  # Réalisations clés
    
    # Skills & Competencies
    skills_used: List[str] = Field(default_factory=list)  # Compétences utilisées
    
    # JLC-specific (if type = internal_jlc)
    mission_id: Optional[str] = None  # Reference to JLC mission
    contract_id: Optional[str] = None  # Reference to contract
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class MissionType(str):
    """Types of missions"""
    SHORT_TERM = "short_term"  # Court terme
    LONG_TERM = "long_term"    # Long terme
    CDD = "cdd"
    CDI = "cdi"
    FREELANCE = "freelance"


class DocumentType(str):
    """Types of documents"""
    CV = "cv"
    DIPLOMA = "diploma"
    CERTIFICATE = "certificate"
    ID_CARD = "id_card"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    OTHER = "other"


# ==================== Sub-Models ====================

class Language(BaseModel):
    """Language and proficiency level"""
    language: str  # e.g., "Français", "Anglais", "Espagnol"
    level: str  # basic, intermediate, advanced, fluent, native
    

class Skill(BaseModel):
    """Professional skill or competency"""
    name: str
    years_of_experience: Optional[int] = None


class AvailabilitySlot(BaseModel):
    """Time slot for availability"""
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: str   # HH:MM format (e.g., "08:00")
    end_time: str     # HH:MM format (e.g., "17:00")


class Document(BaseModel):
    """Document metadata"""
    id: str
    user_id: str
    type: str  # cv, diploma, certificate, id_card, etc.
    filename: str
    original_filename: str
    file_path: str
    file_size: int  # in bytes
    mime_type: str
    uploaded_at: str  # ISO datetime
    

# ==================== Profile Models ====================

class InterimProfile(BaseModel):
    """Complete profile for interim workers"""
    user_id: str
    
    # Personal Information
    photo_url: Optional[str] = None
    nationality: Optional[str] = None
    social_security_number: Optional[str] = None
    
    # Education & Experience
    education_level: Optional[str] = None
    years_of_experience: Optional[int] = None
    
    # Professional Information
    sectors: List[str] = Field(default_factory=list)  # e.g., ["BTP", "Hôtellerie"]
    skills: List[Dict] = Field(default_factory=list)  # List of {name, years_of_experience}
    languages: List[Dict] = Field(default_factory=list)  # List of {language, level}
    
    # Driving
    has_driving_license: bool = False
    driving_license_types: List[str] = Field(default_factory=list)  # e.g., ["B", "C"]
    
    # Availability
    general_availability: List[Dict] = Field(default_factory=list)  # List of time slots
    available_immediately: bool = False
    available_from_date: Optional[str] = None  # ISO date
    accepted_mission_types: List[str] = Field(default_factory=list)  # short_term, long_term, etc.
    
    # Calendar (blocked dates)
    blocked_dates: List[str] = Field(default_factory=list)  # ISO dates
    
    # Documents
    cv_document_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    profile_completed: bool = False
    profile_completion_percentage: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CompanyManagerProfile(BaseModel):
    """Profile for company managers"""
    user_id: str
    
    # Company Role
    job_title: Optional[str] = None
    department: Optional[str] = None
    
    # Documents
    document_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    profile_completed: bool = False
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CollaboratorProfile(BaseModel):
    """Minimal profile for collaborators"""
    user_id: str
    
    # Minimal info
    job_title: Optional[str] = None
    
    # Metadata
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==================== Request/Response Models ====================

class UpdateInterimProfileRequest(BaseModel):
    """Request to update interim profile"""
    photo_url: Optional[str] = None
    nationality: Optional[str] = None
    social_security_number: Optional[str] = None
    education_level: Optional[str] = None
    years_of_experience: Optional[int] = None
    sectors: Optional[List[str]] = None
    skills: Optional[List[Dict]] = None
    languages: Optional[List[Dict]] = None
    has_driving_license: Optional[bool] = None
    driving_license_types: Optional[List[str]] = None
    general_availability: Optional[List[Dict]] = None
    available_immediately: Optional[bool] = None
    available_from_date: Optional[str] = None
    accepted_mission_types: Optional[List[str]] = None
    blocked_dates: Optional[List[str]] = None


class UpdateCompanyManagerProfileRequest(BaseModel):
    """Request to update company manager profile"""
    job_title: Optional[str] = None
    department: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    success: bool
    document_id: str
    filename: str
    file_size: int
    message: str
