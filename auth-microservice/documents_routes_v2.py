"""Documents Routes V2 - Architecture IAM Unifiée
Gestion des documents avec référentiel dynamique et filtrage IAM complet
"""
import os
import mimetypes
from typing import List, Optional
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status

from awana_auth.core.models import User
from awana_auth.services.iam_service import IAMService
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.database import get_database
from awana_auth.core.models import Document

router = APIRouter(prefix="/documents", tags=["documents"])

# Configuration upload
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.xlsx', '.xls'}

os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def generate_unique_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid4()}{ext}"


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    visibility: str = Form(default="private"),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_confidential: bool = Form(default=False),
    retention_period_days: Optional[int] = Form(None),
    current_user: User = Depends(require_permission("documents.create")),
    db = Depends(get_database)
):
    """Upload un document avec catégorie validée depuis le référentiel dynamique"""
    
    # Récupérer les catégories valides depuis le référentiel (pas de valeurs en dur !)
    valid_categories_docs = await db.system_references.find(
        {"category": "documents_types", "is_active": True},
        {"_id": 0, "code": 1}
    ).to_list(1000)
    
    valid_categories = [cat["code"] for cat in valid_categories_docs]
    
    # Si aucune catégorie n'est configurée, fallback sur les basiques
    if not valid_categories:
        valid_categories = ["cv", "piece_identite", "justificatif_domicile", "other"]
    
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Vérifier le type de fichier
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Lire le contenu
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Sauvegarder le fichier
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Parser les tags
    import json
    parsed_tags = [category]  # Tag automatique avec la catégorie
    if tags:
        try:
            additional_tags = json.loads(tags)
            parsed_tags.extend(additional_tags)
        except (json.JSONDecodeError, ValueError):
            parsed_tags.extend([t.strip() for t in tags.split(',') if t.strip()])
    
    # Calculer expiration
    expiry_date = None
    if retention_period_days:
        expiry_date = (datetime.now(timezone.utc) + timedelta(days=retention_period_days)).isoformat()
    
    # Créer le document
    doc_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    document = {
        "id": doc_id,
        "user_id": current_user.id,
        "user_email": current_user.email or "",
        "user_name": current_user.full_name,
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_size": file_size,
        "mime_type": file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream",
        "category": category,
        "visibility": visibility,
        "description": description,
        "tags": parsed_tags,
        "status": "pending",
        "is_confidential": is_confidential,
        "verified_by": None,
        "verified_at": None,
        "retention_period_days": retention_period_days,
        "expiry_date": expiry_date,
        "created_at": now,
        "updated_at": now,
        "download_count": 0
    }
    
    await db.documents.insert_one(document)
    
    return Document(**{k: v for k, v in document.items() if k != '_id'})


@router.get("/", response_model=List[Document])
async def list_documents(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(require_permission("documents.read")),
    db = Depends(get_database)
):
    """Lister les documents avec filtrage IAM complet
    
    Règles de visibilité :
    - Utilisateur normal : seulement ses documents (documents.read.own)
    - RRH/Recrutement : ses documents + tous les CV (documents.view_cv.all)
    - Admin : tous les documents (documents.read.all ou documents.manage.all)
    """
    
    iam_service = IAMService(db)
    
    # Vérifier les permissions
    has_view_all = await iam_service.user_has_permission(current_user.id, "documents.read.all")
    has_manage_all = await iam_service.user_has_permission(current_user.id, "documents.manage.all")
    has_view_cv_all = await iam_service.user_has_permission(current_user.id, "documents.view_cv.all")
    
    query = {}
    
    # Admin : voir tous les documents
    if has_view_all.has_permission or has_manage_all.has_permission:
        # Pas de filtre user_id
        pass
    # RRH/Recrutement : ses documents + tous les CV
    elif has_view_cv_all.has_permission:
        query["$or"] = [
            {"user_id": current_user.id},  # Ses documents
            {"category": "cv"},  # Tous les CV
            {"tags": "cv"}  # Documents tagués CV
        ]
    # Utilisateur normal : seulement ses documents
    else:
        query["user_id"] = current_user.id
    
    # Filtres optionnels
    if category:
        query["category"] = category
    
    if status_filter:
        query["status"] = status_filter
    
    documents = await db.documents.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [Document(**doc) for doc in documents]


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: User = Depends(require_permission("documents.read")),
    db = Depends(get_database)
):
    """Récupérer un document avec vérification IAM complète"""
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    iam_service = IAMService(db)
    
    # Si propriétaire
    if document["user_id"] == current_user.id:
        return Document(**document)
    
    # Vérifier permissions admin
    has_view_all = await iam_service.user_has_permission(current_user.id, "documents.read.all")
    has_manage_all = await iam_service.user_has_permission(current_user.id, "documents.manage.all")
    
    if has_view_all.has_permission or has_manage_all.has_permission:
        return Document(**document)
    
    # Vérifier permission RRH/Recrutement pour les CV
    if document["category"] == "cv" or "cv" in document.get("tags", []):
        has_view_cv = await iam_service.user_has_permission(current_user.id, "documents.view_cv.all")
        if has_view_cv.has_permission:
            return Document(**document)
    
    # Document privé sans permissions
    if document.get("visibility") == "private":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return Document(**document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(require_permission("documents.delete")),
    db = Depends(get_database)
):
    """Supprimer un document"""
    
    document = await db.documents.find_one({"id": document_id})
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Vérifier propriété ou permission admin
    iam_service = IAMService(db)
    has_delete_all = await iam_service.user_has_permission(current_user.id, "documents.delete.all")
    
    if document["user_id"] != current_user.id and not has_delete_all.has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Supprimer le fichier physique
    file_path = os.path.join(UPLOAD_DIR, document["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Supprimer de la DB
    await db.documents.delete_one({"id": document_id})
    
    return None
