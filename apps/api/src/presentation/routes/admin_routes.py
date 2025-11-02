"""Admin routes for KPIs and statistics"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.presentation.dependencies import get_database, require_admin
from src.domain.entities.validation import ValidationStatus, ValidationType
from src.infrastructure.repositories.validation_repository import ValidationRepository
from src.infrastructure.repositories.profile_repository import ProfileRepository
from src.domain.entities.profile import ProfileType
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/kpis")
async def get_dashboard_kpis(
    current_user=Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get dashboard KPIs for admin"""
    validation_repo = ValidationRepository(db)
    profile_repo = ProfileRepository(db)

    # Count validations by status
    pending_count = await validation_repo.count_by_status(ValidationStatus.PENDING)
    approved_count = await validation_repo.count_by_status(ValidationStatus.APPROVED)
    rejected_count = await validation_repo.count_by_status(ValidationStatus.REJECTED)

    # Count pending by type
    pending_interim, _ = await validation_repo.list(
        status=ValidationStatus.PENDING,
        validation_type=ValidationType.INTERIM,
        skip=0,
        limit=0
    )
    pending_company, _ = await validation_repo.list(
        status=ValidationStatus.PENDING,
        validation_type=ValidationType.COMPANY,
        skip=0,
        limit=0
    )

    # Count profiles by type
    admin_profiles = await profile_repo.list_by_type(ProfileType.ADMIN, skip=0, limit=1000)
    agency_profiles = await profile_repo.list_by_type(ProfileType.AGENCY, skip=0, limit=1000)
    company_profiles = await profile_repo.list_by_type(ProfileType.COMPANY, skip=0, limit=1000)
    interim_profiles = await profile_repo.list_by_type(ProfileType.INTERIM, skip=0, limit=1000)

    # Get recent rejections (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    rejected_recent, _ = await validation_repo.list(
        status=ValidationStatus.REJECTED,
        skip=0,
        limit=1000
    )
    recent_rejections = [
        v for v in rejected_recent
        if v.reviewed_at and v.reviewed_at > seven_days_ago
    ]

    return {
        "validations": {
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
            "pending_interim": len(pending_interim),
            "pending_company": len(pending_company),
            "recent_rejections_7d": len(recent_rejections)
        },
        "profiles": {
            "admin": len(admin_profiles),
            "agency": len(agency_profiles),
            "company": len(company_profiles),
            "interim": len(interim_profiles),
            "total": len(admin_profiles) + len(agency_profiles) + len(company_profiles) + len(interim_profiles)
        },
        "active_users": approved_count
    }


@router.get("/users/{user_id}/audit")
async def get_user_audit_trail(
    user_id: str,
    current_user=Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get audit trail for a specific user (admin only)"""
    from src.infrastructure.repositories.audit_repository import AuditRepository

    audit_repo = AuditRepository(db)
    audits = await audit_repo.list_by_user(user_id, skip=0, limit=100)

    return {
        "user_id": user_id,
        "audit_entries": [
            {
                "id": audit.id,
                "action": audit.action,
                "entity": audit.entity,
                "entity_id": audit.entity_id,
                "changes": audit.changes,
                "metadata": audit.metadata,
                "created_at": audit.created_at.isoformat()
            }
            for audit in audits
        ],
        "total": len(audits)
    }
