"""
Modèles Pydantic pour le système de Feature Flags
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class FeatureFlagType(str, Enum):
    """Types de feature flags"""
    GLOBAL = "GLOBAL"      # S'applique à tous
    ROLE = "ROLE"          # S'applique à un rôle spécifique
    USER = "USER"          # S'applique à un utilisateur spécifique
    ENV = "ENV"            # S'applique à un environnement (dev, staging, prod)


class FeatureFlagMetadata(BaseModel):
    """Métadonnées d'un feature flag"""
    description: Optional[str] = None
    rollout_percentage: int = Field(default=0, ge=0, le=100)
    created_by_name: Optional[str] = None
    tags: List[str] = []
    dependencies: List[str] = []  # Autres flags requis
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Nouvelle interface dashboard",
                "rollout_percentage": 50,
                "created_by_name": "Admin User",
                "tags": ["ui", "beta"],
                "dependencies": ["feature.auth.v2"]
            }
        }


class FeatureFlag(BaseModel):
    """Modèle d'un feature flag"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str = Field(..., description="Clé unique du flag (ex: feature.mission.bulk_assign)")
    type: FeatureFlagType
    value: bool = Field(default=False, description="Activé ou désactivé")
    target: Optional[str] = Field(None, description="Cible (role name, user_id, ou env name)")
    metadata: FeatureFlagMetadata = Field(default_factory=FeatureFlagMetadata)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    
    @validator('key')
    def validate_key(cls, v):
        """Valider le format de la clé"""
        if not v or len(v) < 3:
            raise ValueError('La clé doit contenir au moins 3 caractères')
        if not all(c.isalnum() or c in '._-' for c in v):
            raise ValueError('La clé ne peut contenir que des lettres, chiffres, points, tirets')
        return v.lower()
    
    @validator('target')
    def validate_target(cls, v, values):
        """Valider que target est requis pour certains types"""
        flag_type = values.get('type')
        if flag_type in [FeatureFlagType.ROLE, FeatureFlagType.USER, FeatureFlagType.ENV]:
            if not v:
                raise ValueError(f'Target requis pour type {flag_type}')
        elif flag_type == FeatureFlagType.GLOBAL:
            if v:
                raise ValueError('Target doit être null pour type GLOBAL')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "key": "feature.mission.bulk_assign",
                "type": "GLOBAL",
                "value": True,
                "target": None,
                "metadata": {
                    "description": "Permet l'assignation groupée de missions",
                    "rollout_percentage": 100,
                    "tags": ["mission", "productivity"]
                },
                "created_by": "admin_user_id"
            }
        }


class CreateFeatureFlagRequest(BaseModel):
    """Requête de création d'un feature flag"""
    key: str
    type: FeatureFlagType
    value: bool = False
    target: Optional[str] = None
    metadata: Optional[FeatureFlagMetadata] = None


class UpdateFeatureFlagRequest(BaseModel):
    """Requête de mise à jour d'un feature flag"""
    value: Optional[bool] = None
    target: Optional[str] = None
    metadata: Optional[FeatureFlagMetadata] = None


class RolloutRequest(BaseModel):
    """Requête pour appliquer un rollout progressif"""
    rollout_percentage: int = Field(..., ge=0, le=100)
    description: Optional[str] = None


class FeatureFlagContext(BaseModel):
    """Contexte pour l'évaluation d'un feature flag"""
    user_id: Optional[str] = None
    roles: List[str] = []
    environment: str = "production"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_uuid",
                "roles": ["admin", "manager"],
                "environment": "production"
            }
        }


class AuditEventType(str, Enum):
    """Types d'événements d'audit"""
    FEATURE_FLAG_CREATED = "feature_flag.created"
    FEATURE_FLAG_UPDATED = "feature_flag.updated"
    FEATURE_FLAG_DELETED = "feature_flag.deleted"
    FEATURE_FLAG_ROLLOUT = "feature_flag.rollout"
    ROLE_VISIBILITY_UPDATED = "role.visibility.updated"
    USER_QUERY_FILTERED = "user.query.filtered"


class AuditEvent(BaseModel):
    """Événement d'audit"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str
    actor_name: Optional[str] = None
    action: AuditEventType
    target_type: str  # "feature_flag", "role", "user"
    target_id: Optional[str] = None
    payload: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "audit_uuid",
                "actor_id": "admin_uuid",
                "actor_name": "Admin User",
                "action": "feature_flag.updated",
                "target_type": "feature_flag",
                "target_id": "flag_uuid",
                "payload": {
                    "old_value": False,
                    "new_value": True,
                    "flag_key": "feature.mission.bulk_assign"
                }
            }
        }


class RoleVisibilityUpdate(BaseModel):
    """Mise à jour de la visibilité d'un rôle"""
    is_hidden_from_admins: bool
