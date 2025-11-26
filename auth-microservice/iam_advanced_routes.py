"""
Routes API Avancées IAM
- Cache Redis
- Permissions temporaires
- Audit trail
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from awana_auth.services.iam_cache_service import get_cache_service, IAMCacheService
from awana_auth.services.temporary_permissions_service import (
    TemporaryPermissionsService,
    TemporaryPermission
)
from awana_auth.services.iam_audit_service import (
    IAMAuditService,
    AuditAction,
    AuditSeverity,
    AuditEntry
)
from awana_auth.core.database import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.dependencies import get_current_user
from awana_auth.core.models import User

router = APIRouter(prefix="/iam/advanced", tags=["IAM Advanced"])


# ==================== MODÈLES ====================

class GrantTemporaryPermissionRequest(BaseModel):
    user_id: str
    permission_code: str
    duration_hours: int
    reason: Optional[str] = None


class RevokeTemporaryPermissionRequest(BaseModel):
    reason: Optional[str] = None


class AuditSearchRequest(BaseModel):
    action: Optional[str] = None
    actor_id: Optional[str] = None
    target_type: Optional[str] = None
    severity: Optional[str] = None
    result: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None
    limit: int = 100
    skip: int = 0


# ==================== CACHE ENDPOINTS ====================

@router.get("/cache/stats")
async def get_cache_stats(
    cache_service: IAMCacheService = Depends(get_cache_service),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupérer les statistiques du cache Redis
    
    Returns:
        Statistiques détaillées du cache
    """
    stats = await cache_service.get_cache_stats()
    return stats


@router.post("/cache/invalidate/user/{user_id}")
async def invalidate_user_cache(
    user_id: str,
    cache_service: IAMCacheService = Depends(get_cache_service),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Invalider le cache des permissions d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
    """
    success = await cache_service.invalidate_user_permissions(user_id)
    
    # Audit
    audit_service = IAMAuditService(db)
    await audit_service.log_action(
        action=AuditAction.CACHE_INVALIDATED,
        actor_id=current_user.id,
        actor_type="admin",
        target_type="user",
        target_id=user_id,
        details={"cache_type": "user_permissions"}
    )
    
    return {"success": success, "user_id": user_id}


@router.post("/cache/invalidate/all")
async def invalidate_all_cache(
    cache_service: IAMCacheService = Depends(get_cache_service),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("admin.access"))
):
    """
    Invalider TOUT le cache IAM (⚠️ Impact performance)
    """
    success = await cache_service.clear_all_cache()
    
    # Audit
    audit_service = IAMAuditService(db)
    await audit_service.log_action(
        action=AuditAction.CACHE_INVALIDATED,
        actor_id=current_user.id,
        actor_type="admin",
        target_type="cache",
        details={"scope": "all"},
        severity=AuditSeverity.WARNING
    )
    
    return {"success": success, "message": "Cache complet invalidé"}


@router.get("/cache/health")
async def cache_health_check(
    cache_service: IAMCacheService = Depends(get_cache_service),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Vérifier la santé du cache Redis
    """
    health = await cache_service.health_check()
    return health


# ==================== PERMISSIONS TEMPORAIRES ====================

@router.post("/temp-permissions/grant", response_model=TemporaryPermission)
async def grant_temporary_permission(
    request: GrantTemporaryPermissionRequest,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Accorder une permission temporaire à un utilisateur
    
    Args:
        request: Détails de la permission à accorder
    """
    temp_service = TemporaryPermissionsService(db)
    audit_service = IAMAuditService(db)
    
    try:
        temp_perm = await temp_service.grant_temporary_permission(
            user_id=request.user_id,
            permission_code=request.permission_code,
            duration_hours=request.duration_hours,
            granted_by=current_user.id,
            reason=request.reason
        )
        
        # Audit
        await audit_service.log_action(
            action=AuditAction.TEMP_PERMISSION_GRANTED,
            actor_id=current_user.id,
            actor_type="admin",
            target_type="user",
            target_id=request.user_id,
            target_name=request.permission_code,
            details={
                "permission": request.permission_code,
                "duration_hours": request.duration_hours,
                "reason": request.reason
            },
            severity=AuditSeverity.WARNING
        )
        
        # Invalider le cache de l'utilisateur
        cache_service = await get_cache_service()
        await cache_service.invalidate_user_permissions(request.user_id)
        
        return temp_perm
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/temp-permissions/user/{user_id}", response_model=List[TemporaryPermission])
async def get_user_temporary_permissions(
    user_id: str,
    include_expired: bool = False,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupérer toutes les permissions temporaires d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        include_expired: Inclure les permissions expirées
    """
    temp_service = TemporaryPermissionsService(db)
    
    if include_expired:
        perms = await temp_service.get_all_temporary_permissions(user_id, include_expired=True)
    else:
        perms = await temp_service.get_active_temporary_permissions(user_id)
    
    return perms


@router.post("/temp-permissions/{temp_perm_id}/revoke")
async def revoke_temporary_permission(
    temp_perm_id: str,
    request: RevokeTemporaryPermissionRequest,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Révoquer une permission temporaire
    
    Args:
        temp_perm_id: ID de la permission temporaire
        request: Raison de révocation
    """
    temp_service = TemporaryPermissionsService(db)
    audit_service = IAMAuditService(db)
    
    success = await temp_service.revoke_temporary_permission(
        temp_perm_id=temp_perm_id,
        revoked_by=current_user.id,
        reason=request.reason
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Permission temporaire non trouvée")
    
    # Audit
        await audit_service.log_action(
            action=AuditAction.TEMP_PERMISSION_REVOKED,
            actor_id=current_user.id,
            actor_type="admin",
        target_type="temp_permission",
        target_id=temp_perm_id,
        details={"reason": request.reason},
        severity=AuditSeverity.WARNING
    )
    
    return {"success": True, "temp_perm_id": temp_perm_id}


@router.get("/temp-permissions/expiring-soon", response_model=List[TemporaryPermission])
async def get_expiring_soon(
    hours_threshold: int = Query(24, ge=1, le=168),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupérer les permissions qui expirent bientôt
    
    Args:
        hours_threshold: Seuil en heures (1-168)
    """
    temp_service = TemporaryPermissionsService(db)
    perms = await temp_service.get_expiring_soon(hours_threshold=hours_threshold)
    return perms


@router.get("/temp-permissions/statistics")
async def get_temp_permissions_statistics(
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupérer les statistiques des permissions temporaires
    """
    temp_service = TemporaryPermissionsService(db)
    stats = await temp_service.get_statistics()
    return stats


# ==================== AUDIT TRAIL ====================

@router.get("/audit/user/{user_id}", response_model=List[AuditEntry])
async def get_user_audit_trail(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Récupérer l'audit trail d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        limit: Nombre maximum de résultats
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
    """
    audit_service = IAMAuditService(db)
    entries = await audit_service.get_user_actions(
        user_id=user_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    return entries


@router.get("/audit/action/{action}", response_model=List[AuditEntry])
async def get_audit_by_action(
    action: str,
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Récupérer les entrées d'audit par type d'action
    
    Args:
        action: Type d'action (ex: "profile_created")
        limit: Nombre maximum de résultats
        start_date: Date de début (optionnel)
    """
    try:
        audit_action = AuditAction(action)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Action invalide: {action}")
    
    audit_service = IAMAuditService(db)
    entries = await audit_service.get_actions_by_type(
        action=audit_action,
        limit=limit,
        start_date=start_date
    )
    return entries


@router.post("/audit/search")
async def search_audit_trail(
    request: AuditSearchRequest,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Recherche avancée dans l'audit trail
    
    Args:
        request: Critères de recherche
    """
    audit_service = IAMAuditService(db)
    
    filters = request.dict(exclude_none=True)
    results = await audit_service.search_audit_trail(
        filters=filters,
        limit=request.limit,
        skip=request.skip
    )
    
    return results


@router.get("/audit/security-alerts", response_model=List[AuditEntry])
async def get_security_alerts(
    hours_back: int = Query(24, ge=1, le=168),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Récupérer les alertes de sécurité récentes
    
    Args:
        hours_back: Heures en arrière (1-168)
    """
    audit_service = IAMAuditService(db)
    alerts = await audit_service.get_security_alerts(hours_back=hours_back)
    return alerts


@router.get("/audit/statistics")
async def get_audit_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Récupérer les statistiques d'audit
    
    Args:
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
    """
    audit_service = IAMAuditService(db)
    stats = await audit_service.get_statistics(
        start_date=start_date,
        end_date=end_date
    )
    return stats


@router.get("/audit/compliance-report")
async def generate_compliance_report(
    start_date: datetime = Query(..., description="Date de début du rapport"),
    end_date: datetime = Query(..., description="Date de fin du rapport"),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Générer un rapport de conformité (RGPD, SOC2)
    
    Args:
        start_date: Date de début
        end_date: Date de fin
    """
    audit_service = IAMAuditService(db)
    report = await audit_service.generate_compliance_report(
        start_date=start_date,
        end_date=end_date
    )
    return report


@router.get("/audit/failed-actions", response_model=List[AuditEntry])
async def get_failed_actions(
    limit: int = Query(100, ge=1, le=1000),
    hours_back: int = Query(24, ge=1, le=168),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("iam.audit.read"))
):
    """
    Récupérer toutes les actions échouées récentes
    
    Args:
        limit: Nombre maximum de résultats
        hours_back: Heures en arrière
    """
    audit_service = IAMAuditService(db)
    entries = await audit_service.get_failed_actions(
        limit=limit,
        hours_back=hours_back
    )
    return entries
