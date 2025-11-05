"""
Service de gestion des Feature Flags avec cache et rollout progressif
"""
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.feature_flag_models import (
    FeatureFlag,
    FeatureFlagType,
    FeatureFlagContext,
    CreateFeatureFlagRequest,
    UpdateFeatureFlagRequest,
    AuditEvent,
    AuditEventType,
)


class FeatureFlagService:
    """Service de gestion des feature flags"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.cache: Dict[str, Any] = {}  # Cache simple en mémoire
        self.cache_ttl = 300  # 5 minutes
        self.cache_timestamps: Dict[str, datetime] = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Vérifier si le cache est toujours valide"""
        if key not in self.cache_timestamps:
            return False
        age = (datetime.now(timezone.utc) - self.cache_timestamps[key]).total_seconds()
        return age < self.cache_ttl
    
    def _set_cache(self, key: str, value: Any):
        """Mettre en cache une valeur"""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now(timezone.utc)
    
    def _invalidate_cache(self, pattern: Optional[str] = None):
        """Invalider le cache (tout ou pattern spécifique)"""
        if pattern:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
                del self.cache_timestamps[key]
        else:
            self.cache.clear()
            self.cache_timestamps.clear()
    
    async def is_enabled(
        self, 
        flag_key: str, 
        context: FeatureFlagContext
    ) -> bool:
        """
        Vérifier si un feature flag est activé pour le contexte donné
        
        Ordre de priorité:
        1. USER (plus spécifique)
        2. ROLE 
        3. ENV
        4. GLOBAL (fallback)
        """
        cache_key = f"flag:{flag_key}:{context.user_id}:{':'.join(sorted(context.roles))}:{context.environment}"
        
        # Vérifier cache
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, False)
        
        # 1. Vérifier USER flag
        if context.user_id:
            user_flag = await self.db.feature_flags.find_one({
                "key": flag_key,
                "type": FeatureFlagType.USER.value,
                "target": context.user_id
            })
            if user_flag:
                result = self._evaluate_flag(user_flag, context)
                self._set_cache(cache_key, result)
                return result
        
        # 2. Vérifier ROLE flags (première correspondance)
        if context.roles:
            for role in context.roles:
                role_flag = await self.db.feature_flags.find_one({
                    "key": flag_key,
                    "type": FeatureFlagType.ROLE.value,
                    "target": role
                })
                if role_flag:
                    result = self._evaluate_flag(role_flag, context)
                    self._set_cache(cache_key, result)
                    return result
        
        # 3. Vérifier ENV flag
        env_flag = await self.db.feature_flags.find_one({
            "key": flag_key,
            "type": FeatureFlagType.ENV.value,
            "target": context.environment
        })
        if env_flag:
            result = self._evaluate_flag(env_flag, context)
            self._set_cache(cache_key, result)
            return result
        
        # 4. Vérifier GLOBAL flag (fallback)
        global_flag = await self.db.feature_flags.find_one({
            "key": flag_key,
            "type": FeatureFlagType.GLOBAL.value
        })
        if global_flag:
            result = self._evaluate_flag(global_flag, context)
            self._set_cache(cache_key, result)
            return result
        
        # Par défaut: désactivé
        self._set_cache(cache_key, False)
        return False
    
    def _evaluate_flag(self, flag: Dict, context: FeatureFlagContext) -> bool:
        """
        Évaluer un flag en tenant compte du rollout progressif
        """
        if not flag.get('value', False):
            return False
        
        # Vérifier rollout percentage
        rollout_pct = flag.get('metadata', {}).get('rollout_percentage', 100)
        
        if rollout_pct < 100 and context.user_id:
            # Hash consistant pour rollout progressif
            hash_input = f"{flag['key']}:{context.user_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            user_percentage = hash_value % 100
            
            return user_percentage < rollout_pct
        
        return rollout_pct == 100
    
    async def get_all_flags(
        self, 
        caller_roles: List[str],
        include_inactive: bool = False
    ) -> List[Dict]:
        """
        Récupérer tous les flags (filtrés selon les permissions)
        Super-admin voit tout, admin voit GLOBAL et ROLE uniquement
        """
        query = {}
        if not include_inactive:
            query['value'] = True
        
        # Si pas super_admin, filtrer les types visibles
        if 'super_admin' not in caller_roles:
            query['type'] = {'$in': [
                FeatureFlagType.GLOBAL.value,
                FeatureFlagType.ROLE.value
            ]}
        
        cursor = self.db.feature_flags.find(query, {'_id': 0})
        flags = await cursor.to_list(length=None)
        return flags
    
    async def create_flag(
        self,
        request: CreateFeatureFlagRequest,
        created_by: str,
        actor_name: Optional[str] = None
    ) -> Dict:
        """Créer un nouveau feature flag"""
        # Vérifier unicité de la clé
        existing = await self.db.feature_flags.find_one({"key": request.key})
        if existing:
            raise ValueError(f"Un flag avec la clé '{request.key}' existe déjà")
        
        flag = FeatureFlag(
            key=request.key,
            type=request.type,
            value=request.value,
            target=request.target,
            metadata=request.metadata or {},
            created_by=created_by,
        )
        
        flag_dict = flag.dict()
        flag_dict['metadata'] = flag_dict['metadata'] if isinstance(flag_dict['metadata'], dict) else flag_dict['metadata'].dict()
        
        await self.db.feature_flags.insert_one(flag_dict)
        
        # Audit
        await self._create_audit_event(
            actor_id=created_by,
            actor_name=actor_name,
            action=AuditEventType.FEATURE_FLAG_CREATED,
            target_type="feature_flag",
            target_id=flag.id,
            payload={
                "flag_key": flag.key,
                "type": flag.type.value,
                "value": flag.value,
                "target": flag.target
            }
        )
        
        # Invalider cache
        self._invalidate_cache(flag.key)
        
        return flag_dict
    
    async def update_flag(
        self,
        flag_id: str,
        request: UpdateFeatureFlagRequest,
        updated_by: str,
        actor_name: Optional[str] = None
    ) -> Dict:
        """Mettre à jour un feature flag"""
        flag = await self.db.feature_flags.find_one({"id": flag_id})
        if not flag:
            raise ValueError(f"Flag {flag_id} non trouvé")
        
        old_value = flag.get('value')
        update_data = {}
        
        if request.value is not None:
            update_data['value'] = request.value
        if request.target is not None:
            update_data['target'] = request.target
        if request.metadata is not None:
            metadata_dict = request.metadata.dict() if hasattr(request.metadata, 'dict') else request.metadata
            update_data['metadata'] = metadata_dict
        
        update_data['updated_at'] = datetime.now(timezone.utc)
        
        await self.db.feature_flags.update_one(
            {"id": flag_id},
            {"$set": update_data}
        )
        
        # Audit
        await self._create_audit_event(
            actor_id=updated_by,
            actor_name=actor_name,
            action=AuditEventType.FEATURE_FLAG_UPDATED,
            target_type="feature_flag",
            target_id=flag_id,
            payload={
                "flag_key": flag['key'],
                "old_value": old_value,
                "new_value": request.value,
                "changes": update_data
            }
        )
        
        # Invalider cache
        self._invalidate_cache(flag['key'])
        
        updated_flag = await self.db.feature_flags.find_one({"id": flag_id})
        return updated_flag
    
    async def delete_flag(
        self,
        flag_id: str,
        deleted_by: str,
        actor_name: Optional[str] = None
    ) -> bool:
        """Supprimer un feature flag"""
        flag = await self.db.feature_flags.find_one({"id": flag_id})
        if not flag:
            raise ValueError(f"Flag {flag_id} non trouvé")
        
        await self.db.feature_flags.delete_one({"id": flag_id})
        
        # Audit
        await self._create_audit_event(
            actor_id=deleted_by,
            actor_name=actor_name,
            action=AuditEventType.FEATURE_FLAG_DELETED,
            target_type="feature_flag",
            target_id=flag_id,
            payload={
                "flag_key": flag['key'],
                "type": flag['type'],
                "was_enabled": flag.get('value', False)
            }
        )
        
        # Invalider cache
        self._invalidate_cache(flag['key'])
        
        return True
    
    async def apply_rollout(
        self,
        flag_id: str,
        rollout_percentage: int,
        applied_by: str,
        actor_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Appliquer un rollout progressif"""
        flag = await self.db.feature_flags.find_one({"id": flag_id})
        if not flag:
            raise ValueError(f"Flag {flag_id} non trouvé")
        
        old_percentage = flag.get('metadata', {}).get('rollout_percentage', 0)
        
        # Mettre à jour le pourcentage
        await self.db.feature_flags.update_one(
            {"id": flag_id},
            {
                "$set": {
                    "metadata.rollout_percentage": rollout_percentage,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Audit
        await self._create_audit_event(
            actor_id=applied_by,
            actor_name=actor_name,
            action=AuditEventType.FEATURE_FLAG_ROLLOUT,
            target_type="feature_flag",
            target_id=flag_id,
            payload={
                "flag_key": flag['key'],
                "old_percentage": old_percentage,
                "new_percentage": rollout_percentage,
                "description": description
            }
        )
        
        # Invalider cache
        self._invalidate_cache(flag['key'])
        
        updated_flag = await self.db.feature_flags.find_one({"id": flag_id})
        return updated_flag
    
    async def _create_audit_event(
        self,
        actor_id: str,
        action: AuditEventType,
        target_type: str,
        target_id: Optional[str],
        payload: Dict[str, Any],
        actor_name: Optional[str] = None
    ):
        """Créer un événement d'audit"""
        event = AuditEvent(
            actor_id=actor_id,
            actor_name=actor_name,
            action=action,
            target_type=target_type,
            target_id=target_id,
            payload=payload
        )
        
        event_dict = event.dict()
        await self.db.audit_events.insert_one(event_dict)
    
    async def get_audit_history(
        self,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Récupérer l'historique d'audit"""
        query = {}
        if target_type:
            query['target_type'] = target_type
        if target_id:
            query['target_id'] = target_id
        
        events = await self.db.audit_events.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
        return events
