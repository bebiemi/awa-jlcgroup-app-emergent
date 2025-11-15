"""
App Configuration Routes
Dynamic configuration endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Any, Dict, Optional
from pydantic import BaseModel
from awana_auth.core.dependencies import get_database
from awana_auth.services.config_service import ConfigService
from awana_auth.core.dependencies import get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/config/app", tags=["App Configuration"])


class ConfigUpdate(BaseModel):
    """Configuration update model"""
    value: Any
    description: Optional[str] = None


@router.get("")
async def get_config(
    key: Optional[str] = Query(None, description="Configuration key"),
    category: Optional[str] = Query(None, description="Configuration category"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get configuration(s)
    
    - If key is provided: return single config
    - If category is provided: return all configs for category
    - If neither: return all configs
    """
    service = ConfigService(db)
    
    if key:
        config = await service.get_config(key)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    
    if category:
        configs = await service.get_configs_by_category(category)
        return {"configs": configs}
    
    # Return all configs
    all_configs = await db.app_config.find({}, {"_id": 0}).to_list(length=1000)
    return {"configs": all_configs}


@router.get("/value")
async def get_config_value(
    key: str = Query(..., description="Configuration key"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get configuration value directly (without metadata)
    
    Example: /api/config/app/value?key=profiles.badge_new_user
    Returns: { "value": { ... } }
    """
    service = ConfigService(db)
    value = await service.get_config_value(key)
    
    if value is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"value": value}


@router.post("")
async def create_config(
    key: str,
    value: Any,
    category: str,
    description: str = "",
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create or update configuration
    
    Requires: config.manage permission
    """
    # Check permission
    user_permissions = current_user.get("permissions", [])
    if "config.manage" not in user_permissions and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    service = ConfigService(db)
    success = await service.set_config(
        key=key,
        value=value,
        category=category,
        description=description,
        updated_by=current_user.get("id", "unknown")
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save configuration")
    
    return {"message": "Configuration saved", "key": key}


@router.patch("/{key}")
async def update_config(
    key: str,
    update: ConfigUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update configuration value
    
    Requires: config.manage permission
    """
    # Check permission
    user_permissions = current_user.get("permissions", [])
    if "config.manage" not in user_permissions and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    service = ConfigService(db)
    
    # Get existing config
    existing = await service.get_config(key)
    if not existing:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Update
    success = await service.set_config(
        key=key,
        value=update.value,
        category=existing.get("category", "general"),
        description=update.description or existing.get("description", ""),
        updated_by=current_user.get("id", "unknown")
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update configuration")
    
    return {"message": "Configuration updated", "key": key}


@router.delete("/{key}")
async def delete_config(
    key: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete configuration
    
    Requires: config.manage permission
    """
    # Check permission
    user_permissions = current_user.get("permissions", [])
    if "config.manage" not in user_permissions and "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    service = ConfigService(db)
    success = await service.delete_config(key)
    
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"message": "Configuration deleted", "key": key}


@router.get("/categories")
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get list of all configuration categories
    """
    categories = await db.app_config.distinct("category")
    return {"categories": categories}
