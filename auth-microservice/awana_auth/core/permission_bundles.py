"""
Permission Bundles Configuration
Définition de tous les bundles de permissions du système AWANA

Un bundle est un groupe logique de permissions atomiques.
Au lieu d'assigner 50 permissions, on assigne un bundle.

Usage:
    from awana_auth.core.permission_bundles import BUNDLES, get_bundle_permissions
    
    # Récupérer toutes les permissions d'un bundle
    perms = get_bundle_permissions("missions.manage")
"""

# ============================================================================
# BUNDLES DE PERMISSIONS
# ============================================================================

BUNDLES = {
    
    # ========================================================================
    # 1. AUTHENTIFICATION & UTILISATEURS
    # ========================================================================
    
    "auth.basic": {
        "name": "Authentification de base",
        "description": "Authentification et gestion de profil personnel",
        "permissions": [
            "auth.login",
            "auth.logout",
            "auth.refresh_token",
            "profile.view.own",
            "profile.edit.own"
        ]
    },
    
    "users.read": {
        "name": "Lecture utilisateurs",
        "description": "Consultation de la liste et détails des utilisateurs",
        "permissions": [
            "users.view.all",
            "users.view.own",
            "users.read.all",
            "users.read.own",
            "users.browse"
        ]
    },
    
    "users.manage": {
        "name": "Gestion utilisateurs",
        "description": "Gestion complète des utilisateurs (CRUD)",
        "permissions": [
            "users.view.all",
            "users.create",
            "users.update",
            "users.delete",
            "users.archive",
            "users.restore",
            "users.block",
            "users.unblock",
            "users.password.reset",
            "users.roles.assign"
        ]
    },
    
    "users.hr_access": {
        "name": "Accès RH utilisateurs",
        "description": "Accès RH aux profils et documents utilisateurs",
        "permissions": [
            "users.view.all",
            "users.update",
            "users.profiles.view",
            "users.contracts.view",
            "users.documents.view"
        ]
    },
    
    # ========================================================================
    # 2. MISSIONS & CANDIDATURES
    # ========================================================================
    
    "missions.read": {
        "name": "Consultation missions",
        "description": "Lecture et navigation dans les missions",
        "permissions": [
            "missions.view.all",
            "missions.view.own",
            "missions.read.all",
            "missions.read.own",
            "missions.browse"
        ]
    },
    
    "missions.create": {
        "name": "Création missions",
        "description": "Créer et enregistrer des missions",
        "permissions": [
            "missions.create.own",
            "missions.create.all",
            "missions.draft",
            "missions.save_template"
        ]
    },
    
    "missions.manage": {
        "name": "Gestion missions",
        "description": "Gestion complète du cycle de vie des missions",
        "permissions": [
            "missions.read.all",
            "missions.create.all",
            "missions.edit.all",
            "missions.delete.all",
            "missions.publish",
            "missions.unpublish",
            "missions.archive",
            "missions.cancel",
            "missions.assign",
            "missions.close"
        ]
    },
    
    "applications.submit": {
        "name": "Soumission candidatures",
        "description": "Postuler aux missions disponibles",
        "permissions": [
            "applications.create",
            "applications.submit",
            "applications.withdraw",
            "applications.view.own",
            "documents.upload.cv"
        ]
    },
    
    "applications.review": {
        "name": "Révision candidatures",
        "description": "Consulter et évaluer les candidatures",
        "permissions": [
            "applications.view.all",
            "applications.view.own",
            "applications.read.all",
            "applications.comment",
            "applications.shortlist",
            "applications.rate"
        ]
    },
    
    "applications.manage": {
        "name": "Gestion candidatures",
        "description": "Gestion complète des candidatures (validation, rejet)",
        "permissions": [
            "applications.view.all",
            "applications.read.all",
            "applications.approve",
            "applications.reject",
            "applications.comment",
            "applications.shortlist",
            "applications.archive",
            "applications.export"
        ]
    },
    
    # ========================================================================
    # 3. BESOINS RH
    # ========================================================================
    
    "besoins.create": {
        "name": "Création besoins RH",
        "description": "Créer des besoins en ressources humaines",
        "permissions": [
            "besoins.create.own",
            "besoins.create.all",
            "besoins.draft",
            "besoins.submit.own"
        ]
    },
    
    "besoins.manage": {
        "name": "Gestion besoins RH",
        "description": "Gestion complète des besoins (validation, conversion)",
        "permissions": [
            "besoins.read.all",
            "besoins.create.all",
            "besoins.edit.all",
            "besoins.delete.all",
            "besoins.validate.all",
            "besoins.comment.all",
            "besoins.convert_to_mission"
        ]
    },
    
    # ========================================================================
    # 4. ÉMARGEMENTS & SIGNATURES ⭐
    # ========================================================================
    
    "emargements.submit": {
        "name": "Soumission émargements",
        "description": "Soumettre ses heures travaillées (intérimaire)",
        "permissions": [
            "emargements.create.own",
            "emargements.submit.own",
            "emargements.view.own",
            "emargements.edit.own",
            "emargements.draft.own"
        ]
    },
    
    "emargements.validate_interim": {
        "name": "Validation intérimaire",
        "description": "Signature intérimaire de ses émargements",
        "permissions": [
            "emargements.view.own",
            "emargements.sign.own",
            "emargements.submit.own",
            "emargements.comment.own"
        ]
    },
    
    "emargements.validate_client": {
        "name": "Validation client",
        "description": "Validation et signature par l'entreprise cliente",
        "permissions": [
            "emargements.view.all",
            "emargements.view.own",
            "emargements.sign.all",
            "emargements.approve",
            "emargements.reject",
            "emargements.comment"
        ]
    },
    
    "emargements.consolidate": {
        "name": "Consolidation émargements",
        "description": "Consolidation et export des émargements signés",
        "permissions": [
            "emargements.view.all",
            "emargements.consolidate",
            "emargements.export",
            "emargements.generate_report",
            "emargements.statistics"
        ]
    },
    
    "emargements.manage": {
        "name": "Gestion administrative émargements",
        "description": "Gestion complète des émargements (admin/RH)",
        "permissions": [
            "emargements.view.all",
            "emargements.edit.all",
            "emargements.delete.all",
            "emargements.approve.all",
            "emargements.reject.all",
            "emargements.consolidate",
            "emargements.export",
            "emargements.generate_report",
            "emargements.unlock",
            "emargements.archive"
        ]
    },
    
    "signatures.read": {
        "name": "Lecture signatures",
        "description": "Consultation et vérification des signatures",
        "permissions": [
            "signatures.view.all",
            "signatures.view.own",
            "signatures.verify",
            "signatures.history.view"
        ]
    },
    
    "signatures.manage": {
        "name": "Gestion signatures",
        "description": "Gestion complète des signatures électroniques",
        "permissions": [
            "signatures.view.all",
            "signatures.create",
            "signatures.request",
            "signatures.cancel",
            "signatures.verify",
            "signatures.invalidate",
            "signatures.history.view",
            "signatures.audit"
        ]
    },
    
    "consolidation.read": {
        "name": "Consolidation lecture ⭐",
        "description": "Accès lecture consolidation émargements après signatures (Paie, RH, Commercial)",
        "permissions": [
            "emargements.consolidate.view",
            "emargements.consolidate.export",
            "emargements.reports.view",
            "emargements.statistics.view",
            "signatures.verify",
            "signatures.history.view"
        ]
    },
    
    # ========================================================================
    # 5. ENTREPRISES
    # ========================================================================
    
    "entreprises.view": {
        "name": "Consultation entreprises",
        "description": "Lecture des informations entreprises",
        "permissions": [
            "entreprises.view.all",
            "entreprises.view.own",
            "entreprises.read.all",
            "entreprises.browse"
        ]
    },
    
    "entreprises.manage": {
        "name": "Gestion entreprises",
        "description": "Gestion complète des entreprises clientes",
        "permissions": [
            "entreprises.view.all",
            "entreprises.create",
            "entreprises.edit.all",
            "entreprises.delete",
            "entreprises.archive",
            "entreprises.restore",
            "entreprises.validate"
        ]
    },
    
    "entreprises.own_manage": {
        "name": "Gestion propre entreprise",
        "description": "Gestion de sa propre entreprise (compte entreprise)",
        "permissions": [
            "entreprises.view.own",
            "entreprises.edit.own",
            "entreprises.users.manage",
            "entreprises.settings.edit"
        ]
    },
    
    # ========================================================================
    # 6. DOCUMENTS
    # ========================================================================
    
    "documents.upload": {
        "name": "Upload documents",
        "description": "Télécharger des documents (CV, contrats, etc.)",
        "permissions": [
            "documents.upload.cv",
            "documents.upload.contract",
            "documents.upload.general",
            "documents.view.own",
            "documents.delete.own"
        ]
    },
    
    "documents.manage": {
        "name": "Gestion documents",
        "description": "Gestion complète des documents système",
        "permissions": [
            "documents.view.all",
            "documents.upload.all",
            "documents.edit.all",
            "documents.delete.all",
            "documents.download.all",
            "documents.archive",
            "documents.validate"
        ]
    },
    
    "documents.recruitment_access": {
        "name": "Accès recrutement documents",
        "description": "Accès lecture aux CV et documents candidats (recrutement)",
        "permissions": [
            "documents.view.all",
            "documents.download.all",
            "documents.cv.view",
            "documents.cv.download",
            "documents.motivation_letter.view"
        ]
    },
    
    # ========================================================================
    # 7. RECRUTEMENT ⭐
    # ========================================================================
    
    "recruitment.users_view": {
        "name": "Consultation profils candidats",
        "description": "Voir et rechercher tous les profils candidats/intérimaires",
        "permissions": [
            "users.view.all",
            "users.read.all",
            "users.profiles.view",
            "users.skills.view",
            "users.experience.view",
            "users.availability.view",
            "users.search",
            "users.filter"
        ]
    },
    
    "recruitment.evaluate": {
        "name": "Évaluation candidats",
        "description": "Noter et émettre des avis sur les candidats",
        "permissions": [
            "users.rate",
            "users.rating.view",
            "users.comment.create",
            "users.comment.view",
            "users.feedback.create",
            "users.feedback.view",
            "users.notes.create",
            "users.notes.view",
            "users.notes.edit.own"
        ]
    },
    
    "recruitment.assign": {
        "name": "Attribution missions",
        "description": "Attribuer des candidats aux missions",
        "permissions": [
            "missions.view.all",
            "missions.read.all",
            "missions.assign",
            "missions.users.assign",
            "missions.users.unassign",
            "missions.matching.view",
            "applications.assign_candidate"
        ]
    },
    
    "recruitment.manage": {
        "name": "Gestion recrutement complète",
        "description": "Bundle complet pour le profil Recrutement",
        "permissions": [
            # Utilisateurs
            "users.view.all",
            "users.read.all",
            "users.profiles.view",
            "users.skills.view",
            "users.experience.view",
            "users.availability.view",
            "users.search",
            "users.filter",
            # Évaluation
            "users.rate",
            "users.rating.view",
            "users.comment.create",
            "users.comment.view",
            "users.feedback.create",
            "users.feedback.view",
            "users.notes.create",
            "users.notes.view",
            "users.notes.edit.own",
            # Missions & Attribution
            "missions.view.all",
            "missions.read.all",
            "missions.assign",
            "missions.users.assign",
            "missions.users.unassign",
            "missions.matching.view",
            "applications.assign_candidate",
            # Documents
            "documents.cv.view",
            "documents.cv.download",
            "documents.motivation_letter.view",
            # Applications
            "applications.view.all",
            "applications.read.all",
            "applications.comment"
        ]
    },
    
    # ========================================================================
    # 8. COMMUNICATION
    # ========================================================================
    
    "notifications.user": {
        "name": "Notifications utilisateur",
        "description": "Gestion des notifications personnelles",
        "permissions": [
            "notifications.view.own",
            "notifications.read.own",
            "notifications.mark_read",
            "notifications.delete.own"
        ]
    },
    
    "notifications.send": {
        "name": "Envoi notifications",
        "description": "Créer et envoyer des notifications",
        "permissions": [
            "notifications.create",
            "notifications.send",
            "notifications.broadcast",
            "notifications.schedule"
        ]
    },
    
    "emails.send": {
        "name": "Envoi emails",
        "description": "Envoyer des emails via le système",
        "permissions": [
            "emails.send",
            "emails.template.use",
            "emails.history.view.own"
        ]
    },
    
    "emails.manage": {
        "name": "Gestion emails",
        "description": "Gestion complète du système d'emails",
        "permissions": [
            "emails.send",
            "emails.template.create",
            "emails.template.edit",
            "emails.template.delete",
            "emails.settings.edit",
            "emails.history.view.all",
            "emails.logs.view"
        ]
    },
    
    # ========================================================================
    # 8. ADMINISTRATION IAM
    # ========================================================================
    
    "iam.read": {
        "name": "Lecture IAM",
        "description": "Consultation du système de permissions",
        "permissions": [
            "iam.permissions.view",
            "iam.profiles.view",
            "iam.groups.view",
            "iam.bundles.view",
            "iam.users_permissions.view"
        ]
    },
    
    "iam.manage": {
        "name": "Gestion IAM",
        "description": "Gestion complète des permissions et profils",
        "permissions": [
            "iam.permissions.view",
            "iam.permissions.create",
            "iam.permissions.edit",
            "iam.permissions.delete",
            "iam.profiles.view",
            "iam.profiles.create",
            "iam.profiles.edit",
            "iam.profiles.delete",
            "iam.groups.view",
            "iam.groups.create",
            "iam.groups.edit",
            "iam.groups.delete",
            "iam.bundles.view",
            "iam.bundles.create",
            "iam.bundles.edit",
            "iam.users.assign_profile",
            "iam.users.assign_group"
        ]
    },
    
    # ========================================================================
    # 9. CONFIGURATION SYSTÈME
    # ========================================================================
    
    "config.read": {
        "name": "Lecture configuration",
        "description": "Consultation de la configuration système",
        "permissions": [
            "config.view",
            "config.feature_flags.view",
            "config.email_templates.view",
            "config.references.view"
        ]
    },
    
    "config.manage": {
        "name": "Gestion configuration",
        "description": "Modification de la configuration système",
        "permissions": [
            "config.view",
            "config.edit",
            "config.feature_flags.toggle",
            "config.email_templates.edit",
            "config.references.manage",
            "config.system.restart",
            "config.cache.clear"
        ]
    },
    
    # ========================================================================
    # 10. AUDIT & LOGS
    # ========================================================================
    
    "audit.read": {
        "name": "Lecture audit",
        "description": "Consultation des logs d'audit",
        "permissions": [
            "audit.logs.view",
            "audit.logs.search",
            "audit.logs.export",
            "audit.statistics.view"
        ]
    },
    
    "analytics.view": {
        "name": "Consultation analytics",
        "description": "Accès aux tableaux de bord et statistiques",
        "permissions": [
            "analytics.dashboard.view",
            "analytics.reports.view",
            "analytics.statistics.view",
            "analytics.export"
        ]
    },
}


# ============================================================================
# PROFILS ET LEURS BUNDLES
# ============================================================================

PROFILE_BUNDLES = {
    "candidat": [
        "auth.basic",
        "missions.read",
        "applications.submit",
        "documents.upload",
        "notifications.user"
    ],
    
    "interimaire": [
        "auth.basic",
        "missions.read",
        "applications.submit",
        "emargements.submit",
        "emargements.validate_interim",
        "documents.upload",
        "notifications.user"
    ],
    
    "company": [
        "auth.basic",
        "missions.read",
        "missions.create",
        "applications.review",
        "applications.manage",
        "emargements.validate_client",
        "entreprises.own_manage",
        "documents.upload",
        "notifications.user"
    ],
    
    "commercial": [
        "auth.basic",
        "users.read",
        "missions.manage",
        "applications.manage",
        "besoins.create",
        "consolidation.read",  # ⭐ Accès consolidation
        "signatures.read",
        "entreprises.view",
        "documents.upload",
        "notifications.user",
        "notifications.send",
        "emails.send",
        "analytics.view"
    ],
    
    "hr_manager": [
        "auth.basic",
        "users.read",
        "users.hr_access",
        "missions.manage",
        "applications.manage",
        "besoins.manage",
        "emargements.manage",
        "consolidation.read",  # ⭐ Accès consolidation
        "signatures.manage",
        "entreprises.manage",
        "documents.manage",
        "notifications.user",
        "notifications.send",
        "emails.send",
        "analytics.view"
    ],
    
    "payroll": [  # ⭐ Nouveau profil Paie
        "auth.basic",
        "consolidation.read",  # ⭐ Accès consolidation (lecture seule)
        "signatures.read",
        "emargements.consolidate",
        "notifications.user"
    ],
    
    "admin": [
        "auth.basic",
        "users.manage",
        "missions.manage",
        "applications.manage",
        "besoins.manage",
        "emargements.manage",
        "consolidation.read",
        "signatures.manage",
        "entreprises.manage",
        "documents.manage",
        "notifications.user",
        "notifications.send",
        "emails.manage",
        "iam.read",
        "config.read",
        "audit.read",
        "analytics.view"
    ],
    
    "super_admin": [
        "auth.basic",
        "users.manage",
        "missions.manage",
        "applications.manage",
        "besoins.manage",
        "emargements.manage",
        "consolidation.read",
        "signatures.manage",
        "entreprises.manage",
        "documents.manage",
        "notifications.user",
        "notifications.send",
        "emails.manage",
        "iam.manage",
        "config.manage",
        "audit.read",
        "analytics.view"
    ]
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_bundle_permissions(bundle_code: str) -> list[str]:
    """
    Récupère toutes les permissions atomiques d'un bundle
    
    Args:
        bundle_code: Code du bundle (ex: "missions.manage")
        
    Returns:
        Liste des permissions atomiques
        
    Example:
        >>> get_bundle_permissions("missions.manage")
        ['missions.read.all', 'missions.create.all', ...]
    """
    bundle = BUNDLES.get(bundle_code)
    if not bundle:
        raise ValueError(f"Bundle '{bundle_code}' not found")
    
    return bundle["permissions"]


def get_profile_bundles(profile_code: str) -> list[str]:
    """
    Récupère tous les bundles assignés à un profil
    
    Args:
        profile_code: Code du profil (ex: "commercial")
        
    Returns:
        Liste des codes de bundles
        
    Example:
        >>> get_profile_bundles("commercial")
        ['auth.basic', 'users.read', 'missions.manage', ...]
    """
    bundles = PROFILE_BUNDLES.get(profile_code)
    if not bundles:
        raise ValueError(f"Profile '{profile_code}' not found")
    
    return bundles


def get_profile_permissions(profile_code: str) -> list[str]:
    """
    Récupère TOUTES les permissions atomiques d'un profil
    (en résolvant tous ses bundles)
    
    Args:
        profile_code: Code du profil (ex: "commercial")
        
    Returns:
        Liste complète des permissions atomiques (dédupliquées)
        
    Example:
        >>> get_profile_permissions("commercial")
        ['auth.login', 'auth.logout', 'missions.read.all', ...]
    """
    profile_bundles = get_profile_bundles(profile_code)
    
    all_permissions = []
    for bundle_code in profile_bundles:
        all_permissions.extend(get_bundle_permissions(bundle_code))
    
    # Dédupliquer
    return list(set(all_permissions))


def list_all_bundles() -> dict:
    """
    Liste tous les bundles disponibles avec leurs métadonnées
    
    Returns:
        Dictionnaire des bundles avec infos
    """
    return {
        code: {
            "name": bundle["name"],
            "description": bundle["description"],
            "permissions_count": len(bundle["permissions"])
        }
        for code, bundle in BUNDLES.items()
    }


def validate_bundle(bundle_code: str) -> bool:
    """
    Vérifie si un bundle existe
    
    Args:
        bundle_code: Code du bundle
        
    Returns:
        True si le bundle existe, False sinon
    """
    return bundle_code in BUNDLES


# ============================================================================
# EXPORT POUR USAGE
# ============================================================================

__all__ = [
    'BUNDLES',
    'PROFILE_BUNDLES',
    'get_bundle_permissions',
    'get_profile_bundles',
    'get_profile_permissions',
    'list_all_bundles',
    'validate_bundle'
]
