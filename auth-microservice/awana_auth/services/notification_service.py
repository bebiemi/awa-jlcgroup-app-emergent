"""
Notification Service
Handles email and in-app notifications for workflow events
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

# Email service is in same directory
from .email_service_v2 import EmailServiceV2


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.email_service = EmailServiceV2()
        self.notifications_collection = db.notifications
    
    async def send_besoin_notification(
        self,
        event_type: str,
        besoin_id: str,
        besoin_titre: str,
        entreprise_name: str,
        recipients: List[str],  # List of user types or specific emails
        actor_name: str,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send notification for besoin event
        
        Args:
            event_type: Type of event (submitted, analysed, converted, etc.)
            besoin_id: Besoin ID
            besoin_titre: Besoin title
            entreprise_name: Company name
            recipients: List of recipient types ("jlc_team", "entreprise", etc.)
            actor_name: Name of user who triggered the event
            additional_data: Additional context data
        """
        # Get workflow config to determine recipients
        workflow = await self.db.workflow_configs.find_one({"entity_type": "besoin"})
        if not workflow:
            return
        
        # Resolve recipients
        email_recipients = await self._resolve_recipients(recipients, besoin_id)
        
        if not email_recipients:
            return
        
        # Get email template
        template_key = f"besoin_{event_type}"
        subject, body = self._get_email_template(
            event_type,
            besoin_titre,
            entreprise_name,
            actor_name,
            additional_data or {}
        )
        
        # Send email notifications
        for recipient in email_recipients:
            await self._send_email_notification(
                to_email=recipient["email"],
                to_name=recipient["name"],
                subject=subject,
                body=body,
                besoin_id=besoin_id,
                event_type=event_type
            )
        
        # Create in-app notifications
        for recipient in email_recipients:
            if recipient.get("user_id"):
                await self._create_in_app_notification(
                    user_id=recipient["user_id"],
                    title=subject,
                    message=self._get_short_message(event_type, besoin_titre, entreprise_name),
                    link=f"/besoins/{besoin_id}",
                    notification_type=event_type,
                    entity_type="besoin",
                    entity_id=besoin_id
                )
    
    async def _resolve_recipients(
        self,
        recipient_types: List[str],
        besoin_id: str
    ) -> List[Dict[str, str]]:
        """
        Resolve recipient types to actual user emails
        
        Args:
            recipient_types: List like ["jlc_team", "entreprise"]
            besoin_id: Besoin ID to get entreprise info
        
        Returns:
            List of dicts with email, name, user_id
        """
        recipients = []
        
        # Get besoin to retrieve entreprise
        besoin = await self.db.besoins.find_one({"id": besoin_id})
        if not besoin:
            return recipients
        
        for recipient_type in recipient_types:
            if recipient_type == "jlc_team":
                # Get all JLC admins
                jlc_users = await self.db.users.find({
                    "roles": {"$in": ["admin", "super_admin", "jlc_admin"]}
                }).to_list(length=None)
                
                for user in jlc_users:
                    recipients.append({
                        "email": user.get("email"),
                        "name": user.get("full_name") or user.get("username"),
                        "user_id": user.get("id")
                    })
            
            elif recipient_type == "entreprise":
                # Get entreprise users
                entreprise_users = await self.db.users.find({
                    "entreprise_id": besoin["entreprise_id"],
                    "status": "active"
                }).to_list(length=None)
                
                for user in entreprise_users:
                    recipients.append({
                        "email": user.get("email"),
                        "name": user.get("full_name") or user.get("username"),
                        "user_id": user.get("id")
                    })
            
            elif recipient_type == "responsable_besoin":
                # Get the responsable
                responsable = await self.db.users.find_one({
                    "id": besoin.get("responsable_besoin_id")
                })
                
                if responsable:
                    recipients.append({
                        "email": responsable.get("email"),
                        "name": responsable.get("full_name") or responsable.get("username"),
                        "user_id": responsable.get("id")
                    })
        
        # Remove duplicates
        seen = set()
        unique_recipients = []
        for recipient in recipients:
            if recipient["email"] not in seen:
                seen.add(recipient["email"])
                unique_recipients.append(recipient)
        
        return unique_recipients
    
    def _get_email_template(
        self,
        event_type: str,
        besoin_titre: str,
        entreprise_name: str,
        actor_name: str,
        additional_data: Dict[str, Any]
    ) -> tuple:
        """
        Get email subject and body template
        
        Returns:
            (subject, body) tuple
        """
        templates = {
            "submitted": {
                "subject": f"Nouveau besoin soumis: {besoin_titre}",
                "body": f"""
Bonjour,

Un nouveau besoin vient d'être soumis par {entreprise_name}.

**Détails du besoin:**
- Titre: {besoin_titre}
- Entreprise: {entreprise_name}
- Soumis par: {actor_name}

Veuillez consulter la plateforme pour analyser ce besoin.

Cordialement,
L'équipe JLC
                """
            },
            "analysed": {
                "subject": f"Besoin en cours d'analyse: {besoin_titre}",
                "body": f"""
Bonjour,

Votre besoin "{besoin_titre}" est actuellement en cours d'analyse par notre équipe.

Nous reviendrons vers vous prochainement avec notre proposition.

Cordialement,
L'équipe JLC
                """
            },
            "mission_created": {
                "subject": f"Mission créée pour votre besoin: {besoin_titre}",
                "body": f"""
Bonjour,

Bonne nouvelle ! Une ou plusieurs missions ont été créées pour votre besoin "{besoin_titre}".

Notre équipe va maintenant lancer la recherche de candidats qualifiés.

Cordialement,
L'équipe JLC
                """
            },
            "published": {
                "subject": f"Recherche de candidats lancée: {besoin_titre}",
                "body": f"""
Bonjour,

La recherche de candidats pour "{besoin_titre}" est maintenant active.

Nous vous tiendrons informé des profils correspondants.

Cordialement,
L'équipe JLC
                """
            },
            "closed": {
                "subject": f"Besoin clôturé: {besoin_titre}",
                "body": f"""
Bonjour,

Le besoin "{besoin_titre}" a été clôturé avec succès.

Nous espérons que notre collaboration a été satisfaisante.

Cordialement,
L'équipe JLC
                """
            },
            "comment_added": {
                "subject": f"Nouveau commentaire sur: {besoin_titre}",
                "body": f"""
Bonjour,

{actor_name} a ajouté un commentaire sur le besoin "{besoin_titre}".

Commentaire: {additional_data.get('comment', '')}

Veuillez consulter la plateforme pour répondre.

Cordialement,
L'équipe JLC
                """
            }
        }
        
        template = templates.get(event_type, {
            "subject": f"Mise à jour: {besoin_titre}",
            "body": f"Une mise à jour a été effectuée sur le besoin {besoin_titre}."
        })
        
        return template["subject"], template["body"]
    
    def _get_short_message(
        self,
        event_type: str,
        besoin_titre: str,
        entreprise_name: str
    ) -> str:
        """Get short message for in-app notification"""
        messages = {
            "submitted": f"Nouveau besoin soumis: {besoin_titre}",
            "analysed": f"Besoin en analyse: {besoin_titre}",
            "mission_created": f"Mission créée pour: {besoin_titre}",
            "published": f"Recherche lancée: {besoin_titre}",
            "closed": f"Besoin clôturé: {besoin_titre}",
            "comment_added": f"Nouveau commentaire: {besoin_titre}"
        }
        return messages.get(event_type, f"Mise à jour: {besoin_titre}")
    
    async def _send_email_notification(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body: str,
        besoin_id: str,
        event_type: str
    ) -> None:
        """Send email notification"""
        try:
            await self.email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=body.replace("\n", "<br>"),
                metadata={
                    "besoin_id": besoin_id,
                    "event_type": event_type,
                    "notification_type": "besoin_workflow"
                }
            )
        except Exception as e:
            # Log error but don't fail the workflow
            print(f"Failed to send email to {to_email}: {str(e)}")
    
    async def _create_in_app_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        link: str,
        notification_type: str,
        entity_type: str,
        entity_id: str
    ) -> None:
        """Create in-app notification"""
        notification_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        notification_doc = {
            "id": notification_id,
            "user_id": user_id,
            "title": title,
            "message": message,
            "link": link,
            "type": notification_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "read": False,
            "created_at": now,
        }
        
        await self.notifications_collection.insert_one(notification_doc)
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get notifications for a user"""
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        total = await self.notifications_collection.count_documents(query)
        skip = (page - 1) * page_size
        
        cursor = self.notifications_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        notifications = await cursor.to_list(length=page_size)
        
        # Remove MongoDB _id
        for notification in notifications:
            notification.pop("_id", None)
        
        return {
            "items": notifications,
            "total": total,
            "unread_count": await self.notifications_collection.count_documents({"user_id": user_id, "read": False}),
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        result = await self.notifications_collection.update_one(
            {"id": notification_id, "user_id": user_id},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        result = await self.notifications_collection.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count
