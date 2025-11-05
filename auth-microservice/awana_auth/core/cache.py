"""
Simple in-memory cache for configuration references
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio


class ReferenceCache:
    """Cache simple en mémoire pour les référentiels"""
    
    def __init__(self, ttl_minutes: int = 30):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[List[Dict]]:
        """Récupérer une valeur du cache"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            # Vérifier si le cache est expiré
            if datetime.utcnow() - self._timestamps[key] > self.ttl:
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            return self._cache[key]
    
    async def set(self, key: str, value: List[Dict]) -> None:
        """Définir une valeur dans le cache"""
        async with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.utcnow()
    
    async def invalidate(self, key: Optional[str] = None) -> None:
        """Invalider le cache (une clé ou tout)"""
        async with self._lock:
            if key:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
            else:
                self._cache.clear()
                self._timestamps.clear()
    
    async def clear(self) -> None:
        """Vider tout le cache"""
        await self.invalidate()


# Instance globale du cache
reference_cache = ReferenceCache(ttl_minutes=30)


def get_cache_key(category: str, is_active: Optional[bool] = None) -> str:
    """Générer une clé de cache"""
    if is_active is None:
        return f"refs:{category}"
    return f"refs:{category}:active={is_active}"
