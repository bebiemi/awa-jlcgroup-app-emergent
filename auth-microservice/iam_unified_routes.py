"""
Routes IAM Unifiées
Endpoints pour le système IAM hybride (profiles + roles)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from pydantic import BaseModel
import logging

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.services.iam_unified_service import IAMUnifiedService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/iam/unified", tags=["iam-unified"])


# ==================== MODELS ====================

class UserPermissionsUnifiedResponse(BaseModel):
    """Réponse des permissions unifiées"""
    user_id: str
    permissions: List[dict]
    permissions_count: int
    sources: dict  # Détails des sources (profiles, roles, groups)


class PermissionCheckRequest(BaseModel):
    """Requête de vérification de permission"""
    user_id: str
    permission_code: str


class PermissionCheckResponse(BaseModel):
    """Réponse de vérification"""
    has_permission: bool
    user_id: str
    permission_code: str


# ==================== ROUTES ====================

@router.get("/users/{user_id}/permissions", response_model=UserPermissionsUnifiedResponse)
async def get_user_permissions_unified(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère toutes les permissions d'un utilisateur depuis toutes les sources
    
    Sources consolidées:
    - Profiles métier (profile_ids)
    - Rôles IAM (roles)
    - Groupes IAM (group_ids)
    
    Compatible avec requiredPermissions de ProtectedRoute
    """
    # Vérification des droits
    if user_id != current_user.id and "admin" not in current_user.roles and "super_admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que vos propres permissions"
        )
    
    try:
        iam_service = IAMUnifiedService(db)
        
        # Récupérer toutes les permissions
        permissions = await iam_service.get_user_all_permissions(user_id)
        
        # Récupérer les détails des sources
        roles_details = await iam_service.get_user_roles_details(user_id)
        
        return UserPermissionsUnifiedResponse(
            user_id=user_id,
            permissions=permissions,
            permissions_count=len(permissions),
            sources={
                "legacy_roles": roles_details.get("legacy_roles", []),
                "iam_roles_count": len(roles_details.get("iam_roles", [])),
                "profiles_count": len(roles_details.get("profiles", [])),
                "groups_count": len(roles_details.get("groups", []))
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting unified permissions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des permissions: {str(e)}"
        )


@router.post("/check-permission", response_model=PermissionCheckResponse)
async def check_user_permission(
    request: PermissionCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Vérifie si un utilisateur a une permission spécifique
    Support des wildcards (ex: missions.*)
    """
    # Vérification des droits
    if request.user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez vérifier que vos propres permissions"
        )
    
    try:
        iam_service = IAMUnifiedService(db)
        has_permission = await iam_service.user_has_permission(
            request.user_id,
            request.permission_code
        )
        
        return PermissionCheckResponse(
            has_permission=has_permission,
            user_id=request.user_id,
            permission_code=request.permission_code
        )
        
    except Exception as e:
        logger.error(f"Error checking permission: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )


@router.get("/users/{user_id}/roles-details")
async def get_user_roles_details(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère les détails complets des rôles, profiles et groupes d'un utilisateur
    Utile pour le debugging et l'administration
    """
    # Vérification des droits
    if user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    try:
        iam_service = IAMUnifiedService(db)
        roles_details = await iam_service.get_user_roles_details(user_id)
        
        return {
            "user_id": user_id,
            "details": roles_details
        }
        
    except Exception as e:
        logger.error(f"Error getting roles details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/users/{user_id}/sync-legacy-roles")
async def sync_user_legacy_roles(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Synchronise les rôles legacy d'un utilisateur avec le système IAM
    Utile pour la migration progressive
    
    Nécessite admin
    """
    if "admin" not in current_user.roles and "super_admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    try:
        iam_service = IAMUnifiedService(db)
        success = await iam_service.sync_user_legacy_roles_to_iam(user_id)
        
        return {
            "success": success,
            "message": "Synchronisation effectuée" if success else "Certains rôles n'ont pas été trouvés"
        }
        
    except Exception as e:
        logger.error(f"Error syncing legacy roles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )
