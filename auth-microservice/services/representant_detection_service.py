"""
Service de détection des représentants légaux existants
Phase 1 : Détection + Badge
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, List, Optional


async def detect_existing_representant(
    nom: str,
    email: str,
    db: AsyncIOMotorDatabase,
    exclude_user_id: Optional[str] = None
) -> Dict:
    """
    Détecter si un représentant légal existe déjà dans le système
    
    Args:
        nom: Nom du représentant légal
        email: Email du représentant légal
        db: Database instance
        exclude_user_id: User ID à exclure de la recherche (pour éviter auto-détection)
    
    Returns:
        Dict avec les informations de détection:
        {
            "found": bool,
            "user_id": str | None,
            "entreprises": List[Dict],
            "match_type": "exact" | "none"
        }
    """
    
    # Normaliser les données
    nom_normalized = nom.strip().lower() if nom else ""
    email_normalized = email.strip().lower() if email else ""
    
    if not nom_normalized or not email_normalized:
        return {
            "found": False,
            "user_id": None,
            "entreprises": [],
            "match_type": "none"
        }
    
    # Rechercher dans les entreprises existantes
    query = {
        "representant_legal_nom": {"$regex": f"^{nom_normalized}$", "$options": "i"},
        "representant_legal_email": {"$regex": f"^{email_normalized}$", "$options": "i"}
    }
    
    entreprises = await db.entreprises.find(query, {"_id": 0}).to_list(None)
    
    if not entreprises:
        return {
            "found": False,
            "user_id": None,
            "entreprises": [],
            "match_type": "none"
        }
    
    # Trouver l'user_id du représentant
    user_id = None
    for entreprise in entreprises:
        if entreprise.get("user_id"):
            user_id = entreprise["user_id"]
            break
    
    # Si pas de user_id trouvé dans les entreprises, chercher par email
    if not user_id:
        user = await db.users.find_one(
            {"email": {"$regex": f"^{email_normalized}$", "$options": "i"}},
            {"_id": 0, "id": 1}
        )
        if user:
            user_id = user["id"]
    
    # Exclure l'utilisateur actuel si demandé
    if user_id and exclude_user_id and user_id == exclude_user_id:
        return {
            "found": False,
            "user_id": None,
            "entreprises": [],
            "match_type": "none"
        }
    
    return {
        "found": True,
        "user_id": user_id,
        "entreprises": entreprises,
        "match_type": "exact"
    }


async def check_validation_representant(
    validation_id: str,
    db: AsyncIOMotorDatabase
) -> Dict:
    """
    Vérifier si le représentant légal d'une validation existe déjà
    
    Args:
        validation_id: ID de la validation à vérifier
        db: Database instance
    
    Returns:
        Dict avec les résultats de la vérification
    """
    
    # Récupérer la validation
    validation = await db.validations.find_one({"id": validation_id}, {"_id": 0})
    
    if not validation:
        raise ValueError(f"Validation {validation_id} non trouvée")
    
    if validation["validation_type"] != "company":
        return {
            "applicable": False,
            "message": "La détection de représentant s'applique uniquement aux validations de type 'company'"
        }
    
    # Extraire les informations du représentant
    nom = validation.get("representant_legal_nom", "")
    email = validation.get("representant_legal_email", "")
    
    if not nom or not email:
        return {
            "applicable": False,
            "message": "Informations du représentant légal manquantes"
        }
    
    # Détecter
    detection = await detect_existing_representant(
        nom=nom,
        email=email,
        db=db,
        exclude_user_id=validation["user_id"]
    )
    
    # Mettre à jour la validation si représentant trouvé
    if detection["found"]:
        entreprise_ids = [e["id"] for e in detection["entreprises"]]
        
        await db.validations.update_one(
            {"id": validation_id},
            {
                "$set": {
                    "has_existing_representant": True,
                    "existing_representant_user_id": detection["user_id"],
                    "existing_representant_entreprises": entreprise_ids
                }
            }
        )
    
    return {
        "applicable": True,
        "detection": detection,
        "validation_updated": detection["found"]
    }


async def get_representant_details(
    user_id: str,
    db: AsyncIOMotorDatabase
) -> Dict:
    """
    Récupérer les détails d'un représentant légal existant
    
    Args:
        user_id: ID de l'utilisateur représentant
        db: Database instance
    
    Returns:
        Dict avec les informations détaillées du représentant
    """
    
    # Récupérer l'utilisateur
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user:
        return {
            "found": False,
            "user": None,
            "entreprises": []
        }
    
    # Récupérer les entreprises liées
    entreprises = await db.entreprises.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(None)
    
    return {
        "found": True,
        "user": {
            "id": user["id"],
            "full_name": user.get("full_name"),
            "email": user.get("email"),
            "username": user.get("username"),
            "status": user.get("status"),
            "created_at": user.get("created_at")
        },
        "entreprises": [
            {
                "id": e["id"],
                "nom": e.get("nom"),
                "email": e.get("email"),
                "status": e.get("status", "active"),
                "created_at": e.get("created_at")
            }
            for e in entreprises
        ],
        "total_entreprises": len(entreprises)
    }
