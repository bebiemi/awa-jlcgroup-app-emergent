"""
Script to initialize default permissions and profiles in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "auth_db"

# Default permissions by module
DEFAULT_PERMISSIONS = [
    # Admin module
    {"name": "gestion_utilisateurs", "label": "Gestion des utilisateurs", "description": "Créer, modifier, supprimer des utilisateurs", "module": "admin"},
    {"name": "gestion_groupes", "label": "Gestion des groupes", "description": "Créer, modifier, supprimer des groupes", "module": "admin"},
    {"name": "gestion_profils", "label": "Gestion des profils", "description": "Créer, modifier, supprimer des profils de permissions", "module": "admin"},
    {"name": "voir_utilisateurs", "label": "Voir les utilisateurs", "description": "Consulter la liste des utilisateurs", "module": "admin"},
    
    # Validations module
    {"name": "voir_validations", "label": "Voir les validations", "description": "Consulter les demandes de validation", "module": "validations"},
    {"name": "approuver_validations", "label": "Approuver les validations", "description": "Approuver des demandes de validation", "module": "validations"},
    {"name": "rejeter_validations", "label": "Rejeter les validations", "description": "Rejeter des demandes de validation", "module": "validations"},
    
    # Intérimaires module
    {"name": "voir_interimaires", "label": "Voir les intérimaires", "description": "Consulter les profils intérimaires", "module": "interimaires"},
    {"name": "modifier_interimaires", "label": "Modifier les intérimaires", "description": "Modifier les profils intérimaires", "module": "interimaires"},
    {"name": "supprimer_interimaires", "label": "Supprimer les intérimaires", "description": "Supprimer des profils intérimaires", "module": "interimaires"},
    
    # Entreprises module
    {"name": "voir_entreprises", "label": "Voir les entreprises", "description": "Consulter les profils entreprises", "module": "entreprises"},
    {"name": "modifier_entreprises", "label": "Modifier les entreprises", "description": "Modifier les profils entreprises", "module": "entreprises"},
    {"name": "supprimer_entreprises", "label": "Supprimer les entreprises", "description": "Supprimer des profils entreprises", "module": "entreprises"},
    
    # Rapports module
    {"name": "voir_rapports", "label": "Voir les rapports", "description": "Consulter les rapports", "module": "rapports"},
    {"name": "exporter_rapports", "label": "Exporter les rapports", "description": "Exporter les rapports en PDF/Excel", "module": "rapports"},
    
    # Dashboard module
    {"name": "voir_dashboard", "label": "Voir le tableau de bord", "description": "Accès au tableau de bord", "module": "dashboard"},
    {"name": "voir_statistiques", "label": "Voir les statistiques", "description": "Consulter les statistiques détaillées", "module": "dashboard"},
]


async def init_permissions_and_profiles():
    """Initialize default permissions and profiles"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    permissions_collection = db["permissions"]
    profiles_collection = db["profiles"]
    
    print("🔧 Initializing permissions and profiles...")
    
    # Insert permissions
    permission_ids = {}
    for perm_data in DEFAULT_PERMISSIONS:
        # Check if permission already exists
        existing = await permissions_collection.find_one({"name": perm_data["name"]})
        if existing:
            permission_ids[perm_data["name"]] = existing["id"]
            print(f"  ✓ Permission '{perm_data['name']}' already exists")
        else:
            perm_id = str(uuid.uuid4())
            permission = {
                "id": perm_id,
                "name": perm_data["name"],
                "label": perm_data["label"],
                "description": perm_data["description"],
                "module": perm_data["module"],
                "created_at": datetime.now(timezone.utc)
            }
            await permissions_collection.insert_one(permission)
            permission_ids[perm_data["name"]] = perm_id
            print(f"  ✓ Created permission '{perm_data['name']}'")
    
    # Create default profiles
    default_profiles = [
        {
            "name": "Admin Complet",
            "description": "Accès complet à toutes les fonctionnalités",
            "permissions": list(permission_ids.values()),  # All permissions
            "is_system": True
        },
        {
            "name": "Lecture Seule",
            "description": "Accès en lecture seule sans modifications",
            "permissions": [
                permission_ids.get("voir_utilisateurs"),
                permission_ids.get("voir_validations"),
                permission_ids.get("voir_interimaires"),
                permission_ids.get("voir_entreprises"),
                permission_ids.get("voir_rapports"),
                permission_ids.get("voir_dashboard"),
            ],
            "is_system": True
        },
        {
            "name": "Gestionnaire RH",
            "description": "Gestion des intérimaires et validations",
            "permissions": [
                permission_ids.get("voir_utilisateurs"),
                permission_ids.get("voir_validations"),
                permission_ids.get("approuver_validations"),
                permission_ids.get("rejeter_validations"),
                permission_ids.get("voir_interimaires"),
                permission_ids.get("modifier_interimaires"),
                permission_ids.get("voir_dashboard"),
                permission_ids.get("voir_statistiques"),
            ],
            "is_system": True
        },
        {
            "name": "Gestionnaire Commercial",
            "description": "Gestion des entreprises et rapports",
            "permissions": [
                permission_ids.get("voir_entreprises"),
                permission_ids.get("modifier_entreprises"),
                permission_ids.get("voir_rapports"),
                permission_ids.get("exporter_rapports"),
                permission_ids.get("voir_dashboard"),
                permission_ids.get("voir_statistiques"),
            ],
            "is_system": True
        },
    ]
    
    for profile_data in default_profiles:
        # Check if profile already exists
        existing = await profiles_collection.find_one({"name": profile_data["name"]})
        if existing:
            print(f"  ✓ Profile '{profile_data['name']}' already exists")
        else:
            profile = {
                "id": str(uuid.uuid4()),
                "name": profile_data["name"],
                "description": profile_data["description"],
                "permissions": [p for p in profile_data["permissions"] if p],  # Filter None values
                "is_system": profile_data["is_system"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "created_by": None
            }
            await profiles_collection.insert_one(profile)
            print(f"  ✓ Created profile '{profile_data['name']}'")
    
    print("\n✅ Initialization complete!")
    client.close()


if __name__ == "__main__":
    asyncio.run(init_permissions_and_profiles())
