"""
Unit Tests for IAM Constants
Tests the consistency and correctness of IAM constants
"""
import pytest
from awana_auth.core.iam_constants import (
    IAMGroups,
    IAMProfiles,
    IAMPermissions,
    ValidationTypes,
    UserRoles,
    get_group_for_role,
    get_profile_for_role,
    get_validation_type_for_role
)


class TestIAMGroups:
    """Test IAM Groups constants"""
    
    def test_group_values_format(self):
        """Test that all group values follow grp.* format"""
        assert IAMGroups.CANDIDAT.startswith("grp.")
        assert IAMGroups.INTERIMAIRE.startswith("grp.")
        assert IAMGroups.COMPANY.startswith("grp.")
        assert IAMGroups.COLLABORATEUR.startswith("grp.")
        assert IAMGroups.ADMIN.startswith("grp.")
        assert IAMGroups.SUPER_ADMIN.startswith("grp.")
    
    def test_group_values_unique(self):
        """Test that all group values are unique"""
        groups = [
            IAMGroups.CANDIDAT,
            IAMGroups.INTERIMAIRE,
            IAMGroups.COMPANY,
            IAMGroups.COLLABORATEUR,
            IAMGroups.ADMIN,
            IAMGroups.SUPER_ADMIN
        ]
        assert len(groups) == len(set(groups)), "Group values must be unique"
    
    def test_group_specific_values(self):
        """Test specific group values"""
        assert IAMGroups.CANDIDAT == "grp.candidat"
        assert IAMGroups.INTERIMAIRE == "grp.interimaire"
        assert IAMGroups.COMPANY == "grp.company"
        assert IAMGroups.COLLABORATEUR == "grp.collaborateur"
        assert IAMGroups.ADMIN == "grp.admin"
        assert IAMGroups.SUPER_ADMIN == "grp.super_admin"


class TestIAMProfiles:
    """Test IAM Profiles constants"""
    
    def test_profile_values_format(self):
        """Test that all profile values follow role.* format"""
        assert IAMProfiles.CANDIDAT.startswith("role.")
        assert IAMProfiles.INTERIM_USER.startswith("role.")
        assert IAMProfiles.COMPANY_ADMIN.startswith("role.")
        assert IAMProfiles.COLLABORATEUR.startswith("role.")
        assert IAMProfiles.ADMIN.startswith("role.")
        assert IAMProfiles.SUPER_ADMIN.startswith("role.")
    
    def test_profile_values_unique(self):
        """Test that all profile values are unique"""
        profiles = [
            IAMProfiles.CANDIDAT,
            IAMProfiles.INTERIM_USER,
            IAMProfiles.COMPANY_ADMIN,
            IAMProfiles.COLLABORATEUR,
            IAMProfiles.ADMIN,
            IAMProfiles.SUPER_ADMIN
        ]
        assert len(profiles) == len(set(profiles)), "Profile values must be unique"
    
    def test_profile_specific_values(self):
        """Test specific profile values"""
        assert IAMProfiles.CANDIDAT == "role.candidat"
        assert IAMProfiles.INTERIM_USER == "role.interim_user"
        assert IAMProfiles.COMPANY_ADMIN == "role.company_admin"
        assert IAMProfiles.COLLABORATEUR == "role.collaborateur"
        assert IAMProfiles.ADMIN == "role.admin"
        assert IAMProfiles.SUPER_ADMIN == "role.super_admin"


class TestIAMPermissions:
    """Test IAM Permissions constants"""
    
    def test_permissions_format(self):
        """Test that permissions follow resource.action format"""
        permissions = [
            IAMPermissions.MISSIONS_BROWSE,
            IAMPermissions.MISSIONS_READ,
            IAMPermissions.MISSIONS_CREATE,
            IAMPermissions.APPLICATIONS_READ,
            IAMPermissions.PROFILE_MANAGE_OWN,
            IAMPermissions.AUTH_MFA_MANAGE,
            IAMPermissions.ADMIN_DASHBOARD,
            IAMPermissions.USERS_READ,
            IAMPermissions.EMAIL_SETTINGS_READ,
            IAMPermissions.IAM_PROFILES_READ
        ]
        
        for perm in permissions:
            assert "." in perm, f"Permission {perm} must contain a dot separator"
    
    def test_permissions_unique(self):
        """Test that all permission values are unique"""
        permissions = [
            IAMPermissions.MISSIONS_BROWSE,
            IAMPermissions.MISSIONS_READ,
            IAMPermissions.MISSIONS_CREATE,
            IAMPermissions.MISSIONS_UPDATE,
            IAMPermissions.MISSIONS_DELETE,
            IAMPermissions.MISSIONS_MANAGE,
            IAMPermissions.APPLICATIONS_CREATE_OWN,
            IAMPermissions.APPLICATIONS_READ_OWN,
            IAMPermissions.APPLICATIONS_UPDATE_OWN,
            IAMPermissions.APPLICATIONS_READ,
            IAMPermissions.APPLICATIONS_MANAGE,
            IAMPermissions.PROFILE_MANAGE_OWN,
            IAMPermissions.PROFILE_READ,
            IAMPermissions.PROFILE_MANAGE,
            IAMPermissions.AUTH_MFA_MANAGE,
            IAMPermissions.SECURITY_EMAIL_DOMAINS_READ,
            IAMPermissions.SECURITY_EMAIL_DOMAINS_MANAGE,
            IAMPermissions.ADMIN_DASHBOARD,
            IAMPermissions.USERS_READ,
            IAMPermissions.USERS_MANAGE,
            IAMPermissions.EMAIL_SETTINGS_READ,
            IAMPermissions.EMAIL_SETTINGS_MANAGE,
            IAMPermissions.IAM_PROFILES_READ,
            IAMPermissions.IAM_PROFILES_MANAGE,
            IAMPermissions.IAM_GROUPS_READ,
            IAMPermissions.IAM_GROUPS_MANAGE,
            IAMPermissions.IAM_PERMISSIONS_READ
        ]
        assert len(permissions) == len(set(permissions)), "Permission values must be unique"
        assert len(permissions) == 27, "Expected 27 permissions"
    
    def test_mission_permissions(self):
        """Test mission-specific permissions"""
        assert IAMPermissions.MISSIONS_BROWSE == "missions.browse"
        assert IAMPermissions.MISSIONS_READ == "missions.read"
        assert IAMPermissions.MISSIONS_CREATE == "missions.create"
        assert IAMPermissions.MISSIONS_UPDATE == "missions.update"
        assert IAMPermissions.MISSIONS_DELETE == "missions.delete"
        assert IAMPermissions.MISSIONS_MANAGE == "missions.manage"
    
    def test_application_permissions(self):
        """Test application-specific permissions"""
        assert IAMPermissions.APPLICATIONS_CREATE_OWN == "applications.create_own"
        assert IAMPermissions.APPLICATIONS_READ_OWN == "applications.read_own"
        assert IAMPermissions.APPLICATIONS_UPDATE_OWN == "applications.update_own"
        assert IAMPermissions.APPLICATIONS_READ == "applications.read"
        assert IAMPermissions.APPLICATIONS_MANAGE == "applications.manage"


class TestValidationTypes:
    """Test Validation Types constants"""
    
    def test_validation_type_values(self):
        """Test validation type values"""
        assert ValidationTypes.CANDIDAT == "candidat"
        assert ValidationTypes.INTERIM == "interim"
        assert ValidationTypes.COMPANY == "company"
        assert ValidationTypes.COLLABORATEUR == "collaborateur"
    
    def test_validation_types_unique(self):
        """Test that all validation types are unique"""
        types = [
            ValidationTypes.CANDIDAT,
            ValidationTypes.INTERIM,
            ValidationTypes.COMPANY,
            ValidationTypes.COLLABORATEUR
        ]
        assert len(types) == len(set(types)), "Validation types must be unique"


class TestUserRoles:
    """Test User Roles (Legacy) constants"""
    
    def test_user_role_values(self):
        """Test user role values"""
        assert UserRoles.CANDIDAT == "candidat"
        assert UserRoles.INTERIM == "interim"
        assert UserRoles.COMPANY == "company"
        assert UserRoles.COLLABORATEUR == "collaborateur"
        assert UserRoles.ADMIN == "admin"
        assert UserRoles.SUPER_ADMIN == "super_admin"
    
    def test_user_roles_unique(self):
        """Test that all user roles are unique"""
        roles = [
            UserRoles.CANDIDAT,
            UserRoles.INTERIM,
            UserRoles.COMPANY,
            UserRoles.COLLABORATEUR,
            UserRoles.ADMIN,
            UserRoles.SUPER_ADMIN
        ]
        assert len(roles) == len(set(roles)), "User roles must be unique"


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_group_for_role(self):
        """Test role to group mapping"""
        assert get_group_for_role(UserRoles.CANDIDAT) == IAMGroups.CANDIDAT
        assert get_group_for_role(UserRoles.INTERIM) == IAMGroups.INTERIMAIRE
        assert get_group_for_role(UserRoles.COMPANY) == IAMGroups.COMPANY
        assert get_group_for_role(UserRoles.COLLABORATEUR) == IAMGroups.COLLABORATEUR
        assert get_group_for_role(UserRoles.ADMIN) == IAMGroups.ADMIN
        assert get_group_for_role(UserRoles.SUPER_ADMIN) == IAMGroups.SUPER_ADMIN
    
    def test_get_group_for_invalid_role(self):
        """Test get_group_for_role with invalid role (should return default)"""
        result = get_group_for_role("invalid_role")
        assert result == IAMGroups.CANDIDAT, "Should return default CANDIDAT group"
    
    def test_get_profile_for_role(self):
        """Test role to profile mapping"""
        assert get_profile_for_role(UserRoles.CANDIDAT) == IAMProfiles.CANDIDAT
        assert get_profile_for_role(UserRoles.INTERIM) == IAMProfiles.INTERIM_USER
        assert get_profile_for_role(UserRoles.COMPANY) == IAMProfiles.COMPANY_ADMIN
        assert get_profile_for_role(UserRoles.COLLABORATEUR) == IAMProfiles.COLLABORATEUR
        assert get_profile_for_role(UserRoles.ADMIN) == IAMProfiles.ADMIN
        assert get_profile_for_role(UserRoles.SUPER_ADMIN) == IAMProfiles.SUPER_ADMIN
    
    def test_get_profile_for_invalid_role(self):
        """Test get_profile_for_role with invalid role (should return default)"""
        result = get_profile_for_role("invalid_role")
        assert result == IAMProfiles.CANDIDAT, "Should return default CANDIDAT profile"
    
    def test_get_validation_type_for_role(self):
        """Test role to validation type mapping"""
        assert get_validation_type_for_role(UserRoles.CANDIDAT) == UserRoles.CANDIDAT
        assert get_validation_type_for_role(UserRoles.INTERIM) == UserRoles.INTERIM
        assert get_validation_type_for_role(UserRoles.COMPANY) == UserRoles.COMPANY
        assert get_validation_type_for_role(UserRoles.COLLABORATEUR) == UserRoles.COLLABORATEUR


class TestConstantsConsistency:
    """Test consistency between different constant sets"""
    
    def test_role_group_profile_consistency(self):
        """Test that roles map consistently to groups and profiles"""
        role_mappings = {
            UserRoles.CANDIDAT: (IAMGroups.CANDIDAT, IAMProfiles.CANDIDAT),
            UserRoles.INTERIM: (IAMGroups.INTERIMAIRE, IAMProfiles.INTERIM_USER),
            UserRoles.COMPANY: (IAMGroups.COMPANY, IAMProfiles.COMPANY_ADMIN),
            UserRoles.COLLABORATEUR: (IAMGroups.COLLABORATEUR, IAMProfiles.COLLABORATEUR),
            UserRoles.ADMIN: (IAMGroups.ADMIN, IAMProfiles.ADMIN),
            UserRoles.SUPER_ADMIN: (IAMGroups.SUPER_ADMIN, IAMProfiles.SUPER_ADMIN),
        }
        
        for role, (expected_group, expected_profile) in role_mappings.items():
            assert get_group_for_role(role) == expected_group
            assert get_profile_for_role(role) == expected_profile
    
    def test_validation_types_match_roles(self):
        """Test that validation types match corresponding user roles"""
        assert ValidationTypes.CANDIDAT == UserRoles.CANDIDAT
        assert ValidationTypes.INTERIM == UserRoles.INTERIM
        assert ValidationTypes.COMPANY == UserRoles.COMPANY
        assert ValidationTypes.COLLABORATEUR == UserRoles.COLLABORATEUR
    
    def test_total_constants_count(self):
        """Test total number of constants"""
        # Count all constants
        groups_count = 6
        profiles_count = 6
        permissions_count = 27
        validation_types_count = 4
        user_roles_count = 6
        
        total = groups_count + profiles_count + permissions_count + validation_types_count + user_roles_count
        assert total == 49, f"Expected 49 total constants, got {total}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
