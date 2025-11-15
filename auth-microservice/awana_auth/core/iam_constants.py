"""
IAM Constants
Centralized constants for roles, groups, and permissions
"""

# ============================================
# GROUPS
# ============================================
class IAMGroups:
    """IAM Group codes"""
    CANDIDAT = "grp.candidat"
    INTERIMAIRE = "grp.interimaire"
    COMPANY = "grp.company"
    COLLABORATEUR = "grp.collaborateur"
    ADMIN = "grp.admin"
    SUPER_ADMIN = "grp.super_admin"


# ============================================
# PROFILES / ROLES
# ============================================
class IAMProfiles:
    """IAM Profile codes"""
    CANDIDAT = "role.candidat"
    INTERIM_USER = "role.interim_user"
    COMPANY_ADMIN = "role.company_admin"
    COLLABORATEUR = "role.collaborateur"
    ADMIN = "role.admin"
    SUPER_ADMIN = "role.super_admin"


# ============================================
# PERMISSIONS
# ============================================
class IAMPermissions:
    """IAM Permission codes"""
    
    # Missions
    MISSIONS_BROWSE = "missions.browse"
    MISSIONS_READ = "missions.read"
    MISSIONS_CREATE = "missions.create"
    MISSIONS_UPDATE = "missions.update"
    MISSIONS_DELETE = "missions.delete"
    MISSIONS_MANAGE = "missions.manage"
    
    # Applications
    APPLICATIONS_CREATE_OWN = "applications.create_own"
    APPLICATIONS_READ_OWN = "applications.read_own"
    APPLICATIONS_UPDATE_OWN = "applications.update_own"
    APPLICATIONS_READ = "applications.read"
    APPLICATIONS_MANAGE = "applications.manage"
    
    # Profile
    PROFILE_MANAGE_OWN = "profile.manage_own"
    PROFILE_READ = "profile.read"
    PROFILE_MANAGE = "profile.manage"
    
    # Auth & Security
    AUTH_MFA_MANAGE = "auth.mfa.manage"
    SECURITY_EMAIL_DOMAINS_READ = "security.email_domains.read"
    SECURITY_EMAIL_DOMAINS_MANAGE = "security.email_domains.manage"
    
    # Admin
    ADMIN_DASHBOARD = "admin.dashboard"
    USERS_READ = "users.read"
    USERS_MANAGE = "users.manage"
    
    # Email Settings
    EMAIL_SETTINGS_READ = "email.settings.read"
    EMAIL_SETTINGS_MANAGE = "email.settings.manage"
    
    # IAM
    IAM_PROFILES_READ = "iam.profiles.read"
    IAM_PROFILES_MANAGE = "iam.profiles.manage"
    IAM_GROUPS_READ = "iam.groups.read"
    IAM_GROUPS_MANAGE = "iam.groups.manage"
    IAM_PERMISSIONS_READ = "iam.permissions.read"
    
    # Besoins (Hiring Needs)
    BESOINS_CREATE = "besoins.create"
    BESOINS_READ = "besoins.read"
    BESOINS_EDIT = "besoins.edit"
    BESOINS_DELETE = "besoins.delete"
    BESOINS_SUBMIT = "besoins.submit"
    BESOINS_VALIDATE = "besoins.validate"
    BESOINS_CONVERT_TO_MISSION = "besoins.convert_to_mission"
    BESOINS_COMMENT = "besoins.comment"
    
    # Entreprises (Company Management)
    ENTREPRISES_CREATE = "entreprises.create"
    ENTREPRISES_READ = "entreprises.read"
    ENTREPRISES_EDIT = "entreprises.edit"
    ENTREPRISES_DELETE = "entreprises.delete"
    
    # Forms & Configuration
    FORMS_MANAGE = "forms.manage"
    CONFIG_READ = "config.read"
    CONFIG_MANAGE = "config.manage"
    
    # Documents (Phase 2)
    DOCUMENTS_READ_OWN = "documents.read_own"
    DOCUMENTS_UPLOAD_OWN = "documents.upload_own"
    DOCUMENTS_DELETE_OWN = "documents.delete_own"
    DOCUMENTS_READ_ALL = "documents.read_all"
    DOCUMENTS_VERIFY = "documents.verify"
    DOCUMENTS_CONFIGURE = "documents.configure"
    
    # Notifications (Phase 2)
    NOTIFICATIONS_READ_OWN = "notifications.read_own"
    NOTIFICATIONS_MANAGE_OWN = "notifications.manage_own"
    NOTIFICATIONS_SEND = "notifications.send"
    
    # Dashboard (Phase 2)
    DASHBOARD_VIEW_OWN = "dashboard.view_own"
    DASHBOARD_CUSTOMIZE = "dashboard.customize"
    
    # Chat/Messages (Phase 3)
    MESSAGES_READ_OWN = "messages.read_own"
    MESSAGES_SEND_OWN = "messages.send_own"
    MESSAGES_READ_ALL = "messages.read_all"
    MESSAGES_MANAGE = "messages.manage"
    
    # Matching AI (Phase 3)
    MATCHING_VIEW_RECOMMENDATIONS = "matching.view_recommendations"
    MATCHING_CONFIGURE = "matching.configure"


# ============================================
# VALIDATION TYPES
# ============================================
class ValidationTypes:
    """Validation types for user registration"""
    CANDIDAT = "candidat"
    INTERIM = "interim"
    COMPANY = "company"
    COLLABORATEUR = "collaborateur"


# ============================================
# USER ROLES (Legacy - for backward compatibility)
# ============================================
class UserRoles:
    """Legacy user roles - being replaced by IAM"""
    CANDIDAT = "candidat"
    INTERIM = "interim"
    COMPANY = "company"
    COLLABORATEUR = "collaborateur"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# ============================================
# HELPER FUNCTIONS
# ============================================
def get_group_for_role(role: str) -> str:
    """Map a role to its corresponding group"""
    role_to_group = {
        UserRoles.CANDIDAT: IAMGroups.CANDIDAT,
        UserRoles.INTERIM: IAMGroups.INTERIMAIRE,
        UserRoles.COMPANY: IAMGroups.COMPANY,
        UserRoles.COLLABORATEUR: IAMGroups.COLLABORATEUR,
        UserRoles.ADMIN: IAMGroups.ADMIN,
        UserRoles.SUPER_ADMIN: IAMGroups.SUPER_ADMIN,
    }
    return role_to_group.get(role, IAMGroups.CANDIDAT)


def get_profile_for_role(role: str) -> str:
    """Map a role to its corresponding profile"""
    role_to_profile = {
        UserRoles.CANDIDAT: IAMProfiles.CANDIDAT,
        UserRoles.INTERIM: IAMProfiles.INTERIM_USER,
        UserRoles.COMPANY: IAMProfiles.COMPANY_ADMIN,
        UserRoles.COLLABORATEUR: IAMProfiles.COLLABORATEUR,
        UserRoles.ADMIN: IAMProfiles.ADMIN,
        UserRoles.SUPER_ADMIN: IAMProfiles.SUPER_ADMIN,
    }
    return role_to_profile.get(role, IAMProfiles.CANDIDAT)


def get_validation_type_for_role(role: str) -> str:
    """Map a role to its validation type"""
    return role  # Same mapping for now
