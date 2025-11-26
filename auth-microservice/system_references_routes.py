"""
Routes publiques pour les références système
Permet aux utilisateurs authentifiés de récupérer les référentiels (document_types, skills, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from awana_auth.core.dependencies import get_database, get_current_user, get_iam_service
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.services.iam_service import IAMService
from awana_auth.utils.config_helpers import cfg

router = APIRouter(prefix="/api/system-references", tags=["system-references"])
public_router = APIRouter(prefix="/api/public/system-references", tags=["system-references-public"])


ADMIN_ROLE = cfg.get_admin_role()
SUPER_ADMIN_ROLE = cfg.get_super_admin_role()


def _has_admin_role(roles: list) -> bool:
    """Check if the user has one of the configured admin roles."""
    normalized_roles = {role.lower() for role in (roles or [])}
    return ADMIN_ROLE.lower() in normalized_roles or SUPER_ADMIN_ROLE.lower() in normalized_roles


async def _ensure_admin_or_manage_permission(current_user, iam_service: IAMService) -> None:
    """
    Enforce admin role (config-driven) or explicit permission for reference management.
    """

    roles = getattr(current_user, "roles", []) if not isinstance(current_user, dict) else current_user.get("roles", [])
    user_id = getattr(current_user, "id", None) or current_user.get("id")
    has_manage = await iam_service.user_has_permission(user_id, "references.manage")

    if not _has_admin_role(roles) and not has_manage.has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Accès réservé aux administrateurs ou aux titulaires de la permission references.manage"
            ),
        )


@router.get("/document-types")
async def get_document_types(
    required_only: bool = Query(False, description="Ne retourner que les documents requis"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("references.read"))
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


# ==================== PUBLIC ENDPOINTS (filtrés) ====================

@public_router.get("/document-types")
async def get_public_document_types(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("references.read")),
    iam_service: IAMService = Depends(get_iam_service)
):
    """
    Référentiels de types de documents accessibles publiquement (actifs uniquement).
    Champs minimalistes (code, label_fr, label_en optionnel).
    """
    await _ensure_admin_or_manage_permission(current_user, iam_service)
    docs = await db.system_references.find(
        {"category": "document_types", "is_active": True},
        {"_id": 0, "code": 1, "label_fr": 1, "label_en": 1}
    ).sort("order", 1).to_list(length=None)
    return {"success": True, "data": docs, "total": len(docs)}


@public_router.get("/categories/{category}")
async def get_public_references_by_category(
    category: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("references.read")),
    iam_service: IAMService = Depends(get_iam_service)
):
    """
    Référentiels publics filtrés (actifs) par catégorie.
    """
    await _ensure_admin_or_manage_permission(current_user, iam_service)
    refs = await db.system_references.find(
        {"category": category, "is_active": True},
        {"_id": 0, "code": 1, "label_fr": 1, "label_en": 1}
    ).sort("order", 1).to_list(length=None)
    return {"success": True, "category": category, "data": refs, "total": len(refs)}


@router.get("/categories/{category}")
async def get_references_by_category(
    category: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission("references.read"))
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
    current_user: dict = Depends(require_permission("references.read"))
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
