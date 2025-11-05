"""
Service d'envoi d'emails avec support MongoDB, chiffrement et historique
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.services.encryption_service import get_encryption_service
from awana_auth.core.email_config_models import EmailStatus
import re

logger = logging.getLogger(__name__)


class EmailServiceV2:
    """Service d'envoi d'emails avec MongoDB et chiffrement"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db
        self.encryption_service = get_encryption_service()
        self._config_cache = None
        self._cache_time = None
        self.cache_ttl = 300  # 5 minutes
    
    async def _load_config_from_db(self) -> Optional[Dict[str, Any]]:
        """Charger la configuration depuis MongoDB"""
        if not self.db:
            return None
        
        try:
            config = await self.db.email_settings.find_one(
                {"is_active": True},
                sort=[("updated_at", -1)]
            )
            return config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config email: {e}")
            return None
    
    async def _get_config(self) -> Dict[str, Any]:
        """
        Récupérer la configuration email (MongoDB en priorité, puis .env)
        Avec cache de 5 minutes
        """
        # Vérifier le cache
        now = datetime.now(timezone.utc)
        if self._config_cache and self._cache_time:
            if (now.timestamp() - self._cache_time.timestamp()) < self.cache_ttl:
                return self._config_cache
        
        # Charger depuis MongoDB
        db_config = await self._load_config_from_db()
        
        if db_config and db_config.get('enabled', False):
            # Déchiffrer le mot de passe
            encrypted_password = db_config.get('smtp_password_encrypted', '')
            smtp_password = ''
            
            if encrypted_password:
                try:
                    smtp_password = self.encryption_service.decrypt(encrypted_password)
                except Exception as e:
                    logger.error(f"Erreur lors du déchiffrement du mot de passe SMTP: {e}")
            
            config = {
                'enabled': db_config.get('enabled', False),
                'smtp_host': db_config.get('smtp_host', 'localhost'),
                'smtp_port': db_config.get('smtp_port', 587),
                'smtp_user': db_config.get('smtp_user', ''),
                'smtp_password': smtp_password,
                'smtp_use_tls': db_config.get('smtp_use_tls', True),
                'from_email': db_config.get('from_email', 'noreply@jlc.com'),
                'from_name': db_config.get('from_name', 'JLC Application'),
                'admin_emails': db_config.get('admin_emails', [])
            }
        else:
            # Fallback sur les variables d'environnement
            admin_emails_str = os.getenv('ADMIN_NOTIFICATION_EMAILS', '')
            admin_emails = [email.strip() for email in admin_emails_str.split(',') if email.strip()]
            
            config = {
                'enabled': os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'false').lower() == 'true',
                'smtp_host': os.getenv('SMTP_HOST', 'localhost'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'smtp_user': os.getenv('SMTP_USER', ''),
                'smtp_password': os.getenv('SMTP_PASSWORD', ''),
                'smtp_use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
                'from_email': os.getenv('SMTP_FROM_EMAIL', 'noreply@jlc.com'),
                'from_name': os.getenv('SMTP_FROM_NAME', 'JLC Application'),
                'admin_emails': admin_emails
            }
        
        # Mettre en cache
        self._config_cache = config
        self._cache_time = now
        
        return config
    
    async def is_configured(self) -> bool:
        """Vérifier si le service email est configuré"""
        config = await self._get_config()
        return (
            config.get('enabled', False) and
            bool(config.get('smtp_host')) and
            bool(config.get('smtp_user')) and
            bool(config.get('smtp_password')) and
            len(config.get('admin_emails', [])) > 0
        )
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        sent_by: str = "system",
        template_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Envoyer un email et enregistrer dans l'historique
        
        Args:
            to_emails: Liste des destinataires
            subject: Sujet de l'email
            html_content: Contenu HTML
            text_content: Contenu texte alternatif
            sent_by: Utilisateur qui a déclenché l'envoi
            template_name: Nom du template utilisé
            metadata: Métadonnées supplémentaires
            
        Returns:
            Dict avec success (bool), message (str), sent_to (list)
        """
        config = await self._get_config()
        
        if not await self.is_configured():
            logger.warning("Email service not configured. Email not sent.")
            await self._save_to_history(
                to_emails=to_emails,
                subject=subject,
                template_name=template_name,
                status=EmailStatus.FAILED,
                error_message="Service email non configuré",
                sent_by=sent_by,
                metadata=metadata
            )
            return {
                "success": False,
                "message": "Email service not configured",
                "sent_to": []
            }
        
        if not to_emails:
            return {
                "success": False,
                "message": "No recipients specified",
                "sent_to": []
            }
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{config['from_name']} <{config['from_email']}>"
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Ajouter version texte si fournie
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            # Ajouter version HTML
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # Se connecter au serveur SMTP
            if config['smtp_use_tls']:
                server = smtplib.SMTP(config['smtp_host'], config['smtp_port'])
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'])
            
            # Authentification
            if config['smtp_user'] and config['smtp_password']:
                server.login(config['smtp_user'], config['smtp_password'])
            
            # Envoyer
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            
            # Enregistrer dans l'historique
            await self._save_to_history(
                to_emails=to_emails,
                subject=subject,
                template_name=template_name,
                status=EmailStatus.SENT,
                sent_by=sent_by,
                metadata=metadata
            )
            
            return {
                "success": True,
                "message": f"Email sent to {len(to_emails)} recipients",
                "sent_to": to_emails
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            
            # Enregistrer l'échec dans l'historique
            await self._save_to_history(
                to_emails=to_emails,
                subject=subject,
                template_name=template_name,
                status=EmailStatus.FAILED,
                error_message=str(e),
                sent_by=sent_by,
                metadata=metadata
            )
            
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "sent_to": []
            }
    
    async def _save_to_history(
        self,
        to_emails: List[str],
        subject: str,
        template_name: Optional[str],
        status: EmailStatus,
        sent_by: str,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Enregistrer l'envoi dans l'historique"""
        if not self.db:
            return
        
        try:
            history_entry = {
                "id": str(uuid.uuid4()),
                "to_emails": to_emails,
                "subject": subject,
                "template_name": template_name,
                "status": status.value,
                "sent_at": datetime.now(timezone.utc) if status == EmailStatus.SENT else None,
                "error_message": error_message,
                "sent_by": sent_by,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.db.email_history.insert_one(history_entry)
            logger.debug(f"Email history saved: {history_entry['id']}")
        except Exception as e:
            logger.error(f"Failed to save email history: {e}")
    
    async def render_template(self, template_html: str, variables: Dict[str, Any]) -> str:
        """
        Rendre un template avec les variables
        
        Args:
            template_html: Template HTML avec {{variable}}
            variables: Dict des variables à remplacer
            
        Returns:
            HTML rendu
        """
        rendered = template_html
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    async def send_rollback_notification(
        self,
        actor_name: str,
        version_from: str,
        version_to: str,
        reason: str,
        rollback_time: datetime,
        changes_summary: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Envoyer une notification de rollback aux admins"""
        config = await self._get_config()
        
        if not await self.is_configured():
            return {
                "success": False,
                "message": "Email notifications not configured",
                "sent_to": []
            }
        
        subject = f"⚠️ Configuration Rollback Effectué - {version_to}"
        
        # Charger le template depuis la base de données si disponible
        template_html = await self._get_template_content("rollback")
        
        if template_html:
            # Utiliser le template personnalisé
            variables = {
                "actor_name": actor_name,
                "version_from": version_from,
                "version_to": version_to,
                "reason": reason,
                "rollback_time": rollback_time.strftime('%d/%m/%Y %H:%M:%S UTC'),
                "changes_added": changes_summary.get('added', 0) if changes_summary else 0,
                "changes_modified": changes_summary.get('modified', 0) if changes_summary else 0,
                "changes_removed": changes_summary.get('removed', 0) if changes_summary else 0
            }
            html_content = await self.render_template(template_html, variables)
        else:
            # Template par défaut
            html_content = self._generate_rollback_email_html(
                actor_name=actor_name,
                version_from=version_from,
                version_to=version_to,
                reason=reason,
                rollback_time=rollback_time,
                changes_summary=changes_summary
            )
        
        text_content = self._generate_rollback_email_text(
            actor_name=actor_name,
            version_from=version_from,
            version_to=version_to,
            reason=reason,
            rollback_time=rollback_time
        )
        
        return await self.send_email(
            to_emails=config.get('admin_emails', []),
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            sent_by=actor_name,
            template_name="rollback",
            metadata={
                "version_from": version_from,
                "version_to": version_to,
                "reason": reason
            }
        )
    
    async def _get_template_content(self, template_type: str) -> Optional[str]:
        """Récupérer le contenu d'un template depuis la base de données"""
        if not self.db:
            return None
        
        try:
            template = await self.db.email_templates.find_one({
                "type": template_type,
                "is_active": True
            })
            return template.get('html_content') if template else None
        except Exception as e:
            logger.error(f"Failed to load template {template_type}: {e}")
            return None
    
    def _generate_rollback_email_html(
        self,
        actor_name: str,
        version_from: str,
        version_to: str,
        reason: str,
        rollback_time: datetime,
        changes_summary: Optional[Dict[str, int]] = None
    ) -> str:
        """Générer le HTML par défaut pour les notifications de rollback"""
        changes_html = ""
        if changes_summary:
            changes_html = f"""
            <div style="background: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #374151; margin: 0 0 10px 0;">📊 Résumé des Changements</h3>
                <ul style="color: #6b7280; margin: 0; padding-left: 20px;">
                    <li><strong>Références ajoutées:</strong> {changes_summary.get('added', 0)}</li>
                    <li><strong>Références modifiées:</strong> {changes_summary.get('modified', 0)}</li>
                    <li><strong>Références supprimées:</strong> {changes_summary.get('removed', 0)}</li>
                </ul>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px; background: #f3f4f6;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #dc2626 100%); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="color: white; margin: 0;">⚠️ Configuration Rollback Effectué</h2>
                </div>
                
                <p style="color: #374151; font-size: 16px;">Bonjour,</p>
                
                <p style="color: #374151;">Un rollback de configuration a été effectué sur l'application JLC.</p>
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; margin: 20px 0;">
                    <h3 style="color: #1e40af; margin: 0 0 15px 0;">📋 Détails du Rollback</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Version précédente:</td>
                            <td style="padding: 8px 0; color: #374151;">{version_from}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Version cible:</td>
                            <td style="padding: 8px 0; color: #374151; font-weight: bold;">{version_to}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Raison:</td>
                            <td style="padding: 8px 0; color: #374151;">{reason}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Date:</td>
                            <td style="padding: 8px 0; color: #374151;">{rollback_time.strftime('%d/%m/%Y %H:%M:%S UTC')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Effectué par:</td>
                            <td style="padding: 8px 0; color: #374151;">{actor_name}</td>
                        </tr>
                    </table>
                </div>
                
                {changes_html}
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                    <p style="color: #92400e; margin: 0; font-size: 14px;">
                        ⚡ Cette opération a été exécutée automatiquement et peut avoir un impact sur les utilisateurs et le système.
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
                    JLC Application - Notification automatique de rollback<br>
                    Pour toute question, contactez l'équipe technique
                </p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_rollback_email_text(
        self,
        actor_name: str,
        version_from: str,
        version_to: str,
        reason: str,
        rollback_time: datetime
    ) -> str:
        """Générer la version texte pour les notifications de rollback"""
        return f"""
Configuration Rollback Effectué
═══════════════════════════════

Un rollback de configuration a été effectué sur l'application JLC.

Détails du Rollback
-------------------
Version précédente: {version_from}
Version cible: {version_to}
Raison: {reason}
Date: {rollback_time.strftime('%d/%m/%Y %H:%M:%S UTC')}
Effectué par: {actor_name}

Cette opération a été exécutée automatiquement et peut avoir un impact sur les utilisateurs.

---
JLC Application - Notification automatique
        """
    
    def clear_cache(self):
        """Vider le cache de configuration"""
        self._config_cache = None
        self._cache_time = None


# Instance singleton (sera initialisée avec la base de données)
_email_service = None


def init_email_service(db: AsyncIOMotorDatabase):
    """Initialiser le service email avec la base de données"""
    global _email_service
    _email_service = EmailServiceV2(db)
    return _email_service


def get_email_service_v2() -> EmailServiceV2:
    """Récupérer l'instance du service email"""
    if _email_service is None:
        # Retourner une instance sans DB pour les cas où elle n'est pas encore initialisée
        return EmailServiceV2(None)
    return _email_service
