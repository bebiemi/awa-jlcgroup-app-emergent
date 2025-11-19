"""
Script 1: Création des Capability Bundles
Crée tous les bundles de capacités réutilisables
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import sys

# Ajouter le chemin pour importer les modèles
sys.path.append('/app/auth-microservice')

from awana_auth.iam.models import (
    CapabilityBundle,
    PermissionCategory,
    SystemBundles
)


# ============================================================================
# Définition des Bundles
# ============================================================================

CAPABILITY_BUNDLES = [
    # ========== BUNDLES NIVEAU RESTREINT ==========
    {
        "code": SystemBundles.READONLY_ACCESS,
        "name": "Accès Lecture Seule",
        "description": "Permissions de base en lecture seule pour tous les utilisateurs",
        "category": PermissionCategory.SYSTEM,
        "permission_codes": [
            "dashboard.view.readonly",
            "profile.view.own",
        ],
        "tags": ["readonly", "base", "security"],
        "is_system": True
    },
    {
        "code": SystemBundles.PUBLIC_MISSIONS_VIEW,
        "name": "Consultation Missions Publiques",
        "description": "Voir et rechercher les missions publiées",
        "category": PermissionCategory.MISSIONS,
        "permission_codes": [
            "missions.view.published",
            "missions.search.public",
            "missions.browse",
        ],
        "tags": ["missions", "public", "readonly"],
        "is_system": True
    },
    
    # ========== BUNDLES CANDIDAT ==========
    {
        "code": SystemBundles.PROFILE_SELF_MANAGE,
        "name": "Gestion Profil Personnel",
        "description": "Éditer son propre profil et paramètres",
        "category": PermissionCategory.PROFILE,
        "permission_codes": [
            "profile.edit.own",
            "profile.manage.own",
            "security.edit.own",
            "dashboard.customize.own",
        ],
        "tags": ["profile", "self", "edit"],
        "is_system": True
    },
    {
        "code": SystemBundles.DOCUMENTS_SELF_MANAGE,
        "name": "Gestion Documents Personnels",
        "description": "Télécharger, voir et gérer ses documents (CV, ID, etc.)",
        "category": PermissionCategory.DOCUMENTS,
        "permission_codes": [
            "documents.upload.own",
            "documents.view.own",
            "documents.delete.own",
            "documents.download.own",
            "documents.manage.own",
        ],
        "tags": ["documents", "self", "upload"],
        "is_system": True
    },
    {
        "code": SystemBundles.MISSIONS_APPLY,
        "name": "Candidater aux Missions",
        "description": "Postuler aux missions publiées (sauf collaborateurs)",
        "category": PermissionCategory.APPLICATIONS,
        "permission_codes": [
            "missions.apply",
            "applications.create.own",
        ],
        "tags": ["missions", "apply", "candidat"],
        "is_system": True
    },
    {
        "code": SystemBundles.APPLICATIONS_TRACK_OWN,
        "name": "Suivi Candidatures Personnelles",
        "description": "Voir et suivre ses propres candidatures",
        "category": PermissionCategory.APPLICATIONS,
        "permission_codes": [
            "applications.view.own",
            "applications.track.own",
            "applications.read.own",
        ],
        "tags": ["applications", "tracking", "own"],
        "is_system": True
    },
    
    # ========== BUNDLES ENTREPRISE ==========
    {
        "code": SystemBundles.COMPANY_MANAGE_OWN,
        "name": "Gestion Entreprise (Own)",
        "description": "Gérer sa propre entreprise",
        "category": PermissionCategory.ENTREPRISES,
        "permission_codes": [
            "entreprises.manage.own",
            "entreprises.edit.own",
            "entreprises.view.own",
        ],
        "tags": ["entreprises", "own", "manage"],
        "is_system": True
    },
    {
        "code": SystemBundles.BESOINS_MANAGE_OWN,
        "name": "Gestion Besoins (Own)",
        "description": "Créer, éditer et soumettre ses besoins de mission",
        "category": PermissionCategory.BESOINS,
        "permission_codes": [
            "besoins.create.own",
            "besoins.edit.own",
            "besoins.submit.own",
            "besoins.comment.own",
            "besoins.view.own",
        ],
        "tags": ["besoins", "own", "draft"],
        "is_system": True
    },
    {
        "code": SystemBundles.EMARGEMENTS_VALIDATE,
        "name": "Validation Émargements",
        "description": "Valider, refuser et annoter les émargements",
        "category": PermissionCategory.EMARGEMENTS,
        "permission_codes": [
            "emargements.validate",
            "emargements.reject",
            "emargements.annotate",
            "emargements.view.own",
        ],
        "tags": ["emargements", "validation", "company"],
        "is_system": True
    },
    
    # ========== BUNDLES COMMERCIAL ==========
    {
        "code": SystemBundles.MISSIONS_MANAGE_OWN,
        "name": "Gestion Missions (Own)",
        "description": "Gérer ses propres missions",
        "category": PermissionCategory.MISSIONS,
        "permission_codes": [
            "missions.create.own",
            "missions.edit.own",
            "missions.delete.own",
            "missions.view.own",
        ],
        "tags": ["missions", "own", "commercial"],
        "is_system": True
    },
    {
        "code": SystemBundles.MISSIONS_MANAGE_ALL,
        "name": "Gestion Missions (All)",
        "description": "Gérer toutes les missions (pause, publication, assignation)",
        "category": PermissionCategory.MISSIONS,
        "permission_codes": [
            "missions.manage.all",
            "missions.pause",
            "missions.publish",
            "missions.assign_users",
            "missions.view.all",
            "missions.edit.all",
        ],
        "tags": ["missions", "all", "commercial"],
        "is_system": True
    },
    {
        "code": SystemBundles.APPLICATIONS_REVIEW,
        "name": "Revue Candidatures",
        "description": "Examiner, valider et présélectionner les candidatures",
        "category": PermissionCategory.APPLICATIONS,
        "permission_codes": [
            "applications.review.all",
            "applications.validate.all",
            "applications.prescreen",
            "applications.view.all",
        ],
        "tags": ["applications", "review", "commercial"],
        "is_system": True
    },
    {
        "code": SystemBundles.BESOINS_MANAGE_ALL,
        "name": "Gestion Besoins (All)",
        "description": "Voir, éditer, approuver et rejeter tous les besoins",
        "category": PermissionCategory.BESOINS,
        "permission_codes": [
            "besoins.view.all",
            "besoins.edit.all",
            "besoins.approve",
            "besoins.reject",
        ],
        "tags": ["besoins", "all", "commercial"],
        "is_system": True
    },
    {
        "code": SystemBundles.ENTREPRISES_MANAGE_ALL,
        "name": "Gestion Entreprises (All)",
        "description": "Créer, éditer, archiver et transférer les entreprises",
        "category": PermissionCategory.ENTREPRISES,
        "permission_codes": [
            "entreprises.create",
            "entreprises.edit.all",
            "entreprises.archive",
            "entreprises.transfer.validate",
            "entreprises.view.all",
        ],
        "tags": ["entreprises", "all", "commercial"],
        "is_system": True
    },
    {
        "code": SystemBundles.COMMERCIAL_TOOLS,
        "name": "Outils Commerciaux",
        "description": "Accès aux outils spécifiques commerciaux (CVTech, etc.)",
        "category": PermissionCategory.SYSTEM,
        "permission_codes": [
            "cvtech.search",
            "dashboard.manage.own",
            "reports.view",
        ],
        "tags": ["tools", "commercial", "search"],
        "is_system": True
    },
    
    # ========== BUNDLES PAIE ==========
    {
        "code": SystemBundles.MISSIONS_VIEW_ACTIVE,
        "name": "Consultation Missions Actives",
        "description": "Voir toutes les missions en cours",
        "category": PermissionCategory.MISSIONS,
        "permission_codes": [
            "missions.view.all",
        ],
        "tags": ["missions", "view", "payroll"],
        "is_system": True
    },
    {
        "code": SystemBundles.EMARGEMENTS_MANAGE,
        "name": "Gestion Émargements",
        "description": "Voir et ajuster les émargements pour facturation",
        "category": PermissionCategory.EMARGEMENTS,
        "permission_codes": [
            "emargements.view.all",
            "emargements.adjust",
        ],
        "tags": ["emargements", "payroll", "manage"],
        "is_system": True
    },
    {
        "code": SystemBundles.PAYROLL_MANAGE,
        "name": "Gestion Paie",
        "description": "Calculer et gérer la paie",
        "category": PermissionCategory.PAYROLL,
        "permission_codes": [
            "payroll.calculate",
            "payroll.manage",
        ],
        "tags": ["payroll", "calculate", "manage"],
        "is_system": True
    },
    {
        "code": SystemBundles.INVOICING_MANAGE,
        "name": "Gestion Facturation",
        "description": "Gérer la facturation clients",
        "category": PermissionCategory.PAYROLL,
        "permission_codes": [
            "invoicing.manage",
            "invoicing.create",
            "invoicing.edit",
        ],
        "tags": ["invoicing", "billing", "manage"],
        "is_system": True
    },
    
    # ========== BUNDLES RRH ==========
    {
        "code": SystemBundles.USERS_MANAGE,
        "name": "Gestion Utilisateurs",
        "description": "Gérer les utilisateurs du système",
        "category": PermissionCategory.ADMIN,
        "permission_codes": [
            "users.manage",
            "users.create",
            "users.edit",
            "users.view.all",
            "users.manage_status",
        ],
        "tags": ["users", "hr", "manage"],
        "is_system": True
    },
    {
        "code": SystemBundles.RECRUITMENT_PROCESS,
        "name": "Processus de Recrutement",
        "description": "Participer au recrutement et valider les embauches",
        "category": PermissionCategory.RECRUITMENT,
        "permission_codes": [
            "recruitment.validate",
            "recruitment.participate",
            "applications.view.all",
            "missions.view.open",
        ],
        "tags": ["recruitment", "hr", "hiring"],
        "is_system": True
    },
    {
        "code": SystemBundles.MEDICAL_COMPLIANCE,
        "name": "Conformité Médicale",
        "description": "Gérer les visites médicales obligatoires",
        "category": PermissionCategory.RECRUITMENT,
        "permission_codes": [
            "medical_visits.trigger",
            "medical_visits.validate",
        ],
        "tags": ["medical", "compliance", "hr"],
        "is_system": True
    },
    {
        "code": SystemBundles.CANDIDAT_PROGRESSION,
        "name": "Progression Candidat",
        "description": "Approuver le passage candidat → intérimaire",
        "category": PermissionCategory.RECRUITMENT,
        "permission_codes": [
            "candidat_to_interim.approve",
        ],
        "tags": ["progression", "candidat", "interim"],
        "is_system": True
    },
    {
        "code": SystemBundles.HR_REPORTING,
        "name": "Reporting RH",
        "description": "Accès au tableau de bord et rapports RH",
        "category": PermissionCategory.DASHBOARD,
        "permission_codes": [
            "dashboard.hr",
            "reports.view",
        ],
        "tags": ["reporting", "hr", "dashboard"],
        "is_system": True
    },
]


async def get_permission_id_by_code(db, code: str) -> str:
    """Récupère l'ID d'une permission par son code"""
    permission = await db.permissions.find_one({"code": code}, {"_id": 0, "id": 1})
    if permission:
        return permission["id"]
    
    # Si la permission n'existe pas, la créer (mode permissif pour migration)
    print(f"  ⚠️  Permission '{code}' non trouvée, création automatique...")
    parts = code.split(".")
    resource = parts[0] if len(parts) > 0 else "unknown"
    action = parts[1] if len(parts) > 1 else "unknown"
    scope = parts[2] if len(parts) > 2 else "own"
    
    from uuid import uuid4
    perm_id = str(uuid4())
    
    permission_doc = {
        "id": perm_id,
        "code": code,
        "name": code.replace(".", " ").title(),
        "description": f"Permission auto-créée pour {code}",
        "resource": resource,
        "action": action,
        "scope": scope,
        "category": "legacy",
        "tags": ["auto-created"],
        "is_system": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.permissions.insert_one(permission_doc)
    print(f"  ✅ Permission '{code}' créée avec ID: {perm_id}")
    
    return perm_id


async def create_capability_bundles():
    """Crée tous les capability bundles dans la base de données"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🧩 CRÉATION DES CAPABILITY BUNDLES")
    print("=" * 80)
    
    # Créer la collection si elle n'existe pas
    collections = await db.list_collection_names()
    if 'capability_bundles' not in collections:
        await db.create_collection('capability_bundles')
        print("✅ Collection 'capability_bundles' créée")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for bundle_data in CAPABILITY_BUNDLES:
        try:
            code = bundle_data["code"]
            print(f"\n📦 Traitement bundle: {code}")
            print(f"   Nom: {bundle_data['name']}")
            
            # Vérifier si le bundle existe déjà
            existing = await db.capability_bundles.find_one({"code": code}, {"_id": 0})
            
            # Résoudre les permission_ids à partir des codes
            permission_ids = []
            for perm_code in bundle_data["permission_codes"]:
                perm_id = await get_permission_id_by_code(db, perm_code)
                if perm_id:
                    permission_ids.append(perm_id)
            
            print(f"   Permissions résolues: {len(permission_ids)}/{len(bundle_data['permission_codes'])}")
            
            # Créer le bundle
            bundle = CapabilityBundle(
                code=code,
                name=bundle_data["name"],
                description=bundle_data["description"],
                category=bundle_data["category"],
                permission_ids=permission_ids,
                tags=bundle_data["tags"],
                is_system=bundle_data["is_system"],
            )
            
            bundle_dict = bundle.dict()
            bundle_dict["created_at"] = bundle.created_at.isoformat()
            bundle_dict["updated_at"] = bundle.updated_at.isoformat()
            
            if existing:
                # Mettre à jour
                await db.capability_bundles.update_one(
                    {"code": code},
                    {"$set": bundle_dict}
                )
                print(f"   ✅ Bundle mis à jour")
                updated_count += 1
            else:
                # Créer
                await db.capability_bundles.insert_one(bundle_dict)
                print(f"   ✅ Bundle créé")
                created_count += 1
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ")
    print("=" * 80)
    print(f"✅ Bundles créés: {created_count}")
    print(f"🔄 Bundles mis à jour: {updated_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📦 Total: {created_count + updated_count} bundles")
    
    # Vérification finale
    total = await db.capability_bundles.count_documents({})
    print(f"\n✅ Total bundles en base: {total}")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(create_capability_bundles())
