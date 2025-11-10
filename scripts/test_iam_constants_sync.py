#!/usr/bin/env python3
"""
Test IAM Constants Synchronization
Verifies that frontend and backend IAM constants are in sync
"""

import sys
import os
import json
import re
from pathlib import Path

# Add auth-microservice to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'auth-microservice'))

# Colors for output
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

def extract_backend_constants():
    """Extract constants from backend iam_constants.py"""
    backend_file = Path(__file__).parent.parent / 'auth-microservice' / 'awana_auth' / 'core' / 'iam_constants.py'
    
    if not backend_file.exists():
        log_test("Backend File Check", "FAIL", f"File not found: {backend_file}")
        return None
    
    with open(backend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    constants = {
        'groups': {},
        'profiles': {},
        'permissions': {},
        'validation_types': {},
        'user_roles': {}
    }
    
    # Extract IAMGroups
    groups_match = re.search(r'class IAMGroups:.*?(?=class|\Z)', content, re.DOTALL)
    if groups_match:
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', groups_match.group()):
            constants['groups'][match.group(1)] = match.group(2)
    
    # Extract IAMProfiles
    profiles_match = re.search(r'class IAMProfiles:.*?(?=class|\Z)', content, re.DOTALL)
    if profiles_match:
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', profiles_match.group()):
            constants['profiles'][match.group(1)] = match.group(2)
    
    # Extract IAMPermissions
    permissions_match = re.search(r'class IAMPermissions:.*?(?=class|\Z)', content, re.DOTALL)
    if permissions_match:
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', permissions_match.group()):
            constants['permissions'][match.group(1)] = match.group(2)
    
    # Extract ValidationTypes
    validation_match = re.search(r'class ValidationTypes:.*?(?=class|\Z)', content, re.DOTALL)
    if validation_match:
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', validation_match.group()):
            constants['validation_types'][match.group(1)] = match.group(2)
    
    # Extract UserRoles
    roles_match = re.search(r'class UserRoles:.*?(?=class|\Z)', content, re.DOTALL)
    if roles_match:
        for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', roles_match.group()):
            constants['user_roles'][match.group(1)] = match.group(2)
    
    return constants

def extract_frontend_constants():
    """Extract constants from frontend iamConstants.ts"""
    frontend_file = Path(__file__).parent.parent / 'apps' / 'web' / 'src' / 'constants' / 'iamConstants.ts'
    
    if not frontend_file.exists():
        log_test("Frontend File Check", "FAIL", f"File not found: {frontend_file}")
        return None
    
    with open(frontend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    constants = {
        'groups': {},
        'profiles': {},
        'permissions': {},
        'validation_types': {},
        'user_roles': {}
    }
    
    # Extract IAMGroups
    groups_match = re.search(r'export const IAMGroups\s*=\s*{([^}]+)}', content, re.DOTALL)
    if groups_match:
        for match in re.finditer(r'(\w+):\s*[\'"]([^\'\"]+)[\'"]', groups_match.group(1)):
            constants['groups'][match.group(1)] = match.group(2)
    
    # Extract IAMProfiles
    profiles_match = re.search(r'export const IAMProfiles\s*=\s*{([^}]+)}', content, re.DOTALL)
    if profiles_match:
        for match in re.finditer(r'(\w+):\s*[\'"]([^\'\"]+)[\'"]', profiles_match.group(1)):
            constants['profiles'][match.group(1)] = match.group(2)
    
    # Extract IAMPermissions
    permissions_match = re.search(r'export const IAMPermissions\s*=\s*{([^}]+)}', content, re.DOTALL)
    if permissions_match:
        for match in re.finditer(r'(\w+):\s*[\'"]([^\'\"]+)[\'"]', permissions_match.group(1)):
            constants['permissions'][match.group(1)] = match.group(2)
    
    # Extract ValidationTypes
    validation_match = re.search(r'export const ValidationTypes\s*=\s*{([^}]+)}', content, re.DOTALL)
    if validation_match:
        for match in re.finditer(r'(\w+):\s*[\'"]([^\'\"]+)[\'"]', validation_match.group(1)):
            constants['validation_types'][match.group(1)] = match.group(2)
    
    # Extract UserRoles
    roles_match = re.search(r'export const UserRoles\s*=\s*{([^}]+)}', content, re.DOTALL)
    if roles_match:
        for match in re.finditer(r'(\w+):\s*[\'"]([^\'\"]+)[\'"]', roles_match.group(1)):
            constants['user_roles'][match.group(1)] = match.group(2)
    
    return constants

def compare_constants(backend, frontend, category_name):
    """Compare backend and frontend constants for a category"""
    all_passed = True
    
    # Check keys present in backend but missing in frontend
    backend_only = set(backend.keys()) - set(frontend.keys())
    if backend_only:
        log_test(f"{category_name} - Missing in Frontend", "FAIL", 
                f"Constants present in backend but missing in frontend: {backend_only}")
        all_passed = False
    
    # Check keys present in frontend but missing in backend
    frontend_only = set(frontend.keys()) - set(backend.keys())
    if frontend_only:
        log_test(f"{category_name} - Missing in Backend", "FAIL", 
                f"Constants present in frontend but missing in backend: {frontend_only}")
        all_passed = False
    
    # Check values match for common keys
    common_keys = set(backend.keys()) & set(frontend.keys())
    mismatched = []
    for key in common_keys:
        if backend[key] != frontend[key]:
            mismatched.append(f"{key}: backend='{backend[key]}', frontend='{frontend[key]}'")
            all_passed = False
    
    if mismatched:
        log_test(f"{category_name} - Value Mismatch", "FAIL", 
                f"Mismatched values: {', '.join(mismatched)}")
    
    if all_passed and backend and frontend:
        log_test(f"{category_name} Sync Check", "PASS", 
                f"{len(common_keys)} constants verified")
    
    return all_passed

def main():
    """Main test function"""
    print(f"\n{Colors.BOLD}=== IAM Constants Synchronization Test ==={Colors.ENDC}\n")
    
    # Extract constants
    print(f"{Colors.BLUE}Extracting Backend Constants...{Colors.ENDC}")
    backend = extract_backend_constants()
    if not backend:
        return 1
    
    print(f"{Colors.BLUE}Extracting Frontend Constants...{Colors.ENDC}\n")
    frontend = extract_frontend_constants()
    if not frontend:
        return 1
    
    # Compare constants
    all_tests_passed = True
    
    print(f"{Colors.BOLD}Comparing Constants...{Colors.ENDC}\n")
    
    all_tests_passed &= compare_constants(backend['groups'], frontend['groups'], "IAMGroups")
    all_tests_passed &= compare_constants(backend['profiles'], frontend['profiles'], "IAMProfiles")
    all_tests_passed &= compare_constants(backend['permissions'], frontend['permissions'], "IAMPermissions")
    all_tests_passed &= compare_constants(backend['validation_types'], frontend['validation_types'], "ValidationTypes")
    all_tests_passed &= compare_constants(backend['user_roles'], frontend['user_roles'], "UserRoles")
    
    # Summary
    print(f"\n{Colors.BOLD}=== Summary ==={Colors.ENDC}\n")
    
    total_backend = sum(len(v) for v in backend.values())
    total_frontend = sum(len(v) for v in frontend.values())
    
    print(f"Backend Constants: {total_backend}")
    print(f"Frontend Constants: {total_frontend}")
    
    if all_tests_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED{Colors.ENDC}")
        print(f"{Colors.GREEN}Frontend and Backend constants are perfectly synchronized!{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ TESTS FAILED{Colors.ENDC}")
        print(f"{Colors.RED}Frontend and Backend constants are NOT synchronized!{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please update the constants to match in both files.{Colors.ENDC}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
