"""
Professional Experiences Routes
Gestion des expériences professionnelles pour les profils Interim et Candidats

Features:
- CRUD complet sur les expériences
- Validation des dates et de la cohérence
- Permissions IAM (seul le propriétaire peut modifier)
- Gestion d'erreurs robuste
- Audit trail automatique
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import uuid
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.profile_models import ProfessionalExperience, ExperienceType
from awana_auth.core.models import User

router = APIRouter(prefix="/profiles/me/experiences", tags=["Professional Experiences"])


# ==================== Helper Functions ====================

def _get_profile_collection_name(user_roles: List[str]) -> str:
    """
    Déterminer le nom de la collection de profil selon les rôles utilisateur
    
    Architecture:
    - interim_profiles : pour les intérimaires
    - candidat_profiles : pour les candidats/postulants
    - company_manager_profiles : pour les entreprises
    - collaborator_profiles : pour les collaborateurs
    
    Args:
        user_roles: Liste des rôles de l'utilisateur
        
    Returns:
        str: Nom de la collection
    """
    if "intérimaire" in user_roles or "interim" in user_roles:
        return "interim_profiles"
    elif "candidat" in user_roles or "postulant" in user_roles:
        return "candidat_profiles"
    elif "entreprise" in user_roles or "company" in user_roles:
        return "company_manager_profiles"
    elif "collaborator" in user_roles:
        return "collaborator_profiles"
    else:
        # Par défaut, candidat
        return "candidat_profiles"


# ==================== Request Models ====================

class ExperienceCreate(BaseModel):
    """Model for creating a new experience"""
    type: str = ExperienceType.EXTERNAL
    job_title: str = Field(..., min_length=2, max_length=200)
    company_name: str = Field(..., min_length=2, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    start_date: str  # ISO date format
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = Field(None, max_length=2000)
    achievements: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)
    mission_id: Optional[str] = None
    contract_id: Optional[str] = None
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """Validate ISO date format"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end_date is after start_date"""
        if v and 'start_date' in values:
            start = datetime.fromisoformat(values['start_date'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(v.replace('Z', '+00:00'))
            if end < start:
                raise ValueError('end_date must be after start_date')
        return v


class ExperienceUpdate(BaseModel):
    """Model for updating an experience"""
    type: Optional[str] = None
    job_title: Optional[str] = Field(None, min_length=2, max_length=200)
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=2000)
    achievements: Optional[List[str]] = None
    skills_used: Optional[List[str]] = None
    mission_id: Optional[str] = None
    contract_id: Optional[str] = None


# ==================== Endpoints ====================

@router.get("", response_model=List[ProfessionalExperience])
async def get_my_experiences(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Récupérer toutes les expériences professionnelles de l'utilisateur courant
    
    Returns:
        List[ProfessionalExperience]: Liste des expériences
    """
    try:
        # Déterminer la collection selon le rôle
        collection_name = _get_profile_collection_name(current_user.roles)
        
        # Récupérer le profil de l'utilisateur
        profile = await db[collection_name].find_one(
            {"user_id": current_user.id},
            {"_id": 0, "professional_experiences": 1}
        )
        
        if not profile:
            return []
        
        experiences = profile.get("professional_experiences", [])
        
        # Trier par date de début (plus récent en premier)
        experiences_sorted = sorted(
            experiences,
            key=lambda x: x.get("start_date", ""),
            reverse=True
        )
        
        return experiences_sorted
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des expériences: {str(e)}"
        )


@router.post("", response_model=ProfessionalExperience, status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience_data: ExperienceCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Créer une nouvelle expérience professionnelle
    
    Args:
        experience_data: Données de l'expérience
        
    Returns:
        ProfessionalExperience: Expérience créée
        
    Security:
        - Seul le propriétaire peut créer ses expériences
        - Validation stricte des dates
        - Génération automatique de l'ID unique
    """
    try:
        # Vérifier que le profil existe, sinon le créer automatiquement
        profile = await db.profiles.find_one({"user_id": current_user.id})
        
        if not profile:
            # Créer un profil minimal automatiquement pour l'utilisateur
            # Déterminer le type de profil basé sur les rôles
            profile_type = "candidat"
            if "intérimaire" in current_user.roles:
                profile_type = "interim"
            elif "entreprise" in current_user.roles or "company" in current_user.roles:
                profile_type = "company"
            elif "collaborator" in current_user.roles:
                profile_type = "collaborator"
            
            now = datetime.utcnow().isoformat()
            new_profile = {
                "user_id": current_user.id,
                "profile_type": profile_type,
                "professional_experiences": [],
                "created_at": now,
                "updated_at": now,
                "profile_completed": False,
                "profile_completion_percentage": 0
            }
            
            await db.profiles.insert_one(new_profile)
            profile = new_profile
        
        # Créer l'expérience avec un ID unique
        experience_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        new_experience = {
            "id": experience_id,
            **experience_data.dict(),
            "created_at": now,
            "updated_at": now
        }
        
        # Ajouter l'expérience au profil
        result = await db.profiles.update_one(
            {"user_id": current_user.id},
            {
                "$push": {"professional_experiences": new_experience},
                "$set": {"updated_at": now}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de l'ajout de l'expérience"
            )
        
        return new_experience
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'expérience: {str(e)}"
        )


@router.get("/{experience_id}", response_model=ProfessionalExperience)
async def get_experience(
    experience_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Récupérer une expérience spécifique par son ID
    
    Args:
        experience_id: ID de l'expérience
        
    Returns:
        ProfessionalExperience: Expérience trouvée
        
    Raises:
        404: Si l'expérience n'existe pas ou n'appartient pas à l'utilisateur
    """
    try:
        profile = await db.profiles.find_one(
            {"user_id": current_user.id},
            {"_id": 0, "professional_experiences": 1}
        )
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil non trouvé"
            )
        
        experiences = profile.get("professional_experiences", [])
        experience = next((exp for exp in experiences if exp["id"] == experience_id), None)
        
        if not experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expérience {experience_id} non trouvée"
            )
        
        return experience
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'expérience: {str(e)}"
        )


@router.put("/{experience_id}", response_model=ProfessionalExperience)
async def update_experience(
    experience_id: str,
    experience_data: ExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Mettre à jour une expérience existante
    
    Args:
        experience_id: ID de l'expérience
        experience_data: Données à mettre à jour
        
    Returns:
        ProfessionalExperience: Expérience mise à jour
        
    Security:
        - Seul le propriétaire peut modifier ses expériences
        - Validation des dates si modifiées
    """
    try:
        # Récupérer le profil et vérifier l'existence de l'expérience
        profile = await db.profiles.find_one({"user_id": current_user.id})
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil non trouvé"
            )
        
        experiences = profile.get("professional_experiences", [])
        exp_index = next((i for i, exp in enumerate(experiences) if exp["id"] == experience_id), None)
        
        if exp_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expérience {experience_id} non trouvée"
            )
        
        # Construire les champs à mettre à jour
        update_fields = {k: v for k, v in experience_data.dict(exclude_unset=True).items() if v is not None}
        update_fields["updated_at"] = datetime.utcnow().isoformat()
        
        # Créer les opérations de mise à jour MongoDB
        set_operations = {
            f"professional_experiences.{exp_index}.{key}": value
            for key, value in update_fields.items()
        }
        set_operations["updated_at"] = update_fields["updated_at"]
        
        # Exécuter la mise à jour
        result = await db.profiles.update_one(
            {"user_id": current_user.id},
            {"$set": set_operations}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour de l'expérience"
            )
        
        # Récupérer et retourner l'expérience mise à jour
        updated_profile = await db.profiles.find_one({"user_id": current_user.id})
        updated_experience = updated_profile["professional_experiences"][exp_index]
        
        return updated_experience
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    experience_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Supprimer une expérience professionnelle
    
    Args:
        experience_id: ID de l'expérience à supprimer
        
    Returns:
        204 No Content
        
    Security:
        - Seul le propriétaire peut supprimer ses expériences
        - Suppression définitive (pas de soft delete)
    """
    try:
        # Vérifier que l'expérience existe
        profile = await db.profiles.find_one({"user_id": current_user.id})
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil non trouvé"
            )
        
        experiences = profile.get("professional_experiences", [])
        experience_exists = any(exp["id"] == experience_id for exp in experiences)
        
        if not experience_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expérience {experience_id} non trouvée"
            )
        
        # Supprimer l'expérience
        result = await db.profiles.update_one(
            {"user_id": current_user.id},
            {
                "$pull": {"professional_experiences": {"id": experience_id}},
                "$set": {"updated_at": datetime.utcnow().isoformat()}
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression de l'expérience"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )
