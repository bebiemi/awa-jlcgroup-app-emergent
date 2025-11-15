"""
Routes publiques pour les références système
Permet aux utilisateurs authentifiés de récupérer les référentiels (document_types, skills, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from awana_auth.core.dependencies import get_database, get_current_user

router = APIRouter(prefix="/api/system-references", tags=["system-references"])


@router.get("/document-types")
async def get_document_types(
    required_only: bool = Query(False, description="Ne retourner que les documents requis"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer la liste des types de documents disponibles
    Accessible à tous les utilisateurs authentifiés
    """
    query = {"category": "document_types", "is_active": True}
    
    document_types = await db.system_references.find(
        query, 
        {"_id": 0}
    ).sort("order", 1).to_list(length=None)
    
    # Filtrer pour ne garder que les documents requis si demandé
    if required_only:
        document_types = [
            dt for dt in document_types 
            if dt.get("is_system", False) or 
               "onboarding" in dt.get("metadata", {}).get("required_for", [])
        ]
    
    return {
        "success": True,
        "data": document_types,
        "total": len(document_types)
    }


@router.get("/categories/{category}")
async def get_references_by_category(
    category: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer les références pour une catégorie donnée
    Catégories disponibles: document_types, skills, roles, countries, etc.
    """
    references = await db.system_references.find(
        {"category": category, "is_active": True},
        {"_id": 0}
    ).sort("order", 1).to_list(length=None)
    
    if not references:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune référence trouvée pour la catégorie '{category}'"
        )
    
    return {
        "success": True,
        "category": category,
        "data": references,
        "total": len(references)
    }


@router.get("/categories")
async def list_categories(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Lister toutes les catégories de références disponibles
    """
    categories = await db.system_references.distinct("category")
    
    # Compter les références par catégorie
    category_counts = {}
    for cat in categories:
        count = await db.system_references.count_documents({
            "category": cat,
            "is_active": True
        })
        category_counts[cat] = count
    
    return {
        "success": True,
        "categories": sorted(categories),
        "counts": category_counts
    }
