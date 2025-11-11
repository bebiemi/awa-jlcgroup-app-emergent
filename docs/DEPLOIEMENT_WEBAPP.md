# Guide de Déploiement Web App - Application JLC

## Vue d'Ensemble

Ce guide explique comment déployer l'application JLC sur des plateformes de type "Web App" (Azure App Service, AWS Elastic Beanstalk, Google Cloud Run, etc.).

---

## Architecture Déployée

```
┌────────────────────────────────────────────────┐
│  Load Balancer / Ingress                       │
│  (HTTPS, SSL Termination)                      │
└──────────────────┬─────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐      ┌──────────────┐
│  Web App     │      │  MongoDB     │
│  Container   │      │  (Managed)   │
│              │      │  Atlas/Cosmos│
│  ┌────────┐ │      └──────────────┘
│  │ Nginx  │ │
│  │ (80)   │ │
│  └───┬────┘ │
│      │      │
│  ┌───┴────┐ │
│  │Backend │ │
│  │(8001)  │ │
│  └───┬────┘ │
│      │      │
│  ┌───┴────┐ │
│  │  Auth  │ │
│  │ (8000) │ │
│  └────────┘ │
│             │
│  ┌────────┐ │
│  │Frontend│ │
│  │ (3001) │ │
│  └────────┘ │
└──────────────┘
```

**Points clés:**
- Tout dans UN SEUL container (multi-process avec supervisor)
- MongoDB en service managé séparé
- Port 80 exposé (Nginx)
- Processes internes: Nginx + Backend + Auth + Frontend

---

## Option 1: Azure App Service

### Prérequis
- Azure CLI installé
- Compte Azure actif
- MongoDB Atlas ou Azure Cosmos DB

### 1. Préparation

#### Dockerfile pour Azure

`/Dockerfile.azure`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    nodejs \
    npm \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application
COPY . .

# Install Python dependencies
RUN cd auth-microservice && pip install --no-cache-dir -r requirements.txt
RUN cd apps/api && pip install --no-cache-dir -r requirements.txt

# Install Frontend dependencies and build
RUN cd apps/web && yarn install && yarn build

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/jlc-app.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 80

# Start supervisor
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
```

#### Supervisor Configuration

`/supervisor/supervisord.conf`:

```ini
[supervisord]
nodaemon=true
user=root

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/nginx.err.log
stdout_logfile=/var/log/supervisor/nginx.out.log
priority=10

[program:auth-microservice]
command=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
directory=/app/auth-microservice
autostart=true
autorestart=true
environment=MONGO_URL="%(ENV_MONGO_URL)s",DATABASE_NAME="%(ENV_DATABASE_NAME)s"
stderr_logfile=/var/log/supervisor/auth.err.log
stdout_logfile=/var/log/supervisor/auth.out.log
priority=20

[program:backend]
command=/usr/local/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/apps/api
autostart=true
autorestart=true
environment=MONGO_URL="%(ENV_MONGO_URL)s",AUTH_SERVICE_URL="http://localhost:8000"
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
priority=20

[program:frontend]
command=/usr/local/bin/yarn vite --host 0.0.0.0 --port 3001
directory=/app/apps/web
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
priority=30
```

#### Nginx Configuration

`/nginx/conf.d/jlc-app.conf`:

```nginx
server {
    listen 80;
    server_name _;

    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # API Routes
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Important: Remove X-Forwarded headers for internal calls
        proxy_set_header Connection "";
    }

    # Auth API Routes
    location /auth-api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8001/health;
        access_log off;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        
        # WebSocket for HMR
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 2. MongoDB Atlas Setup

```bash
# 1. Créer un cluster sur MongoDB Atlas
# 2. Créer un database user
# 3. Whitelist Azure IPs
# 4. Copier la connection string

# Connection string format:
# mongodb+srv://<username>:<password>@cluster.mongodb.net/<dbname>?retryWrites=true&w=majority
```

### 3. Déploiement sur Azure

```bash
# Login
az login

# Créer un resource group
az group create --name jlc-rg --location westeurope

# Créer un Azure Container Registry (optionnel)
az acr create --resource-group jlc-rg --name jlcregistry --sku Basic

# Build et push l'image
az acr build --registry jlcregistry --image jlc-app:latest -f Dockerfile.azure .

# Créer l'App Service Plan
az appservice plan create \
  --name jlc-plan \
  --resource-group jlc-rg \
  --is-linux \
  --sku B1

# Créer la Web App
az webapp create \
  --resource-group jlc-rg \
  --plan jlc-plan \
  --name jlc-app \
  --deployment-container-image-name jlcregistry.azurecr.io/jlc-app:latest

# Configurer les variables d'environnement
az webapp config appsettings set \
  --resource-group jlc-rg \
  --name jlc-app \
  --settings \
    MONGO_URL="mongodb+srv://..." \
    DATABASE_NAME="auth_db" \
    JWT_SECRET="your-secret-key"

# Activer le logging
az webapp log config \
  --resource-group jlc-rg \
  --name jlc-app \
  --docker-container-logging filesystem

# Voir les logs
az webapp log tail --resource-group jlc-rg --name jlc-app
```

### 4. Configuration SSL

```bash
# Ajouter un domaine custom
az webapp config hostname add \
  --webapp-name jlc-app \
  --resource-group jlc-rg \
  --hostname yourdomain.com

# Activer HTTPS
az webapp update \
  --resource-group jlc-rg \
  --name jlc-app \
  --https-only true

# Créer un certificat managé
az webapp config ssl create \
  --resource-group jlc-rg \
  --name jlc-app \
  --hostname yourdomain.com
```

---

## Option 2: AWS Elastic Beanstalk

### 1. Préparation

#### Dockerrun.aws.json

```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "your-registry/jlc-app:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 80,
      "HostPort": 80
    }
  ],
  "Logging": "/var/log/nginx"
}
```

#### .ebextensions/01_environment.config

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    MONGO_URL: "mongodb+srv://..."
    DATABASE_NAME: "auth_db"
    JWT_SECRET: "your-secret-key"
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: none
```

### 2. Déploiement

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker jlc-app --region eu-west-1

# Create environment
eb create jlc-production \
  --instance-type t3.medium \
  --envvars MONGO_URL=mongodb+srv://...,JWT_SECRET=...

# Deploy
eb deploy

# Open in browser
eb open

# Logs
eb logs
```

### 3. Scaling

```bash
# Configure auto-scaling
eb scale 3

# Configure load balancer
eb config
```

---

## Option 3: Google Cloud Run

### 1. Préparation

Même Dockerfile que Azure (Dockerfile.azure)

### 2. Déploiement

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project your-project-id

# Build image
gcloud builds submit --tag gcr.io/your-project-id/jlc-app

# Deploy
gcloud run deploy jlc-app \
  --image gcr.io/your-project-id/jlc-app \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 80 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars="MONGO_URL=mongodb+srv://...,DATABASE_NAME=auth_db,JWT_SECRET=..."

# Get URL
gcloud run services describe jlc-app --region europe-west1 --format="value(status.url)"
```

---

## Variables d'Environnement Requises

### Obligatoires

```bash
# MongoDB
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=auth_db

# JWT
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# Services (défauts OK)
AUTH_SERVICE_URL=http://localhost:8000
```

### Optionnelles

```bash
# JWT Configuration
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Environnement
NODE_ENV=production
```

---

## Configuration MongoDB Atlas

### 1. Créer le Cluster

1. Aller sur https://cloud.mongodb.com
2. Créer un cluster (M0 Free tier ou M10+ pour production)
3. Créer un database user:
   - Username: `jlc_app`
   - Password: (générer un mot de passe fort)
4. Network Access:
   - Ajouter `0.0.0.0/0` (ou IP spécifiques de votre cloud provider)

### 2. Connection String

```
mongodb+srv://jlc_app:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### 3. Créer les Databases

```javascript
// Se connecter via mongosh ou Compass
use auth_db
use jlc_db
```

### 4. Initialiser les Données

Après déploiement, exécuter:

```bash
# Via Azure CLI
az webapp ssh --name jlc-app --resource-group jlc-rg
cd /app/auth-microservice
python scripts/init_default_configs.py
python scripts/assign_profiles_to_users.py

# Via AWS
eb ssh
# Même commandes

# Via GCP
gcloud run services list
# Note: Cloud Run est stateless, utiliser Cloud SQL ou script externe
```

---

## Monitoring et Logs

### Azure

```bash
# Live logs
az webapp log tail --name jlc-app --resource-group jlc-rg

# Download logs
az webapp log download --name jlc-app --resource-group jlc-rg

# Application Insights (recommandé)
az monitor app-insights component create \
  --app jlc-insights \
  --location westeurope \
  --resource-group jlc-rg
```

### AWS

```bash
# CloudWatch logs
eb logs --stream

# Metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElasticBeanstalk \
  --metric-name EnvironmentHealth \
  --dimensions Name=EnvironmentName,Value=jlc-production
```

### GCP

```bash
# Logs
gcloud run services logs read jlc-app --region europe-west1 --tail=100

# Metrics dans Google Cloud Console
# Operations > Logging / Monitoring
```

---

## CI/CD Pipeline

### GitHub Actions Example

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push image
        run: |
          az acr build \
            --registry jlcregistry \
            --image jlc-app:${{ github.sha }} \
            --image jlc-app:latest \
            -f Dockerfile.azure .
      
      - name: Deploy to App Service
        run: |
          az webapp config container set \
            --name jlc-app \
            --resource-group jlc-rg \
            --docker-custom-image-name jlcregistry.azurecr.io/jlc-app:${{ github.sha }}
          
          az webapp restart \
            --name jlc-app \
            --resource-group jlc-rg
      
      - name: Run migrations
        run: |
          # Script pour exécuter les migrations
          echo "Migrations executed"
```

---

## Sécurité - Production Checklist

### Obligatoire

- [ ] Changer JWT_SECRET (minimum 32 caractères aléatoires)
- [ ] Utiliser HTTPS uniquement
- [ ] Configurer CORS correctement
- [ ] Whitelist IPs MongoDB
- [ ] Activer les firewalls
- [ ] Utiliser secrets management (Azure Key Vault, AWS Secrets Manager, etc.)
- [ ] Configurer rate limiting nginx
- [ ] Activer les logs et monitoring
- [ ] Backups automatiques MongoDB

### Recommandé

- [ ] WAF (Web Application Firewall)
- [ ] DDoS protection
- [ ] Content Security Policy headers
- [ ] Vulnerability scanning
- [ ] Secrets rotation automatique
- [ ] Multi-region deployment
- [ ] Disaster recovery plan

---

## Scaling

### Vertical Scaling (Plus de ressources)

```bash
# Azure
az appservice plan update --name jlc-plan --sku P1V2

# AWS
eb scale --instance-type t3.large

# GCP
gcloud run services update jlc-app --memory 4Gi --cpu 4
```

### Horizontal Scaling (Plus d'instances)

```bash
# Azure - Auto-scaling
az monitor autoscale create \
  --resource-group jlc-rg \
  --resource jlc-app \
  --min-count 2 \
  --max-count 10 \
  --count 2

# AWS
eb config
# Set MinSize=2, MaxSize=10 dans configuration

# GCP - Auto-scaling par défaut
gcloud run services update jlc-app --min-instances=2 --max-instances=10
```

---

## Troubleshooting

### L'application ne démarre pas

```bash
# Vérifier les logs
# Azure
az webapp log tail --name jlc-app --resource-group jlc-rg

# AWS
eb logs --all

# GCP
gcloud run services logs read jlc-app --limit=100
```

### Erreur de connexion MongoDB

1. Vérifier la connection string
2. Vérifier le whitelist IP dans MongoDB Atlas
3. Tester la connexion depuis le container

```bash
# Dans le container
mongosh "mongodb+srv://..."
```

### Performance lente

1. Augmenter les ressources (CPU/RAM)
2. Vérifier les indexes MongoDB
3. Activer le cache
4. CDN pour les assets statiques
5. Monitoring des requêtes lentes

---

## Coûts Estimés

### Azure App Service
- Basic (B1): ~50€/mois
- Standard (S1): ~70€/mois
- Premium (P1V2): ~150€/mois

### AWS Elastic Beanstalk
- t3.medium: ~35$/mois
- t3.large: ~70$/mois
- + Load Balancer: ~20$/mois

### Google Cloud Run
- Pay per use
- 2 CPU, 2GB RAM: ~30-100$/mois selon trafic

### MongoDB Atlas
- M0 (Free): 0€
- M10: ~60$/mois
- M20: ~130$/mois

---

## Support

Pour plus d'informations:
- Architecture: `CHANGELOG_FIXES_COMPLETS.md`
- Docker deployment: `DEPLOIEMENT_DOCKER.md`
