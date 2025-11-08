"""
Routes pour la gestion de la configuration email
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.models import User
from awana_auth.core.email_config_models import (
    EmailConfigUpdate,
    EmailConfigResponse,
    EmailTestRequest
)
from awana_auth.services.encryption_service import get_encryption_service
from awana_auth.services.email_service_v2 import get_email_service_v2
from datetime import datetime, timezone
import uuid
import smtplib
from email.mime.text import MIMEText


router = APIRouter(prefix="/api/emails", tags=["email-settings"])


@router.get("/settings", response_model=EmailConfigResponse)
async def get_email_settings(
    current_user: User = Depends(require_permission("emails.read_config")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer la configuration email actuelle
    Accessible aux admins et super-admins (sans le mot de passe)
    """
    # Récupérer la config depuis MongoDB
    config = await db.email_settings.find_one(
        {"is_active": True},
        sort=[("updated_at", -1)]
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune configuration email trouvée. Veuillez en créer une."
        )
    
    # Retourner sans le mot de passe
    return EmailConfigResponse(
        id=config["id"],
        enabled=config.get("enabled", False),
        provider=config.get("provider", "custom"),
        smtp_host=config.get("smtp_host", ""),
        smtp_port=config.get("smtp_port", 587),
        smtp_user=config.get("smtp_user", ""),
        smtp_use_tls=config.get("smtp_use_tls", True),
        from_email=config.get("from_email", ""),
        from_name=config.get("from_name", "JLC Application"),
        admin_emails=config.get("admin_emails", []),
        created_at=config.get("created_at"),
        updated_at=config.get("updated_at"),
        updated_by=config.get("updated_by", "system"),
        is_configured=True
    )


@router.put("/settings")
async def update_email_settings(
    config_update: EmailConfigUpdate,
    current_user: User = Depends(require_permission("emails.configure")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour la configuration email
    Réservé aux super-admins
    """
    encryption_service = get_encryption_service()
    
    # Chiffrer le mot de passe
    encrypted_password = encryption_service.encrypt(config_update.smtp_password)
    
    # Désactiver l'ancienne config
    await db.email_settings.update_many(
        {"is_active": True},
        {"$set": {"is_active": False}}
    )
    
    # Créer la nouvelle config
    new_config = {
        "id": str(uuid.uuid4()),
        "enabled": config_update.enabled,
        "provider": config_update.provider.value,
        "smtp_host": config_update.smtp_host,
        "smtp_port": config_update.smtp_port,
        "smtp_user": config_update.smtp_user,
        "smtp_password_encrypted": encrypted_password,
        "smtp_use_tls": config_update.smtp_use_tls,
        "from_email": config_update.from_email,
        "from_name": config_update.from_name,
        "admin_emails": config_update.admin_emails,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "updated_by": current_user.username
    }
    
    await db.email_settings.insert_one(new_config)
    
    # Vider le cache du service email
    email_service = get_email_service_v2()
    email_service.clear_cache()
    
    return {
        "message": "Configuration email mise à jour avec succès",
        "id": new_config["id"],
        "enabled": new_config["enabled"]
    }


@router.post("/settings/test")
async def test_email_config(
    test_request: EmailTestRequest,
    current_user: User = Depends(require_permission("emails.test"))
):
    """
    Tester une configuration email avant de l'enregistrer
    Réservé aux super-admins
    """
    try:
        # Créer un message de test
        msg = MIMEText("Ceci est un email de test depuis JLC Application.", 'plain', 'utf-8')
        msg['Subject'] = "Test de configuration SMTP"
        msg['From'] = f"JLC Application <{test_request.from_email}>"
        msg['To'] = test_request.to_email
        
        # Se connecter au serveur SMTP
        if test_request.smtp_use_tls:
            server = smtplib.SMTP(test_request.smtp_host, test_request.smtp_port, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(test_request.smtp_host, test_request.smtp_port, timeout=10)
        
        # Authentification
        if test_request.smtp_user and test_request.smtp_password:
            server.login(test_request.smtp_user, test_request.smtp_password)
        
        # Envoyer
        server.send_message(msg)
        server.quit()
        
        return {
            "success": True,
            "message": f"Email de test envoyé avec succès à {test_request.to_email}"
        }
        
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification SMTP échouée. Vérifiez l'utilisateur et le mot de passe."
        )
    except smtplib.SMTPConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de se connecter au serveur SMTP. Vérifiez l'hôte et le port."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du test: {str(e)}"
        )


@router.delete("/settings")
async def delete_email_settings(
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Désactiver la configuration email
    Réservé aux super-admins
    """
    result = await db.email_settings.update_many(
        {"is_active": True},
        {"$set": {"is_active": False}}
    )
    
    # Vider le cache
    email_service = get_email_service_v2()
    email_service.clear_cache()
    
    return {
        "message": "Configuration email désactivée",
        "count": result.modified_count
    }
