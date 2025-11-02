#!/usr/bin/env python3
"""
Backend Testing for JLC Auth System
Tests auth endpoints through Vite proxy configuration
"""

import requests
import json
import sys
import os
import random
import string
from datetime import datetime

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"  # Direct auth service URL
FRONTEND_PROXY_URL = "http://localhost:3000/auth-api"  # Through Vite proxy

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

def test_local_registration():
    """Test local user registration with role selection"""
    print(f"\n{Colors.BOLD}=== Testing Local Registration ==={Colors.ENDC}")
    
    # Generate unique identifiers for this test run
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    test_cases = [
        {
            "name": "Valid Registration - Interim Role",
            "data": {
                "username": f"testinterim_{random_suffix}",
                "email": f"interim_{random_suffix}@test.com",
                "password": "testpass123",
                "full_name": "Test Interim User",
                "role": "interim"
            },
            "expected_status": 200
        },
        {
            "name": "Valid Registration - Company Role", 
            "data": {
                "username": f"testcompany_{random_suffix}",
                "email": f"company_{random_suffix}@test.com",
                "password": "testpass123",
                "full_name": "Test Company User",
                "role": "company"
            },
            "expected_status": 200
        },
        {
            "name": "Invalid Role",
            "data": {
                "username": "testuser",
                "email": "test@test.com", 
                "password": "testpass123",
                "full_name": "Test User",
                "role": "invalid"
            },
            "expected_status": 400
        },
        {
            "name": "Duplicate Username",
            "data": {
                "username": f"testinterim_{random_suffix}",  # Same as first test
                "email": f"different_{random_suffix}@test.com",
                "password": "testpass123",
                "full_name": "Different User",
                "role": "interim"
            },
            "expected_status": 400
        },
        {
            "name": "Duplicate Email",
            "data": {
                "username": f"differentuser_{random_suffix}",
                "email": f"interim_{random_suffix}@test.com",  # Same as first test
                "password": "testpass123", 
                "full_name": "Different User",
                "role": "company"
            },
            "expected_status": 400
        }
    ]
    
    results = []
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
                    if user.get("role") == test_case["data"]["role"]:
                        log_test(f"  {test_case['name']} - Role Assignment", "PASS",
                                f"Role correctly set to {user.get('role')}")
                    else:
                        log_test(f"  {test_case['name']} - Role Assignment", "FAIL",
                                f"Expected role {test_case['data']['role']}, got {user.get('role')}")
                    
                    if user.get("status") == "pending":
                        log_test(f"  {test_case['name']} - Status", "PASS",
                                "Status correctly set to pending")
                    else:
                        log_test(f"  {test_case['name']} - Status", "WARN",
                                f"Status is {user.get('status')}, expected 'pending'")
            else:
                # Error case - check error message
                error_detail = response.get("detail", "No error message")
                print(f"    Error message: {error_detail}")
        
        results.append({
            "test": test_case["name"],
            "success": response is not None,
            "response": response
        })
    
    return results

def test_local_login():
    """Test local login with admin credentials"""
    print(f"\n{Colors.BOLD}=== Testing Local Login ==={Colors.ENDC}")
    
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
        # Check response structure
        required_fields = ["access_token", "refresh_token", "user"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            log_test("Admin Login - Response Structure", "FAIL",
                    f"Missing fields: {missing_fields}")
        else:
            log_test("Admin Login - Response Structure", "PASS",
                    "All required fields present")
            
            # Check user object
            user = response.get("user", {})
            if "admin" in user.get("roles", []):
                log_test("Admin Login - Role Check", "PASS",
                        "Admin role correctly assigned")
            else:
                log_test("Admin Login - Role Check", "FAIL",
                        f"Admin role missing. Roles: {user.get('roles', [])}")
        
        return response
    
    return None

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
    """Run all backend tests"""
    print(f"{Colors.BOLD}JLC Auth System Backend Testing{Colors.ENDC}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Track results
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "warnings": 0
    }
    
    # Test 1: Auth service health
    if test_auth_service_health():
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
        print(f"\n{Colors.RED}❌ Auth service is not running. Cannot proceed with tests.{Colors.ENDC}")
        return test_results
    test_results["total_tests"] += 1
    
    # Test 2: Google OAuth status
    google_status = test_google_oauth_status()
    if google_status is not None:
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    test_results["total_tests"] += 1
    
    # Test 3: Local registration
    registration_results = test_local_registration()
    for result in registration_results:
        test_results["total_tests"] += 1
        if result["success"]:
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
    
    # Test 4: Local login
    login_result = test_local_login()
    test_results["total_tests"] += 1
    if login_result:
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Test 5: Vite proxy (optional)
    proxy_result = test_vite_proxy()
    test_results["total_tests"] += 1
    if proxy_result:
        test_results["passed_tests"] += 1
    elif proxy_result is False:
        test_results["warnings"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Summary
    print(f"\n{Colors.BOLD}=== Test Summary ==={Colors.ENDC}")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"{Colors.GREEN}Passed: {test_results['passed_tests']}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {test_results['failed_tests']}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Warnings: {test_results['warnings']}{Colors.ENDC}")
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
    print(f"Success Rate: {success_rate:.1f}%")
    
    if test_results['failed_tests'] == 0:
        print(f"\n{Colors.GREEN}✅ All critical tests passed!{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}❌ {test_results['failed_tests']} test(s) failed.{Colors.ENDC}")
    
    return test_results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)