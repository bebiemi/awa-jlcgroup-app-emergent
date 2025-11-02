"""
Abstract base class for authentication providers
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..core.models import AuthResult, User


class AbstractAuthProvider(ABC):
    """Base class for all authentication providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate a user with provided credentials
        
        Args:
            credentials: Provider-specific credentials (e.g., {"code": "...", "redirect_uri": "..."})
        
        Returns:
            AuthResult with user information and tokens
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> Optional[User]:
        """
        Get user information from the provider
        
        Args:
            access_token: Provider access token
        
        Returns:
            User object or None if failed
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Provider refresh token
        
        Returns:
            Dictionary with new tokens or None if failed
        """
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token
        
        Args:
            token: Token to revoke
        
        Returns:
            True if successful, False otherwise
        """
        pass
