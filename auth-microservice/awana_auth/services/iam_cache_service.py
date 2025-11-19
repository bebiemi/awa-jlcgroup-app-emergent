"""
IAM Cache Service - Redis
Gestion du cache des permissions pour améliorer les performances
"""
import redis.asyncio as aioredis
import json
import logging
from typing import Optional, List, Set
from datetime import timedelta
import os

logger = logging.getLogger(__name__)


class IAMCacheService:
    """
    Service de cache Redis pour IAM
    
    Fonctionnalités :
    - Cache des permissions utilisateur
    - Cache des profils
    - Cache des bundles
    - Invalidation sélective
    - TTL configurable
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialiser le service de cache
        
        Args:
            redis_url: URL Redis (ex: redis://localhost:6379/0)
        """
        self.redis_url = redis_url or os.environ.get(
            'REDIS_URL', 
            'redis://localhost:6379/0'
        )
        self.redis: Optional[aioredis.Redis] = None
        self.enabled = True
        
        # Configuration TTL (Time To Live)
        self.ttl_user_permissions = int(os.environ.get('IAM_CACHE_TTL_PERMISSIONS', 300))  # 5 min
        self.ttl_profile = int(os.environ.get('IAM_CACHE_TTL_PROFILE', 600))  # 10 min
        self.ttl_bundle = int(os.environ.get('IAM_CACHE_TTL_BUNDLE', 900))  # 15 min
        
        # Préfixes de clés
        self.prefix_user_perms = "iam:user_perms:"
        self.prefix_profile = "iam:profile:"
        self.prefix_bundle = "iam:bundle:"
        self.prefix_permission = "iam:permission:"
    
    async def connect(self):
        """Établir la connexion Redis"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test de connexion
            await self.redis.ping()
            logger.info(f"✅ Redis connecté: {self.redis_url}")
            self.enabled = True
        except Exception as e:
            logger.warning(f"⚠️  Redis non disponible: {e}. Cache désactivé.")
            self.enabled = False
    
    async def disconnect(self):
        """Fermer la connexion Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis déconnecté")
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Construire une clé Redis"""
        return f"{prefix}{identifier}"
    
    # ==================== PERMISSIONS UTILISATEUR ====================
    
    async def get_user_permissions(self, user_id: str) -> Optional[List[dict]]:
        """
        Récupérer les permissions d'un utilisateur depuis le cache
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste de permissions ou None si pas en cache
        """
        if not self.enabled or not self.redis:
            return None
        
        try:
            key = self._make_key(self.prefix_user_perms, user_id)
            data = await self.redis.get(key)
            
            if data:
                logger.debug(f"🎯 Cache HIT: permissions user {user_id}")
                return json.loads(data)
            
            logger.debug(f"❌ Cache MISS: permissions user {user_id}")
            return None
        except Exception as e:
            logger.error(f"Erreur lecture cache permissions: {e}")
            return None
    
    async def set_user_permissions(
        self, 
        user_id: str, 
        permissions: List[dict],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Mettre en cache les permissions d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            permissions: Liste des permissions
            ttl: Time to live en secondes (optionnel)
            
        Returns:
            True si succès
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            key = self._make_key(self.prefix_user_perms, user_id)
            data = json.dumps(permissions)
            
            ttl = ttl or self.ttl_user_permissions
            await self.redis.setex(key, ttl, data)
            
            logger.debug(f"💾 Cache SET: permissions user {user_id} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Erreur écriture cache permissions: {e}")
            return False
    
    async def invalidate_user_permissions(self, user_id: str) -> bool:
        """
        Invalider le cache des permissions d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            True si succès
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            key = self._make_key(self.prefix_user_perms, user_id)
            await self.redis.delete(key)
            logger.info(f"🗑️  Cache invalidé: permissions user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur invalidation cache: {e}")
            return False
    
    # ==================== PROFILS ====================
    
    async def get_profile(self, profile_id: str) -> Optional[dict]:
        """Récupérer un profil depuis le cache"""
        if not self.enabled or not self.redis:
            return None
        
        try:
            key = self._make_key(self.prefix_profile, profile_id)
            data = await self.redis.get(key)
            
            if data:
                logger.debug(f"🎯 Cache HIT: profile {profile_id}")
                return json.loads(data)
            
            return None
        except Exception as e:
            logger.error(f"Erreur lecture cache profile: {e}")
            return None
    
    async def set_profile(
        self, 
        profile_id: str, 
        profile_data: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """Mettre en cache un profil"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            key = self._make_key(self.prefix_profile, profile_id)
            data = json.dumps(profile_data)
            
            ttl = ttl or self.ttl_profile
            await self.redis.setex(key, ttl, data)
            
            logger.debug(f"💾 Cache SET: profile {profile_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur écriture cache profile: {e}")
            return False
    
    async def invalidate_profile(self, profile_id: str) -> bool:
        """Invalider le cache d'un profil"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            key = self._make_key(self.prefix_profile, profile_id)
            await self.redis.delete(key)
            logger.info(f"🗑️  Cache invalidé: profile {profile_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur invalidation cache profile: {e}")
            return False
    
    # ==================== BUNDLES ====================
    
    async def get_bundle(self, bundle_id: str) -> Optional[dict]:
        """Récupérer un bundle depuis le cache"""
        if not self.enabled or not self.redis:
            return None
        
        try:
            key = self._make_key(self.prefix_bundle, bundle_id)
            data = await self.redis.get(key)
            
            if data:
                logger.debug(f"🎯 Cache HIT: bundle {bundle_id}")
                return json.loads(data)
            
            return None
        except Exception as e:
            logger.error(f"Erreur lecture cache bundle: {e}")
            return None
    
    async def set_bundle(
        self, 
        bundle_id: str, 
        bundle_data: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """Mettre en cache un bundle"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            key = self._make_key(self.prefix_bundle, bundle_id)
            data = json.dumps(bundle_data)
            
            ttl = ttl or self.ttl_bundle
            await self.redis.setex(key, ttl, data)
            
            logger.debug(f"💾 Cache SET: bundle {bundle_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur écriture cache bundle: {e}")
            return False
    
    # ==================== INVALIDATION GLOBALE ====================
    
    async def invalidate_all_user_permissions(self) -> bool:
        """Invalider toutes les permissions utilisateurs en cache"""
        if not self.enabled or not self.redis:
            return False
        
        try:
            pattern = f"{self.prefix_user_perms}*"
            cursor = 0
            count = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                    count += len(keys)
                
                if cursor == 0:
                    break
            
            logger.info(f"🗑️  Cache invalidé: {count} permissions utilisateurs")
            return True
        except Exception as e:
            logger.error(f"Erreur invalidation globale: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalider toutes les clés correspondant à un pattern
        
        Args:
            pattern: Pattern Redis (ex: "iam:user_perms:*")
            
        Returns:
            Nombre de clés invalidées
        """
        if not self.enabled or not self.redis:
            return 0
        
        try:
            cursor = 0
            count = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                    count += len(keys)
                
                if cursor == 0:
                    break
            
            logger.info(f"🗑️  Cache invalidé: {count} clés pour pattern '{pattern}'")
            return count
        except Exception as e:
            logger.error(f"Erreur invalidation pattern: {e}")
            return 0
    
    # ==================== STATISTIQUES ====================
    
    async def get_cache_stats(self) -> dict:
        """
        Récupérer les statistiques du cache
        
        Returns:
            Dictionnaire avec les stats
        """
        if not self.enabled or not self.redis:
            return {"enabled": False}
        
        try:
            info = await self.redis.info("stats")
            
            # Compter les clés par type
            user_perms_count = 0
            profiles_count = 0
            bundles_count = 0
            
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, count=1000)
                for key in keys:
                    if key.startswith(self.prefix_user_perms):
                        user_perms_count += 1
                    elif key.startswith(self.prefix_profile):
                        profiles_count += 1
                    elif key.startswith(self.prefix_bundle):
                        bundles_count += 1
                
                if cursor == 0:
                    break
            
            return {
                "enabled": True,
                "redis_url": self.redis_url.split('@')[-1],  # Masquer credentials
                "total_keys": await self.redis.dbsize(),
                "user_permissions_cached": user_perms_count,
                "profiles_cached": profiles_count,
                "bundles_cached": bundles_count,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "memory_used": info.get("used_memory_human", "N/A"),
            }
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}")
            return {"enabled": True, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculer le taux de cache hits"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    # ==================== HELPERS ====================
    
    async def clear_all_cache(self) -> bool:
        """
        Vider TOUT le cache IAM (⚠️ DANGER)
        
        Returns:
            True si succès
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            # Invalider tous les patterns IAM
            patterns = [
                f"{self.prefix_user_perms}*",
                f"{self.prefix_profile}*",
                f"{self.prefix_bundle}*",
                f"{self.prefix_permission}*",
            ]
            
            total_deleted = 0
            for pattern in patterns:
                count = await self.invalidate_pattern(pattern)
                total_deleted += count
            
            logger.warning(f"🗑️  CACHE VIDÉ: {total_deleted} clés supprimées")
            return True
        except Exception as e:
            logger.error(f"Erreur vidage cache: {e}")
            return False
    
    async def health_check(self) -> dict:
        """
        Vérifier la santé du cache Redis
        
        Returns:
            Statut de santé
        """
        if not self.enabled:
            return {"status": "disabled", "healthy": False}
        
        if not self.redis:
            return {"status": "not_connected", "healthy": False}
        
        try:
            await self.redis.ping()
            return {"status": "healthy", "healthy": True}
        except Exception as e:
            return {"status": "error", "healthy": False, "error": str(e)}


# Instance globale (singleton)
_cache_service: Optional[IAMCacheService] = None


async def get_cache_service() -> IAMCacheService:
    """
    Récupérer l'instance du service de cache (singleton)
    
    Returns:
        Instance IAMCacheService
    """
    global _cache_service
    
    if _cache_service is None:
        _cache_service = IAMCacheService()
        await _cache_service.connect()
    
    return _cache_service


async def close_cache_service():
    """Fermer le service de cache"""
    global _cache_service
    
    if _cache_service:
        await _cache_service.disconnect()
        _cache_service = None
