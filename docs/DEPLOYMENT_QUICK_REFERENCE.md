# 🚀 Guide de Déploiement - Référence Rapide

## 📋 Commandes Essentielles

### Configuration & Secrets

```bash
# Générer clé de chiffrement
cd /app/auth-microservice
python scripts/encrypt_env.py generate-key

# Chiffrer secrets
python scripts/encrypt_env.py encrypt .env .env.encrypted

# Déchiffrer secrets
python scripts/encrypt_env.py decrypt .env.encrypted .env

# Tester configuration
python scripts/test_config.py

# Définir l'environnement
export APP_ENV=local   # ou dev, staging, prod
```

---

## 🔧 Services (Supervisor)

```bash
# Status
sudo supervisorctl status

# Démarrer
sudo supervisorctl start jlc-backend-dev
sudo supervisorctl start jlc-frontend-dev

# Arrêter
sudo supervisorctl stop jlc-backend-dev

# Redémarrer
sudo supervisorctl restart jlc-backend-dev
sudo supervisorctl restart all

# Logs en temps réel
sudo supervisorctl tail -f jlc-backend-dev
sudo supervisorctl tail -f jlc-backend-dev stderr

# Recharger config
sudo supervisorctl reread
sudo supervisorctl update
```

---

## 🐳 Services (Docker)

```bash
# Dev/Staging
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml restart
docker-compose -f docker-compose.dev.yml logs -f auth-microservice

# Production
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml restart auth-microservice
docker-compose -f docker-compose.prod.yml logs -f --tail=100 auth-microservice

# Rebuild
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🏥 Health Checks

```bash
# Backend local
curl http://localhost:8000/health

# Backend dev
curl https://dev-api.jlc-platform.com/health

# Backend production
curl https://api.jlc-platform.com/health

# OAuth status
curl http://localhost:8000/api/auth/google/status

# Admin stats (avec token)
curl http://localhost:8000/api/auth/admin/stats \
  -H "Authorization: Bearer ${TOKEN}"

# Frontend
curl -I http://localhost:3000
curl -I https://jlc-platform.com
```

---

## 🗄️ MongoDB

```bash
# Connexion
mongosh $MONGO_URL

# Backup
mongodump --uri="${MONGO_URL}" --out=/backups/$(date +%Y%m%d_%H%M%S)

# Restore
mongorestore --uri="${MONGO_URL}" /backups/20251105_143000/

# Stats
mongosh $MONGO_URL --eval "db.serverStatus()"
mongosh $MONGO_URL --eval "db.stats()"

# Lister bases
mongosh $MONGO_URL --eval "show dbs"

# Lister collections
mongosh $MONGO_URL --eval "use auth_db; show collections"

# Compter users
mongosh $MONGO_URL --eval "db.users.countDocuments()"
```

---

## 🔐 AWS Secrets Manager

```bash
# Créer secret
aws secretsmanager create-secret \
  --name jlc-auth-prod \
  --secret-string file://secrets.json \
  --region eu-west-1

# Lire secret
aws secretsmanager get-secret-value \
  --secret-id jlc-auth-prod \
  --region eu-west-1 \
  --query SecretString \
  --output text | jq .

# Modifier secret
aws secretsmanager update-secret \
  --secret-id jlc-auth-prod \
  --secret-string file://new-secrets.json \
  --region eu-west-1

# Lister secrets
aws secretsmanager list-secrets --region eu-west-1

# Supprimer secret (avec délai 30 jours)
aws secretsmanager delete-secret \
  --secret-id jlc-auth-prod \
  --recovery-window-in-days 30 \
  --region eu-west-1
```

---

## 📦 Déploiement Complet

### Dev

```bash
# 1. Se connecter au serveur
ssh user@dev-server.jlc-platform.com

# 2. Pull code
cd /app
git pull origin main

# 3. Installer dépendances
cd /app/auth-microservice && pip install -r requirements.txt
cd /app/apps/web && yarn install

# 4. Déchiffrer secrets
cd /app/auth-microservice
python scripts/encrypt_env.py decrypt .env.dev.encrypted .env

# 5. Tester config
python scripts/test_config.py

# 6. Redémarrer
sudo supervisorctl restart all

# 7. Vérifier
curl https://dev-api.jlc-platform.com/health
```

### Production

```bash
# 1. Backup
mongodump --uri="${MONGO_URL}" --out=/backups/$(date +%Y%m%d)

# 2. Pull code
cd /app && git pull origin main

# 3. Build Docker
docker-compose -f docker-compose.prod.yml build

# 4. Deploy avec zero-downtime
docker-compose -f docker-compose.prod.yml up -d --no-deps --build auth-microservice

# 5. Attendre démarrage
sleep 30

# 6. Health check
curl https://api.jlc-platform.com/health || {
    echo "❌ Health check failed - Rollback"
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    exit 1
}

# 7. Frontend
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# 8. Vérifier logs
docker-compose -f docker-compose.prod.yml logs --tail=50 auth-microservice
```

---

## 🔄 Rollback

### Supervisor

```bash
# 1. Trouver dernier commit stable
git log --oneline -10

# 2. Checkout
git checkout <commit-hash>

# 3. Redémarrer
sudo supervisorctl restart all
```

### Docker

```bash
# 1. Arrêter services
docker-compose -f docker-compose.prod.yml down

# 2. Checkout code précédent
cd /app
git checkout HEAD~1

# 3. Rebuild et redéployer
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Vérifier
curl https://api.jlc-platform.com/health
```

---

## 📊 Logs

```bash
# Backend Supervisor
tail -f /var/log/supervisor/jlc-backend-dev.out.log
tail -f /var/log/supervisor/jlc-backend-dev.err.log
tail -n 100 /var/log/supervisor/jlc-backend-dev.*.log

# Frontend Supervisor
tail -f /var/log/supervisor/jlc-frontend-dev.out.log

# Application logs
tail -f /var/log/jlc/auth-service.log

# Docker logs
docker-compose logs -f --tail=100 auth-microservice
docker-compose logs -f frontend

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# MongoDB logs (si local)
tail -f /var/log/mongodb/mongod.log
```

---

## 🐛 Dépannage Express

### Service ne démarre pas

```bash
# Vérifier logs
sudo supervisorctl tail -f jlc-backend-dev stderr

# Vérifier config
python scripts/test_config.py

# Vérifier port disponible
netstat -tulpn | grep 8000
lsof -i :8000

# Tuer process bloquant
kill -9 $(lsof -t -i:8000)
```

### Erreur MongoDB

```bash
# Test connexion
mongosh $MONGO_URL

# Vérifier MONGO_URL
echo $MONGO_URL
cat /app/auth-microservice/.env | grep MONGO_URL

# Ping MongoDB
ping mongodb-host
telnet mongodb-host 27017
```

### Secret manquant

```bash
# Vérifier .env existe
ls -la /app/auth-microservice/.env

# Vérifier contenu
cat /app/auth-microservice/.env | grep JWT_SECRET_KEY

# Re-déchiffrer
python scripts/encrypt_env.py decrypt .env.encrypted .env

# Vérifier environnement
echo $APP_ENV
```

### Frontend ne charge pas

```bash
# Vérifier service
sudo supervisorctl status jlc-frontend-dev

# Vérifier port
curl http://localhost:3000

# Vérifier build
cd /app/apps/web
yarn build

# Vérifier .env
cat .env | grep REACT_APP_BACKEND_URL
```

---

## 🔍 Debug Configuration

```bash
# Environnement détecté
curl http://localhost:8000/health | jq .environment

# Vérifier quelle config est chargée
python -c "
from awana_auth.core.config_manager import get_config
config = get_config()
print(f'Env: {config.env}')
print(f'Debug: {config.get(\"app.debug\")}')
print(f'JWT algo: {config.get(\"security.jwt.algorithm\")}')
print(f'Pool size: {config.get(\"database.pool_size\")}')
"

# Lister toutes les variables d'environnement
env | grep -E "(MONGO|JWT|GOOGLE|AWS)"

# Vérifier fichiers de config
ls -la /app/auth-microservice/config/
cat /app/auth-microservice/config/local.yaml
```

---

## 📋 Checklist Déploiement Rapide

### Avant

- [ ] Code testé localement
- [ ] Tests passent
- [ ] Backup BD fait
- [ ] Secrets configurés

### Pendant

- [ ] Code déployé
- [ ] Dépendances installées
- [ ] Config validée
- [ ] Services redémarrés

### Après

- [ ] Health check OK
- [ ] Tests de fumée OK
- [ ] Logs vérifiés
- [ ] Monitoring actif

---

## 🚨 Contacts Urgence

- **DevOps**: devops@jlc-platform.com
- **Support**: support-tech@jlc-platform.com
- **Urgences**: +241-XX-XX-XX-XX

---

## 📖 Documentation Complète

- [Deployment Overview](/app/docs/DEPLOYMENT_OVERVIEW.md)
- [Dev Guide](/app/docs/DEPLOYMENT_DEV_GUIDE.md)
- [Prod Guide](/app/docs/DEPLOYMENT_PROD_GUIDE.md)
- [Config System](/app/docs/CONFIGURATION_SYSTEM_GUIDE.md)

---

**Dernière mise à jour**: 5 Novembre 2025
