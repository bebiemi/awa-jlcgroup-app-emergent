"""
Modèles pour la gestion de la rétention des données
Support multi-entités : utilisateurs, documents, missions, sociétés, etc.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class RetentionEntityType(str, Enum):
    """Types d'entités supportées pour la rétention"""
    USERS = "users"
    DOCUMENTS = "documents"
    MISSIONS = "missions"
    COMPANIES = "companies"
    APPLICATIONS = "applications"
    CONTRACTS = "contracts"
    AUDIT_LOGS = "audit_logs"


class RetentionStatus(str, Enum):
    """Statut d'une configuration de rétention"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class RetentionWorkflowStage(BaseModel):
    """Configuration d'une étape du workflow de rétention"""
    stage_name: str = Field(..., description="Nom de l'étape (ex: J-7, J-3, J)")
    days_before_deletion: int = Field(..., description="Jours avant suppression définitive")
    action: str = Field(..., description="Action à effectuer (notification, status_change, delete)")
    notification_recipients: List[str] = Field(default_factory=list, description="Rôles destinataires")
    status_transition: Optional[str] = Field(None, description="Nouveau statut si applicable")
    description: str = Field(..., description="Description de l'étape")


class RetentionPolicyConfig(BaseModel):
    """Configuration complète d'une politique de rétention"""
    id: Optional[str] = None
    entity_type: RetentionEntityType
    entity_label: str = Field(..., description="Label lisible (ex: 'Utilisateurs', 'Documents')")
    
    # Configuration principale
    retention_days: int = Field(..., description="Délai global de rétention en jours", ge=1)
    is_enabled: bool = Field(default=True, description="Politique active ou non")
    status: RetentionStatus = Field(default=RetentionStatus.ACTIVE)
    
    # Workflow personnalisé
    workflow_stages: List[RetentionWorkflowStage] = Field(
        default_factory=list,
        description="Étapes du workflow (J-7, J-3, J, J+3...)"
    )
    
    # Options avancées
    auto_archive: bool = Field(default=True, description="Archivage automatique")
    soft_delete: bool = Field(default=True, description="Suppression douce avant définitive")
    keep_audit_trail: bool = Field(default=True, description="Conserver la trace d'audit")
    
    # Métadonnées
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Description et notes
    description: Optional[str] = None
    legal_basis: Optional[str] = Field(None, description="Base légale RGPD")
    notes: Optional[str] = None


class RetentionPolicyResponse(BaseModel):
    """Réponse API pour une politique de rétention"""
    id: str
    entity_type: str
    entity_label: str
    retention_days: int
    is_enabled: bool
    status: str
    workflow_stages_count: int
    created_at: str
    updated_at: str
    description: Optional[str] = None


class RetentionPolicyListResponse(BaseModel):
    """Liste de politiques de rétention"""
    policies: List[RetentionPolicyResponse]
    total: int


class CreateRetentionPolicyRequest(BaseModel):
    """Requête de création de politique"""
    entity_type: RetentionEntityType
    entity_label: str
    retention_days: int = Field(..., ge=1, le=3650)
    workflow_stages: List[RetentionWorkflowStage] = Field(default_factory=list)
    description: Optional[str] = None
    legal_basis: Optional[str] = None
    auto_archive: bool = True
    soft_delete: bool = True
    keep_audit_trail: bool = True


class UpdateRetentionPolicyRequest(BaseModel):
    """Requête de mise à jour de politique"""
    entity_label: Optional[str] = None
    retention_days: Optional[int] = Field(None, ge=1, le=3650)
    is_enabled: Optional[bool] = None
    workflow_stages: Optional[List[RetentionWorkflowStage]] = None
    description: Optional[str] = None
    legal_basis: Optional[str] = None
    auto_archive: Optional[bool] = None
    soft_delete: Optional[bool] = None
    keep_audit_trail: Optional[bool] = None


class RetentionStatsResponse(BaseModel):
    """Statistiques globales de rétention"""
    total_policies: int
    active_policies: int
    inactive_policies: int
    total_entities_in_retention: Dict[str, int]
    policies_by_entity: Dict[str, Dict]
