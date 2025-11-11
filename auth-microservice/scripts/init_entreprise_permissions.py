"""
Script pour initialiser les permissions entreprises et les assigner aux profils
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid


async def init_entreprise_permissions():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # Permissions entreprises à créer
    permissions_data = [
        {
            "code": "entreprises.create",
            "resource": "entreprises",
            "action": "CREATE",
            "scope": "all",
            "name": {
                "fr": "Créer une entreprise",
                "en": "Create a company"
            },
            "description": {
                "fr": "Permet de créer de nouvelles entreprises",
                "en": "Allows creating new companies"
            }
        },
        {
            "code": "entreprises.read",
            "resource": "entreprises",
            "action": "READ",
            "scope": "own",
            "name": {
                "fr": "Consulter les entreprises",
                "en": "View companies"
            },
            "description": {
                "fr": "Permet de consulter les informations des entreprises",
                "en": "Allows viewing company information"
            }
        },
        {
            "code": "entreprises.edit",
            "resource": "entreprises",
            "action": "EDIT",
            "scope": "own",
            "name": {
                "fr": "Modifier une entreprise",
                "en": "Edit a company"
            },
            "description": {
                "fr": "Permet de modifier les informations d'une entreprise",
                "en": "Allows editing company information"
            }
        },
        {
            "code": "entreprises.delete",
            "resource": "entreprises",
            "action": "DELETE",
            "scope": "all",
            "name": {
                "fr": "Supprimer une entreprise",
                "en": "Delete a company"
            },
            "description": {
                "fr": "Permet de supprimer une entreprise (soft delete)",
                "en": "Allows deleting a company (soft delete)"
            }
        }
    ]
    
    created_permissions = {}
    
    for perm_data in permissions_data:
        code = perm_data["code"]
        existing = await db.permissions.find_one({"code": code})
        
        if not existing:
            perm_id = str(uuid.uuid4())
            perm_doc = {
                "id": perm_id,
                **perm_data,
                "is_system": True,
                "created_at": datetime.now(timezone.utc)
            }
            await db.permissions.insert_one(perm_doc)
            print(f"✅ Permission créée: {code}")
            created_permissions[code] = perm_id
        else:
            perm_id = existing['id']
            print(f"✓ Permission existante: {code}")
            created_permissions[code] = perm_id
    
    # Assigner aux profils
    profile_permissions = {
        'entreprise': [
            'entreprises.read',   # Peut lire sa propre entreprise
            'entreprises.edit',   # Peut modifier sa propre entreprise
        ],
        'company_admin': [
            'entreprises.read',
            'entreprises.edit',
        ],
        'admin': [
            'entreprises.create',
            'entreprises.read',
            'entreprises.edit',
            'entreprises.delete',
        ],
        'super_admin': [
            'entreprises.create',
            'entreprises.read',
            'entreprises.edit',
            'entreprises.delete',
        ]
    }
    
    for profile_code, permission_codes in profile_permissions.items():
        profile = await db.profiles.find_one({"code": profile_code})
        if profile:
            # Get permission IDs
            perm_ids = [created_permissions[code] for code in permission_codes if code in created_permissions]
            
            # Add to existing permissions
            current_perms = profile.get('permission_ids', [])
            new_perms = list(set(current_perms + perm_ids))
            
            result = await db.profiles.update_one(
                {"id": profile['id']},
                {"$set": {"permission_ids": new_perms}}
            )
            
            if result.modified_count > 0:
                print(f"  ✅ Profil '{profile_code}': {len(perm_ids)} permissions ajoutées")
            else:
                print(f"  ✓ Profil '{profile_code}': permissions déjà présentes")
        else:
            print(f"  ⚠️  Profil '{profile_code}' non trouvé")
    
    print(f"\n📊 Résumé:")
    print(f"  - {len(created_permissions)} permissions configurées")
    print(f"  - {len(profile_permissions)} profils mis à jour")
    
    client.close()
    print("\n✅ Initialisation des permissions entreprises complète!")


if __name__ == "__main__":
    asyncio.run(init_entreprise_permissions())
