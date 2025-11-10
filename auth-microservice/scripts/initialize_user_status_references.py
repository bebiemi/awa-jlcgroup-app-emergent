"""
Initialize User Status References in Database
Adds standard user statuses to system_references if they don't exist
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/auth_db")

USER_STATUSES = [
    {
        "code": "active",
        "category": "user_statuses",
        "label_fr": "Actif",
        "label_en": "Active",
        "description": "Compte utilisateur actif",
        "order": 1,
        "is_active": True,
        "is_system": True,
        "metadata": {"color": "green", "icon": "check-circle"}
    },
    {
        "code": "pending",
        "category": "user_statuses",
        "label_fr": "En attente",
        "label_en": "Pending",
        "description": "Compte en attente de validation",
        "order": 2,
        "is_active": True,
        "is_system": True,
        "metadata": {"color": "yellow", "icon": "clock"}
    },
    {
        "code": "suspended",
        "category": "user_statuses",
        "label_fr": "Suspendu",
        "label_en": "Suspended",
        "description": "Compte temporairement suspendu",
        "order": 3,
        "is_active": True,
        "is_system": True,
        "metadata": {"color": "red", "icon": "ban"}
    },
    {
        "code": "archived",
        "category": "user_statuses",
        "label_fr": "Archivé",
        "label_en": "Archived",
        "description": "Compte archivé (suppression programmée)",
        "order": 4,
        "is_active": True,
        "is_system": True,
        "metadata": {"color": "orange", "icon": "archive-box"}
    },
    {
        "code": "blocked",
        "category": "user_statuses",
        "label_fr": "Bloqué",
        "label_en": "Blocked",
        "description": "Compte bloqué définitivement",
        "order": 5,
        "is_active": True,
        "is_system": True,
        "metadata": {"color": "red", "icon": "lock-closed"}
    },
    {
        "code": "deleted",
        "category": "user_statuses",
        "label_fr": "Supprimé",
        "label_en": "Deleted",
        "description": "Compte utilisateur supprimé",
        "order": 6,
        "is_active": True,
        "is_system": True,
        "metadata": {"color": "gray", "icon": "trash"}
    },
]


async def initialize_user_status_references():
    """Initialize user status references in database"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()
    
    print("🔄 Initializing User Status References...")
    print(f"📦 Database: {db.name}")
    print(f"📊 Statuses to initialize: {len(USER_STATUSES)}")
    
    created = 0
    updated = 0
    skipped = 0
    
    for status in USER_STATUSES:
        # Check if status already exists
        existing = await db.system_references.find_one({
            "code": status["code"],
            "category": "user_statuses"
        })
        
        if existing:
            # Update existing status
            result = await db.system_references.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        **status,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            if result.modified_count > 0:
                updated += 1
                print(f"   ✏️  Updated: {status['code']} - {status['label_fr']}")
            else:
                skipped += 1
                print(f"   ⏭️  Skipped (no changes): {status['code']}")
        else:
            # Create new status
            await db.system_references.insert_one({
                **status,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            created += 1
            print(f"   ✅ Created: {status['code']} - {status['label_fr']}")
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created}")
    print(f"   ✏️  Updated: {updated}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   📦 Total: {len(USER_STATUSES)}")
    
    # Verify
    total_in_db = await db.system_references.count_documents({"category": "user_statuses"})
    print(f"\n✅ Total user statuses in database: {total_in_db}")
    
    client.close()
    print("\n✅ User Status References initialized successfully!")


if __name__ == "__main__":
    asyncio.run(initialize_user_status_references())
