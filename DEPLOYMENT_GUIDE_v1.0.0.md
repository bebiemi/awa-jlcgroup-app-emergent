# 🚀 Guide de Déploiement - JLC Group Platform v1.0.0 Stable

**Version** : 1.0.0-stable  
**Date** : 15 Novembre 2025  
**Status** : Production Ready

---

## 📋 Prérequis

### Système
- **OS** : Linux (Ubuntu 20.04+ recommandé)
- **RAM** : Minimum 4GB (8GB recommandé)
- **CPU** : 2 cores minimum (4 cores recommandé)
- **Disque** : 20GB disponible minimum

### Logiciels requis
- **Docker** : 20.10+
- **Docker Compose** : 2.0+
- **Git** : 2.x
- **Node.js** : 18.x LTS
- **Python** : 3.11+
- **MongoDB** : 7.0+
- **Supervisor** : 4.x

---

## 🔧 Installation Environnement Local

### Étape 1 : Clone du repository

```bash
# Clone le projet
git clone <repository-url> jlc-group-platform
cd jlc-group-platform

# Checkout la version stable
git checkout tags/v1.0.0-stable

# Vérifier la version
cat VERSION.txt
# Output: 1.0.0-stable
```

### Étape 2 : Configuration des variables d'environnement

#### Frontend (`/app/apps/web/.env`)
```bash
# Ne PAS modifier ces variables en production !
VITE_BACKEND_URL=
VITE_API_BASE_URL=
# VITE_AUTH_SERVICE_URL=  # Commenté - utilise URLs relatives
```

**⚠️ IMPORTANT** : Laisser vide pour utiliser les URLs relatives. Le proxy Vite/Kubernetes gère le routing.

#### Backend (`/app/apps/api/.env`)
```bash
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=jlc_db
AUTH_SERVICE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
UPLOAD_DIR=/app/uploads
BASE_URL=http://localhost:8001

# Email (optionnel)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@jlcgroup.com
FROM_NAME=JLC Group

ENVIRONMENT=development
```

#### Auth Microservice (`/app/auth-microservice/.env`)
```bash
MONGO_URL=mongodb://localhost:27017
APP_ENV=local

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Awana2025!
ADMIN_EMAIL=admin@jlcgroup.com

# JWT Configuration
JWT_SECRET_KEY=<générer-clé-secrète-32-caractères>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# OAuth (optionnel)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

# Email Notifications
EMAIL_NOTIFICATIONS_ENABLED=false
ADMIN_NOTIFICATION_EMAILS=admin@jlcgroup.com
```

**🔐 Génération JWT Secret Key** :
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Étape 3 : Installation des dépendances

#### Frontend
```bash
cd apps/web
yarn install
cd ../..
```

#### Backend
```bash
cd apps/api
pip install -r requirements.txt
cd ../..
```

#### Auth Microservice
```bash
cd auth-microservice
pip install -r requirements.txt
cd ..
```

### Étape 4 : Démarrage MongoDB

```bash
# Démarrer MongoDB
sudo systemctl start mongodb

# Vérifier le statut
sudo systemctl status mongodb

# Ou via Docker
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

### Étape 5 : Démarrage des services avec Supervisor

```bash
# Démarrer tous les services
sudo supervisorctl start all

# Vérifier le statut
sudo supervisorctl status

# Output attendu:
# auth-microservice    RUNNING   pid xxx, uptime x:xx:xx
# backend              RUNNING   pid xxx, uptime x:xx:xx
# frontend-custom      RUNNING   pid xxx, uptime x:xx:xx
# mongodb              RUNNING   pid xxx, uptime x:xx:xx
```

### Étape 6 : Vérification de l'installation

```bash
# Test backend health
curl http://localhost:8001/health
# {"status":"healthy"}

# Test auth microservice
curl http://localhost:8000/health
# {"status":"healthy","service":"AWANA Auth Microservice"}

# Test frontend
curl http://localhost:3000
# HTML page should load
```

### Étape 7 : Login initial

1. Ouvrir navigateur : `http://localhost:3000`
2. Login avec credentials admin :
   - **Username** : `admin`
   - **Password** : `Awana2025!`
3. Redirection vers dashboard admin

---

## 🌐 Déploiement Emergent Preview (HTTPS)

### Configuration spécifique

La version v1.0.0 inclut la détection automatique de l'environnement Emergent preview. Aucune configuration manuelle n'est nécessaire.

**Auto-détection** :
- Détecte `*.preview.emergentagent.com`
- Détecte `*.emergent.host`
- Force automatiquement HTTPS dans les URLs API
- Convertit HTTP → HTTPS via customFetch

**Vérification** :
```javascript
// Console navigateur doit afficher :
🔒 Emergent Preview detected - Using HTTPS baseUrl: https://[hostname]/api
```

### Variables d'environnement Emergent

```bash
# Frontend (.env)
# Laisser VIDE - la détection automatique gère tout
VITE_BACKEND_URL=
VITE_API_BASE_URL=

# Backend (.env)
MONGO_URL=<mongo-url-emergent>
AUTH_SERVICE_URL=http://auth-microservice:8000
CORS_ORIGINS=https://workflow-mapper-6.preview.emergentagent.com
BASE_URL=https://workflow-mapper-6.preview.emergentagent.com
ENVIRONMENT=production
```

---

## 🐳 Déploiement Docker (Production)

### Docker Compose

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: jlc-mongodb
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: auth_db

  auth-microservice:
    build:
      context: ./auth-microservice
      dockerfile: Dockerfile
    container_name: jlc-auth
    restart: always
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - APP_ENV=production
    depends_on:
      - mongodb

  backend:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    container_name: jlc-backend
    restart: always
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - AUTH_SERVICE_URL=http://auth-microservice:8000
    depends_on:
      - mongodb
      - auth-microservice

  frontend:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    container_name: jlc-frontend
    restart: always
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

### Commandes Docker

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ perte de données)
docker-compose down -v
```

---

## ☸️ Déploiement Kubernetes

### Manifests

#### 1. MongoDB Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongodb-storage
          mountPath: /data/db
      volumes:
      - name: mongodb-storage
        persistentVolumeClaim:
          claimName: mongodb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
```

#### 2. Auth Microservice Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-microservice
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-microservice
  template:
    metadata:
      labels:
        app: auth-microservice
    spec:
      containers:
      - name: auth-microservice
        image: jlc-auth:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: MONGO_URL
          value: "mongodb://mongodb:27017"
        - name: APP_ENV
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: auth-microservice
spec:
  selector:
    app: auth-microservice
  ports:
  - port: 8000
    targetPort: 8000
```

#### 3. Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: jlc-backend:1.0.0
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          value: "mongodb://mongodb:27017"
        - name: AUTH_SERVICE_URL
          value: "http://auth-microservice:8000"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
  - port: 8001
    targetPort: 8001
```

#### 4. Frontend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: jlc-frontend:1.0.0
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
```

#### 5. Ingress (HTTPS)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jlc-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - jlcgroup.com
    - api.jlcgroup.com
    secretName: jlc-tls
  rules:
  - host: jlcgroup.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: api.jlcgroup.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8001
```

### Commandes Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployments
kubectl get deployments

# Check pods
kubectl get pods

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# View logs
kubectl logs -f deployment/backend

# Scale deployment
kubectl scale deployment backend --replicas=5
```

---

## 🔄 Rollback

### Rollback vers version précédente

```bash
# Voir les tags disponibles
git tag -l

# Checkout version précédente
git checkout tags/<version-précédente>

# Redémarrer services
sudo supervisorctl restart all
```

### Rollback avec Docker

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout tags/<version-précédente>

# Rebuild and start
docker-compose build
docker-compose up -d
```

### Rollback avec Kubernetes

```bash
# Rollback deployment
kubectl rollout undo deployment/backend
kubectl rollout undo deployment/frontend
kubectl rollout undo deployment/auth-microservice

# Check rollout status
kubectl rollout status deployment/backend
```

---

## 📊 Monitoring

### Logs

```bash
# Supervisor logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
tail -f /var/log/supervisor/auth-microservice.*.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes logs
kubectl logs -f deployment/backend
```

### Health Checks

```bash
# Backend health
curl https://api.jlcgroup.com/health

# Auth microservice health
curl https://api.jlcgroup.com/api/auth/health

# Frontend (page loads)
curl https://jlcgroup.com
```

### Métriques à surveiller

- **CPU Usage** : < 70%
- **RAM Usage** : < 80%
- **Response Time** : < 500ms (95th percentile)
- **Error Rate** : < 1%
- **Uptime** : > 99.9%

---

## 🔐 Sécurité Production

### Checklist Sécurité

- [ ] JWT_SECRET_KEY unique et fort (32+ caractères)
- [ ] HTTPS activé et forcé (HSTS)
- [ ] CORS configuré avec origines spécifiques
- [ ] Rate limiting activé
- [ ] Firewall configuré (ports 22, 80, 443 uniquement)
- [ ] MongoDB authentification activée
- [ ] Backups automatiques configurés
- [ ] Monitoring et alertes en place
- [ ] SSL certificates valides (Let's Encrypt)
- [ ] Headers sécurisés (CSP, X-Frame-Options, etc.)

### Variables sensibles

```bash
# Ne JAMAIS committer dans Git :
JWT_SECRET_KEY
ADMIN_PASSWORD
MONGO_URL (production)
SMTP_PASSWORD
GOOGLE_CLIENT_SECRET
MICROSOFT_CLIENT_SECRET
```

### Stockage secrets (Kubernetes)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: jlc-secrets
type: Opaque
stringData:
  jwt-secret: <base64-encoded-secret>
  mongo-url: <base64-encoded-url>
  admin-password: <base64-encoded-password>
```

---

## 🔧 Troubleshooting

### Problème : Services ne démarrent pas

```bash
# Vérifier logs
sudo supervisorctl tail -f backend

# Vérifier ports occupés
sudo netstat -tulpn | grep -E '3000|8000|8001|27017'

# Restart service
sudo supervisorctl restart backend
```

### Problème : MongoDB connection failed

```bash
# Vérifier MongoDB status
sudo systemctl status mongodb

# Tester connexion
mongosh mongodb://localhost:27017

# Vérifier configuration
cat /app/apps/api/.env | grep MONGO_URL
```

### Problème : Frontend 404 errors

```bash
# Vérifier Vite config
cat /app/apps/web/vite.config.ts

# Vérifier proxy configuration
# Target doit être localhost:8001 (pas jlc-api:8001)

# Restart frontend
sudo supervisorctl restart frontend-custom
```

### Problème : 307 Redirects

**Résolu dans v1.0.0** ✅

Si problème persiste :
- Vérifier proxy routes ont base + {path:path}
- Voir `/app/PROXY_307_FIX_SUMMARY.md`

### Problème : Mixed Content (HTTPS)

**Résolu dans v1.0.0** ✅

Si problème persiste :
- Vérifier console : doit afficher `🔒 Emergent Preview detected`
- Voir `/app/MIXED_CONTENT_FIX_DOCUMENTATION.md`

---

## 📞 Support

### Documentation
- Release Notes : `/app/RELEASE_NOTES_v1.0.0.md`
- Proxy Fix : `/app/PROXY_307_FIX_SUMMARY.md`
- Mixed Content Fix : `/app/MIXED_CONTENT_FIX_DOCUMENTATION.md`
- Roadmap V2 : `/app/ROADMAP_V2.md`

### Contact
- **Email** : devops@jlcgroup.com
- **Documentation** : `/app/docs/`
- **Issues** : Créer ticket sur système de ticketing interne

---

## ✅ Checklist de déploiement

### Pré-déploiement
- [ ] Backup base de données
- [ ] Vérifier variables d'environnement
- [ ] Tester sur environnement staging
- [ ] Review notes de release
- [ ] Notifications équipe prévues

### Déploiement
- [ ] Checkout version stable `v1.0.0-stable`
- [ ] Build images/packages
- [ ] Deploy services
- [ ] Vérifier health checks
- [ ] Smoke tests (login, dashboard, API)

### Post-déploiement
- [ ] Monitoring actif
- [ ] Logs surveillance (30 min)
- [ ] Tests utilisateurs finaux
- [ ] Documentation mise à jour
- [ ] Communication déploiement réussi

---

**Version** : 1.0.0-stable  
**Document** : Guide de Déploiement  
**Dernière mise à jour** : 15 Novembre 2025  
**Status** : ✅ Validé pour Production
