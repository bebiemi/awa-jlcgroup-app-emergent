"""
Validation Routes
Manage user and company validation workflows
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone

from awana_auth.core.location_models import Validation, ValidationStatus
from awana_auth.core.models import User, UserStatus
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from pydantic import BaseModel
from awana_auth.utils.config_helpers import cfg
from services.representant_detection_service import (
    check_validation_representant,
    get_representant_details
)

validation_router = APIRouter(prefix="/validations", tags=["Validations"])

# Centralized validation config values
VALIDATION_STATUS_PENDING = cfg.get_validation_status("pending")
VALIDATION_STATUS_APPROVED = cfg.get_validation_status("approved")
VALIDATION_STATUS_REJECTED = cfg.get_validation_status("rejected")
VALIDATION_TYPE_INTERIM = cfg.get_validation_type("interim")
VALIDATION_TYPE_COMPANY = cfg.get_validation_type("company")
VALIDATION_TYPE_COLLABORATOR = cfg.get_validation_type("collaborator")


class ValidationApproval(BaseModel):
    """Model for approving a validation"""
    notes: Optional[str] = None


class ValidationRejection(BaseModel):
    """Model for rejecting a validation"""
    rejection_reason: str
    notes: Optional[str] = None


class ValidationAssignment(BaseModel):
    """Model for assigning validation to a validator"""
    assigned_to: str  # User ID of validator


class AttachToExistingRequest(BaseModel):
    """Model for attaching validation to existing representant"""
    contact_confirmation: bool
    target_entreprise_id: Optional[str] = None  # Si plusieurs entreprises, choisir laquelle
    notes: Optional[str] = None


class RepresentantEntreprise(BaseModel):
    """Entreprise info for representant"""
    id: str
    nom: str
    email: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None


class RepresentantDetails(BaseModel):
    """Details of existing representant"""
    found: bool
    user: Optional[dict] = None
    entreprises: List[RepresentantEntreprise] = []
    total_entreprises: int = 0


class EnrichedValidationResponse(BaseModel):
    """Validation with representant details"""
    validation: Validation
    representant_details: Optional[RepresentantDetails] = None


@validation_router.get("", response_model=List[Validation])
async def get_validations(
    validation_type: Optional[str] = Query(None, description="Filter by type: interim or company"),
    status: Optional[ValidationStatus] = Query(None, description="Filter by status"),
    has_location_warning: Optional[bool] = Query(None, description="Filter by location warning"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned validator"),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get validations with filters (admin only)"""
    query = {}
    
    if validation_type:
        query["validation_type"] = validation_type
    
    if status:
        query["status"] = status.value
    
    if has_location_warning is not None:
        query["has_location_warning"] = has_location_warning
    
    if assigned_to:
        query["assigned_to"] = assigned_to
    
    skip = (page - 1) * page_size
    
    validations = await db.validations.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(page_size).to_list(length=None)
    
    return [Validation(**v) for v in validations]


@validation_router.get("/stats")
async def get_validation_stats(
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get validation statistics"""
    total_pending = await db.validations.count_documents({"status": VALIDATION_STATUS_PENDING})
    pending_interim = await db.validations.count_documents({"status": VALIDATION_STATUS_PENDING, "validation_type": VALIDATION_TYPE_INTERIM})
    pending_company = await db.validations.count_documents({"status": VALIDATION_STATUS_PENDING, "validation_type": VALIDATION_TYPE_COMPANY})
    pending_collaborator = await db.validations.count_documents({"status": VALIDATION_STATUS_PENDING, "validation_type": VALIDATION_TYPE_COLLABORATOR})
    
    with_warnings = await db.validations.count_documents({
        "status": VALIDATION_STATUS_PENDING,
        "has_location_warning": True
    })

    total_approved = await db.validations.count_documents({"status": VALIDATION_STATUS_APPROVED})
    total_rejected = await db.validations.count_documents({"status": VALIDATION_STATUS_REJECTED})
    
    return {
        "total_pending": total_pending,
        "pending_interim": pending_interim,
        "pending_company": pending_company,
        "pending_collaborator": pending_collaborator,
        "with_location_warnings": with_warnings,
        "total_approved": total_approved,
        "total_rejected": total_rejected,
    }


@validation_router.get("/my-validation", response_model=Optional[Validation])
async def get_my_validation(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get validation for current user"""
    validation = await db.validations.find_one(
        {"user_id": current_user.id},
        {"_id": 0}
    )
    
    if not validation:
        return None
    
    return Validation(**validation)


@validation_router.get("/{validation_id}", response_model=dict)
async def get_validation(
    validation_id: str,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get specific validation with enriched data
    Phase 2: Include representant details if existing representant detected
    """
    validation = await db.validations.find_one({"id": validation_id}, {"_id": 0})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    # Enrichir avec les détails du représentant existant si applicable
    representant_details = None
    if validation.get("has_existing_representant") and validation.get("existing_representant_user_id"):
        representant_details = await get_representant_details(
            validation["existing_representant_user_id"],
            db
        )
    
    return {
        "validation": validation,
        "representant_details": representant_details
    }


@validation_router.post("/{validation_id}/approve")
async def approve_validation(
    validation_id: str,
    approval: ValidationApproval,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Approve a validation request"""
    validation = await db.validations.find_one({"id": validation_id})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    if validation["status"] != VALIDATION_STATUS_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation already processed"
        )
    
    # Get profile ID if company validation
    profile_id = None
    if validation["validation_type"] == VALIDATION_TYPE_COMPANY:
        company_profile = await db.profiles.find_one({"code": "company_admin"})
        if company_profile:
            profile_id = company_profile["id"]
    
    # Update user status to active and assign profile
    update_data = {
        "status": UserStatus.ACTIVE.value,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if profile_id:
        update_data["profile_ids"] = [profile_id]
        update_data["profile_code"] = "company_admin"  # Keep for backward compat
    
    await db.users.update_one(
        {"id": validation["user_id"]},
        {"$set": update_data}
    )
    
    # If company validation, create company profile automatically
    if validation["validation_type"] == VALIDATION_TYPE_COMPANY:
        user = await db.users.find_one({"id": validation["user_id"]}, {"_id": 0})
        
        # Check if profile already exists
        existing_profile = await db.company_profiles.find_one({"user_id": user["id"]})
        
        if not existing_profile:
            # Extract company info from validation or user
            company_name = validation.get("company_name") or user.get("full_name")
            
            company_profile = {
                "user_id": user["id"],
                "company_name": company_name,  # OBLIGATOIRE
                "dirigeant": user.get("full_name"),  # OBLIGATOIRE (nom du contact)
                "nif": validation.get("nif") or user.get("nif"),  # OBLIGATOIRE
                "siret": validation.get("siret"),  # FACULTATIF
                "phone": user.get("phone"),  # FACULTATIF
                "email": user.get("email"),  # FACULTATIF
                "address": validation.get("address"),  # FACULTATIF
                "sector": validation.get("sector"),  # FACULTATIF
                "company_size": validation.get("company_size"),  # FACULTATIF
                "description": validation.get("description"),  # FACULTATIF
                "website": validation.get("website"),  # FACULTATIF
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.company_profiles.insert_one(company_profile)
            
            logger.info(f"Company profile created for user {user['id']}: {company_name}")
    
    # Update validation
    await db.validations.update_one(
        {"id": validation_id},
        {
            "$set": {
                "status": VALIDATION_STATUS_APPROVED,
                "validated_by": current_user.id,
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "notes": approval.notes,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Validation approved for {validation['user_email']}"
    }


@validation_router.post("/{validation_id}/reject")
async def reject_validation(
    validation_id: str,
    rejection: ValidationRejection,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reject a validation request"""
    validation = await db.validations.find_one({"id": validation_id})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    if validation["status"] != VALIDATION_STATUS_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation already processed"
        )
    
    # Update user status to suspended
    await db.users.update_one(
        {"id": validation["user_id"]},
        {
            "$set": {
                "status": UserStatus.SUSPENDED.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Update validation
    await db.validations.update_one(
        {"id": validation_id},
        {
            "$set": {
                "status": VALIDATION_STATUS_REJECTED,
                "validated_by": current_user.id,
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "rejection_reason": rejection.rejection_reason,
                "notes": rejection.notes,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Validation rejected for {validation['user_email']}"
    }


@validation_router.get("/{validation_id}/check-representant")
async def check_representant_endpoint(
    validation_id: str,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Vérifier si le représentant légal d'une validation existe déjà
    Badge automatique pour les validateurs
    """
    try:
        result = await check_validation_representant(validation_id, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@validation_router.get("/representant/{user_id}/details")
async def get_representant_details_endpoint(
    user_id: str,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les détails d'un représentant légal existant
    Affiche les entreprises déjà liées à ce représentant
    """
    details = await get_representant_details(user_id, db)
    
    if not details["found"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Représentant not found"
        )
    
    return details


@validation_router.post("/{validation_id}/attach-to-existing")
async def attach_to_existing_representant(
    validation_id: str,
    attach_request: AttachToExistingRequest,
    current_user: User = Depends(require_permission("entreprises.link_existing")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Rattacher une validation à un représentant légal existant
    Phase 3: Workflow de rattachement
    
    Requires:
    - contact_confirmation: True (prise de contact obligatoire)
    - Permission: entreprises.link_existing
    """
    
    # Validation de la confirmation de contact
    if not attach_request.contact_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La prise de contact avec le client existant est obligatoire avant le rattachement"
        )
    
    # Récupérer la validation
    validation = await db.validations.find_one({"id": validation_id})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    # Vérifier que c'est une validation company
    if validation["validation_type"] != VALIDATION_TYPE_COMPANY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le rattachement ne s'applique qu'aux validations de type '{VALIDATION_TYPE_COMPANY}'"
        )
    
    # Vérifier qu'il y a bien un représentant existant détecté
    if not validation.get("has_existing_representant"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun représentant existant détecté pour cette validation"
        )
    
    existing_user_id = validation.get("existing_representant_user_id")
    if not existing_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID du représentant existant manquant"
        )
    
    # Récupérer le user de la nouvelle validation
    new_user = await db.users.find_one({"id": validation["user_id"]})
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur de la validation non trouvé"
        )
    
    # Récupérer les entreprises du représentant existant
    existing_entreprises = await db.entreprises.find(
        {"user_id": existing_user_id},
        {"_id": 0}
    ).to_list(None)
    
    if not existing_entreprises:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune entreprise trouvée pour le représentant existant"
        )
    
    # Déterminer l'entreprise cible
    target_entreprise = None
    if attach_request.target_entreprise_id:
        # Entreprise spécifique sélectionnée
        target_entreprise = await db.entreprises.find_one(
            {"id": attach_request.target_entreprise_id},
            {"_id": 0}
        )
        if not target_entreprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entreprise cible non trouvée"
            )
    else:
        # Prendre la première entreprise si une seule existe
        if len(existing_entreprises) == 1:
            target_entreprise = existing_entreprises[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plusieurs entreprises trouvées. Veuillez spécifier target_entreprise_id"
            )
    
    # Créer une nouvelle entrée entreprise pour la validation, mais liée au user existant
    # Cette entreprise sera "rattachée" mais reste indépendante
    from uuid import uuid4
    new_entreprise_id = str(uuid4())
    
    # Extraire les données de la validation ou des champs dynamiques
    company_data = new_user.get("company_data", {})
    
    new_entreprise = {
        "id": new_entreprise_id,
        "nom": company_data.get("nom_commercial") or company_data.get("raison_sociale") or validation.get("user_full_name"),
        "raison_sociale": company_data.get("raison_sociale", ""),
        "representant_legal_nom": validation.get("representant_legal_nom", ""),
        "representant_legal_email": validation.get("representant_legal_email", ""),
        "email": company_data.get("email", new_user.get("email")),
        "telephone": company_data.get("telephone", new_user.get("phone")),
        "nif": company_data.get("nif", ""),
        "siret": company_data.get("siret", ""),
        "user_id": existing_user_id,  # IMPORTANT: Lié au user existant
        "linked_entreprises": [target_entreprise["id"]],  # Lien vers l'entreprise existante
        "grouping_status": "linked",  # Statut = rattachée
        "grouping_parent_id": None,
        "created_at": datetime.now(timezone.utc),
        "created_by": current_user.id,
        "updated_at": datetime.now(timezone.utc),
        "status": "active"
    }
    
    await db.entreprises.insert_one(new_entreprise)
    
    # Mettre à jour l'entreprise cible pour ajouter le lien inverse
    await db.entreprises.update_one(
        {"id": target_entreprise["id"]},
        {
            "$addToSet": {"linked_entreprises": new_entreprise_id},
            "$set": {
                "grouping_status": "linked",
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Mettre à jour le statut de l'utilisateur de la validation à "active"
    # Car le rattachement équivaut à une validation
    await db.users.update_one(
        {"id": new_user["id"]},
        {
            "$set": {
                "status": UserStatus.ACTIVE.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Mettre à jour la validation
    await db.validations.update_one(
        {"id": validation_id},
        {
            "$set": {
                "status": VALIDATION_STATUS_APPROVED,
                "rattachement_status": VALIDATION_STATUS_APPROVED,
                "rattachement_to_entreprise_id": target_entreprise["id"],
                "contact_confirmation": True,
                "validated_by": current_user.id,
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "notes": attach_request.notes or f"Rattaché à l'entreprise {target_entreprise['nom']}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Entreprise rattachée avec succès à {target_entreprise['nom']}",
        "new_entreprise_id": new_entreprise_id,
        "linked_to_entreprise_id": target_entreprise["id"],
        "existing_user_id": existing_user_id
    }


@validation_router.post("/{validation_id}/assign")
async def assign_validation(
    validation_id: str,
    assignment: ValidationAssignment,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign validation to a validator"""
    # Check if validator exists and has appropriate role
    validator = await db.users.find_one({"id": assignment.assigned_to})
    if not validator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator not found"
        )
    
    # Check if validator has an allowed validator role from configuration
    allowed_validator_roles = [role for role in (cfg.get_validator_roles() or []) if role]
    if not allowed_validator_roles:
        allowed_validator_roles = [
            role
            for role in [cfg.get_admin_role(), cfg.get_super_admin_role(), cfg.get_commercial_role()]
            if role
        ]

    validator_roles = set(validator.get("roles", []))
    if not any(role in validator_roles for role in allowed_validator_roles):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User does not have validator role ({', '.join(allowed_validator_roles)})"
        )
    
    # Update validation
    result = await db.validations.update_one(
        {"id": validation_id},
        {
            "$set": {
                "assigned_to": assignment.assigned_to,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    return {
        "success": True,
        "message": f"Validation assigned to {validator.get('full_name', validator.get('email'))}"
    }


@validation_router.post("/{validation_id}/add-country")
async def add_country_from_validation(
    validation_id: str,
    current_user: User = Depends(require_permission("validations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a country from validation warning"""
    validation = await db.validations.find_one({"id": validation_id})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    if not validation.get("missing_country"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No missing country to add"
        )
    
    # Check if country already exists
    existing = await db.locations.find_one({
        "type": "country",
        "name": validation["missing_country"]
    })
    
    if existing:
        # Remove warning from validation
        await db.validations.update_one(
            {"id": validation_id},
            {
                "$set": {
                    "has_location_warning": False,
                    "location_warning_message": None,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        return {
            "success": True,
            "message": f"Country {validation['missing_country']} already exists",
            "country_id": existing["id"]
        }
    
    # Create new country
    import uuid
    country_id = str(uuid.uuid4())
    new_country = {
        "id": country_id,
        "type": "country",
        "name": validation["missing_country"],
        "parent_id": None,
        "is_visible": True,
        "is_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user.id
    }
    
    await db.locations.insert_one(new_country)
    
    # Remove warning from validation
    await db.validations.update_one(
        {"id": validation_id},
        {
            "$set": {
                "has_location_warning": False,
                "location_warning_message": None,
                "country_name": validation["missing_country"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "success": True,
        "message": f"Country {validation['missing_country']} created successfully",
        "country_id": country_id
    }
