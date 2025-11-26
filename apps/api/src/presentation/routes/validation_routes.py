"""Validation routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from src.presentation.dependencies import (
    get_database,
    get_current_user,
    require_validator,
)
from src.application.dtos.validation_dtos import (
    ValidationResponse,
    ApproveValidationRequest,
    RejectValidationRequest,
    ValidationListResponse
)
from src.domain.entities.validation import (
    AccountValidation,
    ValidationStatus,
    ValidationType
)
from src.infrastructure.repositories.validation_repository import ValidationRepository
from src.infrastructure.repositories.audit_repository import AuditRepository
from src.domain.entities.audit import AuditTrail
from src.domain.entities.notification import Notification, NotificationChannel, NotificationPriority
from src.infrastructure.repositories.notification_repository import NotificationRepository
from src.infrastructure.providers.email_provider import get_email_provider
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/validations", tags=["Validations"])


def _enum_value(value):
    return value.value if hasattr(value, "value") else str(value)


def validation_to_response(validation: AccountValidation) -> ValidationResponse:
    """Convert validation entity to response DTO"""
    return ValidationResponse(
        id=validation.id,
        user_id=validation.user_id,
        user_email=validation.user_email,
        user_name=validation.user_name,
        validation_type=validation.validation_type,
        status=validation.status,
        comment=validation.comment,
        reviewed_by=validation.reviewed_by,
        reviewed_by_email=validation.reviewed_by_email,
        reviewed_at=validation.reviewed_at.isoformat() if validation.reviewed_at else None,
        created_at=validation.created_at.isoformat()
    )


@router.get("/me", response_model=ValidationResponse)
async def get_my_validation(
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's validation status"""
    repo = ValidationRepository(db)
    validation = await repo.get_by_user_id(current_user['id'])

    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No validation found"
        )

    return validation_to_response(validation)


@router.get("/admin", response_model=ValidationListResponse)
async def list_validations(
    status_filter: Optional[ValidationStatus] = Query(None, alias="status"),
    type_filter: Optional[ValidationType] = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(require_validator),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List validations (admin only)"""
    repo = ValidationRepository(db)

    skip = (page - 1) * page_size
    validations, total = await repo.list(
        status=status_filter,
        validation_type=type_filter,
        skip=skip,
        limit=page_size
    )

    total_pages = math.ceil(total / page_size)

    return ValidationListResponse(
        items=[validation_to_response(v) for v in validations],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/admin/{validation_id}/approve", response_model=ValidationResponse)
async def approve_validation(
    validation_id: str,
    request_data: ApproveValidationRequest,
    request: Request,
    current_user=Depends(require_validator),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Approve a validation (admin only)"""
    repo = ValidationRepository(db)
    audit_repo = AuditRepository(db)
    notification_repo = NotificationRepository(db)
    email_provider = get_email_provider()

    # Get validation
    validation = await repo.get_by_id(validation_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )

    # Check if already processed
    current_status = _enum_value(validation.status)
    if current_status != ValidationStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation already processed",
        )

    # Update validation
    validation.status = ValidationStatus.APPROVED.value
    validation.comment = request_data.comment
    validation.reviewed_by = current_user['id']
    validation.reviewed_by_email = current_user.get('email')
    validation.reviewed_at = datetime.utcnow()

    updated_validation = await repo.update(validation)

    # Create in-app notification
    notification = Notification(
        user_id=validation.user_id,
        channel=NotificationChannel.INAPP,
        title="Compte approuvé ✅",
        body=f"Félicitations! Votre compte {_enum_value(validation.validation_type)} a été approuvé.",
        priority=NotificationPriority.HIGH,
        action_url="/profile"
    )
    await notification_repo.create(notification)

    # Send email notification
    if validation.user_email:
        html_body = f"""
        <html>
        <body>
            <h2>Compte Approuvé</h2>
            <p>Bonjour {validation.user_name or 'Cher utilisateur'},</p>
            <p>Votre compte <strong>{_enum_value(validation.validation_type)}</strong> a été approuvé par notre équipe.</p>
            <p>Vous pouvez maintenant accéder à toutes les fonctionnalités de la plateforme JLC Group.</p>
            {f'<p>Commentaire: {request_data.comment}</p>' if request_data.comment else ''}
            <p>Cordialement,<br>L'équipe JLC Group</p>
        </body>
        </html>
        """
        await email_provider.send_email(
            to=[validation.user_email],
            subject="Votre compte JLC Group a été approuvé",
            html_body=html_body
        )

    # Audit log
    audit = AuditTrail(
        user_id=current_user['id'],
        user_email=current_user.get('email'),
        action="VALIDATION_APPROVED",
        entity="validation",
        entity_id=validation.id,
        metadata={
            "validation_type": _enum_value(validation.validation_type),
            "user_id": validation.user_id,
            "comment": request_data.comment
        }
    )
    await audit_repo.create(audit)

    logger.info(f"Validation {validation_id} approved by {current_user['email']}")

    return validation_to_response(updated_validation)


@router.post("/admin/{validation_id}/reject", response_model=ValidationResponse)
async def reject_validation(
    validation_id: str,
    request_data: RejectValidationRequest,
    request: Request,
    current_user=Depends(require_validator),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reject a validation (admin only)"""
    repo = ValidationRepository(db)
    audit_repo = AuditRepository(db)
    notification_repo = NotificationRepository(db)
    email_provider = get_email_provider()

    # Get validation
    validation = await repo.get_by_id(validation_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation not found"
        )

    # Check if already processed
    current_status = _enum_value(validation.status)
    if current_status != ValidationStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation already processed",
        )

    # Update validation
    validation.status = ValidationStatus.REJECTED.value
    validation.comment = request_data.comment
    validation.reviewed_by = current_user['id']
    validation.reviewed_by_email = current_user.get('email')
    validation.reviewed_at = datetime.utcnow()

    updated_validation = await repo.update(validation)

    # Create in-app notification
    notification = Notification(
        user_id=validation.user_id,
        channel=NotificationChannel.INAPP,
        title="Compte refusé ❌",
        body=f"Votre demande de compte {_enum_value(validation.validation_type)} a été refusée. Raison: {request_data.comment}",
        priority=NotificationPriority.HIGH,
        action_url="/profile"
    )
    await notification_repo.create(notification)

    # Send email notification
    if validation.user_email:
        html_body = f"""
        <html>
        <body>
            <h2>Compte Refusé</h2>
            <p>Bonjour {validation.user_name or 'Cher utilisateur'},</p>
            <p>Nous regrettons de vous informer que votre demande de compte <strong>{_enum_value(validation.validation_type)}</strong> a été refusée.</p>
            <p><strong>Raison:</strong> {request_data.comment}</p>
            <p>Si vous pensez qu'il s'agit d'une erreur, veuillez nous contacter.</p>
            <p>Cordialement,<br>L'équipe JLC Group</p>
        </body>
        </html>
        """
        await email_provider.send_email(
            to=[validation.user_email],
            subject="Votre demande de compte JLC Group",
            html_body=html_body
        )

    # Audit log
    audit = AuditTrail(
        user_id=current_user['id'],
        user_email=current_user.get('email'),
        action="VALIDATION_REJECTED",
        entity="validation",
        entity_id=validation.id,
        metadata={
            "validation_type": _enum_value(validation.validation_type),
            "user_id": validation.user_id,
            "comment": request_data.comment
        }
    )
    await audit_repo.create(audit)

    logger.info(f"Validation {validation_id} rejected by {current_user['email']}")

    return validation_to_response(updated_validation)
