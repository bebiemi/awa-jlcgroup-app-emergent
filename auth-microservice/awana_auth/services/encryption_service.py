"""
Service de chiffrement pour les données sensibles (mots de passe SMTP)
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service de chiffrement/déchiffrement pour les données sensibles"""
    
    def __init__(self):
        # Récupérer ou générer une clé de chiffrement
        self.encryption_key = self._get_or_generate_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_generate_key(self) -> bytes:
        """
        Récupérer la clé de chiffrement depuis l'environnement
        ou en générer une nouvelle
        """
        # Essayer de récupérer depuis l'environnement
        env_key = os.getenv('ENCRYPTION_KEY')
        
        if env_key:
            # Vérifier que la clé est valide
            try:
                return base64.urlsafe_b64decode(env_key.encode())
            except Exception as e:
                logger.warning(f"Clé de chiffrement invalide dans l'environnement: {e}")
        
        # Générer une clé dérivée depuis un secret
        secret = os.getenv('SECRET_KEY', 'default-secret-key-change-me-in-production')
        salt = os.getenv('ENCRYPTION_SALT', 'jlc-email-encryption-salt').encode()
        
        # Dériver une clé de 32 bytes depuis le secret
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        
        logger.info("Clé de chiffrement générée depuis SECRET_KEY")
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Chiffrer une chaîne de caractères
        
        Args:
            plaintext: Texte en clair
            
        Returns:
            Texte chiffré (base64)
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Erreur lors du chiffrement: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Déchiffrer une chaîne de caractères
        
        Args:
            ciphertext: Texte chiffré (base64)
            
        Returns:
            Texte en clair
        """
        if not ciphertext:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            raise
    
    def is_encrypted(self, text: str) -> bool:
        """
        Vérifier si un texte est chiffré
        
        Args:
            text: Texte à vérifier
            
        Returns:
            True si chiffré, False sinon
        """
        if not text:
            return False
        
        try:
            # Tenter de déchiffrer
            self.decrypt(text)
            return True
        except:
            return False


# Instance singleton
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Récupérer l'instance singleton du service de chiffrement"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
