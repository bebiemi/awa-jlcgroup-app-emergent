"""Account validation domain entities"""
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ValidationType(str, Enum):
    """Type of account validation"""
    COMPANY = "company"
    INTERIM = "interim"


class ValidationStatus(str, Enum):
    """Status of account validation"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AccountValidation(BaseModel):
    """Account validation request"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    validation_type: ValidationType
    status: ValidationStatus = ValidationStatus.PENDING
    comment: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_by_email: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
