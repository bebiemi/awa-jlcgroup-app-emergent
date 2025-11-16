"""
Service de Workflow de Rétention des Données
Gère le cycle de vie complet de la suppression progressive des utilisateurs
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import logging
import uuid

from .retention_notification_service import RetentionNotificationService

logger = logging.getLogger(__name__)


class RetentionWorkflowService:
    """
    Gère le workflow complet de rétention en 4 étapes:
    - ARCHIVED: État initial
    - PENDING_DELETION (J-7): Notification gestionnaires
    - TO_DELETE (J): Masqué sauf superadmin + notification
    - DELETED (J+3 + 1h): Suppression définitive
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.notification_service = RetentionNotificationService(db)
    
    async def get_retention_period(self) -> int:
        """Récupère le délai de rétention global configuré"""
        setting = await self.db.app_settings.find_one({"key": "security.user_retention_days"})
        if setting and setting.get("value"):
            return int(setting["value"])
        return 90  # Valeur par défaut
    
    async def process_archived_users(self) -> Dict:
        """
        Traite les utilisateurs archivés pour passage à PENDING_DELETION (J-7)
        """
        retention_days = await self.get_retention_period()
        now = datetime.now(timezone.utc)
        
        # Date cible: deletion_scheduled_at - 7 jours
        j_minus_7_threshold = now + timedelta(days=7)
        
        # Trouver les utilisateurs archivés qui atteignent J-7
        eligible_users = await self.db.users.find({
            "status": "archived",
            "deletion_scheduled_at": {
                "$lte": j_minus_7_threshold,
                "$gt": now  # Pas encore passé
            },
            "pending_deletion_at": None  # Pas encore traité
        }).to_list(length=None)
        
        processed_count = 0
        notifications_sent = 0
        
        for user in eligible_users:
            try:
                # Mettre à jour le statut
                await self.db.users.update_one(
                    {"id": user["id"]},
                    {
                        "$set": {
                            "status": "pending_deletion",
                            "pending_deletion_at": now,
                            "updated_at": now
                        }
                    }
                )
                
                # Envoyer notification J-7
                notification_result = await self.notification_service.send_j_minus_7_notification(user)
                
                if notification_result.get("status") == "sent":
                    await self.notification_service.record_notification_sent(
                        user["id"],
                        "J-7",
                        notification_result["notification_id"]
                    )
                    notifications_sent += 1
                
                processed_count += 1
                logger.info(f"User {user.get('username')} moved to PENDING_DELETION (J-7)")
                
            except Exception as e:
                logger.error(f"Error processing user {user.get('id')} for J-7: {str(e)}")
        
        return {
            "stage": "J-7",
            "processed_count": processed_count,
            "notifications_sent": notifications_sent
        }
    
    async def process_pending_deletion_users(self) -> Dict:
        """
        Traite les utilisateurs PENDING_DELETION pour rappel J-3
        """
        now = datetime.now(timezone.utc)
        
        # Date cible: deletion_scheduled_at - 3 jours
        j_minus_3_threshold = now + timedelta(days=3)
        
        # Trouver les utilisateurs qui atteignent J-3
        eligible_users = await self.db.users.find({
            "status": "pending_deletion",
            "deletion_scheduled_at": {
                "$lte": j_minus_3_threshold,
                "$gt": now
            },
            "notifications_sent": {
                "$not": {"$elemMatch": {"type": "J-3"}}  # Pas encore envoyé
            }
        }).to_list(length=None)
        
        notifications_sent = 0
        
        for user in eligible_users:
            try:
                # Envoyer notification J-3
                notification_result = await self.notification_service.send_j_minus_3_notification(user)
                
                if notification_result.get("status") == "sent":
                    await self.notification_service.record_notification_sent(
                        user["id"],
                        "J-3",
                        notification_result["notification_id"]
                    )
                    notifications_sent += 1
                
                logger.info(f"J-3 notification sent for user {user.get('username')}")
                
            except Exception as e:
                logger.error(f"Error sending J-3 notification for user {user.get('id')}: {str(e)}")
        
        return {
            "stage": "J-3",
            "notifications_sent": notifications_sent
        }
    
    async def process_to_delete_users(self) -> Dict:
        """
        Traite les utilisateurs dont la date de suppression est atteinte (Jour J)
        Passage à TO_DELETE (masqué sauf superadmin)
        """
        now = datetime.now(timezone.utc)
        
        # Trouver les utilisateurs dont deletion_scheduled_at est passé
        eligible_users = await self.db.users.find({
            "status": "pending_deletion",
            "deletion_scheduled_at": {"$lte": now},
            "to_delete_at": None
        }).to_list(length=None)
        
        processed_count = 0
        notifications_sent = 0
        
        for user in eligible_users:
            try:
                # Mettre à jour le statut à TO_DELETE
                await self.db.users.update_one(
                    {"id": user["id"]},
                    {
                        "$set": {
                            "status": "to_delete",
                            "to_delete_at": now,
                            "updated_at": now,
                            # Date de suppression définitive: J+3 + 1h
                            "soft_deleted_at": now + timedelta(days=3, hours=1)
                        }
                    }
                )
                
                # Envoyer notification Jour J
                notification_result = await self.notification_service.send_j_day_notification(user)
                
                if notification_result.get("status") == "sent":
                    await self.notification_service.record_notification_sent(
                        user["id"],
                        "J",
                        notification_result["notification_id"]
                    )
                    notifications_sent += 1
                
                processed_count += 1
                logger.info(f"User {user.get('username')} moved to TO_DELETE (J)")
                
            except Exception as e:
                logger.error(f"Error processing user {user.get('id')} for J: {str(e)}")
        
        return {
            "stage": "J",
            "processed_count": processed_count,
            "notifications_sent": notifications_sent
        }
    
    async def process_final_deletion(self) -> Dict:
        """
        Traite la suppression définitive des utilisateurs (J+3)
        Envoie notification 1h avant puis supprime
        """
        now = datetime.now(timezone.utc)
        
        # Trouver les utilisateurs dont soft_deleted_at - 1h est passé (pour notification)
        notification_threshold = now + timedelta(hours=1)
        users_for_notification = await self.db.users.find({
            "status": "to_delete",
            "soft_deleted_at": {
                "$lte": notification_threshold,
                "$gt": now
            },
            "notifications_sent": {
                "$not": {"$elemMatch": {"type": "J+3"}}
            }
        }).to_list(length=None)
        
        notifications_sent = 0
        
        for user in users_for_notification:
            try:
                # Envoyer notification J+3 (1h avant suppression)
                notification_result = await self.notification_service.send_j_plus_3_notification(user)
                
                if notification_result.get("status") == "sent":
                    await self.notification_service.record_notification_sent(
                        user["id"],
                        "J+3",
                        notification_result["notification_id"]
                    )
                    notifications_sent += 1
                
                logger.info(f"J+3 notification sent for user {user.get('username')}")
                
            except Exception as e:
                logger.error(f"Error sending J+3 notification for user {user.get('id')}: {str(e)}")
        
        # Trouver les utilisateurs à supprimer définitivement
        users_to_delete = await self.db.users.find({
            "status": "to_delete",
            "soft_deleted_at": {"$lte": now}
        }).to_list(length=None)
        
        deleted_count = 0
        deleted_ids = []
        
        for user in users_to_delete:
            try:
                # Sauvegarder dans audit avant suppression
                await self.db.deleted_users_audit.insert_one({
                    "id": str(uuid.uuid4()),
                    "original_user_id": user["id"],
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "roles": user.get("roles", []),
                    "archived_at": user.get("archived_at"),
                    "archived_by": user.get("archived_by"),
                    "pending_deletion_at": user.get("pending_deletion_at"),
                    "to_delete_at": user.get("to_delete_at"),
                    "deletion_executed_at": now,
                    "archive_reason": user.get("archive_reason"),
                    "notifications_sent": user.get("notifications_sent", [])
                })
                
                # Suppression définitive
                await self.db.users.delete_one({"id": user["id"]})
                
                deleted_ids.append(user["id"])
                deleted_count += 1
                
                logger.info(f"User {user.get('username')} permanently deleted (J+3)")
                
            except Exception as e:
                logger.error(f"Error permanently deleting user {user.get('id')}: {str(e)}")
        
        return {
            "stage": "J+3",
            "notifications_sent": notifications_sent,
            "deleted_count": deleted_count,
            "deleted_ids": deleted_ids
        }
    
    async def execute_full_workflow(self) -> Dict:
        """
        Exécute le workflow complet de rétention
        Appelé par la tâche planifiée
        """
        logger.info("🔄 Starting retention workflow execution...")
        start_time = datetime.now(timezone.utc)
        
        results = {
            "execution_time": start_time.isoformat(),
            "stages": {}
        }
        
        try:
            # Étape 1: ARCHIVED → PENDING_DELETION (J-7)
            j_minus_7_result = await self.process_archived_users()
            results["stages"]["j_minus_7"] = j_minus_7_result
            
            # Étape 2: PENDING_DELETION rappel (J-3)
            j_minus_3_result = await self.process_pending_deletion_users()
            results["stages"]["j_minus_3"] = j_minus_3_result
            
            # Étape 3: PENDING_DELETION → TO_DELETE (J)
            j_result = await self.process_to_delete_users()
            results["stages"]["j"] = j_result
            
            # Étape 4: TO_DELETE → Suppression définitive (J+3)
            j_plus_3_result = await self.process_final_deletion()
            results["stages"]["j_plus_3"] = j_plus_3_result
            
            # Calcul du total
            total_processed = (
                j_minus_7_result["processed_count"] +
                j_result["processed_count"]
            )
            total_notifications = (
                j_minus_7_result["notifications_sent"] +
                j_minus_3_result["notifications_sent"] +
                j_result["notifications_sent"] +
                j_plus_3_result["notifications_sent"]
            )
            total_deleted = j_plus_3_result["deleted_count"]
            
            results["summary"] = {
                "total_users_processed": total_processed,
                "total_notifications_sent": total_notifications,
                "total_permanently_deleted": total_deleted
            }
            
            # Enregistrer l'audit
            await self.db.audit_events.insert_one({
                "id": str(uuid.uuid4()),
                "action": "retention_workflow.execute",
                "actor_id": "system",
                "actor_username": "retention_workflow",
                "target_type": "users",
                "target_id": "batch",
                "payload": results,
                "timestamp": start_time,
                "ip_address": None,
                "user_agent": "scheduler"
            })
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"✅ Retention workflow completed in {execution_time:.2f}s: "
                f"{total_processed} processed, {total_notifications} notifications, "
                f"{total_deleted} deleted"
            )
            
            results["execution_duration_seconds"] = execution_time
            results["status"] = "success"
            
        except Exception as e:
            logger.error(f"❌ Error in retention workflow: {str(e)}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
