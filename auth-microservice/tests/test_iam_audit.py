"""
Tests unitaires pour IAMAuditService
"""
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import os

import sys
sys.path.insert(0, '/app/auth-microservice')
from awana_auth.services.iam_audit_service import (
    IAMAuditService,
    AuditEntry,
    AuditAction,
    AuditSeverity
)

pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture
async def db():
    """Fixture pour la connexion DB de test"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db_test']
    
    # Nettoyer avant les tests
    await db.iam_audit_trail.delete_many({})
    await db.users.delete_many({})
    
    yield db
    
    # Nettoyer après les tests
    await db.iam_audit_trail.delete_many({})
    await db.users.delete_many({})
    client.close()


@pytest_asyncio.fixture
async def service(db):
    """Fixture pour IAMAuditService"""
    return IAMAuditService(db)


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


@pytest.mark.asyncio
async def test_log_action_basic(service, test_user):
    """Test de création d'une entrée d'audit basique"""
    entry = await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        target_id="profile_123",
        target_name="Test Profile",
        details={"field": "value"},
        severity=AuditSeverity.INFO
    )
    
    assert entry.action == AuditAction.PROFILE_CREATED
    assert entry.actor_id == test_user["id"]
    assert entry.target_type == "profile"
    assert entry.result == "success"
    assert entry.severity == AuditSeverity.INFO


@pytest.mark.asyncio
async def test_log_action_with_error(service, test_user):
    """Test de création d'une entrée avec erreur"""
    entry = await service.log_action(
        action=AuditAction.PERMISSION_DENIED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission",
        result="failure",
        error_message="Insufficient permissions",
        severity=AuditSeverity.WARNING
    )
    
    assert entry.result == "failure"
    assert entry.error_message == "Insufficient permissions"
    assert entry.severity == AuditSeverity.WARNING


@pytest.mark.asyncio
async def test_get_user_actions(service, test_user):
    """Test de récupération des actions d'un utilisateur"""
    # Créer plusieurs actions
    for i in range(5):
        await service.log_action(
            action=AuditAction.PROFILE_UPDATED,
            actor_id=test_user["id"],
            actor_type="user",
            target_type="profile",
            target_id=f"profile_{i}"
        )
    
    # Récupérer les actions
    actions = await service.get_user_actions(test_user["id"], limit=10)
    
    assert len(actions) == 5
    assert all(a.actor_id == test_user["id"] for a in actions)


@pytest.mark.asyncio
async def test_get_user_actions_with_date_filter(service, test_user):
    """Test de récupération avec filtre de dates"""
    now = datetime.now(timezone.utc)
    
    # Créer une action récente
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile"
    )
    
    # Créer une action "ancienne" (hack en modifiant directement)
    old_entry = await service.log_action(
        action=AuditAction.PROFILE_DELETED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile"
    )
    
    await service.collection.update_one(
        {"id": old_entry.id},
        {"$set": {"timestamp": now - timedelta(days=10)}}
    )
    
    # Récupérer seulement les actions des 7 derniers jours
    recent_actions = await service.get_user_actions(
        test_user["id"],
        start_date=now - timedelta(days=7)
    )
    
    assert len(recent_actions) == 1  # Seulement la récente


@pytest.mark.asyncio
async def test_get_actions_by_type(service, test_user):
    """Test de récupération par type d'action"""
    # Créer différents types d'actions
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile"
    )
    
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id="other_user",
        actor_type="user",
        target_type="profile"
    )
    
    await service.log_action(
        action=AuditAction.PERMISSION_DENIED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission"
    )
    
    # Récupérer seulement PROFILE_CREATED
    created_actions = await service.get_actions_by_type(
        AuditAction.PROFILE_CREATED,
        limit=10
    )
    
    assert len(created_actions) == 2
    assert all(a.action == AuditAction.PROFILE_CREATED for a in created_actions)


@pytest.mark.asyncio
async def test_get_failed_actions(service, test_user):
    """Test de récupération des actions échouées"""
    # Créer une action réussie
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        result="success"
    )
    
    # Créer une action échouée
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        result="failure",
        error_message="Database error"
    )
    
    # Récupérer les échecs
    failed = await service.get_failed_actions(hours_back=24)
    
    assert len(failed) == 1
    assert failed[0].result == "failure"


@pytest.mark.asyncio
async def test_get_security_alerts(service, test_user):
    """Test de récupération des alertes de sécurité"""
    # Créer une entrée normale
    await service.log_action(
        action=AuditAction.PROFILE_UPDATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        severity=AuditSeverity.INFO
    )
    
    # Créer une alerte critique
    await service.log_action(
        action=AuditAction.PERMISSION_DELETED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission",
        severity=AuditSeverity.CRITICAL
    )
    
    # Créer une erreur
    await service.log_action(
        action=AuditAction.PROFILE_DELETED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        severity=AuditSeverity.ERROR
    )
    
    # Récupérer les alertes
    alerts = await service.get_security_alerts(hours_back=24)
    
    assert len(alerts) == 2  # CRITICAL + ERROR
    assert all(a.severity in [AuditSeverity.CRITICAL, AuditSeverity.ERROR] for a in alerts)


@pytest.mark.asyncio
async def test_search_audit_trail(service, test_user):
    """Test de recherche avancée"""
    # Créer plusieurs entrées
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        target_name="Test Profile"
    )
    
    await service.log_action(
        action=AuditAction.PERMISSION_DENIED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission",
        result="failure"
    )
    
    # Rechercher les actions échouées de cet utilisateur
    results = await service.search_audit_trail(
        filters={
            "actor_id": test_user["id"],
            "result": "failure"
        },
        limit=10
    )
    
    assert results["total"] == 1
    assert len(results["results"]) == 1
    assert results["results"][0].result == "failure"


@pytest.mark.asyncio
async def test_get_statistics(service, test_user):
    """Test des statistiques d'audit"""
    # Créer quelques entrées
    await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        severity=AuditSeverity.INFO
    )
    
    await service.log_action(
        action=AuditAction.PERMISSION_DENIED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission",
        severity=AuditSeverity.WARNING
    )
    
    stats = await service.get_statistics()
    
    assert stats["total_actions"] >= 2
    assert "by_action" in stats
    assert "by_severity" in stats
    assert "by_result" in stats
    assert "top_users" in stats


@pytest.mark.asyncio
async def test_generate_compliance_report(service, test_user):
    """Test de génération de rapport de conformité"""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=7)
    
    # Créer des actions sensibles
    await service.log_action(
        action=AuditAction.PERMISSION_DELETED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission"
    )
    
    await service.log_action(
        action=AuditAction.PERMISSION_DENIED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission"
    )
    
    report = await service.generate_compliance_report(
        start_date=start_date,
        end_date=now
    )
    
    assert "report_period" in report
    assert "sensitive_actions" in report
    assert "permissions_denied" in report
    assert "compliance_status" in report


@pytest.mark.asyncio
async def test_cleanup_old_entries(service, test_user):
    """Test du nettoyage des anciennes entrées"""
    now = datetime.now(timezone.utc)
    
    # Créer une entrée récente
    recent = await service.log_action(
        action=AuditAction.PROFILE_CREATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        severity=AuditSeverity.INFO
    )
    
    # Créer une entrée ancienne (non-critique)
    old_info = await service.log_action(
        action=AuditAction.PROFILE_UPDATED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="profile",
        severity=AuditSeverity.INFO
    )
    
    await service.collection.update_one(
        {"id": old_info.id},
        {"$set": {"timestamp": now - timedelta(days=100)}}
    )
    
    # Créer une entrée ancienne CRITIQUE
    old_critical = await service.log_action(
        action=AuditAction.PERMISSION_DELETED,
        actor_id=test_user["id"],
        actor_type="user",
        target_type="permission",
        severity=AuditSeverity.CRITICAL
    )
    
    await service.collection.update_one(
        {"id": old_critical.id},
        {"$set": {"timestamp": now - timedelta(days=100)}}
    )
    
    # Nettoyer les entrées > 90 jours
    count = await service.cleanup_old_entries(days_to_keep=90)
    
    assert count == 1  # Seulement l'INFO ancienne est supprimée
    
    # Vérifier que la CRITICAL est conservée
    remaining = await service.collection.count_documents({})
    assert remaining == 2  # récente + critique ancienne
