"""
RBAC Manager - Core logic for role and permission management
"""
from typing import List, Optional, Set
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.models import User
from ..core.exceptions import AuthorizationError
from .models import Role, Permission, UserRole, DEFAULT_ROLES, DEFAULT_PERMISSIONS
import logging

logger = logging.getLogger(__name__)


class RBACManager:
    """Manages roles, permissions, and authorization checks"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.roles_collection = db.roles
        self.permissions_collection = db.permissions
        self.user_roles_collection = db.user_roles
    
    async def initialize_default_roles(self):
        """Initialize default system roles and permissions"""
        # NOTE: Les permissions sont maintenant gérées par le système IAM moderne
        # et sont créées via le script de réinitialisation (reset_local_db_with_superadmin.py)
        # Nous n'insérons plus les DEFAULT_PERMISSIONS ici pour éviter les conflits
        
        logger.info("Skipping DEFAULT_PERMISSIONS insertion (managed by IAM system)")
        
        # Create default roles (conservé pour compatibilité RBAC legacy)
        for role in DEFAULT_ROLES:
            existing = await self.roles_collection.find_one({"name": role.name})
            if not existing:
                await self.roles_collection.insert_one(role.model_dump())
                logger.info(f"Created role: {role.name}")
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user (including inherited)"""
        user_role_docs = await self.user_roles_collection.find({"user_id": user_id}).to_list(length=None)
        user_roles = [UserRole(**doc) for doc in user_role_docs if not UserRole(**doc).is_expired]
        
        # Get role objects
        role_names = [ur.role_name for ur in user_roles]
        role_docs = await self.roles_collection.find({"name": {"$in": role_names}}).to_list(length=None)
        roles = [Role(**doc) for doc in role_docs]
        
        # Include inherited roles (use dict to avoid duplicates by name)
        all_roles_dict = {role.name: role for role in roles}
        for role in roles:
            inherited = await self._get_inherited_roles(role)
            for inherited_role in inherited:
                all_roles_dict[inherited_role.name] = inherited_role
        
        return list(all_roles_dict.values())
    
    async def _get_inherited_roles(self, role: Role) -> List[Role]:
        """Recursively get all inherited roles"""
        inherited = []
        
        if not role.inherits_from:
            return inherited
        
        parent_docs = await self.roles_collection.find({"name": {"$in": role.inherits_from}}).to_list(length=None)
        for parent_doc in parent_docs:
            parent_role = Role(**parent_doc)
            inherited.append(parent_role)
            # Recursive inheritance
            inherited.extend(await self._get_inherited_roles(parent_role))
        
        return inherited
    
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user (from all roles)"""
        roles = await self.get_user_roles(user_id)
        permissions = set()
        
        for role in roles:
            permissions.update(role.permissions)
        
        return permissions
    
    def _matches_permission(self, required: str, available: Set[str]) -> bool:
        """Check if a required permission matches available permissions
        
        Supports wildcards:
        - *:* matches everything
        - users:* matches users:read, users:write, etc.
        - *:read matches users:read, content:read, etc.
        """
        # Direct match
        if required in available:
            return True
        
        # Wildcard match
        if "*:*" in available:
            return True
        
        resource, action = required.split(":")
        
        # Resource wildcard (e.g., users:*)
        if f"{resource}:*" in available:
            return True
        
        # Action wildcard (e.g., *:read)
        if f"*:{action}" in available:
            return True
        
        return False
    
    async def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        user_permissions = await self.get_user_permissions(user_id)
        return self._matches_permission(permission, user_permissions)
    
    async def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has a specific role"""
        roles = await self.get_user_roles(user_id)
        return any(role.name == role_name for role in roles)
    
    async def has_any_role(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        roles = await self.get_user_roles(user_id)
        user_role_names = {role.name for role in roles}
        return bool(user_role_names.intersection(set(role_names)))
    
    async def grant_role(self, user_id: str, role_name: str, granted_by: Optional[str] = None):
        """Grant a role to a user"""
        # Check if role exists
        role_doc = await self.roles_collection.find_one({"name": role_name})
        if not role_doc:
            raise ValueError(f"Role '{role_name}' does not exist")
        
        # Check if user already has this role
        existing = await self.user_roles_collection.find_one({
            "user_id": user_id,
            "role_name": role_name
        })
        
        if existing:
            logger.info(f"User {user_id} already has role {role_name}")
            return
        
        # Grant role
        user_role = UserRole(
            user_id=user_id,
            role_name=role_name,
            granted_by=granted_by
        )
        await self.user_roles_collection.insert_one(user_role.model_dump())
        logger.info(f"Granted role {role_name} to user {user_id}")
    
    async def revoke_role(self, user_id: str, role_name: str):
        """Revoke a role from a user"""
        result = await self.user_roles_collection.delete_one({
            "user_id": user_id,
            "role_name": role_name
        })
        
        if result.deleted_count > 0:
            logger.info(f"Revoked role {role_name} from user {user_id}")
        else:
            logger.warning(f"Role {role_name} not found for user {user_id}")
    
    async def check_authorization(
        self,
        user: User,
        required_permissions: Optional[List[str]] = None,
        required_roles: Optional[List[str]] = None,
        require_all_permissions: bool = True
    ):
        """Check if user is authorized
        
        Args:
            user: The user to check
            required_permissions: List of required permissions
            required_roles: List of required roles
            require_all_permissions: If True, user must have ALL permissions. If False, any permission is enough.
        
        Raises:
            AuthorizationError: If user doesn't have required permissions/roles
        """
        # Check roles
        if required_roles:
            user_has_role = await self.has_any_role(user.id, required_roles)
            if not user_has_role:
                raise AuthorizationError(
                    f"User requires one of these roles: {', '.join(required_roles)}",
                    details={"required_roles": required_roles, "user_roles": user.roles}
                )
        
        # Check permissions
        if required_permissions:
            if require_all_permissions:
                # User must have ALL permissions
                for permission in required_permissions:
                    if not await self.has_permission(user.id, permission):
                        raise AuthorizationError(
                            f"User lacks required permission: {permission}",
                            details={"required_permission": permission}
                        )
            else:
                # User must have AT LEAST ONE permission
                has_any = False
                for permission in required_permissions:
                    if await self.has_permission(user.id, permission):
                        has_any = True
                        break
                
                if not has_any:
                    raise AuthorizationError(
                        f"User requires at least one of these permissions: {', '.join(required_permissions)}",
                        details={"required_permissions": required_permissions}
                    )
