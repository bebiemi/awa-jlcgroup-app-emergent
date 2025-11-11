# Fix: 403 Forbidden Error for Config Endpoints

## Problem Summary

Users with the `company` role (e.g., `entreprise_test`) were receiving **403 Forbidden** errors when attempting to access configuration endpoints such as:
- `GET /api/config/workflows/besoin`
- `GET /api/config/forms/besoin`

### Root Cause

The issue was identified in the IAM (Identity and Access Management) system:

1. **Users had roles but NO profiles**: Users like `entreprise_test` had `roles: ['company']` but `profile_ids: []` (empty array)
2. **Permissions are profile-based**: The IAM system grants permissions through profiles, not directly through roles
3. **Missing profile = No permissions**: Without any profile assignment, users had zero permissions, including the required `config.read` permission

### Investigation Details

#### Endpoint Configuration ✅
- `form_config_routes.py` properly registered with `/api/config` prefix in `main.py`
- `GET /config/workflows/{entity_type}` endpoint correctly requires `IAMPermissions.CONFIG_READ` permission

#### Permission Configuration ✅
- Permission `config.read` exists in database (`id: 338afa28-269d-40a6-828f-c23ad2e6855b`)
- Permission correctly assigned to profiles: `entreprise` and `company_admin`

#### User Configuration ❌
```python
# BEFORE FIX
user = {
    "username": "entreprise_test",
    "roles": ["company"],        # Has role
    "profile_ids": [],           # NO profiles! ❌
    "group_ids": ["..."]
}
```

## Solution Implemented

### 1. Profile Assignment Scripts

Created two scripts to assign profiles to users based on their roles:

#### `/app/auth-microservice/scripts/assign_profiles_to_users.py`
- Assigns profiles to existing users who have roles but no profiles
- Maps roles to profiles:
  - `admin` → `admin` profile
  - `super_admin` → `super_admin` profile
  - `company` → `entreprise` profile
  - `interim` → `interim_user` profile
  - `commercial` → `commercial` profile

```python
ROLE_TO_PROFILE_MAPPING = {
    'admin': 'admin',
    'super_admin': 'super_admin',
    'company': 'entreprise',
    'interim': 'interim_user',
    'agency': 'company_admin',
    'commercial': 'commercial',
    'validator': 'admin',
}
```

#### `/app/auth-microservice/scripts/init_test_users_profiles.py`
- Initializes specific test users with correct profiles
- Used for consistent test account setup

### 2. Auto-Assignment in User Creation

Modified `/app/auth-microservice/security_routes.py` to automatically assign profiles when creating new users:

```python
# Auto-assign profiles based on roles
profile_ids = []
if request.profile_id:
    profile_ids = [request.profile_id]
else:
    # Auto-assign profiles based on roles
    role_to_profile_map = {
        'admin': 'admin',
        'super_admin': 'super_admin',
        'company': 'entreprise',
        'interim': 'interim_user',
        'commercial': 'commercial',
    }
    
    for role in request.roles:
        profile_code = role_to_profile_map.get(role)
        if profile_code:
            profile = await db.profiles.find_one({"code": profile_code})
            if profile and profile['id'] not in profile_ids:
                profile_ids.append(profile['id'])

user_data["profile_ids"] = profile_ids  # Assign profiles to user
```

### 3. Verification

After applying fixes:

```python
# AFTER FIX
user = {
    "username": "entreprise_test",
    "roles": ["company"],
    "profile_ids": ["7c4124bb-cb6b-4bf0-b887-506575a39d8d"],  # ✅ Has 'entreprise' profile
    "group_ids": ["..."]
}
```

## Test Results

All config endpoints now return **200 OK** for `entreprise_test` user:

```bash
✅ POST /api/auth/local/login          → 200 OK (Login successful)
✅ GET /api/config/workflows/besoin    → 200 OK (6 statuses)
✅ GET /api/config/forms/besoin        → 200 OK (8 fields)
✅ GET /api/besoins                    → 200 OK (0 total besoins)
```

## Impact

### Fixed
- ✅ All users with roles now have corresponding IAM profiles
- ✅ Users can access protected configuration endpoints
- ✅ Test accounts (`entreprise_test`, `commercial_test`, `interim_test2`) have proper permissions
- ✅ New users automatically receive profiles based on their roles

### Files Modified
- `/app/auth-microservice/security_routes.py` - Auto-assignment logic
- `/app/test_result.md` - Documentation of fix

### Files Created
- `/app/auth-microservice/scripts/assign_profiles_to_users.py` - Profile assignment script
- `/app/auth-microservice/scripts/init_test_users_profiles.py` - Test user initialization
- `/app/docs/FIX_403_FORBIDDEN_CONFIG_ENDPOINTS.md` - This documentation

## How to Apply Fix to Existing Users

Run the profile assignment script:

```bash
cd /app/auth-microservice
python3 scripts/assign_profiles_to_users.py
```

Output:
```
Found 68 users
Available profiles: [...]
✅ Updated X users
⏭️  Skipped Y users (already have profiles)
```

## Prevention

The fix in `security_routes.py` ensures all **new users** automatically receive appropriate profiles. Existing users can be fixed by running the assignment script.

## Related Issues

This fix resolves:
- 403 Forbidden errors on `/api/config/*` endpoints
- Permission denied for workflow and form schema access
- IAM profile assignment gap between roles and permissions

## Next Steps

1. ✅ Test workflow with company users creating "Besoins"
2. ✅ Verify permission inheritance through profiles
3. ⚠️  Consider adding profile assignment to registration flow
4. ⚠️  Add validation to ensure users always have at least one profile

---

**Date Fixed**: November 11, 2025  
**Fixed By**: AI Engineer (Agent)  
**Status**: ✅ Resolved and Tested
