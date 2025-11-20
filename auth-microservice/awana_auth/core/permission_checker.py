"""
Permission Checker - Système flexible de vérification des permissions
Supporte à la fois l'ancien et le nouveau format pendant la migration
"""
from typing import List, Set
from fnmatch import fnmatch


class PermissionChecker:
    """
    Vérifie les permissions avec support du matching flexible
    Permet la transition entre ancien et nouveau format
    """
    
    @staticmethod
    def has_permission(user_permissions: List[str], required_permission: str) -> bool:
        """
        Vérifie si l'utilisateur a la permission requise
        
        Stratégies de matching :
        1. Match exact : user a "besoins.create.own" et required = "besoins.create.own" → ✅
        2. Match générique : user a "besoins.create.own" et required = "besoins.create" → ✅
        3. Match wildcard : user a "besoins.*" et required = "besoins.create.own" → ✅
        4. Match super admin : user a "*.*" → ✅ pour tout
        
        Args:
            user_permissions: Liste des permissions de l'utilisateur
            required_permission: Permission requise
            
        Returns:
            bool: True si l'utilisateur a la permission
        """
        user_perms_set = set(user_permissions)
        
        # 1. Match exact
        if required_permission in user_perms_set:
            return True
        
        # 2. Super admin wildcard
        if '*.*' in user_perms_set:
            return True
        
        # 3. Match générique avec scope
        # Si required = "besoins.create" et user a "besoins.create.own" ou "besoins.create.all"
        if '.' in required_permission:
            parts = required_permission.split('.')
            if len(parts) == 2:  # Format: resource.action (sans scope)
                # Chercher si user a la version avec scope
                for scope in ['own', 'all', 'published']:
                    if f"{required_permission}.{scope}" in user_perms_set:
                        return True
        
        # 4. Match wildcard resource
        # Si required = "besoins.create.own" et user a "besoins.*"
        if '.' in required_permission:
            parts = required_permission.split('.')
            resource = parts[0]
            wildcard_perm = f"{resource}.*"
            if wildcard_perm in user_perms_set:
                return True
        
        # 5. Match pattern fnmatch (pour wildcards complexes)
        for user_perm in user_perms_set:
            if '*' in user_perm:
                if fnmatch(required_permission, user_perm):
                    return True
        
        return False
    
    @staticmethod
    def has_any_permission(user_permissions: List[str], required_permissions: List[str]) -> bool:
        """
        Vérifie si l'utilisateur a AU MOINS UNE des permissions requises (mode ANY)
        
        Args:
            user_permissions: Liste des permissions de l'utilisateur
            required_permissions: Liste des permissions requises (ANY)
            
        Returns:
            bool: True si l'utilisateur a au moins une permission
        """
        for required_perm in required_permissions:
            if PermissionChecker.has_permission(user_permissions, required_perm):
                return True
        return False
    
    @staticmethod
    def has_all_permissions(user_permissions: List[str], required_permissions: List[str]) -> bool:
        """
        Vérifie si l'utilisateur a TOUTES les permissions requises (mode ALL)
        
        Args:
            user_permissions: Liste des permissions de l'utilisateur
            required_permissions: Liste des permissions requises (ALL)
            
        Returns:
            bool: True si l'utilisateur a toutes les permissions
        """
        for required_perm in required_permissions:
            if not PermissionChecker.has_permission(user_permissions, required_perm):
                return False
        return True
    
    @staticmethod
    def filter_by_scope(permissions: List[str], scope: str) -> List[str]:
        """
        Filtre les permissions par scope (own, all, published)
        
        Args:
            permissions: Liste des permissions
            scope: Scope à filtrer (own, all, published)
            
        Returns:
            Liste des permissions avec le scope spécifié
        """
        return [p for p in permissions if p.endswith(f'.{scope}')]
    
    @staticmethod
    def get_resource_permissions(permissions: List[str], resource: str) -> List[str]:
        """
        Récupère toutes les permissions pour une ressource donnée
        
        Args:
            permissions: Liste des permissions
            resource: Nom de la ressource (ex: "besoins", "missions")
            
        Returns:
            Liste des permissions pour cette ressource
        """
        return [p for p in permissions if p.startswith(f"{resource}.")]
