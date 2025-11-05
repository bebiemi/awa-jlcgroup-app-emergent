"""
Migration pour ajouter le système de feature flags
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/auth_db')


async def migrate():
    """Exécuter la migration"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🔄 Migration du système de Feature Flags")
    print("=" * 60)
    
    # 1. Créer les collections si elles n'existent pas
    collections = await db.list_collection_names()
    
    if "feature_flags" not in collections:
        await db.create_collection("feature_flags")
        print("✅ Collection 'feature_flags' créée")
    else:
        print("⏭️  Collection 'feature_flags' existe déjà")
    
    if "audit_events" not in collections:
        await db.create_collection("audit_events")
        print("✅ Collection 'audit_events' créée")
    else:
        print("⏭️  Collection 'audit_events' existe déjà")
    
    # 2. Créer les index
    print("\n📊 Création des index...")
    
    # Index sur feature_flags
    await db.feature_flags.create_index("key", unique=True)
    await db.feature_flags.create_index([("type", 1), ("target", 1)])
    await db.feature_flags.create_index("created_at")
    print("✅ Index sur 'feature_flags' créés")
    
    # Index sur audit_events
    await db.audit_events.create_index([("target_type", 1), ("target_id", 1)])
    await db.audit_events.create_index([("created_at", -1)])
    await db.audit_events.create_index("actor_id")
    print("✅ Index sur 'audit_events' créés")
    
    # 3. Ajouter is_hidden_from_admins aux rôles existants
    print("\n👥 Mise à jour des rôles...")
    
    # Vérifier si le champ existe déjà
    sample_role = await db.system_references.find_one({"category": "roles"})
    if sample_role and "is_hidden_from_admins" not in sample_role:
        # Mettre à jour tous les rôles
        result = await db.system_references.update_many(
            {"category": "roles"},
            {"$set": {"is_hidden_from_admins": False}}
        )
        print(f"✅ {result.modified_count} rôles mis à jour avec 'is_hidden_from_admins'")
        
        # Marquer super_admin comme caché
        result_super = await db.system_references.update_one(
            {"category": "roles", "code": "super_admin"},
            {"$set": {"is_hidden_from_admins": True}}
        )
        if result_super.modified_count > 0:
            print("✅ Rôle 'super_admin' marqué comme caché aux admins")
    else:
        print("⏭️  Les rôles ont déjà le champ 'is_hidden_from_admins'")
    
    # 4. Créer des feature flags par défaut (tous désactivés)
    print("\n🎌 Création des feature flags par défaut...")
    
    default_flags = [
        {
            "id": "flag_bulk_assign",
            "key": "feature.mission.bulk_assign",
            "type": "GLOBAL",
            "value": False,
            "target": None,
            "metadata": {
                "description": "Permet l'assignation groupée de missions",
                "rollout_percentage": 0,
                "tags": ["mission", "productivity"],
                "dependencies": []
            },
            "created_by": "system",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "flag_new_dashboard",
            "key": "feature.dashboard.v2",
            "type": "GLOBAL",
            "value": False,
            "target": None,
            "metadata": {
                "description": "Nouveau dashboard V2 avec analytics améliorés",
                "rollout_percentage": 0,
                "tags": ["ui", "dashboard"],
                "dependencies": []
            },
            "created_by": "system",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "flag_advanced_search",
            "key": "feature.search.advanced",
            "type": "GLOBAL",
            "value": False,
            "target": None,
            "metadata": {
                "description": "Recherche avancée avec filtres multiples",
                "rollout_percentage": 0,
                "tags": ["search", "ux"],
                "dependencies": []
            },
            "created_by": "system",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": "flag_export_csv",
            "key": "feature.export.csv",
            "type": "ROLE",
            "value": False,
            "target": "admin",
            "metadata": {
                "description": "Export CSV pour les admins",
                "rollout_percentage": 0,
                "tags": ["export", "admin"],
                "dependencies": []
            },
            "created_by": "system",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
    ]
    
    created_count = 0
    for flag in default_flags:
        existing = await db.feature_flags.find_one({"key": flag["key"]})
        if not existing:
            await db.feature_flags.insert_one(flag)
            created_count += 1
            print(f"  ✅ Flag '{flag['key']}' créé")
        else:
            print(f"  ⏭️  Flag '{flag['key']}' existe déjà")
    
    print(f"\n✅ {created_count} feature flags par défaut créés")
    
    # 5. Statistiques finales
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES FINALES")
    print("=" * 60)
    
    flag_count = await db.feature_flags.count_documents({})
    audit_count = await db.audit_events.count_documents({})
    role_count = await db.system_references.count_documents({"category": "roles"})
    hidden_role_count = await db.system_references.count_documents({
        "category": "roles",
        "is_hidden_from_admins": True
    })
    
    print(f"Feature Flags        : {flag_count}")
    print(f"Événements d'audit   : {audit_count}")
    print(f"Rôles totaux         : {role_count}")
    print(f"Rôles cachés         : {hidden_role_count}")
    
    print("\n✅ Migration terminée avec succès!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
