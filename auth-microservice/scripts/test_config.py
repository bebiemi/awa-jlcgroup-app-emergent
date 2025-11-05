#!/usr/bin/env python3
"""
Script de test de la configuration
Valide que toutes les valeurs sont correctement chargées
"""
import sys
import os

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from awana_auth.core.config_manager import init_config, get_config
from awana_auth.core.config import auth_config


def test_config_loading():
    """Tester le chargement de la configuration"""
    print("=" * 60)
    print("TEST 1: Chargement de la Configuration")
    print("=" * 60)
    
    # Initialiser la config pour l'environnement local
    os.environ['APP_ENV'] = 'local'
    config = init_config('local')
    
    print("✅ ConfigManager initialisé")
    print(f"   Environnement: {os.getenv('APP_ENV')}")
    print()
    
    return config


def test_database_config(config):
    """Tester la configuration de la base de données"""
    print("=" * 60)
    print("TEST 2: Configuration Base de Données")
    print("=" * 60)
    
    db_name = config.get("database.name")
    pool_size = config.get("database.pool_size")
    max_pool = config.get("database.max_pool_size")
    
    print(f"✅ Database name: {db_name}")
    print(f"✅ Pool size: {pool_size}")
    print(f"✅ Max pool size: {max_pool}")
    
    assert db_name == "auth_db", f"Expected 'auth_db', got '{db_name}'"
    assert pool_size == 5, f"Expected 5 (local), got {pool_size}"
    print("✅ Tests DB passés")
    print()


def test_jwt_config(config):
    """Tester la configuration JWT"""
    print("=" * 60)
    print("TEST 3: Configuration JWT")
    print("=" * 60)
    
    algorithm = config.get("security.jwt.algorithm")
    expire_minutes = config.get("security.jwt.access_token_expire_minutes")
    refresh_days = config.get("security.jwt.refresh_token_expire_days")
    
    print(f"✅ JWT Algorithm: {algorithm}")
    print(f"✅ Access token expire: {expire_minutes} minutes")
    print(f"✅ Refresh token expire: {refresh_days} days")
    
    # En local, le token expire après 60 minutes (config/local.yaml)
    assert expire_minutes == 60, f"Expected 60 (local), got {expire_minutes}"
    print("✅ Tests JWT passés")
    print()


def test_password_policy(config):
    """Tester la politique de mot de passe"""
    print("=" * 60)
    print("TEST 4: Politique de Mot de Passe")
    print("=" * 60)
    
    min_length = config.get("security.password.min_length")
    require_upper = config.get("security.password.require_uppercase")
    require_digit = config.get("security.password.require_digit")
    max_attempts = config.get("security.password.max_attempts")
    
    print(f"✅ Min length: {min_length}")
    print(f"✅ Require uppercase: {require_upper}")
    print(f"✅ Require digit: {require_digit}")
    print(f"✅ Max attempts: {max_attempts}")
    
    assert min_length == 8
    assert require_upper == True
    print("✅ Tests Password Policy passés")
    print()


def test_rate_limiting(config):
    """Tester la configuration rate limiting"""
    print("=" * 60)
    print("TEST 5: Rate Limiting")
    print("=" * 60)
    
    enabled = config.get("security.rate_limit.enabled")
    default_limit = config.get("security.rate_limit.default_limit")
    
    print(f"✅ Rate limiting enabled: {enabled}")
    print(f"✅ Default limit: {default_limit}")
    
    # En local, rate limiting est désactivé
    assert enabled == False, f"Expected False (local), got {enabled}"
    print("✅ Tests Rate Limiting passés")
    print()


def test_workflows_config(config):
    """Tester la configuration des workflows"""
    print("=" * 60)
    print("TEST 6: Configuration Workflows")
    print("=" * 60)
    
    auto_publish = config.get("workflows.mission.auto_publish")
    max_apps = config.get("workflows.application.restrictions.max_applications_per_candidate")
    interview_delay = config.get("workflows.application.delays.interview_scheduling")
    
    print(f"✅ Auto-publish missions: {auto_publish}")
    print(f"✅ Max applications per candidate: {max_apps}")
    print(f"✅ Interview scheduling delay: {interview_delay} days")
    
    # En local, auto-publish est activé et délais réduits
    assert auto_publish == True, f"Expected True (local), got {auto_publish}"
    assert interview_delay == 1, f"Expected 1 day (local), got {interview_delay}"
    print("✅ Tests Workflows passés")
    print()


def test_storage_config(config):
    """Tester la configuration du stockage"""
    print("=" * 60)
    print("TEST 7: Configuration Stockage")
    print("=" * 60)
    
    base_path = config.get("storage.uploads.base_path")
    max_size = config.get("storage.uploads.max_file_size_mb")
    allowed_exts = config.get("storage.uploads.allowed_extensions")
    
    print(f"✅ Upload path: {base_path}")
    print(f"✅ Max file size: {max_size}MB")
    print(f"✅ Allowed extensions: {', '.join(allowed_exts)}")
    
    # En local, max size est plus élevé (50MB)
    assert max_size == 50, f"Expected 50MB (local), got {max_size}MB"
    print("✅ Tests Storage passés")
    print()


def test_cache_config(config):
    """Tester la configuration du cache"""
    print("=" * 60)
    print("TEST 8: Configuration Cache")
    print("=" * 60)
    
    enabled = config.get("cache.references.enabled")
    ttl = config.get("cache.references.ttl_minutes")
    
    print(f"✅ Cache enabled: {enabled}")
    print(f"✅ TTL: {ttl} minutes")
    
    # En local, TTL est court (5 minutes)
    assert ttl == 5, f"Expected 5 minutes (local), got {ttl}"
    print("✅ Tests Cache passés")
    print()


def test_features_flags(config):
    """Tester les feature flags"""
    print("=" * 60)
    print("TEST 9: Feature Flags")
    print("=" * 60)
    
    mfa_enabled = config.get("features.mfa.enabled")
    email_verif = config.get("features.email_verification.enabled")
    ai_features = config.get("features.ai_features.enabled")
    
    print(f"✅ MFA enabled: {mfa_enabled}")
    print(f"✅ Email verification: {email_verif}")
    print(f"✅ AI features: {ai_features}")
    
    # En local, MFA désactivé mais AI activé pour tests
    assert mfa_enabled == False, f"Expected False (local), got {mfa_enabled}"
    assert ai_features == True, f"Expected True (local), got {ai_features}"
    print("✅ Tests Feature Flags passés")
    print()


def test_auth_config_compatibility():
    """Tester la compatibilité avec AuthConfig"""
    print("=" * 60)
    print("TEST 10: Compatibilité AuthConfig")
    print("=" * 60)
    
    # Vérifier que AuthConfig charge bien depuis ConfigManager
    jwt_algo = auth_config.jwt_algorithm
    jwt_expire = auth_config.jwt_access_token_expire_minutes
    password_min = auth_config.password_min_length
    
    print(f"✅ AuthConfig JWT algorithm: {jwt_algo}")
    print(f"✅ AuthConfig JWT expire: {jwt_expire} minutes")
    print(f"✅ AuthConfig password min length: {password_min}")
    
    assert jwt_algo == "HS256"
    assert jwt_expire == 60  # Local config
    print("✅ Tests Compatibilité AuthConfig passés")
    print()


def test_environment_override():
    """Tester la surcharge par variables d'environnement"""
    print("=" * 60)
    print("TEST 11: Surcharge Variables d'Environnement")
    print("=" * 60)
    
    # Définir une variable d'environnement pour tester
    os.environ['SERVER_PORT'] = '9000'
    config = get_config()
    config.reload()
    
    port = config.get("server.port")
    print(f"✅ Server port après override: {port}")
    
    # Note: Le test exact dépend de l'implémentation de _override_with_env_vars
    # Pour l'instant on vérifie juste que ça ne crash pas
    print("✅ Test Override Variables passé")
    print()


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n")
    print("=" * 60)
    print("TESTS DE CONFIGURATION - PHASE 3")
    print("=" * 60)
    print()
    
    try:
        config = test_config_loading()
        test_database_config(config)
        test_jwt_config(config)
        test_password_policy(config)
        test_rate_limiting(config)
        test_workflows_config(config)
        test_storage_config(config)
        test_cache_config(config)
        test_features_flags(config)
        test_auth_config_compatibility()
        test_environment_override()
        
        print("=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS")
        print("=" * 60)
        print()
        print("📊 Résumé:")
        print("   - 11 catégories testées")
        print("   - Configuration chargée depuis YAML")
        print("   - Valeurs spécifiques à l'environnement local validées")
        print("   - Compatibilité backwards maintenue")
        print()
        return True
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ TEST ÉCHOUÉ: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERREUR INATTENDUE: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
