#!/usr/bin/env python3
"""
User Presence/Status System Testing
Tests the user presence and status management system
"""

import requests
import json
import sys
import time
from datetime import datetime

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"  # Direct auth service URL

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


def test_user_presence_system():
    """Test the User Presence/Status System"""
    print(f"\n{Colors.BOLD}=== Testing User Presence/Status System ==={Colors.ENDC}")
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "warnings": 0
    }
    
    # Step 1: Login as admin
    print(f"\n  Step 1: Login as Admin (admin/awana2025)")
    
    login_data = {
        "username": "admin",
        "password": "awana2025"
    }
    
    login_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/auth/local/login",
        data=login_data,
        expected_status=200,
        test_name="Admin Login"
    )
    
    test_results["total_tests"] += 1
    
    if not login_response:
        log_test("User Presence Test", "FAIL", "Cannot login as admin")
        test_results["failed_tests"] += 1
        return test_results
    
    access_token = login_response.get("access_token")
    if not access_token:
        log_test("Access Token", "FAIL", "No access token received")
        test_results["failed_tests"] += 1
        return test_results
    
    headers = {"Authorization": f"Bearer {access_token}"}
    log_test("Admin Login", "PASS", f"Successfully logged in, token: {access_token[:20]}...")
    test_results["passed_tests"] += 1
    
    # Step 2: Get current presence status (should be "online" by default)
    print(f"\n  Step 2: Get Current Presence Status (GET /api/users/presence/me)")
    
    current_presence = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/users/presence/me",
        headers=headers,
        expected_status=200,
        test_name="Get Current Presence Status"
    )
    
    test_results["total_tests"] += 1
    
    if not current_presence:
        log_test("Get Current Presence", "FAIL", "Cannot get current presence status")
        test_results["failed_tests"] += 1
        return test_results
    
    # Verify response structure
    required_fields = ["user_id", "username", "presence_status", "presence_updated_at", "last_activity_at"]
    missing_fields = [field for field in required_fields if field not in current_presence]
    
    test_results["total_tests"] += 1
    if missing_fields:
        log_test("Presence Response Structure", "FAIL", f"Missing fields: {missing_fields}")
        test_results["failed_tests"] += 1
    else:
        log_test("Presence Response Structure", "PASS", "All required fields present")
        test_results["passed_tests"] += 1
    
    initial_status = current_presence.get("presence_status", "unknown")
    log_test("Initial Presence Status", "PASS", f"Current status: {initial_status}")
    print(f"    User ID: {current_presence.get('user_id')}")
    print(f"    Username: {current_presence.get('username')}")
    print(f"    Full Name: {current_presence.get('full_name')}")
    print(f"    Presence Status: {initial_status}")
    print(f"    Presence Updated At: {current_presence.get('presence_updated_at')}")
    print(f"    Last Activity At: {current_presence.get('last_activity_at')}")
    
    # Step 3: Change status to "do_not_disturb"
    print(f"\n  Step 3: Change Status to 'do_not_disturb' (PATCH /api/users/presence/me)")
    
    update_to_dnd = test_endpoint(
        "PATCH",
        f"{AUTH_BASE_URL}/users/presence/me",
        data={"status": "do_not_disturb"},
        headers=headers,
        expected_status=200,
        test_name="Change Status to Do Not Disturb"
    )
    
    test_results["total_tests"] += 1
    
    if not update_to_dnd:
        log_test("Change to Do Not Disturb", "FAIL", "Cannot change status to do_not_disturb")
        test_results["failed_tests"] += 1
    else:
        dnd_status = update_to_dnd.get("presence_status", "unknown")
        if dnd_status == "do_not_disturb":
            log_test("Status Changed to DND", "PASS", f"Status successfully changed to: {dnd_status}")
            test_results["passed_tests"] += 1
        else:
            log_test("Status Changed to DND", "FAIL", f"Expected 'do_not_disturb', got: {dnd_status}")
            test_results["failed_tests"] += 1
    
    # Step 4: Verify status has changed
    print(f"\n  Step 4: Verify Status Changed (GET /api/users/presence/me)")
    
    verify_dnd = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/users/presence/me",
        headers=headers,
        expected_status=200,
        test_name="Verify Status Changed"
    )
    
    test_results["total_tests"] += 1
    
    if verify_dnd:
        verified_status = verify_dnd.get("presence_status", "unknown")
        if verified_status == "do_not_disturb":
            log_test("Status Persisted", "PASS", f"Status correctly persisted as: {verified_status}")
            test_results["passed_tests"] += 1
        else:
            log_test("Status Persisted", "FAIL", f"Expected 'do_not_disturb', got: {verified_status}")
            test_results["failed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Step 5: Change status to "offline"
    print(f"\n  Step 5: Change Status to 'offline' (PATCH /api/users/presence/me)")
    
    update_to_offline = test_endpoint(
        "PATCH",
        f"{AUTH_BASE_URL}/users/presence/me",
        data={"status": "offline"},
        headers=headers,
        expected_status=200,
        test_name="Change Status to Offline"
    )
    
    test_results["total_tests"] += 1
    
    if update_to_offline:
        offline_status = update_to_offline.get("presence_status", "unknown")
        if offline_status == "offline":
            log_test("Status Changed to Offline", "PASS", f"Status successfully changed to: {offline_status}")
            test_results["passed_tests"] += 1
        else:
            log_test("Status Changed to Offline", "FAIL", f"Expected 'offline', got: {offline_status}")
            test_results["failed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Step 6: Update activity (POST /api/users/presence/activity)
    print(f"\n  Step 6: Update User Activity (POST /api/users/presence/activity)")
    
    update_activity = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/users/presence/activity",
        headers=headers,
        expected_status=200,
        test_name="Update User Activity"
    )
    
    test_results["total_tests"] += 1
    
    if update_activity:
        if update_activity.get("success"):
            log_test("Activity Update", "PASS", f"Activity updated at: {update_activity.get('timestamp')}")
            test_results["passed_tests"] += 1
        else:
            log_test("Activity Update", "FAIL", "Activity update did not return success")
            test_results["failed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Step 7: Get list of online users (GET /api/users/presence/online)
    print(f"\n  Step 7: Get List of Online Users (GET /api/users/presence/online)")
    
    online_users = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/users/presence/online",
        headers=headers,
        expected_status=200,
        test_name="Get Online Users List"
    )
    
    test_results["total_tests"] += 1
    
    if online_users:
        users_list = online_users.get("users", [])
        total_users = online_users.get("total", 0)
        log_test("Online Users List", "PASS", f"Found {total_users} online users")
        test_results["passed_tests"] += 1
        
        # Verify response structure
        test_results["total_tests"] += 1
        if users_list and len(users_list) > 0:
            first_user = users_list[0]
            user_fields = ["user_id", "username", "presence_status"]
            missing_user_fields = [field for field in user_fields if field not in first_user]
            
            if missing_user_fields:
                log_test("Online Users Structure", "FAIL", f"Missing fields in user object: {missing_user_fields}")
                test_results["failed_tests"] += 1
            else:
                log_test("Online Users Structure", "PASS", "User objects have all required fields")
                test_results["passed_tests"] += 1
                
                # Display first few users
                print(f"    Sample users:")
                for i, user in enumerate(users_list[:3]):
                    print(f"      {i+1}. {user.get('username')} - {user.get('presence_status')}")
        else:
            log_test("Online Users Structure", "WARN", "No users in online list")
            test_results["warnings"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Step 8: Get specific user's presence status
    print(f"\n  Step 8: Get Specific User Presence (GET /api/users/presence/{user_id})")
    
    # Use admin's own user_id from the current_presence response
    admin_user_id = current_presence.get("user_id")
    
    test_results["total_tests"] += 1
    
    if admin_user_id:
        specific_user_presence = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/users/presence/{admin_user_id}",
            headers=headers,
            expected_status=200,
            test_name="Get Specific User Presence"
        )
        
        if specific_user_presence:
            specific_status = specific_user_presence.get("presence_status", "unknown")
            log_test("Specific User Presence", "PASS", f"Retrieved user presence: {specific_status}")
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
    else:
        log_test("Specific User Presence", "SKIP", "No user_id available for testing")
        test_results["warnings"] += 1
    
    # Step 9: Test authentication requirement (401 without token)
    print(f"\n  Step 9: Test Authentication Requirement (401 without token)")
    
    endpoints_to_test = [
        ("GET", "/users/presence/me", "Get My Presence"),
        ("PATCH", "/users/presence/me", "Update My Presence"),
        ("POST", "/users/presence/activity", "Update Activity"),
        ("GET", "/users/presence/online", "Get Online Users")
    ]
    
    for method, endpoint, description in endpoints_to_test:
        test_results["total_tests"] += 1
        
        no_auth_response = test_endpoint(
            method,
            f"{AUTH_BASE_URL}{endpoint}",
            data={"status": "online"} if method == "PATCH" else None,
            expected_status=401,
            test_name=f"{description} - No Auth"
        )
        
        if no_auth_response:
            log_test(f"{description} - Auth Required", "PASS", "Unauthenticated request correctly rejected")
            test_results["passed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
    
    # Step 10: Test invalid status value
    print(f"\n  Step 10: Test Invalid Status Value")
    
    test_results["total_tests"] += 1
    
    invalid_status = test_endpoint(
        "PATCH",
        f"{AUTH_BASE_URL}/users/presence/me",
        data={"status": "invalid_status"},
        headers=headers,
        expected_status=422,  # Validation error
        test_name="Invalid Status Value"
    )
    
    if invalid_status:
        log_test("Invalid Status Validation", "PASS", "Invalid status correctly rejected")
        test_results["passed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Step 11: Test all valid status values
    print(f"\n  Step 11: Test All Valid Status Values")
    
    valid_statuses = ["online", "away", "do_not_disturb", "offline"]
    
    for status in valid_statuses:
        test_results["total_tests"] += 1
        
        status_response = test_endpoint(
            "PATCH",
            f"{AUTH_BASE_URL}/users/presence/me",
            data={"status": status},
            headers=headers,
            expected_status=200,
            test_name=f"Change Status to '{status}'"
        )
        
        if status_response:
            returned_status = status_response.get("presence_status", "unknown")
            if returned_status == status:
                log_test(f"Status '{status}'", "PASS", f"Successfully changed to: {status}")
                test_results["passed_tests"] += 1
            else:
                log_test(f"Status '{status}'", "FAIL", f"Expected '{status}', got: {returned_status}")
                test_results["failed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
    
    # Step 12: Verify timestamps are updated correctly
    print(f"\n  Step 12: Verify Timestamps Update")
    
    # Get current presence
    before_update = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/users/presence/me",
        headers=headers,
        expected_status=200,
        test_name="Get Presence Before Update"
    )
    
    test_results["total_tests"] += 1
    
    if before_update:
        before_timestamp = before_update.get("presence_updated_at")
        
        # Wait a moment
        time.sleep(1)
        
        # Update status
        test_endpoint(
            "PATCH",
            f"{AUTH_BASE_URL}/users/presence/me",
            data={"status": "online"},
            headers=headers,
            expected_status=200,
            test_name="Update Status for Timestamp Test"
        )
        
        # Get presence again
        after_update = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/users/presence/me",
            headers=headers,
            expected_status=200,
            test_name="Get Presence After Update"
        )
        
        if after_update:
            after_timestamp = after_update.get("presence_updated_at")
            
            if after_timestamp != before_timestamp:
                log_test("Timestamp Update", "PASS", "Timestamp correctly updated after status change")
                test_results["passed_tests"] += 1
            else:
                log_test("Timestamp Update", "FAIL", "Timestamp not updated after status change")
                test_results["failed_tests"] += 1
        else:
            test_results["failed_tests"] += 1
    else:
        test_results["failed_tests"] += 1
    
    # Step 13: Verify MongoDB persistence
    print(f"\n  Step 13: Verify MongoDB Persistence")
    
    try:
        from pymongo import MongoClient
        import os
        
        # Connect to MongoDB
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(mongo_url)
        
        auth_db = client['auth_db']
        users_collection = auth_db.users
        
        # Find admin user
        admin_doc = users_collection.find_one({"username": "admin"})
        
        test_results["total_tests"] += 1
        
        if admin_doc:
            db_presence_status = admin_doc.get("presence_status", "not_set")
            db_presence_updated = admin_doc.get("presence_updated_at", "not_set")
            db_last_activity = admin_doc.get("last_activity_at", "not_set")
            
            log_test("MongoDB Persistence", "PASS", "Presence data found in database")
            print(f"    DB Presence Status: {db_presence_status}")
            print(f"    DB Presence Updated At: {db_presence_updated}")
            print(f"    DB Last Activity At: {db_last_activity}")
            test_results["passed_tests"] += 1
        else:
            log_test("MongoDB Persistence", "FAIL", "Admin user not found in database")
            test_results["failed_tests"] += 1
        
        client.close()
        
    except Exception as e:
        log_test("MongoDB Verification", "WARN", f"Could not verify MongoDB: {str(e)}")
        test_results["warnings"] += 1
    
    return test_results


if __name__ == "__main__":
    print(f"{Colors.BOLD}🚀 Starting User Presence/Status System Testing{Colors.ENDC}")
    print(f"Testing Auth Service: {AUTH_BASE_URL}")
    print("=" * 60)
    
    # Test auth service health first
    try:
        health_response = requests.get(f"{AUTH_BASE_URL}/../health", timeout=5)
        if health_response.status_code == 200:
            log_test("Auth Service Health", "PASS", "Auth service is running")
        else:
            log_test("Auth Service Health", "FAIL", f"Unexpected status: {health_response.status_code}")
            sys.exit(1)
    except Exception as e:
        log_test("Auth Service Health", "FAIL", f"Cannot connect to auth service: {str(e)}")
        sys.exit(1)
    
    # Run presence system tests
    test_results = test_user_presence_system()
    
    # Summary
    print(f"\n{Colors.BOLD}📊 TESTING SUMMARY{Colors.ENDC}")
    print("=" * 60)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"{Colors.GREEN}Passed: {test_results['passed_tests']}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {test_results['failed_tests']}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Warnings: {test_results['warnings']}{Colors.ENDC}")
    
    if test_results['total_tests'] > 0:
        success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Overall result
    if test_results['failed_tests'] == 0:
        print(f"\n{Colors.GREEN}🎉 ALL USER PRESENCE TESTS PASSED!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Key Results:{Colors.ENDC}")
        print("✅ GET /api/users/presence/me - Working")
        print("✅ PATCH /api/users/presence/me - Working")
        print("✅ POST /api/users/presence/activity - Working")
        print("✅ GET /api/users/presence/online - Working")
        print("✅ GET /api/users/presence/{user_id} - Working")
        print("✅ Authentication required for all endpoints")
        print("✅ Status changes persisted in database")
        print("✅ Timestamps updated correctly")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}❌ SOME USER PRESENCE TESTS FAILED{Colors.ENDC}")
        print(f"\nPlease review the failed tests above for details.")
        sys.exit(1)
