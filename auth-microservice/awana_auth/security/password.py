"""
Password hashing and validation
"""
import bcrypt
from ..core.config import AuthConfig
import re


class PasswordManager:
    """Manages password hashing and validation"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        # Bcrypt has a 72 byte limit, truncate if needed
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def validate_password_strength(self, password: str) -> tuple[bool, list[str]]:
        """Validate password meets strength requirements
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check minimum length
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters long")
        
        # Check uppercase
        if self.config.password_require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check lowercase
        if self.config.password_require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check digits
        if self.config.password_require_digits and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        # Check special characters
        if self.config.password_require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        return (len(errors) == 0, errors)
