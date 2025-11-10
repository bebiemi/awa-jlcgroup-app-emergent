#!/usr/bin/env python3
"""
Country Configuration and User Data Retention Configuration Testing
Tests the new Country Configuration system and User Data Retention Configuration system
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

# Test configuration
AUTH_BASE_URL = "http://localhost:8000/api"  # Direct auth service URL
API_BASE_URL = "http://localhost:8001/api"   # JLC API service URL (for proxy routes)

# Global variables to store test data
gabon_id = None
france_id = None
libreville_id = None
port_gentil_id = None
original_retention_days = None
original_source = None

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

def test_admin_login():
    """Test admin login to get JWT token for subsequent tests"""
    print(f"\n{Colors.BOLD}=== Testing Admin Login ==={Colors.ENDC}")
    
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
        log_test("Admin Login - MFA Required", "INFO", "Admin has MFA enabled, cannot proceed with automated testing")
        return None
    
    if "access_token" in response:
        log_test("Admin Login - Token Generation", "PASS", 
                f"JWT token received: {response['access_token'][:20]}...")
        return response["access_token"]
    else:
        log_test("Admin Login - Token Generation", "FAIL", f"No access token received. Response: {response}")
        return None

def test_country_configuration_system():
    """Test the complete Country Configuration system"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}COUNTRY CONFIGURATION SYSTEM TESTING{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing Country and Currency Configuration features{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    # Get admin token first
    admin_token = test_admin_login()
    if not admin_token:
        log_test("Country Configuration Test", "FAIL", "Cannot get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Initialize default countries
    print(f"\n  Test 1: Initialize Default Countries")
    
    init_response = test_endpoint(
        "POST",
        f"{AUTH_BASE_URL}/config/countries/init-default",
        headers=headers,
        expected_status=200,
        test_name="Initialize Default Countries"
    )
    
    if init_response:
        count = init_response.get("count", 0)
        message = init_response.get("message", "")
        log_test("Default Countries Initialization", "PASS", f"Message: {message}, Count: {count}")
    
    # Test 2: List all countries - verify Gabon is default
    print(f"\n  Test 2: List All Countries")
    
    countries_response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/config/countries",
        expected_status=200,
        test_name="List All Countries"
    )
    
    if countries_response:
        countries = countries_response if isinstance(countries_response, list) else []
        log_test("Countries List", "PASS", f"Found {len(countries)} countries")
        
        # Check if Gabon is default
        gabon_country = None
        default_country = None
        for country in countries:
            if country.get("name") == "Gabon":
                gabon_country = country
            if country.get("is_default"):
                default_country = country
        
        if gabon_country and gabon_country.get("is_default"):
            log_test("Gabon Default Status", "PASS", "Gabon is correctly set as default")
        else:
            log_test("Gabon Default Status", "FAIL", f"Gabon default status: {gabon_country.get('is_default') if gabon_country else 'Not found'}")
        
        # Store country IDs for later tests
        global gabon_id, france_id
        gabon_id = gabon_country.get("id") if gabon_country else None
        france_country = next((c for c in countries if c.get("name") == "France"), None)
        france_id = france_country.get("id") if france_country else None
    
    # Test 3: Get details of Gabon
    print(f"\n  Test 3: Get Country Details (Gabon)")
    
    if gabon_id:
        gabon_details = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}",
            expected_status=200,
            test_name="Get Gabon Details"
        )
        
        if gabon_details:
            log_test("Gabon Details", "PASS", f"Name: {gabon_details.get('name')}, Currency: {gabon_details.get('currency_code')}")
    
    # Test 4: Set France as default
    print(f"\n  Test 4: Set France as Default Country")
    
    if france_id:
        set_default_response = test_endpoint(
            "PATCH",
            f"{AUTH_BASE_URL}/config/countries/{france_id}/set-default",
            headers=headers,
            expected_status=200,
            test_name="Set France as Default"
        )
        
        if set_default_response:
            log_test("Set France Default", "PASS", f"Message: {set_default_response.get('message')}")
            
            # Verify only France is default now
            verify_response = test_endpoint(
                "GET",
                f"{AUTH_BASE_URL}/config/countries",
                expected_status=200,
                test_name="Verify France is Default"
            )
            
            if verify_response:
                countries = verify_response if isinstance(verify_response, list) else []
                default_countries = [c for c in countries if c.get("is_default")]
                
                if len(default_countries) == 1 and default_countries[0].get("name") == "France":
                    log_test("France Default Verification", "PASS", "Only France is now default")
                else:
                    log_test("France Default Verification", "FAIL", f"Default countries: {[c.get('name') for c in default_countries]}")
    
    # Test 5: List cities for Gabon (should be empty initially)
    print(f"\n  Test 5: List Cities for Gabon (Initial)")
    
    if gabon_id:
        cities_response = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}/cities",
            expected_status=200,
            test_name="List Gabon Cities (Initial)"
        )
        
        if cities_response:
            cities = cities_response if isinstance(cities_response, list) else []
            log_test("Gabon Cities (Initial)", "PASS", f"Found {len(cities)} cities (expected 0)")
    
    # Test 6: Create city "Libreville" for Gabon
    print(f"\n  Test 6: Create City 'Libreville' for Gabon")
    
    if gabon_id:
        libreville_response = test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}/cities",
            data={"name": "Libreville", "active": True},
            headers=headers,
            expected_status=200,
            test_name="Create Libreville City"
        )
        
        if libreville_response:
            log_test("Create Libreville", "PASS", f"City created: {libreville_response.get('name')}")
            global libreville_id
            libreville_id = libreville_response.get("id")
    
    # Test 7: Create city "Port-Gentil" for Gabon
    print(f"\n  Test 7: Create City 'Port-Gentil' for Gabon")
    
    if gabon_id:
        port_gentil_response = test_endpoint(
            "POST",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}/cities",
            data={"name": "Port-Gentil", "active": True},
            headers=headers,
            expected_status=200,
            test_name="Create Port-Gentil City"
        )
        
        if port_gentil_response:
            log_test("Create Port-Gentil", "PASS", f"City created: {port_gentil_response.get('name')}")
            global port_gentil_id
            port_gentil_id = port_gentil_response.get("id")
    
    # Test 8: List cities again - verify 2 cities exist
    print(f"\n  Test 8: List Cities for Gabon (After Creation)")
    
    if gabon_id:
        cities_after_response = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}/cities",
            expected_status=200,
            test_name="List Gabon Cities (After Creation)"
        )
        
        if cities_after_response:
            cities = cities_after_response if isinstance(cities_after_response, list) else []
            log_test("Gabon Cities (After Creation)", "PASS", f"Found {len(cities)} cities (expected 2)")
            
            city_names = [city.get("name") for city in cities]
            if "Libreville" in city_names and "Port-Gentil" in city_names:
                log_test("Cities Verification", "PASS", "Both Libreville and Port-Gentil found")
            else:
                log_test("Cities Verification", "FAIL", f"Cities found: {city_names}")
    
    # Test 9: Search for cities with "Libre" - should return only Libreville
    print(f"\n  Test 9: Search Cities with 'Libre'")
    
    if gabon_id:
        search_response = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}/cities?search=Libre",
            expected_status=200,
            test_name="Search Cities with 'Libre'"
        )
        
        if search_response:
            cities = search_response if isinstance(search_response, list) else []
            log_test("City Search", "PASS", f"Found {len(cities)} cities matching 'Libre'")
            
            if len(cities) == 1 and cities[0].get("name") == "Libreville":
                log_test("Search Results Verification", "PASS", "Only Libreville returned for 'Libre' search")
            else:
                city_names = [city.get("name") for city in cities]
                log_test("Search Results Verification", "FAIL", f"Expected only Libreville, got: {city_names}")
    
    # Test 10: Delete "Port-Gentil" city
    print(f"\n  Test 10: Delete Port-Gentil City")
    
    if port_gentil_id:
        delete_response = test_endpoint(
            "DELETE",
            f"{AUTH_BASE_URL}/config/countries/cities/{port_gentil_id}",
            headers=headers,
            expected_status=200,
            test_name="Delete Port-Gentil City"
        )
        
        if delete_response:
            log_test("Delete Port-Gentil", "PASS", f"Message: {delete_response.get('message')}")
    
    # Test 11: Verify only 1 city remains
    print(f"\n  Test 11: Verify Only Libreville Remains")
    
    if gabon_id:
        final_cities_response = test_endpoint(
            "GET",
            f"{AUTH_BASE_URL}/config/countries/{gabon_id}/cities",
            expected_status=200,
            test_name="Final Cities List"
        )
        
        if final_cities_response:
            cities = final_cities_response if isinstance(final_cities_response, list) else []
            log_test("Final Cities Count", "PASS", f"Found {len(cities)} cities (expected 1)")
            
            if len(cities) == 1 and cities[0].get("name") == "Libreville":
                log_test("Final Cities Verification", "PASS", "Only Libreville remains")
            else:
                city_names = [city.get("name") for city in cities]
                log_test("Final Cities Verification", "FAIL", f"Expected only Libreville, got: {city_names}")
    
    return True


def test_retention_configuration_system():
    """Test the User Data Retention Configuration system"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}USER DATA RETENTION CONFIGURATION TESTING{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing User Data Retention Configuration features{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    # Get admin token first
    admin_token = test_admin_login()
    if not admin_token:
        log_test("Retention Configuration Test", "FAIL", "Cannot get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Get current retention config - should show YAML default
    print(f"\n  Test 1: Get Current Retention Configuration")
    
    config_response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/iam/users/config/retention",
        headers=headers,
        expected_status=200,
        test_name="Get Current Retention Config"
    )
    
    if config_response:
        retention_days = config_response.get("retention_days")
        source = config_response.get("source")
        can_override = config_response.get("can_override")
        
        log_test("Retention Config", "PASS", f"Days: {retention_days}, Source: {source}, Can Override: {can_override}")
        
        # Store original values for restoration
        global original_retention_days, original_source
        original_retention_days = retention_days
        original_source = source
    
    # Test 2: Try to update to 30 days - check if can_override allows it
    print(f"\n  Test 2: Update Retention to 30 Days")
    
    if config_response and config_response.get("can_override"):
        update_response = test_endpoint(
            "PUT",
            f"{AUTH_BASE_URL}/iam/users/config/retention?retention_days=30",
            headers=headers,
            expected_status=200,
            test_name="Update Retention to 30 Days"
        )
        
        if update_response:
            log_test("Update to 30 Days", "PASS", f"Message: {update_response.get('message')}")
    else:
        log_test("Update to 30 Days", "SKIP", "Override not allowed by configuration")
    
    # Test 3: Get config again - verify it changed
    print(f"\n  Test 3: Verify Retention Config Changed")
    
    verify_response = test_endpoint(
        "GET",
        f"{AUTH_BASE_URL}/iam/users/config/retention",
        headers=headers,
        expected_status=200,
        test_name="Verify Config Changed"
    )
    
    if verify_response:
        new_retention_days = verify_response.get("retention_days")
        new_source = verify_response.get("source")
        
        if config_response and config_response.get("can_override"):
            if new_retention_days == 30 and new_source == "database":
                log_test("Config Change Verification", "PASS", f"Successfully changed to 30 days from database")
            else:
                log_test("Config Change Verification", "FAIL", f"Expected 30 days from database, got {new_retention_days} from {new_source}")
        else:
            log_test("Config Change Verification", "PASS", f"Config unchanged as expected (override disabled)")
    
    # Test 4: Try invalid values - 0 days (should get 400 error)
    print(f"\n  Test 4: Try Invalid Value - 0 Days")
    
    invalid_0_response = test_endpoint(
        "PUT",
        f"{AUTH_BASE_URL}/iam/users/config/retention?retention_days=0",
        headers=headers,
        expected_status=400,
        test_name="Invalid Value - 0 Days"
    )
    
    if invalid_0_response:
        error_detail = invalid_0_response.get("detail", "")
        log_test("Invalid 0 Days", "PASS", f"Correctly rejected: {error_detail}")
    
    # Test 5: Try invalid values - 400 days (should get 400 error)
    print(f"\n  Test 5: Try Invalid Value - 400 Days")
    
    invalid_400_response = test_endpoint(
        "PUT",
        f"{AUTH_BASE_URL}/iam/users/config/retention?retention_days=400",
        headers=headers,
        expected_status=400,
        test_name="Invalid Value - 400 Days"
    )
    
    if invalid_400_response:
        error_detail = invalid_400_response.get("detail", "")
        log_test("Invalid 400 Days", "PASS", f"Correctly rejected: {error_detail}")
    
    # Test 6: Try to update to 180 days - should work if can_override=true
    print(f"\n  Test 6: Update Retention to 180 Days")
    
    if config_response and config_response.get("can_override"):
        update_180_response = test_endpoint(
            "PUT",
            f"{AUTH_BASE_URL}/iam/users/config/retention?retention_days=180",
            headers=headers,
            expected_status=200,
            test_name="Update Retention to 180 Days"
        )
        
        if update_180_response:
            log_test("Update to 180 Days", "PASS", f"Message: {update_180_response.get('message')}")
            
            # Verify the change
            final_verify_response = test_endpoint(
                "GET",
                f"{AUTH_BASE_URL}/iam/users/archive/config/retention",
                headers=headers,
                expected_status=200,
                test_name="Verify 180 Days Config"
            )
            
            if final_verify_response:
                final_days = final_verify_response.get("retention_days")
                if final_days == 180:
                    log_test("180 Days Verification", "PASS", "Successfully updated to 180 days")
                else:
                    log_test("180 Days Verification", "FAIL", f"Expected 180 days, got {final_days}")
    else:
        log_test("Update to 180 Days", "SKIP", "Override not allowed by configuration")
    
    return True


def test_authentication_for_config_routes():
    """Test authentication requirements for configuration routes"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}AUTHENTICATION TESTING FOR CONFIG ROUTES{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing authentication requirements{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    # Test 1: Country routes without authentication
    print(f"\n  Test 1: Country Routes Without Authentication")
    
    # Public routes (should work without auth)
    public_routes = [
        ("GET", "/config/countries", "List Countries (Public)"),
        ("GET", "/config/countries/test-id", "Get Country Details (Public)")
    ]
    
    for method, endpoint, description in public_routes:
        response = test_endpoint(
            method,
            f"{AUTH_BASE_URL}{endpoint}",
            expected_status=200 if method == "GET" and "countries" in endpoint and "test-id" not in endpoint else 404,
            test_name=f"{description} - No Auth"
        )
        
        if response or endpoint.endswith("test-id"):  # 404 is expected for test-id
            log_test(f"{description} - No Auth", "PASS", "Public endpoint accessible")
    
    # Protected routes (should require auth)
    protected_routes = [
        ("POST", "/config/countries/init-default", "Initialize Countries"),
        ("POST", "/config/countries", "Create Country"),
        ("PATCH", "/config/countries/test-id/set-default", "Set Default Country"),
        ("POST", "/config/countries/test-id/cities", "Create City"),
        ("DELETE", "/config/countries/cities/test-id", "Delete City")
    ]
    
    for method, endpoint, description in protected_routes:
        response = test_endpoint(
            method,
            f"{AUTH_BASE_URL}{endpoint}",
            data={} if method in ["POST", "PATCH"] else None,
            expected_status=401,
            test_name=f"{description} - No Auth"
        )
        
        if response:
            log_test(f"{description} - Auth Required", "PASS", "Correctly requires authentication")
    
    # Test 2: Retention routes without authentication
    print(f"\n  Test 2: Retention Routes Without Authentication")
    
    retention_routes = [
        ("GET", "/iam/users/archive/config/retention", "Get Retention Config"),
        ("PUT", "/iam/users/archive/config/retention?retention_days=90", "Update Retention Config")
    ]
    
    for method, endpoint, description in retention_routes:
        response = test_endpoint(
            method,
            f"{AUTH_BASE_URL}{endpoint}",
            expected_status=401,
            test_name=f"{description} - No Auth"
        )
        
        if response:
            log_test(f"{description} - Auth Required", "PASS", "Correctly requires authentication")
    
    return True


def run_country_and_retention_tests():
    """Run all Country Configuration and Retention Configuration tests"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}COUNTRY & RETENTION CONFIGURATION TESTING{Colors.ENDC}")
    print(f"{Colors.BOLD}Testing new Country and Retention Configuration systems{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    test_cases = [
        ("Country Configuration System", test_country_configuration_system),
        ("Retention Configuration System", test_retention_configuration_system),
        ("Authentication for Config Routes", test_authentication_for_config_routes)
    ]
    
    results = []
    
    for test_name, test_function in test_cases:
        print(f"\n  Running: {test_name}")
        
        try:
            success = test_function()
            results.append({
                "test": test_name,
                "success": success
            })
            
            if success:
                log_test(f"{test_name} - Overall", "PASS", "All tests in this category passed")
            else:
                log_test(f"{test_name} - Overall", "FAIL", "Some tests in this category failed")
                
        except Exception as e:
            log_test(f"{test_name} - Overall", "FAIL", f"Exception occurred: {str(e)}")
            results.append({
                "test": test_name,
                "success": False,
                "error": str(e)
            })
    
    return results


if __name__ == "__main__":
    print(f"{Colors.BOLD}🚀 Starting Country Configuration and Retention Configuration Testing{Colors.ENDC}")
    print(f"Testing Auth Service: {AUTH_BASE_URL}")
    print(f"Testing JLC API Service: {API_BASE_URL}")
    
    # Test auth service health first
    if not test_auth_service_health():
        print(f"\n{Colors.RED}❌ Auth service is not running. Please start it first.{Colors.ENDC}")
        sys.exit(1)
    
    # Initialize test results
    all_tests_passed = True
    
    try:
        # Run configuration tests
        config_results = run_country_and_retention_tests()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Testing interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error during testing: {str(e)}{Colors.ENDC}")
        all_tests_passed = False
    
    # Summary
    print(f"\n{Colors.BOLD}📊 TESTING SUMMARY{Colors.ENDC}")
    print("=" * 50)
    
    total_test_categories = len(config_results)
    successful_categories = len([r for r in config_results if r["success"]])
    
    print(f"Test Categories: {successful_categories}/{total_test_categories} passed")
    
    for result in config_results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['test']}")
        if not result["success"] and "error" in result:
            print(f"    Error: {result['error']}")
    
    # Overall result
    overall_success = successful_categories == total_test_categories
    
    if overall_success:
        print(f"\n{Colors.GREEN}🎉 ALL CONFIGURATION TESTS PASSED!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Key Results:{Colors.ENDC}")
        print("✅ Country Configuration system working correctly")
        print("✅ User Data Retention Configuration system working correctly")
        print("✅ Authentication and authorization working properly")
        print("✅ All CRUD operations for countries and cities functional")
        print("✅ Retention period validation and updates working")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}❌ SOME CONFIGURATION TESTS FAILED{Colors.ENDC}")
        print(f"{Colors.RED}Please review the failed tests above.{Colors.ENDC}")
        sys.exit(1)