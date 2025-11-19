"""
Service d'Audit Trail IAM
Enregistre toutes les actions sensibles IAM pour conformité et sécurité
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Types d'actions auditées"""
    # Profils
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    PROFILE_DELETED = "profile_deleted"
    PROFILE_ASSIGNED = "profile_assigned"
    PROFILE_REMOVED = "profile_removed"
    
    # Permissions
    PERMISSION_CREATED = "permission_created"
    PERMISSION_UPDATED = "permission_updated"
    PERMISSION_DELETED = "permission_deleted"
    PERMISSION_CHECKED = "permission_checked"  # Pour audit haute fréquence
    PERMISSION_DENIED = "permission_denied"
    
    # Bundles
    BUNDLE_CREATED = "bundle_created"
    BUNDLE_UPDATED = "bundle_updated"
    BUNDLE_DELETED = "bundle_deleted"
    
    # Groupes
    GROUP_CREATED = "group_created"
    GROUP_UPDATED = "group_updated"
    GROUP_DELETED = "group_deleted"
    USER_ADDED_TO_GROUP = "user_added_to_group"
    USER_REMOVED_FROM_GROUP = "user_removed_from_group"
    
    # Permissions temporaires
    TEMP_PERMISSION_GRANTED = "temp_permission_granted"
    TEMP_PERMISSION_REVOKED = "temp_permission_revoked"
    TEMP_PERMISSION_EXPIRED = "temp_permission_expired"
    
    # Autres
    CACHE_INVALIDATED = "cache_invalidated"
    IAM_AUDIT_PERFORMED = "iam_audit_performed"


class AuditSeverity(str, Enum):
    """Niveaux de sévérité"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEntry(BaseModel):
    """Entrée d'audit"""
    id: str
    timestamp: datetime
    action: AuditAction
    severity: AuditSeverity
    actor_id: Optional[str]  # Qui a fait l'action
    actor_type: str  # "user", "system", "admin"
    target_type: str  # "profile", "permission", "user", etc.
    target_id: Optional[str]
    target_name: Optional[str]
    details: Dict[str, Any]  # Détails de l'action
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    result: str  # "success", "failure", "denied"
    error_message: Optional[str] = None


class IAMAuditService:
    """
    Service d'audit trail pour IAM
    
    Fonctionnalités :
    - Enregistrement de toutes les actions IAM
    - Recherche et filtrage des logs
    - Rapports d'audit
    - Alertes de sécurité
    - Conformité RGPD
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.iam_audit_trail
        self.users_collection = db.users
    
    async def log_action(
        self,
        action: AuditAction,
        actor_id: Optional[str],
        actor_type: str,
        target_type: str,
        target_id: Optional[str] = None,
        target_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        result: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEntry:
        """
        Enregistrer une action dans l'audit trail
        
        Args:
            action: Type d'action effectuée
            actor_id: ID de l'acteur (utilisateur, admin, système)
            actor_type: Type d'acteur
            target_type: Type de cible
            target_id: ID de la cible
            target_name: Nom de la cible (pour lisibilité)
            details: Détails additionnels
            severity: Niveau de sévérité
            result: Résultat de l'action
            error_message: Message d'erreur si échec
            ip_address: IP de l'acteur
            user_agent: User agent du navigateur
            
        Returns:
            AuditEntry créée
        """
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            action=action,
            severity=severity,
            actor_id=actor_id,
            actor_type=actor_type,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            details=details or {},
            result=result,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Sauvegarder
        await self.collection.insert_one(entry.dict())
        
        # Logger selon la sévérité
        log_msg = (
            f"[{action.value}] {actor_type}:{actor_id} → "
            f"{target_type}:{target_id or 'N/A'} [{result}]"
        )
        
        if severity == AuditSeverity.CRITICAL:
            logger.critical(log_msg)
        elif severity == AuditSeverity.ERROR:
            logger.error(log_msg)
        elif severity == AuditSeverity.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        return entry
    
    async def get_user_actions(
        self,
        user_id: str,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """
        Récupérer toutes les actions d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum de résultats
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste d'entrées d'audit
        """
        query = {"actor_id": user_id}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        
        entries = []
        async for doc in cursor:
            doc.pop("_id", None)
            entries.append(AuditEntry(**doc))
        
        return entries
    
    async def get_actions_by_type(
        self,
        action: AuditAction,
        limit: int = 100,
        start_date: Optional[datetime] = None
    ) -> List[AuditEntry]:
        """
        Récupérer toutes les actions d'un type spécifique
        
        Args:
            action: Type d'action
            limit: Nombre maximum de résultats
            start_date: Date de début
            
        Returns:
            Liste d'entrées d'audit
        """
        query = {"action": action}
        
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        
        cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
        
        entries = []
        async for doc in cursor:
            doc.pop("_id", None)
            entries.append(AuditEntry(**doc))
        
        return entries
    
    async def get_failed_actions(
        self,
        limit: int = 100,
        hours_back: int = 24
    ) -> List[AuditEntry]:
        """
        Récupérer toutes les actions échouées récentes
        
        Args:
            limit: Nombre maximum de résultats
            hours_back: Heures en arrière
            
        Returns:
            Liste d'entrées d'audit échouées
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        cursor = self.collection.find({
            "result": "failure",
            "timestamp": {"$gte": start_time}
        }).sort("timestamp", -1).limit(limit)
        
        entries = []
        async for doc in cursor:
            doc.pop("_id", None)
            entries.append(AuditEntry(**doc))
        
        return entries
    
    async def get_security_alerts(
        self,
        hours_back: int = 24
    ) -> List[AuditEntry]:
        """
        Récupérer les alertes de sécurité (actions critiques/erreurs)
        
        Args:
            hours_back: Heures en arrière
            
        Returns:
            Liste d'alertes
        """
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        cursor = self.collection.find({
            "severity": {"$in": [AuditSeverity.ERROR, AuditSeverity.CRITICAL]},
            "timestamp": {"$gte": start_time}
        }).sort("timestamp", -1)
        
        alerts = []
        async for doc in cursor:
            doc.pop("_id", None)
            alerts.append(AuditEntry(**doc))
        
        return alerts
    
    async def search_audit_trail(
        self,
        filters: Dict[str, Any],
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Recherche avancée dans l'audit trail
        
        Args:
            filters: Dictionnaire de filtres
            limit: Nombre de résultats
            skip: Nombre à sauter (pagination)
            
        Returns:
            Résultats avec metadata
        """
        query = {}
        
        # Construire la query MongoDB
        if "action" in filters:
            query["action"] = filters["action"]
        
        if "actor_id" in filters:
            query["actor_id"] = filters["actor_id"]
        
        if "target_type" in filters:
            query["target_type"] = filters["target_type"]
        
        if "severity" in filters:
            query["severity"] = filters["severity"]
        
        if "result" in filters:
            query["result"] = filters["result"]
        
        if "start_date" in filters or "end_date" in filters:
            query["timestamp"] = {}
            if "start_date" in filters:
                query["timestamp"]["$gte"] = filters["start_date"]
            if "end_date" in filters:
                query["timestamp"]["$lte"] = filters["end_date"]
        
        # Recherche texte
        if "search_text" in filters:
            query["$or"] = [
                {"target_name": {"$regex": filters["search_text"], "$options": "i"}},
                {"error_message": {"$regex": filters["search_text"], "$options": "i"}},
            ]
        
        # Compter le total
        total = await self.collection.count_documents(query)
        
        # Récupérer les résultats
        cursor = self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        
        entries = []
        async for doc in cursor:
            doc.pop("_id", None)
            entries.append(AuditEntry(**doc))
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "results": entries
        }
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Récupérer les statistiques d'audit
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Statistiques détaillées
        """
        query = {}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        # Total d'actions
        total = await self.collection.count_documents(query)
        
        # Par type d'action
        pipeline_actions = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$action",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        actions_stats = []
        async for doc in self.collection.aggregate(pipeline_actions):
            actions_stats.append({
                "action": doc["_id"],
                "count": doc["count"]
            })
        
        # Par sévérité
        pipeline_severity = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$severity",
                "count": {"$sum": 1}
            }}
        ]
        
        severity_stats = {}
        async for doc in self.collection.aggregate(pipeline_severity):
            severity_stats[doc["_id"]] = doc["count"]
        
        # Par résultat
        pipeline_result = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$result",
                "count": {"$sum": 1}
            }}
        ]
        
        result_stats = {}
        async for doc in self.collection.aggregate(pipeline_result):
            result_stats[doc["_id"]] = doc["count"]
        
        # Utilisateurs les plus actifs
        pipeline_users = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$actor_id",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_users = []
        async for doc in self.collection.aggregate(pipeline_users):
            if doc["_id"]:  # Exclure les None
                user = await self.users_collection.find_one({"id": doc["_id"]})
                top_users.append({
                    "user_id": doc["_id"],
                    "username": user.get("username") if user else "Unknown",
                    "count": doc["count"]
                })
        
        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "total_actions": total,
            "by_action": actions_stats,
            "by_severity": severity_stats,
            "by_result": result_stats,
            "top_users": top_users
        }
    
    async def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Générer un rapport de conformité (RGPD, SOC2, etc.)
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Rapport de conformité
        """
        # Actions sensibles
        sensitive_actions = [
            AuditAction.PERMISSION_DELETED,
            AuditAction.PROFILE_DELETED,
            AuditAction.USER_REMOVED_FROM_GROUP,
            AuditAction.TEMP_PERMISSION_GRANTED,
        ]
        
        sensitive_entries = await self.collection.find({
            "action": {"$in": sensitive_actions},
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(1000)
        
        # Permissions refusées
        denied_count = await self.collection.count_documents({
            "action": AuditAction.PERMISSION_DENIED,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        })
        
        # Erreurs et alertes
        security_alerts = await self.get_security_alerts(
            hours_back=int((end_date - start_date).total_seconds() / 3600)
        )
        
        return {
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "sensitive_actions": len(sensitive_entries),
            "sensitive_details": [
                {
                    "action": e.get("action"),
                    "actor": e.get("actor_id"),
                    "target": e.get("target_name"),
                    "timestamp": e.get("timestamp").isoformat()
                }
                for e in sensitive_entries[:50]  # Limiter à 50
            ],
            "permissions_denied": denied_count,
            "security_alerts": len(security_alerts),
            "compliance_status": "compliant" if len(security_alerts) == 0 else "needs_review"
        }
    
    async def cleanup_old_entries(
        self,
        days_to_keep: int = 90
    ) -> int:
        """
        Nettoyer les anciennes entrées d'audit (conformité RGPD)
        
        Args:
            days_to_keep: Nombre de jours à conserver
            
        Returns:
            Nombre d'entrées supprimées
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        # Garder toujours les entrées critiques
        result = await self.collection.delete_many({
            "timestamp": {"$lt": cutoff_date},
            "severity": {"$ne": AuditSeverity.CRITICAL}
        })
        
        count = result.deleted_count
        if count > 0:
            logger.info(f"🧹 Audit cleanup: {count} entrées supprimées (>{days_to_keep} jours)")
        
        return count
