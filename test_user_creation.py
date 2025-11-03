#!/usr/bin/env python3
"""
Comprehensive User Creation Endpoint Testing
Tests the POST /api/auth/security/users endpoint with various scenarios
"""

import requests
import json
import sys
import random
import string
from datetime import datetime

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"

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

def get_admin_token():
    """Get admin JWT token"""
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/local/login", 
                               json={"username": "admin", "password": "awana2025"})
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_user_creation():
    """Test user creation endpoint comprehensively"""
    print(f"{Colors.BOLD}User Creation Endpoint Testing{Colors.ENDC}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        log_test("Admin Login", "FAIL", "Cannot get admin token")
        return False
    
    log_test("Admin Login", "PASS", "Admin token obtained")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_results = []
    
    # Test 1: Frontend payload (minimal data)
    print(f"\n{Colors.BLUE}Test 1: Frontend Payload (Minimal Data){Colors.ENDC}")
    
    frontend_payload = {
        "email": "frontend.test@example.com",
        "username": None,
        "full_name": None,
        "password": None,
        "roles": ["interim"],
        "group_ids": [],
        "profile_id": None,
        "send_invitation": True
    }
    
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/security/users",
                               json=frontend_payload, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            log_test("Frontend Payload", "PASS", f"User created: {user_data['email']}")
            log_test("Generated Username", "PASS", f"Username: {user_data['username']}")
            log_test("Role Assignment", "PASS", f"Roles: {user_data['roles']}")
            test_results.append(("Frontend Payload", True))
        else:
            log_test("Frontend Payload", "FAIL", f"{response.status_code}: {response.text}")
            test_results.append(("Frontend Payload", False))
    except Exception as e:
        log_test("Frontend Payload", "FAIL", f"Exception: {e}")
        test_results.append(("Frontend Payload", False))
    
    # Test 2: Complete user data
    print(f"\n{Colors.BLUE}Test 2: Complete User Data{Colors.ENDC}")
    
    complete_payload = {
        "email": "complete.user@example.com",
        "username": "completeuser",
        "full_name": "Complete Test User",
        "password": "SecurePass123!",
        "roles": ["company"],
        "group_ids": [],
        "profile_id": None,
        "send_invitation": False
    }
    
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/security/users",
                               json=complete_payload, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            log_test("Complete User Data", "PASS", f"User created: {user_data['email']}")
            log_test("Custom Username", "PASS", f"Username: {user_data['username']}")
            log_test("Full Name", "PASS", f"Full name: {user_data['full_name']}")
            test_results.append(("Complete User Data", True))
        else:
            log_test("Complete User Data", "FAIL", f"{response.status_code}: {response.text}")
            test_results.append(("Complete User Data", False))
    except Exception as e:
        log_test("Complete User Data", "FAIL", f"Exception: {e}")
        test_results.append(("Complete User Data", False))
    
    # Test 3: Multiple roles
    print(f"\n{Colors.BLUE}Test 3: Multiple Roles{Colors.ENDC}")
    
    multi_role_payload = {
        "email": "multi.role@example.com",
        "username": "multirole",
        "full_name": "Multi Role User",
        "password": "SecurePass123!",
        "roles": ["interim", "company"],
        "group_ids": [],
        "profile_id": None,
        "send_invitation": False
    }
    
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/security/users",
                               json=multi_role_payload, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            log_test("Multiple Roles", "PASS", f"User created with roles: {user_data['roles']}")
            test_results.append(("Multiple Roles", True))
        else:
            log_test("Multiple Roles", "FAIL", f"{response.status_code}: {response.text}")
            test_results.append(("Multiple Roles", False))
    except Exception as e:
        log_test("Multiple Roles", "FAIL", f"Exception: {e}")
        test_results.append(("Multiple Roles", False))
    
    # Test 4: Duplicate email (should fail)
    print(f"\n{Colors.BLUE}Test 4: Duplicate Email{Colors.ENDC}")
    
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/security/users",
                               json=frontend_payload, headers=headers)  # Same email as test 1
        
        if response.status_code == 400:
            error_data = response.json()
            log_test("Duplicate Email Validation", "PASS", f"Correctly rejected: {error_data.get('detail', 'No detail')}")
            test_results.append(("Duplicate Email Validation", True))
        else:
            log_test("Duplicate Email Validation", "FAIL", f"Expected 400, got {response.status_code}")
            test_results.append(("Duplicate Email Validation", False))
    except Exception as e:
        log_test("Duplicate Email Validation", "FAIL", f"Exception: {e}")
        test_results.append(("Duplicate Email Validation", False))
    
    # Test 5: Invalid email format
    print(f"\n{Colors.BLUE}Test 5: Invalid Email Format{Colors.ENDC}")
    
    invalid_email_payload = {
        "email": "invalid-email-format",
        "username": "invaliduser",
        "full_name": "Invalid Email User",
        "password": "SecurePass123!",
        "roles": ["interim"],
        "group_ids": [],
        "profile_id": None,
        "send_invitation": False
    }
    
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/security/users",
                               json=invalid_email_payload, headers=headers)
        
        if response.status_code == 422:  # Validation error
            log_test("Invalid Email Format", "PASS", "Invalid email format correctly rejected")
            test_results.append(("Invalid Email Format", True))
        else:
            log_test("Invalid Email Format", "FAIL", f"Expected 422, got {response.status_code}")
            test_results.append(("Invalid Email Format", False))
    except Exception as e:
        log_test("Invalid Email Format", "FAIL", f"Exception: {e}")
        test_results.append(("Invalid Email Format", False))
    
    # Test 6: No authentication (should fail)
    print(f"\n{Colors.BLUE}Test 6: No Authentication{Colors.ENDC}")
    
    try:
        response = requests.post(f"{AUTH_BASE_URL}/auth/security/users",
                               json=frontend_payload)  # No headers
        
        if response.status_code == 401:
            log_test("No Authentication", "PASS", "Correctly requires authentication")
            test_results.append(("No Authentication", True))
        else:
            log_test("No Authentication", "FAIL", f"Expected 401, got {response.status_code}")
            test_results.append(("No Authentication", False))
    except Exception as e:
        log_test("No Authentication", "FAIL", f"Exception: {e}")
        test_results.append(("No Authentication", False))
    
    # Summary
    print(f"\n{Colors.BOLD}=== Test Summary ==={Colors.ENDC}")
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {total - passed}{Colors.ENDC}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✅ All user creation tests passed!{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.RED}❌ Some tests failed.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = test_user_creation()
    sys.exit(0 if success else 1)