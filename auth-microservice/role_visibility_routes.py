"""
Routes pour gérer la visibilité des rôles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional
from awana_auth.core.models import User
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.services.feature_flag_service import FeatureFlagService
from awana_auth.core.feature_flag_models import AuditEventType


router = APIRouter(prefix="/api/roles", tags=["roles-visibility"])


class RoleVisibilityUpdate(BaseModel):
    """Mise à jour de la visibilité d'un rôle"""
    is_hidden_from_admins: bool


@router.get("")
async def list_roles(
    include_hidden_info: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Liste tous les rôles avec leur statut de visibilité
    
    - Admins: Ne voient pas l'info is_hidden_from_admins
    - Super-admins: Voient tout avec include_hidden_info=true
    """
    is_super_admin = "super_admin" in current_user.roles
    
    # Récupérer les rôles
    roles = await db.system_references.find(
        {"category": "roles", "is_active": True},
        {"_id": 0}
    ).to_list(length=None)
    
    # Filtrer les infos sensibles pour non super-admins
    if not is_super_admin or not include_hidden_info:
        for role in roles:
            role.pop("is_hidden_from_admins", None)
    
    return {
        "roles": roles,
        "total": len(roles),
        "can_modify_visibility": is_super_admin
    }


@router.get("/{role_code}")
async def get_role(
    role_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Récupérer les détails d'un rôle"""
    role = await db.system_references.find_one(
        {"category": "roles", "code": role_code},
        {"_id": 0}
    )
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle '{role_code}' non trouvé"
        )
    
    # Masquer is_hidden_from_admins pour non super-admins
    is_super_admin = "super_admin" in current_user.roles
    if not is_super_admin:
        role.pop("is_hidden_from_admins", None)
    
    return role


@router.patch("/{role_code}/visibility", dependencies=[Depends(require_permission("users.manage"))])
async def update_role_visibility(
    role_code: str,
    update: RoleVisibilityUpdate,
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour la visibilité d'un rôle aux admins
    Réservé aux super-admins uniquement
    """
    # Vérifier que le rôle existe
    role = await db.system_references.find_one(
        {"category": "roles", "code": role_code}
    )
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle '{role_code}' non trouvé"
        )
    
    old_value = role.get("is_hidden_from_admins", False)
    
    # Mettre à jour
    result = await db.system_references.update_one(
        {"category": "roles", "code": role_code},
        {"$set": {"is_hidden_from_admins": update.is_hidden_from_admins}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune modification effectuée"
        )
    
    # Audit
    service = FeatureFlagService(db)
    await service._create_audit_event(
        actor_id=current_user.id,
        actor_name=current_user.full_name or current_user.username,
        action=AuditEventType.ROLE_VISIBILITY_UPDATED,
        target_type="role",
        target_id=role["id"],
        payload={
            "role_code": role_code,
            "old_value": old_value,
            "new_value": update.is_hidden_from_admins
        }
    )
    
    return {
        "message": f"Visibilité du rôle '{role_code}' mise à jour",
        "role_code": role_code,
        "is_hidden_from_admins": update.is_hidden_from_admins,
        "old_value": old_value
    }


@router.get("/visibility/stats")
async def get_visibility_stats(
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Statistiques sur la visibilité des rôles
    Réservé aux super-admins
    """
    total_roles = await db.system_references.count_documents({
        "category": "roles",
        "is_active": True
    })
    
    hidden_roles = await db.system_references.count_documents({
        "category": "roles",
        "is_active": True,
        "is_hidden_from_admins": True
    })
    
    # Compter les utilisateurs avec rôles cachés
    hidden_role_docs = await db.system_references.find(
        {"category": "roles", "is_hidden_from_admins": True},
        {"_id": 0, "code": 1}
    ).to_list(length=None)
    
    hidden_role_codes = [r["code"] for r in hidden_role_docs]
    
    hidden_users_count = 0
    if hidden_role_codes:
        hidden_users_count = await db.users.count_documents({
            "roles": {"$in": hidden_role_codes}
        })
    
    return {
        "total_roles": total_roles,
        "visible_roles": total_roles - hidden_roles,
        "hidden_roles": hidden_roles,
        "users_with_hidden_roles": hidden_users_count
    }
