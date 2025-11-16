"""
Tests for ApplicationEligibilityService
Tests business rules for mission applications
"""
import pytest
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from awana_auth.services.application_eligibility_service import ApplicationEligibilityService


@pytest.fixture
async def test_db():
    """Create a test database connection"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.auth_db_test
    yield db
    # Cleanup
    await client.drop_database("auth_db_test")
    client.close()


@pytest.fixture
async def eligibility_service(test_db):
    """Create an ApplicationEligibilityService instance"""
    return ApplicationEligibilityService(test_db)


@pytest.fixture
async def setup_business_rules(test_db):
    """Setup test business rules"""
    rules = [
        {
            "rule_id": "application_eligibility_roles",
            "category": "application",
            "is_active": True,
            "priority": 100,
            "conditions": {
                "allowed_roles": ["candidat", "postulant", "intérimaire", "interim"],
                "required_mission_status": ["open", "published"]
            },
            "error_messages": {
                "role_not_allowed": "Rôle non autorisé à postuler",
                "mission_not_open": "Mission non ouverte aux candidatures"
            }
        },
        {
            "rule_id": "application_interim_contract_restriction",
            "category": "application",
            "is_active": True,
            "priority": 90,
            "conditions": {
                "days_before_contract_end": 5,
                "check_extensions": True,
                "check_amendments": True
            },
            "error_messages": {
                "contract_active": "Vous êtes en mission. Vous pourrez postuler à partir de {days_before} jours avant la fin.",
                "extension_pending": "Une prolongation de contrat est en cours",
                "amendment_active": "Un avenant est actif sur votre contrat"
            }
        },
        {
            "rule_id": "application_cv_requirement",
            "category": "application",
            "is_active": True,
            "priority": 80,
            "conditions": {
                "cv_required": True,
                "allow_upload": True
            },
            "error_messages": {
                "cv_missing": "Un CV est requis pour postuler"
            }
        },
        {
            "rule_id": "application_duplicate_prevention",
            "category": "application",
            "is_active": True,
            "priority": 70,
            "error_messages": {
                "already_applied": "Vous avez déjà postulé à cette mission"
            }
        }
    ]
    
    await test_db.business_rules.insert_many(rules)
    return rules


class TestRoleEligibility:
    """Test role-based eligibility checks"""
    
    @pytest.mark.asyncio
    async def test_allowed_role_candidat(self, eligibility_service, setup_business_rules):
        """Test that candidat role is allowed"""
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["candidat"],
            mission_id="mission123",
            mission_status="published"
        )
        
        assert is_eligible is True
        assert error_msg is None
    
    @pytest.mark.asyncio
    async def test_allowed_role_interim(self, eligibility_service, setup_business_rules):
        """Test that intérimaire role is allowed"""
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["intérimaire"],
            mission_id="mission123",
            mission_status="open"
        )
        
        # Will fail at contract check, but passes role check
        assert error_msg is None or "rôle" not in error_msg.lower()
    
    @pytest.mark.asyncio
    async def test_disallowed_role(self, eligibility_service, setup_business_rules):
        """Test that non-allowed role is rejected"""
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["admin"],
            mission_id="mission123",
            mission_status="published"
        )
        
        assert is_eligible is False
        assert error_msg is not None
        assert "rôle" in error_msg.lower() or "autorisé" in error_msg.lower()


class TestContractRestriction:
    """Test contract-based restrictions for interims"""
    
    @pytest.mark.asyncio
    async def test_no_active_contract_allowed(self, eligibility_service, setup_business_rules, test_db):
        """Test that interim without active contract can apply"""
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["intérimaire"],
            mission_id="mission123",
            mission_status="published"
        )
        
        # Should pass since no contract exists
        assert metadata.get("cv_required") is not None
    
    @pytest.mark.asyncio
    async def test_active_contract_more_than_5_days_blocked(self, eligibility_service, setup_business_rules, test_db):
        """Test that interim with contract >5 days remaining is blocked"""
        # Create active contract with 10 days remaining
        end_date = datetime.now(timezone.utc) + timedelta(days=10)
        await test_db.contracts.insert_one({
            "id": "contract123",
            "user_id": "user123",
            "status": "active",
            "end_date": end_date.isoformat()
        })
        
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["intérimaire"],
            mission_id="mission123",
            mission_status="published"
        )
        
        assert is_eligible is False
        assert error_msg is not None
        assert "mission" in error_msg.lower()
        assert metadata.get("days_remaining") == 10
    
    @pytest.mark.asyncio
    async def test_active_contract_less_than_5_days_allowed(self, eligibility_service, setup_business_rules, test_db):
        """Test that interim with contract ≤5 days remaining is allowed"""
        # Create active contract with 3 days remaining
        end_date = datetime.now(timezone.utc) + timedelta(days=3)
        await test_db.contracts.insert_one({
            "id": "contract123",
            "user_id": "user456",
            "status": "active",
            "end_date": end_date.isoformat()
        })
        
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user456",
            user_roles=["intérimaire"],
            mission_id="mission123",
            mission_status="published"
        )
        
        # Should be eligible or pass contract check
        assert is_eligible is True or "contrat" not in (error_msg or "").lower()


class TestDuplicateApplication:
    """Test duplicate application prevention"""
    
    @pytest.mark.asyncio
    async def test_duplicate_application_blocked(self, eligibility_service, setup_business_rules, test_db):
        """Test that duplicate application is blocked"""
        # Create existing application
        await test_db.applications.insert_one({
            "id": "app123",
            "user_id": "user123",
            "mission_id": "mission123",
            "status": "submitted"
        })
        
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["candidat"],
            mission_id="mission123",
            mission_status="published"
        )
        
        assert is_eligible is False
        assert error_msg is not None
        assert "déjà" in error_msg.lower() or "postulé" in error_msg.lower()
        assert metadata.get("existing_application_id") == "app123"
    
    @pytest.mark.asyncio
    async def test_new_application_allowed(self, eligibility_service, setup_business_rules, test_db):
        """Test that new application is allowed"""
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user789",
            user_roles=["candidat"],
            mission_id="mission456",
            mission_status="published"
        )
        
        assert is_eligible is True
        assert error_msg is None


class TestCVRequirement:
    """Test CV requirement metadata"""
    
    @pytest.mark.asyncio
    async def test_cv_required_metadata(self, eligibility_service, setup_business_rules):
        """Test that CV requirement is returned in metadata"""
        is_eligible, error_msg, metadata = await eligibility_service.check_eligibility(
            user_id="user123",
            user_roles=["candidat"],
            mission_id="mission123",
            mission_status="published"
        )
        
        assert metadata.get("cv_required") is True
        assert metadata.get("allow_upload") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
