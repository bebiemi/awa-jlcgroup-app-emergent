#!/usr/bin/env python3
"""
IAM Migration Backend Testing
Comprehensive tests for permission-based access control system
"""

import requests
import json
import sys
import os
from datetime import datetime

# Test configuration
AUTH_BASE_URL = "http://localhost:8000"
API_BASE_URL = "http://localhost:8001/api"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "awana2025"

# Global test data
test_data = {
    "admin_token": None,
    "admin_user_id": None,
    "test_user_id": None,
    "test_user_token": None,
    "interim_user_id": None,
    "interim_token": None
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
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
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
        
        if response.status_code == expected_status:
            log_test(test_name, "PASS", f"Status: {response.status_code}")
            return response
        else:
            log_test(test_name, "FAIL", f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        log_test(test_name, "FAIL", f"Exception: {str(e)}")
        return None

def login_admin():
    """Login as admin and store token"""
    print(f"\n{Colors.BOLD}=== Admin Login ==={Colors.ENDC}")
    
    response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/auth/local/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        expected_status=200,
        test_name="Admin Login"
    )
    
    if response:
        data = response.json()
        test_data["admin_token"] = data.get("access_token")
        test_data["admin_user_id"] = data.get("user", {}).get("id")
        print(f"    Admin User ID: {test_data['admin_user_id']}")
        return True
    return False

def get_auth_headers(token=None):
    """Get authorization headers"""
    if token is None:
        token = test_data["admin_token"]
    return {"Authorization": f"Bearer {token}"}

# ===== User Management Routes Tests =====

def test_user_management_routes():
    """Test user management endpoints with permission checks"""
    print(f"\n{Colors.BOLD}=== User Management Routes (awana_auth_routes.py) ==={Colors.ENDC}")
    
    # 1. GET /auth/users → users.read permission
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth/users",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /auth/users (users.read permission)"
    )
    if response:
        users = response.json()
        print(f"    Found {len(users)} users")
        if len(users) > 0:
            test_data["test_user_id"] = users[0].get("id")
    
    # 2. GET /auth/users/{id} → users.read permission
    if test_data.get("test_user_id"):
        test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/api/auth/users/{test_data['test_user_id']}",
            headers=get_auth_headers(),
            expected_status=200,
            test_name="GET /auth/users/{id} (users.read permission)"
        )
    
    # 3. PUT /auth/users/{id} → users.edit permission
    if test_data.get("test_user_id"):
        test_endpoint(
            "PUT",
            f"{AUTH_BASE_URL}/api/auth/users/{test_data['test_user_id']}",
            data={"full_name": "Test User Updated"},
            headers=get_auth_headers(),
            expected_status=200,
            test_name="PUT /auth/users/{id} (users.edit permission)"
        )
    
    # 4. PATCH /auth/users/{id}/status → users.manage_status permission
    if test_data.get("test_user_id"):
        test_endpoint(
            "PATCH",
            f"{AUTH_BASE_URL}/api/auth/users/{test_data['test_user_id']}/status",
            data={"status": "active", "reason": "Test status update"},
            headers=get_auth_headers(),
            expected_status=200,
            test_name="PATCH /auth/users/{id}/status (users.manage_status permission)"
        )
    
    # 5. GET /auth/admin/stats → admin.dashboard permission
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth/admin/stats",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /auth/admin/stats (admin.dashboard permission)"
    )
    
    # 6. POST /auth/admin/users/{id}/mfa/reset → users.reset_mfa permission
    if test_data.get("test_user_id"):
        test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/api/auth/admin/users/{test_data['test_user_id']}/mfa/reset",
            headers=get_auth_headers(),
            expected_status=200,
            test_name="POST /auth/admin/users/{id}/mfa/reset (users.reset_mfa permission)"
        )

# ===== Email Routes Tests =====

def test_email_routes():
    """Test email management endpoints with permission checks"""
    print(f"\n{Colors.BOLD}=== Email Routes (email_settings, templates, history) ==={Colors.ENDC}")
    
    # 1. GET /api/emails/settings → emails.read_config permission
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/emails/settings",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /api/emails/settings (emails.read_config permission)"
    )
    
    # 2. PUT /api/emails/settings → emails.configure permission
    test_endpoint(
        "PUT",
        f"{AUTH_BASE_URL}/api/emails/settings",
        data={
            "smtp_host": "smtp.test.com",
            "smtp_port": 587,
            "smtp_user": "test@test.com",
            "smtp_password": "testpass",
            "from_email": "noreply@test.com",
            "from_name": "Test System"
        },
        headers=get_auth_headers(),
        expected_status=200,
        test_name="PUT /api/emails/settings (emails.configure permission)"
    )
    
    # 3. POST /api/emails/settings/test → emails.test permission
    test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/emails/settings/test",
        data={"recipient": "test@example.com"},
        headers=get_auth_headers(),
        expected_status=200,
        test_name="POST /api/emails/settings/test (emails.test permission)"
    )
    
    # 4. GET /api/emails/templates → emails.manage_templates permission
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/emails/templates",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /api/emails/templates (emails.manage_templates permission)"
    )
    
    # 5. POST /api/emails/templates → emails.manage_templates permission
    test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/emails/templates",
        data={
            "name": "test_template",
            "subject": "Test Subject",
            "body_html": "<p>Test body</p>",
            "body_text": "Test body"
        },
        headers=get_auth_headers(),
        expected_status=201,
        test_name="POST /api/emails/templates (emails.manage_templates permission)"
    )
    
    # 6. GET /api/emails/history → emails.read_history permission
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/emails/history",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /api/emails/history (emails.read_history permission)"
    )

# ===== Validation Routes Tests =====

def test_validation_routes():
    """Test validation endpoints with permission checks"""
    print(f"\n{Colors.BOLD}=== Validation Routes (validation_routes.py) ==={Colors.ENDC}")
    
    # 1. GET /validations → validations.manage permission
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/validations",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /validations (validations.manage permission)"
    )
    
    validation_id = None
    if response:
        validations = response.json()
        print(f"    Found {len(validations)} validations")
        if len(validations) > 0:
            validation_id = validations[0].get("id")
    
    # 2. POST /validations/{id}/approve → validations.manage permission
    if validation_id:
        test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/validations/{validation_id}/approve",
            data={"comments": "Test approval"},
            headers=get_auth_headers(),
            expected_status=200,
            test_name="POST /validations/{id}/approve (validations.manage permission)"
        )

# ===== IAM Routes Tests =====

def test_iam_routes():
    """Test IAM management endpoints with permission checks"""
    print(f"\n{Colors.BOLD}=== IAM Routes (iam_routes.py) ==={Colors.ENDC}")
    
    # 1. GET /api/auth-api/iam/permissions → iam.permissions.read permission
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth-api/iam/permissions",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /api/auth-api/iam/permissions (iam.permissions.read permission)"
    )
    if response:
        permissions = response.json()
        print(f"    Found {len(permissions)} permissions")
    
    # 2. POST /api/auth-api/iam/permissions → iam.permissions.create permission
    test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/auth-api/iam/permissions",
        data={
            "code": "test.permission",
            "name": "Test Permission",
            "description": "Test permission for IAM testing",
            "category": "test"
        },
        headers=get_auth_headers(),
        expected_status=201,
        test_name="POST /api/auth-api/iam/permissions (iam.permissions.create permission)"
    )
    
    # 3. GET /api/auth-api/iam/profiles → iam.profiles.read permission
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth-api/iam/profiles",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /api/auth-api/iam/profiles (iam.profiles.read permission)"
    )
    if response:
        profiles = response.json()
        print(f"    Found {len(profiles)} profiles")
    
    # 4. POST /api/auth-api/iam/profiles → iam.profiles.create permission
    test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/auth-api/iam/profiles",
        data={
            "code": "test_profile",
            "name": "Test Profile",
            "description": "Test profile for IAM testing",
            "permission_ids": []
        },
        headers=get_auth_headers(),
        expected_status=201,
        test_name="POST /api/auth-api/iam/profiles (iam.profiles.create permission)"
    )
    
    # 5. GET /api/auth-api/iam/groups → iam.groups.read permission
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth-api/iam/groups",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /api/auth-api/iam/groups (iam.groups.read permission)"
    )
    if response:
        groups = response.json()
        print(f"    Found {len(groups)} groups")
    
    # 6. POST /api/auth-api/iam/groups → iam.groups.create permission
    test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/auth-api/iam/groups",
        data={
            "code": "test_group",
            "name": "Test Group",
            "description": "Test group for IAM testing",
            "profile_ids": []
        },
        headers=get_auth_headers(),
        expected_status=201,
        test_name="POST /api/auth-api/iam/groups (iam.groups.create permission)"
    )

# ===== Authorization Tests =====

def test_authorization():
    """Test 401/403 authorization errors"""
    print(f"\n{Colors.BOLD}=== Authorization Tests (401/403) ==={Colors.ENDC}")
    
    # 1. Test 401 - Unauthenticated request
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/auth/users",
        expected_status=401,
        test_name="GET /auth/users without token (401 Unauthorized)"
    )
    
    # 2. Test 401 - Invalid token
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/auth/users",
        headers={"Authorization": "Bearer invalid_token_12345"},
        expected_status=401,
        test_name="GET /auth/users with invalid token (401 Unauthorized)"
    )
    
    # 3. Create a limited user (interim) to test 403
    print(f"\n{Colors.YELLOW}Creating interim user for 403 testing...{Colors.ENDC}")
    response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/api/auth/security/users",
        data={
            "email": f"interim_test_{datetime.now().timestamp()}@example.com",
            "username": f"interim_test_{int(datetime.now().timestamp())}",
            "password": "TestPass123!",
            "roles": ["interim"],
            "send_invitation": False
        },
        headers=get_auth_headers(),
        expected_status=201,
        test_name="Create interim user for 403 testing"
    )
    
    if response:
        interim_user = response.json()
        test_data["interim_user_id"] = interim_user.get("id")
        
        # Login as interim user
        login_response = test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/auth/local/login",
            data={
                "username": interim_user.get("username"),
                "password": "TestPass123!"
            },
            expected_status=200,
            test_name="Login as interim user"
        )
        
        if login_response:
            login_data = login_response.json()
            test_data["interim_token"] = login_data.get("access_token")
            
            # 4. Test 403 - Insufficient permissions (interim trying to access admin endpoint)
            test_endpoint(
                "GET",
                f"{AUTH_BASE_URL}/auth/admin/stats",
                headers=get_auth_headers(test_data["interim_token"]),
                expected_status=403,
                test_name="GET /auth/admin/stats as interim user (403 Forbidden)"
            )
            
            # 5. Test 403 - Interim user trying to create users
            test_endpoint(
                "POST",
                f"{AUTH_BASE_URL}/api/auth/security/users",
                data={
                    "email": "test@example.com",
                    "roles": ["interim"]
                },
                headers=get_auth_headers(test_data["interim_token"]),
                expected_status=403,
                test_name="POST /api/auth/security/users as interim user (403 Forbidden)"
            )

# ===== Permission Checker Service Tests =====

def test_permission_checker():
    """Test permission checker service functionality"""
    print(f"\n{Colors.BOLD}=== Permission Checker Service Tests ==={Colors.ENDC}")
    
    # 1. Test get_user_permissions via IAM API
    if test_data.get("admin_user_id"):
        response = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/api/auth-api/iam/users/{test_data['admin_user_id']}/permissions",
            headers=get_auth_headers(),
            expected_status=200,
            test_name="Get admin user permissions"
        )
        if response:
            perms_data = response.json()
            print(f"    Total permissions: {perms_data.get('total_permissions', 0)}")
            print(f"    Direct profiles: {len(perms_data.get('direct_profiles', []))}")
            print(f"    Groups: {len(perms_data.get('groups', []))}")
    
    # 2. Test permission check endpoint
    if test_data.get("admin_user_id"):
        test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/api/auth-api/iam/check-permission",
            data={
                "user_id": test_data["admin_user_id"],
                "permission_code": "users.read"
            },
            headers=get_auth_headers(),
            expected_status=200,
            test_name="Check if admin has users.read permission"
        )
    
    # 3. Test SuperAdmin bypass
    print(f"\n{Colors.YELLOW}Testing SuperAdmin bypass...{Colors.ENDC}")
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/auth/users/{test_data['admin_user_id']}",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="SuperAdmin can access all endpoints (bypass)"
    )
    
    # 4. Test wildcard matching (if interim user has users.* permission)
    if test_data.get("interim_user_id"):
        test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/api/auth-api/iam/check-permission",
            data={
                "user_id": test_data["interim_user_id"],
                "permission_code": "users.read"
            },
            headers=get_auth_headers(),
            expected_status=200,
            test_name="Check wildcard permission matching"
        )

# ===== Backward Compatibility Tests =====

def test_backward_compatibility():
    """Test backward compatibility with legacy role-based system"""
    print(f"\n{Colors.BOLD}=== Backward Compatibility Tests ==={Colors.ENDC}")
    
    # 1. Test that legacy role checks still work
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/auth/me",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /auth/me (legacy endpoint)"
    )
    
    if response:
        user_data = response.json()
        roles = user_data.get("roles", [])
        print(f"    User roles: {roles}")
        if "super_admin" in roles or "admin" in roles:
            log_test("Legacy role-based access", "PASS", "Admin/SuperAdmin roles present")
        else:
            log_test("Legacy role-based access", "FAIL", "Expected admin roles not found")
    
    # 2. Test that old endpoints still work
    test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/auth/admin/roles",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="GET /auth/admin/roles (legacy role management)"
    )

# ===== Database Verification =====

def test_database_state():
    """Verify database state for IAM system"""
    print(f"\n{Colors.BOLD}=== Database State Verification ==={Colors.ENDC}")
    
    # This would require MongoDB connection, so we'll use API endpoints instead
    
    # 1. Verify permissions count
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth-api/iam/permissions",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="Verify permissions in database"
    )
    if response:
        permissions = response.json()
        if len(permissions) == 90:
            log_test("Permission count", "PASS", f"Found 90 permissions as expected")
        else:
            log_test("Permission count", "FAIL", f"Expected 90, found {len(permissions)}")
    
    # 2. Verify profiles count
    response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/api/auth-api/iam/profiles",
        headers=get_auth_headers(),
        expected_status=200,
        test_name="Verify profiles in database"
    )
    if response:
        profiles = response.json()
        system_profiles = [p for p in profiles if p.get("is_system")]
        print(f"    Total profiles: {len(profiles)}")
        print(f"    System profiles: {len(system_profiles)}")
        if len(system_profiles) >= 7:
            log_test("System profiles", "PASS", f"Found {len(system_profiles)} system profiles")
        else:
            log_test("System profiles", "FAIL", f"Expected at least 7, found {len(system_profiles)}")
    
    # 3. Verify Admin profile has all permissions
    if response:
        admin_profile = next((p for p in profiles if p.get("code") == "admin"), None)
        if admin_profile:
            perm_count = len(admin_profile.get("permission_ids", []))
            if perm_count == 90:
                log_test("Admin profile permissions", "PASS", f"Admin has all 90 permissions")
            else:
                log_test("Admin profile permissions", "FAIL", f"Expected 90, found {perm_count}")

# ===== Main Test Runner =====

def main():
    """Run all IAM migration tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}IAM Migration Backend Testing{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    
    # Login as admin first
    if not login_admin():
        print(f"\n{Colors.RED}Failed to login as admin. Aborting tests.{Colors.ENDC}")
        sys.exit(1)
    
    # Run all test suites
    test_user_management_routes()
    test_email_routes()
    test_validation_routes()
    test_iam_routes()
    test_authorization()
    test_permission_checker()
    test_backward_compatibility()
    test_database_state()
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}IAM Migration Testing Complete{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
