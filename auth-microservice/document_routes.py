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
from awana_auth.utils.config_helpers import cfg

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
    # Récupérer les limites depuis la configuration
    max_file_size_mb = config.get("storage.uploads.max_file_size_mb", default=10)
    max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    # Récupérer les extensions autorisées
    allowed_extensions = config.get("storage.uploads.allowed_extensions", default=["pdf", "doc", "docx", "jpg", "png"])
    
    # Valider l'extension
    file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension de fichier non autorisée. Autorisées: {', '.join(allowed_extensions)}"
        )
    
    # Vérifier les limites spécifiques au type de document
    if document_type in config.get("storage.uploads.document_types", default={}):
        doc_config = config.get(f"storage.uploads.document_types.{document_type}")
        max_file_size_mb = doc_config.get("max_size_mb", max_file_size_mb)
        max_file_size_bytes = max_file_size_mb * 1024 * 1024
        type_allowed_formats = doc_config.get("allowed_formats", allowed_extensions)
        
        if file_extension not in type_allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format non autorisé pour {document_type}. Autorisés: {', '.join(type_allowed_formats)}"
            )
    
    # Validate file size
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                if file_size > max_file_size_bytes:
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Fichier trop volumineux (max {max_file_size_mb}MB)"
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
    is_admin = any(role in user_roles for role in cfg.get_validator_roles())
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
    """
    Récupérer tous les documents d'une candidature
    
    Accès :
    - Candidat propriétaire de la candidature
    - Entreprise propriétaire de la mission
    - Admin
    """
    user_id = current_user.get("sub")
    
    # Récupérer la candidature
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée"
        )
    
    # Récupérer la mission pour obtenir le company_id
    mission = await db.missions.find_one({"id": application.get("mission_id")})
    
    # Vérifier les droits d'accès
    is_candidate = application.get("candidate_id") == user_id
    is_company_owner = mission and mission.get("company_id") == current_user.get("company_id", "NONE")
    is_admin = "admin" in current_user.get("roles", []) or "super_admin" in current_user.get("roles", [])
    
    if not (is_candidate or is_company_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ces documents"
        )
    
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
    is_admin = any(role in user_roles for role in [cfg.get_admin_role(), cfg.get_super_admin_role()])
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
