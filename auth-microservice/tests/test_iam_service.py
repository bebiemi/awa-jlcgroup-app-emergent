"""
Tests unitaires pour IAMService
Tests du chargement des permissions, bundles, profils et groupes
"""
import pytest
import pytest_asyncio
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid

# Import du service à tester
import sys
sys.path.insert(0, '/app/auth-microservice')
from awana_auth.services.iam_service import IAMService
from awana_auth.core.iam_models import Profile, Permission

# Configuration pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture
async def db():
    """Fixture pour la connexion DB de test"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db_test']
    
    # Nettoyer avant les tests
    await db.users.delete_many({})
    await db.profiles.delete_many({})
    await db.capability_bundles.delete_many({})
    await db.permissions.delete_many({})
    await db.groups.delete_many({})
    
    yield db
    
    # Nettoyer après les tests
    await db.users.delete_many({})
    await db.profiles.delete_many({})
    await db.capability_bundles.delete_many({})
    await db.permissions.delete_many({})
    await db.groups.delete_many({})
    client.close()


@pytest.fixture
async def iam_service(db):
    """Fixture pour IAMService"""
    return IAMService(db)


@pytest.fixture
async def sample_permissions(db):
    """Créer des permissions de test"""
    permissions = [
        {
            "id": f"perm_{i}",
            "code": f"resource.action.{scope}",
            "name": f"Permission {i}",
            "description": f"Test permission {i}",
            "resource": "resource",
            "action": "action",
            "scope": scope,
            "category": "test"
        }
        for i, scope in enumerate(["own", "all", "own", "own"])
    ]
    
    await db.permissions.insert_many(permissions)
    return permissions


@pytest.fixture
async def sample_bundle(db, sample_permissions):
    """Créer un bundle de test"""
    bundle = {
        "id": "bundle_test_1",
        "code": "test_bundle",
        "name": "Test Bundle",
        "description": "Bundle for testing",
        "category": "test",
        "permission_ids": [p["id"] for p in sample_permissions[:2]],  # 2 permissions
        "tags": ["test"],
        "is_system": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.capability_bundles.insert_one(bundle)
    return bundle


@pytest.fixture
async def sample_profile(db, sample_permissions, sample_bundle):
    """Créer un profil de test avec permissions directes et bundle"""
    profile = {
        "id": "profile_test_1",
        "code": "test_profile",
        "name": "Test Profile",
        "description": "Profile for testing",
        "category": "test",
        "permission_ids": [sample_permissions[2]["id"]],  # 1 permission directe
        "capability_bundle_ids": [sample_bundle["id"]],    # 1 bundle (2 permissions)
        "is_protected": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.profiles.insert_one(profile)
    return profile


@pytest.fixture
async def sample_user(db, sample_profile):
    """Créer un utilisateur de test"""
    user = {
        "id": "user_test_1",
        "username": "test_user",
        "email": "test@example.com",
        "password_hash": "hashed",
        "provider": "local",
        "status": "active",
        "roles": ["user"],
        "profile_ids": [sample_profile["id"]],
        "group_ids": [],
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user)
    return user


# ==================== TESTS ====================

@pytest.mark.asyncio
async def test_iam_service_initialization(db):
    """Test que IAMService s'initialise correctement"""
    iam = IAMService(db)
    
    assert iam.db is not None
    assert iam.permissions_collection is not None
    assert iam.profiles_collection is not None
    assert iam.groups_collection is not None
    assert iam.users_collection is not None
    assert iam.bundles_collection is not None  # Vérifier que bundles_collection existe


@pytest.mark.asyncio
async def test_get_user_permissions_basic(iam_service, sample_user, sample_permissions):
    """Test chargement des permissions de base"""
    response = await iam_service.get_user_permissions(sample_user["id"])
    
    assert response.user_id == sample_user["id"]
    assert len(response.all_permissions) > 0
    
    # Vérifier que les codes de permissions sont corrects
    perm_codes = [p.code for p in response.all_permissions]
    assert len(perm_codes) > 0


@pytest.mark.asyncio
async def test_get_user_permissions_with_bundles(iam_service, sample_user, sample_bundle):
    """Test que les permissions des bundles sont chargées"""
    response = await iam_service.get_user_permissions(sample_user["id"])
    
    # Le profil a 1 permission directe + 2 du bundle = 3 total
    assert len(response.all_permissions) == 3, f"Attendu 3 permissions, reçu {len(response.all_permissions)}"
    
    # Vérifier que les permissions du bundle sont présentes
    perm_ids = [p.id for p in response.all_permissions]
    bundle_perm_ids = sample_bundle["permission_ids"]
    
    for bundle_perm_id in bundle_perm_ids:
        assert bundle_perm_id in perm_ids, f"Permission du bundle {bundle_perm_id} non trouvée"


@pytest.mark.asyncio
async def test_get_user_permissions_without_profile(iam_service, db):
    """Test utilisateur sans profil"""
    user = {
        "id": "user_no_profile",
        "username": "no_profile",
        "email": "nopr@example.com",
        "profile_ids": [],
        "group_ids": []
    }
    await db.users.insert_one(user)
    
    response = await iam_service.get_user_permissions(user["id"])
    
    assert response.user_id == user["id"]
    assert len(response.all_permissions) == 0


@pytest.mark.asyncio
async def test_get_user_permissions_nonexistent_user(iam_service):
    """Test utilisateur inexistant"""
    response = await iam_service.get_user_permissions("nonexistent_user_id")
    
    assert response.user_id == "nonexistent_user_id"
    assert len(response.all_permissions) == 0


@pytest.mark.asyncio
async def test_user_has_permission_granted(iam_service, sample_user, sample_permissions):
    """Test vérification permission accordée"""
    # L'utilisateur doit avoir la permission perm_2 (directe)
    check = await iam_service.user_has_permission(
        sample_user["id"],
        sample_permissions[2]["code"]
    )
    
    assert check.has_permission is True
    assert len(check.granted_by) > 0


@pytest.mark.asyncio
async def test_user_has_permission_from_bundle(iam_service, sample_user, sample_permissions):
    """Test vérification permission venant d'un bundle"""
    # L'utilisateur doit avoir les permissions du bundle (perm_0 et perm_1)
    check = await iam_service.user_has_permission(
        sample_user["id"],
        sample_permissions[0]["code"]
    )
    
    assert check.has_permission is True, "Permission du bundle devrait être accordée"


@pytest.mark.asyncio
async def test_user_has_permission_denied(iam_service, sample_user):
    """Test vérification permission refusée"""
    check = await iam_service.user_has_permission(
        sample_user["id"],
        "nonexistent.permission"
    )
    
    assert check.has_permission is False
    assert "not found" in check.reason.lower()


@pytest.mark.asyncio
async def test_super_admin_bypass(iam_service, db):
    """Test que super_admin a toutes les permissions"""
    super_admin = {
        "id": "super_admin_id",
        "username": "super_admin",
        "email": "admin@example.com",
        "roles": ["super_admin"],
        "profile_ids": []
    }
    await db.users.insert_one(super_admin)
    
    check = await iam_service.user_has_permission(
        super_admin["id"],
        "any.permission.ever"
    )
    
    assert check.has_permission is True
    assert "SuperAdmin" in check.reason


@pytest.mark.asyncio
async def test_get_user_permissions_with_groups(iam_service, db, sample_profile, sample_permissions):
    """Test chargement permissions via groupes"""
    # Créer un groupe avec le profil
    group = {
        "id": "group_test_1",
        "code": "test_group",
        "name": "Test Group",
        "profile_ids": [sample_profile["id"]],
        "user_ids": []
    }
    await db.groups.insert_one(group)
    
    # Créer un utilisateur membre du groupe
    user = {
        "id": "user_with_group",
        "username": "group_user",
        "email": "group@example.com",
        "profile_ids": [],
        "group_ids": [group["id"]]
    }
    await db.users.insert_one(user)
    
    response = await iam_service.get_user_permissions(user["id"])
    
    # Devrait avoir les permissions du profil via le groupe
    assert len(response.all_permissions) == 3  # 1 directe + 2 bundle
    assert len(response.group_profiles) == 1


@pytest.mark.asyncio
async def test_multiple_profiles_union(iam_service, db, sample_permissions):
    """Test union de permissions de plusieurs profils"""
    # Créer 2 profils avec permissions différentes
    profile1 = {
        "id": "profile_1",
        "code": "prof1",
        "name": "Profile 1",
        "permission_ids": [sample_permissions[0]["id"]],
        "capability_bundle_ids": []
    }
    profile2 = {
        "id": "profile_2",
        "code": "prof2",
        "name": "Profile 2",
        "permission_ids": [sample_permissions[1]["id"]],
        "capability_bundle_ids": []
    }
    
    await db.profiles.insert_many([profile1, profile2])
    
    # Utilisateur avec les 2 profils
    user = {
        "id": "user_multi_profile",
        "username": "multi",
        "email": "multi@example.com",
        "profile_ids": [profile1["id"], profile2["id"]],
        "group_ids": []
    }
    await db.users.insert_one(user)
    
    response = await iam_service.get_user_permissions(user["id"])
    
    # Devrait avoir les 2 permissions (union)
    assert len(response.all_permissions) == 2
    perm_ids = [p.id for p in response.all_permissions]
    assert sample_permissions[0]["id"] in perm_ids
    assert sample_permissions[1]["id"] in perm_ids


@pytest.mark.asyncio
async def test_bundle_with_no_permissions(iam_service, db, sample_permissions):
    """Test bundle vide ne cause pas d'erreur"""
    empty_bundle = {
        "id": "empty_bundle",
        "code": "empty",
        "name": "Empty Bundle",
        "permission_ids": []
    }
    await db.capability_bundles.insert_one(empty_bundle)
    
    profile = {
        "id": "profile_empty_bundle",
        "code": "prof_empty",
        "name": "Profile with Empty Bundle",
        "permission_ids": [sample_permissions[0]["id"]],
        "capability_bundle_ids": [empty_bundle["id"]]
    }
    await db.profiles.insert_one(profile)
    
    user = {
        "id": "user_empty_bundle",
        "username": "empty_user",
        "email": "empty@example.com",
        "profile_ids": [profile["id"]],
        "group_ids": []
    }
    await db.users.insert_one(user)
    
    response = await iam_service.get_user_permissions(user["id"])
    
    # Devrait avoir seulement la permission directe
    assert len(response.all_permissions) == 1


@pytest.mark.asyncio
async def test_performance_many_permissions(iam_service, db):
    """Test performance avec beaucoup de permissions"""
    import time
    
    # Créer 100 permissions
    permissions = [
        {
            "id": f"perf_perm_{i}",
            "code": f"resource{i}.action",
            "name": f"Permission {i}",
            "resource": f"resource{i}",
            "action": "action",
            "category": "test"
        }
        for i in range(100)
    ]
    await db.permissions.insert_many(permissions)
    
    # Créer profil avec toutes les permissions
    profile = {
        "id": "perf_profile",
        "code": "perf",
        "name": "Performance Profile",
        "permission_ids": [p["id"] for p in permissions],
        "capability_bundle_ids": []
    }
    await db.profiles.insert_one(profile)
    
    # Utilisateur avec ce profil
    user = {
        "id": "perf_user",
        "username": "perf",
        "email": "perf@example.com",
        "profile_ids": [profile["id"]],
        "group_ids": []
    }
    await db.users.insert_one(user)
    
    # Mesurer le temps
    start = time.time()
    response = await iam_service.get_user_permissions(user["id"])
    duration = time.time() - start
    
    assert len(response.all_permissions) == 100
    assert duration < 1.0, f"Chargement trop lent: {duration}s (max: 1s)"


@pytest.mark.asyncio
async def test_assign_profiles_to_user(iam_service, db, sample_profile):
    """Test assignation de profils à un utilisateur"""
    user = {
        "id": "user_assign",
        "username": "assign_user",
        "email": "assign@example.com",
        "profile_ids": [],
        "updated_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(user)
    
    # Assigner le profil
    success = await iam_service.assign_profiles_to_user(
        user["id"],
        [sample_profile["id"]]
    )
    
    assert success is True
    
    # Vérifier que le profil est assigné
    updated_user = await db.users.find_one({"id": user["id"]})
    assert sample_profile["id"] in updated_user["profile_ids"]


@pytest.mark.asyncio
async def test_assign_groups_to_user(iam_service, db):
    """Test assignation de groupes à un utilisateur"""
    group = {
        "id": "group_assign",
        "code": "assign_group",
        "name": "Assign Group",
        "profile_ids": [],
        "user_ids": []
    }
    await db.groups.insert_one(group)
    
    user = {
        "id": "user_group_assign",
        "username": "group_assign_user",
        "email": "ga@example.com",
        "group_ids": [],
        "updated_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(user)
    
    # Assigner le groupe
    success = await iam_service.assign_groups_to_user(
        user["id"],
        [group["id"]]
    )
    
    assert success is True
    
    # Vérifier l'assignation
    updated_user = await db.users.find_one({"id": user["id"]})
    assert group["id"] in updated_user["group_ids"]
    
    updated_group = await db.groups.find_one({"id": group["id"]})
    assert user["id"] in updated_group["user_ids"]


# ==================== TESTS DE RÉGRESSION ====================

@pytest.mark.asyncio
async def test_no_regression_direct_permissions(iam_service, db, sample_permissions):
    """Test de non-régression: permissions directes toujours chargées"""
    profile = {
        "id": "regression_profile",
        "code": "regression",
        "name": "Regression Profile",
        "permission_ids": [sample_permissions[0]["id"], sample_permissions[1]["id"]],
        "capability_bundle_ids": []  # Pas de bundles
    }
    await db.profiles.insert_one(profile)
    
    user = {
        "id": "regression_user",
        "username": "regression",
        "email": "regression@example.com",
        "profile_ids": [profile["id"]],
        "group_ids": []
    }
    await db.users.insert_one(user)
    
    response = await iam_service.get_user_permissions(user["id"])
    
    # Devrait avoir exactement les 2 permissions directes
    assert len(response.all_permissions) == 2


# ==================== EXÉCUTION DES TESTS ====================

if __name__ == "__main__":
    # Pour exécuter manuellement
    print("Exécution des tests IAMService...")
    pytest.main([__file__, "-v", "-s"])
