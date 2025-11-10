"""
Initialize MongoDB indexes for besoins system
Run this script once to create necessary indexes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def create_indexes():
    """Create indexes for besoins and audit_events collections"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "awana_jlc")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔧 Creating indexes for besoins collection...")
    
    # Besoins indexes
    await db.besoins.create_index("id", unique=True)
    await db.besoins.create_index("entreprise_id")
    await db.besoins.create_index("status")
    await db.besoins.create_index("created_at")
    await db.besoins.create_index([("entreprise_id", 1), ("status", 1)])
    await db.besoins.create_index([("entreprise_id", 1), ("created_at", -1)])
    await db.besoins.create_index([("status", 1), ("created_at", -1)])
    
    # Text search indexes
    await db.besoins.create_index([
        ("titre", "text"),
        ("description", "text")
    ])
    
    print("✅ Besoins indexes created")
    
    print("🔧 Creating indexes for besoin_comments collection...")
    
    # Besoin comments indexes
    await db.besoin_comments.create_index("id", unique=True)
    await db.besoin_comments.create_index("besoin_id")
    await db.besoin_comments.create_index([("besoin_id", 1), ("created_at", 1)])
    
    print("✅ Besoin comments indexes created")
    
    print("🔧 Creating indexes for audit_events collection...")
    
    # Audit events indexes (from audit_service)
    await db.audit_events.create_index("entity_type")
    await db.audit_events.create_index("entity_id")
    await db.audit_events.create_index([("entity_type", 1), ("entity_id", 1)])
    await db.audit_events.create_index("actor_id")
    await db.audit_events.create_index("action")
    await db.audit_events.create_index("created_at")
    await db.audit_events.create_index([("entity_type", 1), ("created_at", -1)])
    
    print("✅ Audit events indexes created")
    
    print("🔧 Creating indexes for missions collection (add besoin_id)...")
    
    # Add besoin_id index to missions
    await db.missions.create_index("besoin_id")
    
    print("✅ Missions indexes updated")
    
    print("\n✅ All indexes created successfully!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
