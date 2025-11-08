"""
Routes pour le versioning de configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.version_models import ConfigurationSnapshot, RollbackRequest, ConfigurationDiff
from awana_auth.core.models import User
from awana_auth.core.config_manager import get_config
from datetime import datetime, timezone
import uuid
from awana_auth.services.email_service import get_email_service

router = APIRouter(prefix="/api/versions", tags=["versioning"])

@router.post("/snapshot", dependencies=[Depends(require_admin)])
async def create_snapshot(
    description: str,
    tags: list[str] = [],
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un snapshot manuel de la configuration actuelle
    Nécessite admin
    """
    config_manager = get_config()
    
    # Récupérer toutes les références actives
    references = {}
    categories = [
        "roles", "user_statuses", "mission_statuses", 
        "application_statuses", "validation_statuses", 
        "validation_types", "contract_types"
    ]
    
    for category in categories:
        refs = await db.system_references.find(
            {"category": category, "is_active": True}
        ).to_list(length=None)
        references[category] = [
            {
                "code": ref["code"],
                "label_fr": ref["label_fr"],
                "label_en": ref.get("label_en", ""),
                "order": ref.get("order", 0)
            }
            for ref in refs
        ]
    
    # Créer le snapshot
    snapshot_id = str(uuid.uuid4())
    version = f"v{datetime.now(timezone.utc).strftime('%Y%m%d.%H%M%S')}"
    
    snapshot = {
        "id": snapshot_id,
        "version": version,
        "description": description,
        "created_at": datetime.now(timezone.utc),
        "created_by": current_user.id,
        "created_by_name": current_user.full_name or current_user.username,
        "snapshot_type": "manual",
        "config_data": {
            "references": references,
            "yaml_config": {
                "roles": config_manager.get("security.roles"),
                "user_statuses": config_manager.get("security.user_statuses"),
            }
        },
        "environment": config_manager.env,
        "tags": tags
    }
    
    await db.configuration_history.insert_one(snapshot)
    
    return {
        "message": "Snapshot créé avec succès",
        "snapshot": {
            "id": snapshot_id,
            "version": version,
            "description": description
        }
    }


@router.get("/list")
async def list_versions(
    limit: int = 50,
    skip: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lister toutes les versions disponibles
    """
    cursor = db.configuration_history.find().sort("created_at", -1).skip(skip).limit(limit)
    versions = await cursor.to_list(length=limit)
    
    # Compter le total
    total = await db.configuration_history.count_documents({})
    
    return {
        "versions": [
            {
                "id": v["id"],
                "version": v["version"],
                "description": v["description"],
                "created_at": v["created_at"],
                "created_by_name": v["created_by_name"],
                "snapshot_type": v["snapshot_type"],
                "tags": v.get("tags", [])
            }
            for v in versions
        ],
        "total": total,
        "limit": limit,
        "skip": skip
    }


@router.get("/{version_id}")
async def get_version_details(
    version_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les détails d'une version spécifique
    """
    version = await db.configuration_history.find_one({"id": version_id})
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version non trouvée"
        )
    
    return version


@router.post("/rollback", dependencies=[Depends(require_admin)])
async def rollback_to_version(
    rollback: RollbackRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Rollback vers une version antérieure
    Nécessite admin
    Envoie une notification email aux admins
    """
    # Récupérer la version cible
    target_version = await db.configuration_history.find_one({"id": rollback.version_id})
    
    if not target_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version cible non trouvée"
        )
    
    # Créer un snapshot de la config actuelle avant rollback
    await create_snapshot(
        description=f"Auto-snapshot avant rollback vers {target_version['version']}",
        tags=["auto", "pre-rollback"],
        current_user=current_user,
        db=db
    )
    
    # Appliquer le rollback pour les références
    config_data = target_version["config_data"]
    references = config_data.get("references", {})
    
    # Pour chaque catégorie, désactiver toutes les refs actuelles
    # et recréer celles de la version cible
    for category, refs in references.items():
        # Désactiver toutes les références actuelles
        await db.system_references.update_many(
            {"category": category},
            {"$set": {"is_active": False}}
        )
        
        # Recréer les références de la version cible
        for ref in refs:
            existing = await db.system_references.find_one({
                "category": category,
                "code": ref["code"]
            })
            
            if existing:
                # Mettre à jour
                await db.system_references.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "label_fr": ref["label_fr"],
                        "label_en": ref.get("label_en", ""),
                        "order": ref.get("order", 0),
                        "is_active": True
                    }}
                )
            else:
                # Créer nouveau
                await db.system_references.insert_one({
                    "id": str(uuid.uuid4()),
                    "category": category,
                    "code": ref["code"],
                    "label_fr": ref["label_fr"],
                    "label_en": ref.get("label_en", ""),
                    "order": ref.get("order", 0),
                    "is_active": True,
                    "is_system": False
                })
    
    # Logger le rollback
    current_version_snapshot = await db.configuration_history.find_one(
        {"snapshot_type": {"$ne": "rollback"}},
        sort=[("created_at", -1)]
    )
    
    await db.configuration_history.insert_one({
        "id": str(uuid.uuid4()),
        "version": f"rollback-{datetime.now(timezone.utc).strftime('%Y%m%d.%H%M%S')}",
        "description": f"Rollback vers {target_version['version']}: {rollback.reason}",
        "created_at": datetime.now(timezone.utc),
        "created_by": current_user.id,
        "created_by_name": current_user.full_name or current_user.username,
        "snapshot_type": "rollback",
        "config_data": config_data,
        "environment": "production",
        "tags": ["rollback"]
    })
    
    # Envoyer notification email en arrière-plan
    email_service = get_email_service()
    if email_service.is_configured():
        # Calculer les changements si possible
        changes_summary = None
        if current_version_snapshot:
            try:
                # Compter les changements basiques
                current_refs = set()
                target_refs = set()
                
                for cat, refs in current_version_snapshot.get("config_data", {}).get("references", {}).items():
                    for ref in refs:
                        current_refs.add(f"{cat}.{ref.get('code')}")
                
                for cat, refs in config_data.get("references", {}).items():
                    for ref in refs:
                        target_refs.add(f"{cat}.{ref.get('code')}")
                
                changes_summary = {
                    "added": len(target_refs - current_refs),
                    "removed": len(current_refs - target_refs),
                    "modified": 0  # Simplification
                }
            except:
                pass
        
        background_tasks.add_task(
            email_service.send_rollback_notification,
            actor_name=current_user.full_name or current_user.username,
            version_from=current_version_snapshot.get("version", "current") if current_version_snapshot else "current",
            version_to=target_version["version"],
            reason=rollback.reason,
            rollback_time=datetime.now(timezone.utc),
            changes_summary=changes_summary
        )
    
    return {
        "message": "Rollback effectué avec succès",
        "version": target_version["version"],
        "reason": rollback.reason,
        "email_notification": "sent" if email_service.is_configured() else "disabled"
    }


@router.get("/compare/{version_id_from}/{version_id_to}")
async def compare_versions(
    version_id_from: str,
    version_id_to: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Comparer deux versions et retourner les différences
    """
    version_from = await db.configuration_history.find_one({"id": version_id_from})
    version_to = await db.configuration_history.find_one({"id": version_id_to})
    
    if not version_from or not version_to:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Une ou plusieurs versions non trouvées"
        )
    
    # Comparer les références
    refs_from = version_from["config_data"].get("references", {})
    refs_to = version_to["config_data"].get("references", {})
    
    changes = {}
    added = []
    removed = []
    modified = []
    
    # Comparer chaque catégorie
    all_categories = set(refs_from.keys()) | set(refs_to.keys())
    
    for category in all_categories:
        refs_from_cat = {r["code"]: r for r in refs_from.get(category, [])}
        refs_to_cat = {r["code"]: r for r in refs_to.get(category, [])}
        
        # Nouveaux
        for code in set(refs_to_cat.keys()) - set(refs_from_cat.keys()):
            added.append(f"{category}.{code}")
        
        # Supprimés
        for code in set(refs_from_cat.keys()) - set(refs_to_cat.keys()):
            removed.append(f"{category}.{code}")
        
        # Modifiés
        for code in set(refs_from_cat.keys()) & set(refs_to_cat.keys()):
            if refs_from_cat[code] != refs_to_cat[code]:
                modified.append(f"{category}.{code}")
                changes[f"{category}.{code}"] = {
                    "from": refs_from_cat[code],
                    "to": refs_to_cat[code]
                }
    
    return {
        "version_from": version_from["version"],
        "version_to": version_to["version"],
        "added": added,
        "removed": removed,
        "modified": modified,
        "changes": changes
    }
