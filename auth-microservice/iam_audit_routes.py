"""
Routes API pour l'Audit Trail IAM
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.services.iam_audit_service import (
    IAMAuditService,
    AuditEntry,
    AuditAction,
    AuditSeverity
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iam-audit", tags=["IAM Audit"])


class AuditSearchRequest(BaseModel):
    """Requête de recherche dans l'audit trail"""
    action: Optional[str] = None
    actor_id: Optional[str] = None
    target_type: Optional[str] = None
    severity: Optional[str] = None
    result: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None


def get_audit_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> IAMAuditService:
    """Dépendance pour obtenir le service d'audit"""
    return IAMAuditService(db)


def require_admin(current_user: User = Depends(get_current_user)):
    """Vérifier que l'utilisateur est admin"""
    normalized_roles = [r.lower() for r in current_user.roles]
    if "admin" not in normalized_roles and "super_admin" not in normalized_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


@router.get("/user/{user_id}", response_model=List[AuditEntry])
async def get_user_audit_trail(
    user_id: str,
    limit: int = Query(100, le=500),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Récupérer l'audit trail d'un utilisateur spécifique
    
    **Permissions:**
    - Utilisateur peut voir son propre audit trail
    - Admin peut voir tous les audit trails
    """
    # Vérifier les permissions
    if user_id != current_user.id and "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que votre propre historique"
        )
    
    entries = await service.get_user_actions(
        user_id=user_id,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    
    return entries


@router.get("/actions/{action_type}", response_model=List[AuditEntry])
async def get_actions_by_type(
    action_type: str,
    limit: int = Query(100, le=500),
    start_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Récupérer toutes les actions d'un type spécifique
    
    **Permissions requises:** Admin
    
    **Exemples d'actions:**
    - `profile_created`
    - `permission_granted`
    - `temp_permission_granted`
    - `permission_denied`
    """
    try:
        action = AuditAction(action_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type d'action invalide: {action_type}"
        )
    
    entries = await service.get_actions_by_type(
        action=action,
        limit=limit,
        start_date=start_date
    )
    
    return entries


@router.get("/failed-actions", response_model=List[AuditEntry])
async def get_failed_actions(
    limit: int = Query(100, le=500),
    hours_back: int = Query(24, le=168),  # Max 1 semaine
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Récupérer toutes les actions échouées récentes
    
    **Permissions requises:** Admin
    
    **Utilisation:** Monitoring et détection d'anomalies
    """
    entries = await service.get_failed_actions(
        limit=limit,
        hours_back=hours_back
    )
    
    return entries


@router.get("/security-alerts", response_model=List[AuditEntry])
async def get_security_alerts(
    hours_back: int = Query(24, le=168),
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Récupérer les alertes de sécurité (actions critiques/erreurs)
    
    **Permissions requises:** Admin
    
    **Utilisation:** Dashboard de sécurité et monitoring en temps réel
    """
    alerts = await service.get_security_alerts(hours_back=hours_back)
    return alerts


@router.post("/search")
async def search_audit_trail(
    request: AuditSearchRequest,
    limit: int = Query(100, le=500),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Recherche avancée dans l'audit trail
    
    **Permissions requises:** Admin
    
    **Filtres disponibles:**
    - `action`: Type d'action
    - `actor_id`: ID de l'acteur
    - `target_type`: Type de cible
    - `severity`: Niveau de sévérité
    - `result`: Résultat (success/failure/denied)
    - `start_date` / `end_date`: Période
    - `search_text`: Recherche texte libre
    """
    filters = request.dict(exclude_none=True)
    
    results = await service.search_audit_trail(
        filters=filters,
        limit=limit,
        skip=skip
    )
    
    return results


@router.get("/statistics")
async def get_audit_statistics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Récupérer les statistiques d'audit
    
    **Permissions requises:** Admin
    
    **Statistiques retournées:**
    - Total d'actions
    - Actions par type
    - Actions par sévérité
    - Actions par résultat
    - Utilisateurs les plus actifs
    """
    # Par défaut: derniers 30 jours
    if not start_date:
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    if not end_date:
        end_date = datetime.now(timezone.utc)
    
    stats = await service.get_statistics(
        start_date=start_date,
        end_date=end_date
    )
    
    return stats


@router.get("/compliance-report")
async def generate_compliance_report(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Générer un rapport de conformité (RGPD, SOC2, etc.)
    
    **Permissions requises:** Admin
    
    **Contenu du rapport:**
    - Actions sensibles
    - Permissions refusées
    - Alertes de sécurité
    - Statut de conformité
    """
    if not start_date or not end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les dates de début et de fin sont requises"
        )
    
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être postérieure à la date de début"
        )
    
    report = await service.generate_compliance_report(
        start_date=start_date,
        end_date=end_date
    )
    
    logger.info(
        f"Rapport de conformité généré par {current_user.username} "
        f"pour la période {start_date} - {end_date}"
    )
    
    return report


@router.post("/cleanup")
async def cleanup_old_audit_entries(
    days_to_keep: int = Query(90, ge=30, le=730),  # Entre 30 jours et 2 ans
    current_user: User = Depends(require_admin),
    service: IAMAuditService = Depends(get_audit_service)
):
    """
    Nettoyer les anciennes entrées d'audit (conformité RGPD)
    
    **Permissions requises:** Admin
    
    **Note:** Les entrées CRITICAL sont toujours conservées
    
    **Recommandations:**
    - RGPD: 90 jours minimum
    - SOC2: 365 jours minimum
    - ISO 27001: 180 jours minimum
    """
    if days_to_keep < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum 30 jours requis pour la conformité"
        )
    
    count = await service.cleanup_old_entries(days_to_keep=days_to_keep)
    
    logger.warning(
        f"Nettoyage d'audit effectué par {current_user.username}: "
        f"{count} entrées supprimées (>{days_to_keep} jours)"
    )
    
    return {
        "success": True,
        "deleted_count": count,
        "days_kept": days_to_keep,
        "message": f"{count} entrées d'audit supprimées (plus anciennes que {days_to_keep} jours)"
    }


@router.get("/action-types")
async def get_available_action_types(
    current_user: User = Depends(require_admin)
):
    """
    Récupérer la liste de tous les types d'actions auditées
    
    **Permissions requises:** Admin
    
    **Utilisation:** Pour les filtres et recherches
    """
    actions = [
        {
            "value": action.value,
            "name": action.name,
            "description": _get_action_description(action)
        }
        for action in AuditAction
    ]
    
    return {
        "total": len(actions),
        "actions": actions
    }


@router.get("/severity-levels")
async def get_severity_levels(
    current_user: User = Depends(require_admin)
):
    """
    Récupérer les niveaux de sévérité disponibles
    
    **Permissions requises:** Admin
    """
    severities = [
        {
            "value": sev.value,
            "name": sev.name,
            "description": _get_severity_description(sev)
        }
        for sev in AuditSeverity
    ]
    
    return {
        "total": len(severities),
        "severities": severities
    }


def _get_action_description(action: AuditAction) -> str:
    """Helper pour obtenir une description lisible d'une action"""
    descriptions = {
        AuditAction.PROFILE_CREATED: "Création d'un profil utilisateur",
        AuditAction.PROFILE_UPDATED: "Mise à jour d'un profil",
        AuditAction.PROFILE_DELETED: "Suppression d'un profil",
        AuditAction.PERMISSION_DENIED: "Tentative d'accès refusée",
        AuditAction.TEMP_PERMISSION_GRANTED: "Permission temporaire accordée",
        AuditAction.TEMP_PERMISSION_REVOKED: "Permission temporaire révoquée",
        # Ajouter d'autres si nécessaire
    }
    return descriptions.get(action, action.value.replace("_", " ").title())


def _get_severity_description(severity: AuditSeverity) -> str:
    """Helper pour obtenir une description lisible d'un niveau de sévérité"""
    descriptions = {
        AuditSeverity.INFO: "Information normale",
        AuditSeverity.WARNING: "Avertissement - attention requise",
        AuditSeverity.ERROR: "Erreur - action échouée",
        AuditSeverity.CRITICAL: "Critique - action de sécurité sensible"
    }
    return descriptions.get(severity, severity.value)
