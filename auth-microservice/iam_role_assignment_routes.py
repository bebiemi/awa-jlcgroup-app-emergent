"""
IAM Role Assignment Routes
Endpoints pour assigner des rôles IAM aux profils et groupes (modèle hybride)

Architecture:
- Users → Profiles → IAM Roles → Permissions
- Users → Groups → IAM Roles → Permissions
- Jamais de rôles IAM directement sur les users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel
import logging

from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.models import User
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iam", tags=["IAM Role Assignment"])


# ============================================================================
# Request/Response Models
# ============================================================================

class RoleAssignmentRequest(BaseModel):
    """Request pour assigner des rôles IAM"""
    role_ids: List[str]  # Liste des IDs de rôles IAM à assigner


class RoleAssignmentResponse(BaseModel):
    """Response après assignment de rôles"""
    success: bool
    message: str
    assigned_roles: List[str]


class IAMRoleResponse(BaseModel):
    """Response model pour un rôle IAM"""
    id: str
    code: str
    label: str
    description: str
    permissions: List[str]
    level: int
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    profile_count: int = 0  # Nombre de profils utilisant ce rôle


# ============================================================================
# IAM Roles Management
# ============================================================================

@router.get("/roles", response_model=List[IAMRoleResponse])
async def list_iam_roles(
    current_user: User = Depends(require_permission("rbac.read_roles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lister tous les rôles IAM disponibles avec le nombre de profils utilisant chaque rôle
    
    Permissions requises: rbac.read_roles
    """
    roles_collection = db.iam_roles
    profiles_collection = db.profiles
    
    # Récupérer tous les rôles IAM
    cursor = roles_collection.find({}, {"_id": 0})
    roles = await cursor.to_list(length=None)
    
    # Pour chaque rôle, compter le nombre de profils qui l'utilisent
    for role in roles:
        role_id = role.get("id")
        # Compter les profils ayant ce rôle dans leur iam_role_ids
        profile_count = await profiles_collection.count_documents(
            {"iam_role_ids": role_id}
        )
        role["profile_count"] = profile_count
    
    logger.info(f"Liste des rôles IAM récupérée par {current_user.username}")
    
    return roles


@router.get("/roles/{role_id}")
async def get_iam_role(
    role_id: str,
    current_user: User = Depends(require_permission("rbac.read_roles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer un rôle IAM spécifique
    
    Permissions requises: rbac.read_roles
    """
    roles_collection = db.iam_roles
    
    role = await roles_collection.find_one({"id": role_id}, {"_id": 0})
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rôle IAM {role_id} non trouvé"
        )
    
    return role


# ============================================================================
# Profile Role Assignment
# ============================================================================

@router.post("/profiles/{profile_id}/roles", response_model=RoleAssignmentResponse)
async def assign_roles_to_profile(
    profile_id: str,
    request: RoleAssignmentRequest,
    current_user: User = Depends(require_permission("rbac.manage_profile_roles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Assigner des rôles IAM à un profil métier
    
    Permissions requises: rbac.manage_profile_roles (admin/super_admin)
    """
    profiles_collection = db.profiles
    roles_collection = db.iam_roles
    
    # Vérifier que le profil existe
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil {profile_id} non trouvé"
        )
    
    # Vérifier que les rôles existent
    for role_id in request.role_ids:
        role = await roles_collection.find_one({"id": role_id})
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rôle IAM {role_id} non trouvé"
            )
    
    # Récupérer les rôles actuels
    current_role_ids = profile.get("iam_role_ids", [])
    
    # Ajouter les nouveaux rôles (éviter les doublons)
    updated_role_ids = list(set(current_role_ids + request.role_ids))
    
    # Mettre à jour le profil
    result = await profiles_collection.update_one(
        {"id": profile_id},
        {
            "$set": {
                "iam_role_ids": updated_role_ids,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": current_user.id
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de l'assignation des rôles"
        )
    
    logger.info(
        f"Rôles IAM assignés au profil {profile_id} par {current_user.username}: {request.role_ids}"
    )
    
    return RoleAssignmentResponse(
        success=True,
        message=f"{len(request.role_ids)} rôle(s) assigné(s) au profil avec succès",
        assigned_roles=request.role_ids
    )


@router.delete("/profiles/{profile_id}/roles/{role_id}")
async def remove_role_from_profile(
    profile_id: str,
    role_id: str,
    current_user: User = Depends(require_permission("rbac.manage_profile_roles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retirer un rôle IAM d'un profil métier
    
    Permissions requises: rbac.manage_profile_roles (admin/super_admin)
    """
    profiles_collection = db.profiles
    
    # Vérifier que le profil existe
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil {profile_id} non trouvé"
        )
    
    # Récupérer les rôles actuels
    current_role_ids = profile.get("iam_role_ids", [])
    
    # Retirer le rôle
    if role_id not in current_role_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le rôle {role_id} n'est pas assigné à ce profil"
        )
    
    updated_role_ids = [r for r in current_role_ids if r != role_id]
    
    # Mettre à jour le profil
    result = await profiles_collection.update_one(
        {"id": profile_id},
        {
            "$set": {
                "iam_role_ids": updated_role_ids,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": current_user.id
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec du retrait du rôle"
        )
    
    logger.info(
        f"Rôle IAM {role_id} retiré du profil {profile_id} par {current_user.username}"
    )
    
    return {"success": True, "message": "Rôle retiré du profil avec succès"}


@router.get("/profiles/{profile_id}/roles")
async def get_profile_roles(
    profile_id: str,
    current_user: User = Depends(require_permission("rbac.read_profiles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les rôles IAM d'un profil
    
    Permissions requises: rbac.read_profiles
    """
    profiles_collection = db.profiles
    roles_collection = db.iam_roles
    
    # Vérifier que le profil existe
    profile = await profiles_collection.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil {profile_id} non trouvé"
        )
    
    # Récupérer les rôles IAM
    role_ids = profile.get("iam_role_ids", [])
    roles = []
    
    for role_id in role_ids:
        role = await roles_collection.find_one({"id": role_id}, {"_id": 0})
        if role:
            roles.append(role)
    
    return {
        "profile_id": profile_id,
        "profile_name": profile.get("name"),
        "iam_roles": roles,
        "role_count": len(roles)
    }


# ============================================================================
# Group Role Assignment
# ============================================================================

@router.post("/groups/{group_id}/roles", response_model=RoleAssignmentResponse)
async def assign_roles_to_group(
    group_id: str,
    request: RoleAssignmentRequest,
    current_user: User = Depends(require_permission("rbac.manage_group_roles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Assigner des rôles IAM à un groupe organisationnel
    
    Permissions requises: rbac.manage_group_roles (admin/super_admin)
    """
    groups_collection = db.groups
    roles_collection = db.iam_roles
    
    # Vérifier que le groupe existe
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Groupe {group_id} non trouvé"
        )
    
    # Vérifier que les rôles existent
    for role_id in request.role_ids:
        role = await roles_collection.find_one({"id": role_id})
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rôle IAM {role_id} non trouvé"
            )
    
    # Récupérer les rôles actuels
    current_role_ids = group.get("iam_role_ids", [])
    
    # Ajouter les nouveaux rôles (éviter les doublons)
    updated_role_ids = list(set(current_role_ids + request.role_ids))
    
    # Mettre à jour le groupe
    result = await groups_collection.update_one(
        {"id": group_id},
        {
            "$set": {
                "iam_role_ids": updated_role_ids,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": current_user.id
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de l'assignation des rôles"
        )
    
    logger.info(
        f"Rôles IAM assignés au groupe {group_id} par {current_user.username}: {request.role_ids}"
    )
    
    return RoleAssignmentResponse(
        success=True,
        message=f"{len(request.role_ids)} rôle(s) assigné(s) au groupe avec succès",
        assigned_roles=request.role_ids
    )


@router.delete("/groups/{group_id}/roles/{role_id}")
async def remove_role_from_group(
    group_id: str,
    role_id: str,
    current_user: User = Depends(require_permission("rbac.manage_group_roles")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retirer un rôle IAM d'un groupe
    
    Permissions requises: rbac.manage_group_roles (admin/super_admin)
    """
    groups_collection = db.groups
    
    # Vérifier que le groupe existe
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Groupe {group_id} non trouvé"
        )
    
    # Récupérer les rôles actuels
    current_role_ids = group.get("iam_role_ids", [])
    
    # Retirer le rôle
    if role_id not in current_role_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le rôle {role_id} n'est pas assigné à ce groupe"
        )
    
    updated_role_ids = [r for r in current_role_ids if r != role_id]
    
    # Mettre à jour le groupe
    result = await groups_collection.update_one(
        {"id": group_id},
        {
            "$set": {
                "iam_role_ids": updated_role_ids,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": current_user.id
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec du retrait du rôle"
        )
    
    logger.info(
        f"Rôle IAM {role_id} retiré du groupe {group_id} par {current_user.username}"
    )
    
    return {"success": True, "message": "Rôle retiré du groupe avec succès"}


@router.get("/groups/{group_id}/roles")
async def get_group_roles(
    group_id: str,
    current_user: User = Depends(require_permission("rbac.read_groups")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les rôles IAM d'un groupe
    
    Permissions requises: rbac.read_groups
    """
    groups_collection = db.groups
    roles_collection = db.iam_roles
    
    # Vérifier que le groupe existe
    group = await groups_collection.find_one({"id": group_id})
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Groupe {group_id} non trouvé"
        )
    
    # Récupérer les rôles IAM
    role_ids = group.get("iam_role_ids", [])
    roles = []
    
    for role_id in role_ids:
        role = await roles_collection.find_one({"id": role_id}, {"_id": 0})
        if role:
            roles.append(role)
    
    return {
        "group_id": group_id,
        "group_name": group.get("name"),
        "iam_roles": roles,
        "role_count": len(roles)
    }
