"""
Google OAuth 2.0 Authentication Provider
"""
import httpx
from typing import Optional, Dict, Any
import logging
from .base import AbstractAuthProvider
from ..core.models import AuthResult, User
from ..core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class GoogleAuthProvider(AbstractAuthProvider):
    """Google OAuth 2.0 authentication provider"""
    
    AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"
    REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth requires client_id and client_secret")
    
    def get_authorization_url(self, state: str, redirect_uri: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: CSRF protection state parameter
            redirect_uri: Optional override for redirect URI
        
        Returns:
            Authorization URL to redirect user to
        """
        redirect = redirect_uri or self.redirect_uri
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",  # Get refresh token
            "prompt": "consent"  # Force consent to get refresh token
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_ENDPOINT}?{query_string}"
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate user with Google OAuth code
        
        Args:
            credentials: {"code": "...", "redirect_uri": "..."}
        
        Returns:
            AuthResult with user info and tokens
        """
        code = credentials.get("code")
        redirect_uri = credentials.get("redirect_uri", self.redirect_uri)
        
        if not code:
            raise AuthenticationError("Authorization code is required")
        
        # Exchange code for tokens
        tokens = await self._exchange_code_for_tokens(code, redirect_uri)
        
        # Get user info
        user_info = await self._get_user_info(tokens["access_token"])
        
        # Generate user ID (will be used if new user)
        import secrets
        user_id = secrets.token_urlsafe(16)
        
        # Create User object
        user = User(
            id=user_id,
            username=user_info["email"].split("@")[0],  # Use email prefix
            email=user_info["email"],
            full_name=user_info.get("name"),
            provider="google",
            provider_user_id=user_info["id"],
            is_verified=user_info.get("verified_email", False),
            status="active",
            roles=[]  # Will be assigned based on registration
        )
        
        from ..core.models import AuthProvider as AuthProviderEnum
        
        return AuthResult(
            success=True,
            user=user,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            provider=AuthProviderEnum.GOOGLE,
            metadata={
                "picture": user_info.get("picture"),
                "locale": user_info.get("locale"),
                "google_id": user_info["id"],
                "expires_in": tokens.get("expires_in", 3600)
            }
        )
    
    async def _exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_ENDPOINT,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.text}")
                    raise AuthenticationError(f"Failed to exchange code: {response.text}")
                
                return response.json()
            
            except httpx.RequestError as e:
                logger.error(f"HTTP error during token exchange: {e}")
                raise AuthenticationError(f"Network error: {str(e)}")
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USERINFO_ENDPOINT,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"User info fetch failed: {response.text}")
                    raise AuthenticationError("Failed to get user info")
                
                return response.json()
            
            except httpx.RequestError as e:
                logger.error(f"HTTP error getting user info: {e}")
                raise AuthenticationError(f"Network error: {str(e)}")
    
    async def get_user_info(self, access_token: str) -> Optional[User]:
        """Get user information (implements abstract method)"""
        try:
            user_info = await self._get_user_info(access_token)
            
            import secrets
            user_id = secrets.token_urlsafe(16)
            
            return User(
                id=user_id,
                username=user_info["email"].split("@")[0],
                email=user_info["email"],
                full_name=user_info.get("name"),
                provider="google",
                provider_user_id=user_info["id"],
                is_verified=user_info.get("verified_email", False),
                status="active",
                roles=[]
            )
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh Google access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_ENDPOINT,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.text}")
                    return None
                
                return response.json()
            
            except httpx.RequestError as e:
                logger.error(f"HTTP error during token refresh: {e}")
                return None
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke Google token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.REVOKE_ENDPOINT,
                    data={"token": token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                return response.status_code == 200
            
            except httpx.RequestError as e:
                logger.error(f"HTTP error during token revocation: {e}")
                return False
