#!/usr/bin/env python3
"""
Backend Testing for Système d'Inscription Complet
Tests complete registration system with email validation, profile auto-creation, and password reset
"""

import requests
import json
import sys
import os
import random
import string
from datetime import datetime
import re

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"  # Direct auth service URL
FRONTEND_PROXY_URL = "http://localhost:3000/auth-api"  # Through Vite proxy

# Global variable to store test users for MongoDB verification
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

def test_google_oauth_status():
    """Test Google OAuth configuration status"""
    print(f"\n{Colors.BOLD}=== Testing Google OAuth Status ==={Colors.ENDC}")
    
    # Test through direct URL (auth service)
    response = test_endpoint("GET", f"{AUTH_BASE_URL}/auth/google/status",
                           test_name="Google OAuth Status Check")
    
    if response:
        print(f"    Configured: {response.get('configured', False)}")
        print(f"    Client ID: {response.get('client_id', 'Not set')}")
        return response
    return None

def test_registration_with_email_validation():
    """Test registration system with automatic email validation"""
    print(f"\n{Colors.BOLD}=== Testing Registration with Email Validation ==={Colors.ENDC}")
    
    # Generate unique identifiers for this test run
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    test_cases = [
        {
            "name": "1. Inscription Intérimaire avec Email Valide (Auto-validation)",
            "data": {
                "username": f"interim_test_{random_suffix}",
                "email": f"interim.test.{random_suffix}@gmail.com",
                "password": "SecurePass123!",
                "full_name": "Jean Dupont",
                "role": "interim",
                "phone": "+241 01 23 45 67",
                "date_of_birth": "1990-01-15"
            },
            "expected_status": 200,
            "expected_user_status": "active"  # Gmail should auto-validate
        },
        {
            "name": "2. Inscription Société avec Email Non-Validé (Validation Manuelle)",
            "data": {
                "username": f"company_test_{random_suffix}",
                "email": f"contact.{random_suffix}@entreprise-locale.ga",
                "password": "SecurePass123!",
                "full_name": "Marie Martin",
                "role": "company",
                "company_name": "Entreprise Test SARL",
                "legal_representative": "Marie Martin",
                "nif": "123456789GA",
                "phone": "+241 07 89 01 23"
            },
            "expected_status": 200,
            "expected_user_status": "pending"  # .ga domain should require manual validation
        },
        {
            "name": "3a. Username déjà utilisé",
            "data": {
                "username": f"interim_test_{random_suffix}",  # Same as first test
                "email": f"different_{random_suffix}@gmail.com",
                "password": "SecurePass123!",
                "full_name": "Different User",
                "role": "interim"
            },
            "expected_status": 400,
            "expected_error_french": True
        },
        {
            "name": "3b. Email déjà utilisé",
            "data": {
                "username": f"differentuser_{random_suffix}",
                "email": "interim.test@gmail.com",  # Same as first test
                "password": "SecurePass123!",
                "full_name": "Different User",
                "role": "company"
            },
            "expected_status": 400,
            "expected_error_french": True
        },
        {
            "name": "3c. Rôle invalide",
            "data": {
                "username": f"testuser_{random_suffix}",
                "email": f"test_{random_suffix}@gmail.com",
                "password": "SecurePass123!",
                "full_name": "Test User",
                "role": "invalid_role"
            },
            "expected_status": 400,
            "expected_error_french": True
        }
    ]
    
    results = []
    successful_registrations = []
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        
        response = test_endpoint(
            "POST", 
            f"{AUTH_BASE_URL}/auth/local/register",
            data=test_case["data"],
            expected_status=test_case["expected_status"],
            test_name=test_case["name"]
        )
        
        if response:
            if test_case["expected_status"] == 200:
                # Successful registration - check response structure
                required_fields = ["access_token", "refresh_token", "user"]
                missing_fields = [field for field in required_fields if field not in response]
                
                if missing_fields:
                    log_test(f"  {test_case['name']} - Response Structure", "FAIL", 
                            f"Missing fields: {missing_fields}")
                else:
                    log_test(f"  {test_case['name']} - Response Structure", "PASS", 
                            f"All required fields present")
                    
                    # Check user object
                    user = response.get("user", {})
                    user_roles = user.get("roles", [])
                    expected_role = test_case["data"]["role"]
                    expected_status = test_case.get("expected_user_status", "pending")
                    
                    # Check role assignment
                    if expected_role in user_roles:
                        log_test(f"  {test_case['name']} - Role Assignment", "PASS",
                                f"Role correctly set to {expected_role}")
                    else:
                        log_test(f"  {test_case['name']} - Role Assignment", "FAIL",
                                f"Expected role {expected_role} in roles, got {user_roles}")
                    
                    # Check user status (active vs pending based on email domain)
                    actual_status = user.get("status", "unknown")
                    if actual_status == expected_status:
                        log_test(f"  {test_case['name']} - Email Validation Status", "PASS",
                                f"Status correctly set to {expected_status}")
                    else:
                        log_test(f"  {test_case['name']} - Email Validation Status", "FAIL",
                                f"Expected status {expected_status}, got {actual_status}")
                    
                    # Store successful registration for profile verification
                    successful_registrations.append({
                        "user_id": user.get("id"),
                        "email": user.get("email"),
                        "role": expected_role,
                        "test_name": test_case["name"]
                    })
                    
            else:
                # Error case - check error message is in French
                error_detail = response.get("detail", "No error message")
                print(f"    Error message: {error_detail}")
                
                if test_case.get("expected_error_french"):
                    # Check if error message contains French words
                    french_indicators = ["déjà", "utilisé", "invalide", "Cet", "Ce"]
                    has_french = any(word in error_detail for word in french_indicators)
                    
                    if has_french:
                        log_test(f"  {test_case['name']} - French Error Message", "PASS",
                                f"Error message in French: {error_detail}")
                    else:
                        log_test(f"  {test_case['name']} - French Error Message", "WARN",
                                f"Error message may not be in French: {error_detail}")
        
        results.append({
            "test": test_case["name"],
            "success": response is not None,
            "response": response
        })
    
    # Store successful registrations for later profile verification
    global test_users
    test_users = successful_registrations
    
    return results

def test_password_reset():
    """Test password reset functionality"""
    print(f"\n{Colors.BOLD}=== Testing Password Reset ==={Colors.ENDC}")
    
    # Use the first successful registration email for testing
    global test_users
    test_email = test_users[0]["email"] if test_users else "interim.test@gmail.com"
    
    # Test 4a: Request password reset
    print(f"\n  Testing: 4a. Demande de réinitialisation")
    forgot_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/forgot-password",
        data={"email": test_email},
        expected_status=200,
        test_name="Password Reset Request"
    )
    
    reset_token = None
    if forgot_response:
        # Check response structure
        if "message" in forgot_response:
            log_test("Password Reset Request - Response", "PASS",
                    f"Message: {forgot_response['message']}")
        
        # Extract reset token from response (test mode)
        if "reset_url" in forgot_response:
            reset_url = forgot_response["reset_url"]
            # Extract token from URL
            import re
            token_match = re.search(r'token=([^&]+)', reset_url)
            if token_match:
                reset_token = token_match.group(1)
                log_test("Password Reset Request - Token Generation", "PASS",
                        f"Reset token generated: {reset_token[:10]}...")
            else:
                log_test("Password Reset Request - Token Generation", "FAIL",
                        "No token found in reset URL")
        else:
            log_test("Password Reset Request - Token Generation", "WARN",
                    "No reset_url in response (production mode)")
    
    # Test 4b: Reset password with token
    if reset_token:
        print(f"\n  Testing: 4b. Réinitialisation avec token")
        reset_response = test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/auth/reset-password",
            data={
                "token": reset_token,
                "new_password": "NewSecurePass456!"
            },
            expected_status=200,
            test_name="Password Reset with Token"
        )
        
        if reset_response:
            if "message" in reset_response:
                log_test("Password Reset with Token - Success", "PASS",
                        f"Message: {reset_response['message']}")
    
    # Test 4c: Invalid token
    print(f"\n  Testing: 4c. Token invalide/expiré")
    invalid_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/reset-password",
        data={
            "token": "invalid_token_123",
            "new_password": "NewSecurePass456!"
        },
        expected_status=400,
        test_name="Password Reset with Invalid Token"
    )
    
    if invalid_response:
        error_detail = invalid_response.get("detail", "")
        if "invalide" in error_detail or "invalid" in error_detail.lower():
            log_test("Password Reset Invalid Token - Error Message", "PASS",
                    f"Correct error: {error_detail}")
        else:
            log_test("Password Reset Invalid Token - Error Message", "WARN",
                    f"Unexpected error: {error_detail}")
    
    return {
        "forgot_response": forgot_response,
        "reset_token": reset_token,
        "reset_response": reset_response if reset_token else None,
        "invalid_response": invalid_response
    }


def test_mongodb_verification():
    """Test MongoDB data verification"""
    print(f"\n{Colors.BOLD}=== Testing MongoDB Verification ==={Colors.ENDC}")
    
    try:
        from pymongo import MongoClient
        import os
        
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        
        # Check auth_db.users
        auth_db = client['auth_db']
        users_collection = auth_db.users
        
        # Check jlc_db.profiles  
        jlc_db = client['jlc_db']
        profiles_collection = jlc_db.profiles
        
        print(f"\n  Checking MongoDB Collections:")
        
        # Count users in auth_db
        user_count = users_collection.count_documents({})
        log_test("MongoDB - auth_db.users", "PASS" if user_count > 0 else "WARN",
                f"Found {user_count} users in auth_db.users")
        
        # Count profiles in jlc_db
        profile_count = profiles_collection.count_documents({})
        log_test("MongoDB - jlc_db.profiles", "PASS" if profile_count > 0 else "WARN",
                f"Found {profile_count} profiles in jlc_db.profiles")
        
        # Verify specific test users if available
        global test_users
        if 'test_users' in globals() and test_users:
            print(f"\n  Verifying Test Users:")
            
            for test_user in test_users:
                user_id = test_user.get("user_id")
                email = test_user.get("email")
                role = test_user.get("role")
                
                if user_id:
                    # Check user in auth_db
                    user_doc = users_collection.find_one({"id": user_id})
                    if user_doc:
                        status = user_doc.get("status", "unknown")
                        roles = user_doc.get("roles", [])
                        log_test(f"User {email} in auth_db", "PASS",
                                f"Status: {status}, Roles: {roles}")
                    else:
                        log_test(f"User {email} in auth_db", "FAIL",
                                "User not found in auth_db")
                    
                    # Check profile in jlc_db
                    profile_doc = profiles_collection.find_one({"user_id": user_id})
                    if profile_doc:
                        profile_type = profile_doc.get("profile_type", "unknown")
                        log_test(f"Profile {email} in jlc_db", "PASS",
                                f"Profile type: {profile_type}")
                        
                        # Check role-specific fields
                        if role == "interim":
                            interim_fields = ["skills", "experience_years", "availability"]
                            has_interim_fields = all(field in profile_doc for field in interim_fields)
                            log_test(f"Profile {email} - Interim Fields", 
                                    "PASS" if has_interim_fields else "WARN",
                                    f"Interim-specific fields present: {has_interim_fields}")
                        
                        elif role == "company":
                            company_fields = ["company_name", "nif", "legal_representative"]
                            has_company_fields = any(field in profile_doc for field in company_fields)
                            log_test(f"Profile {email} - Company Fields",
                                    "PASS" if has_company_fields else "WARN", 
                                    f"Company-specific fields present: {has_company_fields}")
                    else:
                        log_test(f"Profile {email} in jlc_db", "FAIL",
                                "Profile not found in jlc_db")
        
        client.close()
        return True
        
    except Exception as e:
        log_test("MongoDB Verification", "FAIL", f"Error connecting to MongoDB: {str(e)}")
        return False

def test_vite_proxy():
    """Test if Vite proxy is working (optional)"""
    print(f"\n{Colors.BOLD}=== Testing Vite Proxy (Optional) ==={Colors.ENDC}")
    
    try:
        # Test Google OAuth status through proxy
        response = test_endpoint("GET", f"{FRONTEND_PROXY_URL}/auth/google/status",
                               test_name="Vite Proxy - Google Status")
        
        if response:
            log_test("Vite Proxy", "PASS", "Proxy is working correctly")
            return True
        else:
            log_test("Vite Proxy", "WARN", "Proxy not available (frontend may not be running)")
            return False
    except:
        log_test("Vite Proxy", "WARN", "Proxy test failed (frontend may not be running)")
        return False

def run_all_tests():
    """Run all backend tests for Système d'Inscription Complet"""
    print(f"{Colors.BOLD}Système d'Inscription Complet - Backend Testing{Colors.ENDC}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Track results
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "warnings": 0,
        "critical_failures": []
    }
    
    # Test 1: Auth service health
    print(f"\n{Colors.BLUE}Phase 1: Service Health Check{Colors.ENDC}")
    if test_auth_service_health():
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
        test_results["critical_failures"].append("Auth service not running")
        print(f"\n{Colors.RED}❌ Auth service is not running. Cannot proceed with tests.{Colors.ENDC}")
        return test_results
    test_results["total_tests"] += 1
    
    # Test 2: Registration with Email Validation
    print(f"\n{Colors.BLUE}Phase 2: Registration System with Email Validation{Colors.ENDC}")
    registration_results = test_registration_with_email_validation()
    
    critical_registration_failures = 0
    for result in registration_results:
        test_results["total_tests"] += 1
        if result["success"]:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
            # Check if it's a critical failure (successful registration tests)
            if "Inscription" in result["test"] and result["test"].startswith(("1.", "2.")):
                critical_registration_failures += 1
                test_results["critical_failures"].append(f"Registration failed: {result['test']}")
    
    # Test 3: Password Reset System
    print(f"\n{Colors.BLUE}Phase 3: Password Reset System{Colors.ENDC}")
    password_reset_results = test_password_reset()
    test_results["total_tests"] += 3  # 3 password reset tests
    
    if password_reset_results.get("forgot_response"):
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
        test_results["critical_failures"].append("Password reset request failed")
    
    if password_reset_results.get("reset_response"):
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
        if password_reset_results.get("reset_token"):
            test_results["critical_failures"].append("Password reset with token failed")
    
    if password_reset_results.get("invalid_response"):
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Test 4: MongoDB Verification
    print(f"\n{Colors.BLUE}Phase 4: MongoDB Data Verification{Colors.ENDC}")
    mongodb_result = test_mongodb_verification()
    test_results["total_tests"] += 1
    if mongodb_result:
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
        test_results["critical_failures"].append("MongoDB verification failed")
    
    # Summary
    print(f"\n{Colors.BOLD}=== Test Summary ==={Colors.ENDC}")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"{Colors.GREEN}Passed: {test_results['passed_tests']}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {test_results['failed_tests']}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Warnings: {test_results['warnings']}{Colors.ENDC}")
    
    if test_results['total_tests'] > 0:
        success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Critical failures summary
    if test_results['critical_failures']:
        print(f"\n{Colors.RED}❌ Critical Failures:{Colors.ENDC}")
        for failure in test_results['critical_failures']:
            print(f"  • {failure}")
    
    if test_results['failed_tests'] == 0:
        print(f"\n{Colors.GREEN}✅ All tests passed! Registration system working correctly.{Colors.ENDC}")
    elif len(test_results['critical_failures']) == 0:
        print(f"\n{Colors.YELLOW}⚠️ Some minor issues found, but core functionality working.{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}❌ Critical issues found in registration system.{Colors.ENDC}")
    
    return test_results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)