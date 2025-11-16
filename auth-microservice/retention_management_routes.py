"""
Routes de Gestion de la Politique de Rétention
Endpoints pour gérer le workflow de rétention en 4 étapes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List, Dict
from pydantic import BaseModel
import logging

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.services.retention_workflow_service import RetentionWorkflowService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/retention", tags=["retention-management"])


# ==================== MODELS ====================

class RetentionStats(BaseModel):
    """Statistiques du workflow de rétention"""
    retention_period_days: int
    archived_users: int
    pending_deletion_users: int  # J-7
    to_delete_users: int  # J (masqués)
    eligible_for_j_minus_7: int
    eligible_for_j_minus_3: int
    eligible_for_j: int
    eligible_for_j_plus_3: int


class WorkflowExecutionResult(BaseModel):
    """Résultat de l'exécution du workflow"""
    status: str
    execution_time: str
    summary: Dict
    stages: Dict


class UserRetentionDetail(BaseModel):
    """Détails d'un utilisateur dans le workflow"""
    id: str
    username: str
    email: str
    status: str
    archived_at: str
    deletion_scheduled_at: str
    current_stage: str
    days_until_deletion: int
    notifications_sent: List[Dict]


# ==================== ROUTES ====================

@router.get("/stats", response_model=RetentionStats)
async def get_retention_stats(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Obtenir les statistiques du workflow de rétention
    """
    workflow_service = RetentionWorkflowService(db)
    retention_days = await workflow_service.get_retention_period()
    now = datetime.now(timezone.utc)
    
    from datetime import timedelta
    
    # Compteurs
    archived_count = await db.users.count_documents({"status": "archived"})
    pending_deletion_count = await db.users.count_documents({"status": "pending_deletion"})
    to_delete_count = await db.users.count_documents({"status": "to_delete"})
    
    # Éligibles pour J-7 (7 jours avant suppression)
    j_minus_7_threshold = now + timedelta(days=7)
    eligible_j_minus_7 = await db.users.count_documents({
        "status": "archived",
        "deletion_scheduled_at": {
            "$lte": j_minus_7_threshold,
            "$gt": now
        },
        "pending_deletion_at": None
    })
    
    # Éligibles pour rappel J-3
    j_minus_3_threshold = now + timedelta(days=3)
    eligible_j_minus_3 = await db.users.count_documents({
        "status": "pending_deletion",
        "deletion_scheduled_at": {
            "$lte": j_minus_3_threshold,
            "$gt": now
        },
        "notifications_sent": {
            "$not": {"$elemMatch": {"type": "J-3"}}
        }
    })
    
    # Éligibles pour J (masquage)
    eligible_j = await db.users.count_documents({
        "status": "pending_deletion",
        "deletion_scheduled_at": {"$lte": now},
        "to_delete_at": None
    })
    
    # Éligibles pour J+3 (suppression définitive)
    eligible_j_plus_3 = await db.users.count_documents({
        "status": "to_delete",
        "soft_deleted_at": {"$lte": now}
    })
    
    return RetentionStats(
        retention_period_days=retention_days,
        archived_users=archived_count,
        pending_deletion_users=pending_deletion_count,
        to_delete_users=to_delete_count,
        eligible_for_j_minus_7=eligible_j_minus_7,
        eligible_for_j_minus_3=eligible_j_minus_3,
        eligible_for_j=eligible_j,
        eligible_for_j_plus_3=eligible_j_plus_3
    )


@router.post("/execute", response_model=WorkflowExecutionResult)
async def execute_retention_workflow(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Exécuter manuellement le workflow de rétention complet
    Traite toutes les étapes: J-7, J-3, J, J+3
    """
    workflow_service = RetentionWorkflowService(db)
    
    # Enregistrer qui a déclenché l'exécution manuelle
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    logger.info(f"Manual retention workflow execution triggered by {actor_id}")
    
    results = await workflow_service.execute_full_workflow()
    
    return WorkflowExecutionResult(
        status=results.get("status", "unknown"),
        execution_time=results.get("execution_time", ""),
        summary=results.get("summary", {}),
        stages=results.get("stages", {})
    )


@router.get("/users/in-workflow", response_model=List[UserRetentionDetail])
async def get_users_in_workflow(
    status_filter: str = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Lister les utilisateurs dans le workflow de rétention
    Filtrage optionnel par statut: archived, pending_deletion, to_delete
    """
    query = {"status": {"$in": ["archived", "pending_deletion", "to_delete"]}}
    
    if status_filter:
        query["status"] = status_filter
    
    users = await db.users.find(
        query,
        {
            "_id": 0,
            "id": 1,
            "username": 1,
            "email": 1,
            "status": 1,
            "archived_at": 1,
            "deletion_scheduled_at": 1,
            "pending_deletion_at": 1,
            "to_delete_at": 1,
            "notifications_sent": 1
        }
    ).to_list(length=1000)
    
    now = datetime.now(timezone.utc)
    result = []
    
    for user in users:
        deletion_date = user.get("deletion_scheduled_at")
        
        if isinstance(deletion_date, datetime):
            days_until = (deletion_date - now).days
        else:
            days_until = -1
        
        # Déterminer le stage actuel
        if user["status"] == "archived":
            current_stage = "Initial (Archived)"
        elif user["status"] == "pending_deletion":
            if user.get("pending_deletion_at"):
                current_stage = "J-7 (Pending Deletion)"
            else:
                current_stage = "Pending J-7 notification"
        elif user["status"] == "to_delete":
            current_stage = "J (Hidden - Superadmin only)"
        else:
            current_stage = "Unknown"
        
        result.append(UserRetentionDetail(
            id=user["id"],
            username=user["username"],
            email=user.get("email", ""),
            status=user["status"],
            archived_at=user.get("archived_at", "").isoformat() if isinstance(user.get("archived_at"), datetime) else "",
            deletion_scheduled_at=deletion_date.isoformat() if isinstance(deletion_date, datetime) else "",
            current_stage=current_stage,
            days_until_deletion=days_until,
            notifications_sent=user.get("notifications_sent", [])
        ))
    
    return result


@router.get("/notifications")
async def get_retention_notifications(
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Récupérer les notifications de rétention récentes
    """
    notifications = await db.retention_notifications.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {
        "notifications": notifications,
        "total": len(notifications)
    }


@router.get("/config")
async def get_retention_config(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Obtenir la configuration actuelle de la rétention
    """
    setting = await db.app_settings.find_one({"key": "security.user_retention_days"})
    
    retention_days = 90  # Défaut
    source = "default"
    
    if setting and setting.get("value"):
        retention_days = int(setting["value"])
        source = "database"
    
    return {
        "retention_days": retention_days,
        "source": source,
        "workflow_stages": {
            "j_minus_7": {
                "description": "7 jours avant expiration - Notification gestionnaires",
                "action": "Passage à PENDING_DELETION"
            },
            "j_minus_3": {
                "description": "3 jours avant expiration - Rappel gestionnaires",
                "action": "Rappel par notification"
            },
            "j": {
                "description": "Jour J - Suppression de la visibilité",
                "action": "Passage à TO_DELETE (visible superadmin uniquement)"
            },
            "j_plus_3": {
                "description": "J+3 + 1h - Suppression définitive",
                "action": "Notification superadmin puis suppression"
            }
        }
    }


@router.put("/config")
async def update_retention_config(
    retention_days: int,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Mettre à jour la période de rétention globale
    """
    if retention_days < 7:
        raise HTTPException(
            status_code=400,
            detail="Le délai de rétention doit être d'au moins 7 jours"
        )
    
    if retention_days > 3650:  # 10 ans max
        raise HTTPException(
            status_code=400,
            detail="Le délai de rétention ne peut pas dépasser 3650 jours (10 ans)"
        )
    
    now = datetime.now(timezone.utc)
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    await db.app_settings.update_one(
        {"key": "security.user_retention_days"},
        {
            "$set": {
                "key": "security.user_retention_days",
                "value": retention_days,
                "updated_at": now,
                "updated_by": actor_id
            }
        },
        upsert=True
    )
    
    # Audit
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "retention_config.update",
        "actor_id": actor_id,
        "actor_username": current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "username", None),
        "target_type": "config",
        "target_id": "security.user_retention_days",
        "payload": {"new_value": retention_days},
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Retention period updated to {retention_days} days by {actor_id}")
    
    return {
        "message": "Configuration de rétention mise à jour avec succès",
        "retention_days": retention_days,
        "source": "database"
    }


import uuid
