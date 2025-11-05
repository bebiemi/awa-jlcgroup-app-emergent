from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, require_admin
from awana_auth.core.reference_models import (
    SystemReference,
    CreateReferenceRequest,
    UpdateReferenceRequest,
    ApplicationSetting,
    CreateSettingRequest,
    BusinessRule
)
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
    """
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
    
    return {"references": references}


@router.post("/references", dependencies=[Depends(require_admin)])
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
    
    # Remove MongoDB _id
    if "_id" in ref_dict:
        del ref_dict["_id"]
    
    return {"reference": ref_dict}


@router.patch("/references/{ref_id}", dependencies=[Depends(require_admin)])
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
    
    updated_ref = await db.system_references.find_one({"id": ref_id})
    if updated_ref and "_id" in updated_ref:
        updated_ref["_id"] = str(updated_ref["_id"])
    
    return {"reference": updated_ref}


@router.delete("/references/{ref_id}", dependencies=[Depends(require_admin)])
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
    
    # Convertir les valeurs en types appropriés
    for setting in settings:
        setting_obj = ApplicationSetting(**setting)
        setting["typed_value"] = setting_obj.get_typed_value()
    
    return {"settings": settings}


@router.post("/settings", dependencies=[Depends(require_admin)])
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
    await db.application_settings.insert_one(app_setting.dict())
    
    return {"setting": app_setting.dict()}


@router.patch("/settings/{key}", dependencies=[Depends(require_admin)])
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
    return {"setting": updated}


# ==================== RÈGLES MÉTIER ====================

@router.get("/rules", dependencies=[Depends(require_admin)])
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
    return {"rules": rules}


@router.post("/rules", dependencies=[Depends(require_admin)])
async def create_business_rule(
    rule: BusinessRule,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer une règle métier (Admin uniquement)
    """
    rule.id = str(uuid.uuid4())
    await db.business_rules.insert_one(rule.dict())
    return {"rule": rule.dict()}


# ==================== CACHE ====================

@router.post("/cache/clear", dependencies=[Depends(require_admin)])
async def clear_cache():
    """
    Vider le cache des configurations
    À appeler après modification des référentiels
    """
    # Implémenter la logique de cache (Redis, mémoire, etc.)
    return {"message": "Cache vidé"}
