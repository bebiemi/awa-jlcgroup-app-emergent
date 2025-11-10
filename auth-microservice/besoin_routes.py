"""
Besoin Routes
CRUD and workflow management for company hiring needs
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional, List

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.core.besoin_models import (
    BesoinCreate,
    BesoinUpdate,
    BesoinResponse,
    BesoinListResponse,
    BesoinStatus,
    BesoinStatusUpdate,
    BesoinJLCAnalysis,
    CommentCreate,
    CommentResponse,
    StatusHistoryEntry,
    ConvertToMissionRequest,
)
from awana_auth.core.audit_models import AuditAction, AuditSeverity
from awana_auth.services.audit_service import AuditService

router = APIRouter()


async def get_current_user_info(current_user: dict) -> tuple:
    """Extract user info from current_user dict"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    user_name = current_user.get("full_name") or current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "full_name", current_user.username)
    user_role = current_user.get("roles", [])[0] if isinstance(current_user, dict) and current_user.get("roles") else "user"
    return user_id, user_name, user_role


# ==================== CREATE BESOIN ====================

@router.post("/", response_model=BesoinResponse, status_code=status.HTTP_201_CREATED)
async def create_besoin(
    besoin: BesoinCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_CREATE))
):
    """
    Create a new besoin (hiring need)
    Company users can create besoins
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    # Get entreprise_id from user profile or user data
    entreprise_id = current_user.get("entreprise_id")
    if not entreprise_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur non associé à une entreprise"
        )
    
    # Get entreprise name
    entreprise = await db.entreprises.find_one({"id": entreprise_id})
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    entreprise_name = entreprise.get("nom", "")
    
    # Generate besoin ID
    besoin_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # Set responsable to creator if not specified
    responsable_id = besoin.responsable_besoin_id or user_id
    
    # Initial status
    initial_status = BesoinStatus.BROUILLON
    
    # Create status history
    status_history = [
        {
            "from_status": None,
            "to_status": initial_status.value,
            "changed_by": user_id,
            "changed_by_name": user_name,
            "changed_at": now,
            "comment": "Création du besoin"
        }
    ]
    
    # Prepare document
    besoin_doc = {
        "id": besoin_id,
        "entreprise_id": entreprise_id,
        "entreprise_name": entreprise_name,
        "titre": besoin.titre,
        "description": besoin.description,
        "duree": besoin.duree.value,
        "date_debut_souhaitee": besoin.date_debut_souhaitee.isoformat() if besoin.date_debut_souhaitee else None,
        "date_fin_souhaitee": besoin.date_fin_souhaitee.isoformat() if besoin.date_fin_souhaitee else None,
        "type_poste": besoin.type_poste,
        "competences_attendues": besoin.competences_attendues,
        "responsable_besoin_id": responsable_id,
        "pieces_jointes": besoin.pieces_jointes,
        "custom_fields": besoin.custom_fields,
        "status": initial_status.value,
        "status_history": status_history,
        "jlc_analysis": None,
        "mission_ids": [],
        "created_by": user_id,
        "created_by_name": user_name,
        "created_at": now,
        "updated_at": now,
        "submitted_at": None,
        "closed_at": None,
        "comments_count": 0,
    }
    
    # Insert into database
    await db.besoins.insert_one(besoin_doc)
    
    # Log audit event
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.BESOIN_CREATED,
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin.titre,
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Besoin créé: {besoin.titre}",
        metadata={
            "entreprise_id": entreprise_id,
            "entreprise_name": entreprise_name,
            "type_poste": besoin.type_poste,
        }
    )
    
    # Remove MongoDB _id
    besoin_doc.pop("_id", None)
    
    # Get responsable name
    if responsable_id != user_id:
        responsable = await db.users.find_one({"id": responsable_id})
        besoin_doc["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    else:
        besoin_doc["responsable_besoin_name"] = user_name
    
    return BesoinResponse(**besoin_doc)


# ==================== GET BESOINS LIST ====================

@router.get("/", response_model=BesoinListResponse)
async def list_besoins(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    entreprise_id: Optional[str] = Query(None, description="Filter by entreprise (JLC only)"),
    search: Optional[str] = Query(None, description="Search in titre or description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_READ))
):
    """
    List besoins with filters
    - Company users see only their besoins
    - JLC users see all besoins
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    # Build query
    query = {}
    
    # Check if user is JLC (admin/super_admin) or company user
    is_jlc_user = "admin" in user_role.lower() or "jlc" in user_role.lower()
    
    if not is_jlc_user:
        # Company users can only see their own besoins
        user_entreprise_id = current_user.get("entreprise_id")
        if not user_entreprise_id:
            return BesoinListResponse(items=[], total=0, page=page, page_size=page_size, total_pages=0)
        query["entreprise_id"] = user_entreprise_id
    elif entreprise_id:
        # JLC users can filter by entreprise
        query["entreprise_id"] = entreprise_id
    
    if status_filter:
        query["status"] = status_filter
    
    if search:
        query["$or"] = [
            {"titre": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Count total
    total = await db.besoins.count_documents(query)
    
    # Pagination
    skip = (page - 1) * page_size
    cursor = db.besoins.find(query).sort("created_at", -1).skip(skip).limit(page_size)
    besoins = await cursor.to_list(length=page_size)
    
    # Remove MongoDB _id and enrich
    for besoin in besoins:
        besoin.pop("_id", None)
        # Get responsable name if needed
        if besoin.get("responsable_besoin_id"):
            responsable = await db.users.find_one({"id": besoin["responsable_besoin_id"]})
            besoin["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    
    return BesoinListResponse(
        items=[BesoinResponse(**b) for b in besoins],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ==================== GET SINGLE BESOIN ====================

@router.get("/{besoin_id}", response_model=BesoinResponse)
async def get_besoin(
    besoin_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_READ))
):
    """Get a single besoin by ID"""
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Check permissions: company users can only see their own besoins
    is_jlc_user = "admin" in user_role.lower() or "jlc" in user_role.lower()
    if not is_jlc_user:
        user_entreprise_id = current_user.get("entreprise_id")
        if besoin["entreprise_id"] != user_entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce besoin"
            )
    
    besoin.pop("_id", None)
    
    # Get responsable name
    if besoin.get("responsable_besoin_id"):
        responsable = await db.users.find_one({"id": besoin["responsable_besoin_id"]})
        besoin["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    
    return BesoinResponse(**besoin)


# ==================== UPDATE BESOIN ====================

@router.patch("/{besoin_id}", response_model=BesoinResponse)
async def update_besoin(
    besoin_id: str,
    updates: BesoinUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_EDIT))
):
    """
    Update a besoin (only in BROUILLON status)
    Company users can only update their own besoins
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Check ownership
    is_jlc_user = "admin" in user_role.lower() or "jlc" in user_role.lower()
    if not is_jlc_user:
        user_entreprise_id = current_user.get("entreprise_id")
        if besoin["entreprise_id"] != user_entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce besoin"
            )
    
    # Check status: can only update if BROUILLON
    if besoin["status"] != BesoinStatus.BROUILLON.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de modifier un besoin qui n'est pas en brouillon"
        )
    
    # Prepare updates
    update_data = updates.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    # Convert dates to ISO format
    if "date_debut_souhaitee" in update_data and update_data["date_debut_souhaitee"]:
        update_data["date_debut_souhaitee"] = update_data["date_debut_souhaitee"].isoformat()
    if "date_fin_souhaitee" in update_data and update_data["date_fin_souhaitee"]:
        update_data["date_fin_souhaitee"] = update_data["date_fin_souhaitee"].isoformat()
    
    if "duree" in update_data:
        update_data["duree"] = update_data["duree"].value
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Update in database
    await db.besoins.update_one(
        {"id": besoin_id},
        {"$set": update_data}
    )
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.BESOIN_UPDATED,
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin["titre"],
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Besoin modifié: {besoin['titre']}",
        changes={"fields_updated": list(update_data.keys())}
    )
    
    # Fetch updated besoin
    updated_besoin = await db.besoins.find_one({"id": besoin_id})
    updated_besoin.pop("_id", None)
    
    # Get responsable name
    if updated_besoin.get("responsable_besoin_id"):
        responsable = await db.users.find_one({"id": updated_besoin["responsable_besoin_id"]})
        updated_besoin["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    
    return BesoinResponse(**updated_besoin)


# ==================== TO BE CONTINUED ====================
# Will add:
# - UPDATE STATUS (workflow)
# - SUBMIT BESOIN
# - ADD COMMENT
# - GET COMMENTS
# - CONVERT TO MISSION (JLC only)
# - JLC ANALYSIS UPDATE
