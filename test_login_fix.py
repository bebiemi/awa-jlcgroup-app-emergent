#!/usr/bin/env python3
"""
Test login for existing accounts after password hash field fix
"""

import requests
import json

AUTH_BASE_URL = "http://localhost:8000/api"

def test_login(username, password, account_name):
    """Test login for a specific account"""
    print(f"\nTesting login for {account_name}:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    
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
            print(f"  Access Token: {data.get('access_token', '')[:20]}...")
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
    print("Testing login for created test accounts after password hash fix")
    
    # Test accounts that were created
    accounts = [
        ("entreprise_test", "Entreprise2025!", "Company Account"),
        ("commercial_test", "Commercial2025!", "Commercial Account"),
        ("interim_test2", "Interim2025!", "Second Interim Account")
    ]
    
    success_count = 0
    for username, password, name in accounts:
        if test_login(username, password, name):
            success_count += 1
    
    print(f"\n=== RESULTS ===")
    print(f"Successful logins: {success_count}/{len(accounts)}")
    
    if success_count == len(accounts):
        print("✅ All accounts can login successfully!")
        return True
    else:
        print("❌ Some accounts still cannot login")
        return False

if __name__ == "__main__":
    main()