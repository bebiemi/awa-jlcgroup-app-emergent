from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.reference_models import (
    SystemReference,
    CreateReferenceRequest,
    UpdateReferenceRequest,
    ApplicationSetting,
    CreateSettingRequest,
    BusinessRule
)
from awana_auth.core.cache import reference_cache, get_cache_key
import uuid
from datetime import datetime

router = APIRouter(prefix="/config", tags=["Configuration"])


# ==================== RÉFÉRENTIELS ====================

@router.get("/references")
async def get_references(
    category: Optional[str] = None,
    parent_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les référentiels
    Public (utilisé côté frontend)
    Avec cache de 30 minutes
    """
    # Tenter de récupérer depuis le cache (seulement si category est fournie)
    if category and parent_id is None:
        cache_key = get_cache_key(category, is_active)
        cached_data = await reference_cache.get(cache_key)
        if cached_data is not None:
            return {"references": cached_data}
    
    # Si pas en cache, récupérer depuis la BD
    query = {}
    if category:
        query["category"] = category
    if parent_id:
        query["parent_id"] = parent_id
    if is_active is not None:
        query["is_active"] = is_active
    
    references = await db.system_references.find(query).sort("order", 1).to_list(length=None)
    
    # Convertir les ObjectId en str pour JSON serialization
    for ref in references:
        if "_id" in ref:
            ref["_id"] = str(ref["_id"])
    
    # Mettre en cache si category fournie
    if category and parent_id is None:
        cache_key = get_cache_key(category, is_active)
        await reference_cache.set(cache_key, references)
    
    return {"references": references}


@router.get("/all")
async def get_all_config(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer toute la configuration structurée pour le frontend
    Public (utilisé par useAppConfig)
    Optimisé avec cache
    """
    from awana_auth.core.config_manager import get_config
    config_manager = get_config()
    
    # Charger les rôles depuis la configuration YAML
    roles = {
        "admin": config_manager.get("security.roles.admin"),
        "super_admin": config_manager.get("security.roles.super_admin"),
        "company": config_manager.get("security.roles.company"),
        "interim": config_manager.get("security.roles.interim"),
        "agency": config_manager.get("security.roles.agency"),
        "commercial": config_manager.get("security.roles.commercial"),
        "validator": config_manager.get("security.roles.validator"),
        "all": config_manager.get("security.roles.all")
    }
    
    # Charger les statuts utilisateur
    user_statuses = {
        "active": config_manager.get("security.user_statuses.active"),
        "pending": config_manager.get("security.user_statuses.pending"),
        "suspended": config_manager.get("security.user_statuses.suspended"),
        "deleted": config_manager.get("security.user_statuses.deleted"),
        "blocked": config_manager.get("security.user_statuses.blocked"),
        "all": config_manager.get("security.user_statuses.all")
    }
    
    # Charger les référentiels dynamiques depuis la BD
    mission_statuses_refs = await db.system_references.find(
        {"category": "mission_statuses", "is_active": True}
    ).sort("order", 1).to_list(length=None)
    
    application_statuses_refs = await db.system_references.find(
        {"category": "application_statuses", "is_active": True}
    ).sort("order", 1).to_list(length=None)
    
    validation_statuses_refs = await db.system_references.find(
        {"category": "validation_statuses", "is_active": True}
    ).sort("order", 1).to_list(length=None)
    
    validation_types_refs = await db.system_references.find(
        {"category": "validation_types", "is_active": True}
    ).sort("order", 1).to_list(length=None)
    
    contract_types_refs = await db.system_references.find(
        {"category": "contract_types", "is_active": True}
    ).sort("order", 1).to_list(length=None)
    
    # Structurer la réponse
    return {
        "roles": roles,
        "user_statuses": user_statuses,
        "mission_statuses": [ref["code"] for ref in mission_statuses_refs],
        "application_statuses": [ref["code"] for ref in application_statuses_refs],
        "validation_statuses": [ref["code"] for ref in validation_statuses_refs],
        "validation_types": [ref["code"] for ref in validation_types_refs],
        "contract_types": [ref["code"] for ref in contract_types_refs],
        "permissions": {
            "mission": {
                "create": config_manager.get("workflows.mission.permissions.create"),
                "view_all": config_manager.get("workflows.mission.permissions.view_all"),
                "publish": config_manager.get("workflows.mission.permissions.publish"),
                "edit": config_manager.get("workflows.mission.permissions.edit"),
                "delete": config_manager.get("workflows.mission.permissions.delete"),
            },
            "application": {
                "view_all": config_manager.get("workflows.application.permissions.view_all"),
                "manage": config_manager.get("workflows.application.permissions.manage"),
                "view_own": config_manager.get("workflows.application.permissions.view_own"),
            },
            "validation": {
                "validator_roles": config_manager.get("workflows.validation.permissions.validator_roles"),
                "view_all": config_manager.get("workflows.validation.permissions.view_all"),
            }
        }
    }


@router.post("/references", dependencies=[Depends(require_permission("references.manage"))])
async def create_reference(
    ref: CreateReferenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un nouveau référentiel (Admin uniquement)
    """
    # Vérifier unicité code dans la catégorie
    existing = await db.system_references.find_one({
        "category": ref.category,
        "code": ref.code
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le code '{ref.code}' existe déjà dans la catégorie '{ref.category}'"
        )
    
    reference = SystemReference(
        **ref.dict(),
        id=str(uuid.uuid4())
    )
    
    ref_dict = reference.dict()
    await db.system_references.insert_one(ref_dict)
    
    # Invalider le cache pour cette catégorie
    await reference_cache.invalidate(f"refs:{ref.category}")
    await reference_cache.invalidate(f"refs:{ref.category}:active=True")
    await reference_cache.invalidate(f"refs:{ref.category}:active=False")
    
    # Remove MongoDB _id
    if "_id" in ref_dict:
        del ref_dict["_id"]
    
    return {"reference": ref_dict}


@router.patch("/references/{ref_id}", dependencies=[Depends(require_permission("references.manage"))])
async def update_reference(
    ref_id: str,
    update: UpdateReferenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un référentiel (Admin uniquement)
    """
    ref = await db.system_references.find_one({"id": ref_id})
    if not ref:
        raise HTTPException(status_code=404, detail="Référentiel non trouvé")
    
    if ref.get("is_system") and update.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les référentiels système ne peuvent pas être désactivés"
        )
    
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.system_references.update_one(
        {"id": ref_id},
        {"$set": update_data}
    )
    
    # Invalider le cache pour cette catégorie
    category = ref.get("category")
    if category:
        await reference_cache.invalidate(f"refs:{category}")
        await reference_cache.invalidate(f"refs:{category}:active=True")
        await reference_cache.invalidate(f"refs:{category}:active=False")
    
    updated_ref = await db.system_references.find_one({"id": ref_id})
    if updated_ref and "_id" in updated_ref:
        updated_ref["_id"] = str(updated_ref["_id"])
    
    return {"reference": updated_ref}


@router.delete("/references/{ref_id}", dependencies=[Depends(require_permission("references.manage"))])
async def delete_reference(
    ref_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Supprimer un référentiel (Admin uniquement)
    Impossible pour les référentiels système
    """
    ref = await db.system_references.find_one({"id": ref_id})
    if not ref:
        raise HTTPException(status_code=404, detail="Référentiel non trouvé")
    
    if ref.get("is_system"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les référentiels système ne peuvent pas être supprimés"
        )
    
    # Vérifier qu'il n'est pas utilisé (exemple pour les rôles)
    if ref["category"] == "roles":
        users_count = await db.users.count_documents({"roles": ref["code"]})
        if users_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ce rôle est utilisé par {users_count} utilisateur(s)"
            )
    
    await db.system_references.delete_one({"id": ref_id})
    
    # Invalider le cache pour cette catégorie
    category = ref.get("category")
    if category:
        await reference_cache.invalidate(f"refs:{category}")
        await reference_cache.invalidate(f"refs:{category}:active=True")
        await reference_cache.invalidate(f"refs:{category}:active=False")
    
    return {"message": "Référentiel supprimé"}


# ==================== PARAMÈTRES ====================

@router.get("/settings")
async def get_settings(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les paramètres
    Si is_public=True, accessible sans authentification
    """
    query = {}
    if category:
        query["category"] = category
    if is_public is not None:
        query["is_public"] = is_public
    
    settings = await db.application_settings.find(query).to_list(length=None)
    
    # Convertir les valeurs en types appropriés et ObjectId
    for setting in settings:
        if "_id" in setting:
            setting["_id"] = str(setting["_id"])
        setting_obj = ApplicationSetting(**setting)
        setting["typed_value"] = setting_obj.get_typed_value()
    
    return {"settings": settings}


@router.post("/settings", dependencies=[Depends(require_permission("config.manage"))])
async def create_setting(
    setting: CreateSettingRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un paramètre (Admin uniquement)
    """
    existing = await db.application_settings.find_one({"key": setting.key})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le paramètre '{setting.key}' existe déjà"
        )
    
    app_setting = ApplicationSetting(**setting.dict(), id=str(uuid.uuid4()))
    setting_dict = app_setting.dict()
    await db.application_settings.insert_one(setting_dict)
    
    if "_id" in setting_dict:
        del setting_dict["_id"]
    
    return {"setting": setting_dict}


@router.patch("/settings/{key}", dependencies=[Depends(require_permission("config.manage"))])
async def update_setting(
    key: str,
    value: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un paramètre (Admin uniquement)
    """
    setting = await db.application_settings.find_one({"key": key})
    if not setting:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    
    await db.application_settings.update_one(
        {"key": key},
        {"$set": {"value": value, "updated_at": datetime.utcnow()}}
    )
    
    updated = await db.application_settings.find_one({"key": key})
    if updated and "_id" in updated:
        updated["_id"] = str(updated["_id"])
    
    return {"setting": updated}


# ==================== RÈGLES MÉTIER ====================

@router.get("/rules", dependencies=[Depends(require_permission("rules.manage"))])
async def get_business_rules(
    rule_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les règles métier (Admin uniquement)
    """
    query = {}
    if rule_type:
        query["rule_type"] = rule_type
    if is_active is not None:
        query["is_active"] = is_active
    
    rules = await db.business_rules.find(query).sort("priority", 1).to_list(length=None)
    
    # Convertir les ObjectId en str
    for rule in rules:
        if "_id" in rule:
            rule["_id"] = str(rule["_id"])
    
    return {"rules": rules}


@router.post("/rules", dependencies=[Depends(require_permission("rules.manage"))])
async def create_business_rule(
    rule: BusinessRule,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer une règle métier (Admin uniquement)
    """
    rule.id = str(uuid.uuid4())
    rule_dict = rule.dict()
    await db.business_rules.insert_one(rule_dict)
    
    if "_id" in rule_dict:
        del rule_dict["_id"]
    
    return {"rule": rule_dict}


# ==================== CACHE ====================

@router.post("/cache/clear", dependencies=[Depends(require_admin)])
async def clear_cache():
    """
    Vider le cache des configurations
    À appeler après modification des référentiels
    """
    await reference_cache.clear()
    return {"message": "Cache vidé avec succès"}
