"""
Support Ticket Routes - Messagerie pour contacter JLC
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4

from awana_auth.core.dependencies import get_current_user, get_database
from awana_auth.dependencies.permission_dependencies import require_permission

router = APIRouter(prefix="/support", tags=["Support"])


# ==================== Models ====================

class TicketCategory(str):
    """Catégories de tickets"""
    TECHNICAL = "technical"
    COMMERCIAL = "commercial"
    HR = "hr"
    GENERAL = "general"
    BUG = "bug"
    FEATURE = "feature"


class TicketStatus(str):
    """Statuts de tickets"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_USER = "waiting_user"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str):
    """Priorités de tickets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCreate(BaseModel):
    subject: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)
    category: str = Field(..., description="Category: technical, commercial, hr, general, bug, feature")
    priority: str = Field(default="medium", description="Priority: low, medium, high, urgent")


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None


class MessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = Field(default=False, description="Internal note (not visible to user)")


class Ticket(BaseModel):
    id: str
    user_id: str
    user_email: str
    user_name: Optional[str] = None
    subject: str
    category: str
    priority: str
    status: str
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    closed_at: Optional[str] = None
    message_count: int = 0


class Message(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    user_email: str
    user_name: Optional[str] = None
    message: str
    is_internal: bool = False
    created_at: str


# ==================== Routes ====================

@router.post("/tickets", status_code=status.HTTP_201_CREATED, response_model=Ticket)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Créer un nouveau ticket de support"""
    
    # Valider la catégorie
    valid_categories = ["technical", "commercial", "hr", "general", "bug", "feature"]
    if ticket_data.category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Valider la priorité
    valid_priorities = ["low", "medium", "high", "urgent"]
    if ticket_data.priority not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        )
    
    ticket_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Créer le ticket
    ticket = {
        "id": ticket_id,
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "user_name": current_user.get("full_name"),
        "subject": ticket_data.subject,
        "category": ticket_data.category,
        "priority": ticket_data.priority,
        "status": "open",
        "assigned_to": None,
        "assigned_to_name": None,
        "created_at": now,
        "updated_at": now,
        "resolved_at": None,
        "closed_at": None,
        "message_count": 1
    }
    
    await db.support_tickets.insert_one(ticket)
    
    # Créer le premier message
    message = {
        "id": str(uuid4()),
        "ticket_id": ticket_id,
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "user_name": current_user.get("full_name"),
        "message": ticket_data.message,
        "is_internal": False,
        "created_at": now
    }
    
    await db.support_messages.insert_one(message)
    
    # TODO: Envoyer une notification email à l'équipe support
    
    return Ticket(**{k: v for k, v in ticket.items() if k != '_id'})


@router.get("/tickets", response_model=List[Ticket])
async def list_tickets(
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Lister les tickets de support de l'utilisateur connecté"""
    
    query = {"user_id": current_user["id"]}
    
    if status_filter:
        query["status"] = status_filter
    
    if category:
        query["category"] = category
    
    tickets = await db.support_tickets.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [Ticket(**ticket) for ticket in tickets]


@router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Récupérer un ticket spécifique"""
    
    ticket = await db.support_tickets.find_one(
        {"id": ticket_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return Ticket(**ticket)


@router.post("/tickets/{ticket_id}/messages", status_code=status.HTTP_201_CREATED, response_model=Message)
async def add_message(
    ticket_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Ajouter un message à un ticket"""
    
    # Vérifier que le ticket existe et appartient à l'utilisateur
    ticket = await db.support_tickets.find_one(
        {"id": ticket_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Vérifier que le ticket n'est pas fermé
    if ticket["status"] == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add message to a closed ticket"
        )
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Créer le message
    message = {
        "id": str(uuid4()),
        "ticket_id": ticket_id,
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "user_name": current_user.get("full_name"),
        "message": message_data.message,
        "is_internal": False,  # Les utilisateurs ne peuvent pas créer de notes internes
        "created_at": now
    }
    
    await db.support_messages.insert_one(message)
    
    # Mettre à jour le ticket
    await db.support_tickets.update_one(
        {"id": ticket_id},
        {
            "$set": {"updated_at": now},
            "$inc": {"message_count": 1}
        }
    )
    
    # Si le ticket était en attente de l'utilisateur, le repasser en cours
    if ticket["status"] == "waiting_user":
        await db.support_tickets.update_one(
            {"id": ticket_id},
            {"$set": {"status": "in_progress"}}
        )
    
    # TODO: Envoyer une notification email à l'équipe support
    
    return Message(**{k: v for k, v in message.items() if k != '_id'})


@router.get("/tickets/{ticket_id}/messages", response_model=List[Message])
async def list_messages(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Lister les messages d'un ticket"""
    
    # Vérifier que le ticket existe et appartient à l'utilisateur
    ticket = await db.support_tickets.find_one(
        {"id": ticket_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Récupérer les messages (exclure les notes internes)
    messages = await db.support_messages.find(
        {"ticket_id": ticket_id, "is_internal": False},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    return [Message(**msg) for msg in messages]


@router.patch("/tickets/{ticket_id}/close", response_model=Ticket)
async def close_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Fermer un ticket (utilisateur uniquement)"""
    
    # Vérifier que le ticket existe et appartient à l'utilisateur
    ticket = await db.support_tickets.find_one(
        {"id": ticket_id, "user_id": current_user["id"]},
        {"_id": 0}
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if ticket["status"] == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already closed"
        )
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Fermer le ticket
    await db.support_tickets.update_one(
        {"id": ticket_id},
        {
            "$set": {
                "status": "closed",
                "closed_at": now,
                "updated_at": now
            }
        }
    )
    
    # Récupérer le ticket mis à jour
    updated_ticket = await db.support_tickets.find_one(
        {"id": ticket_id},
        {"_id": 0}
    )
    
    return Ticket(**updated_ticket)


# ==================== Admin Routes ====================

@router.get("/admin/tickets", response_model=List[Ticket])
async def admin_list_tickets(
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(require_permission("support.manage")),
    db = Depends(get_database)
):
    """[Admin] Lister tous les tickets de support"""
    
    query = {}
    
    if status_filter:
        query["status"] = status_filter
    
    if category:
        query["category"] = category
    
    if priority:
        query["priority"] = priority
    
    if assigned_to:
        query["assigned_to"] = assigned_to
    
    tickets = await db.support_tickets.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [Ticket(**ticket) for ticket in tickets]


@router.patch("/admin/tickets/{ticket_id}", response_model=Ticket)
async def admin_update_ticket(
    ticket_id: str,
    update_data: TicketUpdate,
    current_user: dict = Depends(require_permission("support.manage")),
    db = Depends(get_database)
):
    """[Admin] Mettre à jour un ticket"""
    
    # Vérifier que le ticket existe
    ticket = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Construire les mises à jour
    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if update_data.status:
        valid_statuses = ["open", "in_progress", "waiting_user", "resolved", "closed"]
        if update_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        updates["status"] = update_data.status
        
        if update_data.status == "resolved" and not ticket.get("resolved_at"):
            updates["resolved_at"] = datetime.now(timezone.utc).isoformat()
        
        if update_data.status == "closed" and not ticket.get("closed_at"):
            updates["closed_at"] = datetime.now(timezone.utc).isoformat()
    
    if update_data.priority:
        valid_priorities = ["low", "medium", "high", "urgent"]
        if update_data.priority not in valid_priorities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
            )
        updates["priority"] = update_data.priority
    
    if update_data.assigned_to:
        # Vérifier que l'utilisateur existe
        assigned_user = await db.users.find_one({"id": update_data.assigned_to}, {"_id": 0, "id": 1, "full_name": 1})
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )
        updates["assigned_to"] = update_data.assigned_to
        updates["assigned_to_name"] = assigned_user.get("full_name")
    
    # Appliquer les mises à jour
    await db.support_tickets.update_one(
        {"id": ticket_id},
        {"$set": updates}
    )
    
    # Récupérer le ticket mis à jour
    updated_ticket = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    
    return Ticket(**updated_ticket)


@router.post("/admin/tickets/{ticket_id}/messages", status_code=status.HTTP_201_CREATED, response_model=Message)
async def admin_add_message(
    ticket_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """[Admin] Ajouter un message (ou note interne) à un ticket"""
    
    # Vérifier les permissions admin
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Vérifier que le ticket existe
    ticket = await db.support_tickets.find_one({"id": ticket_id}, {"_id": 0})
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Créer le message
    message = {
        "id": str(uuid4()),
        "ticket_id": ticket_id,
        "user_id": current_user["id"],
        "user_email": current_user.get("email", ""),
        "user_name": current_user.get("full_name"),
        "message": message_data.message,
        "is_internal": message_data.is_internal,
        "created_at": now
    }
    
    await db.support_messages.insert_one(message)
    
    # Mettre à jour le ticket
    update_fields = {"updated_at": now}
    if not message_data.is_internal:
        # Incrémenter le compteur uniquement pour les messages visibles
        await db.support_tickets.update_one(
            {"id": ticket_id},
            {
                "$set": update_fields,
                "$inc": {"message_count": 1}
            }
        )
        
        # Si le ticket était ouvert, le passer en attente de l'utilisateur
        if ticket["status"] == "open" or ticket["status"] == "in_progress":
            await db.support_tickets.update_one(
                {"id": ticket_id},
                {"$set": {"status": "waiting_user"}}
            )
    else:
        await db.support_tickets.update_one(
            {"id": ticket_id},
            {"$set": update_fields}
        )
    
    # TODO: Envoyer une notification email à l'utilisateur si ce n'est pas une note interne
    
    return Message(**{k: v for k, v in message.items() if k != '_id'})
