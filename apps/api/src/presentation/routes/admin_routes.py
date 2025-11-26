"""Admin routes for KPIs and statistics"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.presentation.dependencies import (
    get_all_profile_type_values,
    get_database,
    get_profile_types_from_config,
    get_validation_workflow_config,
    require_admin,
)
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

    validation_config = get_validation_workflow_config()
    validation_statuses = validation_config.get("statuses", {})
    validation_types = validation_config.get("types", {})

    def _as_status(value: str):
        if isinstance(value, ValidationStatus):
            return value
        if value in ValidationStatus._value2member_map_:
            return ValidationStatus(value)
        return value

    def _as_validation_type(value: str):
        if isinstance(value, ValidationType):
            return value
        if value in ValidationType._value2member_map_:
            return ValidationType(value)
        return value

    # Count validations by status
    pending_status_value = validation_statuses.get("pending", ValidationStatus.PENDING.value)
    approved_status_value = validation_statuses.get("approved", ValidationStatus.APPROVED.value)
    rejected_status_value = validation_statuses.get("rejected", ValidationStatus.REJECTED.value)

    pending_count = await validation_repo.count_by_status(_as_status(pending_status_value))
    approved_count = await validation_repo.count_by_status(_as_status(approved_status_value))
    rejected_count = await validation_repo.count_by_status(_as_status(rejected_status_value))

    # Count pending by type
    interim_type_value = validation_types.get("interim", ValidationType.INTERIM.value)
    company_type_value = validation_types.get("company", ValidationType.COMPANY.value)

    pending_interim, _ = await validation_repo.list(
        status=_as_status(pending_status_value),
        validation_type=_as_validation_type(interim_type_value),
        skip=0,
        limit=0
    )
    pending_company, _ = await validation_repo.list(
        status=_as_status(pending_status_value),
        validation_type=_as_validation_type(company_type_value),
        skip=0,
        limit=0
    )

    # Count profiles by type
    profile_types = get_profile_types_from_config()
    profile_values = get_all_profile_type_values()

    def _as_profile_type(profile_value: str):
        if profile_value in ProfileType._value2member_map_:
            return ProfileType(profile_value)
        return profile_value

    admin_profiles = await profile_repo.list_by_type(
        _as_profile_type(profile_types.get("admin", ProfileType.ADMIN.value)), skip=0, limit=1000
    )
    agency_profiles = await profile_repo.list_by_type(
        _as_profile_type(profile_types.get("agency", ProfileType.AGENCY.value)), skip=0, limit=1000
    )
    company_profiles = await profile_repo.list_by_type(
        _as_profile_type(profile_types.get("company", ProfileType.COMPANY.value)), skip=0, limit=1000
    )
    interim_profiles = await profile_repo.list_by_type(
        _as_profile_type(profile_types.get("interim", ProfileType.INTERIM.value)), skip=0, limit=1000
    )

    # Get recent rejections (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    rejected_recent, _ = await validation_repo.list(
        status=_as_status(rejected_status_value),
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
            "total": sum(
                len(bucket)
                for bucket in [admin_profiles, agency_profiles, company_profiles, interim_profiles]
            ),
            "all_codes": profile_values,
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
