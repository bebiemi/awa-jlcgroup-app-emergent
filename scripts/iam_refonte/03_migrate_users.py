"""
Script 3: Migration des Utilisateurs vers les Nouveaux Profils
Assigne les profils sans perte de droits
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import sys

sys.path.append('/app/auth-microservice')

from awana_auth.iam.models import (
    SystemProfiles,
    ProfileHistoryEntry
)


# ============================================================================
# Mapping Rôles → Profils
# ============================================================================

ROLE_TO_PROFILE_MAPPING = {
    # Rôles utilisateurs
    "interim": SystemProfiles.CANDIDAT_CONFIRMED,  # Intérimaires = candidats confirmés
    "intérimaire": SystemProfiles.CANDIDAT_CONFIRMED,
    "candidat": SystemProfiles.CANDIDAT_CONFIRMED,
    "postulant": SystemProfiles.CANDIDAT_CONFIRMED,
    
    # Rôles entreprise
    "company": SystemProfiles.COMPANY,
    "entreprise": SystemProfiles.COMPANY,
    "company_admin": SystemProfiles.COMPANY,
    "company_manager": SystemProfiles.COMPANY,
    
    # Rôles collaborateurs (considérés comme candidats confirmés)
    "collaborateur": SystemProfiles.CANDIDAT_CONFIRMED,
    "collaborator": SystemProfiles.CANDIDAT_CONFIRMED,
    
    # Rôles métier
    "commercial": SystemProfiles.COMMERCIAL,
    "hr_manager": SystemProfiles.HR_MANAGER,
    "payroll": SystemProfiles.PAYROLL,
    
    # Rôles admin
    "admin": SystemProfiles.ADMIN,
    "super_admin": SystemProfiles.SUPER_ADMIN,
    "administrator": SystemProfiles.ADMIN,
}


async def get_profile_id_by_code(db, code: str) -> str:
    """Récupère l'ID d'un profil par son code"""
    profile = await db.profiles.find_one({"code": code}, {"_id": 0, "id": 1})
    if profile:
        return profile["id"]
    return None


async def migrate_users():
    """Migre tous les utilisateurs vers les nouveaux profils"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("👥 MIGRATION DES UTILISATEURS VERS NOUVEAUX PROFILS")
    print("=" * 80)
    
    # Récupérer l'ID du profil restreint (assigné à tous)
    restricted_profile_id = await get_profile_id_by_code(db, SystemProfiles.RESTRICTED)
    if not restricted_profile_id:
        print("❌ Profil 'restricted' introuvable ! Annulation.")
        return
    
    print(f"✅ Profil 'restricted' trouvé: {restricted_profile_id}")
    
    # Récupérer l'ID du profil candidat temporaire
    candidat_temp_profile_id = await get_profile_id_by_code(db, SystemProfiles.CANDIDAT_TEMP)
    candidat_confirmed_profile_id = await get_profile_id_by_code(db, SystemProfiles.CANDIDAT_CONFIRMED)
    
    # Récupérer tous les utilisateurs
    users = await db.users.find({}, {"_id": 0}).to_list(10000)
    print(f"\n📊 Total utilisateurs à migrer: {len(users)}")
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    stats = {
        "with_roles": 0,
        "without_roles": 0,
        "pending": 0,
        "active": 0,
        "suspended": 0,
        "assigned_restricted": 0,
        "assigned_temp": 0,
        "assigned_confirmed": 0,
        "assigned_business": 0,
    }
    
    for user in users:
        try:
            user_id = user.get("id")
            username = user.get("username", "N/A")
            roles = user.get("roles", [])
            status = user.get("status", "active")
            existing_profile_ids = user.get("profile_ids", [])
            
            # Skip si déjà migré (a déjà les nouveaux profils)
            if restricted_profile_id in existing_profile_ids:
                skipped_count += 1
                continue
            
            print(f"\n👤 {username} (roles: {roles}, status: {status})")
            
            # Initialiser les profils à assigner
            new_profile_ids = []
            profile_history = []
            
            # 1. TOUJOURS assigner le profil Restreint
            new_profile_ids.append(restricted_profile_id)
            stats["assigned_restricted"] += 1
            profile_history.append(
                ProfileHistoryEntry(
                    profile_id=restricted_profile_id,
                    action="assigned",
                    reason="Migration IAM - Profil de sécurité de base",
                    performed_by="system",
                    metadata={"migration": "iam_refonte", "date": datetime.now(timezone.utc).isoformat()}
                ).dict()
            )
            
            # 2. Déterminer le profil métier selon les rôles
            if roles:
                stats["with_roles"] += 1
                
                # Mapper les rôles vers profils
                for role in roles:
                    profile_code = ROLE_TO_PROFILE_MAPPING.get(role)
                    if profile_code:
                        profile_id = await get_profile_id_by_code(db, profile_code)
                        if profile_id and profile_id not in new_profile_ids:
                            new_profile_ids.append(profile_id)
                            profile_history.append(
                                ProfileHistoryEntry(
                                    profile_id=profile_id,
                                    action="assigned",
                                    reason=f"Migration IAM - Mapping rôle '{role}' → '{profile_code}'",
                                    performed_by="system",
                                    metadata={"migration": "iam_refonte", "original_role": role}
                                ).dict()
                            )
                            
                            if profile_code in [SystemProfiles.CANDIDAT_CONFIRMED, SystemProfiles.CANDIDAT_TEMP]:
                                stats["assigned_confirmed"] += 1
                            else:
                                stats["assigned_business"] += 1
                            
                            print(f"   ✅ Profil assigné: {profile_code}")
            else:
                stats["without_roles"] += 1
                
                # 3. Utilisateurs sans rôle : selon le statut
                if status == "pending":
                    stats["pending"] += 1
                    # Pending → Candidat Temporaire 15j
                    if candidat_temp_profile_id:
                        new_profile_ids.append(candidat_temp_profile_id)
                        stats["assigned_temp"] += 1
                        profile_history.append(
                            ProfileHistoryEntry(
                                profile_id=candidat_temp_profile_id,
                                action="assigned",
                                reason="Migration IAM - Nouvel utilisateur (pending)",
                                performed_by="system",
                                metadata={"migration": "iam_refonte", "status": "pending"}
                            ).dict()
                        )
                        print(f"   ✅ Profil assigné: {SystemProfiles.CANDIDAT_TEMP} (pending)")
                
                elif status == "active":
                    stats["active"] += 1
                    # Active sans rôle → Candidat Confirmé
                    if candidat_confirmed_profile_id:
                        new_profile_ids.append(candidat_confirmed_profile_id)
                        stats["assigned_confirmed"] += 1
                        profile_history.append(
                            ProfileHistoryEntry(
                                profile_id=candidat_confirmed_profile_id,
                                action="assigned",
                                reason="Migration IAM - Utilisateur actif sans rôle",
                                performed_by="system",
                                metadata={"migration": "iam_refonte", "status": "active"}
                            ).dict()
                        )
                        print(f"   ✅ Profil assigné: {SystemProfiles.CANDIDAT_CONFIRMED} (active)")
                
                elif status == "suspended":
                    stats["suspended"] += 1
                    # Suspended → Seulement Restreint (déjà assigné)
                    print(f"   ℹ️  Utilisateur suspendu : seulement profil Restreint")
            
            # 4. Préserver les profils existants (ne pas perdre de droits)
            for existing_profile_id in existing_profile_ids:
                if existing_profile_id not in new_profile_ids:
                    new_profile_ids.append(existing_profile_id)
                    print(f"   ℹ️  Profil existant préservé: {existing_profile_id}")
            
            # 5. Mettre à jour l'utilisateur
            update_data = {
                "profile_ids": new_profile_ids,
                "profile_history": profile_history,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            
            print(f"   ✅ Migration réussie : {len(new_profile_ids)} profils assignés")
            migrated_count += 1
            
        except Exception as e:
            print(f"   ❌ Erreur migration {username}: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE LA MIGRATION")
    print("=" * 80)
    print(f"✅ Utilisateurs migrés: {migrated_count}")
    print(f"⏭️  Utilisateurs déjà migrés: {skipped_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📊 Total traité: {migrated_count + skipped_count}")
    
    print("\n📈 STATISTIQUES DÉTAILLÉES:")
    print(f"   Avec rôles: {stats['with_roles']}")
    print(f"   Sans rôles: {stats['without_roles']}")
    print(f"     - Pending: {stats['pending']}")
    print(f"     - Active: {stats['active']}")
    print(f"     - Suspended: {stats['suspended']}")
    
    print(f"\n🎯 PROFILS ASSIGNÉS:")
    print(f"   Restreint (tous): {stats['assigned_restricted']}")
    print(f"   Candidat Temp (15j): {stats['assigned_temp']}")
    print(f"   Candidat Confirmé: {stats['assigned_confirmed']}")
    print(f"   Profils métier: {stats['assigned_business']}")
    
    # Vérification finale
    total_with_restricted = await db.users.count_documents({"profile_ids": restricted_profile_id})
    print(f"\n✅ Utilisateurs avec profil Restreint: {total_with_restricted}/{len(users)}")
    
    if total_with_restricted < len(users):
        print(f"⚠️  {len(users) - total_with_restricted} utilisateurs n'ont pas le profil Restreint !")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(migrate_users())
