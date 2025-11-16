"""
Service de Notification pour la Politique de Rétention
Gère l'envoi des notifications aux gestionnaires et superadmins
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)


class RetentionNotificationService:
    """Service pour gérer les notifications de rétention"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_user_managers(self, user_id: str) -> List[Dict]:
        """
        Récupère les gestionnaires d'un utilisateur
        Basé sur les rôles et permissions
        """
        # Récupérer les utilisateurs avec permission USERS_MANAGE
        managers = await self.db.users.find({
            "status": "active",
            "roles": {"$in": ["admin", "user_manager", "rh_manager"]}
        }, {"_id": 0, "id": 1, "email": 1, "username": 1, "roles": 1}).to_list(length=None)
        
        return managers
    
    async def get_superadmins(self) -> List[Dict]:
        """Récupère tous les superadmins actifs"""
        superadmins = await self.db.users.find({
            "status": "active",
            "roles": "super_admin"
        }, {"_id": 0, "id": 1, "email": 1, "username": 1}).to_list(length=None)
        
        return superadmins
    
    async def send_notification(
        self,
        recipient_ids: List[str],
        notification_type: str,
        subject: str,
        message: str,
        user_data: Dict,
        metadata: Dict = None
    ) -> Dict:
        """
        Crée et envoie une notification
        
        Args:
            recipient_ids: IDs des destinataires
            notification_type: Type de notification (J-7, J-3, J, J+3)
            subject: Sujet de la notification
            message: Message de la notification
            user_data: Données de l'utilisateur concerné
            metadata: Métadonnées supplémentaires
        
        Returns:
            Dict avec statut de l'envoi
        """
        now = datetime.now(timezone.utc)
        notification_id = str(uuid.uuid4())
        
        # Créer la notification dans la base
        notification_doc = {
            "id": notification_id,
            "type": notification_type,
            "subject": subject,
            "message": message,
            "recipient_ids": recipient_ids,
            "user_data": {
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "archived_at": user_data.get("archived_at"),
                "deletion_scheduled_at": user_data.get("deletion_scheduled_at")
            },
            "metadata": metadata or {},
            "created_at": now,
            "read_by": [],
            "status": "pending"
        }
        
        await self.db.retention_notifications.insert_one(notification_doc)
        
        # Créer des notifications individuelles pour chaque destinataire
        for recipient_id in recipient_ids:
            await self.db.user_notifications.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": recipient_id,
                "notification_id": notification_id,
                "type": notification_type,
                "subject": subject,
                "message": message,
                "is_read": False,
                "created_at": now,
                "priority": "high" if notification_type in ["J", "J+3"] else "medium"
            })
        
        # TODO: Intégrer avec le service d'email pour envoyer des emails
        # from awana_auth.services.email_service_v2 import send_email
        # for recipient_id in recipient_ids:
        #     recipient = await self.db.users.find_one({"id": recipient_id})
        #     if recipient and recipient.get("email"):
        #         await send_email(recipient["email"], subject, message)
        
        logger.info(
            f"Notification {notification_type} sent for user {user_data.get('username')} "
            f"to {len(recipient_ids)} recipients"
        )
        
        return {
            "notification_id": notification_id,
            "sent_to_count": len(recipient_ids),
            "status": "sent"
        }
    
    async def send_j_minus_7_notification(self, user: Dict) -> Dict:
        """
        Notification J-7: 7 jours avant expiration
        Envoyée aux gestionnaires d'utilisateurs
        """
        managers = await self.get_user_managers(user["id"])
        
        if not managers:
            logger.warning(f"No managers found for user {user.get('username')}")
            return {"status": "no_recipients"}
        
        manager_ids = [m["id"] for m in managers]
        
        deletion_date = user.get("deletion_scheduled_at")
        deletion_str = deletion_date.strftime("%d/%m/%Y") if isinstance(deletion_date, datetime) else str(deletion_date)
        
        subject = f"[URGENT] Suppression imminente du compte utilisateur - {user.get('username')}"
        message = f"""
Bonjour,

Le compte utilisateur suivant est programmé pour suppression dans 7 jours :

- Utilisateur : {user.get('username')}
- Email : {user.get('email')}
- Date d'archivage : {user.get('archived_at').strftime('%d/%m/%Y') if isinstance(user.get('archived_at'), datetime) else 'N/A'}
- Date de suppression prévue : {deletion_str}
- Raison : {user.get('archive_reason', 'Non spécifiée')}

Le statut du compte passera à "À supprimer" (PENDING_DELETION).

Actions possibles :
- Restaurer le compte si nécessaire via le portail d'administration
- Prendre connaissance de cette suppression programmée

Ce message est un rappel automatique. Des rappels suivront à J-3 et au jour J.

Cordialement,
Système de Gestion JLC
"""
        
        return await self.send_notification(
            recipient_ids=manager_ids,
            notification_type="J-7",
            subject=subject,
            message=message,
            user_data=user,
            metadata={"days_remaining": 7}
        )
    
    async def send_j_minus_3_notification(self, user: Dict) -> Dict:
        """
        Notification J-3: 3 jours avant expiration
        Rappel aux gestionnaires
        """
        managers = await self.get_user_managers(user["id"])
        
        if not managers:
            logger.warning(f"No managers found for user {user.get('username')}")
            return {"status": "no_recipients"}
        
        manager_ids = [m["id"] for m in managers]
        
        deletion_date = user.get("deletion_scheduled_at")
        deletion_str = deletion_date.strftime("%d/%m/%Y") if isinstance(deletion_date, datetime) else str(deletion_date)
        
        subject = f"[RAPPEL - J-3] Suppression du compte utilisateur - {user.get('username')}"
        message = f"""
Bonjour,

RAPPEL : Le compte utilisateur suivant sera supprimé dans 3 jours :

- Utilisateur : {user.get('username')}
- Email : {user.get('email')}
- Date de suppression prévue : {deletion_str}

DERNIÈRE CHANCE pour restaurer ce compte si nécessaire.

Après cette date, le compte ne sera plus visible que par les super-administrateurs pendant 3 jours supplémentaires avant suppression définitive.

Cordialement,
Système de Gestion JLC
"""
        
        return await self.send_notification(
            recipient_ids=manager_ids,
            notification_type="J-3",
            subject=subject,
            message=message,
            user_data=user,
            metadata={"days_remaining": 3}
        )
    
    async def send_j_day_notification(self, user: Dict) -> Dict:
        """
        Notification Jour J: Suppression de la visibilité
        Dernier rappel aux gestionnaires + notification superadmin
        """
        # Notification aux gestionnaires
        managers = await self.get_user_managers(user["id"])
        superadmins = await self.get_superadmins()
        
        all_recipients = managers + superadmins
        recipient_ids = list(set([r["id"] for r in all_recipients]))
        
        if not recipient_ids:
            logger.error(f"No recipients found for J-day notification for user {user.get('username')}")
            return {"status": "no_recipients"}
        
        subject = f"[ACTION IMMÉDIATE] Compte utilisateur masqué - {user.get('username')}"
        message = f"""
Bonjour,

Le compte utilisateur suivant a atteint sa date de suppression et n'est plus visible que par les super-administrateurs :

- Utilisateur : {user.get('username')}
- Email : {user.get('email')}
- Statut : TO_DELETE (masqué)

Le compte sera définitivement supprimé dans 3 jours (J+3) sauf action contraire.

SUPER-ADMINISTRATEURS : Vous avez encore 3 jours pour restaurer ce compte si nécessaire.

Cordialement,
Système de Gestion JLC
"""
        
        return await self.send_notification(
            recipient_ids=recipient_ids,
            notification_type="J",
            subject=subject,
            message=message,
            user_data=user,
            metadata={"action": "hidden_from_view"}
        )
    
    async def send_j_plus_3_notification(self, user: Dict) -> Dict:
        """
        Notification J+3: Suppression définitive dans 1h
        Envoyée uniquement aux superadmins
        """
        superadmins = await self.get_superadmins()
        
        if not superadmins:
            logger.error("No superadmins found for J+3 notification")
            return {"status": "no_recipients"}
        
        superadmin_ids = [s["id"] for s in superadmins]
        
        subject = f"[CRITIQUE - SUPPRESSION dans 1h] Compte - {user.get('username')}"
        message = f"""
ATTENTION SUPER-ADMINISTRATEURS,

Le compte utilisateur suivant sera DÉFINITIVEMENT SUPPRIMÉ dans 1 heure :

- Utilisateur : {user.get('username')}
- Email : {user.get('email')}
- Date d'archivage : {user.get('archived_at').strftime('%d/%m/%Y') if isinstance(user.get('archived_at'), datetime) else 'N/A'}

DERNIÈRE CHANCE AVANT SUPPRESSION DÉFINITIVE.

Cette action est IRRÉVERSIBLE.

Cordialement,
Système de Gestion JLC
"""
        
        return await self.send_notification(
            recipient_ids=superadmin_ids,
            notification_type="J+3",
            subject=subject,
            message=message,
            user_data=user,
            metadata={"action": "permanent_deletion_imminent", "hours_remaining": 1}
        )
    
    async def record_notification_sent(self, user_id: str, notification_type: str, notification_id: str):
        """Enregistre qu'une notification a été envoyée pour un utilisateur"""
        now = datetime.now(timezone.utc)
        
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$push": {
                    "notifications_sent": {
                        "type": notification_type,
                        "notification_id": notification_id,
                        "sent_at": now
                    }
                },
                "$set": {
                    "last_notification_at": now
                }
            }
        )
