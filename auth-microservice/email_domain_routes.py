"""
Email Domain Management Routes
CRUD operations for allowed email domains
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from awana_auth.core.email_domain_models import (
    AllowedEmailDomain,
    AllowedEmailDomainCreate,
    AllowedEmailDomainUpdate,
    EmailDomainVerification
)
from awana_auth.services.email_domain_service import EmailDomainService
from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission

router = APIRouter(prefix="/api/security/email-domains", tags=["Email Domains"])


async def get_email_domain_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> EmailDomainService:
    """Dependency to get email domain service"""
    return EmailDomainService(db)


@router.post("/verify", response_model=EmailDomainVerification)
async def verify_email_domain(
    email: str,
    service: EmailDomainService = Depends(get_email_domain_service)
):
    """
    Verify if an email domain is allowed for collaborators
    Public endpoint - no authentication required
    """
    result = await service.verify_email_domain(email)
    return result


@router.get("", response_model=List[AllowedEmailDomain])
async def list_email_domains(
    active_only: bool = False,
    service: EmailDomainService = Depends(get_email_domain_service),
    user: dict = Depends(require_permission('security.email_domains.read'))
):
    """
    List all allowed email domains
    Requires: security.email_domains.read permission
    """
    domains = await service.list_domains(active_only=active_only)
    return domains


@router.get("/{domain_id}", response_model=AllowedEmailDomain)
async def get_email_domain(
    domain_id: str,
    service: EmailDomainService = Depends(get_email_domain_service),
    user: dict = Depends(require_permission('security.email_domains.read'))
):
    """
    Get a specific email domain by ID
    Requires: security.email_domains.read permission
    """
    domain = await service.get_domain(domain_id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    return domain


@router.post("", response_model=AllowedEmailDomain, status_code=status.HTTP_201_CREATED)
async def create_email_domain(
    domain_create: AllowedEmailDomainCreate,
    service: EmailDomainService = Depends(get_email_domain_service),
    user: dict = Depends(require_permission('security.email_domains.manage'))
):
    """
    Create a new allowed email domain
    Requires: security.email_domains.manage permission
    """
    # Check if domain already exists
    existing_domains = await service.list_domains()
    for existing in existing_domains:
        if existing.get("domain") == domain_create.domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Domain {domain_create.domain} already exists"
            )
    
    # Create domain
    domain_data = domain_create.dict()
    import uuid
    domain_data["id"] = str(uuid.uuid4())
    
    created_domain = await service.create_domain(
        domain_data,
        created_by=user.get("id")
    )
    
    return created_domain


@router.put("/{domain_id}", response_model=AllowedEmailDomain)
async def update_email_domain(
    domain_id: str,
    domain_update: AllowedEmailDomainUpdate,
    service: EmailDomainService = Depends(get_email_domain_service),
    user: dict = Depends(require_permission('security.email_domains.manage'))
):
    """
    Update an existing email domain
    Requires: security.email_domains.manage permission
    """
    # Check if domain exists
    existing = await service.get_domain(domain_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    # Update domain
    update_data = domain_update.dict(exclude_unset=True)
    updated_domain = await service.update_domain(domain_id, update_data)
    
    if not updated_domain:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update domain"
        )
    
    return updated_domain


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_domain(
    domain_id: str,
    service: EmailDomainService = Depends(get_email_domain_service),
    user: dict = Depends(require_permission('security.email_domains.manage'))
):
    """
    Delete an email domain (soft delete)
    Requires: security.email_domains.manage permission
    """
    success = await service.delete_domain(domain_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    return None


@router.get("/active/list", response_model=List[str])
async def get_active_domains_list(
    service: EmailDomainService = Depends(get_email_domain_service)
):
    """
    Get list of active domain strings
    Public endpoint for validation
    """
    domains = await service.get_all_active_domains()
    return domains
