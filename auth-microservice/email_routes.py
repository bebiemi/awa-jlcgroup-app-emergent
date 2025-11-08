"""
Routes pour gérer les notifications email
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List
from awana_auth.core.models import User
from awana_auth.core.dependencies import get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.services.email_service import get_email_service
from datetime import datetime, timezone


router = APIRouter(prefix="/api/emails", tags=["emails"])


class TestEmailRequest(BaseModel):
    """Requête pour envoyer un email de test"""
    to_emails: List[EmailStr]
    subject: str = "Email de test JLC"
    message: str = "Ceci est un email de test depuis l'application JLC."


@router.get("/config")
async def get_email_config(
    current_user: User = Depends(require_permission("emails.configure"))
):
    """
    Obtenir la configuration email (sans mot de passe)
    Réservé aux super-admins
    """
    email_service = get_email_service()
    
    return {
        "enabled": email_service.enabled,
        "configured": email_service.is_configured(),
        "smtp_host": email_service.smtp_host,
        "smtp_port": email_service.smtp_port,
        "smtp_user": email_service.smtp_user if email_service.smtp_user else None,
        "smtp_use_tls": email_service.smtp_use_tls,
        "from_email": email_service.from_email,
        "from_name": email_service.from_name,
        "admin_emails": email_service.admin_emails,
        "admin_count": len(email_service.admin_emails)
    }


@router.post("/test", dependencies=[Depends(require_super_admin)])
async def send_test_email(
    request: TestEmailRequest,
    current_user: User = Depends(require_permission("emails.configure"))
):
    """
    Envoyer un email de test
    Réservé aux super-admins
    """
    email_service = get_email_service()
    
    if not email_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service email non configuré. Vérifiez les variables d'environnement."
        )
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #f9fafb; padding: 30px; border-radius: 10px;">
            <h2 style="color: #667eea; margin-top: 0;">✉️ Email de Test JLC</h2>
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p style="color: #374151; margin: 0 0 15px 0;">{request.message}</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 13px; margin: 5px 0;">
                    <strong>Envoyé par:</strong> {current_user.full_name or current_user.username}
                </p>
                <p style="color: #6b7280; font-size: 13px; margin: 5px 0;">
                    <strong>Date:</strong> {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S UTC')}
                </p>
            </div>
            <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 20px 0 0 0;">
                Si vous recevez cet email, la configuration SMTP est correcte ✅
            </p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Email de Test JLC
==================

{request.message}

Envoyé par: {current_user.full_name or current_user.username}
Date: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S UTC')}

Si vous recevez cet email, la configuration SMTP est correcte ✅
    """
    
    result = email_service.send_email(
        to_emails=request.to_emails,
        subject=request.subject,
        html_content=html_content,
        text_content=text_content
    )
    
    if result["success"]:
        return {
            "message": "Email de test envoyé avec succès",
            "sent_to": result["sent_to"],
            "count": len(result["sent_to"])
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Échec de l'envoi: {result['message']}"
        )


@router.post("/test-rollback-notification", dependencies=[Depends(require_super_admin)])
async def send_test_rollback_notification(
    current_user: User = Depends(require_permission("emails.configure"))
):
    """
    Envoyer une notification de rollback de test
    Réservé aux super-admins
    """
    email_service = get_email_service()
    
    if not email_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service email non configuré"
        )
    
    result = email_service.send_rollback_notification(
        actor_name=current_user.full_name or current_user.username,
        version_from="v20251105.120000",
        version_to="v20251104.180000",
        reason="Test de notification email de rollback",
        rollback_time=datetime.now(timezone.utc),
        changes_summary={
            "added": 5,
            "modified": 3,
            "removed": 2
        }
    )
    
    if result["success"]:
        return {
            "message": "Notification de test envoyée",
            "sent_to": result["sent_to"],
            "count": len(result["sent_to"])
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Échec de l'envoi: {result['message']}"
        )


@router.get("/status")
async def get_email_status(
    current_user: User = Depends(get_current_user)
):
    """
    Vérifier le statut du service email
    Accessible aux admins et super-admins
    """
    if "admin" not in current_user.roles and "super_admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : admin requis"
        )
    
    email_service = get_email_service()
    
    return {
        "enabled": email_service.enabled,
        "configured": email_service.is_configured(),
        "smtp_configured": bool(email_service.smtp_host and email_service.smtp_user),
        "recipients_configured": len(email_service.admin_emails) > 0,
        "recipients_count": len(email_service.admin_emails),
        "status": "operational" if email_service.is_configured() else "not_configured"
    }
