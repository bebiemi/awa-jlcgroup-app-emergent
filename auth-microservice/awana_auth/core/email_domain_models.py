"""
Email Domain Models for collaborator email validation
Stores allowed email domains for JLC Group collaborators
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class AllowedEmailDomain(BaseModel):
    """Model for allowed email domains (collaborators)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = Field(..., description="Email domain (e.g., @jlcgroup.org)")
    country_code: Optional[str] = Field(None, description="Country code (e.g., GA, CM, CG)")
    is_active: bool = Field(default=True, description="Whether domain is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User ID who created this domain")
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('domain')
    def validate_domain(cls, v):
        """Ensure domain starts with @"""
        if not v:
            raise ValueError("Domain cannot be empty")
        if not v.startswith('@'):
            v = f"@{v}"
        # Basic domain format validation
        if '.' not in v:
            raise ValueError("Domain must contain a dot (e.g., @jlcgroup.org)")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "domain": "@jlcgroup.org",
                "country_code": "GA",
                "is_active": True,
                "metadata": {
                    "description": "Main JLC Group domain"
                }
            }
        }


class AllowedEmailDomainCreate(BaseModel):
    """Schema for creating a new allowed domain"""
    domain: str = Field(..., description="Email domain")
    country_code: Optional[str] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('domain')
    def validate_domain(cls, v):
        if not v:
            raise ValueError("Domain cannot be empty")
        if not v.startswith('@'):
            v = f"@{v}"
        if '.' not in v:
            raise ValueError("Domain must contain a dot")
        return v.lower()


class AllowedEmailDomainUpdate(BaseModel):
    """Schema for updating an allowed domain"""
    country_code: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class EmailDomainVerification(BaseModel):
    """Response for email domain verification"""
    email: str
    is_valid: bool
    domain: str
    is_collaborator: bool
    message: str
