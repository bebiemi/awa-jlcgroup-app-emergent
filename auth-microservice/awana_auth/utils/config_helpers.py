"""
Helpers pour accéder facilement aux configurations
Simplifie l'utilisation de ConfigManager dans les routes
"""
from awana_auth.core.config_manager import get_config
from typing import List

config = get_config()


class ConfigHelper:
    """Helper pour accéder aux configurations couramment utilisées"""
    
    # Rôles
    @staticmethod
    def get_role(role_name: str) -> str:
        """Obtenir un rôle spécifique"""
        return config.get(f"security.roles.{role_name}")
    
    @staticmethod
    def get_all_roles() -> List[str]:
        """Obtenir tous les rôles"""
        return config.get("security.roles.all")
    
    @staticmethod
    def get_admin_role() -> str:
        return config.get("security.roles.admin")
    
    @staticmethod
    def get_super_admin_role() -> str:
        return config.get("security.roles.super_admin")
    
    @staticmethod
    def get_company_role() -> str:
        return config.get("security.roles.company")
    
    @staticmethod
    def get_interim_role() -> str:
        return config.get("security.roles.interim")
    
    @staticmethod
    def get_commercial_role() -> str:
        return config.get("security.roles.commercial")
    
    @staticmethod
    def get_agency_role() -> str:
        return config.get("security.roles.agency")
    
    @staticmethod
    def get_validator_role() -> str:
        return config.get("security.roles.validator")
    
    # Statuts utilisateur
    @staticmethod
    def get_user_status(status_name: str) -> str:
        """Obtenir un statut utilisateur spécifique"""
        return config.get(f"security.user_statuses.{status_name}")
    
    @staticmethod
    def get_all_user_statuses() -> List[str]:
        """Obtenir tous les statuts utilisateur"""
        return config.get("security.user_statuses.all")
    
    @staticmethod
    def get_active_status() -> str:
        return config.get("security.user_statuses.active")
    
    @staticmethod
    def get_pending_status() -> str:
        return config.get("security.user_statuses.pending")
    
    @staticmethod
    def get_suspended_status() -> str:
        return config.get("security.user_statuses.suspended")
    
    @staticmethod
    def get_deleted_status() -> str:
        return config.get("security.user_statuses.deleted")
    
    @staticmethod
    def get_blocked_status() -> str:
        return config.get("security.user_statuses.blocked")
    
    # Statuts de mission
    @staticmethod
    def get_mission_status(status_name: str) -> str:
        """Obtenir un statut de mission spécifique"""
        return config.get(f"workflows.mission.statuses.{status_name}")
    
    @staticmethod
    def get_all_mission_statuses() -> List[str]:
        return config.get("workflows.mission.statuses.all")
    
    # Statuts d'application
    @staticmethod
    def get_application_status(status_name: str) -> str:
        """Obtenir un statut d'application spécifique"""
        return config.get(f"workflows.application.statuses.{status_name}")
    
    @staticmethod
    def get_all_application_statuses() -> List[str]:
        return config.get("workflows.application.statuses.all")
    
    # Statuts de validation
    @staticmethod
    def get_validation_status(status_name: str) -> str:
        """Obtenir un statut de validation spécifique"""
        return config.get(f"workflows.validation.statuses.{status_name}")
    
    @staticmethod
    def get_all_validation_statuses() -> List[str]:
        return config.get("workflows.validation.statuses.all")
    
    # Types de validation
    @staticmethod
    def get_validation_type(type_name: str) -> str:
        """Obtenir un type de validation spécifique"""
        return config.get(f"workflows.validation.types.{type_name}")
    
    @staticmethod
    def get_all_validation_types() -> List[str]:
        return config.get("workflows.validation.types.all")
    
    # Types de profil
    @staticmethod
    def get_profile_type(type_name: str) -> str:
        """Obtenir un type de profil spécifique"""
        return config.get(f"profiles.types.{type_name}")
    
    @staticmethod
    def get_all_profile_types() -> List[str]:
        return config.get("profiles.types.all")
    
    # Types de contrat
    @staticmethod
    def get_contract_type(type_name: str) -> str:
        """Obtenir un type de contrat spécifique"""
        return config.get(f"contracts.types.{type_name}")
    
    @staticmethod
    def get_all_contract_types() -> List[str]:
        return config.get("contracts.types.all")
    
    # Types de document
    @staticmethod
    def get_document_type(type_name: str) -> str:
        """Obtenir un type de document spécifique"""
        return config.get(f"documents.types.{type_name}")
    
    @staticmethod
    def get_all_document_types() -> List[str]:
        return config.get("documents.types.all")
    
    # Permissions Mission
    @staticmethod
    def get_mission_permission_roles(permission_name: str) -> List[str]:
        """Obtenir les rôles autorisés pour une permission mission"""
        return config.get(f"workflows.mission.permissions.{permission_name}")
    
    # Permissions Application
    @staticmethod
    def get_application_permission_roles(permission_name: str) -> List[str]:
        """Obtenir les rôles autorisés pour une permission application"""
        return config.get(f"workflows.application.permissions.{permission_name}")
    
    # Permissions Validation
    @staticmethod
    def get_validation_permission_roles(permission_name: str) -> List[str]:
        """Obtenir les rôles autorisés pour une permission validation"""
        return config.get(f"workflows.validation.permissions.{permission_name}")
    
    @staticmethod
    def get_validator_roles() -> List[str]:
        """Obtenir les rôles validateurs"""
        return config.get("workflows.validation.permissions.validator_roles")
    
    # Helper pour vérifier si un utilisateur a un rôle spécifique
    @staticmethod
    def user_has_role(user_roles: List[str], required_role: str) -> bool:
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return required_role in user_roles
    
    @staticmethod
    def user_has_any_role(user_roles: List[str], required_roles: List[str]) -> bool:
        """Vérifie si l'utilisateur a au moins un des rôles requis"""
        return any(role in user_roles for role in required_roles)
    
    @staticmethod
    def user_has_all_roles(user_roles: List[str], required_roles: List[str]) -> bool:
        """Vérifie si l'utilisateur a tous les rôles requis"""
        return all(role in user_roles for role in required_roles)


# Instance globale pour faciliter l'utilisation
cfg = ConfigHelper()
