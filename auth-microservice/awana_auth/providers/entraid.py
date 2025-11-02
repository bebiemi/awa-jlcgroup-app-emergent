"""
Microsoft EntraID (Azure AD) OAuth 2.0 / OIDC Provider
"""
from typing import Optional, Dict, Any
import httpx
from jose import jwt
from ..core.models import AuthResult, User, AuthProvider as AuthProviderEnum
from ..core.exceptions import AuthenticationError, ProviderError
from ..core.config import AuthConfig
from .base import AbstractAuthProvider
import logging

logger = logging.getLogger(__name__)


class EntraIDProvider(AbstractAuthProvider):
    """Microsoft EntraID OAuth 2.0 / OIDC authentication provider"""
    
    def __init__(self, config: AuthConfig):
        super().__init__(config.model_dump())
        self.tenant_id = config.azure_tenant_id
        self.backend_client_id = config.azure_backend_client_id
        self.client_secret = config.azure_backend_client_secret
        self.frontend_client_id = config.azure_frontend_client_id
        self.authority = config.azure_authority
        
        # OAuth endpoints
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        self.authorize_endpoint = f"{self.authority}/oauth2/v2.0/authorize"
        self.userinfo_endpoint = "https://graph.microsoft.com/v1.0/me"
        self.jwks_uri = f"{self.authority}/discovery/v2.0/keys"
        
        logger.info(f"EntraID provider initialized for tenant {self.tenant_id}")
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate using authorization code flow
        
        Args:
            credentials: {
                "code": "authorization_code",
                "redirect_uri": "http://localhost:3000",
                "code_verifier": "optional_pkce_verifier"
            }
        """
        try:
            code = credentials.get("code")
            redirect_uri = credentials.get("redirect_uri")
            code_verifier = credentials.get("code_verifier")
            
            if not code or not redirect_uri:
                raise AuthenticationError(
                    "Missing required credentials: code and redirect_uri",
                    details={"provider": "entraid"}
                )
            
            # Exchange authorization code for tokens
            token_data = await self._exchange_code_for_tokens(
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier
            )
            
            # Get user information
            user = await self.get_user_info(token_data["access_token"])
            
            if not user:
                raise AuthenticationError("Failed to retrieve user information")
            
            return AuthResult(
                success=True,
                user=user,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                provider=AuthProviderEnum.ENTRAID,
                metadata={
                    "id_token": token_data.get("id_token"),
                    "expires_in": token_data.get("expires_in"),
                    "scope": token_data.get("scope")
                }
            )
            
        except Exception as e:
            logger.error(f"EntraID authentication failed: {e}")
            return AuthResult(
                success=False,
                error_message=str(e),
                provider=AuthProviderEnum.ENTRAID
            )
    
    async def _exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        
        token_request_data = {
            "client_id": self.frontend_client_id,  # Use Frontend Client ID (SPA has no secret)
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": "openid profile email User.Read"
        }
        
        # SPAs don't use client_secret, only confidential apps do
        
        # Add PKCE code verifier if provided
        if code_verifier:
            token_request_data["code_verifier"] = code_verifier
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_endpoint,
                    data=token_request_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    raise ProviderError(
                        provider="entraid",
                        message=f"Token exchange failed: {error_data.get('error_description', 'Unknown error')}",
                        details=error_data
                    )
                
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error during token exchange: {e}")
                raise ProviderError(
                    provider="entraid",
                    message=f"Network error during token exchange: {str(e)}"
                )
    
    async def get_user_info(self, access_token: str) -> Optional[User]:
        """Get user information from Microsoft Graph API"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get user info: {response.status_code}")
                    return None
                
                user_data = response.json()
                
                # Extract user information
                user = User(
                    id=user_data.get("id"),  # Will be replaced with local user ID later
                    username=user_data.get("userPrincipalName", user_data.get("mail", "")),
                    email=user_data.get("mail", user_data.get("userPrincipalName", "")),
                    full_name=user_data.get("displayName"),
                    provider=AuthProviderEnum.ENTRAID,
                    provider_user_id=user_data.get("id"),
                    is_verified=True,
                    roles=[],  # Will be assigned based on EntraID roles or local mapping
                    metadata={
                        "job_title": user_data.get("jobTitle"),
                        "office_location": user_data.get("officeLocation"),
                        "mobile_phone": user_data.get("mobilePhone"),
                        "business_phones": user_data.get("businessPhones", [])
                    }
                )
                
                return user
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting user info: {e}")
                return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token"""
        
        refresh_data = {
            "client_id": self.frontend_client_id,  # Use Frontend Client ID
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": "openid profile email User.Read offline_access"
        }
        # No client_secret for SPAs
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_endpoint,
                    data=refresh_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed: {response.status_code}")
                    return None
                
                token_data = response.json()
                
                return {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token", refresh_token),
                    "expires_in": token_data.get("expires_in")
                }
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error during token refresh: {e}")
                return None
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (EntraID doesn't have a standard revoke endpoint)
        Just return True as the token will expire naturally
        """
        logger.info("Token revocation requested (EntraID doesn't support explicit revocation)")
        return True
    
    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scope: str = "openid profile email User.Read",
        code_challenge: Optional[str] = None,
        code_challenge_method: str = "S256"
    ) -> str:
        """
        Generate authorization URL for OAuth flow
        
        Args:
            redirect_uri: Callback URL
            state: CSRF protection state parameter
            scope: Requested scopes
            code_challenge: PKCE code challenge (optional)
            code_challenge_method: PKCE method (S256 or plain)
        
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.frontend_client_id,  # Use Frontend Client ID for authorization
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "response_mode": "query"
        }
        
        # Add PKCE parameters if provided
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = code_challenge_method
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorize_endpoint}?{query_string}"
