#!/usr/bin/env python3
"""
Helper script pour déploiement multi-environnements
Usage:
    python scripts/deploy_helper.py validate dev
    python scripts/deploy_helper.py validate prod
    python scripts/deploy_helper.py check-secrets prod
"""
import sys
import os
import subprocess
import json
from pathlib import Path

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from awana_auth.core.config_manager import init_config, ConfigurationError
except ImportError:
    print("❌ Impossible d'importer ConfigManager")
    print("   Assurez-vous d'être dans le bon répertoire")
    sys.exit(1)


def validate_environment(env: str) -> bool:
    """Valider la configuration pour un environnement"""
    print(f"\n{'=' * 60}")
    print(f"🔍 Validation Configuration - Environnement: {env}")
    print(f"{'=' * 60}\n")
    
    try:
        # Initialiser la config
        os.environ['APP_ENV'] = env
        config = init_config(env=env)
        
        print(f"✅ ConfigManager initialisé pour '{env}'")
        print(f"   Debug: {config.get('app.debug')}")
        print(f"   Version: {config.get('app.version')}")
        print()
        
        # Valider (strict pour prod)
        strict = env == 'prod'
        try:
            config.validate(strict=strict)
            print(f"✅ Validation configuration réussie (strict={strict})")
        except ConfigurationError as e:
            print(f"❌ Validation échouée:\n{e}")
            return False
        
        # Afficher des infos clés
        print(f"\n📊 Configuration clé:")
        print(f"   - Database: {config.get('database.name')}")
        print(f"   - Pool size: {config.get('database.pool_size')}")
        print(f"   - JWT expire: {config.get('security.jwt.access_token_expire_minutes')}min")
        print(f"   - Rate limit: {config.get('security.rate_limit.enabled')}")
        print(f"   - Cache TTL: {config.get('cache.references.ttl_minutes')}min")
        print(f"   - Max upload: {config.get('storage.uploads.max_file_size_mb')}MB")
        
        # Vérifier les secrets critiques
        print(f"\n🔐 Secrets critiques:")
        critical_secrets = ['MONGO_URL', 'JWT_SECRET_KEY']
        
        if env == 'prod':
            critical_secrets.extend(['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'])
        
        for secret in critical_secrets:
            try:
                value = config.get_secret(secret, required=True)
                # Masquer la valeur
                masked = value[:10] + "..." if len(value) > 10 else "***"
                print(f"   ✅ {secret}: {masked}")
            except ConfigurationError:
                print(f"   ❌ {secret}: MANQUANT")
                return False
        
        print(f"\n{'=' * 60}")
        print(f"✅ Environnement '{env}' validé avec succès")
        print(f"{'=' * 60}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la validation:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False


def check_aws_secrets(env: str) -> bool:
    """Vérifier l'accès à AWS Secrets Manager"""
    print(f"\n{'=' * 60}")
    print(f"🔐 Vérification AWS Secrets Manager")
    print(f"{'=' * 60}\n")
    
    if env != 'prod':
        print(f"ℹ️  AWS Secrets Manager n'est utilisé qu'en production")
        print(f"   Environnement '{env}' utilise .env.encrypted")
        return True
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        print("❌ boto3 non installé")
        print("   Installer: pip install boto3")
        return False
    
    secret_name = os.getenv("AWS_SECRET_NAME", f"jlc-auth-{env}")
    region = os.getenv("AWS_REGION", "eu-west-1")
    
    print(f"Secret: {secret_name}")
    print(f"Region: {region}")
    print()
    
    try:
        client = boto3.client('secretsmanager', region_name=region)
        
        # Tenter de récupérer le secret
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        
        print(f"✅ Secret trouvé: {secret_name}")
        print(f"   Clés présentes: {len(secret_data)}")
        print(f"   Clés: {', '.join(secret_data.keys())}")
        
        # Vérifier les clés critiques
        required_keys = [
            'MONGO_URL',
            'JWT_SECRET_KEY',
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET'
        ]
        
        missing = [key for key in required_keys if key not in secret_data]
        
        if missing:
            print(f"\n⚠️  Clés manquantes dans le secret:")
            for key in missing:
                print(f"   - {key}")
            return False
        else:
            print(f"\n✅ Toutes les clés requises sont présentes")
        
        return True
        
    except NoCredentialsError:
        print("❌ Credentials AWS non trouvées")
        print("   Configurer: aws configure")
        print("   Ou utiliser IAM Role (EC2/ECS)")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'ResourceNotFoundException':
            print(f"❌ Secret non trouvé: {secret_name}")
            print(f"\n💡 Pour créer le secret:")
            print(f"   aws secretsmanager create-secret \\")
            print(f"     --name {secret_name} \\")
            print(f"     --secret-string '{{...}}' \\")
            print(f"     --region {region}")
        elif error_code == 'AccessDeniedException':
            print(f"❌ Accès refusé au secret: {secret_name}")
            print(f"\n💡 Vérifier les permissions IAM:")
            print(f"   - secretsmanager:GetSecretValue")
            print(f"   - secretsmanager:DescribeSecret")
        else:
            print(f"❌ Erreur AWS: {error_code}")
            print(f"   Message: {e.response['Error']['Message']}")
        
        return False
    
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False


def check_encrypted_env(env: str) -> bool:
    """Vérifier que .env.encrypted existe pour l'environnement"""
    print(f"\n{'=' * 60}")
    print(f"🔐 Vérification .env.encrypted")
    print(f"{'=' * 60}\n")
    
    if env == 'prod':
        print(f"ℹ️  Production utilise AWS Secrets Manager")
        print(f"   .env.encrypted non requis")
        return True
    
    encrypted_file = Path(f".env.{env}.encrypted")
    key_file = Path(".env.key")
    
    print(f"Fichier: {encrypted_file}")
    print(f"Clé: {key_file}")
    print()
    
    if not encrypted_file.exists():
        print(f"❌ Fichier chiffré non trouvé: {encrypted_file}")
        print(f"\n💡 Pour créer:")
        print(f"   1. Créer .env.{env} avec les secrets")
        print(f"   2. Chiffrer: python scripts/encrypt_env.py encrypt .env.{env} {encrypted_file}")
        return False
    
    if not key_file.exists():
        print(f"⚠️  Clé de déchiffrement non trouvée: {key_file}")
        print(f"   Récupérer depuis 1Password ou vault sécurisé")
        print(f"   Requis pour déchiffrer .env.{env}.encrypted")
        return False
    
    print(f"✅ Fichier chiffré existe: {encrypted_file}")
    print(f"✅ Clé de déchiffrement existe")
    
    # Tester le déchiffrement
    try:
        from cryptography.fernet import Fernet
        
        with open(key_file, 'rb') as f:
            key = f.read()
        
        fernet = Fernet(key)
        
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Parser les variables
        vars_count = len([l for l in decrypted_data.decode('utf-8').split('\n') 
                          if l.strip() and not l.strip().startswith('#') and '=' in l])
        
        print(f"✅ Déchiffrement réussi")
        print(f"   Variables: {vars_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de déchiffrement: {e}")
        print(f"   Vérifier que la clé est correcte")
        return False


def compare_environments() -> None:
    """Comparer les configurations entre environnements"""
    print(f"\n{'=' * 60}")
    print(f"📊 Comparaison des Environnements")
    print(f"{'=' * 60}\n")
    
    envs = ['local', 'dev', 'prod']
    configs = {}
    
    for env in envs:
        try:
            os.environ['APP_ENV'] = env
            config = init_config(env=env)
            configs[env] = config
        except Exception as e:
            print(f"⚠️  Impossible de charger '{env}': {e}")
    
    if not configs:
        print("❌ Aucune configuration chargée")
        return
    
    # Paramètres à comparer
    params = [
        ('app.debug', 'Debug'),
        ('database.pool_size', 'DB Pool Size'),
        ('security.jwt.access_token_expire_minutes', 'JWT Expire (min)'),
        ('security.rate_limit.enabled', 'Rate Limiting'),
        ('cache.references.ttl_minutes', 'Cache TTL (min)'),
        ('storage.uploads.max_file_size_mb', 'Max Upload (MB)'),
    ]
    
    print(f"{'Paramètre':<40} | {'local':<10} | {'dev':<10} | {'prod':<10}")
    print(f"{'-' * 40} | {'-' * 10} | {'-' * 10} | {'-' * 10}")
    
    for param, label in params:
        values = {}
        for env in envs:
            if env in configs:
                values[env] = str(configs[env].get(param, 'N/A'))
            else:
                values[env] = 'N/A'
        
        print(f"{label:<40} | {values.get('local', 'N/A'):<10} | {values.get('dev', 'N/A'):<10} | {values.get('prod', 'N/A'):<10}")
    
    print()


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/deploy_helper.py validate <env>")
        print("  python scripts/deploy_helper.py check-secrets <env>")
        print("  python scripts/deploy_helper.py check-encrypted <env>")
        print("  python scripts/deploy_helper.py compare")
        print()
        print("Environnements: local, dev, prod")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'validate':
        if len(sys.argv) < 3:
            print("❌ Environnement requis: validate <env>")
            sys.exit(1)
        
        env = sys.argv[2]
        success = validate_environment(env)
        sys.exit(0 if success else 1)
    
    elif command == 'check-secrets':
        if len(sys.argv) < 3:
            print("❌ Environnement requis: check-secrets <env>")
            sys.exit(1)
        
        env = sys.argv[2]
        success = check_aws_secrets(env)
        sys.exit(0 if success else 1)
    
    elif command == 'check-encrypted':
        if len(sys.argv) < 3:
            print("❌ Environnement requis: check-encrypted <env>")
            sys.exit(1)
        
        env = sys.argv[2]
        success = check_encrypted_env(env)
        sys.exit(0 if success else 1)
    
    elif command == 'compare':
        compare_environments()
        sys.exit(0)
    
    else:
        print(f"❌ Commande inconnue: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
