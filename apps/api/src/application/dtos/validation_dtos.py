"""Validation DTOs for requests and responses"""
from typing import Optional
from pydantic import BaseModel
from src.domain.entities.validation import ValidationType, ValidationStatus


class ValidationResponse(BaseModel):
    """Validation response DTO"""
    id: str
    user_id: str
    user_email: Optional[str]
    user_name: Optional[str]
    validation_type: ValidationType
    status: ValidationStatus
    comment: Optional[str]
    reviewed_by: Optional[str]
    reviewed_by_email: Optional[str]
    reviewed_at: Optional[str]
    created_at: str


class ApproveValidationRequest(BaseModel):
    """Approve validation request DTO"""
    comment: Optional[str] = None


class RejectValidationRequest(BaseModel):
    """Reject validation request DTO"""
    comment: str


class ValidationListResponse(BaseModel):
    """Paginated validation list response"""
    items: list[ValidationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
