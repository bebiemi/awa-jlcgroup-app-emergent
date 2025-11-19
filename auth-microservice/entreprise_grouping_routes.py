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
from awana_auth.core.dependencies import get_database, get_current_user
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


@grouping_router.post("/request")
async def create_grouping_request(
    request_data: GroupingRequest,
    current_user: User = Depends(require_permission("entreprises.group_request")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer une demande de regroupement entre deux entreprises
    
    Règles:
    - Les deux entreprises doivent être "linked" (rattachées)
    - L'utilisateur doit avoir accès aux deux entreprises
    - Génère automatiquement une demande envoyée aux admins des deux entreprises
    """
    
    # Récupérer l'entreprise de l'utilisateur courant
    entreprise_1 = await db.entreprises.find_one(
        {"user_id": current_user.id},
        {"_id": 0}
    )
    
    if not entreprise_1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise de l'utilisateur non trouvée"
        )
    
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
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les demandes de regroupement concernant les entreprises de l'utilisateur
    """
    
    # Récupérer toutes les entreprises de l'utilisateur
    entreprises = await db.entreprises.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1}
    ).to_list(None)
    
    if not entreprises:
        return {
            "requests": [],
            "total": 0
        }
    
    entreprise_ids = [e["id"] for e in entreprises]
    
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
    current_user: User = Depends(get_current_user),
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
    
    # Vérifier que l'utilisateur a accès à cette demande
    user_entreprises = await db.entreprises.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1}
    ).to_list(None)
    
    user_entreprise_ids = [e["id"] for e in user_entreprises]
    
    if (grouping_request["entreprise_1_id"] not in user_entreprise_ids and
        grouping_request["entreprise_2_id"] not in user_entreprise_ids):
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
    user_entreprises = await db.entreprises.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1}
    ).to_list(None)
    
    user_entreprise_ids = [e["id"] for e in user_entreprises]
    
    approval_key = None
    if grouping_request["entreprise_1_id"] in user_entreprise_ids:
        approval_key = "entreprise_1"
    elif grouping_request["entreprise_2_id"] in user_entreprise_ids:
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
    
    # Vérifier que l'utilisateur a accès
    user_entreprises = await db.entreprises.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1}
    ).to_list(None)
    
    user_entreprise_ids = [e["id"] for e in user_entreprises]
    
    if (grouping_request["entreprise_1_id"] not in user_entreprise_ids and
        grouping_request["entreprise_2_id"] not in user_entreprise_ids):
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
