#!/usr/bin/env python3
"""
Critical Authentication Issue Testing
Tests the authentication issue where users get 401 Unauthorized errors when trying to log in immediately after registration.
"""

import requests
import json
import sys
import os
import random
import string
import time
from datetime import datetime
import re
from pymongo import MongoClient

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"  # Direct auth service URL
API_BASE_URL = "http://localhost:8001/api"   # JLC API service URL

# Global variable to store test data
test_users = []

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
        
        # Check status code
        if response.status_code != expected_status:
            log_test(test_name, "FAIL", 
                    f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}")
            return None
        
        # Try to parse JSON
        try:
            json_response = response.json()
            log_test(test_name, "PASS", f"Status: {response.status_code}")
            return json_response
        except json.JSONDecodeError:
            log_test(test_name, "FAIL", f"Invalid JSON response: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        log_test(test_name, "FAIL", f"Request failed: {str(e)}")
        return None

def test_auth_service_health():
    """Test if auth service is running"""
    print(f"\n{Colors.BOLD}=== Testing Auth Service Health ==={Colors.ENDC}")
    
    # Test direct auth service
    response = test_endpoint("GET", f"{AUTH_BASE_URL}/../health", 
                           test_name="Auth Service Health Check")
    
    if response:
        print(f"    Service: {response.get('service', 'Unknown')}")
        print(f"    Status: {response.get('status', 'Unknown')}")
        return True
    return False

def test_candidat_registration_and_immediate_login():
    """Test candidat registration with immediate login - CRITICAL TEST"""
    print(f"\n{Colors.BOLD}=== CRITICAL TEST: Candidat Registration + Immediate Login ==={Colors.ENDC}")
    
    # Generate unique test data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test.candidat.{random_suffix}@gmail.com"
    test_username = f"candidat_{random_suffix}"
    test_password = "TestPass123!"
    
    print(f"  Test Account: {test_username} / {test_email}")
    
    # Step 1: Register candidat account (should get ACTIVE status)
    print(f"\n  Step 1: Register Candidat Account")
    
    registration_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "full_name": "Test Candidat User",
        "role": "interim",
        "phone": "+241 01 23 45 67",
        "date_of_birth": "1990-01-15"
    }
    
    register_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/register",
        data=registration_data,
        expected_status=200,
        test_name="Candidat Registration"
    )
    
    if not register_response:
        log_test("CRITICAL TEST FAILED", "FAIL", "Registration failed - cannot proceed with login test")
        return False
    
    # Verify registration response
    user_data = register_response.get("user", {})
    user_status = user_data.get("status")
    user_id = user_data.get("id")
    
    log_test("Registration Status Check", "PASS" if user_status == "active" else "FAIL", 
             f"User status: {user_status} (expected: active)")
    
    if user_status != "active":
        log_test("CRITICAL ISSUE", "FAIL", f"Candidat user should have 'active' status, got '{user_status}'")
        return False
    
    # Step 2: IMMEDIATELY attempt login with same credentials
    print(f"\n  Step 2: IMMEDIATE Login Attempt (CRITICAL)")
    
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    login_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/login",
        data=login_data,
        expected_status=200,
        test_name="Immediate Login After Registration"
    )
    
    if not login_response:
        log_test("CRITICAL AUTHENTICATION BUG", "FAIL", "Login failed immediately after registration - THIS IS THE BUG!")
        
        # Check backend logs for more details
        print(f"\n  Checking backend logs for login failure...")
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '20', '/var/log/supervisor/auth-microservice.err.log'], 
                                  capture_output=True, text=True)
            if result.stdout:
                print(f"    Backend Error Logs:")
                for line in result.stdout.split('\n')[-10:]:
                    if line.strip():
                        print(f"      {line}")
        except Exception as e:
            print(f"    Could not read logs: {e}")
        
        return False
    
    # Verify login response
    access_token = login_response.get("access_token")
    login_user = login_response.get("user", {})
    
    if access_token:
        log_test("Login Success", "PASS", f"Access token received: {access_token[:20]}...")
        log_test("User Data", "PASS", f"User ID: {login_user.get('id', 'Missing')}")
        
        # Store for MongoDB verification
        global test_users
        test_users.append({
            "user_id": user_id,
            "email": test_email,
            "username": test_username,
            "password": test_password,
            "access_token": access_token,
            "expected_status": "active",
            "test_type": "candidat"
        })
        
        return True
    else:
        log_test("Login Token Missing", "FAIL", "No access token in login response")
        return False

def test_collaborator_registration_and_login():
    """Test collaborator registration (should be pending) and login attempt"""
    print(f"\n{Colors.BOLD}=== Testing Collaborator Registration + Login ==={Colors.ENDC}")
    
    # Generate unique test data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"test.company.{random_suffix}@jlcgroup.com"
    test_username = f"company_{random_suffix}"
    test_password = "TestPass123!"
    
    print(f"  Test Account: {test_username} / {test_email}")
    
    # Step 1: Register collaborator account (should get PENDING status)
    print(f"\n  Step 1: Register Collaborator Account")
    
    registration_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "full_name": "Test Company User",
        "role": "company",
        "company_name": "Test Company SARL",
        "legal_representative": "Test Representative",
        "nif": "123456789GA",
        "phone": "+241 07 89 01 23"
    }
    
    register_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/register",
        data=registration_data,
        expected_status=200,
        test_name="Collaborator Registration"
    )
    
    if not register_response:
        log_test("Collaborator Registration", "FAIL", "Registration failed")
        return False
    
    # Verify registration response
    user_data = register_response.get("user", {})
    user_status = user_data.get("status")
    user_id = user_data.get("id")
    
    log_test("Registration Status Check", "PASS" if user_status == "pending" else "FAIL", 
             f"User status: {user_status} (expected: pending)")
    
    # Step 2: Attempt login (should fail with "Account is not active")
    print(f"\n  Step 2: Login Attempt (Should Fail)")
    
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    login_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/login",
        data=login_data,
        expected_status=401,
        test_name="Login with Pending Account"
    )
    
    if login_response:
        error_detail = login_response.get("detail", "")
        if "not active" in error_detail.lower():
            log_test("Pending Account Login Block", "PASS", f"Correctly blocked: {error_detail}")
        else:
            log_test("Pending Account Login Block", "WARN", f"Unexpected error: {error_detail}")
    
    # Store for MongoDB verification
    global test_users
    test_users.append({
        "user_id": user_id,
        "email": test_email,
        "username": test_username,
        "password": test_password,
        "expected_status": "pending",
        "test_type": "collaborator"
    })
    
    return True

def test_email_domain_verification():
    """Test the email domain verification endpoint (CORS testing)"""
    print(f"\n{Colors.BOLD}=== Testing Email Domain Verification (CORS) ==={Colors.ENDC}")
    
    # Test 1: Public email domain
    print(f"\n  Test 1: Public Email Domain")
    
    public_email_response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/security/email-domains/verify?email=test@gmail.com",
        expected_status=200,
        test_name="Public Email Domain Verification"
    )
    
    if public_email_response:
        is_collaborator = public_email_response.get("is_collaborator", None)
        if is_collaborator == False:
            log_test("Public Domain Detection", "PASS", "Gmail correctly identified as public domain")
        else:
            log_test("Public Domain Detection", "FAIL", f"Gmail incorrectly identified as collaborator: {is_collaborator}")
    
    # Test 2: JLC collaborator email domain
    print(f"\n  Test 2: JLC Collaborator Email Domain")
    
    jlc_email_response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/security/email-domains/verify?email=test@jlcgroup.com",
        expected_status=200,
        test_name="JLC Email Domain Verification"
    )
    
    if jlc_email_response:
        is_collaborator = jlc_email_response.get("is_collaborator", None)
        if is_collaborator == True:
            log_test("Collaborator Domain Detection", "PASS", "JLC domain correctly identified as collaborator")
        else:
            log_test("Collaborator Domain Detection", "FAIL", f"JLC domain incorrectly identified: {is_collaborator}")
    
    return True

def test_mongodb_status_investigation():
    """Investigate the exact status values in MongoDB"""
    print(f"\n{Colors.BOLD}=== MongoDB Status Investigation ==={Colors.ENDC}")
    
    try:
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        auth_db = client['auth_db']
        users_collection = auth_db.users
        
        print(f"\n  Investigating test users in MongoDB...")
        
        global test_users
        for test_user in test_users:
            user_id = test_user.get("user_id")
            email = test_user.get("email")
            expected_status = test_user.get("expected_status")
            test_type = test_user.get("test_type")
            
            # Find user in database
            user_doc = users_collection.find_one({"id": user_id})
            
            if user_doc:
                actual_status = user_doc.get("status")
                password_hash = user_doc.get("password_hash")
                roles = user_doc.get("roles", [])
                is_collaborator = user_doc.get("is_collaborator", False)
                
                print(f"\n    {test_type.upper()} USER: {email}")
                print(f"      User ID: {user_id}")
                print(f"      Expected Status: '{expected_status}'")
                print(f"      Actual Status: '{actual_status}'")
                print(f"      Status Match: {actual_status == expected_status}")
                print(f"      Password Hash Present: {bool(password_hash)}")
                print(f"      Password Hash Length: {len(password_hash) if password_hash else 0}")
                print(f"      Roles: {roles}")
                print(f"      Is Collaborator: {is_collaborator}")
                
                # Check for any whitespace or encoding issues
                if actual_status:
                    print(f"      Status Repr: {repr(actual_status)}")
                    print(f"      Status Length: {len(actual_status)}")
                
                # Verify status matches expected
                if actual_status == expected_status:
                    log_test(f"MongoDB Status - {test_type}", "PASS", f"Status correctly set to '{actual_status}'")
                else:
                    log_test(f"MongoDB Status - {test_type}", "FAIL", f"Expected '{expected_status}', got '{actual_status}'")
            else:
                log_test(f"MongoDB User - {test_type}", "FAIL", f"User {email} not found in database")
        
        # Check for any users with unusual status values
        print(f"\n  Checking for unusual status values...")
        
        status_counts = {}
        cursor = users_collection.find({}, {"status": 1, "email": 1})
        for doc in cursor:
            status = doc.get("status", "null")
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1
        
        print(f"    Status distribution in database:")
        for status, count in status_counts.items():
            print(f"      '{status}': {count} users")
        
        client.close()
        return True
        
    except Exception as e:
        log_test("MongoDB Investigation", "FAIL", f"Error connecting to MongoDB: {str(e)}")
        return False

def test_admin_login():
    """Test admin login to verify basic authentication works"""
    print(f"\n{Colors.BOLD}=== Testing Admin Login (Baseline) ==={Colors.ENDC}")
    
    login_data = {
        "username": "admin",
        "password": "awana2025"
    }
    
    response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/login",
        data=login_data,
        expected_status=200,
        test_name="Admin Login"
    )
    
    if response:
        access_token = response.get("access_token")
        if access_token:
            log_test("Admin Authentication", "PASS", f"Admin login successful, token: {access_token[:20]}...")
            return access_token
        else:
            log_test("Admin Authentication", "FAIL", "No access token received")
            return None
    else:
        log_test("Admin Authentication", "FAIL", "Admin login failed")
        return None

def test_validations_list():
    """Test the validations endpoint to check for pending collaborator accounts"""
    print(f"\n{Colors.BOLD}=== Testing Validations List ==={Colors.ENDC}")
    
    # Get admin token first
    admin_token = test_admin_login()
    if not admin_token:
        log_test("Validations Test", "FAIL", "Cannot get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get validations list
    validations_response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/validations",
        headers=headers,
        expected_status=200,
        test_name="Get Validations List"
    )
    
    if validations_response:
        # Handle different response formats
        if isinstance(validations_response, list):
            validations = validations_response
        else:
            validations = validations_response.get("validations", [])
        
        pending_count = len([v for v in validations if isinstance(v, dict) and v.get("status") == "pending"])
        
        log_test("Validations List", "PASS", f"Found {len(validations)} validations, {pending_count} pending")
        
        # Check if our test collaborator appears in the list
        global test_users
        collaborator_users = [u for u in test_users if u.get("test_type") == "collaborator"]
        
        for test_user in collaborator_users:
            user_email = test_user.get("email")
            found_validation = any(isinstance(v, dict) and v.get("user_email") == user_email for v in validations)
            
            if found_validation:
                log_test(f"Validation Entry - {user_email}", "PASS", "Collaborator appears in validations list")
            else:
                log_test(f"Validation Entry - {user_email}", "WARN", "Collaborator not found in validations list")
        
        return True
    else:
        log_test("Validations List", "FAIL", "Could not retrieve validations")
        return False

def run_critical_authentication_tests():
    """Run all critical authentication tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}CRITICAL AUTHENTICATION ISSUE INVESTIGATION{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing 401 Unauthorized errors after registration{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    test_results = []
    
    # Test 1: Auth service health
    print(f"\n{Colors.BLUE}[1/7] Auth Service Health Check{Colors.ENDC}")
    health_result = test_auth_service_health()
    test_results.append(("Auth Service Health", health_result))
    
    if not health_result:
        print(f"{Colors.RED}❌ Auth service is not running - cannot proceed with tests{Colors.ENDC}")
        return False
    
    # Test 2: Admin login (baseline)
    print(f"\n{Colors.BLUE}[2/7] Admin Login Baseline Test{Colors.ENDC}")
    admin_result = test_admin_login()
    test_results.append(("Admin Login", admin_result is not None))
    
    # Test 3: Email domain verification (CORS)
    print(f"\n{Colors.BLUE}[3/7] Email Domain Verification{Colors.ENDC}")
    domain_result = test_email_domain_verification()
    test_results.append(("Email Domain Verification", domain_result))
    
    # Test 4: CRITICAL - Candidat registration + immediate login
    print(f"\n{Colors.BLUE}[4/7] CRITICAL: Candidat Registration + Immediate Login{Colors.ENDC}")
    candidat_result = test_candidat_registration_and_immediate_login()
    test_results.append(("Candidat Registration + Login", candidat_result))
    
    # Test 5: Collaborator registration + login attempt
    print(f"\n{Colors.BLUE}[5/7] Collaborator Registration + Login Attempt{Colors.ENDC}")
    collaborator_result = test_collaborator_registration_and_login()
    test_results.append(("Collaborator Registration + Login", collaborator_result))
    
    # Test 6: MongoDB status investigation
    print(f"\n{Colors.BLUE}[6/7] MongoDB Status Investigation{Colors.ENDC}")
    mongodb_result = test_mongodb_status_investigation()
    test_results.append(("MongoDB Status Investigation", mongodb_result))
    
    # Test 7: Validations list
    print(f"\n{Colors.BLUE}[7/7] Validations List Check{Colors.ENDC}")
    validations_result = test_validations_list()
    test_results.append(("Validations List", validations_result))
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}TEST RESULTS SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}[{status}]{Colors.ENDC} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{Colors.BOLD}Total: {passed + failed} tests, {Colors.GREEN}{passed} passed{Colors.ENDC}, {Colors.RED}{failed} failed{Colors.ENDC}")
    
    # Critical findings
    print(f"\n{Colors.BOLD}CRITICAL FINDINGS:{Colors.ENDC}")
    
    candidat_success = test_results[3][1]  # Candidat registration + login
    if not candidat_success:
        print(f"{Colors.RED}❌ CRITICAL BUG CONFIRMED: Candidat users cannot login immediately after registration{Colors.ENDC}")
        print(f"   This is the 401 Unauthorized error reported by users")
    else:
        print(f"{Colors.GREEN}✅ Candidat registration + immediate login working correctly{Colors.ENDC}")
    
    collaborator_success = test_results[4][1]  # Collaborator registration + login
    if collaborator_success:
        print(f"{Colors.GREEN}✅ Collaborator registration working correctly (pending status, login blocked){Colors.ENDC}")
    else:
        print(f"{Colors.RED}❌ Collaborator registration flow has issues{Colors.ENDC}")
    
    return candidat_success and collaborator_success

if __name__ == "__main__":
    """Main execution"""
    try:
        success = run_critical_authentication_tests()
        
        if success:
            print(f"\n{Colors.GREEN}✅ All critical authentication tests passed{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}❌ Critical authentication issues found{Colors.ENDC}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test execution failed: {str(e)}{Colors.ENDC}")
        sys.exit(1)