"""
JWT Token Management
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from ..core.config import AuthConfig
from ..core.models import User, TokenPayload
from ..core.exceptions import InvalidTokenError
import logging

logger = logging.getLogger(__name__)


class JWTManager:
    """Manages JWT token creation and validation"""
    
    def __init__(self, config: AuthConfig, iam_service=None):
        self.config = config
        self.secret_key = config.jwt_secret_key
        self.algorithm = config.jwt_algorithm
        self.access_token_expire = timedelta(minutes=config.jwt_access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=config.jwt_refresh_token_expire_days)
        self.iam_service = iam_service  # IAM service for permission resolution
    
    async def create_access_token(
        self,
        user: User,
        session_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new access token with IAM permissions"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + self.access_token_expire
        
        # Resolve user permissions via IAM
        permissions = []
        if self.iam_service:
            try:
                user_perms = await self.iam_service.get_user_permissions(user.id)
                # Extract permission codes from Permission objects
                permissions = [perm.code for perm in user_perms.all_permissions]
                logger.info(f"Resolved {len(permissions)} permissions for user {user.id}")
            except Exception as e:
                logger.error(f"Failed to resolve permissions for user {user.id}: {e}")
                # Continue without permissions rather than failing login
        else:
            logger.warning("IAM service not available, token will not contain permissions")
        
        payload = TokenPayload(
            sub=user.id,
            email=user.email,
            roles=user.roles,
            permissions=permissions,
            session_id=session_id,
            exp=expire,
            iat=datetime.now(timezone.utc),
            type="access"
        )
        
        to_encode = payload.model_dump()
        to_encode["exp"] = expire.timestamp()
        to_encode["iat"] = datetime.now(timezone.utc).timestamp()
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    async def create_refresh_token(
        self,
        user: User,
        session_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new refresh token (refresh tokens don't need permissions)"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + self.refresh_token_expire
        
        payload = TokenPayload(
            sub=user.id,
            email=user.email,
            roles=user.roles,
            permissions=[],  # Refresh tokens don't need permissions
            session_id=session_id,
            exp=expire,
            iat=datetime.now(timezone.utc),
            type="refresh"
        )
        
        to_encode = payload.model_dump()
        to_encode["exp"] = expire.timestamp()
        to_encode["iat"] = datetime.now(timezone.utc).timestamp()
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenPayload:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Convert timestamps back to datetime
            payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            payload["iat"] = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            
            token_payload = TokenPayload(**payload)
            
            # Verify token type
            if token_payload.type != token_type:
                raise InvalidTokenError(
                    f"Invalid token type. Expected '{token_type}', got '{token_payload.type}'"
                )
            
            # Check expiration
            if token_payload.exp < datetime.now(timezone.utc):
                raise InvalidTokenError("Token has expired")
            
            return token_payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    def decode_token_without_verification(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging)"""
        try:
            return jwt.get_unverified_claims(token)
        except JWTError as e:
            logger.error(f"Token decode failed: {e}")
            return {}
