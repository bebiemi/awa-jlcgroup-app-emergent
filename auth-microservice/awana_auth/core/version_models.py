"""
Modèles pour le versioning de configuration
"""
import uuid

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from awana_auth.utils.config_helpers import ConfigHelper as cfg

ROLES_EXAMPLE = [
    role
    for role in [
        cfg.get_admin_role() or "admin",
        cfg.get_company_role() or "company",
        cfg.get_interim_role() or "interim",
    ]
    if role
]

USER_STATUS_EXAMPLE = [
    status
    for status in [cfg.get_active_status() or "active", cfg.get_pending_status() or "pending"]
    if status
]

class ConfigurationSnapshot(BaseModel):
    """Snapshot de configuration à un moment donné"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str  # Format: "v1.0.0" ou timestamp
    description: str
    created_at: datetime
    created_by: str  # User ID
    created_by_name: str  # User name for display
    snapshot_type: str  # "manual" ou "auto"
    
    # Données de configuration
    config_data: Dict[str, Any]
    
    # Métadonnées
    environment: str = "production"  # local, dev, staging, production
    tags: list[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "version": "v1.2.0",
                "description": "Ajout nouveau rôle 'supervisor'",
                "created_at": "2025-11-05T10:00:00Z",
                "created_by": "admin_user_id",
                "created_by_name": "Admin User",
                "snapshot_type": "manual",
                "config_data": {
                    "roles": ROLES_EXAMPLE,
                    "statuses": USER_STATUS_EXAMPLE,
                },
                "environment": "production",
                "tags": ["roles", "major-change"]
            }
        }

class RollbackRequest(BaseModel):
    """Requête de rollback vers une version"""
    version_id: str
    reason: str
    
class ConfigurationDiff(BaseModel):
    """Différence entre deux versions"""
    version_from: str
    version_to: str
    changes: Dict[str, Any]
    added: list[str] = []
    removed: list[str] = []
    modified: list[str] = []
