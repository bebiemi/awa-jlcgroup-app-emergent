"""
Application Eligibility Service
Service pour vérifier l'éligibilité d'un utilisateur à postuler à une mission

Features:
- Vérification des règles métiers dynamiques
- Check permissions IAM
- Vérification contrat actif pour intérimaires
- Vérification CV requis
- Messages d'erreur configurables
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase


class ApplicationEligibilityService:
    """Service pour vérifier l'éligibilité aux candidatures"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._rules_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    async def _get_active_rules(self) -> List[Dict]:
        """Récupérer les règles métiers actives (avec cache)"""
        now = datetime.utcnow()
        
        # Vérifier cache
        if (self._rules_cache is not None and 
            self._cache_timestamp is not None and 
            (now - self._cache_timestamp).seconds < self._cache_ttl):
            return self._rules_cache
        
        # Charger depuis DB
        rules = await self.db.business_rules.find({
            "category": "application",
            "is_active": True
        }).sort("priority", -1).to_list(None)
        
        self._rules_cache = rules
        self._cache_timestamp = now
        
        return rules
    
    async def check_eligibility(
        self,
        user_id: str,
        user_roles: List[str],
        mission_id: str,
        mission_status: str,
        user_permissions: List[str] = None
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Vérifier l'éligibilité complète d'un utilisateur à postuler
        
        Args:
            user_id: ID de l'utilisateur
            user_roles: Rôles de l'utilisateur
            mission_id: ID de la mission
            mission_status: Statut de la mission
            user_permissions: Permissions IAM de l'utilisateur (optionnel)
            
        Returns:
            Tuple[is_eligible, error_message, metadata]
            - is_eligible: True si peut postuler
            - error_message: Message d'erreur si non éligible
            - metadata: Données supplémentaires (jours restants, etc.)
        """
        rules = await self._get_active_rules()
        metadata = {}
        
        # 1. Vérifier rôles autorisés
        role_check = await self._check_role_eligibility(user_roles, mission_status, rules)
        if not role_check[0]:
            return role_check
        
        # 2. Vérifier permissions IAM (si fournies)
        if user_permissions is not None:
            perm_check = await self._check_permissions(user_permissions)
            if not perm_check[0]:
                return perm_check
        
        # 3. Vérifier candidature dupliquée
        duplicate_check = await self._check_duplicate_application(user_id, mission_id, rules)
        if not duplicate_check[0]:
            return duplicate_check
        
        # 4. Vérifier contrat actif pour intérimaires
        if "intérimaire" in user_roles or "interim" in user_roles:
            contract_check = await self._check_active_contract(user_id, rules)
            if not contract_check[0]:
                return contract_check
            metadata["contract_info"] = contract_check[2]
        
        # 5. Vérifier CV (note: le frontend gérera l'upload si manquant)
        cv_check = await self._check_cv_requirement(user_id, rules)
        metadata["cv_required"] = cv_check[2].get("cv_required", True)
        metadata["allow_upload"] = cv_check[2].get("allow_upload", True)
        
        return True, None, metadata
    
    async def _check_role_eligibility(
        self,
        user_roles: List[str],
        mission_status: str,
        rules: List[Dict]
    ) -> Tuple[bool, Optional[str], Dict]:
        """Vérifier si le rôle utilisateur est autorisé"""
        # Trouver la règle d'éligibilité des rôles
        role_rule = next((r for r in rules if r["rule_id"] == "application_eligibility_roles"), None)
        
        if not role_rule:
            # Pas de règle = refuser par sécurité
            return False, "Configuration manquante : règles d'éligibilité introuvables", {}
        
        allowed_roles = role_rule["conditions"].get("allowed_roles", [])
        required_statuses = role_rule["conditions"].get("required_mission_status", [])
        
        # Vérifier rôle
        has_allowed_role = any(role in allowed_roles for role in user_roles)
        if not has_allowed_role:
            msg = role_rule["error_messages"].get("role_not_allowed", "Rôle non autorisé")
            return False, msg, {}
        
        # Vérifier statut mission
        if mission_status not in required_statuses:
            msg = role_rule["error_messages"].get("mission_not_open", "Mission non ouverte")
            return False, msg, {}
        
        return True, None, {}
    
    async def _check_permissions(self, user_permissions: List[str]) -> Tuple[bool, Optional[str], Dict]:
        """Vérifier les permissions IAM"""
        required_perm = "applications.create_own"
        
        if required_perm not in user_permissions:
            return False, "Vous n'avez pas les permissions nécessaires pour postuler", {}
        
        return True, None, {}
    
    async def _check_duplicate_application(
        self,
        user_id: str,
        mission_id: str,
        rules: List[Dict]
    ) -> Tuple[bool, Optional[str], Dict]:
        """Vérifier si l'utilisateur a déjà postulé"""
        # Chercher candidature existante
        existing = await self.db.applications.find_one({
            "user_id": user_id,
            "mission_id": mission_id
        })
        
        if existing:
            duplicate_rule = next((r for r in rules if r["rule_id"] == "application_duplicate_prevention"), None)
            if duplicate_rule:
                msg = duplicate_rule["error_messages"].get("already_applied", "Candidature déjà envoyée")
            else:
                msg = "Vous avez déjà postulé à cette mission"
            
            return False, msg, {"existing_application_id": existing.get("id")}
        
        return True, None, {}
    
    async def _check_active_contract(
        self,
        user_id: str,
        rules: List[Dict]
    ) -> Tuple[bool, Optional[str], Dict]:
        """Vérifier les restrictions de contrat actif pour intérimaires"""
        # Trouver la règle de restriction contrat
        contract_rule = next((r for r in rules if r["rule_id"] == "application_interim_contract_restriction"), None)
        
        if not contract_rule:
            # Pas de règle = autoriser
            return True, None, {}
        
        # Chercher contrat actif
        now = datetime.utcnow()
        active_contract = await self.db.contracts.find_one({
            "user_id": user_id,
            "status": "active",
            "end_date": {"$gte": now.isoformat()}
        })
        
        if not active_contract:
            # Pas de contrat actif = peut postuler
            return True, None, {"has_active_contract": False}
        
        # Contrat actif trouvé - vérifier conditions
        conditions = contract_rule["conditions"]
        days_before_end = conditions.get("days_before_contract_end", 5)
        check_extensions = conditions.get("check_extensions", True)
        check_amendments = conditions.get("check_amendments", True)
        
        # Calculer jours restants
        end_date = datetime.fromisoformat(active_contract["end_date"].replace('Z', '+00:00'))
        days_remaining = (end_date - now).days
        
        # Vérifier si proche de la fin
        if days_remaining > days_before_end:
            msg = contract_rule["error_messages"]["contract_active"].format(days_before=days_before_end)
            return False, msg, {
                "has_active_contract": True,
                "days_remaining": days_remaining,
                "can_apply_from_days": days_before_end
            }
        
        # Vérifier prolongations/extensions
        if check_extensions:
            extension = await self.db.contract_extensions.find_one({
                "contract_id": active_contract.get("id"),
                "status": {"$in": ["pending", "approved"]}
            })
            
            if extension:
                msg = contract_rule["error_messages"].get("extension_pending", "Prolongation en cours")
                return False, msg, {
                    "has_active_contract": True,
                    "has_extension": True
                }
        
        # Vérifier avenants
        if check_amendments:
            amendment = await self.db.contract_amendments.find_one({
                "contract_id": active_contract.get("id"),
                "status": "active"
            })
            
            if amendment:
                msg = contract_rule["error_messages"].get("amendment_active", "Avenant actif")
                return False, msg, {
                    "has_active_contract": True,
                    "has_amendment": True
                }
        
        # Toutes les conditions sont remplies
        return True, None, {
            "has_active_contract": True,
            "days_remaining": days_remaining,
            "can_apply": True
        }
    
    async def _check_cv_requirement(
        self,
        user_id: str,
        rules: List[Dict]
    ) -> Tuple[bool, Optional[str], Dict]:
        """Vérifier l'exigence de CV (retourne toujours True car upload possible)"""
        cv_rule = next((r for r in rules if r["rule_id"] == "application_cv_requirement"), None)
        
        if not cv_rule:
            return True, None, {"cv_required": False}
        
        conditions = cv_rule["conditions"]
        allow_upload = conditions.get("allow_upload_during_application", True)
        
        # Chercher CV dans les profils
        # Vérifier interim_profiles
        interim_profile = await self.db.interim_profiles.find_one(
            {"user_id": user_id},
            {"_id": 0, "cv_document_id": 1, "document_ids": 1}
        )
        
        has_cv = False
        if interim_profile:
            has_cv = bool(interim_profile.get("cv_document_id"))
        
        # Vérifier candidat_profiles si pas trouvé
        if not has_cv:
            candidat_profile = await self.db.candidat_profiles.find_one(
                {"user_id": user_id},
                {"_id": 0, "cv_document_id": 1, "document_ids": 1}
            )
            if candidat_profile:
                has_cv = bool(candidat_profile.get("cv_document_id"))
        
        # Retourner True car upload autorisé
        return True, None, {
            "cv_required": True,
            "has_cv": has_cv,
            "allow_upload": allow_upload,
            "max_file_size_mb": conditions.get("max_file_size_mb", 5),
            "allowed_formats": conditions.get("allowed_formats", ["pdf", "doc", "docx"])
        }
