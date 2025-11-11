"""
Mission Management Routes
Gestion complète du processus de missions d'intérim
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from awana_auth.core.dependencies import get_database, get_configuration
from awana_auth.core.config_manager import ConfigManager
from awana_auth.core.models import User
from awana_auth.core.mission_models import (
    Mission, MissionCreate, MissionUpdate, MissionStatus,
    Application, ApplicationCreate, ApplicationUpdate, ApplicationStatus,
    Document, DocumentUpload, DocumentType,
    MedicalStatus, ContractStatus
)
from awana_auth.core.dependencies import get_current_user as get_user_dep
from awana_auth.dependencies.permission_dependencies import require_permission, require_any_permission
from awana_auth.services.permission_checker import PermissionChecker
from awana_auth.utils.config_helpers import cfg

router = APIRouter(prefix="/api/missions", tags=["missions"])


# ==================== VALIDATION HELPERS ====================

async def validate_status(
    db: AsyncIOMotorDatabase, 
    category: str, 
    status_code: str
) -> bool:
    """Valider qu'un statut existe et est actif dans les référentiels"""
    ref = await db.system_references.find_one({
        "category": category,
        "code": status_code,
        "is_active": True
    })
    return ref is not None


async def get_status_metadata(
    db: AsyncIOMotorDatabase,
    category: str,
    status_code: str
) -> Dict[str, Any]:
    """Récupérer les métadonnées d'un statut"""
    ref = await db.system_references.find_one({
        "category": category,
        "code": status_code
    })
    return ref.get("metadata", {}) if ref else {}


async def get_valid_statuses(db: AsyncIOMotorDatabase, category: str) -> List[str]:
    """Récupérer la liste des codes de statuts valides"""
    references = await db.system_references.find({
        "category": category,
        "is_active": True
    }).to_list(length=None)
    return [ref["code"] for ref in references]


async def check_application_restrictions(
    db: AsyncIOMotorDatabase,
    config: ConfigManager,
    candidate_id: str,
    mission_id: str
) -> None:
    """
    Vérifier les restrictions de candidature selon la configuration
    
    Raises:
        HTTPException: Si une restriction n'est pas respectée
    """
    # Vérifier le nombre max de candidatures par candidat
    max_applications = config.get("workflows.application.restrictions.max_applications_per_candidate", default=10)
    candidate_apps_count = await db.applications.count_documents({"candidate_id": candidate_id})
    
    if candidate_apps_count >= max_applications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vous avez atteint la limite de {max_applications} candidatures"
        )
    
    # Vérifier le délai minimum entre candidatures
    min_days_between = config.get("workflows.application.restrictions.min_days_between_applications", default=1)
    if min_days_between > 0:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=min_days_between)
        recent_app = await db.applications.find_one({
            "candidate_id": candidate_id,
            "created_at": {"$gte": cutoff_date}
        })
        
        if recent_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Veuillez attendre {min_days_between} jour(s) entre deux candidatures"
            )
    
    # Vérifier si déjà candidaté à cette mission
    existing_app = await db.applications.find_one({
        "candidate_id": candidate_id,
        "mission_id": mission_id
    })
    
    if existing_app:
        # Vérifier si peut re-candidater après rejet
        if existing_app["status"] in ["rejected", "rejected_initial"]:
            allow_reapply_days = config.get(
                "workflows.application.restrictions.allow_reapplication_after_rejection_days",
                default=30
            )
            rejection_date = existing_app.get("updated_at")
            if isinstance(rejection_date, str):
                rejection_date = datetime.fromisoformat(rejection_date)
            
            if datetime.now(timezone.utc) - rejection_date < timedelta(days=allow_reapply_days):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Vous pourrez re-candidater à cette mission après {allow_reapply_days} jours"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous avez déjà candidaté à cette mission"
            )


# Custom dependency to get user as dict
async def get_current_user(user: User = Depends(get_user_dep)) -> dict:
    """Get current user as dict"""
    return {
        "sub": user.id,
        "email": user.email,
        "roles": user.roles or [],
        "full_name": user.full_name
    }


# Alias for db
get_db = get_database


# ==================== MISSION ROUTES ====================

@router.post("", response_model=Mission, status_code=status.HTTP_201_CREATED)
async def create_mission(
    mission: MissionCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Créer une nouvelle mission (Étape 1)
    Accessible par: Entreprises, Admin, Commerciaux
    """
    # IAM Permission Check
    checker = PermissionChecker(db)
    has_permission = await checker.user_has_any_permission(
        current_user.get("id"),
        ["missions.create", "missions.manage"]
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de créer une mission"
        )
    
    # Valider le type de contrat contre les référentiels
    if not await validate_status(db, "contract_types", mission.contract_type):
        valid_types = await get_valid_statuses(db, "contract_types")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de contrat invalide '{mission.contract_type}'. Valeurs autorisées: {valid_types}"
        )
    
    mission_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    mission_data = {
        "id": mission_id,
        **mission.dict(),
        "status": MissionStatus.DRAFT,
        "applications_count": 0,
        "shortlisted_count": 0,
        "selected_count": 0,
        "hired_count": 0,
        "created_at": now,
        "updated_at": now
    }
    
    await db.missions.insert_one(mission_data)
    
    return Mission(**mission_data)


@router.get("", response_model=List[Mission])
async def get_missions(
    status: Optional[MissionStatus] = None,
    company_id: Optional[str] = None,
    commercial_id: Optional[str] = None,
    published_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Récupérer la liste des missions
    Filtres selon le rôle:
    - Intérimaires: Seulement missions publiées
    - Entreprises: Leurs missions uniquement
    - Admin/Commercial: Toutes les missions
    """
    query = {}
    user_id = current_user.get("sub")
    
    # IAM: Check permissions instead of roles
    checker = PermissionChecker(db)
    can_manage_all = await checker.user_has_any_permission(
        current_user.get("id"),
        ["missions.manage", "missions.read"]
    )
    can_create = await checker.user_has_permission(
        current_user.get("id"),
        "missions.create"
    )
    can_browse = await checker.user_has_permission(
        current_user.get("id"),
        "missions.browse"
    )
    
    # Filtrer selon les permissions
    if can_browse and not can_manage_all and not can_create:
        # Interim users (missions.browse) - only published missions
        query["status"] = MissionStatus.PUBLISHED
    elif can_create and not can_manage_all:
        # Company users (missions.create) - only their missions
        query["company_id"] = user_id
    
    # Appliquer les filtres supplémentaires
    if status:
        query["status"] = status
    if company_id and can_manage_all:
        query["company_id"] = company_id
    if commercial_id:
        query["commercial_id"] = commercial_id
    if published_only:
        query["status"] = MissionStatus.PUBLISHED
    
    missions = await db.missions.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Remove MongoDB _id before creating Pydantic models
    for mission in missions:
        mission.pop('_id', None)
    
    return [Mission(**mission) for mission in missions]


@router.get("/{mission_id}", response_model=Mission)
async def get_mission(
    mission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Récupérer une mission spécifique"""
    mission = await db.missions.find_one({"id": mission_id})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # IAM: Check permissions
    checker = PermissionChecker(db)
    user_id = current_user.get("sub")
    
    can_manage_all = await checker.user_has_any_permission(
        current_user.get("id"),
        ["missions.manage", "missions.read"]
    )
    can_browse = await checker.user_has_permission(
        current_user.get("id"),
        "missions.browse"
    )
    can_create = await checker.user_has_permission(
        current_user.get("id"),
        "missions.create"
    )
    
    # Interim users (missions.browse) can only see published missions
    if can_browse and not can_manage_all and not can_create:
        if mission["status"] != MissionStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Mission non accessible"
            )
    
    # Company users (missions.create) can only see their missions
    if can_create and not can_manage_all and mission["company_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez voir que vos missions"
        )
    
    return Mission(**mission)


@router.put("/{mission_id}", response_model=Mission)
async def update_mission(
    mission_id: str,
    mission_update: MissionUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Mettre à jour une mission
    Accessible par: Créateur, Admin, Commercial assigné
    """
    mission = await db.missions.find_one({"id": mission_id})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # IAM: Check permissions
    checker = PermissionChecker(db)
    user_id = current_user.get("sub")
    
    can_manage = await checker.user_has_permission(
        current_user.get("id"),
        "missions.manage"
    )
    can_edit = await checker.user_has_permission(
        current_user.get("id"),
        "missions.edit"
    )
    
    can_update = (
        can_manage or
        can_edit or
        mission["created_by"] == user_id or
        mission.get("commercial_id") == user_id
    )
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de modifier cette mission"
        )
    
    # Mettre à jour
    update_data = {k: v for k, v in mission_update.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Tracking des changements de statut
    if "status" in update_data:
        if update_data["status"] == MissionStatus.PUBLISHED and not mission.get("published_at"):
            update_data["published_at"] = datetime.now(timezone.utc)
        elif update_data["status"] in [MissionStatus.COMPLETED, MissionStatus.CANCELLED]:
            update_data["closed_at"] = datetime.now(timezone.utc)
    
    await db.missions.update_one(
        {"id": mission_id},
        {"$set": update_data}
    )
    
    updated_mission = await db.missions.find_one({"id": mission_id})
    return Mission(**updated_mission)


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mission(
    mission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Supprimer une mission (soft delete en changeant le statut)
    Accessible par: Créateur, Admin
    """
    mission = await db.missions.find_one({"id": mission_id})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # IAM: Check permissions
    checker = PermissionChecker(db)
    user_id = current_user.get("sub")
    
    can_manage = await checker.user_has_permission(
        current_user.get("id"),
        "missions.manage"
    )
    can_delete_perm = await checker.user_has_permission(
        current_user.get("id"),
        "missions.delete"
    )
    
    can_delete = (
        can_manage or
        can_delete_perm or
        mission["created_by"] == user_id
    )
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de supprimer cette mission"
        )
    
    # Soft delete
    await db.missions.update_one(
        {"id": mission_id},
        {"$set": {"status": MissionStatus.CANCELLED, "closed_at": datetime.now(timezone.utc)}}
    )


@router.post("/{mission_id}/publish", response_model=Mission)
async def publish_mission(
    mission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Publier une mission (Étape 3)
    Rend la mission visible aux intérimaires
    """
    mission = await db.missions.find_one({"id": mission_id})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # IAM: Check permissions
    checker = PermissionChecker(db)
    
    can_publish = await checker.user_has_any_permission(
        current_user.get("id"),
        ["missions.publish", "missions.manage"]
    )
    
    if not can_publish:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas la permission de publier des missions"
        )
    
    # Publier
    await db.missions.update_one(
        {"id": mission_id},
        {
            "$set": {
                "status": MissionStatus.PUBLISHED,
                "published_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    updated_mission = await db.missions.find_one({"id": mission_id})
    return Mission(**updated_mission)


# ==================== APPLICATION ROUTES ====================

@router.post("/{mission_id}/apply", response_model=Application, status_code=status.HTTP_201_CREATED)
async def apply_to_mission(
    mission_id: str,
    application: ApplicationCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Postuler à une mission (Étape 4)
    Accessible par: Intérimaires
    """
    # Vérifier que c'est un intérimaire
    user_roles = current_user.get("roles", [])
    if cfg.get_interim_role() not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les intérimaires peuvent postuler"
        )
    
    # Vérifier que la mission existe et est publiée
    mission = await db.missions.find_one({"id": mission_id})
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    if mission["status"] != MissionStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette mission n'accepte plus de candidatures"
        )
    
    # Vérifier si l'utilisateur a déjà postulé
    existing = await db.applications.find_one({
        "mission_id": mission_id,
        "user_id": current_user["sub"]
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà postulé à cette mission"
        )
    
    # Créer la candidature
    application_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    application_data = {
        "id": application_id,
        **application.dict(),
        "status": ApplicationStatus.SUBMITTED,
        "medical_status": MedicalStatus.NOT_REQUIRED if not mission.get("requires_medical_check") else MedicalStatus.PENDING,
        "contract_status": ContractStatus.NOT_GENERATED,
        "created_at": now,
        "updated_at": now
    }
    
    await db.applications.insert_one(application_data)
    
    # Mettre à jour le compteur de la mission
    await db.missions.update_one(
        {"id": mission_id},
        {"$inc": {"applications_count": 1}}
    )
    
    return Application(**application_data)


@router.get("/{mission_id}/applications", response_model=List[Application])
async def get_mission_applications(
    mission_id: str,
    status: Optional[ApplicationStatus] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Récupérer les candidatures d'une mission (Étape 5-6)
    Accessible par: Admin, Commercial, Entreprise propriétaire
    """
    # Vérifier que la mission existe
    mission = await db.missions.find_one({"id": mission_id})
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # IAM: Check permissions
    checker = PermissionChecker(db)
    user_id = current_user.get("sub")
    
    can_manage = await checker.user_has_any_permission(
        current_user.get("id"),
        ["applications.manage", "applications.review"]
    )
    can_create = await checker.user_has_permission(
        current_user.get("id"),
        "missions.create"
    )
    
    can_view = (
        can_manage or
        (mission["company_id"] == user_id and can_create)
    )
    
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès aux candidatures"
        )
    
    # Récupérer les candidatures
    query = {"mission_id": mission_id}
    if status:
        query["status"] = status
    
    applications = await db.applications.find(query).to_list(length=None)
    
    return [Application(**app) for app in applications]


@router.get("/applications/my-applications", response_model=List[Application])
async def get_my_applications(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Récupérer mes candidatures (pour intérimaire)
    """
    user_id = current_user.get("sub")
    
    applications = await db.applications.find({"user_id": user_id}).to_list(length=None)
    
    return [Application(**app) for app in applications]


@router.put("/applications/{application_id}", response_model=Application)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Mettre à jour une candidature (workflow)
    Utilisé pour: tri, sélection, entretien, etc.
    """
    application = await db.applications.find_one({"id": application_id})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée"
        )
    
    # Vérifier permissions
    user_roles = current_user.get("roles", [])
    can_update = cfg.get_admin_role() in user_roles or cfg.get_super_admin_role() in user_roles or cfg.get_commercial_role() in user_roles
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission insuffisante"
        )
    
    # Mettre à jour
    update_data = {k: v for k, v in application_update.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Valider le nouveau statut si présent
    if "status" in update_data:
        new_status = update_data["status"]
        
        # Valider que le statut existe
        if not await validate_status(db, "application_statuses", new_status):
            valid_statuses = await get_valid_statuses(db, "application_statuses")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statut invalide '{new_status}'. Valeurs autorisées: {valid_statuses}"
            )
        
        # Valider les transitions autorisées
        current_status = application.get("status")
        current_metadata = await get_status_metadata(db, "application_statuses", current_status)
        allowed_transitions = current_metadata.get("next_possible_statuses", [])
        
        if allowed_transitions and new_status not in allowed_transitions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transition non autorisée de '{current_status}' vers '{new_status}'. Transitions possibles: {allowed_transitions}"
            )
    
    # Tracking automatique des dates
    if "status" in update_data:
        if update_data["status"] == ApplicationStatus.SENT_TO_CLIENT:
            update_data["sent_to_client_at"] = datetime.now(timezone.utc)
        elif update_data["status"] == ApplicationStatus.INTERVIEW_COMPLETED:
            update_data["interview_completed_at"] = datetime.now(timezone.utc)
        elif update_data["status"] in [ApplicationStatus.SELECTED_BY_CLIENT, ApplicationStatus.REJECTED_BY_CLIENT]:
            update_data["client_response_at"] = datetime.now(timezone.utc)
    
    await db.applications.update_one(
        {"id": application_id},
        {"$set": update_data}
    )
    
    updated_app = await db.applications.find_one({"id": application_id})
    return Application(**updated_app)


@router.post("/applications/{application_id}/shortlist", response_model=Application)
async def shortlist_application(
    application_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Présélectionner une candidature (Étape 6)"""
    application = await db.applications.find_one({"id": application_id})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée"
        )
    
    await db.applications.update_one(
        {"id": application_id},
        {
            "$set": {
                "status": ApplicationStatus.SHORTLISTED,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Incrémenter le compteur de la mission
    await db.missions.update_one(
        {"id": application["mission_id"]},
        {"$inc": {"shortlisted_count": 1}}
    )
    
    updated_app = await db.applications.find_one({"id": application_id})
    return Application(**updated_app)


@router.post("/applications/{application_id}/upload-medical", response_model=Application)
async def upload_medical_document(
    application_id: str,
    file_url: str = Form(...),
    medical_status: MedicalStatus = Form(...),
    notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Upload du document de visite médicale (Étape 14)
    Accessible par: Intérimaire concerné
    """
    application = await db.applications.find_one({"id": application_id})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée"
        )
    
    # Vérifier que c'est bien l'intérimaire concerné
    if application["user_id"] != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres candidatures"
        )
    
    # Mettre à jour
    await db.applications.update_one(
        {"id": application_id},
        {
            "$set": {
                "medical_status": medical_status,
                "medical_document_url": file_url,
                "medical_notes": notes,
                "medical_completed_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    updated_app = await db.applications.find_one({"id": application_id})
    return Application(**updated_app)


# ==================== STATISTIQUES ====================

@router.get("/{mission_id}/stats")
async def get_mission_stats(
    mission_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Statistiques d'une mission"""
    mission = await db.missions.find_one({"id": mission_id})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # Statistiques des candidatures
    total_applications = await db.applications.count_documents({"mission_id": mission_id})
    shortlisted = await db.applications.count_documents({
        "mission_id": mission_id,
        "status": ApplicationStatus.SHORTLISTED
    })
    selected_by_client = await db.applications.count_documents({
        "mission_id": mission_id,
        "status": ApplicationStatus.SELECTED_BY_CLIENT
    })
    hired = await db.applications.count_documents({
        "mission_id": mission_id,
        "status": ApplicationStatus.HIRED
    })
    
    return {
        "mission_id": mission_id,
        "total_applications": total_applications,
        "shortlisted": shortlisted,
        "selected_by_client": selected_by_client,
        "hired": hired,
        "conversion_rate": (hired / total_applications * 100) if total_applications > 0 else 0
    }
