"""
Routes API pour la Gestion des Permissions Temporaires
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.services.temporary_permissions_service import (
    TemporaryPermissionsService,
    TemporaryPermission
)
from awana_auth.dependencies.permission_dependencies import require_permission
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/temporary-permissions", tags=["Temporary Permissions"])


class GrantTempPermissionRequest(BaseModel):
    """Requête pour accorder une permission temporaire"""
    user_id: str
    permission_code: str
    duration_hours: int
    reason: Optional[str] = None


class ExtendTempPermissionRequest(BaseModel):
    """Requête pour prolonger une permission temporaire"""
    additional_hours: int


class RevokeTempPermissionRequest(BaseModel):
    """Requête pour révoquer une permission temporaire"""
    reason: Optional[str] = None


def get_temp_perm_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> TemporaryPermissionsService:
    """Dépendance pour obtenir le service"""
    return TemporaryPermissionsService(db)


@router.post("", response_model=TemporaryPermission)
async def grant_temporary_permission(
    request: GrantTempPermissionRequest,
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Accorder une permission temporaire à un utilisateur
    
    **Permissions requises:** `permissions.manage.temp` ou `admin`
    
    **Cas d'usage:**
    - Accès temporaire pour un projet spécifique
    - Remplacement d'un collègue absent
    - Test de nouvelles fonctionnalités
    """
    try:
        temp_perm = await service.grant_temporary_permission(
            user_id=request.user_id,
            permission_code=request.permission_code,
            duration_hours=request.duration_hours,
            granted_by=current_user.id,
            reason=request.reason
        )
        
        logger.info(
            f"Permission temporaire accordée: {request.permission_code} "
            f"à {request.user_id} pour {request.duration_hours}h par {current_user.username}"
        )
        
        return temp_perm
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'octroi de permission temporaire: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'octroi de la permission temporaire"
        )


@router.get("/user/{user_id}", response_model=List[TemporaryPermission])
async def get_user_temporary_permissions(
    user_id: str,
    include_expired: bool = False,
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Récupérer les permissions temporaires d'un utilisateur
    
    **Permissions:**
    - Utilisateur peut voir ses propres permissions
    - Admin peut voir toutes les permissions
    """
    # Vérifier les permissions
    if user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que vos propres permissions temporaires"
        )
    
    temp_perms = await service.get_all_temporary_permissions(
        user_id=user_id,
        include_expired=include_expired
    )
    
    return temp_perms


@router.get("/active/{user_id}", response_model=List[TemporaryPermission])
async def get_active_temporary_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Récupérer uniquement les permissions temporaires actives d'un utilisateur
    """
    # Vérifier les permissions
    if user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    active_perms = await service.get_active_temporary_permissions(user_id)
    return active_perms


@router.post("/{temp_perm_id}/extend", response_model=TemporaryPermission)
async def extend_temporary_permission(
    temp_perm_id: str,
    request: ExtendTempPermissionRequest,
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Prolonger une permission temporaire
    
    **Permissions requises:** Admin
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent prolonger les permissions temporaires"
        )
    
    extended = await service.extend_temporary_permission(
        temp_perm_id=temp_perm_id,
        additional_hours=request.additional_hours
    )
    
    if not extended:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission temporaire non trouvée"
        )
    
    logger.info(
        f"Permission temporaire {temp_perm_id} prolongée de "
        f"{request.additional_hours}h par {current_user.username}"
    )
    
    return extended


@router.post("/{temp_perm_id}/revoke")
async def revoke_temporary_permission(
    temp_perm_id: str,
    request: RevokeTempPermissionRequest,
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Révoquer une permission temporaire avant son expiration
    
    **Permissions requises:** Admin
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent révoquer les permissions temporaires"
        )
    
    success = await service.revoke_temporary_permission(
        temp_perm_id=temp_perm_id,
        revoked_by=current_user.id,
        reason=request.reason
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission temporaire non trouvée"
        )
    
    logger.info(
        f"Permission temporaire {temp_perm_id} révoquée par {current_user.username}"
    )
    
    return {"success": True, "message": "Permission temporaire révoquée"}


@router.get("/expiring-soon", response_model=List[TemporaryPermission])
async def get_expiring_permissions(
    hours_threshold: int = 24,
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Récupérer les permissions qui expirent bientôt (pour notifications)
    
    **Permissions requises:** Admin
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux administrateurs"
        )
    
    expiring = await service.get_expiring_soon(hours_threshold=hours_threshold)
    return expiring


@router.get("/statistics")
async def get_temp_permissions_statistics(
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Récupérer les statistiques des permissions temporaires
    
    **Permissions requises:** Admin
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux administrateurs"
        )
    
    stats = await service.get_statistics()
    return stats


@router.post("/cleanup")
async def cleanup_expired_permissions(
    current_user: User = Depends(get_current_user),
    service: TemporaryPermissionsService = Depends(get_temp_perm_service)
):
    """
    Nettoyer les permissions expirées (désactivation)
    
    **Permissions requises:** Admin
    
    **Note:** Cette route peut aussi être appelée par une tâche cron
    """
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux administrateurs"
        )
    
    count = await service.cleanup_expired_permissions()
    
    return {
        "success": True,
        "cleaned_count": count,
        "message": f"{count} permissions expirées désactivées"
    }
