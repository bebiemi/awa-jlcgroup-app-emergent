"""
Entreprise Grouping Routes
Phase 4: Workflow de regroupement d'entreprises
Permet aux entreprises liées de demander un regroupement avec validation double
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4

from awana_auth.core.models import User
from awana_auth.core.dependencies import get_database, get_current_user, get_iam_service
from awana_auth.services.iam_service import IAMService
from awana_auth.utils.iam_helpers import get_resource_filter
from awana_auth.dependencies.permission_dependencies import require_permission
from pydantic import BaseModel

grouping_router = APIRouter(prefix="/entreprises/grouping", tags=["Entreprise Grouping"])


class GroupingRequest(BaseModel):
    """Model for grouping request creation"""
    entreprise_2_id: str
    reason: Optional[str] = None


class GroupingApproval(BaseModel):
    """Model for approving grouping request"""
    notes: Optional[str] = None


class GroupingRejection(BaseModel):
    """Model for rejecting grouping request"""
    rejection_reason: str
    notes: Optional[str] = None


async def get_user_company_ids(current_user: User, db: AsyncIOMotorDatabase) -> list[str]:
    """Récupère les IDs d'entreprise associés à l'utilisateur (attributs + fallback DB)."""
    ids = set()
    attr_id = getattr(current_user, "company_id", None) or getattr(current_user, "entreprise_id", None)
    if attr_id:
        ids.add(attr_id)
    user_doc = await db.users.find_one({"id": current_user.id}) if hasattr(current_user, "id") else None
    if user_doc:
        for key in ("company_id", "entreprise_id"):
            if user_doc.get(key):
                ids.add(user_doc[key])
    # Legacy mapping
    entreprises = await db.entreprises.find({"user_id": current_user.id}, {"_id": 0, "id": 1}).to_list(None)
    ids.update(e["id"] for e in entreprises)
    return list(ids)


async def ensure_grouping_scope(
    iam_service: IAMService,
    user_id: str,
    user_company_id: Optional[str],
    target_entreprise_id: str,
    action: str,
):
    """Vérifie le scope IAM (all/own) pour les regroupements."""
    iam_filter = await get_resource_filter(
        iam_service,
        user_id,
        user_company_id,
        "entreprises",
        action
    )
    if iam_filter is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )
    allowed = iam_filter.get("entreprise_id") or iam_filter.get("id")
    if iam_filter and allowed and target_entreprise_id != allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès restreint à votre périmètre"
        )


@grouping_router.post("/request")
async def create_grouping_request(
    request_data: GroupingRequest,
    current_user: User = Depends(require_permission("entreprises.group_request")),
    iam_service: IAMService = Depends(get_iam_service),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer une demande de regroupement entre deux entreprises
    
    Règles:
    - Les deux entreprises doivent être "linked" (rattachées)
    - L'utilisateur doit avoir accès aux deux entreprises
    - Génère automatiquement une demande envoyée aux admins des deux entreprises
    """
    
    user_companies = await get_user_company_ids(current_user, db)
    entreprise_1_id = user_companies[0] if user_companies else None
    if not entreprise_1_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise de l'utilisateur non trouvée"
        )
    entreprise_1 = await db.entreprises.find_one({"id": entreprise_1_id}, {"_id": 0})
    
    # Récupérer l'entreprise cible
    entreprise_2 = await db.entreprises.find_one(
        {"id": request_data.entreprise_2_id},
        {"_id": 0}
    )
    
    if not entreprise_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise cible non trouvée"
        )
    
    # Vérifier les scopes IAM (.own/.all) côté utilisateur sur l'entreprise source
    await ensure_grouping_scope(
        iam_service,
        current_user.id,
        entreprise_1_id,
        entreprise_1_id,
        "group"
    )
    
    # Vérifier que les deux entreprises sont liées
    if (entreprise_2["id"] not in entreprise_1.get("linked_entreprises", []) or
        entreprise_1["id"] not in entreprise_2.get("linked_entreprises", [])):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les deux entreprises doivent être rattachées avant de demander un regroupement"
        )
    
    # Vérifier qu'il n'existe pas déjà une demande en cours
    existing_request = await db.entreprise_grouping_requests.find_one({
        "$or": [
            {"entreprise_1_id": entreprise_1["id"], "entreprise_2_id": entreprise_2["id"]},
            {"entreprise_1_id": entreprise_2["id"], "entreprise_2_id": entreprise_1["id"]}
        ],
        "status": "pending"
    })
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une demande de regroupement est déjà en cours entre ces deux entreprises"
        )
    
    # Créer la demande
    grouping_request_id = str(uuid4())
    grouping_request = {
        "id": grouping_request_id,
        "entreprise_1_id": entreprise_1["id"],
        "entreprise_1_nom": entreprise_1["nom"],
        "entreprise_2_id": entreprise_2["id"],
        "entreprise_2_nom": entreprise_2["nom"],
        "requested_by": current_user.id,
        "requested_by_name": current_user.full_name,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "reason": request_data.reason,
        "approvals": {
            "entreprise_1": {
                "approved": False,
                "approved_by": None,
                "approved_by_name": None,
                "approved_at": None
            },
            "entreprise_2": {
                "approved": False,
                "approved_by": None,
                "approved_by_name": None,
                "approved_at": None
            }
        },
        "rejection_reason": None,
        "rejected_by": None,
        "rejected_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.entreprise_grouping_requests.insert_one(grouping_request)
    
    return {
        "success": True,
        "message": "Demande de regroupement créée avec succès",
        "request_id": grouping_request_id,
        "status": "pending"
    }


@grouping_router.get("/my-requests")
async def get_my_grouping_requests(
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_permission("entreprises.group_request")),
    iam_service: IAMService = Depends(get_iam_service),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les demandes de regroupement concernant les entreprises de l'utilisateur
    """
    
    user_company_ids = await get_user_company_ids(current_user, db)
    if not user_company_ids:
        return {
            "requests": [],
            "total": 0
        }
    # IAM scope : on filtre si .own
    iam_filter = await get_resource_filter(
        iam_service,
        current_user.id,
        user_company_ids[0],
        "entreprises",
        "group"
    )
    if iam_filter is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )
    entreprise_ids = [iam_filter.get("entreprise_id")] if iam_filter and iam_filter.get("entreprise_id") else user_company_ids
    
    # Construire la requête
    query = {
        "$or": [
            {"entreprise_1_id": {"$in": entreprise_ids}},
            {"entreprise_2_id": {"$in": entreprise_ids}}
        ]
    }
    
    if status_filter:
        query["status"] = status_filter
    
    # Récupérer les demandes
    requests = await db.entreprise_grouping_requests.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(None)
    
    return {
        "requests": requests,
        "total": len(requests)
    }


@grouping_router.get("/{request_id}")
async def get_grouping_request(
    request_id: str,
    current_user: User = Depends(require_permission("entreprises.group_request")),
    iam_service: IAMService = Depends(get_iam_service),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les détails d'une demande de regroupement
    """
    
    grouping_request = await db.entreprise_grouping_requests.find_one(
        {"id": request_id},
        {"_id": 0}
    )
    
    if not grouping_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de regroupement non trouvée"
        )
    
    user_company_ids = await get_user_company_ids(current_user, db)
    iam_filter = await get_resource_filter(
        iam_service,
        current_user.id,
        user_company_ids[0] if user_company_ids else None,
        "entreprises",
        "group"
    )
    if iam_filter is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )
    allowed_ids = set(user_company_ids)
    if iam_filter and iam_filter.get("entreprise_id"):
        allowed_ids = {iam_filter.get("entreprise_id")}

    if (grouping_request["entreprise_1_id"] not in allowed_ids and
        grouping_request["entreprise_2_id"] not in allowed_ids):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à cette demande"
        )
    
    return grouping_request


@grouping_router.post("/{request_id}/approve")
async def approve_grouping_request(
    request_id: str,
    approval: GroupingApproval,
    current_user: User = Depends(require_permission("entreprises.group_approve")),
    iam_service: IAMService = Depends(get_iam_service),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Approuver une demande de regroupement
    
    Règles:
    - Au moins 1 admin de chaque entreprise doit approuver
    - Si les deux côtés approuvent → regroupement effectif
    """
    
    # Récupérer la demande
    grouping_request = await db.entreprise_grouping_requests.find_one({"id": request_id})
    
    if not grouping_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de regroupement non trouvée"
        )
    
    if grouping_request["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette demande a déjà été traitée"
        )
    
    # Déterminer quelle entreprise approuve
    user_company_ids = await get_user_company_ids(current_user, db)
    iam_filter = await get_resource_filter(
        iam_service,
        current_user.id,
        user_company_ids[0] if user_company_ids else None,
        "entreprises",
        "group"
    )
    if iam_filter is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )
    allowed_ids = set(user_company_ids)
    if iam_filter and iam_filter.get("entreprise_id"):
        allowed_ids = {iam_filter.get("entreprise_id")}
    
    approval_key = None
    if grouping_request["entreprise_1_id"] in allowed_ids:
        approval_key = "entreprise_1"
    elif grouping_request["entreprise_2_id"] in allowed_ids:
        approval_key = "entreprise_2"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à approuver cette demande"
        )
    
    # Marquer l'approbation
    now = datetime.now(timezone.utc).isoformat()
    
    update_data = {
        f"approvals.{approval_key}.approved": True,
        f"approvals.{approval_key}.approved_by": current_user.id,
        f"approvals.{approval_key}.approved_by_name": current_user.full_name,
        f"approvals.{approval_key}.approved_at": now,
        "updated_at": now
    }
    
    await db.entreprise_grouping_requests.update_one(
        {"id": request_id},
        {"$set": update_data}
    )
    
    # Récupérer la demande mise à jour
    updated_request = await db.entreprise_grouping_requests.find_one({"id": request_id})
    
    # Vérifier si les deux côtés ont approuvé
    if (updated_request["approvals"]["entreprise_1"]["approved"] and
        updated_request["approvals"]["entreprise_2"]["approved"]):
        
        # REGROUPEMENT EFFECTIF
        await execute_grouping(
            updated_request["entreprise_1_id"],
            updated_request["entreprise_2_id"],
            db
        )
        
        # Marquer la demande comme approved
        await db.entreprise_grouping_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": "approved",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Regroupement approuvé et effectué avec succès",
            "status": "approved",
            "grouped": True
        }
    else:
        return {
            "success": True,
            "message": "Votre approbation a été enregistrée. En attente de l'autre partie.",
            "status": "pending",
            "grouped": False
        }


@grouping_router.post("/{request_id}/reject")
async def reject_grouping_request(
    request_id: str,
    rejection: GroupingRejection,
    current_user: User = Depends(require_permission("entreprises.group_approve")),
    iam_service: IAMService = Depends(get_iam_service),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Rejeter une demande de regroupement
    
    Règles:
    - Un seul rejet suffit pour annuler la demande
    """
    
    grouping_request = await db.entreprise_grouping_requests.find_one({"id": request_id})
    
    if not grouping_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande de regroupement non trouvée"
        )
    
    if grouping_request["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette demande a déjà été traitée"
        )
    
    user_company_ids = await get_user_company_ids(current_user, db)
    iam_filter = await get_resource_filter(
        iam_service,
        current_user.id,
        user_company_ids[0] if user_company_ids else None,
        "entreprises",
        "group"
    )
    if iam_filter is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )
    allowed_ids = set(user_company_ids)
    if iam_filter and iam_filter.get("entreprise_id"):
        allowed_ids = {iam_filter.get("entreprise_id")}
    
    if (grouping_request["entreprise_1_id"] not in allowed_ids and
        grouping_request["entreprise_2_id"] not in allowed_ids):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à rejeter cette demande"
        )
    
    # Rejeter la demande
    await db.entreprise_grouping_requests.update_one(
        {"id": request_id},
        {
            "$set": {
                "status": "rejected",
                "rejection_reason": rejection.rejection_reason,
                "rejected_by": current_user.id,
                "rejected_by_name": current_user.full_name,
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "success": True,
        "message": "Demande de regroupement rejetée",
        "status": "rejected"
    }


async def execute_grouping(entreprise_1_id: str, entreprise_2_id: str, db: AsyncIOMotorDatabase):
    """
    Exécuter le regroupement effectif de deux entreprises
    
    Actions:
    - Mise à jour grouping_status = "grouped"
    - Définir entreprise_1 comme parent (grouping_parent_id)
    - Les deux entreprises restent dans la base mais sont regroupées
    """
    
    # Mettre à jour entreprise 1 (devient le parent)
    await db.entreprises.update_one(
        {"id": entreprise_1_id},
        {
            "$set": {
                "grouping_status": "grouped",
                "grouping_parent_id": None,  # C'est le parent
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Mettre à jour entreprise 2 (enfant)
    await db.entreprises.update_one(
        {"id": entreprise_2_id},
        {
            "$set": {
                "grouping_status": "grouped",
                "grouping_parent_id": entreprise_1_id,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
