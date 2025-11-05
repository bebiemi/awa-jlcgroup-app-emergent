"""
Document Upload Routes
Gestion des uploads de fichiers (CV, certificats, contrats)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime, timezone
import uuid
import os
import shutil

from awana_auth.core.dependencies import get_database
from awana_auth.core.config_manager import get_config
from awana_auth.core.models import User
from awana_auth.core.dependencies import get_current_user as get_user_dep

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Upload directory - Chargé depuis ConfigManager
config = get_config()
UPLOAD_DIR = config.get("storage.uploads.base_path", default="/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Custom dependency to get user as dict
async def get_current_user(user: User = Depends(get_user_dep)) -> dict:
    """Get current user as dict"""
    return {
        "sub": user.id,
        "email": user.email,
        "roles": user.roles or [],
        "full_name": user.full_name
    }

get_db = get_database


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "other",
    application_id: Optional[str] = None,
    mission_id: Optional[str] = None,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Upload un document
    Types: cv, cover_letter, medical_certificate, contract, id_document, other
    """
    # Validate file size (max 10MB)
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Fichier trop volumineux (max 10MB)"
                    )
                buffer.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )
    
    # Create document record
    document_id = str(uuid.uuid4())
    document_data = {
        "id": document_id,
        "user_id": current_user["sub"],
        "application_id": application_id,
        "mission_id": mission_id,
        "document_type": document_type,
        "file_name": file.filename,
        "file_path": file_path,
        "file_url": f"/api/documents/{document_id}/download",
        "file_size": file_size,
        "mime_type": file.content_type,
        "description": description,
        "validated": False,
        "uploaded_at": datetime.now(timezone.utc),
    }
    
    await db.documents.insert_one(document_data)
    
    return {
        "id": document_id,
        "file_name": file.filename,
        "file_url": document_data["file_url"],
        "file_size": file_size,
        "uploaded_at": document_data["uploaded_at"].isoformat()
    }


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Télécharger un document"""
    document = await db.documents.find_one({"id": document_id})
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document non trouvé"
        )
    
    # Check permissions
    user_roles = current_user.get("roles", [])
    is_admin = any(role in user_roles for role in ["admin", "super_admin", "commercial"])
    is_owner = document["user_id"] == current_user["sub"]
    
    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce document"
        )
    
    file_path = document["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier non trouvé sur le serveur"
        )
    
    return FileResponse(
        path=file_path,
        filename=document["file_name"],
        media_type=document["mime_type"]
    )


@router.get("/application/{application_id}")
async def get_application_documents(
    application_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Récupérer tous les documents d'une candidature"""
    documents = await db.documents.find({"application_id": application_id}).to_list(length=None)
    
    return [
        {
            "id": doc["id"],
            "file_name": doc["file_name"],
            "file_url": doc["file_url"],
            "file_size": doc["file_size"],
            "document_type": doc["document_type"],
            "description": doc.get("description"),
            "uploaded_at": doc["uploaded_at"],
            "validated": doc.get("validated", False),
        }
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Supprimer un document"""
    document = await db.documents.find_one({"id": document_id})
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document non trouvé"
        )
    
    # Check permissions
    user_roles = current_user.get("roles", [])
    is_admin = any(role in user_roles for role in ["admin", "super_admin"])
    is_owner = document["user_id"] == current_user["sub"]
    
    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres documents"
        )
    
    # Delete file
    file_path = document["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete database record
    await db.documents.delete_one({"id": document_id})
    
    return {"success": True, "message": "Document supprimé"}
