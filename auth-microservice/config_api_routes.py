"""
Routes API pour exposer la configuration au frontend
Permet au frontend d'utiliser les mêmes valeurs que le backend
"""
from fastapi import APIRouter, Depends
from awana_auth.core.config_manager import get_config
from awana_auth.core.dependencies import get_current_user
from awana_auth.core.models import User
from typing import Dict, Any

router = APIRouter(prefix="/api/config", tags=["configuration"])

config = get_config()


@router.get("/roles")
async def get_roles_config() -> Dict[str, Any]:
    """
    Retourne la configuration des rôles
    Public - utilisé par le frontend pour les comparaisons
    """
    return {
        "admin": config.get("security.roles.admin"),
        "super_admin": config.get("security.roles.super_admin"),
        "company": config.get("security.roles.company"),
        "interim": config.get("security.roles.interim"),
        "agency": config.get("security.roles.agency"),
        "commercial": config.get("security.roles.commercial"),
        "validator": config.get("security.roles.validator"),
        "all": config.get("security.roles.all"),
    }


@router.get("/user-statuses")
async def get_user_statuses_config() -> Dict[str, Any]:
    """
    Retourne la configuration des statuts utilisateur
    """
    return {
        "active": config.get("security.user_statuses.active"),
        "pending": config.get("security.user_statuses.pending"),
        "suspended": config.get("security.user_statuses.suspended"),
        "deleted": config.get("security.user_statuses.deleted"),
        "blocked": config.get("security.user_statuses.blocked"),
        "all": config.get("security.user_statuses.all"),
    }


@router.get("/mission-statuses")
async def get_mission_statuses_config() -> Dict[str, Any]:
    """
    Retourne la configuration des statuts de mission
    """
    return {
        "draft": config.get("workflows.mission.statuses.draft"),
        "published": config.get("workflows.mission.statuses.published"),
        "closed": config.get("workflows.mission.statuses.closed"),
        "cancelled": config.get("workflows.mission.statuses.cancelled"),
        "archived": config.get("workflows.mission.statuses.archived"),
        "all": config.get("workflows.mission.statuses.all"),
    }


@router.get("/application-statuses")
async def get_application_statuses_config() -> Dict[str, Any]:
    """
    Retourne la configuration des statuts d'application
    """
    return {
        "submitted": config.get("workflows.application.statuses.submitted"),
        "review": config.get("workflows.application.statuses.review"),
        "interview_scheduled": config.get("workflows.application.statuses.interview_scheduled"),
        "interviewed": config.get("workflows.application.statuses.interviewed"),
        "selected": config.get("workflows.application.statuses.selected"),
        "rejected": config.get("workflows.application.statuses.rejected"),
        "medical_pending": config.get("workflows.application.statuses.medical_pending"),
        "medical_completed": config.get("workflows.application.statuses.medical_completed"),
        "contract_pending": config.get("workflows.application.statuses.contract_pending"),
        "contract_signed": config.get("workflows.application.statuses.contract_signed"),
        "all": config.get("workflows.application.statuses.all"),
    }


@router.get("/validation-statuses")
async def get_validation_statuses_config() -> Dict[str, Any]:
    """
    Retourne la configuration des statuts de validation
    """
    return {
        "pending": config.get("workflows.validation.statuses.pending"),
        "approved": config.get("workflows.validation.statuses.approved"),
        "rejected": config.get("workflows.validation.statuses.rejected"),
        "all": config.get("workflows.validation.statuses.all"),
    }


@router.get("/validation-types")
async def get_validation_types_config() -> Dict[str, Any]:
    """
    Retourne la configuration des types de validation
    """
    return {
        "interim": config.get("workflows.validation.types.interim"),
        "company": config.get("workflows.validation.types.company"),
        "collaborator": config.get("workflows.validation.types.collaborator"),
        "all": config.get("workflows.validation.types.all"),
    }


@router.get("/profile-types")
async def get_profile_types_config() -> Dict[str, Any]:
    """
    Retourne la configuration des types de profil
    """
    return {
        "interim": config.get("profiles.types.interim"),
        "company": config.get("profiles.types.company"),
        "agency": config.get("profiles.types.agency"),
        "all": config.get("profiles.types.all"),
    }


@router.get("/contract-types")
async def get_contract_types_config() -> Dict[str, Any]:
    """
    Retourne la configuration des types de contrat
    """
    return {
        "cdi": config.get("contracts.types.cdi"),
        "cdd": config.get("contracts.types.cdd"),
        "interim": config.get("contracts.types.interim"),
        "freelance": config.get("contracts.types.freelance"),
        "stage": config.get("contracts.types.stage"),
        "all": config.get("contracts.types.all"),
    }


@router.get("/document-types")
async def get_document_types_config() -> Dict[str, Any]:
    """
    Retourne la configuration des types de document
    """
    return {
        "cv": config.get("documents.types.cv"),
        "medical_certificate": config.get("documents.types.medical_certificate"),
        "contract": config.get("documents.types.contract"),
        "identity_document": config.get("documents.types.identity_document"),
        "diploma": config.get("documents.types.diploma"),
        "all": config.get("documents.types.all"),
    }


@router.get("/permissions/mission")
async def get_mission_permissions_config() -> Dict[str, Any]:
    """
    Retourne la configuration des permissions pour les missions
    """
    return {
        "create": config.get("workflows.mission.permissions.create"),
        "view_all": config.get("workflows.mission.permissions.view_all"),
        "publish": config.get("workflows.mission.permissions.publish"),
        "edit": config.get("workflows.mission.permissions.edit"),
        "delete": config.get("workflows.mission.permissions.delete"),
        "view_own": config.get("workflows.mission.permissions.view_own"),
        "apply": config.get("workflows.mission.permissions.apply"),
    }


@router.get("/permissions/application")
async def get_application_permissions_config() -> Dict[str, Any]:
    """
    Retourne la configuration des permissions pour les candidatures
    """
    return {
        "view_all": config.get("workflows.application.permissions.view_all"),
        "manage": config.get("workflows.application.permissions.manage"),
        "view_own": config.get("workflows.application.permissions.view_own"),
    }


@router.get("/permissions/validation")
async def get_validation_permissions_config() -> Dict[str, Any]:
    """
    Retourne la configuration des permissions pour les validations
    """
    return {
        "validator_roles": config.get("workflows.validation.permissions.validator_roles"),
        "view_all": config.get("workflows.validation.permissions.view_all"),
        "assign_validator": config.get("workflows.validation.permissions.assign_validator"),
    }


@router.get("/all")
async def get_all_config() -> Dict[str, Any]:
    """
    Retourne toute la configuration pertinente pour le frontend
    Endpoint pratique pour charger toute la config en une seule requête
    """
    return {
        "roles": await get_roles_config(),
        "user_statuses": await get_user_statuses_config(),
        "mission_statuses": await get_mission_statuses_config(),
        "application_statuses": await get_application_statuses_config(),
        "validation_statuses": await get_validation_statuses_config(),
        "validation_types": await get_validation_types_config(),
        "profile_types": await get_profile_types_config(),
        "contract_types": await get_contract_types_config(),
        "document_types": await get_document_types_config(),
        "permissions": {
            "mission": await get_mission_permissions_config(),
            "application": await get_application_permissions_config(),
            "validation": await get_validation_permissions_config(),
        }
    }
