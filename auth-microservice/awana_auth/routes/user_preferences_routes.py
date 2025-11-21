"""
Routes pour la gestion des préférences UI utilisateur
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from awana_auth.core.dependencies import get_database, get_current_user
from awana_auth.core.ui_preferences_models import (
    UIPreferences,
    UIPreferencesUpdate,
    UIPreferencesResponse
)

router = APIRouter(prefix="/users/me/preferences", tags=["User Preferences"])


@router.get(
    "",
    response_model=UIPreferencesResponse,
    summary="Récupérer les préférences UI de l'utilisateur connecté"
)
async def get_my_ui_preferences(
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Récupère les préférences UI de l'utilisateur connecté.
    
    Rétrocompatible : si l'utilisateur n'a pas de préférences, 
    retourne les valeurs par défaut.
    """
    try:
        # Extraire l'ID utilisateur
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        
        # Récupérer l'utilisateur
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Récupérer les préférences UI ou utiliser les valeurs par défaut
        ui_prefs = user.get("ui_preferences", {})
        
        preferences = UIPreferences(
            sidebar_style=ui_prefs.get("sidebar_style", "v2")
        )
        
        return UIPreferencesResponse(
            ui_preferences=preferences,
            updated_at=user.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des préférences: {str(e)}"
        )


@router.patch(
    "",
    response_model=UIPreferencesResponse,
    summary="Mettre à jour les préférences UI de l'utilisateur connecté"
)
async def update_my_ui_preferences(
    preferences: UIPreferencesUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Met à jour les préférences UI de l'utilisateur connecté.
    
    Rétrocompatible : crée le champ ui_preferences s'il n'existe pas.
    """
    try:
        # Extraire l'ID utilisateur
        user_id = current_user.id if hasattr(current_user, 'id') else current_user.get('id')
        
        # Vérifier que l'utilisateur existe
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Récupérer les préférences existantes
        current_prefs = user.get("ui_preferences", {})
        
        # Mettre à jour uniquement les champs fournis
        update_data = preferences.model_dump(exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="Aucune préférence à mettre à jour"
            )
        
        # Fusionner avec les préférences existantes
        updated_prefs = {**current_prefs, **update_data}
        
        # Mettre à jour dans la base de données
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "ui_preferences": updated_prefs,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Récupérer et retourner les préférences mises à jour
        updated_user = await db.users.find_one({"id": user_id})
        
        preferences_obj = UIPreferences(
            sidebar_style=updated_user.get("ui_preferences", {}).get("sidebar_style", "v2")
        )
        
        return UIPreferencesResponse(
            ui_preferences=preferences_obj,
            updated_at=updated_user.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour des préférences: {str(e)}"
        )
