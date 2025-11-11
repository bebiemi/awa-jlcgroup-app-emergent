# Guide Rapide de Déploiement - Application JLC

## 📚 Documentation Disponible

Voici tous les documents créés pour vous aider au déploiement :

### 1. **CHANGELOG_FIXES_COMPLETS.md**
Récapitulatif complet de tous les problèmes résolus et changements effectués.
- Liste des 4 problèmes résolus (403, ERR_SSL, 404, 503)
- Fichiers modifiés
- Configuration critique
- Variables d'environnement

### 2. **DEPLOIEMENT_DOCKER.md** 
Guide complet pour déploiement avec Docker Compose.
- docker-compose.yml complet
- Dockerfiles pour chaque service
- Configuration nginx
- Commandes de gestion
- Scaling et monitoring

### 3. **DEPLOIEMENT_WEBAPP.md**
Guide pour déploiement sur plateformes Cloud.
- Azure App Service
- AWS Elastic Beanstalk  
- Google Cloud Run
- MongoDB Atlas setup
- CI/CD pipelines
- Coûts estimés

### 4. **ARCHITECTURE_FINALE.md**
Documentation technique détaillée de l'architecture.
- Diagrammes complets
- Stack technologique
- Flux de données
- Système IAM
- Schéma MongoDB
- Sécurité et performance

---

## 🚀 Démarrage Rapide

### Option 1: Docker (Recommandé pour dev/staging)

```bash
# 1. Cloner et préparer
git clone <repo>
cd jlc-app
cp .env.example .env

# 2. Éditer .env avec vos valeurs
nano .env

# 3. Démarrer
docker-compose up -d

# 4. Initialiser la DB
docker-compose exec auth-microservice python scripts/init_default_configs.py

# 5. Accéder
open http://localhost
```

**Voir:** `DEPLOIEMENT_DOCKER.md` pour détails complets

### Option 2: Cloud Platform (Production)

#### Azure
```bash
az login
az acr build --registry jlcregistry --image jlc-app:latest .
az webapp create --name jlc-app --deployment-container-image-name jlcregistry.azurecr.io/jlc-app:latest
az webapp config appsettings set --settings MONGO_URL="..." JWT_SECRET="..."
```

#### AWS
```bash
eb init -p docker jlc-app
eb create jlc-production --envvars MONGO_URL=...,JWT_SECRET=...
eb deploy
```

#### GCP
```bash
gcloud builds submit --tag gcr.io/project-id/jlc-app
gcloud run deploy jlc-app --image gcr.io/project-id/jlc-app --set-env-vars="MONGO_URL=...,JWT_SECRET=..."
```

**Voir:** `DEPLOIEMENT_WEBAPP.md` pour détails complets

---

## ⚙️ Configuration Essentielle

### Variables d'Environnement Obligatoires

```bash
# MongoDB Connection
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/

# Database Names
DATABASE_NAME=auth_db

# JWT Secret (CHANGEZ CECI!)
JWT_SECRET=votre-secret-super-securise-minimum-32-caracteres

# Services URLs (déjà configurés par défaut)
AUTH_SERVICE_URL=http://localhost:8000
```

### MongoDB Atlas (Base de données Cloud)

1. Créer compte sur https://cloud.mongodb.com
2. Créer un cluster (M0 gratuit pour commencer)
3. Créer un user database
4. Whitelist les IPs (0.0.0.0/0 pour commencer)
5. Copier la connection string
6. Remplacer dans MONGO_URL

---

## 🔧 Points Critiques à Vérifier

### ✅ Checklist Avant Déploiement

- [ ] **JWT_SECRET changé** (pas la valeur par défaut !)
- [ ] **MongoDB accessible** (tester la connexion)
- [ ] **Port 80 exposé** (ou port configuré pour votre plateforme)
- [ ] **Nginx configuration** copiée correctement
- [ ] **Variables d'environnement** définies
- [ ] **Logs accessibles** pour debugging

### ⚠️ Problèmes Courants

**Erreur 503 Service Unavailable**
- Vérifier que nginx tourne
- Vérifier que backend/auth-microservice sont UP
- Voir les logs: `docker-compose logs backend`

**Erreur de connexion MongoDB**
- Vérifier MONGO_URL
- Vérifier whitelist IP dans MongoDB Atlas
- Tester: `mongosh "mongodb+srv://..."`

**Frontend ne charge pas**
- Vérifier nginx routing
- Voir logs: `docker-compose logs nginx`
- Port 3001 doit être accessible en interne

---

## 📊 Architecture Simplifiée

```
Internet → Nginx (80) → Backend (8001) → Auth (8000) → MongoDB
                      ↘ Frontend (3001)
```

**Ports:**
- 80: Nginx (point d'entrée externe)
- 8001: Backend Gateway
- 8000: Auth Microservice  
- 3001: Frontend React
- 27017: MongoDB

**Routing:**
- `/api/*` → Backend → Auth Microservice
- `/auth-api/*` → Backend → Auth Microservice
- `/*` → Frontend

---

## 🐛 Debugging

### Voir les Logs

**Docker:**
```bash
docker-compose logs -f backend
docker-compose logs -f auth-microservice
docker-compose logs -f nginx
```

**Azure:**
```bash
az webapp log tail --name jlc-app --resource-group jlc-rg
```

**AWS:**
```bash
eb logs --all
```

**GCP:**
```bash
gcloud run services logs read jlc-app --limit=100
```

### Tester les Services

```bash
# Health check
curl http://localhost/health

# Login
curl -X POST http://localhost/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# API avec token
curl http://localhost/api/besoins \
  -H "Authorization: Bearer <token>"
```

---

## 🔒 Sécurité - Important !

### À FAIRE en Production

1. **Changer JWT_SECRET** (32+ caractères aléatoires)
2. **HTTPS uniquement** (activer SSL)
3. **Restreindre CORS** (pas * en production)
4. **Whitelist MongoDB IPs** (pas 0.0.0.0/0)
5. **Activer monitoring** (logs, métriques)
6. **Backups automatiques** (MongoDB)
7. **Firewall** (limiter accès aux ports)
8. **Rate limiting** (nginx)

### Secrets Management

**Ne jamais commit:**
- `.env` files
- Clés API
- Passwords
- JWT_SECRET

**Utiliser:**
- Azure Key Vault
- AWS Secrets Manager
- GCP Secret Manager
- Docker secrets

---

## 📞 Support

### En cas de problème

1. **Consulter les docs** dans `/app/docs/`
2. **Vérifier les logs** des services
3. **Tester en local** (Docker) d'abord
4. **Isoler le problème** (quel service ?)
5. **Vérifier la config** (nginx, env vars)

### Fichiers de Configuration Importants

```
/app/
├── docs/                          # 📚 Toute la documentation
│   ├── CHANGELOG_FIXES_COMPLETS.md
│   ├── DEPLOIEMENT_DOCKER.md
│   ├── DEPLOIEMENT_WEBAPP.md
│   └── ARCHITECTURE_FINALE.md
│
├── nginx/
│   ├── nginx.conf                 # Config nginx principale
│   └── conf.d/jlc-app.conf       # Routing rules
│
├── apps/
│   ├── api/                       # Backend Gateway
│   │   ├── server.py
│   │   └── src/presentation/routes/*_proxy_routes.py
│   │
│   └── web/                       # Frontend React
│       ├── vite.config.ts
│       └── src/utils/baseQueryWithAuth.ts
│
├── auth-microservice/             # Service d'authentification
│   ├── main.py
│   └── scripts/                   # Scripts d'initialisation
│
├── docker-compose.yml             # Config Docker
├── .env                          # Variables d'environnement
└── README.md                     # Ce fichier
```

---

## 🎯 Prochaines Étapes

1. **Choisir votre méthode de déploiement** (Docker ou Cloud)
2. **Lire le guide complet** correspondant
3. **Préparer MongoDB** (Atlas ou autre)
4. **Configurer les variables** d'environnement
5. **Déployer** en suivant le guide
6. **Initialiser la base** de données
7. **Tester** l'application
8. **Monitorer** les logs et métriques

---

## 📈 Évolution

### Aujourd'hui
- ✅ Application fonctionnelle
- ✅ Architecture microservices
- ✅ IAM complet
- ✅ Documentation complète

### Prochainement
- [ ] Tests automatisés
- [ ] CI/CD pipeline
- [ ] Monitoring avancé
- [ ] Scaling horizontal
- [ ] Cache Redis
- [ ] CDN pour assets

---

**Version:** 1.0  
**Date:** 11 Novembre 2025  
**Status:** ✅ Production Ready
