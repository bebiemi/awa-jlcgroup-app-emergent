"""
Tests unitaires pour TemporaryPermissionsService
"""
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import os

import sys
sys.path.insert(0, '/app/auth-microservice')
from awana_auth.services.temporary_permissions_service import (
    TemporaryPermissionsService,
    TemporaryPermission
)

pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture
async def db():
    """Fixture pour la connexion DB de test"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db_test']
    
    # Nettoyer avant les tests
    await db.temporary_permissions.delete_many({})
    await db.users.delete_many({})
    await db.permissions.delete_many({})
    
    yield db
    
    # Nettoyer après les tests
    await db.temporary_permissions.delete_many({})
    await db.users.delete_many({})
    await db.permissions.delete_many({})
    client.close()


@pytest_asyncio.fixture
async def service(db):
    """Fixture pour TemporaryPermissionsService"""
    return TemporaryPermissionsService(db)


@pytest_asyncio.fixture
async def test_user(db):
    """Créer un utilisateur de test"""
    user = {
        "id": "test_user_1",
        "username": "testuser",
        "email": "test@example.com"
    }
    await db.users.insert_one(user)
    return user


@pytest_asyncio.fixture
async def test_permission(db):
    """Créer une permission de test"""
    permission = {
        "id": "perm_test_1",
        "code": "missions.delete.own",
        "name": "Delete Own Missions",
        "description": "Permission to delete own missions"
    }
    await db.permissions.insert_one(permission)
    return permission


@pytest.mark.asyncio
async def test_grant_temporary_permission(service, test_user, test_permission):
    """Test d'octroi d'une permission temporaire"""
    temp_perm = await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=24,
        granted_by="admin_user",
        reason="Test purpose"
    )
    
    assert temp_perm.user_id == test_user["id"]
    assert temp_perm.permission_code == test_permission["code"]
    assert temp_perm.is_active is True
    assert temp_perm.granted_by == "admin_user"
    assert temp_perm.reason == "Test purpose"
    
    # Vérifier que expires_at est dans le futur
    assert temp_perm.expires_at > datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_grant_invalid_permission(service, test_user):
    """Test d'octroi avec une permission invalide"""
    with pytest.raises(ValueError, match="Permission.*non trouvée"):
        await service.grant_temporary_permission(
            user_id=test_user["id"],
            permission_code="invalid.permission",
            duration_hours=24,
            granted_by="admin_user"
        )


@pytest.mark.asyncio
async def test_grant_invalid_user(service, test_permission):
    """Test d'octroi à un utilisateur invalide"""
    with pytest.raises(ValueError, match="Utilisateur.*non trouvé"):
        await service.grant_temporary_permission(
            user_id="invalid_user",
            permission_code=test_permission["code"],
            duration_hours=24,
            granted_by="admin_user"
        )


@pytest.mark.asyncio
async def test_get_active_temporary_permissions(service, test_user, test_permission):
    """Test de récupération des permissions actives"""
    # Créer 2 permissions temporaires
    await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=24,
        granted_by="admin_user"
    )
    
    # Créer une permission expirée (hack pour le test)
    expired_perm = await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=1,
        granted_by="admin_user"
    )
    
    # Forcer l'expiration
    await service.collection.update_one(
        {"id": expired_perm.id},
        {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(hours=1)}}
    )
    
    # Récupérer les permissions actives
    active_perms = await service.get_active_temporary_permissions(test_user["id"])
    
    assert len(active_perms) == 1  # Seulement la non-expirée


@pytest.mark.asyncio
async def test_revoke_temporary_permission(service, test_user, test_permission):
    """Test de révocation d'une permission temporaire"""
    temp_perm = await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=24,
        granted_by="admin_user"
    )
    
    # Révoquer
    success = await service.revoke_temporary_permission(
        temp_perm_id=temp_perm.id,
        revoked_by="admin_user",
        reason="Test revocation"
    )
    
    assert success is True
    
    # Vérifier que la permission est désactivée
    active_perms = await service.get_active_temporary_permissions(test_user["id"])
    assert len(active_perms) == 0


@pytest.mark.asyncio
async def test_extend_temporary_permission(service, test_user, test_permission):
    """Test de prolongation d'une permission temporaire"""
    temp_perm = await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=24,
        granted_by="admin_user"
    )
    
    original_expires = temp_perm.expires_at
    
    # Prolonger de 12 heures
    extended = await service.extend_temporary_permission(
        temp_perm_id=temp_perm.id,
        additional_hours=12
    )
    
    assert extended is not None
    # La nouvelle date d'expiration devrait être ~12h plus tard
    time_diff = (extended.expires_at - original_expires).total_seconds() / 3600
    assert 11 < time_diff < 13  # Tolérance pour le temps de traitement


@pytest.mark.asyncio
async def test_cleanup_expired_permissions(service, test_user, test_permission):
    """Test du nettoyage des permissions expirées"""
    # Créer une permission active
    active = await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=24,
        granted_by="admin_user"
    )
    
    # Créer une permission expirée
    expired = await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=1,
        granted_by="admin_user"
    )
    
    # Forcer l'expiration
    await service.collection.update_one(
        {"id": expired.id},
        {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(hours=1)}}
    )
    
    # Nettoyer
    count = await service.cleanup_expired_permissions()
    
    assert count == 1  # Une permission nettoyée
    
    # Vérifier que seule l'active reste
    active_perms = await service.get_active_temporary_permissions(test_user["id"])
    assert len(active_perms) == 1


@pytest.mark.asyncio
async def test_get_statistics(service, test_user, test_permission):
    """Test des statistiques"""
    # Créer quelques permissions
    await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=24,
        granted_by="admin_user"
    )
    
    stats = await service.get_statistics()
    
    assert stats["total"] >= 1
    assert stats["active"] >= 1
    assert "top_permissions" in stats
    assert len(stats["top_permissions"]) > 0


@pytest.mark.asyncio
async def test_get_expiring_soon(service, test_user, test_permission):
    """Test de récupération des permissions qui expirent bientôt"""
    # Créer une permission qui expire dans 12h
    await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=12,
        granted_by="admin_user"
    )
    
    # Créer une permission qui expire dans 48h
    await service.grant_temporary_permission(
        user_id=test_user["id"],
        permission_code=test_permission["code"],
        duration_hours=48,
        granted_by="admin_user"
    )
    
    # Récupérer celles qui expirent dans les 24h
    expiring = await service.get_expiring_soon(hours_threshold=24)
    
    assert len(expiring) == 1  # Seulement celle à 12h
