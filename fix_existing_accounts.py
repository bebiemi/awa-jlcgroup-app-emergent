#!/usr/bin/env python3
"""
Fix existing test accounts by updating password hash field name
"""

import requests
import json
from pymongo import MongoClient
import os
import bcrypt

# MongoDB connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
AUTH_BASE_URL = "http://localhost:8000/api"

def get_admin_token():
    """Get admin token"""
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/local/login",
            json={"username": "admin", "password": "awana2025"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Admin login error: {e}")
        return None

def fix_password_hashes():
    """Fix password hash field names in MongoDB"""
    print("Fixing password hash field names in MongoDB...")
    
    try:
        client = MongoClient(MONGO_URL)
        db = client['auth_db']
        users_collection = db.users
        
        # Find users with hashed_password field but no password_hash field
        users_to_fix = users_collection.find({
            "hashed_password": {"$exists": True},
            "password_hash": {"$exists": False}
        })
        
        fixed_count = 0
        for user in users_to_fix:
            # Copy hashed_password to password_hash and remove hashed_password
            result = users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {"password_hash": user["hashed_password"]},
                    "$unset": {"hashed_password": ""}
                }
            )
            
            if result.modified_count > 0:
                fixed_count += 1
                print(f"  Fixed user: {user.get('email', user.get('username', 'Unknown'))}")
        
        client.close()
        print(f"Fixed {fixed_count} users")
        return fixed_count > 0
        
    except Exception as e:
        print(f"Error fixing password hashes: {e}")
        return False

def test_login(username, password, account_name):
    """Test login for a specific account"""
    print(f"\nTesting login for {account_name}:")
    print(f"  Username: {username}")
    
    try:
        response = requests.post(
            f"{AUTH_BASE_URL}/auth/local/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Login successful!")
            user = data.get('user', {})
            print(f"  User ID: {user.get('id', 'Unknown')}")
            print(f"  Email: {user.get('email', 'Unknown')}")
            print(f"  Roles: {user.get('roles', [])}")
            return True
        else:
            print(f"  ❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Request failed: {str(e)}")
        return False

def main():
    print("Fixing existing test accounts password hash field names")
    
    # Step 1: Fix password hash field names
    if fix_password_hashes():
        print("\n✅ Password hash fields fixed successfully")
    else:
        print("\n❌ Failed to fix password hash fields")
        return False
    
    # Step 2: Test logins
    print("\nTesting logins after fix...")
    
    accounts = [
        ("entreprise_test", "Entreprise2025!", "Company Account"),
        ("commercial_test", "Commercial2025!", "Commercial Account"),
        ("interim_test2", "Interim2025!", "Second Interim Account")
    ]
    
    success_count = 0
    for username, password, name in accounts:
        if test_login(username, password, name):
            success_count += 1
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Successful logins: {success_count}/{len(accounts)}")
    
    if success_count == len(accounts):
        print("✅ All test accounts are now working!")
        
        # Print summary
        print(f"\n=== TEST ACCOUNT CREDENTIALS ===")
        for username, password, name in accounts:
            print(f"{name}: {username} / {password}")
        
        return True
    else:
        print("❌ Some accounts still cannot login")
        return False

if __name__ == "__main__":
    main()