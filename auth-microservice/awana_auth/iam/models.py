"""
IAM Models - Nouvelle Architecture
Refonte complète pour scalabilité et gouvernance
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class PermissionScope(str, Enum):
    """Scopes de permissions"""
    OWN = "own"           # Ressources propres à l'utilisateur
    ALL = "all"           # Toutes les ressources
    PUBLISHED = "published"  # Ressources publiques
    ORGANIZATION = "organization"  # Scope organisation
    SYSTEM = "system"     # Scope système


class PermissionCategory(str, Enum):
    """Catégories de permissions"""
    MISSIONS = "missions"
    APPLICATIONS = "applications"
    DOCUMENTS = "documents"
    PROFILE = "profile"
    SECURITY = "security"
    ADMIN = "admin"
    BESOINS = "besoins"
    ENTREPRISES = "entreprises"
    DASHBOARD = "dashboard"
    EMARGEMENTS = "emargements"
    PAYROLL = "payroll"
    RECRUITMENT = "recruitment"
    SYSTEM = "system"
    IAM = "iam"
    CONFIG = "configuration"
    LEGACY = "legacy"


class PermissionAction(str, Enum):
    """Actions de permissions"""
    VIEW = "view"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    MANAGE = "manage"
    APPROVE = "approve"
    REJECT = "reject"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    ASSIGN = "assign"
    VALIDATE = "validate"
    SUBMIT = "submit"
    COMMENT = "comment"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SEARCH = "search"
    BROWSE = "browse"
    APPLY = "apply"
    TRACK = "track"
    ADJUST = "adjust"
    CALCULATE = "calculate"
    TRIGGER = "trigger"
    PARTICIPATE = "participate"


class ProfileCategory(str, Enum):
    """Catégories de profils"""
    SYSTEM = "system"      # Profils système (restreint, etc.)
    BUSINESS = "business"  # Profils métier (candidat, entreprise, etc.)
    ADMIN = "admin"        # Profils admin (admin, super_admin)
    TECHNICAL = "technical"  # Profils techniques (auditeur, etc.)


class Permission(BaseModel):
    """
    Permission atomique - Format: resource.action.scope
    Ex: missions.view.published
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Format: resource.action.scope
    name: str  # Nom lisible
    description: str  # Description obligatoire
    
    resource: str  # Ex: "missions", "documents"
    action: PermissionAction  # Ex: "view", "create"
    scope: PermissionScope = PermissionScope.OWN  # Ex: "own", "all"
    
    category: PermissionCategory  # Pour regroupement
    tags: List[str] = Field(default_factory=list)  # Tags pour recherche
    
    is_system: bool = False  # Permission système non modifiable
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class CapabilityBundle(BaseModel):
    """
    Bundle de capacités réutilisable
    Regroupe plusieurs permissions liées à une fonctionnalité
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Ex: "missions_manage_own"
    name: str  # Ex: "Gestion Missions (Own)"
    description: str  # Description obligatoire
    
    category: PermissionCategory  # Catégorie principale
    permission_ids: List[str] = Field(default_factory=list)  # Permissions incluses
    
    tags: List[str] = Field(default_factory=list)  # Pour recherche
    is_system: bool = False  # Bundle système non modifiable
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class ProfileMetadata(BaseModel):
    """Métadonnées de profil pour UI"""
    priority: int = 0  # Ordre d'affichage
    icon: Optional[str] = None  # Icône pour UI
    color: Optional[str] = None  # Couleur pour UI
    badge: Optional[str] = None  # Badge (ex: "BETA", "NEW")


class Profile(BaseModel):
    """
    Profil métier visible dans l'UI
    Compose des bundles de capacités et/ou permissions directes
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Ex: "candidat_confirmed", "profile.company"
    name: str  # Ex: "Candidat Confirmé", "Entreprise"
    description: str  # Description obligatoire
    
    category: ProfileCategory  # system|business|admin|technical
    
    # Permissions
    capability_bundle_ids: List[str] = Field(default_factory=list)  # Bundles utilisés
    permission_ids: List[str] = Field(default_factory=list)  # Permissions directes (legacy)
    
    # Hiérarchie
    parent_profile_id: Optional[str] = None  # Profil parent (héritage)
    
    # Visibilité et système
    is_visible: bool = True  # Visible dans l'UI
    is_system: bool = False  # Profil système non modifiable
    is_protected: bool = False  # Ne peut pas être supprimé
    
    # Métadonnées
    metadata: ProfileMetadata = Field(default_factory=ProfileMetadata)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class TemporaryProfile(BaseModel):
    """
    Profil temporaire avec expiration
    Ex: Candidat 15j
    """
    profile_id: str
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime  # Date d'expiration
    reason: Optional[str] = None  # Raison de l'assignation temporaire
    notified_at: Optional[datetime] = None  # Date de dernière notification
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si le profil est expiré"""
        now = datetime.now(timezone.utc)
        # Gérer les datetime avec et sans timezone
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now > expires
    
    @property
    def days_until_expiration(self) -> int:
        """Nombre de jours avant expiration"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.now(timezone.utc)
        return delta.days
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProfileHistoryEntry(BaseModel):
    """
    Entrée d'historique de profil
    Pour audit et traçabilité
    """
    profile_id: str
    action: str  # "assigned", "removed", "expired", "upgraded", "downgraded"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = None
    performed_by: Optional[str] = None  # User ID qui a effectué l'action
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserIAMData(BaseModel):
    """
    Données IAM d'un utilisateur (complément au modèle User)
    """
    user_id: str
    
    # Profils assignés
    profile_ids: List[str] = Field(default_factory=list)
    
    # Profils temporaires
    temporary_profiles: List[TemporaryProfile] = Field(default_factory=list)
    
    # Date de première connexion (pour calcul expiration)
    first_login_at: Optional[datetime] = None
    
    # Historique des changements de profils
    profile_history: List[ProfileHistoryEntry] = Field(default_factory=list)
    
    # Métadonnées
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProfileHierarchy(BaseModel):
    """
    Hiérarchie de profil avec permissions résolues
    """
    profile: Profile
    parent_profiles: List[Profile] = Field(default_factory=list)
    bundles: List[CapabilityBundle] = Field(default_factory=list)
    effective_permissions: List[Permission] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExpirationCheck(BaseModel):
    """
    Résultat de vérification d'expiration
    """
    user_id: str
    username: str
    email: str
    expired_profiles: List[TemporaryProfile] = Field(default_factory=list)
    expiring_soon: List[TemporaryProfile] = Field(default_factory=list)  # < 3 jours
    downgrade_to_profile_id: str  # Profil de repli (généralement "restricted")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# Profils Système Prédéfinis (Codes)
# ============================================================================

class SystemProfiles:
    """Codes des profils système"""
    RESTRICTED = "profile.restricted"
    CANDIDAT_TEMP = "profile.candidat_temp"
    CANDIDAT_CONFIRMED = "profile.candidat_confirmed"
    COMPANY = "profile.company"
    COMMERCIAL = "profile.commercial"
    PAYROLL = "profile.payroll"
    HR_MANAGER = "profile.hr_manager"
    ADMIN = "profile.admin"
    SUPER_ADMIN = "profile.super_admin"


# ============================================================================
# Bundles Système Prédéfinis (Codes)
# ============================================================================

class SystemBundles:
    """Codes des bundles système"""
    READONLY_ACCESS = "readonly_access"
    PUBLIC_MISSIONS_VIEW = "public_missions_view"
    PROFILE_SELF_MANAGE = "profile_self_manage"
    DOCUMENTS_SELF_MANAGE = "documents_self_manage"
    MISSIONS_APPLY = "missions_apply"
    APPLICATIONS_TRACK_OWN = "applications_track_own"
    
    COMPANY_MANAGE_OWN = "company_manage_own"
    BESOINS_MANAGE_OWN = "besoins_manage_own"
    EMARGEMENTS_VALIDATE = "emargements_validate"
    
    MISSIONS_MANAGE_OWN = "missions_manage_own"
    MISSIONS_MANAGE_ALL = "missions_manage_all"
    APPLICATIONS_REVIEW = "applications_review"
    BESOINS_MANAGE_ALL = "besoins_manage_all"
    ENTREPRISES_MANAGE_ALL = "entreprises_manage_all"
    COMMERCIAL_TOOLS = "commercial_tools"
    
    MISSIONS_VIEW_ACTIVE = "missions_view_active"
    EMARGEMENTS_MANAGE = "emargements_manage"
    PAYROLL_MANAGE = "payroll_manage"
    INVOICING_MANAGE = "invoicing_manage"
    
    USERS_MANAGE = "users_manage"
    RECRUITMENT_PROCESS = "recruitment_process"
    MEDICAL_COMPLIANCE = "medical_compliance"
    CANDIDAT_PROGRESSION = "candidat_progression"
    HR_REPORTING = "hr_reporting"
