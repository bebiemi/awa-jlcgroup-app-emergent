#!/usr/bin/env python3
"""
Test User Creation for Mission Workflow Testing
Creates specific test accounts as requested in the review
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

# Test configuration - using auth service URL from frontend env
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

def get_admin_token():
    """Get admin token for authentication"""
    print(f"\n{Colors.BOLD}=== Getting Admin Token ==={Colors.ENDC}")
    
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
    
    if not response:
        log_test("Admin Login - Token Generation", "FAIL", "No response received")
        return None
    
    # Check if MFA is required
    if response.get("mfa_required", False):
        log_test("Admin Login - MFA Required", "WARN", "Admin has MFA enabled - cannot proceed with automated testing")
        return None
    
    if "access_token" in response:
        log_test("Admin Login - Token Generation", "PASS", 
                f"JWT token received: {response['access_token'][:20]}...")
        return response["access_token"]
    else:
        log_test("Admin Login - Token Generation", "FAIL", f"No access token received. Response: {response}")
        return None

def create_test_accounts():
    """Create the three test accounts as specified in the review request"""
    print(f"\n{Colors.BOLD}=== Creating Test Accounts for Mission Workflow ==={Colors.ENDC}")
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        log_test("Test Account Creation", "FAIL", "Cannot get admin token")
        return []
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Define the three test accounts as specified
    test_accounts = [
        {
            "name": "Company Account",
            "data": {
                "email": "entreprise.test@jlcgroup.com",
                "username": "entreprise_test",
                "full_name": "Entreprise Test SARL",
                "password": "Entreprise2025!",
                "roles": ["company"],
                "send_invitation": False
            }
        },
        {
            "name": "Commercial Account", 
            "data": {
                "email": "commercial.test@jlcgroup.com",
                "username": "commercial_test",
                "full_name": "Commercial Test",
                "password": "Commercial2025!",
                "roles": ["commercial", "admin"],
                "send_invitation": False
            }
        },
        {
            "name": "Second Interim Account",
            "data": {
                "email": "interim2.test@jlcgroup.com",
                "username": "interim_test2",
                "full_name": "Jean Candidat",
                "password": "Interim2025!",
                "roles": ["interim"],
                "send_invitation": False
            }
        }
    ]
    
    created_accounts = []
    
    for account in test_accounts:
        print(f"\n  Creating: {account['name']}")
        
        response = test_endpoint(
            "POST", 
            f"{AUTH_BASE_URL}/auth/security/users",
            data=account["data"],
            headers=headers,
            expected_status=200,
            test_name=f"Create {account['name']}"
        )
        
        if response:
            # Verify response structure
            required_fields = ["id", "email", "username", "roles", "status"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                log_test(f"  {account['name']} - Response Structure", "FAIL", 
                        f"Missing fields: {missing_fields}")
            else:
                log_test(f"  {account['name']} - Response Structure", "PASS", 
                        f"All required fields present")
                
                # Store account info for login testing
                created_accounts.append({
                    "name": account["name"],
                    "username": account["data"]["username"],
                    "password": account["data"]["password"],
                    "email": response.get("email"),
                    "roles": response.get("roles", []),
                    "status": response.get("status"),
                    "id": response.get("id")
                })
                
                print(f"    Created User ID: {response.get('id', 'Unknown')}")
                print(f"    Email: {response.get('email', 'Unknown')}")
                print(f"    Username: {response.get('username', 'Unknown')}")
                print(f"    Roles: {response.get('roles', [])}")
                print(f"    Status: {response.get('status', 'Unknown')}")
        else:
            log_test(f"Create {account['name']}", "FAIL", "Account creation failed")
    
    return created_accounts

def test_account_logins(created_accounts):
    """Test login for each created account"""
    print(f"\n{Colors.BOLD}=== Testing Account Logins ==={Colors.ENDC}")
    
    login_results = []
    
    for account in created_accounts:
        print(f"\n  Testing login for: {account['name']}")
        
        login_data = {
            "username": account["username"],
            "password": account["password"]
        }
        
        response = test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/auth/local/login",
            data=login_data,
            expected_status=200,
            test_name=f"Login {account['name']}"
        )
        
        if response:
            # Check if MFA is required
            if response.get("mfa_required", False):
                log_test(f"  {account['name']} - MFA Required", "INFO", 
                        "Account has MFA enabled - login successful but MFA completion needed")
                login_results.append({
                    "account": account["name"],
                    "success": True,
                    "mfa_required": True,
                    "session_token": response.get("mfa_session_token", "")[:10] + "..."
                })
            else:
                # Verify login response structure
                required_fields = ["access_token", "token_type", "user"]
                missing_fields = [field for field in required_fields if field not in response]
                
                if missing_fields:
                    log_test(f"  {account['name']} - Login Response", "FAIL", 
                            f"Missing fields: {missing_fields}")
                    login_results.append({
                        "account": account["name"],
                        "success": False,
                        "error": f"Missing fields: {missing_fields}"
                    })
                else:
                    # Verify user info matches
                    user_info = response.get("user", {})
                    expected_roles = account["roles"]
                    actual_roles = user_info.get("roles", [])
                    
                    roles_match = all(role in actual_roles for role in expected_roles)
                    
                    if roles_match:
                        log_test(f"  {account['name']} - Role Verification", "PASS", 
                                f"Roles match: {actual_roles}")
                    else:
                        log_test(f"  {account['name']} - Role Verification", "FAIL", 
                                f"Expected: {expected_roles}, Got: {actual_roles}")
                    
                    login_results.append({
                        "account": account["name"],
                        "success": True,
                        "mfa_required": False,
                        "access_token": response.get("access_token", "")[:20] + "...",
                        "user_id": user_info.get("id", ""),
                        "roles": actual_roles,
                        "roles_match": roles_match
                    })
                    
                    print(f"    Login successful")
                    print(f"    Access Token: {response.get('access_token', '')[:20]}...")
                    print(f"    User ID: {user_info.get('id', 'Unknown')}")
                    print(f"    Roles: {actual_roles}")
        else:
            log_test(f"Login {account['name']}", "FAIL", "Login failed")
            login_results.append({
                "account": account["name"],
                "success": False,
                "error": "Login request failed"
            })
    
    return login_results

def print_summary(created_accounts, login_results):
    """Print summary of created accounts and their credentials"""
    print(f"\n{Colors.BOLD}=== SUMMARY OF CREATED TEST ACCOUNTS ==={Colors.ENDC}")
    
    if not created_accounts:
        print(f"{Colors.RED}No accounts were successfully created.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.GREEN}Successfully created {len(created_accounts)} test accounts:{Colors.ENDC}")
    
    for i, account in enumerate(created_accounts, 1):
        # Find corresponding login result
        login_result = next((lr for lr in login_results if lr["account"] == account["name"]), None)
        
        print(f"\n{i}. {Colors.BOLD}{account['name']}{Colors.ENDC}")
        print(f"   Email: {account['email']}")
        print(f"   Username: {account['username']}")
        print(f"   Password: {account['password']}")
        print(f"   Roles: {account['roles']}")
        print(f"   Status: {account['status']}")
        print(f"   User ID: {account['id']}")
        
        if login_result:
            if login_result["success"]:
                if login_result.get("mfa_required"):
                    print(f"   Login Status: {Colors.YELLOW}✓ Success (MFA Required){Colors.ENDC}")
                else:
                    print(f"   Login Status: {Colors.GREEN}✓ Success{Colors.ENDC}")
            else:
                print(f"   Login Status: {Colors.RED}✗ Failed - {login_result.get('error', 'Unknown error')}{Colors.ENDC}")
        else:
            print(f"   Login Status: {Colors.YELLOW}Not tested{Colors.ENDC}")
    
    # Print credentials for easy copy-paste
    print(f"\n{Colors.BOLD}=== CREDENTIALS FOR TESTING ==={Colors.ENDC}")
    for account in created_accounts:
        print(f"{account['username']} / {account['password']} ({account['name']})")

def main():
    """Main test execution"""
    print(f"{Colors.BOLD}Test User Creation for Mission Workflow Testing{Colors.ENDC}")
    print(f"Auth Service URL: {AUTH_BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Create test accounts
    created_accounts = create_test_accounts()
    
    # Step 2: Test logins
    login_results = []
    if created_accounts:
        login_results = test_account_logins(created_accounts)
    
    # Step 3: Print summary
    print_summary(created_accounts, login_results)
    
    # Return success status
    success_count = len([acc for acc in created_accounts])
    login_success_count = len([lr for lr in login_results if lr["success"]])
    
    print(f"\n{Colors.BOLD}=== TEST RESULTS ==={Colors.ENDC}")
    print(f"Accounts Created: {success_count}/3")
    print(f"Logins Successful: {login_success_count}/{len(created_accounts) if created_accounts else 0}")
    
    if success_count == 3 and login_success_count >= 2:  # Allow for MFA cases
        print(f"{Colors.GREEN}✓ Test completed successfully{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}✗ Test completed with issues{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)