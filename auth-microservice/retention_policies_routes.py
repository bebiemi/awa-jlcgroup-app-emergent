"""
Routes de Gestion des Politiques de Rétention Multi-Entités
Permet de configurer les délais de rétention pour différents types de données
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List
import logging
import uuid

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.core.retention_models import (
    RetentionPolicyConfig,
    RetentionPolicyResponse,
    RetentionPolicyListResponse,
    CreateRetentionPolicyRequest,
    UpdateRetentionPolicyRequest,
    RetentionStatsResponse,
    RetentionEntityType,
    RetentionWorkflowStage
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/retention-policies", tags=["retention-policies"])


# ==================== HELPERS ====================

async def get_default_workflow_for_users() -> List[RetentionWorkflowStage]:
    """Workflow par défaut pour les utilisateurs"""
    return [
        RetentionWorkflowStage(
            stage_name="J-7",
            days_before_deletion=7,
            action="notification_and_status_change",
            notification_recipients=["admin", "user_manager", "rh_manager"],
            status_transition="pending_deletion",
            description="Notification gestionnaires - Passage à PENDING_DELETION"
        ),
        RetentionWorkflowStage(
            stage_name="J-3",
            days_before_deletion=3,
            action="notification",
            notification_recipients=["admin", "user_manager", "rh_manager"],
            status_transition=None,
            description="Rappel aux gestionnaires"
        ),
        RetentionWorkflowStage(
            stage_name="J",
            days_before_deletion=0,
            action="status_change_and_notification",
            notification_recipients=["admin", "user_manager", "rh_manager", "super_admin"],
            status_transition="to_delete",
            description="Masquage - Visible superadmin uniquement"
        ),
        RetentionWorkflowStage(
            stage_name="J+3",
            days_before_deletion=-3,
            action="notification_and_delete",
            notification_recipients=["super_admin"],
            status_transition="deleted",
            description="Suppression définitive après notification 1h avant"
        )
    ]


async def policy_to_response(policy: dict) -> RetentionPolicyResponse:
    """Convertir un document de politique en réponse API"""
    return RetentionPolicyResponse(
        id=policy["id"],
        entity_type=policy["entity_type"],
        entity_label=policy["entity_label"],
        retention_days=policy["retention_days"],
        is_enabled=policy.get("is_enabled", True),
        status=policy.get("status", "active"),
        workflow_stages_count=len(policy.get("workflow_stages", [])),
        created_at=policy["created_at"].isoformat() if isinstance(policy.get("created_at"), datetime) else "",
        updated_at=policy["updated_at"].isoformat() if isinstance(policy.get("updated_at"), datetime) else "",
        description=policy.get("description")
    )


# ==================== ROUTES ====================

@router.get("", response_model=RetentionPolicyListResponse)
async def list_retention_policies(
    entity_type: str = None,
    enabled_only: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Lister toutes les politiques de rétention configurées
    Filtrage optionnel par type d'entité
    """
    query = {}
    
    if entity_type:
        query["entity_type"] = entity_type
    
    if enabled_only:
        query["is_enabled"] = True
    
    policies = await db.retention_policies.find(query, {"_id": 0}).to_list(length=None)
    
    responses = [await policy_to_response(p) for p in policies]
    
    return RetentionPolicyListResponse(
        policies=responses,
        total=len(responses)
    )


@router.get("/stats", response_model=RetentionStatsResponse)
async def get_retention_stats(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Obtenir les statistiques globales des politiques de rétention
    """
    # Compter les politiques
    total_policies = await db.retention_policies.count_documents({})
    active_policies = await db.retention_policies.count_documents({"is_enabled": True})
    inactive_policies = total_policies - active_policies
    
    # Compter les entités en rétention
    entities_count = {
        "users": await db.users.count_documents({"status": {"$in": ["archived", "pending_deletion", "to_delete"]}}),
        "documents": 0,  # À implémenter
        "missions": 0,   # À implémenter
        "companies": 0   # À implémenter
    }
    
    # Grouper par type d'entité
    policies = await db.retention_policies.find({}, {"_id": 0}).to_list(length=None)
    policies_by_entity = {}
    
    for policy in policies:
        entity_type = policy["entity_type"]
        policies_by_entity[entity_type] = {
            "retention_days": policy["retention_days"],
            "is_enabled": policy.get("is_enabled", True),
            "workflow_stages": len(policy.get("workflow_stages", []))
        }
    
    return RetentionStatsResponse(
        total_policies=total_policies,
        active_policies=active_policies,
        inactive_policies=inactive_policies,
        total_entities_in_retention=entities_count,
        policies_by_entity=policies_by_entity
    )


@router.get("/{policy_id}", response_model=RetentionPolicyConfig)
async def get_retention_policy(
    policy_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_READ))
):
    """
    Obtenir les détails d'une politique de rétention
    """
    policy = await db.retention_policies.find_one({"id": policy_id}, {"_id": 0})
    
    if not policy:
        raise HTTPException(status_code=404, detail="Politique de rétention non trouvée")
    
    return RetentionPolicyConfig(**policy)


@router.post("", response_model=RetentionPolicyResponse)
async def create_retention_policy(
    request: CreateRetentionPolicyRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Créer une nouvelle politique de rétention pour un type d'entité
    """
    # Vérifier si une politique existe déjà pour ce type
    existing = await db.retention_policies.find_one({"entity_type": request.entity_type})
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Une politique existe déjà pour {request.entity_type}. Utilisez PUT pour la mettre à jour."
        )
    
    now = datetime.now(timezone.utc)
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    policy_id = str(uuid.uuid4())
    
    # Utiliser le workflow par défaut pour les utilisateurs si non fourni
    workflow_stages = request.workflow_stages
    if not workflow_stages and request.entity_type == RetentionEntityType.USERS:
        workflow_stages = await get_default_workflow_for_users()
    
    policy_doc = {
        "id": policy_id,
        "entity_type": request.entity_type,
        "entity_label": request.entity_label,
        "retention_days": request.retention_days,
        "is_enabled": True,
        "status": "active",
        "workflow_stages": [stage.dict() for stage in workflow_stages],
        "auto_archive": request.auto_archive,
        "soft_delete": request.soft_delete,
        "keep_audit_trail": request.keep_audit_trail,
        "description": request.description,
        "legal_basis": request.legal_basis,
        "created_at": now,
        "updated_at": now,
        "created_by": actor_id,
        "updated_by": actor_id
    }
    
    await db.retention_policies.insert_one(policy_doc)
    
    # Audit
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "retention_policy.create",
        "actor_id": actor_id,
        "actor_username": current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "username", None),
        "target_type": "retention_policy",
        "target_id": policy_id,
        "payload": {
            "entity_type": request.entity_type,
            "retention_days": request.retention_days
        },
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Retention policy created for {request.entity_type} by {actor_id}")
    
    return await policy_to_response(policy_doc)


@router.put("/{policy_id}", response_model=RetentionPolicyResponse)
async def update_retention_policy(
    policy_id: str,
    request: UpdateRetentionPolicyRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Mettre à jour une politique de rétention existante
    """
    policy = await db.retention_policies.find_one({"id": policy_id})
    
    if not policy:
        raise HTTPException(status_code=404, detail="Politique de rétention non trouvée")
    
    now = datetime.now(timezone.utc)
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    # Préparer les mises à jour
    update_data = {
        "updated_at": now,
        "updated_by": actor_id
    }
    
    if request.entity_label is not None:
        update_data["entity_label"] = request.entity_label
    
    if request.retention_days is not None:
        update_data["retention_days"] = request.retention_days
    
    if request.is_enabled is not None:
        update_data["is_enabled"] = request.is_enabled
        update_data["status"] = "active" if request.is_enabled else "inactive"
    
    if request.workflow_stages is not None:
        update_data["workflow_stages"] = [stage.dict() for stage in request.workflow_stages]
    
    if request.description is not None:
        update_data["description"] = request.description
    
    if request.legal_basis is not None:
        update_data["legal_basis"] = request.legal_basis
    
    if request.auto_archive is not None:
        update_data["auto_archive"] = request.auto_archive
    
    if request.soft_delete is not None:
        update_data["soft_delete"] = request.soft_delete
    
    if request.keep_audit_trail is not None:
        update_data["keep_audit_trail"] = request.keep_audit_trail
    
    # Mettre à jour
    await db.retention_policies.update_one(
        {"id": policy_id},
        {"$set": update_data}
    )
    
    # Audit
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "retention_policy.update",
        "actor_id": actor_id,
        "actor_username": current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "username", None),
        "target_type": "retention_policy",
        "target_id": policy_id,
        "payload": update_data,
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Retention policy {policy_id} updated by {actor_id}")
    
    # Récupérer la politique mise à jour
    updated_policy = await db.retention_policies.find_one({"id": policy_id}, {"_id": 0})
    
    return await policy_to_response(updated_policy)


@router.delete("/{policy_id}")
async def delete_retention_policy(
    policy_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Supprimer une politique de rétention
    Note: Cela ne supprime pas les entités, seulement la configuration
    """
    policy = await db.retention_policies.find_one({"id": policy_id})
    
    if not policy:
        raise HTTPException(status_code=404, detail="Politique de rétention non trouvée")
    
    now = datetime.now(timezone.utc)
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    # Supprimer
    result = await db.retention_policies.delete_one({"id": policy_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Échec de la suppression")
    
    # Audit
    await db.audit_events.insert_one({
        "id": str(uuid.uuid4()),
        "action": "retention_policy.delete",
        "actor_id": actor_id,
        "actor_username": current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "username", None),
        "target_type": "retention_policy",
        "target_id": policy_id,
        "payload": {
            "entity_type": policy["entity_type"]
        },
        "timestamp": now,
        "ip_address": None,
        "user_agent": None
    })
    
    logger.info(f"Retention policy {policy_id} deleted by {actor_id}")
    
    return {
        "message": "Politique de rétention supprimée avec succès",
        "policy_id": policy_id
    }


@router.post("/initialize-defaults")
async def initialize_default_policies(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE))
):
    """
    Initialiser les politiques de rétention par défaut pour tous les types d'entités
    Utilisé lors de la première configuration
    """
    now = datetime.now(timezone.utc)
    actor_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    
    default_policies = [
        {
            "entity_type": "users",
            "entity_label": "Utilisateurs",
            "retention_days": 90,
            "description": "Politique de rétention pour les comptes utilisateurs archivés",
            "legal_basis": "RGPD Art. 17 - Droit à l'effacement"
        },
        {
            "entity_type": "documents",
            "entity_label": "Documents",
            "retention_days": 365,
            "description": "Conservation des documents uploadés (CV, justificatifs)",
            "legal_basis": "Code du travail - Conservation 5 ans max"
        },
        {
            "entity_type": "missions",
            "entity_label": "Missions",
            "retention_days": 1825,  # 5 ans
            "description": "Archive des missions terminées",
            "legal_basis": "Conservation archives comptables"
        },
        {
            "entity_type": "companies",
            "entity_label": "Entreprises",
            "retention_days": 3650,  # 10 ans
            "description": "Données des entreprises clientes",
            "legal_basis": "Obligations comptables et fiscales"
        }
    ]
    
    created_count = 0
    
    for policy_data in default_policies:
        # Vérifier si existe déjà
        existing = await db.retention_policies.find_one({"entity_type": policy_data["entity_type"]})
        
        if not existing:
            policy_id = str(uuid.uuid4())
            
            # Workflow par défaut pour utilisateurs
            workflow_stages = []
            if policy_data["entity_type"] == "users":
                workflow_stages = await get_default_workflow_for_users()
            
            policy_doc = {
                "id": policy_id,
                **policy_data,
                "is_enabled": True,
                "status": "active",
                "workflow_stages": [stage.dict() for stage in workflow_stages],
                "auto_archive": True,
                "soft_delete": True,
                "keep_audit_trail": True,
                "created_at": now,
                "updated_at": now,
                "created_by": actor_id,
                "updated_by": actor_id,
                "notes": "Politique créée automatiquement lors de l'initialisation"
            }
            
            await db.retention_policies.insert_one(policy_doc)
            created_count += 1
            
            logger.info(f"Default retention policy created for {policy_data['entity_type']}")
    
    return {
        "message": f"{created_count} politiques de rétention par défaut créées",
        "created_count": created_count
    }
