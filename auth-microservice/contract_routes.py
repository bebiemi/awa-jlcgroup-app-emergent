"""
Routes pour la gestion des contrats
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from awana_auth.core.dependencies import get_current_user
from awana_auth.core.models import User
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

# Connexion dédiée à jlc_db (base de données métier)
_jlc_db_client = None
_jlc_db = None

def get_jlc_database() -> AsyncIOMotorDatabase:
    """
    Récupérer la base de données jlc_db (données métier: missions, candidatures)
    Séparée de auth_db qui contient les utilisateurs
    """
    global _jlc_db_client, _jlc_db
    
    if _jlc_db is None:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        _jlc_db_client = AsyncIOMotorClient(mongo_url)
        _jlc_db = _jlc_db_client["jlc_db"]
        logger.info("📊 Connected to jlc_db for contract operations")
    
    return _jlc_db


@router.get("/me")
async def get_my_contracts(
    status_filter: Optional[str] = Query(None, description="Filtrer par statut (active, completed, cancelled)"),
    include_ended: bool = Query(False, description="Inclure les contrats terminés"),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_jlc_database)
):
    """
    Récupérer les contrats de l'utilisateur connecté (intérimaire)
    Retourne les contrats associés aux applications acceptées
    """
    # Vérifier que l'utilisateur est un intérimaire
    if "interim" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux intérimaires"
        )
    
    # Récupérer le profil de l'utilisateur
    profile = await db.interim_profiles.find_one({"user_id": current_user.id})
    
    if not profile:
        return {
            "contracts": [],
            "active_contract": None,
            "upcoming_end": None
        }
    
    # Construire le filtre pour les applications
    app_query = {
        "interim_id": current_user.id,
        "status": {"$in": ["contract_signed", "contract_pending"]}
    }
    
    # Récupérer les applications avec contrat
    applications = await db.mission_applications.find(app_query).to_list(length=None)
    
    contracts = []
    active_contract = None
    upcoming_end = None
    
    now = datetime.now(timezone.utc)
    
    for app in applications:
        # Récupérer la mission associée
        mission = await db.missions.find_one({"id": app["mission_id"]})
        
        if not mission:
            continue
        
        contract_data = {
            "id": app["id"],
            "mission_id": app["mission_id"],
            "mission_title": mission.get("title", "Mission"),
            "mission_description": mission.get("description", ""),
            "company_name": mission.get("company_name", ""),
            "location": mission.get("location", ""),
            "start_date": mission.get("start_date"),
            "end_date": mission.get("end_date"),
            "contract_type": mission.get("contract_type", ""),
            "status": app["status"],
            "application_date": app.get("created_at"),
            "contract_signed_date": app.get("updated_at") if app["status"] == "contract_signed" else None,
            "salary_range": mission.get("salary_range", ""),
            "work_schedule": mission.get("work_schedule", "")
        }
        
        # Déterminer si le contrat est actif
        is_active = False
        is_ended = False
        
        if contract_data["status"] == "contract_signed":
            if contract_data["start_date"] and contract_data["end_date"]:
                try:
                    start = datetime.fromisoformat(contract_data["start_date"].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(contract_data["end_date"].replace('Z', '+00:00'))
                    
                    if start <= now <= end:
                        is_active = True
                        contract_data["is_active"] = True
                        
                        # Calculer les jours restants
                        days_remaining = (end - now).days
                        contract_data["days_remaining"] = days_remaining
                        
                        # Vérifier si alerte J-14
                        if days_remaining <= 14 and days_remaining > 0:
                            contract_data["alert_upcoming_end"] = True
                            if not upcoming_end or days_remaining < upcoming_end["days_remaining"]:
                                upcoming_end = {
                                    "contract_id": contract_data["id"],
                                    "mission_title": contract_data["mission_title"],
                                    "end_date": contract_data["end_date"],
                                    "days_remaining": days_remaining
                                }
                        
                        if not active_contract:
                            active_contract = contract_data
                    elif now > end:
                        is_ended = True
                        contract_data["is_ended"] = True
                except:
                    pass
        
        # Filtrer selon les paramètres
        if status_filter:
            if status_filter == "active" and not is_active:
                continue
            if status_filter == "completed" and not is_ended:
                continue
        
        if is_ended and not include_ended:
            continue
        
        contracts.append(contract_data)
    
    # Trier par date de début (plus récent en premier)
    contracts.sort(key=lambda x: x.get("start_date", ""), reverse=True)
    
    return {
        "contracts": contracts,
        "total": len(contracts),
        "active_contract": active_contract,
        "upcoming_end": upcoming_end,
        "can_apply": active_contract is None or (
            upcoming_end and upcoming_end["days_remaining"] <= 5
        )
    }


@router.get("/active")
async def get_active_contract(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_jlc_database)
):
    """
    Récupérer le contrat actif de l'utilisateur (s'il existe)
    """
    result = await get_my_contracts(
        status_filter="active",
        include_ended=False,
        current_user=current_user,
        db=db
    )
    
    return {
        "active_contract": result["active_contract"],
        "upcoming_end": result["upcoming_end"],
        "can_apply": result["can_apply"]
    }


@router.get("/{contract_id}")
async def get_contract_details(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_jlc_database)
):
    """
    Récupérer les détails d'un contrat spécifique
    """
    # Récupérer l'application
    application = await db.mission_applications.find_one({
        "id": contract_id,
        "interim_id": current_user.id
    })
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrat non trouvé"
        )
    
    # Récupérer la mission
    mission = await db.missions.find_one({"id": application["mission_id"]})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission associée non trouvée"
        )
    
    return {
        "contract": {
            "id": application["id"],
            "mission_id": application["mission_id"],
            "mission_title": mission.get("title"),
            "mission_description": mission.get("description"),
            "company_name": mission.get("company_name"),
            "location": mission.get("location"),
            "start_date": mission.get("start_date"),
            "end_date": mission.get("end_date"),
            "contract_type": mission.get("contract_type"),
            "status": application["status"],
            "salary_range": mission.get("salary_range"),
            "work_schedule": mission.get("work_schedule"),
            "requirements": mission.get("requirements", []),
            "benefits": mission.get("benefits", [])
        }
    }
