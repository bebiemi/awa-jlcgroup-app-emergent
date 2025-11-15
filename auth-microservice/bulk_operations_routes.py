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
                # Soft delete (mark as deleted)
                result = await db.users.update_one(
                    {"id": user_id},
                    {
                        "$set": {
                            "status": "deleted",
                            "deleted_at": datetime.now(timezone.utc),
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
@require_permission("users.read")
async def export_users_csv(
    request: BulkOperationRequest,
    current_user: User = Depends(get_current_user),
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
