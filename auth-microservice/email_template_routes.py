"""
Routes pour la gestion des templates d'email
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.core.email_config_models import (
    EmailTemplate,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateType
)
from datetime import datetime, timezone
import uuid
from typing import List, Optional


router = APIRouter(prefix="/api/emails/templates", tags=["email-templates"])


def require_super_admin(current_user: User = Depends(get_current_user)):
    """Vérifier que l'utilisateur est super admin"""
    if "super_admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : super admin requis"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)):
    """Vérifier que l'utilisateur est admin ou super admin"""
    if "admin" not in current_user.roles and "super_admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : admin requis"
        )
    return current_user


@router.get("")
async def list_templates(
    template_type: Optional[EmailTemplateType] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lister tous les templates d'email
    Accessible aux admins et super-admins
    """
    query_filter = {}
    
    if template_type:
        query_filter["type"] = template_type.value
    
    if is_active is not None:
        query_filter["is_active"] = is_active
    
    templates = await db.email_templates.find(query_filter)\
        .sort("created_at", -1)\
        .to_list(length=None)
    
    return {
        "templates": templates,
        "count": len(templates)
    }


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer un template par ID
    Accessible aux admins et super-admins
    """
    template = await db.email_templates.find_one({"id": template_id})
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    
    return template


@router.post("")
async def create_template(
    template_data: EmailTemplateCreate,
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un nouveau template d'email
    Réservé aux super-admins
    """
    # Vérifier si un template avec ce nom existe déjà
    existing = await db.email_templates.find_one({"name": template_data.name})
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un template avec ce nom existe déjà"
        )
    
    new_template = {
        "id": str(uuid.uuid4()),
        "name": template_data.name,
        "type": template_data.type.value,
        "subject": template_data.subject,
        "html_content": template_data.html_content,
        "text_content": template_data.text_content,
        "variables": template_data.variables,
        "is_active": True,
        "is_system": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": current_user.username
    }
    
    await db.email_templates.insert_one(new_template)
    
    return {
        "message": "Template créé avec succès",
        "template": new_template
    }


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    template_update: EmailTemplateUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un template d'email
    Réservé aux super-admins
    """
    template = await db.email_templates.find_one({"id": template_id})
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    
    # Ne pas permettre la modification des templates système
    if template.get("is_system", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les templates système ne peuvent pas être modifiés"
        )
    
    # Construire les mises à jour
    update_data = {"updated_at": datetime.now(timezone.utc)}
    
    if template_update.name is not None:
        update_data["name"] = template_update.name
    
    if template_update.subject is not None:
        update_data["subject"] = template_update.subject
    
    if template_update.html_content is not None:
        update_data["html_content"] = template_update.html_content
    
    if template_update.text_content is not None:
        update_data["text_content"] = template_update.text_content
    
    if template_update.variables is not None:
        update_data["variables"] = template_update.variables
    
    if template_update.is_active is not None:
        update_data["is_active"] = template_update.is_active
    
    await db.email_templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    # Récupérer le template mis à jour
    updated_template = await db.email_templates.find_one({"id": template_id})
    
    return {
        "message": "Template mis à jour avec succès",
        "template": updated_template
    }


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Supprimer un template d'email
    Réservé aux super-admins
    """
    template = await db.email_templates.find_one({"id": template_id})
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    
    # Ne pas permettre la suppression des templates système
    if template.get("is_system", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les templates système ne peuvent pas être supprimés"
        )
    
    await db.email_templates.delete_one({"id": template_id})
    
    return {
        "message": "Template supprimé avec succès"
    }


@router.post("/{template_id}/preview")
async def preview_template(
    template_id: str,
    variables: dict,
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Prévisualiser un template avec des variables
    Accessible aux admins et super-admins
    """
    template = await db.email_templates.find_one({"id": template_id})
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    
    # Remplacer les variables dans le contenu
    html_content = template.get("html_content", "")
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        html_content = html_content.replace(placeholder, str(value))
    
    return {
        "preview": html_content,
        "subject": template.get("subject", ""),
        "variables_used": list(variables.keys())
    }


@router.post("/init-defaults")
async def initialize_default_templates(
    current_user: User = Depends(require_super_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Initialiser les templates par défaut
    Réservé aux super-admins
    """
    # Vérifier si les templates existent déjà
    existing_count = await db.email_templates.count_documents({"is_system": True})
    
    if existing_count > 0:
        return {
            "message": "Les templates par défaut existent déjà",
            "count": existing_count
        }
    
    # Template de rollback
    rollback_template = {
        "id": str(uuid.uuid4()),
        "name": "Notification de Rollback",
        "type": EmailTemplateType.ROLLBACK.value,
        "subject": "⚠️ Configuration Rollback Effectué - {{version_to}}",
        "html_content": """
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
                    <td style="padding: 8px 0; color: #374151;">{{version_from}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Version cible:</td>
                    <td style="padding: 8px 0; color: #374151; font-weight: bold;">{{version_to}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Raison:</td>
                    <td style="padding: 8px 0; color: #374151;">{{reason}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Date:</td>
                    <td style="padding: 8px 0; color: #374151;">{{rollback_time}}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #6b7280; font-weight: bold;">Effectué par:</td>
                    <td style="padding: 8px 0; color: #374151;">{{actor_name}}</td>
                </tr>
            </table>
        </div>
        
        <div style="background: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #374151; margin: 0 0 10px 0;">📊 Résumé des Changements</h3>
            <ul style="color: #6b7280; margin: 0; padding-left: 20px;">
                <li><strong>Références ajoutées:</strong> {{changes_added}}</li>
                <li><strong>Références modifiées:</strong> {{changes_modified}}</li>
                <li><strong>Références supprimées:</strong> {{changes_removed}}</li>
            </ul>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        
        <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">
            JLC Application - Notification automatique
        </p>
    </div>
</body>
</html>
        """,
        "text_content": "Configuration Rollback effectué. Version: {{version_to}}. Par: {{actor_name}}. Raison: {{reason}}",
        "variables": ["actor_name", "version_from", "version_to", "reason", "rollback_time", "changes_added", "changes_modified", "changes_removed"],
        "is_active": True,
        "is_system": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": current_user.username
    }
    
    await db.email_templates.insert_one(rollback_template)
    
    return {
        "message": "Templates par défaut créés avec succès",
        "count": 1
    }
