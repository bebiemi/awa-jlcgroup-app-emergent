"""
Script 2: Création des Profils Métier
Crée les 8 profils métier avec leurs bundles et hiérarchies
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import sys

sys.path.append('/app/auth-microservice')

from awana_auth.iam.models import (
    Profile,
    ProfileCategory,
    ProfileMetadata,
    SystemProfiles,
    SystemBundles
)


# ============================================================================
# Définition des Profils Métier
# ============================================================================

PROFILES = [
    # ========== 1. PROFIL RESTREINT (Base de sécurité) ==========
    {
        "code": SystemProfiles.RESTRICTED,
        "name": "Restreint",
        "description": "Profil de sécurité minimum avec accès lecture seule. Assigné automatiquement à tous les utilisateurs (Zero Trust).",
        "category": ProfileCategory.SYSTEM,
        "bundle_codes": [
            SystemBundles.READONLY_ACCESS,
            SystemBundles.PUBLIC_MISSIONS_VIEW,
        ],
        "parent_profile_code": None,
        "is_visible": True,
        "is_system": True,
        "is_protected": True,
        "metadata": ProfileMetadata(
            priority=1,
            icon="lock",
            color="gray",
            badge="SÉCURITÉ"
        )
    },
    
    # ========== 2. CANDIDAT TEMPORAIRE 15J ==========
    {
        "code": SystemProfiles.CANDIDAT_TEMP,
        "name": "Utilisateur Défaut 15j",
        "description": "Profil temporaire pour nouveaux candidats. Expire après 15 jours glissants basés sur first_login_at. Downgrade automatique vers Restreint.",
        "category": ProfileCategory.BUSINESS,
        "bundle_codes": [
            SystemBundles.PROFILE_SELF_MANAGE,
            SystemBundles.DOCUMENTS_SELF_MANAGE,
            SystemBundles.MISSIONS_APPLY,
            SystemBundles.APPLICATIONS_TRACK_OWN,
        ],
        "parent_profile_code": SystemProfiles.RESTRICTED,  # Hérite de Restreint
        "is_visible": True,
        "is_system": True,
        "is_protected": True,
        "metadata": ProfileMetadata(
            priority=10,
            icon="clock",
            color="yellow",
            badge="15J"
        )
    },
    
    # ========== 3. CANDIDAT CONFIRMÉ ==========
    {
        "code": SystemProfiles.CANDIDAT_CONFIRMED,
        "name": "Candidat/Postulant",
        "description": "Profil permanent pour candidats validés (email/téléphone/identité). Permissions identiques à Candidat 15j mais sans expiration.",
        "category": ProfileCategory.BUSINESS,
        "bundle_codes": [
            SystemBundles.PROFILE_SELF_MANAGE,
            SystemBundles.DOCUMENTS_SELF_MANAGE,
            SystemBundles.MISSIONS_APPLY,
            SystemBundles.APPLICATIONS_TRACK_OWN,
        ],
        "parent_profile_code": SystemProfiles.RESTRICTED,  # Hérite de Restreint
        "is_visible": True,
        "is_system": False,
        "is_protected": False,
        "metadata": ProfileMetadata(
            priority=20,
            icon="user-check",
            color="green",
            badge=None
        )
    },
    
    # ========== 4. ENTREPRISE ==========
    {
        "code": SystemProfiles.COMPANY,
        "name": "Entreprise",
        "description": "Profil métier pour gestionnaires d'entreprise. Gérer entreprise, créer besoins, valider émargements. Ne peut pas modifier besoin soumis à JLC.",
        "category": ProfileCategory.BUSINESS,
        "bundle_codes": [
            SystemBundles.COMPANY_MANAGE_OWN,
            SystemBundles.BESOINS_MANAGE_OWN,
            SystemBundles.EMARGEMENTS_VALIDATE,
            SystemBundles.PROFILE_SELF_MANAGE,
            SystemBundles.DOCUMENTS_SELF_MANAGE,
        ],
        "parent_profile_code": SystemProfiles.RESTRICTED,
        "is_visible": True,
        "is_system": False,
        "is_protected": False,
        "metadata": ProfileMetadata(
            priority=30,
            icon="building",
            color="blue",
            badge=None
        )
    },
    
    # ========== 5. COMMERCIAL ==========
    {
        "code": SystemProfiles.COMMERCIAL,
        "name": "Commercial",
        "description": "Profil commercial avec permissions granulaires (own/all). Gestion missions, candidatures, besoins, entreprises. Accès CVTech.",
        "category": ProfileCategory.BUSINESS,
        "bundle_codes": [
            SystemBundles.MISSIONS_MANAGE_OWN,
            SystemBundles.MISSIONS_MANAGE_ALL,
            SystemBundles.APPLICATIONS_REVIEW,
            SystemBundles.BESOINS_MANAGE_ALL,
            SystemBundles.ENTREPRISES_MANAGE_ALL,
            SystemBundles.COMMERCIAL_TOOLS,
            SystemBundles.PROFILE_SELF_MANAGE,
        ],
        "parent_profile_code": SystemProfiles.RESTRICTED,
        "is_visible": True,
        "is_system": False,
        "is_protected": False,
        "metadata": ProfileMetadata(
            priority=40,
            icon="briefcase",
            color="purple",
            badge=None
        )
    },
    
    # ========== 6. PAIE ==========
    {
        "code": SystemProfiles.PAYROLL,
        "name": "Paie",
        "description": "Profil paie et facturation. Voir missions actives, gérer émargements, calculer paie, gérer facturation. Accès limité données entreprises.",
        "category": ProfileCategory.BUSINESS,
        "bundle_codes": [
            SystemBundles.MISSIONS_VIEW_ACTIVE,
            SystemBundles.EMARGEMENTS_MANAGE,
            SystemBundles.PAYROLL_MANAGE,
            SystemBundles.INVOICING_MANAGE,
            SystemBundles.PROFILE_SELF_MANAGE,
        ],
        "parent_profile_code": SystemProfiles.RESTRICTED,
        "is_visible": True,
        "is_system": False,
        "is_protected": False,
        "metadata": ProfileMetadata(
            priority=45,
            icon="calculator",
            color="teal",
            badge=None
        )
    },
    
    # ========== 7. RRH ==========
    {
        "code": SystemProfiles.HR_MANAGER,
        "name": "RRH",
        "description": "Responsable Ressources Humaines. Gestion utilisateurs, recrutement, visites médicales, progression candidat→intérimaire, reporting RH.",
        "category": ProfileCategory.BUSINESS,
        "bundle_codes": [
            SystemBundles.USERS_MANAGE,
            SystemBundles.RECRUITMENT_PROCESS,
            SystemBundles.MEDICAL_COMPLIANCE,
            SystemBundles.CANDIDAT_PROGRESSION,
            SystemBundles.HR_REPORTING,
            SystemBundles.PROFILE_SELF_MANAGE,
        ],
        "parent_profile_code": SystemProfiles.RESTRICTED,
        "is_visible": True,
        "is_system": False,
        "is_protected": False,
        "metadata": ProfileMetadata(
            priority=50,
            icon="users-cog",
            color="orange",
            badge=None
        )
    },
    
    # ========== 8. ADMIN (Consolidation de l'existant) ==========
    {
        "code": SystemProfiles.ADMIN,
        "name": "Administrateur",
        "description": "Profil administrateur système. Accès complet aux fonctionnalités d'administration. Conservation du profil existant.",
        "category": ProfileCategory.ADMIN,
        "bundle_codes": [],  # Garder les permissions directes existantes
        "parent_profile_code": SystemProfiles.RESTRICTED,
        "is_visible": True,
        "is_system": True,
        "is_protected": True,
        "metadata": ProfileMetadata(
            priority=90,
            icon="shield",
            color="red",
            badge="ADMIN"
        )
    },
    
    # ========== 9. SUPER ADMIN (Consolidation de l'existant) ==========
    {
        "code": SystemProfiles.SUPER_ADMIN,
        "name": "Super Administrateur",
        "description": "Profil super administrateur avec tous les pouvoirs. Conservation du profil existant.",
        "category": ProfileCategory.ADMIN,
        "bundle_codes": [],  # Garder les permissions directes existantes
        "parent_profile_code": None,  # Pas d'héritage
        "is_visible": True,
        "is_system": True,
        "is_protected": True,
        "metadata": ProfileMetadata(
            priority=100,
            icon="crown",
            color="gold",
            badge="SUPER ADMIN"
        )
    },
]


async def get_bundle_id_by_code(db, code: str) -> str:
    """Récupère l'ID d'un bundle par son code"""
    bundle = await db.capability_bundles.find_one({"code": code}, {"_id": 0, "id": 1})
    if bundle:
        return bundle["id"]
    print(f"  ⚠️  Bundle '{code}' non trouvé")
    return None


async def get_profile_id_by_code(db, code: str) -> str:
    """Récupère l'ID d'un profil par son code"""
    profile = await db.profiles.find_one({"code": code}, {"_id": 0, "id": 1})
    if profile:
        return profile["id"]
    return None


async def create_profiles():
    """Crée tous les profils métier dans la base de données"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("👥 CRÉATION DES PROFILS MÉTIER")
    print("=" * 80)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for profile_data in PROFILES:
        try:
            code = profile_data["code"]
            print(f"\n📋 Traitement profil: {code}")
            print(f"   Nom: {profile_data['name']}")
            print(f"   Catégorie: {profile_data['category']}")
            
            # Vérifier si le profil existe déjà
            existing = await db.profiles.find_one({"code": code}, {"_id": 0})
            
            # Résoudre les bundle_ids à partir des codes
            capability_bundle_ids = []
            for bundle_code in profile_data["bundle_codes"]:
                bundle_id = await get_bundle_id_by_code(db, bundle_code)
                if bundle_id:
                    capability_bundle_ids.append(bundle_id)
            
            print(f"   Bundles résolus: {len(capability_bundle_ids)}/{len(profile_data['bundle_codes'])}")
            
            # Résoudre le parent_profile_id
            parent_profile_id = None
            if profile_data["parent_profile_code"]:
                parent_profile_id = await get_profile_id_by_code(db, profile_data["parent_profile_code"])
                if parent_profile_id:
                    print(f"   Parent: {profile_data['parent_profile_code']}")
            
            # Créer le profil
            profile = Profile(
                code=code,
                name=profile_data["name"],
                description=profile_data["description"],
                category=profile_data["category"],
                capability_bundle_ids=capability_bundle_ids,
                permission_ids=[],  # Permissions directes (à conserver pour existants)
                parent_profile_id=parent_profile_id,
                is_visible=profile_data["is_visible"],
                is_system=profile_data["is_system"],
                is_protected=profile_data["is_protected"],
                metadata=profile_data["metadata"],
            )
            
            profile_dict = profile.dict()
            profile_dict["created_at"] = profile.created_at.isoformat()
            profile_dict["updated_at"] = profile.updated_at.isoformat()
            
            # Préserver les permission_ids existantes si le profil existe déjà
            if existing:
                existing_permission_ids = existing.get("permission_ids", [])
                if existing_permission_ids:
                    profile_dict["permission_ids"] = existing_permission_ids
                    print(f"   ℹ️  Permissions directes préservées: {len(existing_permission_ids)}")
                
                # Pour admin/super_admin, ne pas écraser les bundles existants
                if code in [SystemProfiles.ADMIN, SystemProfiles.SUPER_ADMIN]:
                    if existing.get("capability_bundle_ids"):
                        profile_dict["capability_bundle_ids"] = existing["capability_bundle_ids"]
                    
                # Mettre à jour
                await db.profiles.update_one(
                    {"code": code},
                    {"$set": profile_dict}
                )
                print(f"   ✅ Profil mis à jour")
                updated_count += 1
            else:
                # Créer
                await db.profiles.insert_one(profile_dict)
                print(f"   ✅ Profil créé")
                created_count += 1
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ")
    print("=" * 80)
    print(f"✅ Profils créés: {created_count}")
    print(f"🔄 Profils mis à jour: {updated_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"👥 Total: {created_count + updated_count} profils")
    
    # Vérification finale
    total = await db.profiles.count_documents({})
    system_profiles = await db.profiles.count_documents({"is_system": True})
    business_profiles = await db.profiles.count_documents({"category": "business"})
    
    print(f"\n✅ Total profils en base: {total}")
    print(f"   - Système: {system_profiles}")
    print(f"   - Métier: {business_profiles}")
    
    # Afficher la hiérarchie
    print("\n🌳 HIÉRARCHIE DES PROFILS:")
    restricted_id = await get_profile_id_by_code(db, SystemProfiles.RESTRICTED)
    children = await db.profiles.find({"parent_profile_id": restricted_id}, {"_id": 0, "code": 1, "name": 1}).to_list(100)
    print(f"   {SystemProfiles.RESTRICTED} (Restreint)")
    for child in children:
        print(f"   ├── {child['code']} ({child['name']})")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(create_profiles())
