"""
Script to create profile for Google OAuth user
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

async def create_profile_for_user():
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    
    # Auth DB - where users are stored
    auth_db = client['auth_db']
    # JLC DB - where profiles are stored
    jlc_db = client['jlc_db']
    
    email = "brown.ebiemi@gmail.com"
    
    # Find user in auth_db
    user = await auth_db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ User {email} not found in auth_db")
        client.close()
        return
    
    user_id = user['id']
    print(f"✅ Found user: {user['full_name']} (ID: {user_id})")
    
    # Check if profile already exists
    existing_profile = await jlc_db.profiles.find_one({"user_id": user_id})
    
    if existing_profile:
        print(f"✅ Profile already exists for {email}")
        client.close()
        return
    
    # Create profile based on user role
    roles = user.get('roles', [])
    profile_type = roles[0] if roles else 'interim'  # Default to interim
    
    # Base profile data
    profile = {
        "user_id": user_id,
        "profile_type": profile_type,
        "first_name": user.get('full_name', '').split()[0] if user.get('full_name') else '',
        "last_name": ' '.join(user.get('full_name', '').split()[1:]) if user.get('full_name') else '',
        "email": user['email'],
        "phone": None,
        "avatar_url": None,
        "address": None,
        "city": None,
        "postal_code": None,
        "country": "France",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add role-specific fields
    if profile_type == 'interim':
        profile.update({
            "skills": [],
            "experience_years": 0,
            "availability": "available",
            "hourly_rate": None,
            "resume_url": None
        })
    elif profile_type == 'company':
        profile.update({
            "company_name": None,
            "siret": None,
            "industry": None,
            "company_size": None,
            "description": None,
            "website": None
        })
    elif profile_type in ['admin', 'super_admin']:
        profile.update({
            "department": "Administration",
            "position": "Administrator"
        })
    
    # Insert profile
    result = await jlc_db.profiles.insert_one(profile)
    
    print(f"✅ Profile created successfully for {email}")
    print(f"   Profile Type: {profile_type}")
    print(f"   Profile ID: {result.inserted_id}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_profile_for_user())
