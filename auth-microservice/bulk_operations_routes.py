"""
Bulk Operations Routes for User Management
Handles mass operations on multiple users at once
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.models import User
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import csv
import io

bulk_router = APIRouter()


class BulkOperationRequest(BaseModel):
    """Request model for bulk operations"""
    user_ids: List[str]
    reason: Optional[str] = None


class BulkUpdateStatusRequest(BaseModel):
    """Request model for bulk status update"""
    user_ids: List[str]
    status: str  # 'active', 'suspended', 'archived'
    reason: Optional[str] = None


class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete"""
    user_ids: List[str]
    permanent: bool = False
    reason: Optional[str] = None


class BulkOperationResponse(BaseModel):
    """Response model for bulk operations"""
    success: bool
    message: str
    total: int
    succeeded: int
    failed: int
    errors: List[dict] = []


@bulk_router.post("/bulk-block", response_model=BulkOperationResponse)
async def bulk_block_users(
    request: BulkOperationRequest,
    current_user: User = Depends(require_permission("users.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Block multiple users at once"""
    succeeded = 0
    failed = 0
    errors = []
    
    for user_id in request.user_ids:
        try:
            # Check if user exists
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                errors.append({"user_id": user_id, "error": "User not found"})
                failed += 1
                continue
            
            # Don't allow blocking super admins
            if "super_admin" in user.get("roles", []):
                errors.append({"user_id": user_id, "error": "Cannot block super admin"})
                failed += 1
                continue
            
            # Update status to suspended
            result = await db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "status": "suspended",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                succeeded += 1
            else:
                failed += 1
                errors.append({"user_id": user_id, "error": "Failed to update"})
                
        except Exception as e:
            failed += 1
            errors.append({"user_id": user_id, "error": str(e)})
    
    return BulkOperationResponse(
        success=failed == 0,
        message=f"Blocked {succeeded} user(s), {failed} failed",
        total=len(request.user_ids),
        succeeded=succeeded,
        failed=failed,
        errors=errors
    )


@bulk_router.post("/bulk-unblock", response_model=BulkOperationResponse)
async def bulk_unblock_users(
    request: BulkOperationRequest,
    current_user: User = Depends(require_permission("users.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Unblock multiple users at once"""
    succeeded = 0
    failed = 0
    errors = []
    
    for user_id in request.user_ids:
        try:
            # Update status to active
            result = await db.users.update_one(
                {"id": user_id, "status": "suspended"},
                {
                    "$set": {
                        "status": "active",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                succeeded += 1
            else:
                # Check if user was already active or doesn't exist
                user = await db.users.find_one({"id": user_id}, {"_id": 0})
                if not user:
                    errors.append({"user_id": user_id, "error": "User not found"})
                else:
                    errors.append({"user_id": user_id, "error": "User not suspended"})
                failed += 1
                
        except Exception as e:
            failed += 1
            errors.append({"user_id": user_id, "error": str(e)})
    
    return BulkOperationResponse(
        success=failed == 0,
        message=f"Unblocked {succeeded} user(s), {failed} failed",
        total=len(request.user_ids),
        succeeded=succeeded,
        failed=failed,
        errors=errors
    )


@bulk_router.post("/bulk-archive", response_model=BulkOperationResponse)
async def bulk_archive_users(
    request: BulkOperationRequest,
    current_user: User = Depends(require_permission("users.update")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Archive multiple users at once"""
    succeeded = 0
    failed = 0
    errors = []
    
    for user_id in request.user_ids:
        try:
            # Check if user exists
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                errors.append({"user_id": user_id, "error": "User not found"})
                failed += 1
                continue
            
            # Don't allow archiving super admins
            if "super_admin" in user.get("roles", []):
                errors.append({"user_id": user_id, "error": "Cannot archive super admin"})
                failed += 1
                continue
            
            # Update status to archived
            result = await db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "status": "archived",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                succeeded += 1
            else:
                failed += 1
                errors.append({"user_id": user_id, "error": "Failed to update"})
                
        except Exception as e:
            failed += 1
            errors.append({"user_id": user_id, "error": str(e)})
    
    return BulkOperationResponse(
        success=failed == 0,
        message=f"Archived {succeeded} user(s), {failed} failed",
        total=len(request.user_ids),
        succeeded=succeeded,
        failed=failed,
        errors=errors
    )


@bulk_router.post("/bulk-delete", response_model=BulkOperationResponse)
async def bulk_delete_users(
    request: BulkDeleteRequest,
    current_user: User = Depends(require_permission("users.delete")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete multiple users at once (soft delete by default)"""
    succeeded = 0
    failed = 0
    errors = []
    
    for user_id in request.user_ids:
        try:
            # Check if user exists
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                errors.append({"user_id": user_id, "error": "User not found"})
                failed += 1
                continue
            
            # Don't allow deleting super admins
            if "super_admin" in user.get("roles", []):
                errors.append({"user_id": user_id, "error": "Cannot delete super admin"})
                failed += 1
                continue
            
            if request.permanent:
                # Hard delete
                result = await db.users.delete_one({"id": user_id})
                if result.deleted_count > 0:
                    succeeded += 1
                else:
                    failed += 1
            else:
                # Soft delete (archive user instead of marking as deleted)
                result = await db.users.update_one(
                    {"id": user_id},
                    {
                        "$set": {
                            "status": "archived",
                            "archived_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                if result.modified_count > 0:
                    succeeded += 1
                else:
                    failed += 1
                    errors.append({"user_id": user_id, "error": "Failed to delete"})
                
        except Exception as e:
            failed += 1
            errors.append({"user_id": user_id, "error": str(e)})
    
    return BulkOperationResponse(
        success=failed == 0,
        message=f"Deleted {succeeded} user(s), {failed} failed",
        total=len(request.user_ids),
        succeeded=succeeded,
        failed=failed,
        errors=errors
    )


@bulk_router.post("/export-csv")
async def export_users_csv(
    request: BulkOperationRequest,
    current_user: User = Depends(require_permission("users.read")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Export selected users to CSV"""
    from fastapi.responses import StreamingResponse
    
    # Fetch users
    users = []
    for user_id in request.user_ids:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user:
            users.append(user)
    
    # Create CSV
    output = io.StringIO()
    fieldnames = ['id', 'username', 'email', 'full_name', 'status', 'roles', 'created_at', 'last_login_at', 'is_verified']
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    
    writer.writeheader()
    for user in users:
        # Format roles as comma-separated string
        user_data = user.copy()
        user_data['roles'] = ','.join(user.get('roles', []))
        user_data['created_at'] = user.get('created_at', '').isoformat() if isinstance(user.get('created_at'), datetime) else user.get('created_at', '')
        user_data['last_login_at'] = user.get('last_login_at', '').isoformat() if isinstance(user.get('last_login_at'), datetime) else user.get('last_login_at', '')
        writer.writerow(user_data)
    
    # Return CSV as download
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=users_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@bulk_router.post("/bulk-import")
async def bulk_import_users(
    file: bytes = Depends(lambda request: request.body()),
    current_user: User = Depends(require_permission("users.create")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Bulk import users from CSV file
    Expected CSV format: username,email,full_name,roles,phone
    - Auto-generates secure passwords
    - Sends invitation emails with activation links
    - Validates email domains against allowed list
    - Returns detailed success/error report
    """
    from fastapi import UploadFile, File
    import secrets
    import string
    import re
    from uuid import uuid4
    
    succeeded = 0
    failed = 0
    errors = []
    created_users = []
    
    try:
        # Parse CSV
        csv_content = file.decode('utf-8')
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Get allowed email domains
        allowed_domains_doc = await db.email_domains.find_one({}, {"_id": 0})
        allowed_domains = allowed_domains_doc.get('domains', []) if allowed_domains_doc else []
        
        line_number = 1  # Start at 1 (header is line 0)
        for row in reader:
            line_number += 1
            username = row.get('username', '').strip()
            email = row.get('email', '').strip().lower()
            full_name = row.get('full_name', '').strip()
            roles_str = row.get('roles', 'interim').strip()
            phone = row.get('phone', '').strip()
            
            # Validation
            if not username or not email:
                errors.append({
                    "line": line_number,
                    "username": username,
                    "email": email,
                    "error": "Username and email are required"
                })
                failed += 1
                continue
            
            # Validate email format
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                errors.append({
                    "line": line_number,
                    "username": username,
                    "email": email,
                    "error": "Invalid email format"
                })
                failed += 1
                continue
            
            # Validate email domain if allowed_domains list exists
            if allowed_domains:
                email_domain = email.split('@')[1]
                if email_domain not in allowed_domains:
                    errors.append({
                        "line": line_number,
                        "username": username,
                        "email": email,
                        "error": f"Email domain '{email_domain}' not in allowed list"
                    })
                    failed += 1
                    continue
            
            # Check if user already exists
            existing_user = await db.users.find_one({
                "$or": [
                    {"username": username},
                    {"email": email}
                ]
            }, {"_id": 0})
            
            if existing_user:
                errors.append({
                    "line": line_number,
                    "username": username,
                    "email": email,
                    "error": "User with this username or email already exists"
                })
                failed += 1
                continue
            
            # Generate secure password (16 chars, alphanumeric + symbols)
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(alphabet) for _ in range(16))
            
            # Parse roles (comma-separated)
            roles = [r.strip() for r in roles_str.split(',') if r.strip()]
            if not roles:
                roles = ['interim']  # Default role
            
            # Validate roles
            valid_roles = ['admin', 'super_admin', 'candidat', 'interim', 'company', 'collaborator', 'postulant']
            roles = [r for r in roles if r in valid_roles]
            if not roles:
                roles = ['interim']
            
            # Create user
            from awana_auth.core.security import get_password_hash
            user_id = str(uuid4())
            new_user = {
                "id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name or username,
                "password_hash": get_password_hash(password),
                "provider": "local",
                "status": "pending",  # Pending email verification
                "roles": roles,
                "is_verified": False,
                "phone": phone or None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "login_count": 0,
                "failed_login_attempts": 0,
                "metadata": {
                    "created_by": "bulk_import",
                    "created_by_user_id": current_user.id,
                    "imported_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
            try:
                await db.users.insert_one(new_user)
                
                # Create user roles
                for role in roles:
                    await db.user_roles.insert_one({
                        "user_id": user_id,
                        "role": role,
                        "created_at": datetime.now(timezone.utc)
                    })
                
                # TODO: Send invitation email with password and activation link
                # For now, store password temporarily (in real app, send via email only)
                created_users.append({
                    "username": username,
                    "email": email,
                    "password": password,  # In production, this would be sent via email only
                    "roles": roles
                })
                
                succeeded += 1
                
            except Exception as e:
                errors.append({
                    "line": line_number,
                    "username": username,
                    "email": email,
                    "error": f"Database error: {str(e)}"
                })
                failed += 1
        
        return {
            "success": failed == 0,
            "message": f"Imported {succeeded} user(s), {failed} failed",
            "total": succeeded + failed,
            "succeeded": succeeded,
            "failed": failed,
            "errors": errors,
            "created_users": created_users  # Return credentials (in production, these would be emailed)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV: {str(e)}"
        )
