"""
Service de gestion des expirations de profils temporaires
Vérifie et downgrade automatiquement les profils expirés
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import logging

from .models import (
    TemporaryProfile,
    ExpirationCheck,
    ProfileHistoryEntry,
    SystemProfiles
)

logger = logging.getLogger(__name__)


class ExpirationService:
    """Service de gestion des expirations de profils"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.downgrade_profile_code = SystemProfiles.RESTRICTED  # Profil de repli
        
    async def get_profile_id_by_code(self, code: str) -> str:
        """Récupère l'ID d'un profil par son code"""
        profile = await self.db.profiles.find_one({"code": code}, {"_id": 0, "id": 1})
        return profile["id"] if profile else None
    
    async def check_user_expirations(self, user_id: str) -> ExpirationCheck:
        """
        Vérifie les profils expirés et ceux expirant bientôt pour un utilisateur
        """
        user = await self.db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Récupérer les profils temporaires
        temporary_profiles_data = user.get("temporary_profiles", [])
        
        expired_profiles = []
        expiring_soon = []  # < 3 jours
        
        for temp_prof_data in temporary_profiles_data:
            temp_prof = TemporaryProfile(**temp_prof_data)
            
            if temp_prof.is_expired:
                expired_profiles.append(temp_prof)
            elif temp_prof.days_until_expiration <= 3:
                expiring_soon.append(temp_prof)
        
        downgrade_profile_id = await self.get_profile_id_by_code(self.downgrade_profile_code)
        
        return ExpirationCheck(
            user_id=user_id,
            username=user.get("username", ""),
            email=user.get("email", ""),
            expired_profiles=expired_profiles,
            expiring_soon=expiring_soon,
            downgrade_to_profile_id=downgrade_profile_id
        )
    
    async def check_all_expirations(self) -> List[ExpirationCheck]:
        """
        Vérifie les expirations pour tous les utilisateurs
        """
        logger.info("🔍 Vérification des expirations pour tous les utilisateurs...")
        
        # Récupérer tous les utilisateurs avec des profils temporaires
        users = await self.db.users.find(
            {"temporary_profiles": {"$exists": True, "$ne": []}},
            {"_id": 0, "id": 1}
        ).to_list(10000)
        
        logger.info(f"📊 {len(users)} utilisateurs avec profils temporaires trouvés")
        
        results = []
        for user in users:
            try:
                check = await self.check_user_expirations(user["id"])
                if check.expired_profiles or check.expiring_soon:
                    results.append(check)
            except Exception as e:
                logger.error(f"❌ Erreur vérification user {user['id']}: {e}")
        
        return results
    
    async def downgrade_expired_profile(
        self,
        user_id: str,
        expired_profile: TemporaryProfile,
        reason: str = "Expiration automatique"
    ) -> bool:
        """
        Downgrade un profil expiré
        - Retire le profil temporaire de temporary_profiles
        - Retire le profil de profile_ids
        - Ajoute une entrée dans l'historique
        - Envoie une notification (TODO)
        """
        try:
            user = await self.db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                return False
            
            # Retirer le profil expiré
            temporary_profiles = user.get("temporary_profiles", [])
            temporary_profiles = [
                tp for tp in temporary_profiles 
                if tp.get("profile_id") != expired_profile.profile_id
            ]
            
            profile_ids = user.get("profile_ids", [])
            if expired_profile.profile_id in profile_ids:
                profile_ids.remove(expired_profile.profile_id)
            
            # Ajouter à l'historique
            profile_history = user.get("profile_history", [])
            history_entry = ProfileHistoryEntry(
                profile_id=expired_profile.profile_id,
                action="expired",
                reason=reason,
                performed_by="system",
                metadata={
                    "assigned_at": expired_profile.assigned_at.isoformat() if expired_profile.assigned_at else None,
                    "expired_at": expired_profile.expires_at.isoformat() if expired_profile.expires_at else None,
                    "downgraded_at": datetime.now(timezone.utc).isoformat()
                }
            )
            profile_history.append(history_entry.dict())
            
            # Mettre à jour l'utilisateur
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "temporary_profiles": temporary_profiles,
                        "profile_ids": profile_ids,
                        "profile_history": profile_history,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"✅ Profil {expired_profile.profile_id} expiré pour user {user_id}")
            
            # TODO: Envoyer notification à l'utilisateur
            # await self.send_expiration_notification(user_id, expired_profile)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur downgrade profil pour user {user_id}: {e}")
            return False
    
    async def downgrade_all_expired_profiles(self) -> Dict[str, Any]:
        """
        Downgrade tous les profils expirés
        À exécuter en tâche planifiée (cron)
        """
        logger.info("🔄 Lancement du downgrade des profils expirés...")
        
        checks = await self.check_all_expirations()
        
        total_expired = sum(len(check.expired_profiles) for check in checks)
        downgraded_count = 0
        error_count = 0
        
        for check in checks:
            for expired_profile in check.expired_profiles:
                success = await self.downgrade_expired_profile(
                    check.user_id,
                    expired_profile,
                    reason=f"Expiration automatique après 15 jours"
                )
                
                if success:
                    downgraded_count += 1
                else:
                    error_count += 1
        
        logger.info(f"✅ Downgrade terminé: {downgraded_count}/{total_expired} profils downgradés")
        
        return {
            "total_checked": len(checks),
            "total_expired": total_expired,
            "downgraded": downgraded_count,
            "errors": error_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def notify_expiring_soon(self) -> Dict[str, Any]:
        """
        Notifie les utilisateurs dont les profils expirent bientôt (< 3 jours)
        À exécuter en tâche planifiée quotidienne
        """
        logger.info("📧 Envoi des notifications d'expiration imminente...")
        
        checks = await self.check_all_expirations()
        
        notified_count = 0
        error_count = 0
        
        for check in checks:
            for expiring_profile in check.expiring_soon:
                try:
                    # Vérifier si déjà notifié récemment
                    user = await self.db.users.find_one({"id": check.user_id}, {"_id": 0})
                    temp_profiles = user.get("temporary_profiles", [])
                    
                    needs_notification = True
                    for tp in temp_profiles:
                        if tp.get("profile_id") == expiring_profile.profile_id:
                            last_notified = tp.get("notified_at")
                            if last_notified:
                                # Ne notifier qu'une fois par jour max
                                last_notified_dt = datetime.fromisoformat(last_notified.replace("Z", "+00:00"))
                                if (datetime.now(timezone.utc) - last_notified_dt).days < 1:
                                    needs_notification = False
                            break
                    
                    if needs_notification:
                        # TODO: Envoyer la notification
                        # await self.send_expiring_notification(check.user_id, expiring_profile)
                        
                        # Marquer comme notifié
                        await self.db.users.update_one(
                            {
                                "id": check.user_id,
                                "temporary_profiles.profile_id": expiring_profile.profile_id
                            },
                            {
                                "$set": {
                                    "temporary_profiles.$.notified_at": datetime.now(timezone.utc).isoformat()
                                }
                            }
                        )
                        
                        notified_count += 1
                        logger.info(f"📧 Notification envoyée à {check.username} (expire dans {expiring_profile.days_until_expiration}j)")
                
                except Exception as e:
                    logger.error(f"❌ Erreur notification user {check.user_id}: {e}")
                    error_count += 1
        
        return {
            "notified": notified_count,
            "errors": error_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def assign_temporary_profile(
        self,
        user_id: str,
        profile_id: str,
        duration_days: int = 15,
        reason: str = "Attribution temporaire"
    ) -> bool:
        """
        Assigne un profil temporaire à un utilisateur
        Basé sur first_login_at
        """
        try:
            user = await self.db.users.find_one({"id": user_id}, {"_id": 0})
            if not user:
                return False
            
            # Calculer la date d'expiration
            first_login_at = user.get("first_login_at")
            if not first_login_at:
                # Si pas de first_login_at, utiliser la date actuelle
                first_login_at = datetime.now(timezone.utc).isoformat()
                await self.db.users.update_one(
                    {"id": user_id},
                    {"$set": {"first_login_at": first_login_at}}
                )
            
            first_login_dt = datetime.fromisoformat(first_login_at.replace("Z", "+00:00"))
            expires_at = first_login_dt + timedelta(days=duration_days)
            
            # Créer le profil temporaire
            temp_profile = TemporaryProfile(
                profile_id=profile_id,
                assigned_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                reason=reason
            )
            
            # Ajouter aux temporary_profiles et profile_ids
            temporary_profiles = user.get("temporary_profiles", [])
            temporary_profiles.append(temp_profile.dict())
            
            profile_ids = user.get("profile_ids", [])
            if profile_id not in profile_ids:
                profile_ids.append(profile_id)
            
            # Historique
            profile_history = user.get("profile_history", [])
            history_entry = ProfileHistoryEntry(
                profile_id=profile_id,
                action="assigned",
                reason=reason,
                performed_by="system",
                metadata={
                    "temporary": True,
                    "duration_days": duration_days,
                    "expires_at": expires_at.isoformat()
                }
            )
            profile_history.append(history_entry.dict())
            
            # Mettre à jour
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "temporary_profiles": temporary_profiles,
                        "profile_ids": profile_ids,
                        "profile_history": profile_history,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"✅ Profil temporaire {profile_id} assigné à {user_id} (expire: {expires_at})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur assignation profil temporaire: {e}")
            return False
