"""
Centralized configuration for the authentication system
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class AuthConfig(BaseSettings):
    """Authentication system configuration"""
    
    # Application settings
    app_name: str = Field(default="AWANA GROUP", description="Application name")
    environment: str = Field(default="development", description="Environment (development/staging/production)")
    
    # EntraID OAuth Settings
    azure_tenant_id: Optional[str] = Field(default=None, env="AZURE_TENANT_ID")
    azure_backend_client_id: Optional[str] = Field(default=None, env="AZURE_BACKEND_CLIENT_ID")
    azure_backend_client_secret: Optional[str] = Field(default=None, env="AZURE_BACKEND_CLIENT_SECRET")
    azure_frontend_client_id: Optional[str] = Field(default=None, env="AZURE_FRONTEND_CLIENT_ID")
    azure_authority: Optional[str] = None
    azure_api_scope: Optional[str] = None
    
    # JWT Settings
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expire_days: int = Field(default=7)
    
    # Session Settings
    session_storage: str = Field(default="mongodb", description="Session storage backend (mongodb/redis)")
    session_max_age_seconds: int = Field(default=86400)  # 24 hours
    
    # Security Settings
    password_min_length: int = Field(default=12)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_digits: bool = Field(default=True)
    password_require_special: bool = Field(default=True)
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_login_attempts: int = Field(default=5)
    rate_limit_window_seconds: int = Field(default=300)  # 5 minutes
    
    # Audit Logging
    audit_log_enabled: bool = Field(default=True)
    audit_log_retention_days: int = Field(default=90)
    
    # Enabled Authentication Providers
    enabled_providers: List[str] = Field(
        default=["entraid"],
        description="List of enabled auth providers (entraid, webauthn, totp, local)"
    )
    
    # Database
    mongo_url: str = Field(default="mongodb://localhost:27017", env="MONGO_URL")
    database_name: str = Field(default="awana_auth", env="DATABASE_NAME")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields to be set dynamically
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate azure_authority and azure_api_scope if not provided
        if self.azure_tenant_id and not self.azure_authority:
            self.azure_authority = f"https://login.microsoftonline.com/{self.azure_tenant_id}"
        if self.azure_backend_client_id and not self.azure_api_scope:
            self.azure_api_scope = f"api://{self.azure_backend_client_id}/access_as_user"
        
        # Load admin emails from environment (not a Pydantic field)
        admin_emails_env = os.getenv("ADMIN_EMAILS", "")
        if admin_emails_env:
            self.admin_emails: List[str] = [email.strip() for email in admin_emails_env.split(",") if email.strip()]
        else:
            self.admin_emails: List[str] = []
    
    @property
    def is_entraid_enabled(self) -> bool:
        """Check if EntraID provider is enabled"""
        return "entraid" in self.enabled_providers and all([
            self.azure_tenant_id,
            self.azure_backend_client_id,
            self.azure_backend_client_secret
        ])
    
    @property
    def is_webauthn_enabled(self) -> bool:
        """Check if WebAuthn provider is enabled"""
        return "webauthn" in self.enabled_providers
    
    @property
    def is_totp_enabled(self) -> bool:
        """Check if TOTP provider is enabled"""
        return "totp" in self.enabled_providers


# Global configuration instance
auth_config = AuthConfig()
