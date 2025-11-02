"""Profile DTOs for requests and responses"""
from typing import Optional, List
from pydantic import BaseModel, Field
from src.domain.entities.profile import ProfileType, AgencyProfile, CompanyProfile, InterimProfile


class ProfileResponse(BaseModel):
    """Profile response DTO"""
    id: str
    user_id: str
    profile_type: ProfileType
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    agency_data: Optional[AgencyProfile]
    company_data: Optional[CompanyProfile]
    interim_data: Optional[InterimProfile]
    completeness: int = 0
    created_at: str
    updated_at: str


class UpdateProfileRequest(BaseModel):
    """Update profile request DTO"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    # Agency fields
    agency_name: Optional[str] = None
    agency_code: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    # Company fields
    company_name: Optional[str] = None
    registration_number: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    # Interim fields
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    availability: Optional[str] = None
    bio: Optional[str] = None
    certifications: Optional[List[str]] = None


class CreateProfileRequest(BaseModel):
    """Create profile request DTO"""
    user_id: str
    profile_type: ProfileType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
