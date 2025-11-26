"""
Profile Management Routes
Handles user profiles with role-specific fields
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.core.models import User
from awana_auth.core.profile_models import (
    DocumentUploadResponse
)
from awana_auth.services.permission_checker import PermissionChecker
import uuid
import os
from datetime import datetime, timezone
import mimetypes
from awana_auth.utils.config_helpers import cfg

profile_router = APIRouter(prefix="/profiles", tags=["Profiles"])

INTERIM_ROLE = cfg.get_interim_role()
COMPANY_ROLE = cfg.get_company_role()
CANDIDATE_ROLE = cfg.get_candidate_role()
POSTULANT_ROLE = cfg.get_postulant_role()
COLLABORATOR_ROLE = cfg.get_collaborator_role()
AGENCY_ROLE = cfg.get_agency_role()

PROFILE_TYPE_INTERIM = cfg.get_profile_type("interim")
PROFILE_TYPE_COMPANY = cfg.get_profile_type("company")
PROFILE_TYPE_AGENCY_COUNTRY = cfg.get_profile_type("agency_country")
PROFILE_TYPE_CANDIDATE = cfg.get_profile_type("candidat")
PROFILE_TYPE_POSTULANT = cfg.get_profile_type("postulant")
PROFILE_TYPE_COLLABORATOR = cfg.get_profile_type("collaborator")

DOCUMENT_TYPE_CV = cfg.get_document_type("cv")

# Upload configuration
UPLOAD_DIR = "/app/uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_profile_context(current_user: User, db: AsyncIOMotorDatabase):
    """Return the profile collection and configured profile type for the current user."""
    if CANDIDATE_ROLE in current_user.roles:
        return db.candidat_profiles, PROFILE_TYPE_CANDIDATE

    if POSTULANT_ROLE in current_user.roles:
        return db.candidat_profiles, PROFILE_TYPE_POSTULANT

    if INTERIM_ROLE in current_user.roles:
        return db.interim_profiles, PROFILE_TYPE_INTERIM

    if AGENCY_ROLE in current_user.roles:
        return db.agency_country_profiles, PROFILE_TYPE_AGENCY_COUNTRY

    if COMPANY_ROLE in current_user.roles:
        return db.company_manager_profiles, PROFILE_TYPE_COMPANY

    return db.collaborator_profiles, PROFILE_TYPE_COLLABORATOR


def calculate_profile_completion(profile_data: dict, profile_type: str) -> int:
    """Calculate profile completion percentage based on filled fields"""
    # Use same logic for interim, candidat, and postulant profiles
    if profile_type in [PROFILE_TYPE_INTERIM, PROFILE_TYPE_CANDIDATE, PROFILE_TYPE_POSTULANT]:
        total_fields = 20  # Augmenté pour inclure les champs de base
        filled = 0
        
        # Champs de base (essentiels)
        if profile_data.get("first_name"): filled += 1
        if profile_data.get("last_name"): filled += 1
        if profile_data.get("email"): filled += 1
        if profile_data.get("phone"): filled += 1
        if profile_data.get("date_of_birth"): filled += 1
        if profile_data.get("place_of_birth"): filled += 1
        if profile_data.get("address"): filled += 1
        
        # Informations professionnelles
        if profile_data.get("education_level"): filled += 1
        if profile_data.get("years_of_experience"): filled += 1
        if profile_data.get("sectors") and len(profile_data["sectors"]) > 0: filled += 1
        if profile_data.get("skills") and len(profile_data["skills"]) > 0: filled += 1
        if profile_data.get("languages") and len(profile_data["languages"]) > 0: filled += 1
        if profile_data.get("has_driving_license"): filled += 1
        
        # Disponibilités
        if profile_data.get("general_availability") and len(profile_data["general_availability"]) > 0: filled += 1
        if profile_data.get("available_immediately") or profile_data.get("available_from_date"): filled += 1
        if profile_data.get("accepted_mission_types") and len(profile_data["accepted_mission_types"]) > 0: filled += 1
        
        # Documents (important)
        if profile_data.get("cv_document_id"): filled += 2  # CV est très important
        if profile_data.get("photo_url"): filled += 1
        if profile_data.get("nationality"): filled += 1
        if profile_data.get("document_ids") and len(profile_data["document_ids"]) > 0: filled += 1
        
        return int((filled / total_fields) * 100)
    
    elif profile_type == PROFILE_TYPE_COMPANY:
        total_fields = 2
        filled = 0
        if profile_data.get("job_title"): filled += 1
        if profile_data.get("department"): filled += 1
        return int((filled / total_fields) * 100)
    
    return 0


@profile_router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's profile based on their role"""
    profile_collection, profile_type_to_return = get_profile_context(current_user, db)

    # Determine profile collection based on role
    # Support for interim, candidat, and postulant roles
    if INTERIM_ROLE in current_user.roles or CANDIDATE_ROLE in current_user.roles or POSTULANT_ROLE in current_user.roles:
        profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})
        
        # Parse full_name into first_name and last_name if available
        first_name = None
        last_name = None
        if current_user.full_name:
            name_parts = current_user.full_name.strip().split(None, 1)
            first_name = name_parts[0] if len(name_parts) > 0 else None
            last_name = name_parts[1] if len(name_parts) > 1 else None
        
        if not profile:
            # Create default profile with user's basic info
            profile = {
                "user_id": current_user.id,
                "first_name": first_name,
                "last_name": last_name,
                "email": current_user.email,
                "phone": current_user.phone_number if hasattr(current_user, 'phone_number') and current_user.phone_number else None,
                "sectors": [],
                "skills": [],
                "languages": [],
                "has_driving_license": False,
                "driving_license_types": [],
                "general_availability": [],
                "available_immediately": False,
                "accepted_mission_types": [],
                "blocked_dates": [],
                "document_ids": [],
                "profile_completed": False,
                "profile_completion_percentage": 0,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            # Calculate initial completion
            completion = calculate_profile_completion(profile, profile_type_to_return)
            profile["profile_completion_percentage"] = completion
            profile["profile_completed"] = completion >= 80
            
            await profile_collection.insert_one(profile)

            # Reload profile without _id
            profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})
        else:
            # Ensure basic user info is synced from user object if missing in profile
            needs_update = False
            updates = {}
            
            if not profile.get("first_name") and first_name:
                updates["first_name"] = first_name
                needs_update = True
            if not profile.get("last_name") and last_name:
                updates["last_name"] = last_name
                needs_update = True
            if not profile.get("email") and current_user.email:
                updates["email"] = current_user.email
                needs_update = True
            if not profile.get("phone") and hasattr(current_user, 'phone_number') and current_user.phone_number:
                updates["phone"] = current_user.phone_number
                needs_update = True
            
            if needs_update:
                updates["updated_at"] = datetime.now(timezone.utc).isoformat()
                await profile_collection.update_one(
                    {"user_id": current_user.id},
                    {"$set": updates}
                )
                # Reload profile with updates
                profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})

                # Recalculate completion with synced data
                completion = calculate_profile_completion(profile, profile_type_to_return)
                await profile_collection.update_one(
                    {"user_id": current_user.id},
                    {"$set": {
                        "profile_completion_percentage": completion,
                        "profile_completed": completion >= 80
                    }}
                )
                profile["profile_completion_percentage"] = completion
                profile["profile_completed"] = completion >= 80

        # Add is_verified from user to profile response for email verification status consistency
        profile["is_verified"] = current_user.is_verified
        
        return {"profile_type": profile_type_to_return, "profile": profile}
    
    elif COMPANY_ROLE in current_user.roles:
        profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})
        if not profile:
            profile = {
                "user_id": current_user.id,
                "document_ids": [],
                "profile_completed": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await profile_collection.insert_one(profile)

            completion = calculate_profile_completion(profile, PROFILE_TYPE_COMPANY)
            await profile_collection.update_one(
                {"user_id": current_user.id},
                {"$set": {
                    "profile_completion_percentage": completion,
                    "profile_completed": completion >= 80
                }}
            )

            # Reload profile without _id
            profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})

        # Add is_verified from user to profile response
        profile["is_verified"] = current_user.is_verified

        return {"profile_type": PROFILE_TYPE_COMPANY, "profile": profile}

    elif AGENCY_ROLE in current_user.roles:
        profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})
        if not profile:
            profile = {
                "user_id": current_user.id,
                "document_ids": [],
                "profile_completed": False,
                "country": "GABON",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await profile_collection.insert_one(profile)

            # Reload profile without _id
            profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})

        # Add is_verified from user to profile response
        profile["is_verified"] = current_user.is_verified

        return {"profile_type": PROFILE_TYPE_AGENCY_COUNTRY, "profile": profile}
    
    else:
        # Collaborator or other roles
        profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})
        if not profile:
            profile = {
                "user_id": current_user.id,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await profile_collection.insert_one(profile)

            completion = calculate_profile_completion(profile, PROFILE_TYPE_COLLABORATOR)
            await profile_collection.update_one(
                {"user_id": current_user.id},
                {"$set": {
                    "profile_completion_percentage": completion,
                    "profile_completed": completion >= 80
                }}
            )

            # Reload profile without _id
            profile = await profile_collection.find_one({"user_id": current_user.id}, {"_id": 0})
        
        # Add is_verified from user to profile response
        profile["is_verified"] = current_user.is_verified
        
        return {"profile_type": PROFILE_TYPE_COLLABORATOR, "profile": profile}


@profile_router.put("/me")
async def update_my_profile(
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update current user's profile"""
    # Remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # If skills are being updated, add new ones to system references
    if "skills" in update_data and isinstance(update_data["skills"], list):
        for skill in update_data["skills"]:
            skill_name = skill if isinstance(skill, str) else skill.get("name")
            if skill_name:
                # Check if skill exists in references
                existing_skill = await db.system_references.find_one({
                    "category": "skills",
                    "code": skill_name.lower().replace(" ", "_")
                })
                
                if not existing_skill:
                    # Add new skill to references
                    new_skill_ref = {
                        "id": str(uuid.uuid4()),
                        "category": "skills",
                        "code": skill_name.lower().replace(" ", "_"),
                        "label_fr": skill_name,
                        "label_en": skill_name,
                        "description": f"Compétence: {skill_name}",
                        "is_active": True,
                        "metadata": {
                            "added_by": "user",
                            "user_id": current_user.id
                        },
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    await db.system_references.insert_one(new_skill_ref)
    
    collection, profile_type = get_profile_context(current_user, db)
    
    # Update profile
    await collection.update_one(
        {"user_id": current_user.id},
        {"$set": update_data},
        upsert=True
    )
    
    # Calculate completion
    updated_profile = await collection.find_one({"user_id": current_user.id}, {"_id": 0})
    completion = calculate_profile_completion(updated_profile, profile_type)
    
    await collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "profile_completion_percentage": completion,
            "profile_completed": completion >= 80
        }}
    )
    
    return {
        "success": True,
        "message": "Profil mis à jour",
        "completion_percentage": completion
    }


@profile_router.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload a document (CV, diploma, certificate, etc.)"""
    allowed_document_types = cfg.get_all_document_types()
    if document_type not in allowed_document_types:
        raise HTTPException(status_code=400, detail="Document type not allowed")

    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size: 5MB")
    
    # Validate MIME type
    mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"File type not allowed: {mime_type}")
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{current_user.id}_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create document record
    document = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "type": document_type,
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": mime_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.documents.insert_one(document)
    
    # Update profile with document ID
    collection, profile_type = get_profile_context(current_user, db)

    update_doc = {
        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
        "$setOnInsert": {"user_id": current_user.id}
    }

    if document_type == DOCUMENT_TYPE_CV:
        update_doc["$set"]["cv_document_id"] = document["id"]
    else:
        update_doc["$addToSet"] = {"document_ids": document["id"]}
        update_doc["$setOnInsert"]["document_ids"] = []

    await collection.update_one(
        {"user_id": current_user.id},
        update_doc,
        upsert=True
    )

    # Recalculate completion after document change
    profile = await collection.find_one({"user_id": current_user.id}, {"_id": 0}) or {}
    completion = calculate_profile_completion(profile, profile_type)

    await collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "profile_completion_percentage": completion,
            "profile_completed": completion >= 80,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return DocumentUploadResponse(
        success=True,
        document_id=document["id"],
        filename=file.filename,
        file_size=file_size,
        message="Document uploadé avec succès"
    )


@profile_router.get("/documents")
async def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all documents for current user"""
    documents = await db.documents.find(
        {"user_id": current_user.id},
        {"_id": 0, "file_path": 0}  # Don't expose file path
    ).to_list(length=100)
    
    return {"documents": documents}


@profile_router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a document"""
    # Find document
    document = await db.documents.find_one({
        "id": document_id,
        "user_id": current_user.id
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    try:
        if os.path.exists(document["file_path"]):
            os.remove(document["file_path"])
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Delete from database
    await db.documents.delete_one({"id": document_id})
    
    # Remove from profile
    collection, profile_type = get_profile_context(current_user, db)

    if document["type"] == DOCUMENT_TYPE_CV:
        await collection.update_one(
            {"user_id": current_user.id},
            {"$unset": {"cv_document_id": ""}}
        )
    else:
        await collection.update_one(
            {"user_id": current_user.id},
            {"$pull": {"document_ids": document_id}}
        )

    # Recalculate completion after document removal
    profile = await collection.find_one({"user_id": current_user.id}, {"_id": 0}) or {}
    completion = calculate_profile_completion(profile, profile_type)

    await collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "profile_completion_percentage": completion,
            "profile_completed": completion >= 80,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"success": True, "message": "Document supprimé"}
