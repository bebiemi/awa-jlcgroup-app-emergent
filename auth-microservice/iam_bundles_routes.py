"""
Routes API pour la gestion des Capability Bundles
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.dependencies.permission_dependencies import require_permission

router = APIRouter(prefix="/iam/bundles", tags=["IAM Bundles"])


class CapabilityBundleCreate(BaseModel):
    """Modèle de création de bundle"""
    code: str
    name: str
    description: str
    category: str
    permission_ids: List[str]
    tags: Optional[List[str]] = []


class CapabilityBundleUpdate(BaseModel):
    """Modèle de mise à jour de bundle"""
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class CapabilityBundleResponse(BaseModel):
    """Réponse bundle"""
    id: str
    code: str
    name: str
    description: str
    category: str
    permission_ids: List[str]
    tags: List[str]
    is_system: bool
    metadata: dict
    created_at: str
    updated_at: str


@router.get("", response_model=List[CapabilityBundleResponse])
async def get_bundles(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupère la liste des capability bundles
    Filtrage optionnel par catégorie
    """
    query = {}
    if category:
        query["category"] = category
    
    bundles = await db.capability_bundles.find(query, {"_id": 0}).to_list(1000)
    return bundles


@router.get("/{bundle_id}", response_model=CapabilityBundleResponse)
async def get_bundle(
    bundle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.read"))
):
    """
    Récupère les détails d'un bundle spécifique
    """
    bundle = await db.capability_bundles.find_one({"id": bundle_id}, {"_id": 0})
    
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle {bundle_id} non trouvé"
        )
    
    return bundle


@router.post("", response_model=CapabilityBundleResponse, status_code=status.HTTP_201_CREATED)
async def create_bundle(
    bundle: CapabilityBundleCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Crée un nouveau capability bundle
    Requiert: iam.permissions.update
    """
    # Vérifier que le code n'existe pas déjà
    existing = await db.capability_bundles.find_one({"code": bundle.code}, {"_id": 0})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un bundle avec le code '{bundle.code}' existe déjà"
        )
    
    # Créer le bundle
    new_bundle = {
        "id": str(uuid.uuid4()),
        "code": bundle.code,
        "name": bundle.name,
        "description": bundle.description,
        "category": bundle.category,
        "permission_ids": bundle.permission_ids,
        "tags": bundle.tags,
        "is_system": False,  # Les bundles créés via API ne sont jamais système
        "metadata": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.capability_bundles.insert_one(new_bundle)
    
    return new_bundle


@router.put("/{bundle_id}", response_model=CapabilityBundleResponse)
async def update_bundle(
    bundle_id: str,
    bundle_update: CapabilityBundleUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Met à jour un capability bundle
    Requiert: iam.permissions.update
    Les bundles système ne peuvent pas être modifiés
    """
    # Vérifier que le bundle existe
    existing = await db.capability_bundles.find_one({"id": bundle_id}, {"_id": 0})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle {bundle_id} non trouvé"
        )
    
    # Vérifier que ce n'est pas un bundle système
    if existing.get("is_system", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les bundles système ne peuvent pas être modifiés"
        )
    
    # Préparer les mises à jour
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if bundle_update.name is not None:
        update_data["name"] = bundle_update.name
    if bundle_update.description is not None:
        update_data["description"] = bundle_update.description
    if bundle_update.permission_ids is not None:
        update_data["permission_ids"] = bundle_update.permission_ids
    if bundle_update.tags is not None:
        update_data["tags"] = bundle_update.tags
    
    # Mettre à jour
    await db.capability_bundles.update_one(
        {"id": bundle_id},
        {"$set": update_data}
    )
    
    # Récupérer et retourner le bundle mis à jour
    updated_bundle = await db.capability_bundles.find_one({"id": bundle_id}, {"_id": 0})
    return updated_bundle


@router.delete("/{bundle_id}")
async def delete_bundle(
    bundle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(require_permission("iam.permissions.update"))
):
    """
    Supprime un capability bundle
    Requiert: iam:manage
    Les bundles système ne peuvent pas être supprimés
    """
    # Vérifier que le bundle existe
    existing = await db.capability_bundles.find_one({"id": bundle_id}, {"_id": 0})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bundle {bundle_id} non trouvé"
        )
    
    # Vérifier que ce n'est pas un bundle système
    if existing.get("is_system", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les bundles système ne peuvent pas être supprimés"
        )
    
    # Vérifier qu'aucun profil n'utilise ce bundle
    profiles_using_bundle = await db.profiles.count_documents({
        "capability_bundle_ids": bundle_id
    })
    
    if profiles_using_bundle > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ce bundle est utilisé par {profiles_using_bundle} profil(s). Impossible de le supprimer."
        )
    
    # Supprimer
    await db.capability_bundles.delete_one({"id": bundle_id})
    
    return {
        "success": True,
        "message": f"Bundle {bundle_id} supprimé avec succès"
    }
