"""
Script 4: Test du Système d'Expiration
Teste le service d'expiration et crée des profils temporaires de test
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone, timedelta
import sys

sys.path.append('/app/auth-microservice')

from awana_auth.iam.expiration_service import ExpirationService
from awana_auth.iam.models import SystemProfiles


async def test_expiration_system():
    """Teste le système d'expiration"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("⏰ TEST DU SYSTÈME D'EXPIRATION")
    print("=" * 80)
    
    service = ExpirationService(db)
    
    # 1. Vérifier les profils temporaires existants
    print("\n1️⃣ VÉRIFICATION DES PROFILS TEMPORAIRES EXISTANTS")
    print("-" * 80)
    
    users_with_temp = await db.users.count_documents({"temporary_profiles": {"$ne": []}})
    print(f"Utilisateurs avec profils temporaires: {users_with_temp}")
    
    if users_with_temp > 0:
        sample_users = await db.users.find(
            {"temporary_profiles": {"$ne": []}},
            {"_id": 0, "username": 1, "temporary_profiles": 1}
        ).limit(3).to_list(3)
        
        for user in sample_users:
            print(f"\n👤 {user.get('username')}")
            for tp in user.get("temporary_profiles", []):
                expires_at = tp.get("expires_at")
                print(f"   - Profil: {tp.get('profile_id')}")
                print(f"     Expire: {expires_at}")
    
    # 2. Vérifier toutes les expirations
    print("\n2️⃣ VÉRIFICATION GLOBALE DES EXPIRATIONS")
    print("-" * 80)
    
    checks = await service.check_all_expirations()
    print(f"Utilisateurs vérifiés: {len(checks)}")
    
    if checks:
        for check in checks[:5]:  # Montrer les 5 premiers
            print(f"\n👤 {check.username} ({check.email})")
            print(f"   Profils expirés: {len(check.expired_profiles)}")
            print(f"   Profils expirant bientôt (<3j): {len(check.expiring_soon)}")
            
            for exp in check.expired_profiles:
                print(f"      ❌ EXPIRÉ: {exp.profile_id}")
            
            for exp in check.expiring_soon:
                print(f"      ⚠️  EXPIRE DANS {exp.days_until_expiration}j: {exp.profile_id}")
    else:
        print("✅ Aucune expiration détectée")
    
    # 3. Créer un profil temporaire de test (expire dans 1 jour pour test)
    print("\n3️⃣ CRÉATION D'UN PROFIL TEMPORAIRE DE TEST")
    print("-" * 80)
    
    # Trouver un utilisateur candidat pour test
    test_user = await db.users.find_one(
        {"roles": "candidat"},
        {"_id": 0, "id": 1, "username": 1}
    )
    
    if test_user:
        print(f"Utilisateur de test: {test_user.get('username')}")
        
        candidat_temp_profile_id = await service.get_profile_id_by_code(SystemProfiles.CANDIDAT_TEMP)
        
        if candidat_temp_profile_id:
            # Assigner un profil temporaire qui expire demain (pour test)
            success = await service.assign_temporary_profile(
                user_id=test_user["id"],
                profile_id=candidat_temp_profile_id,
                duration_days=1,  # Expire demain
                reason="Profil de test - expire dans 1 jour"
            )
            
            if success:
                print(f"✅ Profil temporaire assigné (expire dans 1 jour)")
                
                # Vérifier
                check = await service.check_user_expirations(test_user["id"])
                print(f"   Expiring soon: {len(check.expiring_soon)}")
                print(f"   Expired: {len(check.expired_profiles)}")
            else:
                print("❌ Échec assignation profil temporaire")
        else:
            print("❌ Profil candidat_temp non trouvé")
    else:
        print("⚠️  Aucun utilisateur candidat trouvé pour test")
    
    # 4. Test du downgrade (simulation)
    print("\n4️⃣ TEST DU DOWNGRADE AUTOMATIQUE (SIMULATION)")
    print("-" * 80)
    print("ℹ️  Pour tester réellement, il faudrait:")
    print("   1. Créer des profils expirés (dates passées)")
    print("   2. Exécuter: service.downgrade_all_expired_profiles()")
    print("   3. Vérifier que les profils sont downgradés vers 'restricted'")
    
    # 5. Statistiques finales
    print("\n5️⃣ STATISTIQUES FINALES")
    print("-" * 80)
    
    total_users = await db.users.count_documents({})
    users_with_restricted = await db.users.count_documents({
        "profile_ids": await service.get_profile_id_by_code(SystemProfiles.RESTRICTED)
    })
    users_with_temp = await db.users.count_documents({"temporary_profiles": {"$ne": []}})
    
    print(f"Total utilisateurs: {total_users}")
    print(f"Avec profil Restreint: {users_with_restricted}")
    print(f"Avec profils temporaires: {users_with_temp}")
    
    print("\n" + "=" * 80)
    print("✅ TEST TERMINÉ")
    print("=" * 80)
    
    print("\n📋 PROCHAINES ÉTAPES:")
    print("   1. Monter les routes API d'expiration dans le serveur")
    print("   2. Créer un job cron pour exécuter:")
    print("      - Downgrade automatique (quotidien à 2h du matin)")
    print("      - Notifications (quotidien à 10h)")
    print("   3. Tester via API: GET /api/iam/expirations/check/me")
    print("   4. Tester via API: POST /api/iam/expirations/process")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(test_expiration_system())
