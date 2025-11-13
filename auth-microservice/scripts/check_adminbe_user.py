import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import sys

async def check_user():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        print(f"Connecting to MongoDB: {mongo_url}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        print("\n=== Searching for user 'adminbe' ===")
        user = await db.users.find_one({"username": "adminbe"})
        
        if user:
            print("\n✓ User found!")
            # Remove _id for display
            user_display = user.copy()
            user_display.pop('_id', None)
            
            print("\n=== User Document ===")
            print(json.dumps(user_display, indent=2, default=str))
            
            # Check critical fields
            print("\n=== Critical Fields Check ===")
            print(f"✓ username: {user.get('username')}")
            print(f"✓ email: {user.get('email')}")
            print(f"✓ provider: {user.get('provider')}")
            print(f"✓ is_active: {user.get('is_active')}")
            print(f"✓ is_verified: {user.get('is_verified')}")
            print(f"✓ password_hash exists: {'password_hash' in user}")
            print(f"✓ hashed_password exists: {'hashed_password' in user}")
            
            if 'password_hash' in user:
                print(f"✓ password_hash length: {len(user.get('password_hash', ''))}")
                print(f"✓ password_hash starts with: {user.get('password_hash', '')[:10]}...")
            
        else:
            print("\n✗ User 'adminbe' NOT FOUND in database!")
            
        client.close()
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_user())
