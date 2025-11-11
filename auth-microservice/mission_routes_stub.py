"""
Mission Routes Stub
Temporary stub endpoints for missions until full implementation
"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions

router = APIRouter()


@router.get("/")
async def get_missions(
    status: str = None,
    company_id: str = None,
    commercial_id: str = None,
    published_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.MISSIONS_READ))
):
    """
    Get missions list (stub endpoint)
    Returns empty list until missions are implemented
    """
    # TODO: Implement full missions logic
    return []


@router.get("/{mission_id}")
async def get_mission(
    mission_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.MISSIONS_READ))
):
    """
    Get single mission (stub endpoint)
    """
    # TODO: Implement full mission detail logic
    return {
        "id": mission_id,
        "status": "draft",
        "title": "Mission en cours d'implémentation",
        "description": "Cette fonctionnalité sera bientôt disponible"
    }


@router.get("/{mission_id}/stats")
async def get_mission_stats(
    mission_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.MISSIONS_READ))
):
    """
    Get mission statistics (stub endpoint)
    """
    # TODO: Implement full mission stats logic
    return {
        "total_applications": 0,
        "pending_applications": 0,
        "accepted_applications": 0,
        "rejected_applications": 0
    }
