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
from awana_auth.core.dependencies import require_admin, get_database, get_current_user
from pydantic import BaseModel

validation_router = APIRouter(prefix="/validations", tags=["Validations"])


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


@validation_router.get("", response_model=List[Validation])
async def get_validations(
    validation_type: Optional[str] = Query(None, description="Filter by type: interim or company"),
    status: Optional[ValidationStatus] = Query(None, description="Filter by status"),
    has_location_warning: Optional[bool] = Query(None, description="Filter by location warning"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned validator"),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    current_user: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get validation statistics"""
    total_pending = await db.validations.count_documents({"status": "pending"})
    pending_interim = await db.validations.count_documents({"status": "pending", "validation_type": "interim"})
    pending_company = await db.validations.count_documents({"status": "pending", "validation_type": "company"})
    
    with_warnings = await db.validations.count_documents({
        "status": "pending",
        "has_location_warning": True
    })
    
    total_approved = await db.validations.count_documents({"status": "approved"})
    total_rejected = await db.validations.count_documents({"status": "rejected"})
    
    return {
        "total_pending": total_pending,
        "pending_interim": pending_interim,
        "pending_company": pending_company,
        "with_location_warnings": with_warnings,
        "total_approved": total_approved,
        "total_rejected": total_rejected,
    }


@validation_router.get("/{validation_id}", response_model=Validation)
async def get_validation(
    validation_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific validation"""
    validation = await db.validations.find_one({"id": validation_id}, {"_id": 0})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    return Validation(**validation)


@validation_router.post("/{validation_id}/approve")
async def approve_validation(
    validation_id: str,
    approval: ValidationApproval,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Approve a validation request"""
    validation = await db.validations.find_one({"id": validation_id})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    if validation["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation already processed"
        )
    
    # Update user status to active
    await db.users.update_one(
        {"id": validation["user_id"]},
        {
            "$set": {
                "status": UserStatus.ACTIVE.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Update validation
    await db.validations.update_one(
        {"id": validation_id},
        {
            "$set": {
                "status": "approved",
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
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reject a validation request"""
    validation = await db.validations.find_one({"id": validation_id})
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )
    
    if validation["status"] != "pending":
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
                "status": "rejected",
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


@validation_router.post("/{validation_id}/assign")
async def assign_validation(
    validation_id: str,
    assignment: ValidationAssignment,
    current_user: User = Depends(require_admin),
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
    
    # Check if validator has admin or commercial role
    validator_roles = validator.get("roles", [])
    if not any(role in validator_roles for role in ["admin", "super_admin", "commercial"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have validator role (admin, super_admin, or commercial)"
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
    current_user: User = Depends(require_admin),
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
