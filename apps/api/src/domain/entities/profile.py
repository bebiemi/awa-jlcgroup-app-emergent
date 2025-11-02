"""Profile domain entities"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class ProfileType(str, Enum):
    """Profile types matching user roles"""
    ADMIN = "admin"
    AGENCY = "agency"
    COMPANY = "company"
    INTERIM = "interim"


class ProfileBase(BaseModel):
    """Base profile fields for all users"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    profile_type: ProfileType
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class AgencyProfile(BaseModel):
    """Extended profile for Agency users"""
    agency_name: Optional[str] = None
    agency_code: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class CompanyProfile(BaseModel):
    """Extended profile for Company users"""
    company_name: Optional[str] = None
    registration_number: Optional[str] = None  # SIRET
    address: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None


class InterimProfile(BaseModel):
    """Extended profile for Interim (temporary worker) users"""
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    resume_url: Optional[str] = None
    availability: Optional[str] = None
    bio: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)


class Profile(ProfileBase):
    """Complete profile with role-specific data"""
    # Extended data stored as nested objects
    agency_data: Optional[AgencyProfile] = None
    company_data: Optional[CompanyProfile] = None
    interim_data: Optional[InterimProfile] = None

    def get_extended_data(self):
        """Get role-specific extended data"""
        if self.profile_type == ProfileType.AGENCY:
            return self.agency_data
        elif self.profile_type == ProfileType.COMPANY:
            return self.company_data
        elif self.profile_type == ProfileType.INTERIM:
            return self.interim_data
        return None

    def calculate_completeness(self) -> int:
        """Calculate profile completeness percentage"""
        total_fields = 0
        filled_fields = 0

        # Base fields
        base_fields = [self.first_name, self.last_name, self.phone, self.avatar_url]
        total_fields += len(base_fields)
        filled_fields += sum(1 for field in base_fields if field)

        # Extended fields by type
        extended_data = self.get_extended_data()
        if extended_data:
            if isinstance(extended_data, InterimProfile):
                fields = [
                    extended_data.skills,
                    extended_data.experience_years,
                    extended_data.resume_url,
                    extended_data.availability,
                    extended_data.bio
                ]
                total_fields += len(fields)
                filled_fields += sum(1 for field in fields if field)
            elif isinstance(extended_data, CompanyProfile):
                fields = [
                    extended_data.company_name,
                    extended_data.registration_number,
                    extended_data.address,
                    extended_data.industry
                ]
                total_fields += len(fields)
                filled_fields += sum(1 for field in fields if field)
            elif isinstance(extended_data, AgencyProfile):
                fields = [
                    extended_data.agency_name,
                    extended_data.agency_code,
                    extended_data.address
                ]
                total_fields += len(fields)
                filled_fields += sum(1 for field in fields if field)

        return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
