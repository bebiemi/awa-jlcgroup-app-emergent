"""
Mission Management Models
Gestion complète du processus de mise à disposition des candidats
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MissionStatus(str, Enum):
    """Statuts d'une mission dans le workflow"""
    # Étape 1: Création du besoin
    DRAFT = "draft"  # Brouillon
    PENDING_VALIDATION = "pending_validation"  # En attente validation commerciale
    
    # Étape 2-3: Publication
    PUBLISHED = "published"  # Publiée et visible aux intérimaires
    
    # Étape 4-8: Recrutement
    ACCEPTING_APPLICATIONS = "accepting_applications"  # Accepte les candidatures
    APPLICATIONS_CLOSED = "applications_closed"  # Candidatures fermées
    IN_REVIEW = "in_review"  # Analyse des candidatures
    INTERVIEWS_SCHEDULED = "interviews_scheduled"  # Entretiens planifiés
    INTERVIEWS_COMPLETED = "interviews_completed"  # Entretiens terminés
    
    # Étape 9-12: Sélection client
    PROFILES_SENT_TO_CLIENT = "profiles_sent_to_client"  # Profils envoyés au client
    CLIENT_SELECTION_PENDING = "client_selection_pending"  # Attente sélection client
    CLIENT_SELECTION_COMPLETED = "client_selection_completed"  # Client a sélectionné
    
    # Étape 13-15: Visite médicale et contrat
    MEDICAL_CHECK_PENDING = "medical_check_pending"  # Visite médicale en attente
    MEDICAL_CHECK_COMPLETED = "medical_check_completed"  # Visite médicale faite
    CONTRACT_PENDING = "contract_pending"  # Contrat en attente
    CONTRACT_SIGNED = "contract_signed"  # Contrat signé
    
    # Statuts finaux
    COMPLETED = "completed"  # Mission complétée
    CANCELLED = "cancelled"  # Mission annulée
    ON_HOLD = "on_hold"  # Mission suspendue


class ApplicationStatus(str, Enum):
    """Statuts d'une candidature dans le workflow"""
    # Étape 4-5: Candidature
    SUBMITTED = "submitted"  # Candidature soumise
    RECEIVED = "received"  # Candidature reçue
    
    # Étape 6: Analyse
    UNDER_REVIEW = "under_review"  # En cours d'analyse
    SHORTLISTED = "shortlisted"  # Présélectionné
    REJECTED_INITIAL = "rejected_initial"  # Rejeté lors du tri initial
    
    # Étape 7-8: Entretien
    INTERVIEW_SCHEDULED = "interview_scheduled"  # Entretien planifié
    INTERVIEW_COMPLETED = "interview_completed"  # Entretien passé
    SELECTED_FOR_CLIENT = "selected_for_client"  # Retenu pour présentation client
    REJECTED_AFTER_INTERVIEW = "rejected_after_interview"  # Rejeté après entretien
    
    # Étape 9-12: Présentation client
    SENT_TO_CLIENT = "sent_to_client"  # Envoyé au client
    SELECTED_BY_CLIENT = "selected_by_client"  # Retenu par le client
    REJECTED_BY_CLIENT = "rejected_by_client"  # Rejeté par le client
    STANDBY = "standby"  # En attente (liste de réserve)
    
    # Étape 13-15: Process médical et contrat
    MEDICAL_CHECK_PENDING = "medical_check_pending"  # Visite médicale à faire
    MEDICAL_APPROVED = "medical_approved"  # Apte médicalement
    MEDICAL_REJECTED = "medical_rejected"  # Inapte médicalement
    CONTRACT_PENDING = "contract_pending"  # Contrat à signer
    CONTRACT_SIGNED = "contract_signed"  # Contrat signé
    
    # Statuts finaux
    HIRED = "hired"  # Embauché
    REJECTED = "rejected"  # Rejeté définitivement
    WITHDRAWN = "withdrawn"  # Candidature retirée


class MedicalStatus(str, Enum):
    """Statut de la visite médicale"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED_APTE = "completed_apte"  # Apte
    COMPLETED_INAPTE = "completed_inapte"  # Inapte
    DOCUMENT_UPLOADED = "document_uploaded"


class ContractStatus(str, Enum):
    """Statut du contrat"""
    NOT_GENERATED = "not_generated"
    DRAFT = "draft"
    SENT = "sent"
    SIGNED_BY_INTERIM = "signed_by_interim"
    SIGNED_BY_COMPANY = "signed_by_company"
    FULLY_SIGNED = "fully_signed"


# ==================== MISSION MODELS ====================

class MissionBase(BaseModel):
    """Base pour la création d'une mission"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    company_id: str  # ID de l'entreprise cliente
    
    # Détails du poste
    job_type: str  # Type de poste (ex: "développeur", "comptable")
    required_skills: List[str] = []  # Compétences requises
    experience_required: str  # Expérience requise (ex: "2-5 ans")
    education_level: Optional[str] = None  # Niveau d'études
    
    # Informations mission
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[str] = None  # Durée (ex: "3 mois", "CDI")
    location: str  # Lieu de la mission
    location_details: Optional[Dict[str, Any]] = None  # Détails localisation
    
    # Conditions
    salary_range: Optional[str] = None  # Fourchette salariale
    contract_type: str  # Type de contrat (CDD, CDI, etc.)
    working_hours: Optional[str] = None  # Horaires
    benefits: Optional[List[str]] = None  # Avantages
    
    # Configuration
    max_applications: Optional[int] = None  # Nombre max de candidatures
    application_deadline: Optional[datetime] = None  # Date limite candidatures
    requires_medical_check: bool = True  # Visite médicale obligatoire
    
    # Metadata
    custom_fields: Optional[Dict[str, Any]] = None


class MissionCreate(MissionBase):
    """Création d'une mission"""
    created_by: str  # ID de l'utilisateur créateur
    commercial_id: Optional[str] = None  # ID du commercial assigné


class MissionUpdate(BaseModel):
    """Mise à jour d'une mission"""
    title: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_required: Optional[str] = None
    education_level: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    contract_type: Optional[str] = None
    working_hours: Optional[str] = None
    benefits: Optional[List[str]] = None
    max_applications: Optional[int] = None
    application_deadline: Optional[datetime] = None
    requires_medical_check: Optional[bool] = None
    status: Optional[MissionStatus] = None
    commercial_id: Optional[str] = None


class Mission(MissionBase):
    """Modèle complet d'une mission"""
    id: str
    status: MissionStatus = MissionStatus.DRAFT
    created_by: str
    commercial_id: Optional[str] = None
    
    # Statistiques
    applications_count: int = 0
    shortlisted_count: int = 0
    selected_count: int = 0
    hired_count: int = 0
    
    # Workflow tracking
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CANDIDATURE MODELS ====================

class ApplicationBase(BaseModel):
    """Base pour une candidature"""
    mission_id: str
    user_id: str  # ID de l'intérimaire
    
    # Motivation
    cover_letter: Optional[str] = None  # Lettre de motivation
    
    # Compétences déclarées
    matching_skills: List[str] = []  # Compétences correspondantes
    additional_info: Optional[str] = None  # Informations complémentaires


class ApplicationCreate(ApplicationBase):
    """Création d'une candidature"""
    pass


class ApplicationUpdate(BaseModel):
    """Mise à jour d'une candidature"""
    status: Optional[ApplicationStatus] = None
    cover_letter: Optional[str] = None
    matching_skills: Optional[List[str]] = None
    additional_info: Optional[str] = None
    
    # Notes internes
    internal_notes: Optional[str] = None
    score: Optional[int] = None  # Score d'évaluation (0-100)
    
    # Entretien
    interview_scheduled_at: Optional[datetime] = None
    interview_notes: Optional[str] = None
    interview_rating: Optional[int] = None  # Note entretien (1-5)
    
    # Client
    client_feedback: Optional[str] = None
    client_selected: Optional[bool] = None
    
    # Médical
    medical_status: Optional[MedicalStatus] = None
    medical_document_url: Optional[str] = None
    medical_notes: Optional[str] = None
    
    # Contrat
    contract_status: Optional[ContractStatus] = None
    contract_url: Optional[str] = None
    contract_signed_at: Optional[datetime] = None


class Application(ApplicationBase):
    """Modèle complet d'une candidature"""
    id: str
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    
    # Évaluation
    score: Optional[int] = None
    internal_notes: Optional[str] = None
    
    # Entretien
    interview_scheduled_at: Optional[datetime] = None
    interview_completed_at: Optional[datetime] = None
    interview_notes: Optional[str] = None
    interview_rating: Optional[int] = None
    
    # Client
    sent_to_client_at: Optional[datetime] = None
    client_response_at: Optional[datetime] = None
    client_selected: Optional[bool] = None
    client_feedback: Optional[str] = None
    
    # Médical
    medical_status: MedicalStatus = MedicalStatus.NOT_REQUIRED
    medical_document_url: Optional[str] = None
    medical_scheduled_at: Optional[datetime] = None
    medical_completed_at: Optional[datetime] = None
    medical_notes: Optional[str] = None
    
    # Contrat
    contract_status: ContractStatus = ContractStatus.NOT_GENERATED
    contract_url: Optional[str] = None
    contract_sent_at: Optional[datetime] = None
    contract_signed_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== DOCUMENT MODELS ====================

class DocumentType(str, Enum):
    """Types de documents"""
    CV = "cv"
    COVER_LETTER = "cover_letter"
    MEDICAL_CERTIFICATE = "medical_certificate"
    CONTRACT = "contract"
    ID_DOCUMENT = "id_document"
    OTHER = "other"


class DocumentUpload(BaseModel):
    """Upload d'un document"""
    application_id: str
    document_type: DocumentType
    file_name: str
    file_size: int
    mime_type: str
    description: Optional[str] = None


class Document(DocumentUpload):
    """Modèle complet d'un document"""
    id: str
    user_id: str  # Qui a uploadé
    file_url: str  # URL du fichier
    uploaded_at: datetime
    
    # Validation
    validated: bool = False
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== NOTIFICATION MODELS ====================

class NotificationType(str, Enum):
    """Types de notifications"""
    MISSION_CREATED = "mission_created"
    MISSION_PUBLISHED = "mission_published"
    APPLICATION_RECEIVED = "application_received"
    APPLICATION_SHORTLISTED = "application_shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    SELECTED_FOR_CLIENT = "selected_for_client"
    SELECTED_BY_CLIENT = "selected_by_client"
    REJECTED_BY_CLIENT = "rejected_by_client"
    MEDICAL_CHECK_REQUIRED = "medical_check_required"
    CONTRACT_AVAILABLE = "contract_available"
    MISSION_COMPLETED = "mission_completed"


class NotificationCreate(BaseModel):
    """Création d'une notification"""
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    link: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Notification(NotificationCreate):
    """Modèle complet d'une notification"""
    id: str
    read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
