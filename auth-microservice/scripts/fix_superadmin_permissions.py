#!/usr/bin/env python3
"""
Corriger le profil super_admin pour qu'il possède TOUTES les permissions
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_superadmin():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        print("=" * 70)
        print(" 🔧 CORRECTION DU PROFIL SUPER_ADMIN")
        print("=" * 70 + "\n")
        
        # 1. Récupérer TOUTES les permissions
        print("1️⃣ Récupération de toutes les permissions...\n")
        
        all_permissions = await db.permissions.find({}, {"_id": 0, "id": 1, "code": 1}).to_list(None)
        all_perm_ids = [p['id'] for p in all_permissions]
        
        print(f"✅ {len(all_perm_ids)} permissions trouvées en base")
        
        # 2. Mettre à jour le profil super_admin
        print("\n2️⃣ Mise à jour du profil 'super_admin'...\n")
        
        super_admin_profile = await db.profiles.find_one({"code": "super_admin"})
        
        if not super_admin_profile:
            print("❌ Profil 'super_admin' non trouvé!")
            print("   Création du profil...")
            
            import uuid
            profile_id = str(uuid.uuid4())
            super_admin_profile = {
                "id": profile_id,
                "code": "super_admin",
                "name": "Super Administrateur",
                "description": "Accès complet et illimité à toutes les fonctionnalités",
                "permission_ids": all_perm_ids,
                "is_system_role": True,
                "is_protected": True,
                "priority": 1000,
                "category": "admin",
                "color": "#DC2626",
                "icon": "shield-check",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.profiles.insert_one(super_admin_profile)
            print(f"✅ Profil créé avec {len(all_perm_ids)} permissions")
        else:
            # Mettre à jour avec TOUTES les permissions
            old_count = len(super_admin_profile.get('permission_ids', []))
            
            await db.profiles.update_one(
                {"code": "super_admin"},
                {
                    "$set": {
                        "permission_ids": all_perm_ids,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            print(f"✅ Profil mis à jour:")
            print(f"   - Avant: {old_count} permissions")
            print(f"   - Après: {len(all_perm_ids)} permissions")
            print(f"   - Ajoutées: {len(all_perm_ids) - old_count}")
        
        # 3. Vérifier les utilisateurs super_admin
        print("\n3️⃣ Vérification des utilisateurs super_admin...\n")
        
        super_admin_users = await db.users.find(
            {"roles": "super_admin"},
            {"_id": 0, "id": 1, "username": 1, "status": 1, "is_active": 1}
        ).to_list(None)
        
        print(f"📊 {len(super_admin_users)} utilisateur(s) avec rôle 'super_admin'")
        
        for user in super_admin_users:
            print(f"\n   👤 {user.get('username')}:")
            
            fixes_needed = []
            
            if user.get('status') != 'active':
                fixes_needed.append('status')
            
            if not user.get('is_active'):
                fixes_needed.append('is_active')
            
            if fixes_needed:
                update_data = {}
                if 'status' in fixes_needed:
                    update_data['status'] = 'active'
                if 'is_active' in fixes_needed:
                    update_data['is_active'] = True
                
                await db.users.update_one(
                    {"id": user.get('id')},
                    {"$set": update_data}
                )
                
                print(f"      🔧 Corrigé: {', '.join(fixes_needed)}")
            else:
                print(f"      ✅ OK")
        
        # 4. Vérifier le groupe IAM super_admin
        print("\n4️⃣ Vérification du groupe IAM...\n")
        
        super_admin_group = await db.iam_groups.find_one({"code": "grp.super_admin"})
        
        if super_admin_group:
            # Ajouter tous les super_admin au groupe
            super_admin_user_ids = [u['id'] for u in super_admin_users]
            current_user_ids = super_admin_group.get('user_ids', [])
            
            # Ajouter les utilisateurs manquants
            new_users = [uid for uid in super_admin_user_ids if uid not in current_user_ids]
            
            if new_users:
                await db.iam_groups.update_one(
                    {"code": "grp.super_admin"},
                    {"$addToSet": {"user_ids": {"$each": new_users}}}
                )
                print(f"✅ {len(new_users)} utilisateur(s) ajouté(s) au groupe IAM")
            else:
                print(f"✅ Tous les super_admin sont déjà dans le groupe")
        else:
            print("⚠️ Groupe IAM 'grp.super_admin' non trouvé (optionnel)")
        
        # 5. Résumé
        print("\n" + "=" * 70)
        print(" ✅ CORRECTION TERMINÉE")
        print("=" * 70)
        print(f"\n📊 Résumé:")
        print(f"   ✓ Profil super_admin: {len(all_perm_ids)} permissions")
        print(f"   ✓ Utilisateurs super_admin: {len(super_admin_users)}")
        print(f"\n💡 Prochaines étapes:")
        print("   1. Reconnectez-vous à l'interface")
        print("   2. Vérifiez que toutes les pages IAM sont accessibles")
        print("   3. Les {len(all_perm_ids)} permissions devraient être visibles")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_superadmin())
