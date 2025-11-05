from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class ReferenceCategory(str, Enum):
    """Catégories de référentiels"""
    ROLES = "roles"
    STATUSES = "statuses"
    CONTRACT_TYPES = "contract_types"
    COUNTRIES = "countries"
    REGIONS = "regions"
    CITIES = "cities"
    SKILLS = "skills"
    DOCUMENT_TYPES = "document_types"
    PERMISSIONS = "permissions"
    MISSION_STATUSES = "mission_statuses"
    APPLICATION_STATUSES = "application_statuses"
    MEDICAL_APTITUDES = "medical_aptitudes"


class SystemReference(BaseModel):
    """Modèle pour les référentiels système"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    code: str  # Identifiant unique dans la catégorie
    label_fr: str
    label_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None  # Pour hiérarchies
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_system: bool = False  # Ne peut pas être modifié/supprimé si True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "roles",
                "code": "interim",
                "label_fr": "Intérimaire",
                "label_en": "Temporary Worker",
                "description": "Utilisateur cherchant des missions intérim",
                "metadata": {
                    "color": "#3B82F6",
                    "icon": "user",
                    "permissions": ["view_jobs", "apply"]
                },
                "is_active": True,
                "is_system": False
            }
        }


class ApplicationSetting(BaseModel):
    """Paramètres applicatifs"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str  # Clé unique
    value: str  # Valeur stockée en string
    type: str = "string"  # string, integer, boolean, json, array
    category: str = "general"
    label: str
    description: Optional[str] = None
    is_public: bool = False  # Accessible côté frontend
    validation_rules: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_typed_value(self) -> Any:
        """Retourne la valeur avec le bon type"""
        if self.type == "integer":
            return int(self.value)
        elif self.type == "boolean":
            return self.value.lower() in ['true', '1', 'yes']
        elif self.type == "json":
            import json
            return json.loads(self.value)
        elif self.type == "array":
            import json
            return json.loads(self.value)
        return self.value


class BusinessRule(BaseModel):
    """Règles métier"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    rule_type: str  # validation, notification, workflow, automation
    conditions: Dict[str, Any]  # Conditions pour déclencher la règle
    actions: Dict[str, Any]  # Actions à exécuter
    priority: int = 0  # Ordre d'exécution
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Requêtes API
class CreateReferenceRequest(BaseModel):
    category: str
    code: str
    label_fr: str
    label_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class UpdateReferenceRequest(BaseModel):
    label_fr: Optional[str] = None
    label_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CreateSettingRequest(BaseModel):
    key: str
    value: str
    type: str = "string"
    category: str = "general"
    label: str
    description: Optional[str] = None
    is_public: bool = False
