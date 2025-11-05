"""
Modèles pour la configuration email et l'historique
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmailProvider(str, Enum):
    """Fournisseurs email supportés"""
    GMAIL = "gmail"
    SENDGRID = "sendgrid"
    OFFICE365 = "office365"
    MAILTRAP = "mailtrap"
    CUSTOM = "custom"


class EmailConfigUpdate(BaseModel):
    """Modèle pour la mise à jour de la configuration email"""
    enabled: bool = Field(default=False, description="Activer/désactiver les notifications email")
    provider: EmailProvider = Field(default=EmailProvider.CUSTOM, description="Fournisseur SMTP")
    smtp_host: str = Field(..., min_length=1, description="Hôte SMTP")
    smtp_port: int = Field(..., ge=1, le=65535, description="Port SMTP")
    smtp_user: str = Field(..., min_length=1, description="Utilisateur SMTP")
    smtp_password: str = Field(..., min_length=1, description="Mot de passe SMTP (sera chiffré)")
    smtp_use_tls: bool = Field(default=True, description="Utiliser TLS")
    from_email: EmailStr = Field(..., description="Email expéditeur")
    from_name: str = Field(default="JLC Application", description="Nom expéditeur")
    admin_emails: List[EmailStr] = Field(default=[], description="Liste des emails admin")
    
    @validator('smtp_host')
    def validate_smtp_host(cls, v):
        if not v or v.strip() == '':
            raise ValueError("L'hôte SMTP est requis")
        return v.strip()
    
    @validator('smtp_user')
    def validate_smtp_user(cls, v):
        if not v or v.strip() == '':
            raise ValueError("L'utilisateur SMTP est requis")
        return v.strip()
    
    @validator('admin_emails')
    def validate_admin_emails(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Au moins un email admin est requis")
        return v


class EmailConfigResponse(BaseModel):
    """Modèle de réponse pour la configuration email (sans mot de passe)"""
    id: str
    enabled: bool
    provider: EmailProvider
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_use_tls: bool
    from_email: str
    from_name: str
    admin_emails: List[str]
    created_at: datetime
    updated_at: datetime
    updated_by: str
    is_configured: bool = True


class EmailTestRequest(BaseModel):
    """Requête pour tester une configuration email"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_use_tls: bool
    from_email: EmailStr
    to_email: EmailStr = Field(..., description="Email de test destinataire")


class EmailStatus(str, Enum):
    """Statut d'envoi d'un email"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailHistory(BaseModel):
    """Modèle pour l'historique des emails envoyés"""
    id: str
    to_emails: List[str]
    subject: str
    template_name: Optional[str] = None
    status: EmailStatus
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    sent_by: str
    metadata: Optional[Dict[str, Any]] = {}


class EmailTemplateType(str, Enum):
    """Types de templates email"""
    ROLLBACK = "rollback"
    FEATURE_FLAG = "feature_flag"
    USER_WELCOME = "user_welcome"
    PASSWORD_RESET = "password_reset"
    CUSTOM = "custom"


class EmailTemplate(BaseModel):
    """Modèle pour les templates d'email personnalisables"""
    id: str
    name: str = Field(..., description="Nom du template")
    type: EmailTemplateType = Field(..., description="Type de template")
    subject: str = Field(..., description="Sujet de l'email")
    html_content: str = Field(..., description="Contenu HTML avec variables {{variable}}")
    text_content: Optional[str] = Field(None, description="Contenu texte alternatif")
    variables: List[str] = Field(default=[], description="Liste des variables disponibles")
    is_active: bool = Field(default=True, description="Template actif")
    is_system: bool = Field(default=False, description="Template système (non modifiable)")
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    @validator('html_content')
    def validate_html_content(cls, v):
        if not v or v.strip() == '':
            raise ValueError("Le contenu HTML est requis")
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        if not v or v.strip() == '':
            raise ValueError("Le sujet est requis")
        return v


class EmailTemplateCreate(BaseModel):
    """Modèle pour créer un template"""
    name: str
    type: EmailTemplateType
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: List[str] = []


class EmailTemplateUpdate(BaseModel):
    """Modèle pour mettre à jour un template"""
    name: Optional[str] = None
    subject: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
