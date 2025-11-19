"""
IAM Helper Functions
Utilitaires pour gérer le filtrage des données selon les permissions IAM
"""
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.services.iam_service import IAMService
import logging

logger = logging.getLogger(__name__)


async def get_resource_filter(
    iam_service: IAMService,
    user_id: str,
    user_company_id: Optional[str],
    resource: str,
    action: str = "read"
) -> Dict[str, Any]:
    """
    Générer un filtre MongoDB basé sur les permissions IAM de l'utilisateur
    
    Args:
        iam_service: Instance du service IAM
        user_id: ID de l'utilisateur
        user_company_id: ID de l'entreprise de l'utilisateur (peut être None)
        resource: Nom de la ressource (ex: "missions", "besoins")
        action: Action demandée (ex: "read", "create", "update", "delete")
    
    Returns:
        Dictionnaire de filtre MongoDB à appliquer
        - {} si l'utilisateur a la permission .all (pas de filtre)
        - {"company_id": user_company_id} si permission .own
        - None si aucune permission (à gérer par l'appelant)
    
    Examples:
        >>> filter = await get_resource_filter(iam, user_id, company_id, "missions", "read")
        >>> missions = await db.missions.find(filter).to_list(100)
    """
    # Vérifier la permission .all
    permission_all = f"{resource}.{action}.all"
    result_all = await iam_service.user_has_permission(user_id, permission_all)
    
    if result_all.has_permission:
        logger.debug(f"User {user_id} has {permission_all} - no filter")
        return {}  # Pas de filtre, accès total
    
    # Vérifier la permission .own
    permission_own = f"{resource}.{action}.own"
    result_own = await iam_service.user_has_permission(user_id, permission_own)
    
    if result_own.has_permission:
        if not user_company_id:
            logger.warning(f"User {user_id} has {permission_own} but no company_id - denying access")
            return None  # Pas d'accès si pas de company_id
        
        logger.debug(f"User {user_id} has {permission_own} - filtering by company_id={user_company_id}")
        
        # Déterminer le champ de filtrage selon la ressource
        filter_field = _get_filter_field(resource)
        return {filter_field: user_company_id}
    
    # Aucune permission
    logger.warning(f"User {user_id} has no permission for {resource}.{action}")
    return None


def _get_filter_field(resource: str) -> str:
    """
    Déterminer le champ de filtrage selon la ressource
    
    Different resources use different fields for company ownership:
    - missions: company_id
    - besoins: entreprise_id
    - entreprises: id (self-reference)
    - documents: owner_id or company_id
    """
    mapping = {
        "missions": "company_id",
        "besoins": "entreprise_id",
        "candidatures": "entreprise_id",  # À confirmer
        "entreprises": "id",
        "documents": "company_id",
        "validations": "entreprise_id"
    }
    
    return mapping.get(resource, "company_id")  # Default: company_id


async def check_resource_permission(
    iam_service: IAMService,
    user_id: str,
    user_company_id: Optional[str],
    resource: str,
    action: str,
    resource_company_id: Optional[str] = None
) -> bool:
    """
    Vérifier si un utilisateur a la permission d'effectuer une action sur une ressource spécifique
    
    Args:
        iam_service: Instance du service IAM
        user_id: ID de l'utilisateur
        user_company_id: ID de l'entreprise de l'utilisateur
        resource: Nom de la ressource
        action: Action demandée
        resource_company_id: ID de l'entreprise propriétaire de la ressource (optionnel)
    
    Returns:
        True si l'utilisateur a la permission, False sinon
    """
    # Vérifier .all
    permission_all = f"{resource}.{action}.all"
    result_all = await iam_service.user_has_permission(user_id, permission_all)
    
    if result_all.has_permission:
        return True
    
    # Vérifier .own
    permission_own = f"{resource}.{action}.own"
    result_own = await iam_service.user_has_permission(user_id, permission_own)
    
    if result_own.has_permission:
        # Si pas de resource_company_id fourni, on autorise (pour les créations par exemple)
        if resource_company_id is None:
            return user_company_id is not None
        
        # Vérifier que l'utilisateur possède la ressource
        return user_company_id == resource_company_id
    
    return False


async def get_allowed_permissions_list(
    iam_service: IAMService,
    user_id: str
) -> List[str]:
    """
    Récupérer la liste de tous les codes de permissions de l'utilisateur
    
    Returns:
        Liste des codes de permissions (ex: ["missions.read.own", "missions.create.own"])
    """
    user_perms = await iam_service.get_user_permissions(user_id)
    return [perm.code for perm in user_perms.all_permissions]


async def user_has_any_permission(
    iam_service: IAMService,
    user_id: str,
    permission_codes: List[str]
) -> bool:
    """
    Vérifier si l'utilisateur a au moins une des permissions de la liste
    
    Args:
        iam_service: Instance du service IAM
        user_id: ID de l'utilisateur
        permission_codes: Liste de codes de permissions
    
    Returns:
        True si l'utilisateur a au moins une permission, False sinon
    """
    for perm_code in permission_codes:
        result = await iam_service.user_has_permission(user_id, perm_code)
        if result.has_permission:
            return True
    return False
