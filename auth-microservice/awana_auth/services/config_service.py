"""
Configuration Service
Centralized service for dynamic application configuration
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ConfigService:
    """Service for managing dynamic application configuration"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.app_config
    
    async def get_config(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration by key
        
        Args:
            key: Configuration key (e.g., 'profiles.badge_new_user')
            
        Returns:
            Configuration document or None
        """
        try:
            config = await self.collection.find_one(
                {"key": key},
                {"_id": 0}
            )
            return config
        except Exception as e:
            logger.error(f"Error fetching config {key}: {e}")
            return None
    
    async def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value directly
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        config = await self.get_config(key)
        if config and "value" in config:
            return config["value"]
        return default
    
    async def get_configs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all configurations for a category
        
        Args:
            category: Configuration category (e.g., 'documents')
            
        Returns:
            List of configuration documents
        """
        try:
            configs = await self.collection.find(
                {"category": category},
                {"_id": 0}
            ).to_list(length=100)
            return configs
        except Exception as e:
            logger.error(f"Error fetching configs for category {category}: {e}")
            return []
    
    async def set_config(
        self,
        key: str,
        value: Any,
        category: str,
        description: str = "",
        updated_by: str = "system"
    ) -> bool:
        """
        Set or update configuration
        
        Args:
            key: Configuration key
            value: Configuration value
            category: Configuration category
            description: Configuration description
            updated_by: User ID who updated
            
        Returns:
            True if successful
        """
        try:
            result = await self.collection.update_one(
                {"key": key},
                {
                    "$set": {
                        "key": key,
                        "value": value,
                        "category": category,
                        "description": description,
                        "updated_at": datetime.now(timezone.utc),
                        "updated_by": updated_by
                    }
                },
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error setting config {key}: {e}")
            return False
    
    async def delete_config(self, key: str) -> bool:
        """
        Delete configuration
        
        Args:
            key: Configuration key
            
        Returns:
            True if successful
        """
        try:
            result = await self.collection.delete_one({"key": key})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting config {key}: {e}")
            return False


# Default configurations
DEFAULT_CONFIGS = {
    "profiles.badge_new_user": {
        "key": "profiles.badge_new_user",
        "value": {
            "enabled": True,
            "expiration_days": 7,
            "expiration_mode": "first_view",  # "first_view" | "creation_date" | "both"
            "badge_text": {
                "fr": "NOUVEAU",
                "en": "NEW"
            }
        },
        "description": "Configuration du badge 'Nouveau profil'",
        "category": "profiles"
    },
    "documents.categories": {
        "key": "documents.categories",
        "value": [
            {
                "id": "identity",
                "name": {"fr": "Pièce d'identité", "en": "Identity Document"},
                "required": True,
                "expirable": True,
                "retention_years": 5,
                "allowed_formats": ["pdf", "jpg", "png"],
                "max_size_mb": 5,
                "required_for_roles": ["interim", "company", "agency"]
            },
            {
                "id": "contract",
                "name": {"fr": "Contrat", "en": "Contract"},
                "required": False,
                "expirable": False,
                "retention_years": 10,
                "allowed_formats": ["pdf"],
                "max_size_mb": 10,
                "required_for_roles": ["interim"]
            },
            {
                "id": "payslip",
                "name": {"fr": "Fiche de paie", "en": "Payslip"},
                "required": False,
                "expirable": False,
                "retention_years": 5,
                "allowed_formats": ["pdf"],
                "max_size_mb": 5,
                "required_for_roles": ["interim"]
            },
            {
                "id": "medical",
                "name": {"fr": "Certificat médical", "en": "Medical Certificate"},
                "required": True,
                "expirable": True,
                "expiration_reminder_days": [30, 15, 7],
                "retention_years": 3,
                "allowed_formats": ["pdf"],
                "max_size_mb": 5,
                "required_for_roles": ["interim"]
            },
            {
                "id": "siret",
                "name": {"fr": "Extrait SIRET", "en": "SIRET Extract"},
                "required": True,
                "expirable": False,
                "retention_years": None,
                "allowed_formats": ["pdf"],
                "max_size_mb": 5,
                "required_for_roles": ["company"]
            },
            {
                "id": "diploma",
                "name": {"fr": "Diplôme", "en": "Diploma"},
                "required": False,
                "expirable": False,
                "retention_years": None,
                "allowed_formats": ["pdf", "jpg", "png"],
                "max_size_mb": 5,
                "required_for_roles": ["interim", "postulant"]
            }
        ],
        "description": "Catégories de documents configurables",
        "category": "documents"
    },
    "notifications.types": {
        "key": "notifications.types",
        "value": {
            "document_expiring": {
                "enabled": True,
                "channels": ["email", "in_app"],
                "template": "document_expiring",
                "reminder_days": [30, 15, 7, 1]
            },
            "new_mission_match": {
                "enabled": True,
                "channels": ["email", "in_app"],
                "template": "new_mission_match",
                "min_match_score": 70
            },
            "application_status_change": {
                "enabled": True,
                "channels": ["email", "in_app"],
                "template": "application_status_change"
            },
            "new_message": {
                "enabled": True,
                "channels": ["in_app"],
                "template": "new_message"
            },
            "profile_validation": {
                "enabled": True,
                "channels": ["email", "in_app"],
                "template": "profile_validation"
            }
        },
        "description": "Types de notifications configurables",
        "category": "notifications"
    },
    "dashboard.widgets": {
        "key": "dashboard.widgets",
        "value": {
            "profile_completion": {
                "enabled": True,
                "priority": 1,
                "roles": ["interim", "company", "agency", "postulant"]
            },
            "missing_documents": {
                "enabled": True,
                "priority": 2,
                "roles": ["interim", "company", "postulant"]
            },
            "recent_notifications": {
                "enabled": True,
                "priority": 3,
                "max_items": 5,
                "roles": ["all"]
            },
            "active_applications": {
                "enabled": True,
                "priority": 4,
                "roles": ["interim", "postulant"]
            },
            "recommended_missions": {
                "enabled": True,
                "priority": 5,
                "max_items": 5,
                "roles": ["interim", "postulant"]
            }
        },
        "description": "Widgets du dashboard configurables",
        "category": "dashboard"
    }
}


async def init_default_configs(db: AsyncIOMotorDatabase) -> int:
    """
    Initialize default configurations if they don't exist
    
    Args:
        db: Database instance
        
    Returns:
        Number of configs initialized
    """
    service = ConfigService(db)
    initialized = 0
    
    for key, config in DEFAULT_CONFIGS.items():
        existing = await service.get_config(key)
        if not existing:
            success = await service.set_config(
                key=config["key"],
                value=config["value"],
                category=config["category"],
                description=config["description"],
                updated_by="system"
            )
            if success:
                initialized += 1
                logger.info(f"Initialized config: {key}")
    
    return initialized
