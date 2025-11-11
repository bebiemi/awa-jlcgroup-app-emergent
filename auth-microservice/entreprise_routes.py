"""
Entreprise Management Routes
CRUD operations for company/entreprise information
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from awana_auth.core.dependencies import get_database
from awana_auth.security import get_current_user
from awana_auth.core.models import User
from awana_auth.core.iam_helpers import require_permission
from pydantic import BaseModel, Field, EmailStr


router = APIRouter()


# ==================== MODELS ====================

class EntrepriseBase(BaseModel):
    """Base model for entreprise data"""
    nom: str = Field(..., min_length=2, max_length=200)
    raison_sociale: str = Field(..., min_length=2, max_length=200)
    siret: str = Field(..., pattern=r'^\d{14}$')
    adresse: str
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    pays: str = "France"
    email: EmailStr
    telephone: str
    description: Optional[str] = None
    secteur_activite: Optional[str] = None
    effectif: Optional[str] = None  # TPE, PME, ETI, GE
    site_web: Optional[str] = None


class EntrepriseCreate(EntrepriseBase):
    """Model for creating entreprise"""
    pass


class EntrepriseUpdate(BaseModel):
    """Model for updating entreprise - all fields optional"""
    nom: Optional[str] = Field(None, min_length=2, max_length=200)
    raison_sociale: Optional[str] = Field(None, min_length=2, max_length=200)
    siret: Optional[str] = Field(None, pattern=r'^\d{14}$')
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    description: Optional[str] = None
    secteur_activite: Optional[str] = None
    effectif: Optional[str] = None
    site_web: Optional[str] = None
    status: Optional[str] = None  # active, inactive, suspended


class EntrepriseResponse(EntrepriseBase):
    """Model for entreprise response"""
    id: str
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None


# ==================== GET MY ENTREPRISE ====================

@router.get("/me", response_model=EntrepriseResponse)
async def get_my_entreprise(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current user's entreprise information
    """
    # Get company_id from user
    company_id = getattr(current_user, "company_id", None) or getattr(current_user, "entreprise_id", None)
    
    if not company_id:
        # Try from database
        user_doc = await db.users.find_one({"id": current_user.id})
        if user_doc:
            company_id = user_doc.get("company_id") or user_doc.get("entreprise_id")
    
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non associé à une entreprise"
        )
    
    entreprise = await db.entreprises.find_one({"id": company_id})
    
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    # Clean MongoDB _id
    entreprise.pop("_id", None)
    
    return entreprise


# ==================== GET ENTREPRISE BY ID ====================

@router.get("/{entreprise_id}", response_model=EntrepriseResponse)
async def get_entreprise(
    entreprise_id: str,
    current_user: User = Depends(get_current_user),
    permissions: dict = Depends(require_permission("entreprises.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get entreprise by ID
    Requires: entreprises.read permission
    """
    # Check if user can access this entreprise (own company or admin)
    user_company_id = getattr(current_user, "company_id", None) or getattr(current_user, "entreprise_id", None)
    
    # If not admin, can only access own company
    if permissions.get("scope") != "all" and user_company_id != entreprise_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à cette entreprise"
        )
    
    entreprise = await db.entreprises.find_one({"id": entreprise_id})
    
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    entreprise.pop("_id", None)
    
    return entreprise


# ==================== LIST ENTREPRISES ====================

@router.get("/", response_model=List[EntrepriseResponse])
async def list_entreprises(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    permissions: dict = Depends(require_permission("entreprises.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    List entreprises
    Requires: entreprises.read permission
    Admin sees all, others see only their own
    """
    query = {}
    
    # Filter by status if provided
    if status:
        query["status"] = status
    
    # Scope filtering
    if permissions.get("scope") == "own":
        # User can only see their own company
        user_company_id = getattr(current_user, "company_id", None) or getattr(current_user, "entreprise_id", None)
        if user_company_id:
            query["id"] = user_company_id
        else:
            return []  # No company
    
    entreprises = await db.entreprises.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Clean MongoDB _id
    for entreprise in entreprises:
        entreprise.pop("_id", None)
    
    return entreprises


# ==================== CREATE ENTREPRISE ====================

@router.post("/", response_model=EntrepriseResponse, status_code=status.HTTP_201_CREATED)
async def create_entreprise(
    entreprise_data: EntrepriseCreate,
    current_user: User = Depends(get_current_user),
    permissions: dict = Depends(require_permission("entreprises.create")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new entreprise
    Requires: entreprises.create permission
    """
    # Check if SIRET already exists
    existing = await db.entreprises.find_one({"siret": entreprise_data.siret})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une entreprise avec ce SIRET existe déjà"
        )
    
    # Create entreprise document
    entreprise_id = str(uuid.uuid4())
    entreprise_doc = {
        "id": entreprise_id,
        **entreprise_data.model_dump(),
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "created_by": current_user.id
    }
    
    await db.entreprises.insert_one(entreprise_doc)
    
    entreprise_doc.pop("_id", None)
    
    return entreprise_doc


# ==================== UPDATE ENTREPRISE ====================

@router.patch("/me", response_model=EntrepriseResponse)
async def update_my_entreprise(
    entreprise_data: EntrepriseUpdate,
    current_user: User = Depends(get_current_user),
    permissions: dict = Depends(require_permission("entreprises.edit")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update current user's entreprise
    Requires: entreprises.edit permission
    """
    # Get company_id
    company_id = getattr(current_user, "company_id", None) or getattr(current_user, "entreprise_id", None)
    
    if not company_id:
        user_doc = await db.users.find_one({"id": current_user.id})
        if user_doc:
            company_id = user_doc.get("company_id") or user_doc.get("entreprise_id")
    
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non associé à une entreprise"
        )
    
    # Get current entreprise
    entreprise = await db.entreprises.find_one({"id": company_id})
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    # Prepare update data (only non-None fields)
    update_data = {k: v for k, v in entreprise_data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    # Check SIRET uniqueness if being updated
    if "siret" in update_data and update_data["siret"] != entreprise.get("siret"):
        existing = await db.entreprises.find_one({"siret": update_data["siret"]})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Une entreprise avec ce SIRET existe déjà"
            )
    
    # Update
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.entreprises.update_one(
        {"id": company_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune modification effectuée"
        )
    
    # Get updated document
    updated_entreprise = await db.entreprises.find_one({"id": company_id})
    updated_entreprise.pop("_id", None)
    
    return updated_entreprise


# ==================== UPDATE ENTREPRISE BY ID ====================

@router.patch("/{entreprise_id}", response_model=EntrepriseResponse)
async def update_entreprise(
    entreprise_id: str,
    entreprise_data: EntrepriseUpdate,
    current_user: User = Depends(get_current_user),
    permissions: dict = Depends(require_permission("entreprises.edit")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update entreprise by ID
    Requires: entreprises.edit permission
    Admin can edit any, others can only edit their own
    """
    # Check access
    user_company_id = getattr(current_user, "company_id", None) or getattr(current_user, "entreprise_id", None)
    
    if permissions.get("scope") != "all" and user_company_id != entreprise_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à cette entreprise"
        )
    
    # Get current entreprise
    entreprise = await db.entreprises.find_one({"id": entreprise_id})
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    # Prepare update
    update_data = {k: v for k, v in entreprise_data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à mettre à jour"
        )
    
    # Check SIRET uniqueness
    if "siret" in update_data and update_data["siret"] != entreprise.get("siret"):
        existing = await db.entreprises.find_one({"siret": update_data["siret"], "id": {"$ne": entreprise_id}})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Une entreprise avec ce SIRET existe déjà"
            )
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.entreprises.update_one(
        {"id": entreprise_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune modification effectuée"
        )
    
    updated_entreprise = await db.entreprises.find_one({"id": entreprise_id})
    updated_entreprise.pop("_id", None)
    
    return updated_entreprise


# ==================== DELETE ENTREPRISE ====================

@router.delete("/{entreprise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entreprise(
    entreprise_id: str,
    current_user: User = Depends(get_current_user),
    permissions: dict = Depends(require_permission("entreprises.delete")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete entreprise (soft delete - set status to inactive)
    Requires: entreprises.delete permission
    Only admins can delete
    """
    if permissions.get("scope") != "all":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent supprimer une entreprise"
        )
    
    # Soft delete - set status to inactive
    result = await db.entreprises.update_one(
        {"id": entreprise_id},
        {"$set": {
            "status": "inactive",
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    return None
