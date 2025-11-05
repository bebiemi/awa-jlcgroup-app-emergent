"""
Service d'envoi d'emails avec support SMTP et templates HTML
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service d'envoi d'emails"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.from_email = os.getenv('SMTP_FROM_EMAIL', 'noreply@jlc.com')
        self.from_name = os.getenv('SMTP_FROM_NAME', 'JLC Application')
        self.enabled = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
        
        # Liste des admins à notifier (séparés par virgule)
        self.admin_emails = os.getenv('ADMIN_NOTIFICATION_EMAILS', '').split(',')
        self.admin_emails = [email.strip() for email in self.admin_emails if email.strip()]
    
    def is_configured(self) -> bool:
        """Vérifier si le service email est configuré"""
        return (
            self.enabled and
            bool(self.smtp_host) and
            bool(self.smtp_user) and
            bool(self.smtp_password) and
            len(self.admin_emails) > 0
        )
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envoyer un email
        
        Returns:
            Dict avec success (bool) et message (str)
        """
        if not self.is_configured():
            logger.warning("Email service not configured. Email not sent.")
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
            msg['From'] = f"{self.from_name} <{self.from_email}>"
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
            if self.smtp_use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            # Authentification
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            # Envoyer
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            
            return {
                "success": True,
                "message": f"Email sent to {len(to_emails)} recipients",
                "sent_to": to_emails
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "sent_to": []
            }
    
    def send_rollback_notification(
        self,
        actor_name: str,
        version_from: str,
        version_to: str,
        reason: str,
        rollback_time: datetime,
        changes_summary: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Envoyer une notification de rollback aux admins
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Email notifications not configured",
                "sent_to": []
            }
        
        subject = f"⚠️ Configuration Rollback Effectué - {version_to}"
        
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
        
        return self.send_email(
            to_emails=self.admin_emails,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def send_feature_flag_alert(
        self,
        flag_key: str,
        action: str,
        actor_name: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envoyer une alerte pour un changement critique de feature flag
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Email notifications not configured",
                "sent_to": []
            }
        
        subject = f"🚩 Feature Flag {action}: {flag_key}"
        
        html_content = self._generate_feature_flag_email_html(
            flag_key=flag_key,
            action=action,
            actor_name=actor_name,
            details=details
        )
        
        text_content = f"""
Feature Flag {action}

Flag: {flag_key}
Action: {action}
Par: {actor_name}
Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

Détails: {details}
        """
        
        return self.send_email(
            to_emails=self.admin_emails,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def _generate_rollback_email_html(
        self,
        actor_name: str,
        version_from: str,
        version_to: str,
        reason: str,
        rollback_time: datetime,
        changes_summary: Optional[Dict[str, int]] = None
    ) -> str:
        """Générer le HTML pour l'email de rollback"""
        
        changes_html = ""
        if changes_summary:
            changes_html = f"""
            <div style="margin: 20px 0; padding: 15px; background-color: #f3f4f6; border-radius: 8px;">
                <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #374151;">Résumé des changements</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                    <div style="text-align: center; padding: 10px; background: #dcfce7; border-radius: 6px;">
                        <div style="font-size: 24px; font-weight: bold; color: #16a34a;">{changes_summary.get('added', 0)}</div>
                        <div style="font-size: 12px; color: #15803d;">Ajoutés</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: #fed7aa; border-radius: 6px;">
                        <div style="font-size: 24px; font-weight: bold; color: #ea580c;">{changes_summary.get('modified', 0)}</div>
                        <div style="font-size: 12px; color: #c2410c;">Modifiés</div>
                    </div>
                    <div style="text-align: center; padding: 10px; background: #fecaca; border-radius: 6px;">
                        <div style="font-size: 24px; font-weight: bold; color: #dc2626;">{changes_summary.get('removed', 0)}</div>
                        <div style="font-size: 12px; color: #b91c1c;">Supprimés</div>
                    </div>
                </div>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">⚠️ Configuration Rollback</h1>
        </div>
        
        <!-- Content -->
        <div style="padding: 30px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
            <!-- Alert Box -->
            <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <p style="margin: 0; color: #92400e; font-weight: 600;">
                    Un rollback de configuration a été effectué sur l'application JLC.
                </p>
            </div>
            
            <!-- Details -->
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #111827;">Détails du Rollback</h2>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; width: 40%;">
                            <strong>Effectué par</strong>
                        </td>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px;">
                            {actor_name}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
                            <strong>Date et heure</strong>
                        </td>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px;">
                            {rollback_time.strftime('%d/%m/%Y à %H:%M:%S UTC')}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
                            <strong>Version source</strong>
                        </td>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px;">
                            <code style="background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-family: monospace;">{version_from}</code>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
                            <strong>Version cible</strong>
                        </td>
                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb; color: #111827; font-size: 14px;">
                            <code style="background: #dbeafe; padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #1e40af;">{version_to}</code>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0; color: #6b7280; font-size: 14px; vertical-align: top;">
                            <strong>Raison</strong>
                        </td>
                        <td style="padding: 10px 0; color: #111827; font-size: 14px;">
                            {reason}
                        </td>
                    </tr>
                </table>
            </div>
            
            {changes_html}
            
            <!-- Actions -->
            <div style="background-color: #eff6ff; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <p style="margin: 0 0 10px 0; color: #1e40af; font-size: 14px; font-weight: 600;">
                    📋 Actions recommandées
                </p>
                <ul style="margin: 0; padding-left: 20px; color: #1e3a8a; font-size: 13px;">
                    <li style="margin-bottom: 5px;">Vérifier que les services fonctionnent correctement</li>
                    <li style="margin-bottom: 5px;">Consulter les logs d'application</li>
                    <li style="margin-bottom: 5px;">Informer l'équipe si nécessaire</li>
                </ul>
            </div>
            
            <!-- Footer -->
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center;">
                <p style="margin: 0; color: #6b7280; font-size: 12px;">
                    Cet email a été envoyé automatiquement par le système JLC.<br>
                    Pour plus d'informations, connectez-vous à l'interface d'administration.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_rollback_email_text(
        self,
        actor_name: str,
        version_from: str,
        version_to: str,
        reason: str,
        rollback_time: datetime
    ) -> str:
        """Générer la version texte de l'email"""
        return f"""
⚠️ CONFIGURATION ROLLBACK EFFECTUÉ

Un rollback de configuration a été effectué sur l'application JLC.

DÉTAILS:
--------
Effectué par: {actor_name}
Date et heure: {rollback_time.strftime('%d/%m/%Y à %H:%M:%S UTC')}
Version source: {version_from}
Version cible: {version_to}
Raison: {reason}

ACTIONS RECOMMANDÉES:
--------------------
- Vérifier que les services fonctionnent correctement
- Consulter les logs d'application
- Informer l'équipe si nécessaire

---
Cet email a été envoyé automatiquement par le système JLC.
        """
    
    def _generate_feature_flag_email_html(
        self,
        flag_key: str,
        action: str,
        actor_name: str,
        details: Dict[str, Any]
    ) -> str:
        """Générer HTML pour alerte feature flag"""
        
        action_colors = {
            "CREATED": ("#10b981", "#d1fae5"),
            "UPDATED": ("#f59e0b", "#fef3c7"),
            "DELETED": ("#ef4444", "#fee2e2"),
            "ROLLOUT": ("#3b82f6", "#dbeafe")
        }
        
        color, bg_color = action_colors.get(action.upper(), ("#6b7280", "#f3f4f6"))
        
        details_html = "<ul style='margin: 10px 0; padding-left: 20px; color: #374151;'>"
        for key, value in details.items():
            details_html += f"<li style='margin: 5px 0;'><strong>{key}:</strong> {value}</li>"
        details_html += "</ul>"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: {bg_color}; border-left: 4px solid {color}; padding: 20px; border-radius: 8px;">
            <h2 style="margin: 0 0 15px 0; color: {color};">🚩 Feature Flag {action}</h2>
            <p style="margin: 0 0 10px 0; color: #111827;"><strong>Flag:</strong> <code>{flag_key}</code></p>
            <p style="margin: 0 0 10px 0; color: #111827;"><strong>Par:</strong> {actor_name}</p>
            <p style="margin: 0 0 15px 0; color: #111827;"><strong>Date:</strong> {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S UTC')}</p>
            <div style="background: white; padding: 15px; border-radius: 6px;">
                <strong style="color: #111827;">Détails:</strong>
                {details_html}
            </div>
        </div>
    </div>
</body>
</html>
        """


# Instance globale
_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Obtenir l'instance du service email (singleton)"""
    global _email_service_instance
    
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    
    return _email_service_instance
