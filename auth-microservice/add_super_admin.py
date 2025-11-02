"""
Script to add brown.ebiemi@gmail.com as super admin
Run this after Google OAuth authentication
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def add_super_admin():
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    email = "brown.ebiemi@gmail.com"
    
    # Find user by email
    user = await db.users.find_one({"email": email})
    
    if user:
        # Update user to have admin and super_admin roles
        result = await db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "roles": ["admin", "super_admin"],
                    "status": "active"
                }
            }
        )
        
        print(f"✅ User {email} updated successfully!")
        print(f"   Roles: admin, super_admin")
        print(f"   Status: active")
        print(f"   User ID: {user['id']}")
    else:
        print(f"❌ User {email} not found in database")
        print("   Please log in with Google first to create the account")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_super_admin())
