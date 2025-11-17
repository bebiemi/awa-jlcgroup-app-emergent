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
        "id": user.id,
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
    
    # Remove MongoDB _id before creating Pydantic model
    mission_data.pop('_id', None)
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



# ==================== MISSION MATCHING ENDPOINTS ====================
# Ces routes doivent être AVANT /{mission_id} pour éviter les conflits de routing

@router.get("/recommended", response_model=List[Dict[str, Any]])
async def get_recommended_missions(
    limit: int = 10,
    min_score: float = 50.0,
    current_user: User = Depends(get_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère les missions recommandées pour l'utilisateur connecté
    basées sur le score de matching avec son profil
    
    Args:
        limit: Nombre maximum de missions à retourner
        min_score: Score minimum requis (0-100)
    
    Returns:
        Liste des missions avec leur score de matching, triées par score décroissant
    """
    from awana_auth.services.mission_matching_service import MissionMatchingService
    
    # Récupérer le profil de l'utilisateur
    # Essayer d'abord interim_profiles, puis candidat_profiles
    user_profile = await db.interim_profiles.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not user_profile:
        user_profile = await db.candidat_profiles.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not user_profile:
        # Profil non trouvé, retourner liste vide
        return []
    
    # Récupérer les missions publiées et actives
    missions = await db.missions.find({
        "status": {"$in": [
            MissionStatus.PUBLISHED,
            MissionStatus.ACCEPTING_APPLICATIONS
        ]}
    }, {"_id": 0}).to_list(length=None)
    
    if not missions:
        return []
    
    # Récupérer les candidatures existantes de l'utilisateur
    existing_applications = await db.applications.find(
        {"user_id": current_user.id},
        {"_id": 0, "mission_id": 1}
    ).to_list(length=None)
    
    applied_mission_ids = {app["mission_id"] for app in existing_applications}
    
    # Calculer le score de matching pour chaque mission
    missions_with_score = []
    for mission in missions:
        # Ne pas inclure les missions où l'utilisateur a déjà candidaté
        if mission["id"] in applied_mission_ids:
            continue
        
        # Calculer le matching
        matching_result = MissionMatchingService.calculate_matching_score(
            mission=mission,
            user_profile=user_profile
        )
        
        # Filtrer par score minimum
        if matching_result['score'] >= min_score:
            mission_with_matching = {
                **mission,
                "matching": matching_result
            }
            missions_with_score.append(mission_with_matching)
    
    # Trier par score décroissant
    missions_with_score.sort(key=lambda x: x["matching"]["score"], reverse=True)
    
    # Limiter le nombre de résultats
    return missions_with_score[:limit]


@router.post("/batch-matching", response_model=List[Dict[str, Any]])
async def batch_calculate_matching(
    mission_ids: List[str],
    current_user: User = Depends(get_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Calcule le score de matching pour plusieurs missions en une seule requête
    Utile pour enrichir une liste de missions avec leur score
    
    Args:
        mission_ids: Liste des IDs de missions
    
    Returns:
        Liste des résultats de matching pour chaque mission
    """
    from awana_auth.services.mission_matching_service import MissionMatchingService
    
    # Récupérer le profil de l'utilisateur
    user_profile = await db.interim_profiles.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not user_profile:
        user_profile = await db.candidat_profiles.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not user_profile:
        return []
    
    # Récupérer les missions
    missions = await db.missions.find(
        {"id": {"$in": mission_ids}},
        {"_id": 0}
    ).to_list(length=None)
    
    # Calculer le matching pour chaque mission
    results = []
    for mission in missions:
        matching_result = MissionMatchingService.calculate_matching_score(
            mission=mission,
            user_profile=user_profile
        )
        
        results.append({
            "mission_id": mission["id"],
            "matching": matching_result
        })
    
    return results



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
    
    # Remove MongoDB _id before creating Pydantic model
    mission.pop('_id', None)
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
    # Remove MongoDB _id before creating Pydantic model
    updated_mission.pop('_id', None)
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
    # Remove MongoDB _id before creating Pydantic model
    updated_mission.pop('_id', None)
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
    Accessible par: Candidats, Postulants, Intérimaires (selon règles métiers)
    
    Vérifie :
    - Rôles autorisés (règles métiers)
    - Permissions IAM
    - Contrat actif pour intérimaires
    - CV requis
    - Candidature dupliquée
    """
    from awana_auth.services.application_eligibility_service import ApplicationEligibilityService
    
    user_id = current_user.get("sub")
    user_roles = current_user.get("roles", [])
    
    # Vérifier que la mission existe
    mission = await db.missions.find_one({"id": mission_id})
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    mission_status = mission.get("status")
    
    # Vérifier éligibilité via service avec règles métiers
    eligibility_service = ApplicationEligibilityService(db)
    is_eligible, error_message, metadata = await eligibility_service.check_eligibility(
        user_id=user_id,
        user_roles=user_roles,
        mission_id=mission_id,
        mission_status=mission_status
    )
    
    if not is_eligible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message
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
    
    # Enregistrer l'historique si le statut a changé
    if "status" in update_data:
        from awana_auth.services.application_history_service import ApplicationHistoryService
        
        old_status = application.get("status")
        new_status = update_data["status"]
        
        if old_status != new_status:
            await ApplicationHistoryService.create_history_entry(
                db=db,
                application_id=application_id,
                old_status=old_status,
                new_status=new_status,
                changed_by=current_user.get("id"),
                changed_by_name=current_user.get("full_name"),
                reason=update_data.get("internal_notes"),
                metadata={
                    "score": update_data.get("score"),
                    "interview_rating": update_data.get("interview_rating"),
                    "client_selected": update_data.get("client_selected")
                }
            )
    
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



@router.get("/{mission_id}/matching", response_model=Dict[str, Any])
async def get_mission_matching_score(
    mission_id: str,
    current_user: User = Depends(get_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Calcule le score de matching entre une mission spécifique et le profil de l'utilisateur
    
    Args:
        mission_id: ID de la mission
    
    Returns:
        Score de matching détaillé avec breakdown et recommandations
    """
    from awana_auth.services.mission_matching_service import MissionMatchingService
    
    # Récupérer la mission
    mission = await db.missions.find_one({"id": mission_id}, {"_id": 0})
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    # Récupérer le profil de l'utilisateur
    user_profile = await db.interim_profiles.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not user_profile:
        user_profile = await db.candidat_profiles.find_one({"user_id": current_user.id}, {"_id": 0})
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil utilisateur non trouvé"
        )
    
    # Calculer le matching
    matching_result = MissionMatchingService.calculate_matching_score(
        mission=mission,
        user_profile=user_profile
    )
    
    return matching_result



# ==================== CANDIDAT/POSTULANT ENDPOINTS ====================

@router.patch("/applications/me/{application_id}", response_model=Application)
async def update_my_application(
    application_id: str,
    additional_info: Optional[str] = None,
    current_user: dict = Depends(get_user_dep),
    db = Depends(get_db)
):
    """
    Modifier sa propre candidature (Candidat/Postulant)
    Permet de mettre à jour les informations additionnelles avant validation
    """
    # Support both dict and User object
    user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user.id
    
    # Vérifier que la candidature appartient à l'utilisateur
    application = await db.applications.find_one({
        "id": application_id,
        "user_id": user_id
    })
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée ou vous n'avez pas accès à cette candidature"
        )
    
    # Vérifier que la candidature peut encore être modifiée
    current_status = application.get("status")
    if current_status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vous ne pouvez plus modifier cette candidature (statut: {current_status})"
        )
    
    # Mettre à jour
    update_data = {
        "updated_at": datetime.now(timezone.utc)
    }
    
    if additional_info is not None:
        update_data["additional_info"] = additional_info
    
    await db.applications.update_one(
        {"id": application_id},
        {"$set": update_data}
    )
    
    updated_app = await db.applications.find_one({"id": application_id})
    return Application(**updated_app)


@router.post("/applications/me/{application_id}/cancel", response_model=Application)
async def cancel_my_application(
    application_id: str,
    cancellation_reason: Optional[str] = None,
    current_user: dict = Depends(get_user_dep),
    db = Depends(get_db)
):
    """
    Annuler sa propre candidature (Candidat/Postulant)
    Change le statut à WITHDRAWN (Retirée)
    """
    # Support both dict and User object
    user_id = current_user.get("sub") if isinstance(current_user, dict) else current_user.id
    
    # Vérifier que la candidature appartient à l'utilisateur
    application = await db.applications.find_one({
        "id": application_id,
        "user_id": user_id
    })
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée ou vous n'avez pas accès à cette candidature"
        )
    
    # Vérifier que la candidature peut encore être annulée
    current_status = application.get("status")
    if current_status in [ApplicationStatus.HIRED, ApplicationStatus.WITHDRAWN, ApplicationStatus.CONTRACT_SIGNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vous ne pouvez plus annuler cette candidature (statut: {current_status})"
        )
    
    # Annuler la candidature
    update_data = {
        "status": ApplicationStatus.WITHDRAWN,
        "updated_at": datetime.now(timezone.utc),
        "withdrawn_at": datetime.now(timezone.utc)
    }
    
    if cancellation_reason:
        update_data["cancellation_reason"] = cancellation_reason
        update_data["additional_info"] = f"{application.get('additional_info', '')}\n\nRaison d'annulation: {cancellation_reason}".strip()
    
    await db.applications.update_one(
        {"id": application_id},
        {"$set": update_data}
    )
    
    # Décrémenter le compteur de candidatures de la mission
    await db.missions.update_one(
        {"id": application.get("mission_id")},
        {"$inc": {"applications_count": -1}}
    )
    
    updated_app = await db.applications.find_one({"id": application_id})
    return Application(**updated_app)



# MATCHING ENDPOINTS MOVED BEFORE /{mission_id}


# ==================== APPLICATION HISTORY & TIMELINE ENDPOINTS ====================

@router.get("/applications/{application_id}/history", response_model=List[Dict[str, Any]])
async def get_application_history(
    application_id: str,
    sort_order: str = "asc",
    current_user: User = Depends(get_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère l'historique complet d'une candidature (timeline)
    
    Args:
        application_id: ID de la candidature
        sort_order: Ordre de tri ("asc" pour chronologique, "desc" pour inverse)
    
    Returns:
        Liste des entrées d'historique avec les changements de statut
    """
    from awana_auth.services.application_history_service import ApplicationHistoryService
    
    # Vérifier que l'application existe et que l'utilisateur y a accès
    application = await db.applications.find_one({"id": application_id}, {"_id": 0})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée"
        )
    
    # Vérifier les permissions
    permission_checker = PermissionChecker(db)
    user_permissions = await permission_checker.get_user_permissions(current_user.id)
    
    can_manage_all = "applications.manage" in user_permissions
    is_owner = application["user_id"] == current_user.id
    
    if not (can_manage_all or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à l'historique de cette candidature"
        )
    
    # Récupérer l'historique
    history = await ApplicationHistoryService.get_application_history(
        db=db,
        application_id=application_id,
        sort_order=sort_order
    )
    
    return history


@router.get("/applications/{application_id}/timeline-stats", response_model=Dict[str, Any])
async def get_application_timeline_stats(
    application_id: str,
    current_user: User = Depends(get_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère les statistiques de la timeline d'une candidature
    (durées, temps passé dans chaque statut, etc.)
    
    Args:
        application_id: ID de la candidature
    
    Returns:
        Statistiques de la timeline
    """
    from awana_auth.services.application_history_service import ApplicationHistoryService
    
    # Vérifier que l'application existe et que l'utilisateur y a accès
    application = await db.applications.find_one({"id": application_id}, {"_id": 0})
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidature non trouvée"
        )
    
    # Vérifier les permissions
    permission_checker = PermissionChecker(db)
    user_permissions = await permission_checker.get_user_permissions(current_user.id)
    
    can_manage_all = "applications.manage" in user_permissions
    is_owner = application["user_id"] == current_user.id
    
    if not (can_manage_all or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès aux statistiques de cette candidature"
        )
    
    # Calculer les stats
    stats = await ApplicationHistoryService.get_timeline_stats(
        db=db,
        application_id=application_id
    )
    
    # Ajouter des infos sur la candidature
    stats["application"] = {
        "id": application["id"],
        "mission_id": application["mission_id"],
        "current_status": application["status"],
        "created_at": application["created_at"].isoformat() if isinstance(application["created_at"], datetime) else application["created_at"]
    }
    
    return stats


@router.get("/applications/my-applications/with-history", response_model=List[Dict[str, Any]])
async def get_my_applications_with_history(
    current_user: User = Depends(get_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupère toutes les candidatures de l'utilisateur avec leur historique
    Optimisé avec une seule requête bulk pour l'historique
    
    Returns:
        Liste des candidatures enrichies avec leur historique
    """
    from awana_auth.services.application_history_service import ApplicationHistoryService
    
    # Récupérer les candidatures de l'utilisateur
    applications = await db.applications.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(length=None)
    
    if not applications:
        return []
    
    # Récupérer les IDs
    application_ids = [app["id"] for app in applications]
    
    # Récupérer l'historique en bulk (optimisé)
    histories = await ApplicationHistoryService.get_applications_history_bulk(
        db=db,
        application_ids=application_ids
    )
    
    # Enrichir chaque candidature avec son historique
    for application in applications:
        app_id = application["id"]
        application["history"] = histories.get(app_id, [])
        application["history_count"] = len(application["history"])
        
        # Ajouter un flag pour les nouvelles mises à jour
        if application["history"]:
            last_change = application["history"][-1]
            last_change_date = last_change.get("changed_at")
            
            if isinstance(last_change_date, str):
                last_change_date = datetime.fromisoformat(last_change_date.replace("Z", "+00:00"))
            
            # Considérer comme "nouveau" si changement dans les dernières 48h
            if last_change_date and (datetime.now(timezone.utc) - last_change_date).days < 2:
                application["has_recent_update"] = True
            else:
                application["has_recent_update"] = False
        else:
            application["has_recent_update"] = False
    
    return applications


@router.post("/admin/backfill-application-history")
async def backfill_application_history(
    current_user: User = Depends(require_permission("applications.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    [ADMIN ONLY] Crée l'historique rétroactif pour toutes les candidatures existantes
    Cette route doit être appelée une seule fois pour initialiser l'historique
    
    Returns:
        Statistiques du backfill
    """
    from awana_auth.services.application_history_service import ApplicationHistoryService
    
    result = await ApplicationHistoryService.backfill_existing_applications(db)
    
    return {
        "success": True,
        "message": "Backfill de l'historique terminé",
        "stats": result
    }

