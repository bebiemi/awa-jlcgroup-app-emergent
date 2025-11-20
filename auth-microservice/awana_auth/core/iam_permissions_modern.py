"""
IAM Permissions - Format Moderne
Pattern: resource.action.scope où scope = own|all|published

Ce fichier contient les permissions au format moderne.
Les anciennes constantes dans iam_constants.py sont conservées pour compatibilité.
"""

class IAMPermissionsModern:
    """Permissions IAM au format moderne (resource.action.scope)"""
    
    # ============================================
    # MISSIONS
    # ============================================
    MISSIONS_BROWSE = "missions.browse"  # Navigation générale (pas de scope)
    MISSIONS_READ_ALL = "missions.read.all"
    MISSIONS_READ_OWN = "missions.read.own"
    MISSIONS_CREATE_ALL = "missions.create.all"
    MISSIONS_CREATE_OWN = "missions.create.own"
    MISSIONS_EDIT_ALL = "missions.edit.all"
    MISSIONS_EDIT_OWN = "missions.edit.own"
    MISSIONS_DELETE_ALL = "missions.delete.all"
    MISSIONS_DELETE_OWN = "missions.delete.own"
    MISSIONS_MANAGE_ALL = "missions.manage.all"
    
    # Permissions génériques (pour compatibilité backend)
    MISSIONS_READ = "missions.read"
    MISSIONS_CREATE = "missions.create"
    MISSIONS_UPDATE = "missions.update"
    MISSIONS_DELETE = "missions.delete"
    MISSIONS_MANAGE = "missions.manage"
    
    # ============================================
    # BESOINS
    # ============================================
    BESOINS_VIEW_ALL = "besoins.view.all"
    BESOINS_VIEW_OWN = "besoins.view.own"
    BESOINS_CREATE_ALL = "besoins.create.all"
    BESOINS_CREATE_OWN = "besoins.create.own"
    BESOINS_EDIT_ALL = "besoins.edit.all"
    BESOINS_EDIT_OWN = "besoins.edit.own"
    BESOINS_DELETE_ALL = "besoins.delete.all"
    BESOINS_DELETE_OWN = "besoins.delete.own"
    
    # Permissions génériques (pour compatibilité backend)
    BESOINS_READ = "besoins.read"
    BESOINS_CREATE = "besoins.create"
    BESOINS_EDIT = "besoins.edit"
    BESOINS_DELETE = "besoins.delete"
    BESOINS_SUBMIT = "besoins.submit"
    BESOINS_VALIDATE = "besoins.validate"
    BESOINS_CONVERT_TO_MISSION = "besoins.convert_to_mission"
    BESOINS_COMMENT = "besoins.comment"
    
    # ============================================
    # APPLICATIONS
    # ============================================
    APPLICATIONS_READ_ALL = "applications.read.all"
    APPLICATIONS_READ_OWN = "applications.read.own"
    APPLICATIONS_CREATE_ALL = "applications.create.all"
    APPLICATIONS_CREATE_OWN = "applications.create.own"
    APPLICATIONS_UPDATE_ALL = "applications.update.all"
    APPLICATIONS_UPDATE_OWN = "applications.update.own"
    APPLICATIONS_DELETE_ALL = "applications.delete.all"
    APPLICATIONS_DELETE_OWN = "applications.delete.own"
    APPLICATIONS_MANAGE_ALL = "applications.manage.all"
    
    # Permissions génériques
    APPLICATIONS_READ = "applications.read"
    APPLICATIONS_CREATE = "applications.create"
    APPLICATIONS_MANAGE = "applications.manage"
    
    # ============================================
    # PROFILE
    # ============================================
    PROFILE_VIEW_ALL = "profile.view.all"
    PROFILE_VIEW_OWN = "profile.view.own"
    PROFILE_EDIT_ALL = "profile.edit.all"
    PROFILE_EDIT_OWN = "profile.edit.own"
    PROFILE_MANAGE_ALL = "profile.manage.all"
    PROFILE_MANAGE_OWN = "profile.manage.own"
    
    # Permissions génériques
    PROFILE_READ = "profile.read"
    PROFILE_MANAGE = "profile.manage"
    
    # ============================================
    # ENTREPRISES
    # ============================================
    ENTREPRISES_VIEW_ALL = "entreprises.view.all"
    ENTREPRISES_VIEW_OWN = "entreprises.view.own"
    ENTREPRISES_EDIT_ALL = "entreprises.edit.all"
    ENTREPRISES_EDIT_OWN = "entreprises.edit.own"
    
    # Permissions génériques
    ENTREPRISES_READ = "entreprises.read"
    ENTREPRISES_CREATE = "entreprises.create"
    ENTREPRISES_EDIT = "entreprises.edit"
    ENTREPRISES_DELETE = "entreprises.delete"
    ENTREPRISES_VALIDATE = "entreprises.validate"
    ENTREPRISES_LINK_EXISTING = "entreprises.link_existing"
    ENTREPRISES_GROUP_REQUEST = "entreprises.group_request"
    ENTREPRISES_GROUP_APPROVE = "entreprises.group_approve"
    ENTREPRISES_INVITE_USER = "entreprises.invite_user"
    ENTREPRISES_MANAGE = "entreprises.manage"
    
    # ============================================
    # DOCUMENTS
    # ============================================
    DOCUMENTS_READ_ALL = "documents.read.all"
    DOCUMENTS_READ_OWN = "documents.read.own"
    DOCUMENTS_CREATE_ALL = "documents.create.all"
    DOCUMENTS_CREATE_OWN = "documents.create.own"
    DOCUMENTS_UPDATE_ALL = "documents.update.all"
    DOCUMENTS_UPDATE_OWN = "documents.update.own"
    DOCUMENTS_DELETE_ALL = "documents.delete.all"
    DOCUMENTS_DELETE_OWN = "documents.delete.own"
    
    # Permissions génériques
    DOCUMENTS_READ = "documents.read"
    DOCUMENTS_CREATE = "documents.create"
    DOCUMENTS_UPDATE = "documents.update"
    DOCUMENTS_DELETE = "documents.delete"
    DOCUMENTS_DOWNLOAD = "documents.download"
    DOCUMENTS_VERIFY = "documents.verify"
    
    # ============================================
    # USERS (Admin)
    # ============================================
    USERS_READ = "users.read"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"
    USERS_EDIT = "users.edit"
    USERS_DELETE = "users.delete"
    USERS_MANAGE = "users.manage"
    USERS_MANAGE_STATUS = "users.manage_status"
    USERS_PASSWORD_UPDATE = "users.password.update"
    USERS_RESET_MFA = "users.reset_mfa"
    
    # ============================================
    # CONFIG & FORMS
    # ============================================
    CONFIG_READ = "config.read"
    CONFIG_MANAGE = "config.manage"
    FORMS_READ = "forms.read"
    FORMS_MANAGE = "forms.manage"
    FORMS_ENTERPRISE_MANAGE = "forms.enterprise.manage"
    FORMS_ENTERPRISE_UPDATE = "forms.enterprise.update"
    
    # ============================================
    # ADMIN & SYSTEM
    # ============================================
    ADMIN_DASHBOARD = "admin.dashboard"
    ADMIN_ACCESS = "admin.access"
    ADMIN_SETTINGS = "admin.settings"
    
    # ============================================
    # IAM
    # ============================================
    IAM_PROFILES_READ = "iam.profiles.read"
    IAM_PROFILES_MANAGE = "iam.profiles.manage"
    IAM_PROFILES_CREATE = "iam.profiles.create"
    IAM_PROFILES_UPDATE = "iam.profiles.update"
    IAM_PROFILES_DELETE = "iam.profiles.delete"
    IAM_GROUPS_READ = "iam.groups.read"
    IAM_GROUPS_MANAGE = "iam.groups.manage"
    IAM_GROUPS_CREATE = "iam.groups.create"
    IAM_GROUPS_UPDATE = "iam.groups.update"
    IAM_GROUPS_DELETE = "iam.groups.delete"
    IAM_PERMISSIONS_READ = "iam.permissions.read"
    IAM_PERMISSIONS_CREATE = "iam.permissions.create"
    IAM_PERMISSIONS_UPDATE = "iam.permissions.update"
    IAM_PERMISSIONS_DELETE = "iam.permissions.delete"
    IAM_USERS_ASSIGN = "iam.users.assign"
    IAM_MANAGE = "iam:manage"
    
    # ============================================
    # RBAC
    # ============================================
    RBAC_READ_ROLES = "rbac.read_roles"
    RBAC_READ_GROUPS = "rbac.read_groups"
    RBAC_READ_PROFILES = "rbac.read_profiles"
    RBAC_MANAGE_PROFILE_ROLES = "rbac.manage_profile_roles"
    RBAC_MANAGE_GROUP_ROLES = "rbac.manage_group_roles"
    RBAC_ASSIGN_PROFILES = "rbac.assign_profiles"
    RBAC_ASSIGN_GROUPS = "rbac.assign_groups"
    
    # ============================================
    # VALIDATIONS
    # ============================================
    VALIDATIONS_MANAGE = "validations.manage"
    
    # ============================================
    # LOCATIONS
    # ============================================
    LOCATIONS_MANAGE = "locations.manage"
    
    # ============================================
    # REFERENCES
    # ============================================
    REFERENCES_MANAGE = "references.manage"
    
    # ============================================
    # RULES
    # ============================================
    RULES_MANAGE = "rules.manage"
    
    # ============================================
    # FLAGS
    # ============================================
    FLAGS_MANAGE = "flags.manage"
    
    # ============================================
    # EMAILS
    # ============================================
    EMAILS_CONFIGURE = "emails.configure"
    EMAILS_READ_CONFIG = "emails.read_config"
    EMAILS_READ_HISTORY = "emails.read_history"
    EMAILS_MANAGE_TEMPLATES = "emails.manage_templates"
    EMAILS_TEST = "emails.test"
    EMAIL_SETTINGS_READ = "email.settings.read"
    EMAIL_SETTINGS_MANAGE = "email.settings.manage"
    
    # ============================================
    # SECURITY
    # ============================================
    SECURITY_EMAIL_DOMAINS_READ = "security.email_domains.read"
    SECURITY_EMAIL_DOMAINS_MANAGE = "security.email_domains.manage"
    AUTH_MFA_MANAGE = "auth.mfa.manage"
    
    # ============================================
    # DASHBOARD
    # ============================================
    DASHBOARD_ACCESS = "dashboard.access"
    DASHBOARD_CUSTOMIZE_OWN = "dashboard.customize.own"


# Alias pour compatibilité avec ancien code
IAMPerms = IAMPermissionsModern
