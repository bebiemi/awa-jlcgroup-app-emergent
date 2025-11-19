"""
Service de Gestion des Permissions Temporaires
Permet d'accorder des permissions limitées dans le temps
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import uuid

logger = logging.getLogger(__name__)


class TemporaryPermission(BaseModel):
    """Modèle pour une permission temporaire"""
    id: str
    user_id: str
    permission_id: str
    permission_code: str
    granted_by: str  # ID de l'admin qui a accordé
    granted_at: datetime
    expires_at: datetime
    reason: Optional[str] = None
    is_active: bool = True
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None
    revoke_reason: Optional[str] = None


class TemporaryPermissionsService:
    """
    Service pour gérer les permissions temporaires
    
    Cas d'usage :
    - Accès temporaire pour un projet
    - Remplacement temporaire d'un collègue
    - Urgence nécessitant des permissions élevées
    - Test de nouvelles fonctionnalités
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.temporary_permissions
        self.users_collection = db.users
        self.permissions_collection = db.permissions
    
    async def grant_temporary_permission(
        self,
        user_id: str,
        permission_code: str,
        duration_hours: int,
        granted_by: str,
        reason: Optional[str] = None
    ) -> TemporaryPermission:
        """
        Accorder une permission temporaire à un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            permission_code: Code de la permission (ex: "missions.edit.all")
            duration_hours: Durée en heures
            granted_by: ID de l'administrateur qui accorde
            reason: Raison de l'octroi
            
        Returns:
            TemporaryPermission créée
        """
        # Vérifier que la permission existe
        permission = await self.permissions_collection.find_one({"code": permission_code})
        if not permission:
            raise ValueError(f"Permission '{permission_code}' non trouvée")
        
        # Vérifier que l'utilisateur existe
        user = await self.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Utilisateur '{user_id}' non trouvé")
        
        # Créer la permission temporaire
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=duration_hours)
        
        temp_perm = TemporaryPermission(
            id=str(uuid.uuid4()),
            user_id=user_id,
            permission_id=permission["id"],
            permission_code=permission_code,
            granted_by=granted_by,
            granted_at=now,
            expires_at=expires_at,
            reason=reason,
            is_active=True
        )
        
        # Sauvegarder en base
        await self.collection.insert_one(temp_perm.dict())
        
        logger.info(
            f"✅ Permission temporaire accordée: {permission_code} "
            f"à user {user_id} pour {duration_hours}h"
        )
        
        return temp_perm
    
    async def get_active_temporary_permissions(
        self,
        user_id: str
    ) -> List[TemporaryPermission]:
        """
        Récupérer toutes les permissions temporaires actives d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des permissions temporaires actives et non expirées
        """
        now = datetime.now(timezone.utc)
        
        cursor = self.collection.find({
            "user_id": user_id,
            "is_active": True,
            "expires_at": {"$gt": now}
        })
        
        temp_perms = []
        async for doc in cursor:
            doc.pop("_id", None)
            temp_perms.append(TemporaryPermission(**doc))
        
        return temp_perms
    
    async def get_all_temporary_permissions(
        self,
        user_id: str,
        include_expired: bool = False
    ) -> List[TemporaryPermission]:
        """
        Récupérer toutes les permissions temporaires d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            include_expired: Inclure les permissions expirées
            
        Returns:
            Liste des permissions temporaires
        """
        query = {"user_id": user_id}
        
        if not include_expired:
            now = datetime.now(timezone.utc)
            query["expires_at"] = {"$gt": now}
        
        cursor = self.collection.find(query).sort("granted_at", -1)
        
        temp_perms = []
        async for doc in cursor:
            doc.pop("_id", None)
            temp_perms.append(TemporaryPermission(**doc))
        
        return temp_perms
    
    async def revoke_temporary_permission(
        self,
        temp_perm_id: str,
        revoked_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Révoquer une permission temporaire avant son expiration
        
        Args:
            temp_perm_id: ID de la permission temporaire
            revoked_by: ID de l'admin qui révoque
            reason: Raison de la révocation
            
        Returns:
            True si succès
        """
        now = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"id": temp_perm_id},
            {
                "$set": {
                    "is_active": False,
                    "revoked_at": now,
                    "revoked_by": revoked_by,
                    "revoke_reason": reason
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"🚫 Permission temporaire révoquée: {temp_perm_id}")
            return True
        
        return False
    
    async def extend_temporary_permission(
        self,
        temp_perm_id: str,
        additional_hours: int
    ) -> Optional[TemporaryPermission]:
        """
        Prolonger une permission temporaire
        
        Args:
            temp_perm_id: ID de la permission temporaire
            additional_hours: Heures supplémentaires
            
        Returns:
            Permission mise à jour ou None
        """
        temp_perm = await self.collection.find_one({"id": temp_perm_id})
        if not temp_perm:
            return None
        
        new_expires_at = temp_perm["expires_at"] + timedelta(hours=additional_hours)
        
        await self.collection.update_one(
            {"id": temp_perm_id},
            {"$set": {"expires_at": new_expires_at}}
        )
        
        logger.info(
            f"⏰ Permission temporaire prolongée: {temp_perm_id} "
            f"de {additional_hours}h"
        )
        
        # Récupérer la version mise à jour
        updated = await self.collection.find_one({"id": temp_perm_id})
        updated.pop("_id", None)
        return TemporaryPermission(**updated)
    
    async def cleanup_expired_permissions(self) -> int:
        """
        Nettoyer les permissions expirées (tâche cron)
        
        Returns:
            Nombre de permissions désactivées
        """
        now = datetime.now(timezone.utc)
        
        result = await self.collection.update_many(
            {
                "is_active": True,
                "expires_at": {"$lt": now}
            },
            {
                "$set": {"is_active": False}
            }
        )
        
        count = result.modified_count
        if count > 0:
            logger.info(f"🧹 Nettoyage: {count} permissions temporaires expirées désactivées")
        
        return count
    
    async def get_expiring_soon(
        self,
        hours_threshold: int = 24
    ) -> List[TemporaryPermission]:
        """
        Récupérer les permissions qui expirent bientôt (pour notifications)
        
        Args:
            hours_threshold: Seuil en heures (par défaut 24h)
            
        Returns:
            Liste des permissions qui expirent bientôt
        """
        now = datetime.now(timezone.utc)
        threshold_time = now + timedelta(hours=hours_threshold)
        
        cursor = self.collection.find({
            "is_active": True,
            "expires_at": {
                "$gt": now,
                "$lt": threshold_time
            }
        })
        
        temp_perms = []
        async for doc in cursor:
            doc.pop("_id", None)
            temp_perms.append(TemporaryPermission(**doc))
        
        return temp_perms
    
    async def get_statistics(self) -> dict:
        """
        Récupérer les statistiques des permissions temporaires
        
        Returns:
            Dictionnaire de statistiques
        """
        now = datetime.now(timezone.utc)
        
        total = await self.collection.count_documents({})
        active = await self.collection.count_documents({
            "is_active": True,
            "expires_at": {"$gt": now}
        })
        expired = await self.collection.count_documents({
            "expires_at": {"$lt": now}
        })
        revoked = await self.collection.count_documents({
            "is_active": False,
            "revoked_at": {"$ne": None}
        })
        
        # Top permissions temporaires accordées
        pipeline = [
            {"$group": {
                "_id": "$permission_code",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_permissions = []
        async for doc in self.collection.aggregate(pipeline):
            top_permissions.append({
                "permission": doc["_id"],
                "count": doc["count"]
            })
        
        return {
            "total": total,
            "active": active,
            "expired": expired,
            "revoked": revoked,
            "top_permissions": top_permissions
        }
    
    async def get_user_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[TemporaryPermission]:
        """
        Récupérer l'historique complet des permissions temporaires d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum de résultats
            
        Returns:
            Liste chronologique des permissions
        """
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("granted_at", -1).limit(limit)
        
        history = []
        async for doc in cursor:
            doc.pop("_id", None)
            history.append(TemporaryPermission(**doc))
        
        return history
