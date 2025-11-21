"""
Modèles pour les préférences UI utilisateur
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class UIPreferences(BaseModel):
    """Préférences d'interface utilisateur"""
    sidebar_style: Literal['v2', 'v3'] = Field(
        default='v2',
        description="Style de la sidebar (v2=classique, v3=premium)"
    )
    # Futures préférences possibles :
    # theme: Literal['light', 'dark'] = 'light'
    # language: str = 'fr'
    # notifications_enabled: bool = True
    

class UIPreferencesUpdate(BaseModel):
    """Modèle pour mise à jour des préférences UI"""
    sidebar_style: Optional[Literal['v2', 'v3']] = Field(
        default=None,
        description="Style de la sidebar"
    )
    
    class Config:
        extra = 'forbid'  # Rejeter les champs non définis


class UIPreferencesResponse(BaseModel):
    """Réponse API avec les préférences UI"""
    ui_preferences: UIPreferences
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
