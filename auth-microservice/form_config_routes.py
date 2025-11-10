"""
Form Configuration Routes
Admin endpoints to manage dynamic forms, workflows, and reference data
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional, List

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.core.config_models import (
    FormSchemaCreate,
    FormSchemaResponse,
    WorkflowConfigCreate,
    WorkflowConfigResponse,
    ReferenceDataCreate,
    ReferenceDataResponse,
    ConfigListResponse,
    FormField,
    StatusConfig,
    ReferenceDataItem,
)
from awana_auth.core.audit_models import AuditAction, AuditSeverity
from awana_auth.services.audit_service import AuditService

router = APIRouter()


async def get_current_user_info(current_user: dict) -> tuple:
    """Extract user info from current_user"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    user_name = current_user.get("full_name") or current_user.get("username") if isinstance(current_user, dict) else getattr(current_user, "full_name", current_user.username)
    if isinstance(current_user, dict):
        user_role = current_user.get("roles", [])[0] if current_user.get("roles") else "admin"
    else:
        user_role = current_user.roles[0] if current_user.roles else "admin"
    return user_id, user_name, user_role


# ==================== FORM SCHEMAS ====================

@router.post("/forms", response_model=FormSchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_form_schema(
    schema: FormSchemaCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.FORMS_MANAGE))
):
    """
    Create or update form schema
    Admin only
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    # Check if schema already exists
    existing = await db.form_schemas.find_one({"form_type": schema.form_type})
    
    now = datetime.now(timezone.utc)
    schema_id = existing["id"] if existing else str(uuid.uuid4())
    
    # Convert fields to dict
    fields_dict = [field.dict() for field in schema.fields]
    
    schema_doc = {
        "id": schema_id,
        "form_type": schema.form_type,
        "version": "1.0",
        "fields": fields_dict,
        "groups": schema.groups,
        "metadata": schema.metadata,
        "created_at": existing["created_at"] if existing else now,
        "updated_at": now,
    }
    
    if existing:
        await db.form_schemas.update_one(
            {"id": schema_id},
            {"$set": schema_doc}
        )
        action = "updated"
    else:
        await db.form_schemas.insert_one(schema_doc)
        action = "created"
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.FORM_SCHEMA_UPDATED,
        entity_type="form_schema",
        entity_id=schema_id,
        entity_label=schema.form_type,
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Form schema {action}: {schema.form_type}",
        metadata={"form_type": schema.form_type, "fields_count": len(schema.fields)}
    )
    
    schema_doc.pop("_id", None)
    return FormSchemaResponse(**schema_doc)


@router.get("/forms", response_model=ConfigListResponse)
async def list_form_schemas(
    form_type: Optional[str] = Query(None, description="Filter by form type"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.CONFIG_READ))
):
    """Get all form schemas"""
    query = {}
    if form_type:
        query["form_type"] = form_type
    
    cursor = db.form_schemas.find(query)
    schemas = await cursor.to_list(length=None)
    
    for schema in schemas:
        schema.pop("_id", None)
    
    return ConfigListResponse(
        items=[FormSchemaResponse(**s) for s in schemas],
        total=len(schemas),
        config_type="forms"
    )


@router.get("/forms/{form_type}", response_model=FormSchemaResponse)
async def get_form_schema(
    form_type: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.CONFIG_READ))
):
    """Get form schema by type"""
    schema = await db.form_schemas.find_one({"form_type": form_type})
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form schema '{form_type}' not found"
        )
    
    schema.pop("_id", None)
    return FormSchemaResponse(**schema)


@router.delete("/forms/{form_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form_schema(
    form_type: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.FORMS_MANAGE))
):
    """Delete form schema"""
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    result = await db.form_schemas.delete_one({"form_type": form_type})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form schema '{form_type}' not found"
        )
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.CONFIG_UPDATED,
        entity_type="form_schema",
        entity_id=form_type,
        entity_label=form_type,
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Form schema deleted: {form_type}",
        severity=AuditSeverity.WARNING
    )


# ==================== WORKFLOW CONFIGS ====================

@router.post("/workflows", response_model=WorkflowConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_config(
    workflow: WorkflowConfigCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.FORMS_MANAGE))
):
    """
    Create or update workflow configuration
    Admin only
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    # Check if workflow already exists
    existing = await db.workflow_configs.find_one({"entity_type": workflow.entity_type})
    
    now = datetime.now(timezone.utc)
    workflow_id = existing["id"] if existing else str(uuid.uuid4())
    
    # Convert statuses to dict
    statuses_dict = [status.dict() for status in workflow.statuses]
    
    workflow_doc = {
        "id": workflow_id,
        "entity_type": workflow.entity_type,
        "version": "1.0",
        "statuses": statuses_dict,
        "initial_status": workflow.initial_status,
        "metadata": workflow.metadata,
        "created_at": existing["created_at"] if existing else now,
        "updated_at": now,
    }
    
    if existing:
        await db.workflow_configs.update_one(
            {"id": workflow_id},
            {"$set": workflow_doc}
        )
        action = "updated"
    else:
        await db.workflow_configs.insert_one(workflow_doc)
        action = "created"
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.CONFIG_UPDATED,
        entity_type="workflow_config",
        entity_id=workflow_id,
        entity_label=workflow.entity_type,
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Workflow config {action}: {workflow.entity_type}",
        metadata={"entity_type": workflow.entity_type, "statuses_count": len(workflow.statuses)}
    )
    
    workflow_doc.pop("_id", None)
    return WorkflowConfigResponse(**workflow_doc)


@router.get("/workflows", response_model=ConfigListResponse)
async def list_workflow_configs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.CONFIG_READ))
):
    """Get all workflow configurations"""
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    
    cursor = db.workflow_configs.find(query)
    workflows = await cursor.to_list(length=None)
    
    for workflow in workflows:
        workflow.pop("_id", None)
    
    return ConfigListResponse(
        items=[WorkflowConfigResponse(**w) for w in workflows],
        total=len(workflows),
        config_type="workflows"
    )


@router.get("/workflows/{entity_type}", response_model=WorkflowConfigResponse)
async def get_workflow_config(
    entity_type: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.CONFIG_READ))
):
    """Get workflow configuration by entity type"""
    workflow = await db.workflow_configs.find_one({"entity_type": entity_type})
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow config for '{entity_type}' not found"
        )
    
    workflow.pop("_id", None)
    return WorkflowConfigResponse(**workflow)


# ==================== REFERENCE DATA ====================

@router.post("/references", response_model=ReferenceDataResponse, status_code=status.HTTP_201_CREATED)
async def create_reference_data(
    reference: ReferenceDataCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.FORMS_MANAGE))
):
    """
    Create or update reference data
    Admin only
    """
    user_id, user_name, user_role = await get_current_user_info(current_user)
    
    # Check if reference data already exists
    existing = await db.reference_data.find_one({"reference_type": reference.reference_type})
    
    now = datetime.now(timezone.utc)
    reference_id = existing["id"] if existing else str(uuid.uuid4())
    
    # Convert items to dict
    items_dict = [item.dict() for item in reference.items]
    
    reference_doc = {
        "id": reference_id,
        "reference_type": reference.reference_type,
        "version": "1.0",
        "items": items_dict,
        "metadata": reference.metadata,
        "created_at": existing["created_at"] if existing else now,
        "updated_at": now,
    }
    
    if existing:
        await db.reference_data.update_one(
            {"id": reference_id},
            {"$set": reference_doc}
        )
        action = "updated"
    else:
        await db.reference_data.insert_one(reference_doc)
        action = "created"
    
    # Log audit
    audit_service = AuditService(db)
    await audit_service.log_event(
        action=AuditAction.CONFIG_UPDATED,
        entity_type="reference_data",
        entity_id=reference_id,
        entity_label=reference.reference_type,
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        description=f"Reference data {action}: {reference.reference_type}",
        metadata={"reference_type": reference.reference_type, "items_count": len(reference.items)}
    )
    
    reference_doc.pop("_id", None)
    return ReferenceDataResponse(**reference_doc)


@router.get("/references", response_model=ConfigListResponse)
async def list_reference_data(
    reference_type: Optional[str] = Query(None, description="Filter by reference type"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.CONFIG_READ))
):
    """Get all reference data"""
    query = {}
    if reference_type:
        query["reference_type"] = reference_type
    
    cursor = db.reference_data.find(query)
    references = await cursor.to_list(length=None)
    
    for reference in references:
        reference.pop("_id", None)
    
    return ConfigListResponse(
        items=[ReferenceDataResponse(**r) for r in references],
        total=len(references),
        config_type="references"
    )


@router.get("/references/{reference_type}", response_model=ReferenceDataResponse)
async def get_reference_data(
    reference_type: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(require_permission(IAMPermissions.CONFIG_READ))
):
    """Get reference data by type"""
    reference = await db.reference_data.find_one({"reference_type": reference_type})
    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reference data '{reference_type}' not found"
        )
    
    reference.pop("_id", None)
    return ReferenceDataResponse(**reference)
