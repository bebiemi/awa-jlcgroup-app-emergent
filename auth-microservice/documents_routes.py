"""
Documents Management Routes - Gestion des documents avec classifications et RGPD
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import os
import mimetypes

from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.services.iam_service import IAMService
from awana_auth.core.models import User

router = APIRouter(prefix="/api/documents", tags=["Documents"])


# ==================== Models ====================

class DocumentCategory(str):
    """Catégories de documents"""
    CV = "cv"
    COVER_LETTER = "cover_letter"
    DIPLOMA = "diploma"
    CERTIFICATE = "certificate"
    ID_CARD = "id_card"
    CONTRACT = "contract"
    PAYSLIP = "payslip"
    RGPD = "rgpd"
    OTHER = "other"


class DocumentStatus(str):
    """Statuts de documents"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DocumentVisibility(str):
    """Visibilité des documents"""
    PRIVATE = "private"  # Visible uniquement par le propriétaire
    TEAM = "team"  # Visible par l'équipe/managers
    PUBLIC = "public"  # Visible par tous (ex: CV public)


class DocumentCreate(BaseModel):
    category: str = Field(..., description="Document category")
    visibility: str = Field(default="private", description="Document visibility")
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    is_confidential: bool = Field(default=False)
    retention_period_days: Optional[int] = None  # RGPD: durée de conservation


class DocumentUpdate(BaseModel):
    category: Optional[str] = None
    visibility: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    is_confidential: Optional[bool] = None


class Document(BaseModel):
    id: str
    user_id: str
    user_email: str
    user_name: Optional[str] = None
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    category: str
    visibility: str
    description: Optional[str] = None
    tags: List[str] = []
    status: str
    is_confidential: bool
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    retention_period_days: Optional[int] = None
    expiry_date: Optional[str] = None
    created_at: str
    updated_at: str
    download_count: int = 0


# ==================== Configuration ====================

UPLOAD_DIR = "/app/uploads/documents"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'
}

# Créer le dossier d'upload s'il n'existe pas
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==================== Helper Functions ====================

def get_file_extension(filename: str) -> str:
    """Extraire l'extension du fichier"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def is_allowed_file(filename: str) -> bool:
    """Vérifier si le fichier est autorisé"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Générer un nom de fichier unique"""
    ext = get_file_extension(original_filename)
    return f"{uuid4()}.{ext}"


# ==================== Routes ====================

@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    visibility: str = Form(default="private"),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string
    is_confidential: bool = Form(default=False),
    retention_period_days: Optional[int] = Form(None),
    current_user: User = Depends(require_permission("documents.create")),
    db = Depends(get_database)
):
    """Upload un document"""
    
    # Valider la catégorie
    valid_categories = ["cv", "cover_letter", "diploma", "certificate", "id_card", "contract", "payslip", "rgpd", "other"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Valider la visibilité
    valid_visibilities = ["private", "team", "public"]
    if visibility not in valid_visibilities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid visibility. Must be one of: {', '.join(valid_visibilities)}"
        )
    
    # Vérifier le type de fichier
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Lire le contenu du fichier
    content = await file.read()
    file_size = len(content)
    
    # Vérifier la taille
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Générer un nom unique
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Sauvegarder le fichier
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Parser les tags
    import json
    parsed_tags = []
    if tags:
        try:
            parsed_tags = json.loads(tags)
        except:
            parsed_tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    # Calculer la date d'expiration
    expiry_date = None
    if retention_period_days:
        from datetime import timedelta
        expiry_date = (datetime.now(timezone.utc) + timedelta(days=retention_period_days)).isoformat()
    
    # Créer le document
    doc_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    document = {
        "id": doc_id,
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "user_name": current_user.get("full_name"),
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
    """Lister les documents de l'utilisateur"""
    
    query = {"user_id": current_user.id}
    
    if category:
        query["category"] = category
    
    if status_filter:
        query["status"] = status_filter
    
    documents = await db.documents.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [Document(**doc) for doc in documents]


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Récupérer un document"""
    
    document = await db.documents.find_one(
        {"id": document_id},
        {"_id": 0}
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Vérifier les permissions
    if document["user_id"] != current_user["id"]:
        # Si pas le propriétaire, vérifier la visibilité
        if document["visibility"] == "private":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return Document(**document)


@router.patch("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Mettre à jour un document"""
    
    # Vérifier que le document existe et appartient à l'utilisateur
    document = await db.documents.find_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Construire les mises à jour
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update_data.category:
        updates["category"] = update_data.category
    
    if update_data.visibility:
        updates["visibility"] = update_data.visibility
    
    if update_data.description is not None:
        updates["description"] = update_data.description
    
    if update_data.tags is not None:
        updates["tags"] = update_data.tags
    
    if update_data.status:
        updates["status"] = update_data.status
    
    if update_data.is_confidential is not None:
        updates["is_confidential"] = update_data.is_confidential
    
    # Appliquer les mises à jour
    await db.documents.update_one(
        {"id": document_id},
        {"$set": updates}
    )
    
    # Récupérer le document mis à jour
    updated_doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
    
    return Document(**updated_doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Supprimer un document"""
    
    # Vérifier que le document existe et appartient à l'utilisateur
    document = await db.documents.find_one(
        {"id": document_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Supprimer le fichier physique
    file_path = os.path.join(UPLOAD_DIR, document["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Supprimer de la base de données
    await db.documents.delete_one({"id": document_id})
    
    return None


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Télécharger un document"""
    from fastapi.responses import FileResponse
    
    # Récupérer le document
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Vérifier les permissions
    if document["user_id"] != current_user["id"]:
        if document["visibility"] == "private":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Chemin du fichier
    file_path = os.path.join(UPLOAD_DIR, document["filename"])
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    # Incrémenter le compteur de téléchargements
    await db.documents.update_one(
        {"id": document_id},
        {"$inc": {"download_count": 1}}
    )
    
    return FileResponse(
        path=file_path,
        filename=document["original_filename"],
        media_type=document["mime_type"]
    )


# ==================== Admin Routes ====================

@router.get("/admin/all", response_model=List[Document])
async def admin_list_documents(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """[Admin] Lister tous les documents"""
    
    # Vérifier les permissions admin
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    query = {}
    
    if user_id:
        query["user_id"] = user_id
    
    if category:
        query["category"] = category
    
    if status_filter:
        query["status"] = status_filter
    
    documents = await db.documents.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [Document(**doc) for doc in documents]


@router.patch("/admin/{document_id}/verify", response_model=Document)
async def admin_verify_document(
    document_id: str,
    approved: bool,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """[Admin] Vérifier/approuver un document"""
    
    # Vérifier les permissions admin
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Vérifier que le document existe
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Mettre à jour le statut
    now = datetime.now(timezone.utc).isoformat()
    updates = {
        "status": "verified" if approved else "rejected",
        "verified_by": current_user["id"],
        "verified_at": now,
        "updated_at": now
    }
    
    await db.documents.update_one(
        {"id": document_id},
        {"$set": updates}
    )
    
    # Récupérer le document mis à jour
    updated_doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
    
    return Document(**updated_doc)
