"""
IAM Cache Management Routes
Endpoints pour gérer et monitorer le cache Redis de l'IAM
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from awana_auth.core.dependencies import get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.models import User
from awana_auth.services.iam_cache_service import get_cache_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iam/cache", tags=["IAM Cache"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupérer les statistiques du cache Redis IAM
    
    Permissions requises:
    - iam.permissions.read
    """
    cache_service = await get_cache_service()
    stats = await cache_service.get_cache_stats()
    
    return {
        "status": "success",
        "data": stats
    }


@router.get("/health")
async def check_cache_health(
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Vérifier la santé du service de cache Redis
    
    Permissions requises:
    - iam.permissions.read
    """
    cache_service = await get_cache_service()
    health = await cache_service.health_check()
    
    return {
        "status": "success",
        "data": health
    }


@router.post("/invalidate/user/{user_id}", status_code=status.HTTP_200_OK)
async def invalidate_user_cache(
    user_id: str,
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Invalider le cache des permissions d'un utilisateur spécifique
    
    Permissions requises:
    - iam.permissions.update
    """
    cache_service = await get_cache_service()
    success = await cache_service.invalidate_user_permissions(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invalidate cache"
        )
    
    return {
        "status": "success",
        "message": f"Cache invalidé pour l'utilisateur {user_id}"
    }


@router.post("/invalidate/all-users", status_code=status.HTTP_200_OK)
async def invalidate_all_users_cache(
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Invalider le cache de tous les utilisateurs
    ⚠️ Opération coûteuse - à utiliser avec précaution
    
    Permissions requises:
    - iam.permissions.update
    """
    cache_service = await get_cache_service()
    success = await cache_service.invalidate_all_user_permissions()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invalidate all user caches"
        )
    
    return {
        "status": "success",
        "message": "Cache de tous les utilisateurs invalidé"
    }


@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_all_cache(
    current_user: User = Depends(require_permission("admin.access"))
):
    """
    Vider TOUT le cache IAM (⚠️ DANGER)
    
    Cette opération supprime toutes les données en cache.
    À utiliser uniquement en cas de problème critique.
    
    Permissions requises:
    - admin.access (super admin uniquement)
    """
    cache_service = await get_cache_service()
    success = await cache_service.clear_all_cache()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )
    
    logger.warning(f"🗑️ CACHE ENTIÈREMENT VIDÉ par {current_user.username}")
    
    return {
        "status": "success",
        "message": "Tout le cache IAM a été vidé"
    }
