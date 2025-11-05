"""
Gestionnaire de configuration centralisé
Support YAML hiérarchique + .env + AWS Secrets Manager
"""
import os
import yaml
import json
from typing import Any, Optional, Dict, List
from pathlib import Path
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Erreur de configuration"""
    pass


class ConfigManager:
    """
    Gestionnaire de configuration centralisé
    
    Ordre de priorité (du plus prioritaire au moins prioritaire) :
    1. Variables d'environnement
    2. AWS Secrets Manager (prod uniquement)
    3. Fichier .env.encrypted (décrypté)
    4. Fichier .env
    5. Fichier config/{env}.yaml
    6. Fichier config/base.yaml
    """
    
    def __init__(self, env: Optional[str] = None, config_dir: Optional[str] = None):
        """
        Initialiser le gestionnaire de configuration
        
        Args:
            env: Environnement (local, dev, staging, prod). Auto-détecté si None.
            config_dir: Répertoire des fichiers de configuration
        """
        self.env = env or os.getenv("APP_ENV", "local")
        # Détecter si on est dans Docker (WORKDIR=/app) ou en local
        default_config_dir = "/app/config" if os.path.exists("/app/config") else "/app/auth-microservice/config"
        self.config_dir = Path(config_dir or default_config_dir)
        self._config: Dict[str, Any] = {}
        self._secrets: Dict[str, Any] = {}
        self._required_vars: List[str] = []
        self._is_loaded = False
        
        # Charger la configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Charger toute la configuration selon l'ordre de priorité"""
        logger.info(f"🔧 Chargement de la configuration pour l'environnement: {self.env}")
        
        # 1. Charger la configuration de base
        self._load_yaml_file("base.yaml")
        
        # 2. Charger la configuration spécifique à l'environnement
        env_file = f"{self.env}.yaml"
        if (self.config_dir / env_file).exists():
            self._load_yaml_file(env_file)
        else:
            logger.warning(f"⚠️  Fichier de configuration {env_file} non trouvé, utilisation de base.yaml uniquement")
        
        # 3. Charger les variables d'environnement depuis .env
        self._load_env_file()
        
        # 4. Charger les secrets chiffrés (.env.encrypted)
        if self.env != "prod":
            self._load_encrypted_env()
        
        # 5. Charger depuis AWS Secrets Manager (prod uniquement)
        if self.env == "prod":
            self._load_aws_secrets()
        
        # 6. Surcharger avec les variables d'environnement système
        self._override_with_env_vars()
        
        self._is_loaded = True
        logger.info("✅ Configuration chargée avec succès")
    
    def _load_yaml_file(self, filename: str):
        """Charger un fichier YAML et fusionner avec la config existante"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise ConfigurationError(f"Fichier de configuration manquant: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                self._deep_merge(self._config, data)
                logger.debug(f"📄 Chargé: {filename}")
        except Exception as e:
            raise ConfigurationError(f"Erreur lors du chargement de {filename}: {e}")
    
    def _load_env_file(self):
        """Charger le fichier .env"""
        env_file = Path("/app/auth-microservice/.env")
        if env_file.exists():
            load_dotenv(env_file)
            logger.debug("📄 Variables .env chargées")
    
    def _load_encrypted_env(self):
        """Charger et déchiffrer .env.encrypted"""
        encrypted_file = Path("/app/auth-microservice/.env.encrypted")
        key_file = Path("/app/auth-microservice/.env.key")
        
        if not encrypted_file.exists():
            logger.debug("ℹ️  Pas de fichier .env.encrypted trouvé")
            return
        
        if not key_file.exists():
            logger.warning("⚠️  .env.encrypted trouvé mais .env.key manquant")
            return
        
        try:
            # Lire la clé de chiffrement
            with open(key_file, 'rb') as f:
                key = f.read()
            
            # Déchiffrer le fichier
            fernet = Fernet(key)
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
            
            # Parser les variables
            for line in decrypted_data.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    self._secrets[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
            
            logger.info("🔐 Secrets déchiffrés depuis .env.encrypted")
        except Exception as e:
            logger.error(f"❌ Erreur lors du déchiffrement de .env.encrypted: {e}")
    
    def _load_aws_secrets(self):
        """Charger les secrets depuis AWS Secrets Manager"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            secret_name = os.getenv("AWS_SECRET_NAME", f"jlc-auth-{self.env}")
            region = os.getenv("AWS_REGION", "eu-west-1")
            
            client = boto3.client('secretsmanager', region_name=region)
            
            try:
                response = client.get_secret_value(SecretId=secret_name)
                secret_data = json.loads(response['SecretString'])
                
                # Injecter dans l'environnement
                for key, value in secret_data.items():
                    self._secrets[key] = value
                    os.environ[key] = str(value)
                
                logger.info(f"🔐 Secrets chargés depuis AWS Secrets Manager: {secret_name}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    logger.warning(f"⚠️  Secret AWS non trouvé: {secret_name}")
                else:
                    logger.error(f"❌ Erreur AWS Secrets Manager: {e}")
        except ImportError:
            logger.warning("⚠️  boto3 non installé, impossible de charger les secrets AWS")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des secrets AWS: {e}")
    
    def _override_with_env_vars(self):
        """Surcharger la configuration avec les variables d'environnement système"""
        # Mapping des variables d'environnement vers les clés de config
        env_mappings = {
            # Database
            "MONGO_URL": "database.url",
            "DATABASE_NAME": "database.name",
            "DB_POOL_SIZE": "database.pool_size",
            
            # Security
            "JWT_SECRET_KEY": "security.jwt.secret_key",
            "JWT_ALGORITHM": "security.jwt.algorithm",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "security.jwt.access_token_expire_minutes",
            
            # OAuth
            "GOOGLE_CLIENT_ID": "security.oauth.google.client_id",
            "GOOGLE_CLIENT_SECRET": "security.oauth.google.client_secret",
            
            # Server
            "SERVER_HOST": "server.host",
            "SERVER_PORT": "server.port",
            
            # Features
            "ENABLE_MFA": "features.mfa.enabled",
            "ENABLE_EMAIL_VERIFICATION": "features.email_verification.enabled",
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested(config_key, self._parse_value(value))
                logger.debug(f"🔄 Surchargé: {config_key} depuis ${env_var}")
    
    def _deep_merge(self, base: Dict, override: Dict):
        """Fusionner deux dictionnaires de manière récursive"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _set_nested(self, key_path: str, value: Any):
        """Définir une valeur dans un chemin imbriqué (ex: 'database.host')"""
        keys = key_path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _parse_value(self, value: str) -> Any:
        """Parser une valeur string en type approprié"""
        # Boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Nombre
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # JSON
        if value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        return value
    
    def get(self, key_path: str, default: Any = None, required: bool = False) -> Any:
        """
        Récupérer une valeur de configuration
        
        Args:
            key_path: Chemin vers la valeur (ex: 'database.host')
            default: Valeur par défaut si non trouvée
            required: Si True, lève une exception si la valeur est absente
            
        Returns:
            La valeur de configuration
            
        Raises:
            ConfigurationError: Si required=True et valeur absente
        """
        if not self._is_loaded:
            raise ConfigurationError("Configuration non chargée")
        
        keys = key_path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            if required:
                raise ConfigurationError(f"Variable de configuration requise manquante: {key_path}")
            return default
    
    def get_secret(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Récupérer un secret (depuis .env, .env.encrypted ou AWS Secrets Manager)
        
        Args:
            key: Nom du secret
            default: Valeur par défaut
            required: Si True, lève une exception si absent
        """
        # Priorité 1: Variable d'environnement système
        value = os.getenv(key)
        if value is not None:
            return value
        
        # Priorité 2: Secrets chargés (_secrets dict)
        if key in self._secrets:
            return self._secrets[key]
        
        # Pas trouvé
        if required:
            raise ConfigurationError(f"Secret requis manquant: {key}")
        
        return default
    
    def require(self, *key_paths: str):
        """
        Marquer des variables comme requises et valider leur présence
        
        Args:
            *key_paths: Chemins des variables requises
            
        Raises:
            ConfigurationError: Si une variable requise est absente
        """
        missing = []
        for key_path in key_paths:
            try:
                self.get(key_path, required=True)
            except ConfigurationError:
                missing.append(key_path)
        
        if missing:
            raise ConfigurationError(
                f"Variables de configuration requises manquantes: {', '.join(missing)}"
            )
    
    def validate(self, strict: bool = None):
        """
        Valider la configuration selon l'environnement
        
        Args:
            strict: Si True, mode strict (fail fast). Si None, auto selon env
        """
        if strict is None:
            strict = self.env in ('staging', 'prod')
        
        logger.info(f"🔍 Validation de la configuration (strict={strict})")
        
        # Variables critiques pour tous les environnements
        critical_vars = [
            "database.name",
            "security.jwt.algorithm",
            "server.host",
            "server.port",
        ]
        
        # Secrets critiques
        critical_secrets = [
            "MONGO_URL",
            "JWT_SECRET_KEY",
        ]
        
        # Variables critiques pour la production
        if self.env == "prod":
            critical_vars.extend([
                "storage.cloud.bucket",
                "storage.cloud.region",
                "notifications.email.from_email",
            ])
            critical_secrets.extend([
                "GOOGLE_CLIENT_ID",
                "GOOGLE_CLIENT_SECRET",
            ])
        
        missing_config = []
        missing_secrets = []
        
        # Vérifier les variables de config
        for var in critical_vars:
            try:
                value = self.get(var, required=True)
                if value is None or value == "":
                    missing_config.append(var)
            except ConfigurationError:
                missing_config.append(var)
        
        # Vérifier les secrets
        for secret in critical_secrets:
            try:
                value = self.get_secret(secret, required=True)
                if value is None or value == "":
                    missing_secrets.append(secret)
            except ConfigurationError:
                missing_secrets.append(secret)
        
        # Rapport
        if missing_config or missing_secrets:
            error_msg = "❌ Validation de configuration échouée:\n"
            if missing_config:
                error_msg += f"  - Config manquantes: {', '.join(missing_config)}\n"
            if missing_secrets:
                error_msg += f"  - Secrets manquants: {', '.join(missing_secrets)}\n"
            
            if strict:
                raise ConfigurationError(error_msg)
            else:
                logger.warning(error_msg)
        else:
            logger.info("✅ Validation de configuration réussie")
    
    def get_all(self) -> Dict[str, Any]:
        """Récupérer toute la configuration (sans les secrets)"""
        return self._config.copy()
    
    def reload(self):
        """Recharger la configuration"""
        self._config = {}
        self._secrets = {}
        self._is_loaded = False
        self._load_configuration()


# Instance globale
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Récupérer l'instance globale du gestionnaire de configuration"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.validate()
    return _config_manager


def init_config(env: Optional[str] = None, config_dir: Optional[str] = None):
    """
    Initialiser le gestionnaire de configuration
    À appeler au démarrage de l'application
    """
    global _config_manager
    _config_manager = ConfigManager(env=env, config_dir=config_dir)
    _config_manager.validate()
    return _config_manager
