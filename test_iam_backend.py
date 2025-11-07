#!/usr/bin/env python3
"""
IAM Backend Testing
Comprehensive tests for Identity and Access Management system
"""

import requests
import json
import sys
from datetime import datetime

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"
IAM_BASE_URL = "http://localhost:8000/api/iam"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "awana2025"

# Global test data
test_data = {
    "admin_token": None,
    "created_permission_id": None,
    "created_profile_id": None,
    "created_group_id": None,
    "test_user_id": None,
    "system_profile_id": None,
    "system_group_id": None
}

# Test statistics
stats = {
    "total": 0,
    "passed": 0,
    "failed": 0
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_test(test_name, status, details=""):
    """Log test results with colors"""
    stats["total"] += 1
    if status == "PASS":
        stats["passed"] += 1
        color = Colors.GREEN
    elif status == "FAIL":
        stats["failed"] += 1
        color = Colors.RED
    else:
        color = Colors.YELLOW
    
    print(f"{color}[{status}]{Colors.ENDC} {test_name}")
    if details:
        print(f"    {details}")

def test_endpoint(method, url, data=None, headers=None, expected_status=200, test_name=""):
    """Generic endpoint testing function"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            log_test(test_name, "FAIL", f"Unsupported method: {method}")
            return None
        
        # Check status code
        if response.status_code != expected_status:
            log_test(test_name, "FAIL", 
                    f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:500]}")
            return None
        
        # Try to parse JSON
        try:
            json_response = response.json()
            log_test(test_name, "PASS", f"Status: {response.status_code}")
            return json_response
        except json.JSONDecodeError:
            if expected_status == 204:  # No content expected
                log_test(test_name, "PASS", f"Status: {response.status_code}")
                return {}
            log_test(test_name, "FAIL", f"Invalid JSON response: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        log_test(test_name, "FAIL", f"Request failed: {str(e)}")
        return None

def test_admin_login():
    """Test admin login and get access token"""
    print(f"\n{Colors.BOLD}=== 1. Admin Authentication ==={Colors.ENDC}")
    
    response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        test_name="Admin Login"
    )
    
    if response and "access_token" in response:
        test_data["admin_token"] = response["access_token"]
        print(f"    ✓ Admin token obtained")
        return True
    return False

def get_auth_headers():
    """Get authorization headers with admin token"""
    return {"Authorization": f"Bearer {test_data['admin_token']}"}

def test_permissions_management():
    """Test permissions CRUD operations"""
    print(f"\n{Colors.BOLD}=== 2. Permissions Management ==={Colors.ENDC}")
    
    # 2.1 List all permissions (authenticated)
    response = test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/permissions",
        headers=get_auth_headers(),
        test_name="List All Permissions (Authenticated)"
    )
    
    if response:
        print(f"    ✓ Found {len(response)} permissions")
        # Store a system permission ID for later tests
        if len(response) > 0:
            test_data["system_permission_id"] = response[0]["id"]
    
    # 2.2 List permissions without authentication (should fail)
    test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/permissions",
        expected_status=401,
        test_name="List Permissions (Unauthenticated - Should Fail)"
    )
    
    # 2.3 Create new permission (admin)
    new_permission = {
        "code": "test.custom.permission",
        "name": "Test Custom Permission",
        "description": "Permission created for testing",
        "resource": "test",
        "action": "execute",
        "scope": "organization",
        "category": "testing"
    }
    
    response = test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/permissions",
        data=new_permission,
        headers=get_auth_headers(),
        expected_status=201,
        test_name="Create New Permission (Admin)"
    )
    
    if response and "id" in response:
        test_data["created_permission_id"] = response["id"]
        print(f"    ✓ Permission created with ID: {response['id']}")
    
    # 2.4 Create duplicate permission (should fail)
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/permissions",
        data=new_permission,
        headers=get_auth_headers(),
        expected_status=400,
        test_name="Create Duplicate Permission (Should Fail)"
    )
    
    # 2.5 Create permission without authentication (should fail)
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/permissions",
        data=new_permission,
        expected_status=401,
        test_name="Create Permission (Unauthenticated - Should Fail)"
    )

def test_profiles_management():
    """Test profiles CRUD operations"""
    print(f"\n{Colors.BOLD}=== 3. Profiles Management ==={Colors.ENDC}")
    
    # 3.1 List all profiles
    response = test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/profiles",
        headers=get_auth_headers(),
        test_name="List All Profiles"
    )
    
    if response:
        print(f"    ✓ Found {len(response)} profiles")
        # Find a system profile for later tests
        for profile in response:
            if profile.get("is_system_role"):
                test_data["system_profile_id"] = profile["id"]
                test_data["system_profile_code"] = profile["code"]
                break
    
    # 3.2 Get specific profile details
    if test_data.get("system_profile_id"):
        response = test_endpoint(
            "GET",
            f"{IAM_BASE_URL}/profiles/{test_data['system_profile_id']}",
            headers=get_auth_headers(),
            test_name="Get Profile Details"
        )
        
        if response:
            print(f"    ✓ Profile: {response.get('name')}, Permissions: {len(response.get('permission_ids', []))}")
    
    # 3.3 Get non-existent profile (should fail)
    test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/profiles/non-existent-id",
        headers=get_auth_headers(),
        expected_status=404,
        test_name="Get Non-existent Profile (Should Fail)"
    )
    
    # 3.4 Create new profile
    new_profile = {
        "code": "test_custom_profile",
        "name": "Test Custom Profile",
        "description": "Profile created for testing",
        "permission_ids": [test_data.get("created_permission_id")] if test_data.get("created_permission_id") else [],
        "category": "custom",
        "color": "#FF5733",
        "icon": "test-icon"
    }
    
    response = test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/profiles",
        data=new_profile,
        headers=get_auth_headers(),
        expected_status=201,
        test_name="Create New Profile (Admin)"
    )
    
    if response and "id" in response:
        test_data["created_profile_id"] = response["id"]
        print(f"    ✓ Profile created with ID: {response['id']}")
    
    # 3.5 Create duplicate profile (should fail)
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/profiles",
        data=new_profile,
        headers=get_auth_headers(),
        expected_status=400,
        test_name="Create Duplicate Profile (Should Fail)"
    )
    
    # 3.6 Update profile
    if test_data.get("created_profile_id"):
        update_data = {
            "name": "Updated Test Profile",
            "description": "Updated description"
        }
        
        response = test_endpoint(
            "PUT",
            f"{IAM_BASE_URL}/profiles/{test_data['created_profile_id']}",
            data=update_data,
            headers=get_auth_headers(),
            test_name="Update Profile (Admin)"
        )
        
        if response:
            print(f"    ✓ Profile updated: {response.get('name')}")
    
    # 3.7 Try to update protected system profile (should fail)
    if test_data.get("system_profile_id"):
        test_endpoint(
            "PUT",
            f"{IAM_BASE_URL}/profiles/{test_data['system_profile_id']}",
            data={"name": "Hacked Profile"},
            headers=get_auth_headers(),
            expected_status=403,
            test_name="Update Protected Profile (Should Fail)"
        )
    
    # 3.8 List profiles without authentication (should fail)
    test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/profiles",
        expected_status=401,
        test_name="List Profiles (Unauthenticated - Should Fail)"
    )

def test_groups_management():
    """Test groups CRUD operations"""
    print(f"\n{Colors.BOLD}=== 4. Groups Management ==={Colors.ENDC}")
    
    # 4.1 List all groups
    response = test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/groups",
        headers=get_auth_headers(),
        test_name="List All Groups"
    )
    
    if response:
        print(f"    ✓ Found {len(response)} groups")
        # Find a system group for later tests
        for group in response:
            if group.get("is_system_group"):
                test_data["system_group_id"] = group["id"]
                break
    
    # 4.2 Get specific group details
    if test_data.get("system_group_id"):
        response = test_endpoint(
            "GET",
            f"{IAM_BASE_URL}/groups/{test_data['system_group_id']}",
            headers=get_auth_headers(),
            test_name="Get Group Details"
        )
        
        if response:
            print(f"    ✓ Group: {response.get('name')}, Members: {len(response.get('user_ids', []))}")
    
    # 4.3 Create new group
    new_group = {
        "code": "test_custom_group",
        "name": "Test Custom Group",
        "description": "Group created for testing",
        "profile_ids": [test_data.get("created_profile_id")] if test_data.get("created_profile_id") else []
    }
    
    response = test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/groups",
        data=new_group,
        headers=get_auth_headers(),
        expected_status=201,
        test_name="Create New Group (Admin)"
    )
    
    if response and "id" in response:
        test_data["created_group_id"] = response["id"]
        print(f"    ✓ Group created with ID: {response['id']}")
    
    # 4.4 Create duplicate group (should fail)
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/groups",
        data=new_group,
        headers=get_auth_headers(),
        expected_status=400,
        test_name="Create Duplicate Group (Should Fail)"
    )
    
    # 4.5 Update group
    if test_data.get("created_group_id"):
        update_data = {
            "name": "Updated Test Group",
            "description": "Updated group description"
        }
        
        response = test_endpoint(
            "PUT",
            f"{IAM_BASE_URL}/groups/{test_data['created_group_id']}",
            data=update_data,
            headers=get_auth_headers(),
            test_name="Update Group (Admin)"
        )
        
        if response:
            print(f"    ✓ Group updated: {response.get('name')}")
    
    # 4.6 Try to update protected system group (should fail)
    if test_data.get("system_group_id"):
        test_endpoint(
            "PUT",
            f"{IAM_BASE_URL}/groups/{test_data['system_group_id']}",
            data={"name": "Hacked Group"},
            headers=get_auth_headers(),
            expected_status=403,
            test_name="Update Protected Group (Should Fail)"
        )
    
    # 4.7 Get non-existent group (should fail)
    test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/groups/non-existent-id",
        headers=get_auth_headers(),
        expected_status=404,
        test_name="Get Non-existent Group (Should Fail)"
    )

def test_user_assignments():
    """Test user profile and group assignments"""
    print(f"\n{Colors.BOLD}=== 5. User Assignments ==={Colors.ENDC}")
    
    # First, get a test user ID (use admin user for testing)
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/auth/me",
        headers=get_auth_headers(),
        test_name="Get Current User Info"
    )
    
    if response and "id" in response:
        test_data["test_user_id"] = response["id"]
        print(f"    ✓ Using user ID: {response['id']}")
    
    if not test_data.get("test_user_id"):
        print(f"{Colors.RED}    ✗ Cannot proceed without user ID{Colors.ENDC}")
        return
    
    # 5.1 Assign profiles to user
    if test_data.get("created_profile_id"):
        assignment_data = {
            "user_id": test_data["test_user_id"],
            "profile_ids": [test_data["created_profile_id"]]
        }
        
        response = test_endpoint(
            "POST",
            f"{IAM_BASE_URL}/users/{test_data['test_user_id']}/profiles",
            data=assignment_data,
            headers=get_auth_headers(),
            test_name="Assign Profiles to User"
        )
        
        if response:
            print(f"    ✓ Profiles assigned successfully")
    
    # 5.2 Assign groups to user
    if test_data.get("created_group_id"):
        assignment_data = {
            "user_id": test_data["test_user_id"],
            "group_ids": [test_data["created_group_id"]]
        }
        
        response = test_endpoint(
            "POST",
            f"{IAM_BASE_URL}/users/{test_data['test_user_id']}/groups",
            data=assignment_data,
            headers=get_auth_headers(),
            test_name="Assign Groups to User"
        )
        
        if response:
            print(f"    ✓ Groups assigned successfully")
    
    # 5.3 Get user's effective permissions
    response = test_endpoint(
        "GET",
        f"{IAM_BASE_URL}/users/{test_data['test_user_id']}/permissions",
        headers=get_auth_headers(),
        test_name="Get User's Effective Permissions"
    )
    
    if response:
        print(f"    ✓ Direct Profiles: {len(response.get('direct_profiles', []))}")
        print(f"    ✓ Group Profiles: {len(response.get('group_profiles', []))}")
        print(f"    ✓ Total Permissions: {len(response.get('all_permissions', []))}")
        print(f"    ✓ Groups: {len(response.get('groups', []))}")
    
    # 5.4 Try to assign non-existent profile (should fail)
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/users/{test_data['test_user_id']}/profiles",
        data={"user_id": test_data["test_user_id"], "profile_ids": ["non-existent-id"]},
        headers=get_auth_headers(),
        expected_status=400,
        test_name="Assign Non-existent Profile (Should Fail)"
    )
    
    # 5.5 Try to assign to non-existent user (should fail)
    if test_data.get("created_profile_id"):
        test_endpoint(
            "POST",
            f"{IAM_BASE_URL}/users/non-existent-user/profiles",
            data={"user_id": "non-existent-user", "profile_ids": [test_data["created_profile_id"]]},
            headers=get_auth_headers(),
            expected_status=404,
            test_name="Assign Profile to Non-existent User (Should Fail)"
        )

def test_permission_checks():
    """Test permission checking functionality"""
    print(f"\n{Colors.BOLD}=== 6. Permission Checks ==={Colors.ENDC}")
    
    if not test_data.get("test_user_id"):
        print(f"{Colors.RED}    ✗ Cannot proceed without user ID{Colors.ENDC}")
        return
    
    # 6.1 Check if user has a permission they should have
    check_data = {
        "user_id": test_data["test_user_id"],
        "permission_code": "users.read"
    }
    
    response = test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/check-permission",
        data=check_data,
        headers=get_auth_headers(),
        test_name="Check Permission (User Has)"
    )
    
    if response:
        print(f"    ✓ Has Permission: {response.get('has_permission')}")
        print(f"    ✓ Granted By: {response.get('granted_by', [])}")
    
    # 6.2 Check if user has a permission they don't have
    check_data = {
        "user_id": test_data["test_user_id"],
        "permission_code": "nonexistent.permission"
    }
    
    response = test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/check-permission",
        data=check_data,
        headers=get_auth_headers(),
        test_name="Check Permission (User Doesn't Have)"
    )
    
    if response:
        print(f"    ✓ Has Permission: {response.get('has_permission')}")
        print(f"    ✓ Reason: {response.get('reason')}")

def test_data_validation():
    """Test data validation rules"""
    print(f"\n{Colors.BOLD}=== 7. Data Validation ==={Colors.ENDC}")
    
    # 7.1 Create profile with invalid permission ID (should fail)
    invalid_profile = {
        "code": "invalid_profile_test",
        "name": "Invalid Profile",
        "permission_ids": ["invalid-permission-id"]
    }
    
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/profiles",
        data=invalid_profile,
        headers=get_auth_headers(),
        expected_status=400,
        test_name="Create Profile with Invalid Permission (Should Fail)"
    )
    
    # 7.2 Create group with invalid profile ID (should fail)
    invalid_group = {
        "code": "invalid_group_test",
        "name": "Invalid Group",
        "profile_ids": ["invalid-profile-id"]
    }
    
    test_endpoint(
        "POST",
        f"{IAM_BASE_URL}/groups",
        data=invalid_group,
        headers=get_auth_headers(),
        expected_status=400,
        test_name="Create Group with Invalid Profile (Should Fail)"
    )
    
    # 7.3 Try to delete protected system profile (should fail)
    if test_data.get("system_profile_id"):
        test_endpoint(
            "DELETE",
            f"{IAM_BASE_URL}/profiles/{test_data['system_profile_id']}",
            headers=get_auth_headers(),
            expected_status=403,
            test_name="Delete Protected System Profile (Should Fail)"
        )
    
    # 7.4 Try to delete protected system group (should fail)
    if test_data.get("system_group_id"):
        test_endpoint(
            "DELETE",
            f"{IAM_BASE_URL}/groups/{test_data['system_group_id']}",
            headers=get_auth_headers(),
            expected_status=403,
            test_name="Delete Protected System Group (Should Fail)"
        )

def test_cleanup():
    """Clean up test data"""
    print(f"\n{Colors.BOLD}=== 8. Cleanup Test Data ==={Colors.ENDC}")
    
    # Delete test group
    if test_data.get("created_group_id"):
        response = test_endpoint(
            "DELETE",
            f"{IAM_BASE_URL}/groups/{test_data['created_group_id']}",
            headers=get_auth_headers(),
            test_name="Delete Test Group"
        )
    
    # Delete test profile
    if test_data.get("created_profile_id"):
        response = test_endpoint(
            "DELETE",
            f"{IAM_BASE_URL}/profiles/{test_data['created_profile_id']}",
            headers=get_auth_headers(),
            test_name="Delete Test Profile"
        )
    
    # Delete test permission
    if test_data.get("created_permission_id"):
        response = test_endpoint(
            "DELETE",
            f"{IAM_BASE_URL}/permissions/{test_data['created_permission_id']}",
            headers=get_auth_headers(),
            test_name="Delete Test Permission"
        )

def verify_mongodb_data():
    """Verify data in MongoDB collections"""
    print(f"\n{Colors.BOLD}=== 9. MongoDB Data Verification ==={Colors.ENDC}")
    
    try:
        from pymongo import MongoClient
        import os
        
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        db = client.auth_db
        
        # Check permissions collection
        perm_count = db.permissions.count_documents({})
        log_test("MongoDB: Permissions Collection", "PASS", f"Found {perm_count} permissions")
        
        # Check profiles collection
        profile_count = db.profiles.count_documents({})
        log_test("MongoDB: Profiles Collection", "PASS", f"Found {profile_count} profiles")
        
        # Check groups collection
        group_count = db.groups.count_documents({})
        log_test("MongoDB: Groups Collection", "PASS", f"Found {group_count} groups")
        
        # Check if users have IAM fields
        user_with_iam = db.users.find_one({"profile_ids": {"$exists": True}})
        if user_with_iam:
            log_test("MongoDB: User IAM Fields", "PASS", "Users have profile_ids and group_ids fields")
        else:
            log_test("MongoDB: User IAM Fields", "FAIL", "Users missing IAM fields")
        
        client.close()
        
    except Exception as e:
        log_test("MongoDB Verification", "FAIL", f"Error: {str(e)}")

def print_summary():
    """Print test summary"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"Total Tests: {stats['total']}")
    print(f"{Colors.GREEN}Passed: {stats['passed']}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {stats['failed']}{Colors.ENDC}")
    
    if stats['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
    
    success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

def main():
    """Main test execution"""
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}IAM BACKEND COMPREHENSIVE TESTING{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"Auth Service: {AUTH_BASE_URL}")
    print(f"IAM Endpoints: {IAM_BASE_URL}")
    print(f"Admin User: {ADMIN_USERNAME}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests in sequence
    if not test_admin_login():
        print(f"\n{Colors.RED}❌ Admin login failed. Cannot proceed with tests.{Colors.ENDC}")
        return 1
    
    test_permissions_management()
    test_profiles_management()
    test_groups_management()
    test_user_assignments()
    test_permission_checks()
    test_data_validation()
    test_cleanup()
    verify_mongodb_data()
    
    print_summary()
    
    return 0 if stats['failed'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
