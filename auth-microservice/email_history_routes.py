"""
Routes pour l'historique des emails
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.models import User
from typing import List, Optional
from datetime import datetime


router = APIRouter(prefix="/api/emails", tags=["email-history"])


@router.get("/history")
async def get_email_history(
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de la page"),
    status_filter: Optional[str] = Query(None, description="Filtrer par statut (sent, failed)"),
    sent_by: Optional[str] = Query(None, description="Filtrer par expéditeur"),
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer l'historique des emails envoyés
    Accessible aux admins et super-admins
    """
    # Construire le filtre
    query_filter = {}
    
    if status_filter:
        query_filter["status"] = status_filter
    
    if sent_by:
        query_filter["sent_by"] = sent_by
    
    # Compter le total
    total = await db.email_history.count_documents(query_filter)
    
    # Récupérer la page
    skip = (page - 1) * page_size
    
    history = await db.email_history.find(query_filter)\
        .sort("created_at", -1)\
        .skip(skip)\
        .limit(page_size)\
        .to_list(length=page_size)
    
    # Formater les résultats
    results = []
    for entry in history:
        results.append({
            "id": entry.get("id"),
            "to_emails": entry.get("to_emails", []),
            "subject": entry.get("subject", ""),
            "template_name": entry.get("template_name"),
            "status": entry.get("status"),
            "sent_at": entry.get("sent_at"),
            "error_message": entry.get("error_message"),
            "sent_by": entry.get("sent_by"),
            "metadata": entry.get("metadata", {}),
            "created_at": entry.get("created_at")
        })
    
    return {
        "items": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/history/stats")
async def get_email_stats(
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les statistiques des emails
    Accessible aux admins et super-admins
    """
    # Total d'emails
    total = await db.email_history.count_documents({})
    
    # Emails envoyés avec succès
    sent = await db.email_history.count_documents({"status": "sent"})
    
    # Emails échoués
    failed = await db.email_history.count_documents({"status": "failed"})
    
    # Emails des 7 derniers jours
    from datetime import timedelta, timezone
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    last_7_days = await db.email_history.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    # Taux de succès
    success_rate = (sent / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "sent": sent,
        "failed": failed,
        "last_7_days": last_7_days,
        "success_rate": round(success_rate, 2)
    }


@router.delete("/history")
async def clear_email_history(
    older_than_days: int = Query(30, ge=1, description="Supprimer les emails plus anciens que X jours"),
    current_user: User = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Nettoyer l'historique des emails
    Accessible aux admins et super-admins
    """
    from datetime import timedelta, timezone
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    
    result = await db.email_history.delete_many({
        "created_at": {"$lt": cutoff_date}
    })
    
    return {
        "message": f"Historique nettoyé (emails de plus de {older_than_days} jours)",
        "deleted_count": result.deleted_count
    }
