# 🔧 Guide du Système de Configuration Centralisé

## Vue d'ensemble

Le système de configuration de JLC permet de gérer toutes les valeurs de l'application de manière centralisée, sécurisée et adaptable par environnement.

**Principes clés :**
- ✅ Aucune valeur en dur dans le code
- ✅ Configuration hiérarchique par environnement
- ✅ Secrets chiffrés ou dans AWS Secrets Manager
- ✅ Surcharge par variables d'environnement
- ✅ Validation au démarrage (fail fast)
- ✅ Documentation et versioning

---

## 📁 Structure des Fichiers

```
/app/auth-microservice/
├── config/
│   ├── base.yaml           # Configuration par défaut
│   ├── local.yaml          # Dev local
│   ├── dev.yaml            # Intégration
│   ├── staging.yaml        # Préproduction
│   └── prod.yaml           # Production
├── .env                    # Secrets locaux (gitignored)
├── .env.encrypted          # Secrets chiffrés (versionné)
├── .env.key                # Clé de chiffrement (gitignored)
└── scripts/
    └── encrypt_env.py      # Utilitaire chiffrement
```

---

## 🔑 Ordre de Priorité

Le système charge les configurations dans cet ordre (du plus prioritaire au moins prioritaire) :

1. **Variables d'environnement système** (`export VAR=value`)
2. **AWS Secrets Manager** (prod uniquement)
3. **Fichier .env.encrypted** (déchiffré)
4. **Fichier .env**
5. **Fichier config/{env}.yaml**
6. **Fichier config/base.yaml**

---

## 💻 Utilisation dans le Code

### Initialisation (main.py)

```python
from awana_auth.core.config_manager import init_config, get_config

# Au démarrage de l'application
config = init_config(env="local")  # ou "dev", "staging", "prod"

# La validation stricte se fait automatiquement
# En cas d'erreur, l'application s'arrête (fail fast)
```

### Récupération de Valeurs

```python
from awana_auth.core.config_manager import get_config

config = get_config()

# Valeur simple
db_name = config.get("database.name")
# Résultat: "auth_db"

# Valeur avec défaut
pool_size = config.get("database.pool_size", default=10)

# Valeur requise (erreur si absente)
jwt_algo = config.get("security.jwt.algorithm", required=True)

# Valeur imbriquée
email_from = config.get("notifications.email.from_email")
# Résultat: "noreply@jlc-platform.com"

# Secret (depuis .env ou AWS)
mongo_url = config.get_secret("MONGO_URL", required=True)
jwt_secret = config.get_secret("JWT_SECRET_KEY", required=True)

# Valeur boolean
debug_mode = config.get("app.debug")
# Résultat: True ou False selon l'environnement
```

### Exemples Concrets

#### ❌ AVANT (hardcodé)

```python
# routes.py
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Hardcodé !
JWT_ALGORITHM = "HS256"  # Hardcodé !

@router.post("/login")
async def login(user: dict):
    token = create_token(
        user_id=user["id"],
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES  # ❌
    )
```

#### ✅ APRÈS (configuré)

```python
# routes.py
from awana_auth.core.config_manager import get_config

config = get_config()

@router.post("/login")
async def login(user: dict):
    token = create_token(
        user_id=user["id"],
        expires_minutes=config.get("security.jwt.access_token_expire_minutes")  # ✅
    )
```

---

## 🔐 Gestion des Secrets

### Environnements Local, Dev, Staging

**Utiliser .env.encrypted (chiffrement symétrique)**

#### 1. Générer une clé de chiffrement

```bash
cd /app/auth-microservice
python scripts/encrypt_env.py generate-key
```

Résultat : fichier `.env.key` créé (⚠️ **NE JAMAIS COMMITER**)

#### 2. Créer un fichier .env avec vos secrets

```bash
# .env
MONGO_URL=mongodb://localhost:27017
JWT_SECRET_KEY=super-secret-key-change-me
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnop
```

#### 3. Chiffrer le fichier

```bash
python scripts/encrypt_env.py encrypt .env .env.encrypted
```

Résultat : fichier `.env.encrypted` créé (✅ **Peut être commité**)

#### 4. Partager la clé de manière sécurisée

**Ne PAS envoyer .env.key par email ou Slack !**

Méthodes sécurisées :
- 🔐 1Password / LastPass / Bitwarden (partagé d'équipe)
- 🔐 Vault HashiCorp
- 🔐 AWS S3 privé avec accès IAM
- 🔐 En dernier recours : message chiffré PGP

#### 5. Déchiffrer en local (nouveau dev)

```bash
# Récupérer .env.key de manière sécurisée
# Puis déchiffrer
python scripts/encrypt_env.py decrypt .env.encrypted .env
```

### Environnement Production

**Utiliser AWS Secrets Manager**

#### 1. Créer le secret dans AWS

```bash
aws secretsmanager create-secret \
  --name jlc-auth-prod \
  --secret-string '{
    "MONGO_URL": "mongodb+srv://user:pass@cluster.mongodb.net/prod_db",
    "JWT_SECRET_KEY": "prod-super-secret-key",
    "GOOGLE_CLIENT_ID": "prod-client-id",
    "GOOGLE_CLIENT_SECRET": "prod-client-secret"
  }' \
  --region eu-west-1
```

#### 2. Configurer les permissions IAM

Donner l'accès `secretsmanager:GetSecretValue` au rôle EC2/ECS/Lambda

#### 3. L'application charge automatiquement

```python
# Au démarrage en prod
config = init_config(env="prod")
# Les secrets sont automatiquement chargés depuis AWS
```

#### Variables d'environnement requises

```bash
export APP_ENV=prod
export AWS_SECRET_NAME=jlc-auth-prod
export AWS_REGION=eu-west-1
```

---

## 🌍 Configuration par Environnement

### Local (développement)

**Fichier** : `config/local.yaml`

- Debug activé
- Rate limiting désactivé
- Délais raccourcis
- Notifications désactivées
- Cache court (5 min)

### Dev (intégration)

**Fichier** : `config/dev.yaml`

- Debug activé
- Rate limiting permissif
- Délais réduits
- Notifications activées (email uniquement)
- Cloud storage activé (S3 dev)

### Staging (préproduction)

**Fichier** : `config/staging.yaml`

- Proche de la prod
- Rate limiting normal
- Toutes les fonctionnalités activées
- Monitoring activé

### Production

**Fichier** : `config/prod.yaml`

- Debug désactivé
- Rate limiting strict
- Délais normaux
- Toutes sécurités activées
- Monitoring & tracing activés

---

## ✅ Validation au Démarrage

### Mode Strict (Prod, Staging)

L'application **s'arrête immédiatement** si :
- Une variable critique est absente
- Un secret requis n'est pas trouvé
- Une valeur est invalide

```python
config = init_config(env="prod")
config.validate(strict=True)
# ❌ Lève ConfigurationError si problème
```

### Mode Permissif (Local, Dev)

L'application **log des warnings** mais continue :

```python
config = init_config(env="local")
config.validate(strict=False)
# ⚠️  Log des warnings mais ne crash pas
```

### Variables Critiques

Variables obligatoires dans **tous les environnements** :
- `database.name`
- `database.url` (secret)
- `security.jwt.secret_key` (secret)
- `security.jwt.algorithm`
- `server.host`
- `server.port`

Variables obligatoires en **production uniquement** :
- `storage.cloud.bucket`
- `storage.cloud.region`
- `notifications.email.from_email`
- `security.oauth.google.client_id` (secret)
- `security.oauth.google.client_secret` (secret)

---

## 📋 Catégories de Configuration

### Database

```yaml
database:
  name: "auth_db"
  pool_size: 10
  max_pool_size: 50
  socket_timeout_ms: 30000
```

**Secrets** :
- `MONGO_URL`

### Security

```yaml
security:
  jwt:
    algorithm: "HS256"
    access_token_expire_minutes: 30
  password:
    min_length: 8
    max_attempts: 5
  rate_limit:
    enabled: true
    default_limit: 100
```

**Secrets** :
- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### Workflows

```yaml
workflows:
  mission:
    auto_publish: false
    max_applications_per_mission: 100
  application:
    delays:
      interview_scheduling: 7
      medical_check: 14
    restrictions:
      max_applications_per_candidate: 10
```

### Notifications

```yaml
notifications:
  email:
    enabled: true
    from_email: "noreply@jlc-platform.com"
    templates:
      application_received: "application_received"
```

**Secrets** :
- `SENDGRID_API_KEY` (si utilisé)
- `TWILIO_ACCOUNT_SID` (pour SMS)

### Storage

```yaml
storage:
  uploads:
    max_file_size_mb: 10
  cloud:
    enabled: true
    provider: "s3"
    bucket: "jlc-prod-uploads"
```

**Secrets** :
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Features (Feature Flags)

```yaml
features:
  mfa:
    enabled: true
  email_verification:
    enabled: true
  ai_features:
    enabled: false
```

---

## 🔄 Surcharge par Variable d'Environnement

Toute configuration peut être surchargée via une variable d'environnement :

```bash
# Surcharger le port
export SERVER_PORT=8080

# Surcharger le pool size de la DB
export DB_POOL_SIZE=20

# Activer le debug
export APP_DEBUG=true

# Désactiver les notifications
export NOTIFICATIONS_EMAIL_ENABLED=false
```

Le système mappe automatiquement :
- `SERVER_PORT` → `server.port`
- `DB_POOL_SIZE` → `database.pool_size`
- etc.

---

## 🚀 Déploiement

### Docker

```dockerfile
# Dockerfile
FROM python:3.11

# Copier les fichiers de config
COPY config/ /app/config/

# Copier le fichier .env.encrypted
COPY .env.encrypted /app/.env.encrypted

# NE PAS copier .env ni .env.key
# Ces fichiers sont injectés au runtime

# Variables d'environnement
ENV APP_ENV=prod
ENV AWS_SECRET_NAME=jlc-auth-prod
ENV AWS_REGION=eu-west-1
```

### Docker Compose (Dev/Staging)

```yaml
# docker-compose.yml
services:
  auth-service:
    environment:
      - APP_ENV=dev
      - MONGO_URL=${MONGO_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./.env.key:/app/.env.key:ro
```

### Kubernetes (Prod)

```yaml
# deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth-config
data:
  APP_ENV: "prod"
  AWS_SECRET_NAME: "jlc-auth-prod"
  AWS_REGION: "eu-west-1"
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      serviceAccountName: jlc-auth-service  # Avec IAM role
      containers:
      - name: auth
        envFrom:
        - configMapRef:
            name: auth-config
```

---

## 🔍 Debugging

### Afficher la configuration actuelle

```python
from awana_auth.core.config_manager import get_config

config = get_config()

# Voir toute la config (sans secrets)
print(config.get_all())

# Voir une valeur spécifique
print(config.get("database.pool_size"))
```

### Logs de configuration

Au démarrage, le système log :
```
🔧 Chargement de la configuration pour l'environnement: local
📄 Chargé: base.yaml
📄 Chargé: local.yaml
📄 Variables .env chargées
🔐 Secrets déchiffrés depuis .env.encrypted
✅ Configuration chargée avec succès
🔍 Validation de la configuration (strict=False)
✅ Validation de configuration réussie
```

---

## ⚠️ Erreurs Communes

### 1. ConfigurationError: Variable manquante

```
❌ Variable de configuration requise manquante: database.url
```

**Solution** : Ajouter la variable dans `.env` ou `config/{env}.yaml`

### 2. Erreur de déchiffrement

```
❌ Erreur lors du déchiffrement de .env.encrypted
```

**Solution** : Vérifier que vous avez la bonne clé `.env.key`

### 3. AWS Secrets Manager non accessible

```
⚠️  Secret AWS non trouvé: jlc-auth-prod
```

**Solutions** :
- Vérifier les permissions IAM
- Vérifier le nom du secret
- Vérifier la région AWS

---

## 📚 Bonnes Pratiques

### ✅ À FAIRE

1. **Toujours utiliser `config.get()`** au lieu de valeurs en dur
2. **Marquer les variables critiques comme required**
3. **Documenter chaque nouvelle configuration** dans `base.yaml`
4. **Tester sur tous les environnements** avant le merge
5. **Versionner les fichiers .yaml** dans git
6. **Chiffrer les .env** avant de les partager
7. **Utiliser AWS Secrets Manager** en production

### ❌ À ÉVITER

1. **Ne jamais commiter `.env`, `.env.key`**
2. **Ne jamais logger les secrets** (passwords, tokens)
3. **Ne pas hardcoder de valeurs** dans le code
4. **Ne pas partager les clés** par email/Slack
5. **Ne pas utiliser les mêmes secrets** entre environnements
6. **Ne pas désactiver la validation** en prod

---

## 🔗 Fichiers Associés

- **ConfigManager** : `/app/auth-microservice/awana_auth/core/config_manager.py`
- **Config base** : `/app/auth-microservice/config/base.yaml`
- **Utilitaire chiffrement** : `/app/auth-microservice/scripts/encrypt_env.py`
- **Gitignore secrets** : `/app/auth-microservice/.gitignore.secrets`

---

## 🆘 Support

En cas de problème :
1. Vérifier les logs au démarrage
2. Valider que tous les fichiers de config existent
3. Vérifier les permissions de lecture
4. Tester avec `config.get_all()` pour voir ce qui est chargé

Pour toute question : support-tech@jlc-platform.com
