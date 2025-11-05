"""
Service de cache Redis pour production
Fallback sur cache mémoire si Redis non disponible
"""
import os
import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

# Try import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Using memory cache fallback.")


class CacheService:
    """
    Service de cache avec support Redis + fallback mémoire
    """
    
    def __init__(self, use_redis: bool = True):
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_client = None
        self.memory_cache = {}
        self.cache_timestamps = {}
        self.default_ttl = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes par défaut
        
        if self.use_redis:
            self._init_redis()
    
    def _init_redis(self):
        """Initialiser la connexion Redis"""
        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_db = int(os.getenv('REDIS_DB', '0'))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test connexion
            self.redis_client.ping()
            logger.info(f"✅ Redis connected: {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed: {e}. Using memory cache.")
            self.redis_client = None
            self.use_redis = False
    
    def _make_key(self, key: str, prefix: str = "jlc") -> str:
        """Créer une clé Redis avec préfixe"""
        return f"{prefix}:{key}"
    
    def get(self, key: str, prefix: str = "jlc") -> Optional[Any]:
        """
        Récupérer une valeur du cache
        """
        cache_key = self._make_key(key, prefix)
        
        if self.use_redis and self.redis_client:
            try:
                value = self.redis_client.get(cache_key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                logger.error(f"Redis GET error: {e}")
                # Fallback to memory
                return self._get_memory(cache_key)
        else:
            return self._get_memory(cache_key)
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        prefix: str = "jlc"
    ) -> bool:
        """
        Stocker une valeur dans le cache
        
        Args:
            key: Clé du cache
            value: Valeur à stocker (sera JSON serialized)
            ttl: Time to live en secondes (None = default_ttl)
            prefix: Préfixe de la clé
        """
        cache_key = self._make_key(key, prefix)
        ttl = ttl or self.default_ttl
        
        if self.use_redis and self.redis_client:
            try:
                serialized = json.dumps(value)
                self.redis_client.setex(cache_key, ttl, serialized)
                return True
            except Exception as e:
                logger.error(f"Redis SET error: {e}")
                # Fallback to memory
                return self._set_memory(cache_key, value, ttl)
        else:
            return self._set_memory(cache_key, value, ttl)
    
    def delete(self, key: str, prefix: str = "jlc") -> bool:
        """
        Supprimer une clé du cache
        """
        cache_key = self._make_key(key, prefix)
        
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(cache_key)
                return True
            except Exception as e:
                logger.error(f"Redis DELETE error: {e}")
                return self._delete_memory(cache_key)
        else:
            return self._delete_memory(cache_key)
    
    def delete_pattern(self, pattern: str, prefix: str = "jlc") -> int:
        """
        Supprimer toutes les clés matchant un pattern
        
        Args:
            pattern: Pattern glob (ex: "feature_flags:*")
            prefix: Préfixe de la clé
        
        Returns:
            Nombre de clés supprimées
        """
        full_pattern = self._make_key(pattern, prefix)
        
        if self.use_redis and self.redis_client:
            try:
                keys = self.redis_client.keys(full_pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            except Exception as e:
                logger.error(f"Redis DELETE_PATTERN error: {e}")
                return self._delete_pattern_memory(pattern)
        else:
            return self._delete_pattern_memory(pattern)
    
    def clear(self) -> bool:
        """
        Vider tout le cache (attention en production!)
        """
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.flushdb()
                return True
            except Exception as e:
                logger.error(f"Redis CLEAR error: {e}")
                return self._clear_memory()
        else:
            return self._clear_memory()
    
    def exists(self, key: str, prefix: str = "jlc") -> bool:
        """Vérifier si une clé existe"""
        cache_key = self._make_key(key, prefix)
        
        if self.use_redis and self.redis_client:
            try:
                return bool(self.redis_client.exists(cache_key))
            except Exception as e:
                logger.error(f"Redis EXISTS error: {e}")
                return self._exists_memory(cache_key)
        else:
            return self._exists_memory(cache_key)
    
    def ttl(self, key: str, prefix: str = "jlc") -> int:
        """Obtenir le TTL restant d'une clé (-1 si pas de TTL, -2 si inexistant)"""
        cache_key = self._make_key(key, prefix)
        
        if self.use_redis and self.redis_client:
            try:
                return self.redis_client.ttl(cache_key)
            except Exception as e:
                logger.error(f"Redis TTL error: {e}")
                return self._ttl_memory(cache_key)
        else:
            return self._ttl_memory(cache_key)
    
    # Memory cache fallback methods
    
    def _get_memory(self, key: str) -> Optional[Any]:
        """Get from memory cache"""
        if key in self.cache_timestamps:
            timestamp = self.cache_timestamps[key]
            if datetime.now(timezone.utc) < timestamp:
                return self.memory_cache.get(key)
            else:
                # Expired
                self._delete_memory(key)
        return None
    
    def _set_memory(self, key: str, value: Any, ttl: int) -> bool:
        """Set in memory cache"""
        self.memory_cache[key] = value
        self.cache_timestamps[key] = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        return True
    
    def _delete_memory(self, key: str) -> bool:
        """Delete from memory cache"""
        self.memory_cache.pop(key, None)
        self.cache_timestamps.pop(key, None)
        return True
    
    def _delete_pattern_memory(self, pattern: str) -> int:
        """Delete pattern from memory cache"""
        pattern = pattern.replace('*', '')
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            self._delete_memory(key)
        return len(keys_to_delete)
    
    def _clear_memory(self) -> bool:
        """Clear memory cache"""
        self.memory_cache.clear()
        self.cache_timestamps.clear()
        return True
    
    def _exists_memory(self, key: str) -> bool:
        """Check if key exists in memory"""
        if key in self.cache_timestamps:
            if datetime.now(timezone.utc) < self.cache_timestamps[key]:
                return True
            else:
                self._delete_memory(key)
        return False
    
    def _ttl_memory(self, key: str) -> int:
        """Get TTL from memory cache"""
        if key in self.cache_timestamps:
            remaining = (self.cache_timestamps[key] - datetime.now(timezone.utc)).total_seconds()
            return int(remaining) if remaining > 0 else -2
        return -2
    
    def get_stats(self) -> dict:
        """Obtenir les statistiques du cache"""
        if self.use_redis and self.redis_client:
            try:
                info = self.redis_client.info('stats')
                return {
                    "type": "redis",
                    "connected": True,
                    "keys": self.redis_client.dbsize(),
                    "hits": info.get('keyspace_hits', 0),
                    "misses": info.get('keyspace_misses', 0),
                    "memory_used": self.redis_client.info('memory').get('used_memory_human', 'N/A')
                }
            except Exception as e:
                logger.error(f"Redis STATS error: {e}")
                return {"type": "redis", "connected": False, "error": str(e)}
        else:
            return {
                "type": "memory",
                "connected": True,
                "keys": len(self.memory_cache),
                "memory_estimate": f"{len(str(self.memory_cache)) / 1024:.2f} KB"
            }


# Instance globale (singleton pattern)
_cache_instance: Optional[CacheService] = None


def get_cache_service(use_redis: bool = True) -> CacheService:
    """
    Obtenir l'instance du service de cache (singleton)
    
    Args:
        use_redis: True pour utiliser Redis si disponible, False pour forcer memory cache
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = CacheService(use_redis=use_redis)
    
    return _cache_instance
