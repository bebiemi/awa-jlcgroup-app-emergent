"""
Routes API pour la gestion des expirations de profils
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.iam.expiration_service import ExpirationService
from awana_auth.iam.models import ExpirationCheck

router = APIRouter(prefix="/iam/expirations", tags=["IAM Expirations"])


class ExpirationCheckResponse(BaseModel):
    """Réponse de vérification d'expiration"""
    user_id: str
    username: str
    email: str
    expired_count: int
    expiring_soon_count: int
    expired_profiles: List[Dict[str, Any]]
    expiring_soon: List[Dict[str, Any]]
    downgrade_to_profile_id: str


class ExpirationStats(BaseModel):
    """Statistiques d'expiration"""
    total_users_checked: int
    users_with_expiring: int
    total_expired: int
    total_expiring_soon: int
    last_check: datetime


@router.get("/check/me", response_model=ExpirationCheckResponse)
async def check_my_expirations(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Vérifie les profils expirés et expirant bientôt pour l'utilisateur connecté
    """
    service = ExpirationService(db)
    
    try:
        check = await service.check_user_expirations(current_user.id)
        
        return ExpirationCheckResponse(
            user_id=check.user_id,
            username=check.username,
            email=check.email,
            expired_count=len(check.expired_profiles),
            expiring_soon_count=len(check.expiring_soon),
            expired_profiles=[p.dict() for p in check.expired_profiles],
            expiring_soon=[p.dict() for p in check.expiring_soon],
            downgrade_to_profile_id=check.downgrade_to_profile_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur vérification expirations: {str(e)}"
        )


@router.get("/check/{user_id}", response_model=ExpirationCheckResponse)
async def check_user_expirations(
    user_id: str,
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Vérifie les profils expirés et expirant bientôt pour un utilisateur spécifique
    Requiert: users.manage
    """
    service = ExpirationService(db)
    
    try:
        check = await service.check_user_expirations(user_id)
        
        return ExpirationCheckResponse(
            user_id=check.user_id,
            username=check.username,
            email=check.email,
            expired_count=len(check.expired_profiles),
            expiring_soon_count=len(check.expiring_soon),
            expired_profiles=[p.dict() for p in check.expired_profiles],
            expiring_soon=[p.dict() for p in check.expiring_soon],
            downgrade_to_profile_id=check.downgrade_to_profile_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur vérification expirations: {str(e)}"
        )


@router.get("/check/all", response_model=List[ExpirationCheckResponse])
async def check_all_expirations(
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Vérifie les expirations pour tous les utilisateurs
    Requiert: users.manage
    """
    service = ExpirationService(db)
    
    try:
        checks = await service.check_all_expirations()
        
        return [
            ExpirationCheckResponse(
                user_id=check.user_id,
                username=check.username,
                email=check.email,
                expired_count=len(check.expired_profiles),
                expiring_soon_count=len(check.expiring_soon),
                expired_profiles=[p.dict() for p in check.expired_profiles],
                expiring_soon=[p.dict() for p in check.expiring_soon],
                downgrade_to_profile_id=check.downgrade_to_profile_id
            )
            for check in checks
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur vérification globale: {str(e)}"
        )


@router.post("/process")
async def process_expirations(
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Force le traitement des expirations (downgrade automatique)
    Requiert: users.manage
    
    Normalement exécuté automatiquement par cron, mais peut être déclenché manuellement
    """
    service = ExpirationService(db)
    
    try:
        result = await service.downgrade_all_expired_profiles()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur traitement expirations: {str(e)}"
        )


@router.post("/notify")
async def send_expiration_notifications(
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Envoie les notifications d'expiration imminente (< 3 jours)
    Requiert: users.manage
    
    Normalement exécuté automatiquement par cron quotidien
    """
    service = ExpirationService(db)
    
    try:
        result = await service.notify_expiring_soon()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur envoi notifications: {str(e)}"
        )


@router.get("/stats", response_model=ExpirationStats)
async def get_expiration_stats(
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Statistiques globales sur les expirations
    Requiert: users.manage
    """
    service = ExpirationService(db)
    
    try:
        checks = await service.check_all_expirations()
        
        total_expired = sum(len(check.expired_profiles) for check in checks)
        total_expiring_soon = sum(len(check.expiring_soon) for check in checks)
        
        return ExpirationStats(
            total_users_checked=len(checks),
            users_with_expiring=len(checks),
            total_expired=total_expired,
            total_expiring_soon=total_expiring_soon,
            last_check=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur récupération statistiques: {str(e)}"
        )


@router.post("/downgrade/{user_id}/{profile_id}")
async def manual_downgrade_profile(
    user_id: str,
    profile_id: str,
    current_user: User = Depends(require_permission("users.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Downgrade manuel d'un profil temporaire
    Requiert: users.manage
    """
    service = ExpirationService(db)
    
    try:
        # Récupérer le profil temporaire
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        temp_profiles = user.get("temporary_profiles", [])
        temp_profile_data = next((tp for tp in temp_profiles if tp.get("profile_id") == profile_id), None)
        
        if not temp_profile_data:
            raise HTTPException(status_code=404, detail="Profil temporaire non trouvé")
        
        from awana_auth.iam.models import TemporaryProfile
        temp_profile = TemporaryProfile(**temp_profile_data)
        
        success = await service.downgrade_expired_profile(
            user_id,
            temp_profile,
            reason=f"Downgrade manuel par {current_user.username}"
        )
        
        if success:
            return {
                "success": True,
                "message": f"Profil {profile_id} downgradé pour utilisateur {user_id}",
                "user_id": user_id,
                "profile_id": profile_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec du downgrade"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur downgrade manuel: {str(e)}"
        )
