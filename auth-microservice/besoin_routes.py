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
from awana_auth.services.notification_service import NotificationService

router = APIRouter()


async def get_current_user_info(current_user: dict) -> tuple:
    """Extract user info from current_user dict"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    user_name = current_user.get("full_name") or current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "full_name", current_user.username)
    if isinstance(current_user, dict):
        user_role = current_user.get("roles", [])[0] if current_user.get("roles") else "user"
    else:
        # For User objects, get roles from the roles attribute
        user_role = current_user.roles[0] if current_user.roles else "user"
    return user_id, user_name, user_role


async def get_user_entreprise_id(current_user, db: AsyncIOMotorDatabase, user_id: str, user_role: str) -> str:
    """Get entreprise_id for current user, creating test entreprise for admin if needed"""
    if isinstance(current_user, dict):
        entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
    else:
        # For User objects, check if it has entreprise_id attribute
        entreprise_id = getattr(current_user, "entreprise_id", None)
    
    # For admin users, create a default test entreprise if none exists
    if not entreprise_id and "admin" in user_role.lower():
        # Create or get default test entreprise for admin testing
        test_entreprise = await db.entreprises.find_one({"nom": "Test Entreprise Admin"})
        if not test_entreprise:
            test_entreprise_id = str(uuid.uuid4())
            test_entreprise_doc = {
                "id": test_entreprise_id,
                "nom": "Test Entreprise Admin",
                "description": "Entreprise de test pour les administrateurs",
                "created_at": datetime.now(timezone.utc),
                "created_by": user_id
            }
            await db.entreprises.insert_one(test_entreprise_doc)
            entreprise_id = test_entreprise_id
        else:
            entreprise_id = test_entreprise["id"]
    
    return entreprise_id


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
    entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
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
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
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
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
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
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
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


# ==================== SUBMIT BESOIN ====================

@router.post("/{besoin_id}/submit", response_model=BesoinResponse)
async def submit_besoin(
    besoin_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_SUBMIT))
):
    """
    Submit besoin to JLC for validation
    Locks the besoin from further edits by company
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
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
        if besoin["entreprise_id"] != user_entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce besoin"
            )
    
    # Check current status
    if besoin["status"] != BesoinStatus.BROUILLON.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les besoins en brouillon peuvent être soumis"
        )
    
    # Update status
    now = datetime.now(timezone.utc)
    new_status = BesoinStatus.SOUMIS
    
    # Add to status history
    status_history = besoin.get("status_history", [])
    status_history.append({
        "from_status": besoin["status"],
        "to_status": new_status.value,
        "changed_by": user_id,
        "changed_by_name": user_name,
        "changed_at": now,
        "comment": "Soumis à JLC pour validation"
    })
    
    await db.besoins.update_one(
        {"id": besoin_id},
        {
            "$set": {
                "status": new_status.value,
                "status_history": status_history,
                "submitted_at": now,
                "updated_at": now,
            }
        }
    )
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.BESOIN_SUBMITTED,
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin["titre"],
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Besoin soumis à JLC: {besoin['titre']}",
        severity=AuditSeverity.INFO,
    )
    
    # Send notification to JLC team
    notification_service = NotificationService(db)
    await notification_service.send_besoin_notification(
        event_type="submitted",
        besoin_id=besoin_id,
        besoin_titre=besoin["titre"],
        entreprise_name=besoin["entreprise_name"],
        recipients=["jlc_team"],
        actor_name=user_name
    )
    
    # Fetch updated besoin
    updated_besoin = await db.besoins.find_one({"id": besoin_id})
    updated_besoin.pop("_id", None)
    
    # Get responsable name
    if updated_besoin.get("responsable_besoin_id"):
        responsable = await db.users.find_one({"id": updated_besoin["responsable_besoin_id"]})
        updated_besoin["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    
    return BesoinResponse(**updated_besoin)


# ==================== UPDATE STATUS (WORKFLOW) ====================

@router.post("/{besoin_id}/status", response_model=BesoinResponse)
async def update_besoin_status(
    besoin_id: str,
    status_update: BesoinStatusUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_VALIDATE))
):
    """
    Update besoin status (JLC only)
    Manages workflow transitions
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    current_status = besoin["status"]
    new_status = status_update.new_status
    
    # Validate status transition
    valid_transitions = {
        BesoinStatus.BROUILLON.value: [BesoinStatus.SOUMIS.value],
        BesoinStatus.SOUMIS.value: [BesoinStatus.ANALYSE.value, BesoinStatus.BROUILLON.value],
        BesoinStatus.ANALYSE.value: [BesoinStatus.MISSION_CREEE.value, BesoinStatus.SOUMIS.value],
        BesoinStatus.MISSION_CREEE.value: [BesoinStatus.PUBLICATION.value],
        BesoinStatus.PUBLICATION.value: [BesoinStatus.POURVU.value],
        BesoinStatus.POURVU.value: [],  # Terminal state
    }
    
    if new_status.value not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transition de statut invalide: {current_status} → {new_status.value}"
        )
    
    # Update status
    now = datetime.now(timezone.utc)
    
    # Add to status history
    status_history = besoin.get("status_history", [])
    status_history.append({
        "from_status": current_status,
        "to_status": new_status.value,
        "changed_by": user_id,
        "changed_by_name": user_name,
        "changed_at": now,
        "comment": status_update.comment
    })
    
    update_data = {
        "status": new_status.value,
        "status_history": status_history,
        "updated_at": now,
    }
    
    # Set closed_at if moving to POURVU
    if new_status == BesoinStatus.POURVU:
        update_data["closed_at"] = now
    
    await db.besoins.update_one(
        {"id": besoin_id},
        {"$set": update_data}
    )
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_status_change(
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin["titre"],
        from_status=current_status,
        to_status=new_status.value,
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        comment=status_update.comment,
    )
    
    # TODO: Send notification based on status change
    
    # Fetch updated besoin
    updated_besoin = await db.besoins.find_one({"id": besoin_id})
    updated_besoin.pop("_id", None)
    
    # Get responsable name
    if updated_besoin.get("responsable_besoin_id"):
        responsable = await db.users.find_one({"id": updated_besoin["responsable_besoin_id"]})
        updated_besoin["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    
    return BesoinResponse(**updated_besoin)


# ==================== ADD COMMENT ====================

@router.post("/{besoin_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    besoin_id: str,
    comment: CommentCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_COMMENT))
):
    """
    Add a comment to a besoin
    Both company and JLC users can comment
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Check access
    is_jlc_user = "admin" in user_role.lower() or "jlc" in user_role.lower()
    if not is_jlc_user:
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
        if besoin["entreprise_id"] != user_entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce besoin"
            )
    
    # Determine author type
    author_type = "jlc" if is_jlc_user else "entreprise"
    
    # Create comment
    comment_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    comment_doc = {
        "id": comment_id,
        "besoin_id": besoin_id,
        "author_type": author_type,
        "author_id": user_id,
        "author_name": user_name,
        "content": comment.content,
        "created_at": now,
        "updated_at": None,
    }
    
    await db.besoin_comments.insert_one(comment_doc)
    
    # Increment comment count on besoin
    await db.besoins.update_one(
        {"id": besoin_id},
        {"$inc": {"comments_count": 1}}
    )
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.BESOIN_COMMENT_ADDED,
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin["titre"],
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Commentaire ajouté par {author_type}",
        metadata={"author_type": author_type}
    )
    
    # TODO: Send notification to other party
    
    comment_doc.pop("_id", None)
    return CommentResponse(**comment_doc)


# ==================== GET COMMENTS ====================

@router.get("/{besoin_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    besoin_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_READ))
):
    """
    Get all comments for a besoin
    Ordered by creation date
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Check access
    is_jlc_user = "admin" in user_role.lower() or "jlc" in user_role.lower()
    if not is_jlc_user:
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
        if besoin["entreprise_id"] != user_entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce besoin"
            )
    
    # Fetch comments
    cursor = db.besoin_comments.find({"besoin_id": besoin_id}).sort("created_at", 1)
    comments = await cursor.to_list(length=None)
    
    # Remove MongoDB _id
    for comment in comments:
        comment.pop("_id", None)
    
    return [CommentResponse(**c) for c in comments]


# ==================== UPDATE JLC ANALYSIS ====================

@router.patch("/{besoin_id}/jlc-analysis", response_model=BesoinResponse)
async def update_jlc_analysis(
    besoin_id: str,
    analysis: BesoinJLCAnalysis,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_VALIDATE))
):
    """
    Update JLC internal analysis (JLC only)
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Prepare analysis data
    analysis_data = analysis.dict(exclude_unset=True)
    
    await db.besoins.update_one(
        {"id": besoin_id},
        {
            "$set": {
                "jlc_analysis": analysis_data,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.BESOIN_ANALYSED,
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin["titre"],
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Analyse JLC mise à jour pour: {besoin['titre']}",
        metadata={"fields_updated": list(analysis_data.keys())}
    )
    
    # Fetch updated besoin
    updated_besoin = await db.besoins.find_one({"id": besoin_id})
    updated_besoin.pop("_id", None)
    
    # Get responsable name
    if updated_besoin.get("responsable_besoin_id"):
        responsable = await db.users.find_one({"id": updated_besoin["responsable_besoin_id"]})
        updated_besoin["responsable_besoin_name"] = responsable.get("full_name") or responsable.get("username") if responsable else None
    
    return BesoinResponse(**updated_besoin)


# ==================== CONVERT TO MISSION ====================

@router.post("/{besoin_id}/convert-to-mission", status_code=status.HTTP_201_CREATED)
async def convert_to_mission(
    besoin_id: str,
    conversion_request: ConvertToMissionRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_CONVERT_TO_MISSION))
):
    """
    Convert besoin to mission (JLC only)
    Creates a new mission linked to this besoin
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Check status - should be in ANALYSE or later
    if besoin["status"] not in [
        BesoinStatus.ANALYSE.value,
        BesoinStatus.MISSION_CREEE.value,
        BesoinStatus.PUBLICATION.value
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le besoin doit être en cours d'analyse pour créer une mission"
        )
    
    # Create mission
    mission_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # Prepare mission data from besoin
    mission_doc = {
        "id": mission_id,
        "besoin_id": besoin_id,  # Link to besoin
        "entreprise_id": besoin["entreprise_id"],
        "titre": conversion_request.mission_titre or besoin["titre"],
        "description": conversion_request.mission_description or besoin["description"],
        "type_poste": besoin["type_poste"],
        "competences_requises": besoin["competences_attendues"],
        "date_debut": besoin.get("date_debut_souhaitee"),
        "date_fin": besoin.get("date_fin_souhaitee"),
        "duree": besoin["duree"],
        "statut": "brouillon",  # Mission starts as draft
        "created_by": user_id,
        "created_by_name": user_name,
        "created_at": now,
        "updated_at": now,
        "internal_notes": conversion_request.internal_notes,
    }
    
    # Copy custom fields if requested
    if conversion_request.copy_all_fields:
        mission_doc["custom_fields"] = besoin.get("custom_fields", {})
    
    # Insert mission
    await db.missions.insert_one(mission_doc)
    
    # Update besoin with mission_id
    await db.besoins.update_one(
        {"id": besoin_id},
        {
            "$push": {"mission_ids": mission_id},
            "$set": {
                "status": BesoinStatus.MISSION_CREEE.value,
                "updated_at": now
            }
        }
    )
    
    # Add to besoin status history
    status_history = besoin.get("status_history", [])
    status_history.append({
        "from_status": besoin["status"],
        "to_status": BesoinStatus.MISSION_CREEE.value,
        "changed_by": user_id,
        "changed_by_name": user_name,
        "changed_at": now,
        "comment": f"Mission créée: {mission_id}"
    })
    
    await db.besoins.update_one(
        {"id": besoin_id},
        {"$set": {"status_history": status_history}}
    )
    
    # Log audit for besoin
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.BESOIN_CONVERTED,
        entity_type="besoin",
        entity_id=besoin_id,
        entity_label=besoin["titre"],
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Besoin converti en mission: {besoin['titre']}",
        metadata={
            "mission_id": mission_id,
            "mission_titre": mission_doc["titre"]
        }
    )
    
    # Log audit for mission creation
    await audit_service.log_event(
        action=AuditAction.MISSION_CREATED,
        entity_type="mission",
        entity_id=mission_id,
        entity_label=mission_doc["titre"],
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Mission créée depuis besoin: {mission_doc['titre']}",
        metadata={
            "besoin_id": besoin_id,
            "source": "besoin_conversion"
        }
    )
    
    # TODO: Send notification to company
    
    mission_doc.pop("_id", None)
    return {
        "message": "Mission créée avec succès",
        "mission_id": mission_id,
        "besoin_id": besoin_id,
        "mission": mission_doc
    }


# ==================== GET AUDIT TRAIL ====================

@router.get("/{besoin_id}/audit", response_model=dict)
async def get_besoin_audit_trail(
    besoin_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.BESOINS_READ))
):
    """
    Get audit trail for a besoin
    Complete history of all actions
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    besoin = await db.besoins.find_one({"id": besoin_id})
    if not besoin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Besoin non trouvé"
        )
    
    # Check access
    is_jlc_user = "admin" in user_role.lower() or "jlc" in user_role.lower()
    if not is_jlc_user:
        user_entreprise_id = await get_user_entreprise_id(current_user, db, user_id, user_role)
        if besoin["entreprise_id"] != user_entreprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé à ce besoin"
            )
    
    # Get audit trail
    audit_service = AuditService(db)
    audit_trail = await audit_service.get_entity_audit_trail(
        entity_type="besoin",
        entity_id=besoin_id,
        page=page,
        page_size=page_size
    )
    
    return audit_trail
