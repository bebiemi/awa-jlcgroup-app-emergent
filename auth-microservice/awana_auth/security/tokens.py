"""
Token generation utilities
"""
import secrets
import string


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def generate_state_token(length: int = 32) -> str:
    """Generate a state token for OAuth flow (CSRF protection)"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_code_verifier(length: int = 64) -> str:
    """Generate PKCE code verifier"""
    alphabet = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(alphabet) for _ in range(length))
