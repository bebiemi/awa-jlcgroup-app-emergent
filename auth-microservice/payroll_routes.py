"""
Payroll Routes - Secure exchange of timesheets and payslips data
Public surface: none. All endpoints require explicit IAM permissions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from pydantic import BaseModel

from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.core.models import User
from awana_auth.dependencies.permission_dependencies import require_permission, require_any_permission

router = APIRouter(prefix="/api/payroll", tags=["payroll"])


# ==================== MODELS ====================

class Timesheet(BaseModel):
  id: str
  user_id: str
  period_start: datetime
  period_end: datetime
  hours_worked: float
  status: str
  created_at: datetime
  updated_at: datetime
  validated_at: Optional[datetime] = None
  validator_id: Optional[str] = None


class TimesheetCreate(BaseModel):
  period_start: datetime
  period_end: datetime
  hours_worked: float
  notes: Optional[str] = None


class TimesheetValidation(BaseModel):
  status: str = "validated"
  comment: Optional[str] = None


class PayslipMetadata(BaseModel):
  id: str
  user_id: str
  period: str
  status: str
  amount_net: Optional[float] = None
  available_at: datetime
  requested_at: Optional[datetime] = None


class PayslipDownloadUrl(BaseModel):
  url: str
  expires_at: datetime


class PayslipRequest(BaseModel):
  period: str
  reason: Optional[str] = None


class PayrollShareRequest(BaseModel):
  user_id: str
  period_start: datetime
  period_end: datetime
  data_types: List[str] = ["timesheets", "payslips"]
  target_app: str
  reason: Optional[str] = None


class PayrollSettings(BaseModel):
  enable_download_url: bool = True
  download_url_ttl_minutes: int = 30
  allow_public_link: bool = False
  data_sharing_allowed_apps: List[str] = []


# ==================== TIMESHEETS ====================

@router.get("/timesheets/my", response_model=List[Timesheet])
async def get_my_timesheets(
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.timesheets.read"))
):
  """
  Liste des feuilles de temps de l'intérimaire (scope own).
  """
  timesheets = await db.timesheets.find(
      {"user_id": current_user.id},
      {"_id": 0}
  ).sort("period_start", -1).to_list(200)
  return [Timesheet(**ts) for ts in timesheets]


@router.post("/timesheets/my", response_model=Timesheet, status_code=status.HTTP_201_CREATED)
async def submit_timesheet(
    payload: TimesheetCreate,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.timesheets.submit"))
):
  """
  Soumission d'une feuille de temps par l'intérimaire.
  """
  now = datetime.now(timezone.utc)
  ts_id = str(uuid4())
  ts_doc = {
      "id": ts_id,
      "user_id": current_user.id,
      "period_start": payload.period_start,
      "period_end": payload.period_end,
      "hours_worked": payload.hours_worked,
      "notes": payload.notes,
      "status": "submitted",
      "created_at": now,
      "updated_at": now,
  }
  await db.timesheets.insert_one(ts_doc)
  return Timesheet(**ts_doc)


@router.get("/timesheets", response_model=List[Timesheet])
async def list_timesheets(
    user_id: Optional[str] = Query(None, description="Filtrer par utilisateur"),
    status_filter: Optional[str] = Query(None, description="Filtrer par statut"),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.timesheets.read.all"))
):
  """
  Vue RH/Paie : liste des timesheets sur périmètre autorisé (all).
  """
  query = {}
  if user_id:
    query["user_id"] = user_id
  if status_filter:
    query["status"] = status_filter
  timesheets = await db.timesheets.find(query, {"_id": 0}).sort("period_start", -1).to_list(500)
  return [Timesheet(**ts) for ts in timesheets]


@router.post("/timesheets/{timesheet_id}/validate", response_model=Timesheet)
async def validate_timesheet(
    timesheet_id: str,
    payload: TimesheetValidation,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.timesheets.validate"))
):
  """
  Validation RH/Paie d'une feuille de temps.
  """
  ts = await db.timesheets.find_one({"id": timesheet_id})
  if not ts:
    raise HTTPException(status_code=404, detail="Timesheet not found")
  now = datetime.now(timezone.utc)
  await db.timesheets.update_one(
      {"id": timesheet_id},
      {"$set": {
          "status": payload.status,
          "validation_comment": payload.comment,
          "validated_at": now,
          "validator_id": current_user.id,
          "updated_at": now,
      }}
  )
  updated = await db.timesheets.find_one({"id": timesheet_id}, {"_id": 0})
  return Timesheet(**updated)


# ==================== PAYSLIPS ====================

@router.post("/slips/requests", status_code=status.HTTP_202_ACCEPTED)
async def request_payslip(
    payload: PayslipRequest,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.slips.request"))
):
  """
  Intérimaire : demande de mise à dispo d'une fiche de paie pour une période.
  """
  req_id = str(uuid4())
  now = datetime.now(timezone.utc)
  doc = {
      "id": req_id,
      "user_id": current_user.id,
      "period": payload.period,
      "reason": payload.reason,
      "status": "requested",
      "requested_at": now,
  }
  await db.payslip_requests.insert_one(doc)
  return {"request_id": req_id, "status": "requested"}


@router.get("/slips", response_model=List[PayslipMetadata])
async def list_payslips(
    user_id: Optional[str] = Query(None),
    db = Depends(get_database),
    current_user: User = Depends(require_any_permission(["payroll.slips.read", "payroll.slips.read.all"]))
):
  """
  Liste des fiches de paie :
  - si permission read (own) : restreint à l'utilisateur courant
  - si read.all : peut filtrer par user_id
  """
  query = {}
  if "payroll.slips.read.all" in getattr(current_user, "permissions", []):
    if user_id:
      query["user_id"] = user_id
  else:
    query["user_id"] = current_user.id

  slips = await db.payslips.find(query, {"_id": 0}).sort("available_at", -1).to_list(200)
  return [PayslipMetadata(**s) for s in slips]


@router.get("/slips/{slip_id}/metadata", response_model=PayslipMetadata)
async def get_payslip_metadata(
    slip_id: str,
    db = Depends(get_database),
    current_user: User = Depends(require_any_permission(["payroll.slips.read", "payroll.slips.read.all"]))
):
  slip = await db.payslips.find_one({"id": slip_id}, {"_id": 0})
  if not slip:
    raise HTTPException(status_code=404, detail="Payslip not found")
  # Vérifier ownership si pas read.all
  if "payroll.slips.read.all" not in getattr(current_user, "permissions", []) and slip.get("user_id") != current_user.id:
    raise HTTPException(status_code=403, detail="Access denied")
  return PayslipMetadata(**slip)


@router.post("/slips/{slip_id}/download-url", response_model=PayslipDownloadUrl)
async def generate_download_url(
    slip_id: str,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.slips.download"))
):
  """
  Génère une URL signée courte durée pour télécharger la fiche.
  (Ici, URL simulée; à remplacer par un vrai générateur de lien signé)
  """
  slip = await db.payslips.find_one({"id": slip_id})
  if not slip:
    raise HTTPException(status_code=404, detail="Payslip not found")

  expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
  signed_url = f"https://download.jlcgroup.org/payslips/{slip_id}?token={uuid4()}"
  return PayslipDownloadUrl(url=signed_url, expires_at=expires_at)


# ==================== DATA SHARING ====================

@router.post("/data/share")
async def share_payroll_data(
    payload: PayrollShareRequest,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.data.share"))
):
  """
  Mise à disposition de données (timesheets/payslips) pour apps partenaires.
  Implémentation à adapter vers callbacks/queues selon le SI cible.
  """
  share_id = str(uuid4())
  now = datetime.now(timezone.utc)
  doc = {
      "id": share_id,
      "user_id": payload.user_id,
      "period_start": payload.period_start,
      "period_end": payload.period_end,
      "data_types": payload.data_types,
      "target_app": payload.target_app,
      "reason": payload.reason,
      "created_at": now,
      "created_by": current_user.id,
  }
  await db.payroll_shares.insert_one(doc)
  return {"share_id": share_id, "status": "queued"}


# ==================== AUDIT ====================

@router.get("/audit/slips")
async def audit_slip_access(
    user_id: Optional[str] = Query(None),
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.audit.read"))
):
  """
  Journal des accès/téléchargements de fiches de paie.
  """
  query = {}
  if user_id:
    query["user_id"] = user_id
  logs = await db.payslip_audit.find(query, {"_id": 0}).sort("timestamp", -1).to_list(500)
  return {"items": logs, "total": len(logs)}


# ==================== SETTINGS (ADMIN UI) ====================

@router.get("/settings", response_model=PayrollSettings)
async def get_payroll_settings(
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.configure"))
):
  """
  Paramètres administrables (UI) pour le module paie.
  """
  settings = await db.payroll_settings.find_one({}, {"_id": 0})
  if not settings:
    return PayrollSettings()
  return PayrollSettings(**settings)


@router.put("/settings", response_model=PayrollSettings)
async def update_payroll_settings(
    payload: PayrollSettings,
    db = Depends(get_database),
    current_user: User = Depends(require_permission("payroll.configure"))
):
  """
  Mise à jour des paramètres (accès admin uniquement).
  """
  doc = payload.dict()
  await db.payroll_settings.delete_many({})
  await db.payroll_settings.insert_one(doc)
  return payload
