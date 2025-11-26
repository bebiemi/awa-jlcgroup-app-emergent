"""
Location Management Routes
CRUD operations for hierarchical location management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone

from awana_auth.core.location_models import (
    Location, LocationCreate, LocationUpdate, LocationTree, LocationType
)
from awana_auth.core.models import User
from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from message_catalog import LOCATION_MESSAGES

location_router = APIRouter(prefix="/locations", tags=["Locations"])


@location_router.get("", response_model=List[Location])
async def get_locations(
    type: Optional[LocationType] = None,
    parent_id: Optional[str] = None,
    is_visible: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get locations with filters (public endpoint)"""
    query = {}
    
    if type:
        query["type"] = type.value
    
    if parent_id is not None:
        query["parent_id"] = parent_id
    
    if is_visible is not None:
        query["is_visible"] = is_visible
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    locations = await db.locations.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(length=None)
    return [Location(**loc) for loc in locations]


@location_router.get("/tree", response_model=List[LocationTree])
async def get_location_tree(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get complete location hierarchy as tree (public endpoint)"""
    # Get all visible locations
    all_locations = await db.locations.find({"is_visible": True}, {"_id": 0}).to_list(length=None)
    
    # Build tree structure
    location_map = {loc["id"]: LocationTree(**loc) for loc in all_locations}
    
    # Organize by parent
    roots = []
    for loc_id, loc in location_map.items():
        if loc.parent_id and loc.parent_id in location_map:
            location_map[loc.parent_id].children.append(loc)
        else:
            roots.append(loc)
    
    return roots


@location_router.get("/{location_id}", response_model=Location)
async def get_location(
    location_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific location by ID"""
    location = await db.locations.find_one({"id": location_id}, {"_id": 0})
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LOCATION_MESSAGES["not_found"]
        )
    return Location(**location)


@location_router.post("", response_model=Location)
async def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(require_permission("locations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new location (admin only)"""
    # Validate parent exists if provided
    if location_data.parent_id:
        parent = await db.locations.find_one({"id": location_data.parent_id})
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=LOCATION_MESSAGES["parent_not_found"]
            )
    
    # Check for duplicate name at same level
    duplicate_query = {
        "name": location_data.name,
        "type": location_data.type.value,
        "parent_id": location_data.parent_id
    }
    existing = await db.locations.find_one(duplicate_query)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=LOCATION_MESSAGES["duplicate"].format(name=location_data.name)
        )
    
    # Determine if required based on type
    is_required = location_data.type in [
        LocationType.COUNTRY,
        LocationType.CITY,
        LocationType.NEIGHBORHOOD
    ]
    
    location = Location(
        **location_data.dict(),
        is_required=is_required,
        created_by=current_user.id
    )
    
    await db.locations.insert_one(location.dict())
    return location


@location_router.put("/{location_id}", response_model=Location)
async def update_location(
    location_id: str,
    location_data: LocationUpdate,
    current_user: User = Depends(require_permission("locations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update location (admin only)"""
    existing = await db.locations.find_one({"id": location_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LOCATION_MESSAGES["not_found"]
        )
    
    # Only update provided fields
    update_data = {
        k: v for k, v in location_data.dict(exclude_unset=True).items()
        if v is not None
    }
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.locations.update_one(
            {"id": location_id},
            {"$set": update_data}
        )
    
    updated = await db.locations.find_one({"id": location_id}, {"_id": 0})
    return Location(**updated)


@location_router.delete("/{location_id}")
async def delete_location(
    location_id: str,
    current_user: User = Depends(require_permission("locations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete location (admin only)"""
    # Check if location has children
    children = await db.locations.count_documents({"parent_id": location_id})
    if children > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=LOCATION_MESSAGES["children_block_delete"].format(children=children)
        )
    
    result = await db.locations.delete_one({"id": location_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LOCATION_MESSAGES["not_found"]
        )
    
    return {"success": True, "message": "Location deleted successfully"}


@location_router.patch("/{location_id}/visibility")
async def toggle_location_visibility(
    location_id: str,
    is_visible: bool,
    current_user: User = Depends(require_permission("locations.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Toggle location visibility (admin only)"""
    result = await db.locations.update_one(
        {"id": location_id},
        {"$set": {
            "is_visible": is_visible,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LOCATION_MESSAGES["not_found"]
        )
    
    return {
        "success": True,
        "message": f"Location visibility set to {is_visible}"
    }


@location_router.get("/children/{parent_id}", response_model=List[Location])
async def get_location_children(
    parent_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all children of a location"""
    children = await db.locations.find(
        {"parent_id": parent_id, "is_visible": True},
        {"_id": 0}
    ).to_list(length=None)
    
    return [Location(**child) for child in children]
