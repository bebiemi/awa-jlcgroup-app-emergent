"""
Service IAM Unifié - Support Profiles + Roles
Architecture hybride pour maximum de flexibilité et compatibilité
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Set, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class IAMUnifiedService:
    """
    Service IAM unifié supportant à la fois:
    - profiles (collection 'profiles') : profiles métier existants
    - iam_roles (collection 'iam_roles') : rôles IAM pour granularité fine
    - iam_permissions (collection 'iam_permissions') : permissions centralisées
    
    Priorité de consolidation :
    1. Permissions des profiles (via profile_ids)
    2. Permissions des roles IAM (via roles)
    3. Permissions des groupes (via group_ids)
    4. Déduplication automatique
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.profiles_collection = db.profiles  # Profiles métier existants
        self.iam_roles_collection = db.iam_roles  # Rôles IAM granulaires
        self.iam_permissions_collection = db.permissions  # FIX: Use 'permissions' not 'iam_permissions'
        self.users_collection = db.users
        self.groups_collection = db.iam_groups
    
    async def get_user_all_permissions(self, user_id: str) -> List[dict]:
        """
        Récupère TOUTES les permissions d'un utilisateur depuis toutes les sources
        
        Sources consolidées :
        1. Profiles métier (profile_ids → profiles.permission_ids)
        2. Rôles IAM (roles → iam_roles.permissions)  
        3. Groupes IAM (group_ids → groups → profiles/roles)
        
        Returns:
            List[dict]: Liste de permissions avec code, label, description
        """
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                logger.warning(f"User {user_id} not found")
                return []
            
            all_permission_codes = set()
            
            # ===== SOURCE 1: Profiles Métier =====
            profile_ids = user.get("profile_ids", [])
            if profile_ids:
                profiles_cursor = self.profiles_collection.find(
                    {"id": {"$in": profile_ids}},
                    {"permission_ids": 1}
                )
                
                async for profile in profiles_cursor:
                    permission_ids = profile.get("permission_ids", [])
                    all_permission_codes.update(permission_ids)
                
                logger.debug(f"User {user_id} - Permissions from profiles: {len(all_permission_codes)}")
            
            # ===== SOURCE 2: Rôles IAM =====
            user_roles = user.get("roles", [])
            if user_roles:
                iam_roles_cursor = self.iam_roles_collection.find(
                    {"code": {"$in": user_roles}, "is_active": True},
                    {"permissions": 1}
                )
                
                async for iam_role in iam_roles_cursor:
                    role_permissions = iam_role.get("permissions", [])
                    all_permission_codes.update(role_permissions)
                
                logger.debug(f"User {user_id} - Total permissions (profiles + roles): {len(all_permission_codes)}")
            
            # ===== SOURCE 3: Groupes IAM =====
            group_ids = user.get("group_ids", [])
            if group_ids:
                groups_cursor = self.groups_collection.find(
                    {"id": {"$in": group_ids}},
                    {"profile_ids": 1}
                )
                
                async for group in groups_cursor:
                    group_profile_ids = group.get("profile_ids", [])
                    if group_profile_ids:
                        group_profiles_cursor = self.profiles_collection.find(
                            {"id": {"$in": group_profile_ids}},
                            {"permission_ids": 1}
                        )
                        async for profile in group_profiles_cursor:
                            all_permission_codes.update(profile.get("permission_ids", []))
                
                logger.debug(f"User {user_id} - Total permissions (all sources): {len(all_permission_codes)}")
            
            # ===== Résolution des permissions =====
            if not all_permission_codes:
                return []
            
            # Récupérer les détails des permissions depuis iam_permissions
            permissions_details = []
            permissions_cursor = self.iam_permissions_collection.find(
                {"code": {"$in": list(all_permission_codes)}},
                {"_id": 0, "id": 1, "code": 1, "label": 1, "description": 1, "category": 1}
            )
            
            async for perm in permissions_cursor:
                permissions_details.append(perm)
            
            logger.info(f"User {user_id} - Final consolidated permissions: {len(permissions_details)}")
            
            return permissions_details
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}", exc_info=True)
            return []
    
    async def user_has_permission(self, user_id: str, permission_code: str) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique
        
        Supporte les wildcards:
        - "missions.*" matche "missions.browse", "missions.read", etc.
        - "users.manage" matche exactement "users.manage"
        
        Args:
            user_id: ID de l'utilisateur
            permission_code: Code de la permission (ex: "missions.browse")
        
        Returns:
            bool: True si l'utilisateur a la permission
        """
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return False
            
            # Super admin a toutes les permissions
            if "super_admin" in user.get("roles", []):
                return True
            
            all_permissions = await self.get_user_all_permissions(user_id)
            all_permission_codes = {p.get("code") for p in all_permissions}
            
            # Correspondance exacte
            if permission_code in all_permission_codes:
                return True
            
            # Correspondance wildcard (ex: missions.* matche missions.browse)
            permission_parts = permission_code.split('.')
            for i in range(len(permission_parts)):
                wildcard = '.'.join(permission_parts[:i+1]) + '.*'
                if wildcard in all_permission_codes:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}", exc_info=True)
            return False
    
    async def get_user_roles_details(self, user_id: str) -> dict:
        """
        Récupère les détails complets des rôles d'un utilisateur
        
        Returns:
            dict: {
                "legacy_roles": [...],  # Rôles du champ 'roles'
                "iam_roles": [...],     # Détails depuis iam_roles
                "profiles": [...],      # Détails depuis profiles
                "groups": [...]         # Détails depuis groups
            }
        """
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return {}
            
            result = {
                "legacy_roles": user.get("roles", []),
                "iam_roles": [],
                "profiles": [],
                "groups": []
            }
            
            # IAM Roles
            if user.get("roles"):
                iam_roles_cursor = self.iam_roles_collection.find(
                    {"code": {"$in": user["roles"]}},
                    {"_id": 0}
                )
                result["iam_roles"] = await iam_roles_cursor.to_list(length=None)
            
            # Profiles
            if user.get("profile_ids"):
                profiles_cursor = self.profiles_collection.find(
                    {"id": {"$in": user["profile_ids"]}},
                    {"_id": 0}
                )
                result["profiles"] = await profiles_cursor.to_list(length=None)
            
            # Groups
            if user.get("group_ids"):
                groups_cursor = self.groups_collection.find(
                    {"id": {"$in": user["group_ids"]}},
                    {"_id": 0}
                )
                result["groups"] = await groups_cursor.to_list(length=None)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user roles details: {e}", exc_info=True)
            return {}
    
    async def sync_user_legacy_roles_to_iam(self, user_id: str) -> bool:
        """
        Synchronise les rôles legacy d'un utilisateur avec le système IAM
        Utile pour la migration progressive
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            bool: True si synchronisation réussie
        """
        try:
            user = await self.users_collection.find_one({"id": user_id})
            if not user:
                return False
            
            legacy_roles = user.get("roles", [])
            if not legacy_roles:
                return True
            
            # Vérifier quels rôles IAM existent
            existing_iam_roles = await self.iam_roles_collection.find(
                {"code": {"$in": legacy_roles}},
                {"code": 1}
            ).to_list(length=None)
            
            existing_codes = {r["code"] for r in existing_iam_roles}
            
            logger.info(f"User {user_id} - Legacy roles: {legacy_roles}, IAM roles found: {existing_codes}")
            
            return len(existing_codes) == len(legacy_roles)
            
        except Exception as e:
            logger.error(f"Error syncing legacy roles: {e}", exc_info=True)
            return False
