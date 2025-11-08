#!/usr/bin/env python3
"""
Script to migrate role checks to IAM permission checks in mission_routes.py
"""

# Mapping de vérifications de rôles vers permissions IAM
ROLE_TO_PERMISSION_MAPPING = {
    # Create mission
    "[cfg.get_admin_role(), cfg.get_super_admin_role(), cfg.get_company_role(), cfg.get_commercial_role()]": 
        '["missions.create", "missions.manage"]',
    
    # View missions (read)
    "cfg.get_admin_role() in user_roles or cfg.get_super_admin_role() in user_roles":
        '"missions.manage"',
    
    # Publish mission
    "cfg.get_admin_role() in user_roles or cfg.get_super_admin_role() in user_roles or cfg.get_commercial_role() in user_roles":
        '["missions.publish", "missions.manage"]',
    
    # Update/Delete mission
    "cfg.get_admin_role() in user_roles or cfg.get_super_admin_role() in user_roles or cfg.get_commercial_role() in user_roles":
        '["missions.edit", "missions.manage"]',
}

# Template pour le check IAM
IAM_CHECK_TEMPLATE = """    # IAM Permission Check
    checker = PermissionChecker(db)
    has_permission = await checker.user_has_any_permission(
        current_user.get("id"),
        {permissions}
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="{error_message}"
        )"""

print("Migration script ready. Apply replacements manually in mission_routes.py")
print("\nKey permission mappings:")
print("- missions.create - Créer des missions")
print("- missions.read - Lire les missions")
print("- missions.edit - Modifier les missions")
print("- missions.delete - Supprimer les missions")
print("- missions.publish - Publier les missions")
print("- missions.manage - Gestion complète")
print("- applications.read - Voir les candidatures")
print("- applications.manage - Gérer les candidatures")
print("- applications.create - Postuler")
