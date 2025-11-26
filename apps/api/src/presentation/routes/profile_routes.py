"""Profile routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.presentation.dependencies import (
    get_admin_roles_from_config,
    get_database,
    get_current_user,
)
from src.application.dtos.profile_dtos import (
    ProfileResponse,
    UpdateProfileRequest,
    CreateProfileRequest
)
from src.domain.entities.profile import (
    Profile,
    ProfileType,
    AgencyProfile,
    CompanyProfile,
    InterimProfile
)
from src.infrastructure.repositories.profile_repository import ProfileRepository
from src.infrastructure.repositories.audit_repository import AuditRepository
from src.infrastructure.providers.storage_provider import get_storage_provider
from src.domain.entities.audit import AuditTrail
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profiles", tags=["Profiles"])


def profile_to_response(profile: Profile) -> ProfileResponse:
    """Convert profile entity to response DTO"""
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        profile_type=profile.profile_type,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone=profile.phone,
        avatar_url=profile.avatar_url,
        agency_data=profile.agency_data,
        company_data=profile.company_data,
        interim_data=profile.interim_data,
        completeness=profile.calculate_completeness(),
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user's profile"""
    repo = ProfileRepository(db)
    profile = await repo.get_by_user_id(current_user['id'])

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile_to_response(profile)


@router.post("/me", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_data: CreateProfileRequest,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create profile for current user"""
    repo = ProfileRepository(db)
    audit_repo = AuditRepository(db)

    # Check if profile already exists
    existing = await repo.get_by_user_id(current_user['id'])
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )

    # Create profile
    profile = Profile(
        user_id=current_user['id'],
        profile_type=profile_data.profile_type,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        phone=profile_data.phone
    )

    # Initialize extended data based on profile type
    if profile.profile_type == ProfileType.AGENCY:
        profile.agency_data = AgencyProfile()
    elif profile.profile_type == ProfileType.COMPANY:
        profile.company_data = CompanyProfile()
    elif profile.profile_type == ProfileType.INTERIM:
        profile.interim_data = InterimProfile()

    created_profile = await repo.create(profile)

    # Audit log
    audit = AuditTrail(
        user_id=current_user['id'],
        user_email=current_user.get('email'),
        action="PROFILE_CREATED",
        entity="profile",
        entity_id=created_profile.id,
        metadata={"profile_type": profile.profile_type.value}
    )
    await audit_repo.create(audit)

    return profile_to_response(created_profile)


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    update_data: UpdateProfileRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update current user's profile"""
    repo = ProfileRepository(db)
    audit_repo = AuditRepository(db)

    # Get existing profile
    profile = await repo.get_by_user_id(current_user['id'])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Track changes
    changes = {}

    # Update base fields
    if update_data.first_name is not None:
        changes['first_name'] = {'old': profile.first_name, 'new': update_data.first_name}
        profile.first_name = update_data.first_name
    if update_data.last_name is not None:
        changes['last_name'] = {'old': profile.last_name, 'new': update_data.last_name}
        profile.last_name = update_data.last_name
    if update_data.phone is not None:
        changes['phone'] = {'old': profile.phone, 'new': update_data.phone}
        profile.phone = update_data.phone

    # Update extended fields based on profile type
    if profile.profile_type == ProfileType.AGENCY:
        if profile.agency_data is None:
            profile.agency_data = AgencyProfile()
        if update_data.agency_name is not None:
            profile.agency_data.agency_name = update_data.agency_name
        if update_data.agency_code is not None:
            profile.agency_data.agency_code = update_data.agency_code
        if update_data.address is not None:
            profile.agency_data.address = update_data.address
        if update_data.description is not None:
            profile.agency_data.description = update_data.description

    elif profile.profile_type == ProfileType.COMPANY:
        if profile.company_data is None:
            profile.company_data = CompanyProfile()
        if update_data.company_name is not None:
            profile.company_data.company_name = update_data.company_name
        if update_data.registration_number is not None:
            profile.company_data.registration_number = update_data.registration_number
        if update_data.address is not None:
            profile.company_data.address = update_data.address
        if update_data.industry is not None:
            profile.company_data.industry = update_data.industry
        if update_data.company_size is not None:
            profile.company_data.company_size = update_data.company_size
        if update_data.website is not None:
            profile.company_data.website = update_data.website

    elif profile.profile_type == ProfileType.INTERIM:
        if profile.interim_data is None:
            profile.interim_data = InterimProfile()
        if update_data.skills is not None:
            profile.interim_data.skills = update_data.skills
        if update_data.experience_years is not None:
            profile.interim_data.experience_years = update_data.experience_years
        if update_data.availability is not None:
            profile.interim_data.availability = update_data.availability
        if update_data.bio is not None:
            profile.interim_data.bio = update_data.bio
        if update_data.certifications is not None:
            profile.interim_data.certifications = update_data.certifications

    # Update profile
    updated_profile = await repo.update(profile)

    # Audit log
    if changes:
        audit = AuditTrail(
            user_id=current_user['id'],
            user_email=current_user.get('email'),
            action="PROFILE_UPDATED",
            entity="profile",
            entity_id=profile.id,
            changes=changes
        )
        await audit_repo.create(audit)

    return profile_to_response(updated_profile)


@router.post("/me/avatar", response_model=ProfileResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Upload user avatar"""
    repo = ProfileRepository(db)
    audit_repo = AuditRepository(db)
    storage = get_storage_provider()

    # Get profile
    profile = await repo.get_by_user_id(current_user['id'])
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    # Upload file
    try:
        old_avatar = profile.avatar_url
        avatar_url = await storage.upload_file(
            file.file,
            file.filename,
            file.content_type,
            folder="avatars"
        )

        # Update profile
        profile.avatar_url = avatar_url
        updated_profile = await repo.update(profile)

        # Delete old avatar if exists
        if old_avatar:
            await storage.delete_file(old_avatar)

        # Audit log
        audit = AuditTrail(
            user_id=current_user['id'],
            user_email=current_user.get('email'),
            action="AVATAR_UPLOADED",
            entity="profile",
            entity_id=profile.id,
            metadata={"avatar_url": avatar_url}
        )
        await audit_repo.create(audit)

        return profile_to_response(updated_profile)

    except Exception as e:
        logger.error(f"Failed to upload avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar"
        )


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get user profile by ID (admin or self only)"""
    # Check permission: admin or self
    user_roles = current_user.get('roles', [])
    admin_roles = get_admin_roles_from_config()
    if not any(role in admin_roles for role in user_roles) and current_user['id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    repo = ProfileRepository(db)
    profile = await repo.get_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile_to_response(profile)
