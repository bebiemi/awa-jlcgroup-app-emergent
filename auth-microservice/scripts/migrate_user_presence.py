"""
Migration script to add presence/status fields to existing users
Run this script to update the database schema for existing users
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def migrate_users():
    """Add presence fields to all existing users"""
    
    # Get MongoDB connection string from environment
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    users_collection = db.users
    
    print("🔄 Starting user presence field migration...")
    
    # Count users without presence fields
    users_without_presence = await users_collection.count_documents({
        "presence_status": {"$exists": False}
    })
    
    print(f"📊 Found {users_without_presence} users to update")
    
    if users_without_presence == 0:
        print("✅ All users already have presence fields")
        return
    
    # Update all users without presence fields
    now = datetime.now(timezone.utc)
    
    result = await users_collection.update_many(
        {"presence_status": {"$exists": False}},
        {
            "$set": {
                "presence_status": "online",
                "presence_updated_at": now,
                "last_activity_at": now
            }
        }
    )
    
    print(f"✅ Updated {result.modified_count} users with presence fields")
    
    # Verify
    total_users = await users_collection.count_documents({})
    users_with_presence = await users_collection.count_documents({
        "presence_status": {"$exists": True}
    })
    
    print(f"\n📈 Migration Summary:")
    print(f"   Total users: {total_users}")
    print(f"   Users with presence fields: {users_with_presence}")
    print(f"   Migration complete: {'✅' if total_users == users_with_presence else '❌'}")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    print("=" * 60)
    print("User Presence Fields Migration")
    print("=" * 60)
    asyncio.run(migrate_users())
