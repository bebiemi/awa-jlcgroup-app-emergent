"""
Entreprise Form Configuration Routes
Système de gestion des champs dynamiques pour les fiches entreprises
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.dependencies.permission_dependencies import require_permission

router = APIRouter(prefix="/entreprises/form-config", tags=["Entreprise Form Config"])

# ==================== MODELS ====================

class FieldOption(BaseModel):
    """Option pour les champs de type select"""
    label: str
    value: str

class FieldValidation(BaseModel):
    """Règles de validation pour un champ"""
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    custom_error_message: Optional[str] = None

class FormFieldConfig(BaseModel):
    """Configuration d'un champ de formulaire"""
    id: Optional[str] = None
    field_key: str = Field(..., description="Clé unique du champ (snake_case)")
    field_label: str = Field(..., description="Label affiché")
    field_type: str = Field(..., description="text|textarea|select|multiselect|checkbox|radio|date|number|email|tel|url|file")
    category: str = Field(default="general", description="Catégorie du champ")
    order: int = Field(default=0, description="Ordre d'affichage")
    
    # Options de configuration
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[Any] = None
    options: Optional[List[FieldOption]] = None  # Pour select/radio
    
    # Validation
    validation: FieldValidation = Field(default_factory=FieldValidation)
    
    # Visibilité et permissions
    visible_for_roles: List[str] = Field(default_factory=lambda: ["admin", "company_manager"])
    editable_for_roles: List[str] = Field(default_factory=lambda: ["admin"])
    
    # État
    is_active: bool = True
    is_system: bool = False
    
    # Métadonnées
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

class FormFieldUpdate(BaseModel):
    """Modèle pour mise à jour d'un champ"""
    field_label: Optional[str] = None
    field_type: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[Any] = None
    options: Optional[List[FieldOption]] = None
    validation: Optional[FieldValidation] = None
    visible_for_roles: Optional[List[str]] = None
    editable_for_roles: Optional[List[str]] = None
    is_active: Optional[bool] = None

class FormConfigResponse(BaseModel):
    """Réponse avec la configuration complète du formulaire"""
    fields: List[FormFieldConfig]
    categories: List[str]
    total_fields: int

# ==================== CREATE FIELD ====================

@router.post("/fields", response_model=FormFieldConfig, status_code=status.HTTP_201_CREATED)
async def create_form_field(
    field_data: FormFieldConfig,
    current_user: User = Depends(require_permission("forms.enterprise.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un nouveau champ de formulaire
    Nécessite: forms.enterprise.manage
    """
    # Vérifier que la clé du champ n'existe pas déjà
    existing = await db.entreprise_form_fields.find_one({"field_key": field_data.field_key})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un champ avec la clé '{field_data.field_key}' existe déjà"
        )
    
    # Créer le champ
    field_id = str(uuid.uuid4())
    field_doc = {
        "id": field_id,
        **field_data.model_dump(exclude={"id"}),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": current_user.id
    }
    
    await db.entreprise_form_fields.insert_one(field_doc)
    
    field_doc.pop("_id", None)
    return field_doc


# ==================== GET PUBLIC FIELDS (FOR REGISTRATION) ====================

@router.get("/fields/public", response_model=FormConfigResponse)
async def get_public_form_fields(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les champs du formulaire visibles pour le public (inscription)
    Endpoint PUBLIC - ne nécessite pas d'authentification
    """
    query = {
        "is_active": True,
        "visible_for_roles": {"$in": ["public", "all"]}
    }
    
    # Récupérer les champs triés par ordre
    fields = await db.entreprise_form_fields.find(query, {"_id": 0}).sort("order", 1).to_list(None)
    
    # Extraire les catégories uniques
    categories = list(set([f.get("category", "general") for f in fields]))
    
    return {
        "fields": fields,
        "categories": sorted(categories),
        "total_fields": len(fields)
    }


# ==================== GET ALL FIELDS ====================

@router.get("/fields", response_model=FormConfigResponse)
async def get_form_fields(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer tous les champs du formulaire
    Accessible à tous les utilisateurs authentifiés
    """
    query = {}
    
    if category:
        query["category"] = category
    
    if is_active is not None:
        query["is_active"] = is_active
    
    # Récupérer les champs triés par ordre
    fields = await db.entreprise_form_fields.find(query, {"_id": 0}).sort("order", 1).to_list(None)
    
    # Extraire les catégories uniques
    categories = list(set([f.get("category", "general") for f in fields]))
    
    return {
        "fields": fields,
        "categories": sorted(categories),
        "total_fields": len(fields)
    }


# ==================== GET FIELD BY ID ====================

@router.get("/fields/{field_id}", response_model=FormFieldConfig)
async def get_form_field(
    field_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Récupérer un champ par son ID"""
    field = await db.entreprise_form_fields.find_one({"id": field_id}, {"_id": 0})
    
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Champ non trouvé"
        )
    
    return field


# ==================== UPDATE FIELD ====================

@router.patch("/fields/{field_id}", response_model=FormFieldConfig)
async def update_form_field(
    field_id: str,
    field_update: FormFieldUpdate,
    current_user: User = Depends(require_permission("forms.enterprise.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un champ
    Nécessite: forms.enterprise.update
    """
    # Vérifier que le champ existe
    existing = await db.entreprise_form_fields.find_one({"id": field_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Champ non trouvé"
        )
    
    # Ne pas permettre la modification des champs système
    if existing.get("is_system") and not current_user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de modifier un champ système"
        )
    
    # Préparer les données de mise à jour
    update_data = field_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Mettre à jour
    await db.entreprise_form_fields.update_one(
        {"id": field_id},
        {"$set": update_data}
    )
    
    # Récupérer le champ mis à jour
    updated_field = await db.entreprise_form_fields.find_one({"id": field_id}, {"_id": 0})
    
    return updated_field


# ==================== DELETE FIELD ====================

@router.delete("/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form_field(
    field_id: str,
    current_user: User = Depends(require_permission("forms.enterprise.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Supprimer un champ
    Nécessite: forms.enterprise.manage
    """
    # Vérifier que le champ existe
    existing = await db.entreprise_form_fields.find_one({"id": field_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Champ non trouvé"
        )
    
    # Ne pas permettre la suppression des champs système
    if existing.get("is_system"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de supprimer un champ système"
        )
    
    # Supprimer
    await db.entreprise_form_fields.delete_one({"id": field_id})


# ==================== REORDER FIELDS ====================

@router.post("/fields/reorder")
async def reorder_fields(
    field_orders: List[dict],  # [{"id": "field_id", "order": 1}, ...]
    current_user: User = Depends(require_permission("forms.enterprise.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Réorganiser l'ordre des champs
    Nécessite: forms.enterprise.update
    """
    for item in field_orders:
        field_id = item.get("id")
        order = item.get("order")
        
        if field_id and order is not None:
            await db.entreprise_form_fields.update_one(
                {"id": field_id},
                {"$set": {"order": order, "updated_at": datetime.now(timezone.utc)}}
            )
    
    return {"message": f"{len(field_orders)} champs réorganisés"}


# ==================== GET FIELDS BY ROLE ====================

@router.get("/fields/for-role/{role}")
async def get_fields_for_role(
    role: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les champs visibles pour un rôle spécifique
    Utile pour générer dynamiquement les formulaires côté frontend
    """
    # Récupérer tous les champs actifs visibles pour ce rôle
    fields = await db.entreprise_form_fields.find(
        {
            "is_active": True,
            "visible_for_roles": {"$in": [role, "all"]}
        },
        {"_id": 0}
    ).sort("order", 1).to_list(None)
    
    # Déterminer quels champs sont éditables
    for field in fields:
        field["is_editable"] = role in field.get("editable_for_roles", [])
    
    return {
        "fields": fields,
        "total": len(fields)
    }
