"""
Routes API pour la gestion des Feature Flags
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.models import User
from awana_auth.core.feature_flag_models import (
    FeatureFlag,
    FeatureFlagType,
    FeatureFlagContext,
    CreateFeatureFlagRequest,
    UpdateFeatureFlagRequest,
    RolloutRequest,
)
from awana_auth.services.feature_flag_service import FeatureFlagService


router = APIRouter(prefix="/api/feature-flags", tags=["feature-flags"])


@router.get("/check/{flag_key}")
async def check_feature_flag(
    flag_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Vérifier si un feature flag est activé pour l'utilisateur actuel
    """
    service = FeatureFlagService(db)
    
    context = FeatureFlagContext(
        user_id=current_user.id,
        roles=current_user.roles,
        environment="production"  # TODO: récupérer depuis config
    )
    
    is_enabled = await service.is_enabled(flag_key, context)
    
    return {
        "flag_key": flag_key,
        "enabled": is_enabled,
        "user_id": current_user.id,
        "roles": current_user.roles
    }


@router.get("")
async def list_feature_flags(
    include_inactive: bool = Query(False),
    type_filter: Optional[FeatureFlagType] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lister tous les feature flags
    Filtrés selon les permissions de l'utilisateur
    """
    service = FeatureFlagService(db)
    
    flags = await service.get_all_flags(
        caller_roles=current_user.roles,
        include_inactive=include_inactive
    )
    
    # Filtrer par type si spécifié
    if type_filter:
        flags = [f for f in flags if f['type'] == type_filter.value]
    
    return {
        "flags": flags,
        "total": len(flags),
        "can_create": "super_admin" in current_user.roles
    }


@router.post("", dependencies=[Depends(require_permission("flags.manage"))])
async def create_feature_flag(
    request: CreateFeatureFlagRequest,
    current_user: User = Depends(require_permission("flags.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un nouveau feature flag
    Réservé aux super admins
    """
    service = FeatureFlagService(db)
    
    try:
        flag = await service.create_flag(
            request=request,
            created_by=current_user.id,
            actor_name=current_user.full_name or current_user.username
        )
        
        return {
            "message": "Feature flag créé avec succès",
            "flag": flag
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{flag_id}", dependencies=[Depends(require_permission("flags.manage"))])
async def update_feature_flag(
    flag_id: str,
    request: UpdateFeatureFlagRequest,
    current_user: User = Depends(require_permission("flags.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un feature flag
    Réservé aux super admins
    """
    service = FeatureFlagService(db)
    
    try:
        flag = await service.update_flag(
            flag_id=flag_id,
            request=request,
            updated_by=current_user.id,
            actor_name=current_user.full_name or current_user.username
        )
        
        return {
            "message": "Feature flag mis à jour avec succès",
            "flag": flag
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{flag_id}", dependencies=[Depends(require_permission("flags.manage"))])
async def delete_feature_flag(
    flag_id: str,
    current_user: User = Depends(require_permission("flags.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Supprimer un feature flag
    Réservé aux super admins
    """
    service = FeatureFlagService(db)
    
    try:
        await service.delete_flag(
            flag_id=flag_id,
            deleted_by=current_user.id,
            actor_name=current_user.full_name or current_user.username
        )
        
        return {
            "message": "Feature flag supprimé avec succès"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{flag_id}/rollout", dependencies=[Depends(require_permission("flags.manage"))])
async def apply_rollout(
    flag_id: str,
    request: RolloutRequest,
    current_user: User = Depends(require_permission("flags.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Appliquer un rollout progressif à un feature flag
    Réservé aux super admins
    """
    service = FeatureFlagService(db)
    
    try:
        flag = await service.apply_rollout(
            flag_id=flag_id,
            rollout_percentage=request.rollout_percentage,
            applied_by=current_user.id,
            actor_name=current_user.full_name or current_user.username,
            description=request.description
        )
        
        return {
            "message": f"Rollout appliqué: {request.rollout_percentage}%",
            "flag": flag
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{flag_id}/history")
async def get_flag_history(
    flag_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer l'historique d'audit d'un feature flag
    """
    service = FeatureFlagService(db)
    
    events = await service.get_audit_history(
        target_type="feature_flag",
        target_id=flag_id,
        limit=limit
    )
    
    return {
        "flag_id": flag_id,
        "events": events,
        "total": len(events)
    }


@router.get("/audit/all")
async def get_all_audit_events(
    limit: int = Query(50, ge=1, le=100),
    target_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer tous les événements d'audit
    Filtré par target_type si spécifié
    """
    # Seuls les admins peuvent voir les audits
    if "admin" not in current_user.roles and "super_admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : admin requis"
        )
    
    service = FeatureFlagService(db)
    
    events = await service.get_audit_history(
        target_type=target_type,
        limit=limit
    )
    
    return {
        "events": events,
        "total": len(events),
        "filtered_by": target_type
    }


@router.get("/export", dependencies=[Depends(require_permission("flags.manage"))])
async def export_feature_flags(
    current_user: User = Depends(require_permission("flags.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Exporter tous les feature flags au format JSON
    Réservé aux super-admins
    """
    from fastapi.responses import JSONResponse
    import json
    from datetime import datetime
    
    service = FeatureFlagService(db)
    flags = await service.get_all_flags(
        caller_roles=current_user.roles,
        include_inactive=True
    )
    
    export_data = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "exported_by": current_user.username,
        "total_flags": len(flags),
        "flags": flags
    }
    
    # Audit
    await service._create_audit_event(
        actor_id=current_user.id,
        actor_name=current_user.full_name or current_user.username,
        action=AuditEventType.FEATURE_FLAG_CREATED,  # Using existing type
        target_type="export",
        target_id=None,
        payload={
            "action": "export_all_flags",
            "total_exported": len(flags)
        }
    )
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename=feature_flags_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@router.post("/import", dependencies=[Depends(require_permission("flags.manage"))])
async def import_feature_flags(
    import_data: dict,
    overwrite: bool = Query(False, description="Overwrite existing flags with same key"),
    current_user: User = Depends(require_permission("flags.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Importer des feature flags depuis un fichier JSON
    Réservé aux super-admins
    """
    service = FeatureFlagService(db)
    
    if "flags" not in import_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format invalide: 'flags' requis"
        )
    
    flags_to_import = import_data["flags"]
    results = {
        "total": len(flags_to_import),
        "imported": 0,
        "skipped": 0,
        "errors": []
    }
    
    for flag_data in flags_to_import:
        try:
            # Vérifier si existe déjà
            existing = await db.feature_flags.find_one({"key": flag_data["key"]})
            
            if existing and not overwrite:
                results["skipped"] += 1
                continue
            
            if existing and overwrite:
                # Mettre à jour
                await db.feature_flags.update_one(
                    {"key": flag_data["key"]},
                    {"$set": {
                        "type": flag_data["type"],
                        "value": flag_data["value"],
                        "target": flag_data.get("target"),
                        "metadata": flag_data.get("metadata", {}),
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                results["imported"] += 1
            else:
                # Créer nouveau
                flag_data["created_by"] = current_user.id
                flag_data["created_at"] = datetime.now(timezone.utc)
                flag_data["updated_at"] = datetime.now(timezone.utc)
                await db.feature_flags.insert_one(flag_data)
                results["imported"] += 1
                
        except Exception as e:
            results["errors"].append({
                "key": flag_data.get("key", "unknown"),
                "error": str(e)
            })
    
    # Audit
    await service._create_audit_event(
        actor_id=current_user.id,
        actor_name=current_user.full_name or current_user.username,
        action=AuditEventType.FEATURE_FLAG_CREATED,
        target_type="import",
        target_id=None,
        payload={
            "action": "import_flags",
            "total": results["total"],
            "imported": results["imported"],
            "skipped": results["skipped"],
            "errors_count": len(results["errors"])
        }
    )
    
    # Invalider cache
    service._invalidate_cache()
    
    return {
        "message": f"Import terminé: {results['imported']} importés, {results['skipped']} ignorés",
        "results": results
    }
