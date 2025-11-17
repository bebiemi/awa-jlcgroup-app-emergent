"""
Company Profile Sync Service
Service de synchronisation automatique des profils entreprise
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class CompanyProfileSyncService:
    """
    Service pour synchroniser automatiquement les profils entreprise
    avec les données utilisateur
    """
    
    @staticmethod
    async def sync_profile_from_user(
        db: AsyncIOMotorDatabase,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> bool:
        """
        Synchronise le profil entreprise avec les données utilisateur
        
        Args:
            db: Database connection
            user_id: ID de l'utilisateur
            user_data: Données utilisateur mises à jour
        
        Returns:
            True si synchronisation effectuée, False sinon
        """
        try:
            # Récupérer l'utilisateur complet
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            
            if not user or "company" not in user.get("roles", []):
                # Pas une entreprise, pas de sync
                return False
            
            # Vérifier si le profil existe
            profile = await db.company_profiles.find_one({"user_id": user_id})
            
            if not profile:
                logger.warning(f"Company profile not found for user {user_id}, skipping sync")
                return False
            
            # Préparer les champs à synchroniser
            sync_fields = {}
            
            # Synchroniser les champs de base
            if "full_name" in user_data and user_data["full_name"]:
                sync_fields["dirigeant"] = user_data["full_name"]
            
            if "phone" in user_data and user_data["phone"]:
                sync_fields["phone"] = user_data["phone"]
            
            if "email" in user_data and user_data["email"]:
                sync_fields["email"] = user_data["email"]
            
            # Synchroniser les champs métier entreprise si présents
            company_fields = [
                "company_name", "nif", "siret", "address", 
                "sector", "company_size", "description", "website"
            ]
            
            for field in company_fields:
                if field in user_data and user_data[field]:
                    sync_fields[field] = user_data[field]
            
            # Si aucun champ à synchroniser, skip
            if not sync_fields:
                return False
            
            # Ajouter le timestamp
            sync_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
            sync_fields["last_sync_at"] = datetime.now(timezone.utc).isoformat()
            
            # Mettre à jour le profil
            result = await db.company_profiles.update_one(
                {"user_id": user_id},
                {"$set": sync_fields}
            )
            
            if result.modified_count > 0:
                logger.info(f"Company profile synced for user {user_id}: {list(sync_fields.keys())}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error syncing company profile for user {user_id}: {e}")
            return False
    
    @staticmethod
    async def ensure_profile_exists(
        db: AsyncIOMotorDatabase,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Vérifie qu'un profil entreprise existe, sinon le crée
        
        Args:
            db: Database connection
            user_id: ID de l'utilisateur
        
        Returns:
            Le profil entreprise (existant ou créé), ou None si pas applicable
        """
        try:
            # Récupérer l'utilisateur
            user = await db.users.find_one({"id": user_id}, {"_id": 0})
            
            if not user or "company" not in user.get("roles", []):
                return None
            
            # Vérifier si le profil existe déjà
            profile = await db.company_profiles.find_one({"user_id": user_id}, {"_id": 0})
            
            if profile:
                return profile
            
            # Créer le profil minimal
            company_profile = {
                "user_id": user_id,
                "company_name": user.get("company_name") or user.get("full_name") or "Entreprise sans nom",
                "dirigeant": user.get("full_name") or "Non renseigné",
                "nif": user.get("nif"),
                "siret": user.get("siret"),
                "phone": user.get("phone"),
                "email": user.get("email"),
                "address": user.get("address"),
                "sector": user.get("sector"),
                "company_size": user.get("company_size"),
                "description": user.get("description"),
                "website": user.get("website"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.company_profiles.insert_one(company_profile)
            
            logger.info(f"Company profile created via ensure_profile_exists for user {user_id}")
            
            # Retourner le profil sans _id
            profile = await db.company_profiles.find_one({"user_id": user_id}, {"_id": 0})
            return profile
            
        except Exception as e:
            logger.error(f"Error ensuring company profile exists for user {user_id}: {e}")
            return None
    
    @staticmethod
    async def validate_required_fields(profile: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Valide que les champs obligatoires du profil sont remplis
        
        Args:
            profile: Profil entreprise à valider
        
        Returns:
            (is_valid, missing_fields)
        """
        required_fields = ["company_name", "dirigeant", "nif"]
        missing = []
        
        for field in required_fields:
            if not profile.get(field):
                missing.append(field)
        
        return len(missing) == 0, missing
