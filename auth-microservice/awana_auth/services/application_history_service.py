"""
Application History Service
Service de gestion de l'historique des candidatures
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import logging

logger = logging.getLogger(__name__)


class ApplicationHistoryService:
    """
    Service pour gérer l'historique des changements de statut des candidatures
    """
    
    @staticmethod
    async def create_history_entry(
        db: AsyncIOMotorDatabase,
        application_id: str,
        old_status: Optional[str],
        new_status: str,
        changed_by: str,
        changed_by_name: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crée une entrée dans l'historique des candidatures
        
        Args:
            db: Database connection
            application_id: ID de la candidature
            old_status: Ancien statut (None si création)
            new_status: Nouveau statut
            changed_by: ID de l'utilisateur qui a fait le changement
            changed_by_name: Nom de l'utilisateur (optionnel)
            reason: Raison du changement (optionnel)
            metadata: Données additionnelles (optionnel)
        
        Returns:
            ID de l'entrée créée
        """
        entry_id = str(uuid.uuid4())
        
        history_entry = {
            "id": entry_id,
            "application_id": application_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_by": changed_by,
            "changed_by_name": changed_by_name,
            "changed_at": datetime.now(timezone.utc),
            "reason": reason,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.application_history.insert_one(history_entry)
        
        logger.info(
            f"History entry created: application_id={application_id}, "
            f"status_change={old_status} → {new_status}, changed_by={changed_by}"
        )
        
        return entry_id
    
    @staticmethod
    async def get_application_history(
        db: AsyncIOMotorDatabase,
        application_id: str,
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        Récupère l'historique complet d'une candidature
        
        Args:
            db: Database connection
            application_id: ID de la candidature
            sort_order: Ordre de tri ("asc" ou "desc")
        
        Returns:
            Liste des entrées d'historique
        """
        sort_direction = 1 if sort_order == "asc" else -1
        
        history = await db.application_history.find(
            {"application_id": application_id},
            {"_id": 0}
        ).sort("changed_at", sort_direction).to_list(length=None)
        
        # Enrichir avec des informations de statut lisibles
        for entry in history:
            entry["changed_at_iso"] = entry["changed_at"].isoformat() if isinstance(entry["changed_at"], datetime) else entry["changed_at"]
        
        return history
    
    @staticmethod
    async def get_applications_history_bulk(
        db: AsyncIOMotorDatabase,
        application_ids: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère l'historique de plusieurs candidatures en une seule requête
        
        Args:
            db: Database connection
            application_ids: Liste des IDs de candidatures
        
        Returns:
            Dictionnaire {application_id: [history_entries]}
        """
        history_entries = await db.application_history.find(
            {"application_id": {"$in": application_ids}},
            {"_id": 0}
        ).sort("changed_at", 1).to_list(length=None)
        
        # Grouper par application_id
        result = {}
        for entry in history_entries:
            app_id = entry["application_id"]
            if app_id not in result:
                result[app_id] = []
            
            # Convertir datetime en ISO string
            entry["changed_at_iso"] = entry["changed_at"].isoformat() if isinstance(entry["changed_at"], datetime) else entry["changed_at"]
            result[app_id].append(entry)
        
        return result
    
    @staticmethod
    async def get_timeline_stats(
        db: AsyncIOMotorDatabase,
        application_id: str
    ) -> Dict[str, Any]:
        """
        Calcule des statistiques sur la timeline d'une candidature
        
        Returns:
            Dictionnaire avec :
            - total_duration: Durée totale depuis création
            - stages: Temps passé dans chaque statut
            - current_stage_duration: Temps dans le statut actuel
        """
        history = await ApplicationHistoryService.get_application_history(db, application_id, "asc")
        
        if not history:
            return {
                "total_duration_days": 0,
                "stages": [],
                "current_stage_duration_days": 0
            }
        
        # Calculer la durée totale
        first_entry = history[0]
        last_entry = history[-1]
        
        first_date = first_entry["changed_at"] if isinstance(first_entry["changed_at"], datetime) else datetime.fromisoformat(first_entry["changed_at"])
        last_date = last_entry["changed_at"] if isinstance(last_entry["changed_at"], datetime) else datetime.fromisoformat(last_entry["changed_at"])
        
        total_duration = (datetime.now(timezone.utc) - first_date).days
        
        # Calculer le temps dans chaque statut
        stages = []
        for i in range(len(history)):
            entry = history[i]
            start_date = entry["changed_at"] if isinstance(entry["changed_at"], datetime) else datetime.fromisoformat(entry["changed_at"])
            
            if i < len(history) - 1:
                # Il y a un statut suivant
                next_entry = history[i + 1]
                end_date = next_entry["changed_at"] if isinstance(next_entry["changed_at"], datetime) else datetime.fromisoformat(next_entry["changed_at"])
            else:
                # Dernier statut, utiliser maintenant
                end_date = datetime.now(timezone.utc)
            
            duration_days = (end_date - start_date).days
            duration_hours = (end_date - start_date).total_seconds() / 3600
            
            stages.append({
                "status": entry["new_status"],
                "duration_days": duration_days,
                "duration_hours": round(duration_hours, 1),
                "started_at": start_date.isoformat(),
                "ended_at": end_date.isoformat() if i < len(history) - 1 else None
            })
        
        # Durée dans le statut actuel
        current_stage_start = last_date
        current_stage_duration = (datetime.now(timezone.utc) - current_stage_start).days
        
        return {
            "total_duration_days": total_duration,
            "stages": stages,
            "current_stage_duration_days": current_stage_duration,
            "total_stages": len(stages)
        }
    
    @staticmethod
    async def backfill_existing_applications(
        db: AsyncIOMotorDatabase,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Crée l'historique rétroactif pour les candidatures existantes
        qui n'ont pas encore d'entrées dans application_history
        
        Args:
            db: Database connection
            batch_size: Taille des lots de traitement
        
        Returns:
            Statistiques du backfill (nombre traité, erreurs, etc.)
        """
        logger.info("Starting application history backfill...")
        
        # Récupérer toutes les candidatures
        applications = await db.applications.find({}, {"_id": 0}).to_list(length=None)
        
        processed = 0
        created = 0
        skipped = 0
        errors = []
        
        for application in applications:
            try:
                app_id = application["id"]
                
                # Vérifier si une entrée existe déjà
                existing = await db.application_history.find_one({"application_id": app_id})
                
                if existing:
                    skipped += 1
                    continue
                
                # Créer l'entrée initiale
                current_status = application.get("status", "submitted")
                created_at = application.get("created_at")
                
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                elif not isinstance(created_at, datetime):
                    created_at = datetime.now(timezone.utc)
                
                history_entry = {
                    "id": str(uuid.uuid4()),
                    "application_id": app_id,
                    "old_status": None,
                    "new_status": current_status,
                    "changed_by": application.get("user_id", "system"),
                    "changed_by_name": "Système (backfill)",
                    "changed_at": created_at,
                    "reason": "Création initiale de la candidature",
                    "metadata": {
                        "backfilled": True,
                        "backfilled_at": datetime.now(timezone.utc).isoformat()
                    },
                    "created_at": created_at
                }
                
                await db.application_history.insert_one(history_entry)
                created += 1
                
                # Si le statut actuel n'est pas "submitted", créer une entrée de transition
                if current_status != "submitted":
                    updated_at = application.get("updated_at", created_at)
                    
                    if isinstance(updated_at, str):
                        updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    elif not isinstance(updated_at, datetime):
                        updated_at = datetime.now(timezone.utc)
                    
                    transition_entry = {
                        "id": str(uuid.uuid4()),
                        "application_id": app_id,
                        "old_status": "submitted",
                        "new_status": current_status,
                        "changed_by": "system",
                        "changed_by_name": "Système (backfill)",
                        "changed_at": updated_at,
                        "reason": f"Transition vers {current_status}",
                        "metadata": {
                            "backfilled": True,
                            "backfilled_at": datetime.now(timezone.utc).isoformat()
                        },
                        "created_at": updated_at
                    }
                    
                    await db.application_history.insert_one(transition_entry)
                    created += 1
                
                processed += 1
                
            except Exception as e:
                logger.error(f"Error backfilling application {application.get('id')}: {e}")
                errors.append({
                    "application_id": application.get("id"),
                    "error": str(e)
                })
        
        result = {
            "total_applications": len(applications),
            "processed": processed,
            "created_entries": created,
            "skipped": skipped,
            "errors_count": len(errors),
            "errors": errors[:10]  # Limiter à 10 erreurs pour ne pas surcharger
        }
        
        logger.info(f"Backfill completed: {result}")
        
        return result
