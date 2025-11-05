# 🚀 Guide de Déploiement - Environnement DEV

## Vue d'ensemble

Ce guide détaille le déploiement de l'application JLC sur l'environnement **dev** (intégration/développement).

---

## 📋 Prérequis

- ✅ Accès au serveur dev
- ✅ Git configuré
- ✅ Python 3.11+
- ✅ MongoDB accessible
- ✅ Fichier `.env.key` (clé de déchiffrement)

---

## 🔐 Étape 1 : Préparer les Secrets

### Option A : Utiliser .env.encrypted (Recommandé pour dev)

**Sur votre machine locale :**

```bash
cd /app/auth-microservice

# 1. Créer le fichier .env pour dev
cat > .env.dev << 'EOF'
# Database
MONGO_URL=mongodb://dev-mongodb-host:27017
DATABASE_NAME=auth_db_dev

# JWT
JWT_SECRET_KEY=dev-jwt-secret-key-change-me-min-32-chars
JWT_ALGORITHM=HS256

# OAuth2 Google
GOOGLE_CLIENT_ID=your-dev-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-dev-google-client-secret
GOOGLE_REDIRECT_URI=https://dev.jlc-platform.com/auth/google/callback

# Email (SendGrid optionnel)
SENDGRID_API_KEY=SG.your-dev-sendgrid-api-key

# Storage (AWS S3 Dev)
AWS_ACCESS_KEY_ID=your-dev-aws-access-key
AWS_SECRET_ACCESS_KEY=your-dev-aws-secret-key
AWS_REGION=eu-west-1
EOF

# 2. Chiffrer le fichier
python scripts/encrypt_env.py encrypt .env.dev .env.dev.encrypted

# 3. Commiter .env.dev.encrypted (sécurisé)
git add .env.dev.encrypted
git commit -m "Add dev encrypted secrets"
git push

# 4. Partager .env.key de manière sécurisée
# NE PAS commiter .env.key !
# Options :
# - 1Password (équipe dev)
# - Vault HashiCorp
# - Message chiffré PGP
# - AWS S3 privé avec IAM
```

---

## 🏗️ Étape 2 : Déploiement sur le Serveur Dev

### Connexion au serveur

```bash
ssh user@dev-server.jlc-platform.com
cd /app
```

### Clone/Update du code

```bash
# Premier déploiement
git clone https://github.com/votre-org/jlc-app.git /app
cd /app

# Ou mise à jour
cd /app
git pull origin main
```

### Installation des dépendances

```bash
# Backend
cd /app/auth-microservice
pip install -r requirements.txt

# Frontend
cd /app/apps/web
yarn install
```

### Configuration de l'environnement

```bash
# 1. Définir l'environnement
export APP_ENV=dev

# 2. Récupérer la clé de déchiffrement (.env.key)
# Copier depuis 1Password ou votre gestionnaire de secrets
# Placer dans /app/auth-microservice/.env.key

# 3. Déchiffrer les secrets
cd /app/auth-microservice
python scripts/encrypt_env.py decrypt .env.dev.encrypted .env

# 4. Vérifier que .env existe
ls -la .env
cat .env  # Vérifier le contenu (sans partager !)
```

### Validation de la configuration

```bash
# Test de chargement de la config
cd /app/auth-microservice
python scripts/test_config.py

# Devrait afficher :
# ✅ TOUS LES TESTS SONT PASSÉS
```

---

## 🚀 Étape 3 : Démarrage des Services

### Avec Supervisor

```bash
# Copier la config supervisor si nécessaire
sudo cp /app/config/supervisor/dev.conf /etc/supervisor/conf.d/jlc-dev.conf

# Recharger supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Démarrer les services
sudo supervisorctl start jlc-backend-dev
sudo supervisorctl start jlc-frontend-dev

# Vérifier le statut
sudo supervisorctl status
```

### Avec Docker Compose (Alternative)

```bash
cd /app

# Créer docker-compose.dev.yml
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  auth-microservice:
    build:
      context: ./auth-microservice
      dockerfile: Dockerfile
    environment:
      - APP_ENV=dev
    volumes:
      - ./auth-microservice/.env:/app/.env:ro
      - ./auth-microservice/config:/app/config:ro
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
      - VITE_API_BASE_URL=https://dev-api.jlc-platform.com
    ports:
      - "3000:3000"
    restart: unless-stopped

  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb-dev-data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
    ports:
      - "27017:27017"
    restart: unless-stopped

volumes:
  mongodb-dev-data:
EOF

# Démarrer
docker-compose -f docker-compose.dev.yml up -d

# Vérifier les logs
docker-compose -f docker-compose.dev.yml logs -f
```

---

## ✅ Étape 4 : Validation Post-Déploiement

### Tests de santé

```bash
# 1. Health check backend
curl https://dev-api.jlc-platform.com/health
# Devrait retourner :
# {
#   "status": "healthy",
#   "service": "JLC Auth Service",
#   "version": "1.0.0",
#   "environment": "dev"
# }

# 2. Test configuration
curl https://dev-api.jlc-platform.com/
# Devrait retourner les infos du service

# 3. Test OAuth status
curl https://dev-api.jlc-platform.com/api/auth/google/status
# {
#   "enabled": true,
#   "configured": true
# }

# 4. Test frontend
curl -I https://dev.jlc-platform.com
# HTTP/1.1 200 OK
```

### Tests fonctionnels

```bash
# 1. Test login
curl -X POST https://dev-api.jlc-platform.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@jlc.com",
    "password": "Test1234!"
  }'

# 2. Test création mission (avec token)
curl -X POST https://dev-api.jlc-platform.com/api/missions \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Mission Dev",
    "contract_type": "cdi"
  }'

# 3. Test upload document
curl -X POST https://dev-api.jlc-platform.com/api/documents/upload \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test.pdf" \
  -F "document_type=cv"
```

---

## 📊 Étape 5 : Monitoring

### Logs

```bash
# Supervisor
sudo tail -f /var/log/supervisor/jlc-backend-dev.*.log

# Docker
docker-compose -f docker-compose.dev.yml logs -f auth-microservice

# Application logs
tail -f /var/log/jlc/auth-service.log
```

### Métriques (si activées)

```bash
# Prometheus metrics
curl https://dev-api.jlc-platform.com:9090/metrics

# Application stats
curl https://dev-api.jlc-platform.com/api/auth/admin/stats \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

---

## 🔄 Mises à Jour

### Déploiement d'une nouvelle version

```bash
# 1. Se connecter au serveur
ssh user@dev-server.jlc-platform.com

# 2. Pull du code
cd /app
git pull origin main

# 3. Installer nouvelles dépendances (si nécessaire)
cd /app/auth-microservice
pip install -r requirements.txt

cd /app/apps/web
yarn install

# 4. Redémarrer les services
sudo supervisorctl restart jlc-backend-dev
sudo supervisorctl restart jlc-frontend-dev

# Ou avec Docker
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build

# 5. Vérifier les logs
sudo supervisorctl tail -f jlc-backend-dev
```

### Mise à jour de la configuration

```bash
# 1. Éditer config/dev.yaml localement
vim /app/auth-microservice/config/dev.yaml

# 2. Commit et push
git add config/dev.yaml
git commit -m "Update dev config: ..."
git push

# 3. Sur le serveur, pull et restart
cd /app
git pull
sudo supervisorctl restart jlc-backend-dev
```

### Mise à jour des secrets

```bash
# 1. Sur votre machine locale
cd /app/auth-microservice

# 2. Éditer .env.dev
vim .env.dev

# 3. Re-chiffrer
python scripts/encrypt_env.py encrypt .env.dev .env.dev.encrypted

# 4. Commit et push
git add .env.dev.encrypted
git commit -m "Update dev secrets"
git push

# 5. Sur le serveur
cd /app/auth-microservice
git pull
python scripts/encrypt_env.py decrypt .env.dev.encrypted .env
sudo supervisorctl restart jlc-backend-dev
```

---

## 🐛 Troubleshooting

### Service ne démarre pas

```bash
# Vérifier les logs
sudo supervisorctl tail -f jlc-backend-dev stderr

# Erreurs communes :
# 1. Variable manquante
#    → Vérifier .env existe et contient toutes les variables
#    → Exécuter scripts/test_config.py

# 2. MongoDB inaccessible
#    → Vérifier MONGO_URL dans .env
#    → Tester connexion : mongosh $MONGO_URL

# 3. Port déjà utilisé
#    → Vérifier : netstat -tulpn | grep 8000
#    → Tuer le process : sudo kill <PID>
```

### Configuration incorrecte

```bash
# 1. Vérifier l'environnement détecté
curl https://dev-api.jlc-platform.com/health | jq .environment
# Devrait retourner : "dev"

# 2. Vérifier quelle config est chargée
cd /app/auth-microservice
python -c "
from awana_auth.core.config_manager import get_config
config = get_config()
print(f'Env: {config.env}')
print(f'Debug: {config.get(\"app.debug\")}')
print(f'Pool size: {config.get(\"database.pool_size\")}')
"
# dev devrait avoir debug=True, pool_size=10
```

### Secrets non déchiffrés

```bash
# Vérifier que .env.key existe
ls -la /app/auth-microservice/.env.key

# Re-déchiffrer
cd /app/auth-microservice
python scripts/encrypt_env.py decrypt .env.dev.encrypted .env

# Vérifier le contenu
head -n 5 .env
```

---

## 🔒 Sécurité

### Bonnes pratiques

1. **Clés de chiffrement**
   - ❌ Ne JAMAIS commiter .env.key
   - ✅ Stocker dans 1Password/Vault
   - ✅ Permissions restrictives : `chmod 600 .env.key`

2. **Secrets**
   - ❌ Ne JAMAIS logger les secrets
   - ❌ Ne JAMAIS commiter .env
   - ✅ Utiliser .env.encrypted versionné

3. **Accès serveur**
   - ✅ SSH avec clés uniquement
   - ✅ Firewall configuré
   - ✅ Logs d'accès activés

4. **Mise à jour**
   - ✅ Tester en local d'abord
   - ✅ Backup avant déploiement
   - ✅ Plan de rollback préparé

---

## 📋 Checklist Déploiement Dev

### Avant le déploiement
- [ ] Code testé en local
- [ ] Tests automatisés passent
- [ ] .env.dev.encrypted créé
- [ ] .env.key partagé de manière sécurisée
- [ ] Backup de la base de données

### Pendant le déploiement
- [ ] Code pullé sur le serveur
- [ ] Dépendances installées
- [ ] .env déchiffré
- [ ] Configuration validée (test_config.py)
- [ ] Services redémarrés

### Après le déploiement
- [ ] Health check OK
- [ ] Tests fonctionnels OK
- [ ] Logs vérifiés (pas d'erreur)
- [ ] OAuth configuré
- [ ] Upload fonctionne
- [ ] Monitoring actif

---

## 🔗 Liens Utiles

- **Config guide** : `/app/docs/CONFIGURATION_SYSTEM_GUIDE.md`
- **Phase 3 log** : `/app/docs/CONFIGURATION_PHASE3_COMPLETE.md`
- **Encrypt tool** : `/app/auth-microservice/scripts/encrypt_env.py`
- **Test script** : `/app/auth-microservice/scripts/test_config.py`

---

## 📞 Support

En cas de problème :
1. Vérifier les logs : `sudo supervisorctl tail -f jlc-backend-dev stderr`
2. Exécuter les tests : `python scripts/test_config.py`
3. Contacter : devops@jlc-platform.com

---

**Environnement DEV - Prêt pour l'intégration continue** ✅
