#!/usr/bin/env python3
"""
Script de test détaillé pour la connexion locale
Exécute dans le conteneur Docker pour tester la connexion
"""
import asyncio
import sys
import os
import json
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

async def test_login():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        print(f"🔌 Connecting to MongoDB: {mongo_url}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        username = "adminbe"
        password = "Awana2025!"
        
        print(f"\n🔍 Searching for user: {username}")
        
        # Test 1: Find user by username
        user_doc = await db.users.find_one({
            "$or": [
                {"username": username},
                {"email": username}
            ],
            "provider": "local"
        }, {"_id": 0})
        
        print(f"\n👤 User found: {bool(user_doc)}")
        
        if not user_doc:
            print("\n❌ ERROR: User not found in database!")
            print("\n🔍 Listing all users:")
            all_users = await db.users.find({}, {"_id": 0, "username": 1, "email": 1, "provider": 1}).to_list(10)
            for u in all_users:
                print(f"  - {u}")
            sys.exit(1)
        
        print("\n=== USER DOCUMENT ===")
        print(json.dumps(user_doc, indent=2, default=str))
        
        # Test 2: Check critical fields
        print("\n=== CRITICAL FIELDS ===")
        print(f"✓ username: {user_doc.get('username')}")
        print(f"✓ email: {user_doc.get('email')}")
        print(f"✓ provider: {user_doc.get('provider')}")
        print(f"✓ status: {user_doc.get('status')}")
        print(f"✓ is_active: {user_doc.get('is_active')}")
        print(f"✓ is_verified: {user_doc.get('is_verified')}")
        print(f"✓ password_hash exists: {'password_hash' in user_doc}")
        print(f"✓ hashed_password exists: {'hashed_password' in user_doc}")
        
        # Test 3: Check password hash
        password_hash_key = None
        if 'password_hash' in user_doc:
            password_hash_key = 'password_hash'
        elif 'hashed_password' in user_doc:
            password_hash_key = 'hashed_password'
        
        if not password_hash_key:
            print("\n❌ ERROR: No password hash field found!")
            sys.exit(1)
        
        password_hash = user_doc[password_hash_key]
        print(f"\n🔐 Password hash field: {password_hash_key}")
        print(f"🔐 Password hash length: {len(password_hash)}")
        print(f"🔐 Password hash prefix: {password_hash[:10]}...")
        
        # Test 4: Verify password with bcrypt
        print(f"\n🧪 Testing password verification...")
        try:
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
            print(f"✅ Password verification result: {password_valid}")
            
            if not password_valid:
                print("\n❌ Password verification FAILED!")
                print("This means the password hash in the database doesn't match the password.")
            else:
                print("\n✅ Password verification SUCCESS!")
                
                # Test 5: Check status
                user_status = user_doc.get('status')
                print(f"\n📊 Checking user status...")
                print(f"Current status: {user_status}")
                print(f"Expected status: 'active'")
                
                if user_status != 'active':
                    print(f"\n⚠️ WARNING: User status is '{user_status}', not 'active'!")
                    print("The API will reject login for non-active users.")
                else:
                    print("\n✅ User status is ACTIVE - login should work!")
                    print("\n🎯 SUMMARY: All checks passed! Login should work.")
                    print("If login still fails, the issue is in the API logic.")
        
        except Exception as e:
            print(f"\n❌ Password verification error: {e}")
            import traceback
            traceback.print_exc()
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_login())
