"""
Assign Application Permissions to IAM Profiles/Roles
Assigne les permissions de candidature aux profils candidat, postulant, intérimaire
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def assign_application_permissions():
    """Assigner les permissions de candidature aux bons profils/rôles"""
    
    # Connexion MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("🔐 Attribution des permissions de candidature...")
    print("=" * 60)
    
    # 1. Trouver les permissions d'application
    app_permissions = await db.permissions.find({
        "code": {"$in": [
            "applications.create",
            "applications.create_own",
            "applications.read_own",
            "applications.update_own"
        ]}
    }, {"_id": 0, "id": 1, "code": 1}).to_list(None)
    
    if not app_permissions:
        print("❌ Aucune permission d'application trouvée")
        client.close()
        return
    
    permission_ids = [p["id"] for p in app_permissions]
    print(f"\n📋 Permissions trouvées: {len(permission_ids)}")
    for p in app_permissions:
        print(f"   - {p['code']}")
    
    # 2. Assigner aux profils IAM (collection profiles)
    profiles_to_update = [
        "profile_postulant",
        "applicant",
        "role.postulant",
        "role.candidat",
        "role.interim"
    ]
    
    print(f"\n👤 Attribution aux profils IAM...")
    for profile_code in profiles_to_update:
        profile = await db.profiles.find_one({"code": profile_code})
        
        if profile:
            existing_perms = profile.get("permission_ids", [])
            # Ajouter seulement les permissions qui n'existent pas déjà
            new_perms = [p for p in permission_ids if p not in existing_perms]
            
            if new_perms:
                updated_perms = existing_perms + new_perms
                result = await db.profiles.update_one(
                    {"code": profile_code},
                    {"$set": {"permission_ids": updated_perms}}
                )
                print(f"   ✅ {profile_code}: {len(new_perms)} permissions ajoutées")
            else:
                print(f"   ℹ️  {profile_code}: permissions déjà présentes")
        else:
            print(f"   ⚠️  {profile_code}: profil non trouvé")
    
    # 3. Vérifier/créer des rôles IAM spécifiques si nécessaire
    print(f"\n🎭 Vérification des rôles IAM...")
    
    roles_to_check = [
        {
            "name": "candidat",
            "description": "Rôle pour les candidats/postulants",
            "permissions": permission_ids
        },
        {
            "name": "intérimaire",
            "description": "Rôle pour les intérimaires",
            "permissions": permission_ids
        }
    ]
    
    for role_data in roles_to_check:
        existing_role = await db.iam_roles.find_one({"name": role_data["name"]})
        
        if existing_role:
            # Mettre à jour les permissions
            existing_perms = existing_role.get("permissions", [])
            new_perms = [p for p in permission_ids if p not in existing_perms]
            
            if new_perms:
                updated_perms = existing_perms + new_perms
                await db.iam_roles.update_one(
                    {"name": role_data["name"]},
                    {"$set": {"permissions": updated_perms}}
                )
                print(f"   ✅ Rôle IAM '{role_data['name']}': {len(new_perms)} permissions ajoutées")
            else:
                print(f"   ℹ️  Rôle IAM '{role_data['name']}': permissions déjà présentes")
        else:
            print(f"   ⚠️  Rôle IAM '{role_data['name']}': non trouvé (utilise profils)")
    
    print("\n" + "=" * 60)
    print("✅ Permissions assignées avec succès!")
    
    # Résumé
    total_profiles = await db.profiles.count_documents({"permission_ids": {"$in": permission_ids}})
    print(f"\n📊 Résumé:")
    print(f"   Profils avec permissions application: {total_profiles}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(assign_application_permissions())
