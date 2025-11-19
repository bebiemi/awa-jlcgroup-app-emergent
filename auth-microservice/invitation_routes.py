"""
Invitation Routes
Système d'invitation sécurisé pour ajouter des utilisateurs aux entreprises
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
import secrets
import uuid

from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.models import User
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.services.iam_service import IAMService

router = APIRouter(prefix="/invitations", tags=["Invitations"])

# ==================== MODELS ====================

class InvitationCreate(BaseModel):
    """Modèle pour créer une invitation"""
    email: EmailStr
    entreprise_id: str
    profile_code: str = "company_manager"  # Profil par défaut
    message: Optional[str] = None

class BulkInvitationCreate(BaseModel):
    """Modèle pour inviter plusieurs utilisateurs"""
    emails: List[EmailStr]
    entreprise_id: str
    profile_code: str = "company_manager"
    message: Optional[str] = None

class InvitationResponse(BaseModel):
    """Modèle de réponse pour une invitation"""
    id: str
    token: str
    email: str
    entreprise_id: str
    entreprise_name: str
    profile_code: str
    status: str
    created_at: datetime
    expires_at: datetime
    created_by: str

class InvitationAccept(BaseModel):
    """Modèle pour accepter une invitation"""
    username: str
    full_name: str
    password: str
    phone: Optional[str] = None


# ==================== HELPER FUNCTIONS ====================

def generate_secure_token() -> str:
    """Générer un token sécurisé de 32 caractères"""
    return secrets.token_urlsafe(32)


async def send_invitation_email(
    email: str,
    token: str,
    entreprise_name: str,
    inviter_name: str,
    message: Optional[str] = None,
    db: AsyncIOMotorDatabase = None
):
    """
    Envoyer un email d'invitation
    TODO: Implémenter avec le service email existant
    """
    # Pour l'instant, on log juste
    invitation_link = f"https://app.example.com/invitation/{token}"
    
    print(f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📧 EMAIL D'INVITATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    À: {email}
    De: {inviter_name}
    Entreprise: {entreprise_name}
    
    Lien d'invitation: {invitation_link}
    
    Message: {message or 'Aucun message'}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    # TODO: Intégrer avec le service email réel
    # await email_service.send_invitation(...)


# ==================== CREATE INVITATION ====================

@router.post("/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation_data: InvitationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_permission("entreprises.invite_user")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer une invitation pour un utilisateur
    Nécessite: entreprises.invite_user
    """
    # Vérifier que l'entreprise existe
    entreprise = await db.entreprises.find_one(
        {"id": invitation_data.entreprise_id},
        {"_id": 0}
    )
    
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    # Vérifier que l'utilisateur n'existe pas déjà avec cet email
    existing_user = await db.users.find_one({"email": invitation_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Vérifier qu'il n'y a pas d'invitation en attente pour cet email/entreprise
    existing_invitation = await db.invitations.find_one({
        "email": invitation_data.email,
        "entreprise_id": invitation_data.entreprise_id,
        "status": "pending"
    })
    
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Une invitation est déjà en attente pour cet email"
        )
    
    # Générer le token sécurisé
    token = generate_secure_token()
    
    # Créer l'invitation
    invitation_id = str(uuid.uuid4())
    invitation_doc = {
        "id": invitation_id,
        "token": token,
        "email": invitation_data.email,
        "entreprise_id": invitation_data.entreprise_id,
        "entreprise_name": entreprise.get("nom"),
        "profile_code": invitation_data.profile_code,
        "status": "pending",
        "message": invitation_data.message,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),  # 7 jours
        "created_by": current_user.id,
        "created_by_name": current_user.full_name,
    }
    
    await db.invitations.insert_one(invitation_doc)
    
    # Envoyer l'email en arrière-plan
    background_tasks.add_task(
        send_invitation_email,
        email=invitation_data.email,
        token=token,
        entreprise_name=entreprise.get("nom"),
        inviter_name=current_user.full_name,
        message=invitation_data.message,
        db=db
    )
    
    invitation_doc.pop("_id", None)
    return invitation_doc


# ==================== BULK INVITATION ====================

@router.post("/bulk", response_model=List[InvitationResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_invitations(
    invitation_data: BulkInvitationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_permission("entreprises.invite_user")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer plusieurs invitations en une fois
    Nécessite: entreprises.invite_user
    """
    # Vérifier que l'entreprise existe
    entreprise = await db.entreprises.find_one(
        {"id": invitation_data.entreprise_id},
        {"_id": 0}
    )
    
    if not entreprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    created_invitations = []
    
    for email in invitation_data.emails:
        # Vérifier que l'utilisateur n'existe pas déjà
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            print(f"⚠️  User {email} already exists, skipping")
            continue
        
        # Vérifier invitation en attente
        existing_invitation = await db.invitations.find_one({
            "email": email,
            "entreprise_id": invitation_data.entreprise_id,
            "status": "pending"
        })
        
        if existing_invitation:
            print(f"⚠️  Invitation already pending for {email}, skipping")
            continue
        
        # Générer le token
        token = generate_secure_token()
        
        # Créer l'invitation
        invitation_id = str(uuid.uuid4())
        invitation_doc = {
            "id": invitation_id,
            "token": token,
            "email": email,
            "entreprise_id": invitation_data.entreprise_id,
            "entreprise_name": entreprise.get("nom"),
            "profile_code": invitation_data.profile_code,
            "status": "pending",
            "message": invitation_data.message,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "created_by": current_user.id,
            "created_by_name": current_user.full_name,
        }
        
        await db.invitations.insert_one(invitation_doc)
        
        # Envoyer l'email
        background_tasks.add_task(
            send_invitation_email,
            email=email,
            token=token,
            entreprise_name=entreprise.get("nom"),
            inviter_name=current_user.full_name,
            message=invitation_data.message,
            db=db
        )
        
        invitation_doc.pop("_id", None)
        created_invitations.append(invitation_doc)
    
    return created_invitations


# ==================== GET INVITATION BY TOKEN ====================

@router.get("/{token}")
async def get_invitation_by_token(
    token: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer une invitation par son token (pour validation)
    Endpoint public - pas d'authentification requise
    """
    invitation = await db.invitations.find_one(
        {"token": token},
        {"_id": 0}
    )
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation non trouvée"
        )
    
    # Vérifier si l'invitation a expiré
    if invitation["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette invitation a déjà été {invitation['status']}"
        )
    
    if datetime.now(timezone.utc) > invitation["expires_at"]:
        # Marquer comme expirée
        await db.invitations.update_one(
            {"token": token},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation a expiré"
        )
    
    # Récupérer les infos de l'entreprise
    entreprise = await db.entreprises.find_one(
        {"id": invitation["entreprise_id"]},
        {"_id": 0, "nom": 1, "secteur_activite": 1}
    )
    
    return {
        "email": invitation["email"],
        "entreprise_name": invitation["entreprise_name"],
        "entreprise_details": entreprise,
        "profile_code": invitation["profile_code"],
        "expires_at": invitation["expires_at"],
        "message": invitation.get("message")
    }


# ==================== ACCEPT INVITATION ====================

@router.post("/{token}/accept")
async def accept_invitation(
    token: str,
    accept_data: InvitationAccept,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Accepter une invitation et créer le compte utilisateur
    Endpoint public - pas d'authentification requise
    """
    # Récupérer l'invitation
    invitation = await db.invitations.find_one({"token": token})
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation non trouvée"
        )
    
    # Vérifier le statut et l'expiration
    if invitation["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cette invitation a déjà été {invitation['status']}"
        )
    
    if datetime.now(timezone.utc) > invitation["expires_at"]:
        await db.invitations.update_one(
            {"token": token},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation a expiré"
        )
    
    # Vérifier que le username n'existe pas
    existing_user = await db.users.find_one({"username": accept_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    # Vérifier que l'email n'existe pas
    existing_email = await db.users.find_one({"email": invitation["email"]})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Récupérer le profil métier
    profile = await db.profiles.find_one({"code": invitation["profile_code"]})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profil {invitation['profile_code']} non trouvé"
        )
    
    # Créer l'utilisateur
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(accept_data.password)
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "username": accept_data.username,
        "email": invitation["email"],
        "full_name": accept_data.full_name,
        "phone": accept_data.phone,
        "hashed_password": hashed_password,
        "company_id": invitation["entreprise_id"],
        "entreprise_id": invitation["entreprise_id"],
        "profile_ids": [profile["id"]],
        "group_ids": [],
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_via": "invitation"
    }
    
    await db.users.insert_one(user_doc)
    
    # Marquer l'invitation comme acceptée
    await db.invitations.update_one(
        {"token": token},
        {
            "$set": {
                "status": "accepted",
                "accepted_at": datetime.now(timezone.utc),
                "user_id": user_id
            }
        }
    )
    
    return {
        "message": "Compte créé avec succès",
        "user_id": user_id,
        "email": invitation["email"],
        "entreprise_id": invitation["entreprise_id"]
    }


# ==================== LIST INVITATIONS ====================

@router.get("/", response_model=List[InvitationResponse])
async def list_invitations(
    entreprise_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_permission("entreprises.manage")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lister les invitations
    Nécessite: entreprises.manage
    """
    query = {}
    
    if entreprise_id:
        query["entreprise_id"] = entreprise_id
    
    if status:
        query["status"] = status
    
    invitations = await db.invitations.find(query, {"_id": 0}).to_list(None)
    
    return invitations
