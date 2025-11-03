# 🌐 Guide d'Architecture Cloud - Application JLC
## AWS, Azure & GCP

---

## 📊 Comparatif des Solutions Cloud

| Critère | AWS | Azure | GCP |
|---------|-----|-------|-----|
| **Coût** (estimation/mois) | $150-250 | $160-270 | $140-230 |
| **Facilité de déploiement** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalabilité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Support francophone** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Écosystème** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Présence Afrique** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🔷 Architecture AWS

### Vue d'ensemble

```
Internet
   ↓
CloudFront (CDN)
   ↓
Route 53 (DNS)
   ↓
Application Load Balancer
   ├─→ ECS Fargate (Frontend)
   ├─→ ECS Fargate (API Backend)
   ├─→ ECS Fargate (Auth Service)
   ↓
DocumentDB (MongoDB compatible)
```

### Services Recommandés

#### 1. **Computing & Containers**
- **ECS Fargate** (sans serveur) ou **EKS** (Kubernetes)
  - Frontend: 0.5 vCPU, 1GB RAM
  - API Backend: 1 vCPU, 2GB RAM
  - Auth Service: 0.5 vCPU, 1GB RAM

#### 2. **Base de Données**
- **Amazon DocumentDB** (compatible MongoDB)
  - Instance: db.t3.medium (2 vCPU, 4GB RAM)
  - Stockage: 100GB SSD
  - Backup automatique activé

**Alternative moins chère:**
- **MongoDB Atlas** sur AWS (géré par MongoDB)

#### 3. **Réseau & Sécurité**
- **VPC** avec sous-réseaux publics/privés
- **Application Load Balancer (ALB)**
- **Route 53** pour DNS
- **CloudFront** pour CDN
- **Certificate Manager** pour SSL/TLS gratuit
- **WAF** pour protection DDoS

#### 4. **Stockage & Assets**
- **S3** pour uploads utilisateurs
- **CloudFront** pour distribution

#### 5. **Monitoring & Logs**
- **CloudWatch** pour logs et métriques
- **X-Ray** pour tracing
- **SNS/SES** pour notifications email

### Configuration ECS (docker-compose → task-definition)

```json
{
  "family": "jlc-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "jlc-frontend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/jlc-frontend:latest",
      "cpu": 512,
      "memory": 1024,
      "portMappings": [{"containerPort": 80}],
      "environment": [
        {"name": "VITE_API_BASE_URL", "value": "https://api.votredomaine.com"}
      ]
    },
    {
      "name": "jlc-api",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/jlc-api:latest",
      "cpu": 1024,
      "memory": 2048,
      "portMappings": [{"containerPort": 8001}],
      "secrets": [
        {"name": "MONGO_URL", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

### Script de Déploiement AWS

```bash
#!/bin/bash
# deploy-aws.sh

# 1. Build et push des images vers ECR
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-1.amazonaws.com

docker build -t jlc-frontend:latest -f apps/web/Dockerfile.prod apps/web/
docker tag jlc-frontend:latest <account-id>.dkr.ecr.eu-west-1.amazonaws.com/jlc-frontend:latest
docker push <account-id>.dkr.ecr.eu-west-1.amazonaws.com/jlc-frontend:latest

# 2. Mise à jour du service ECS
aws ecs update-service --cluster jlc-cluster --service jlc-frontend --force-new-deployment

# 3. Attendre le déploiement
aws ecs wait services-stable --cluster jlc-cluster --services jlc-frontend
```

### Infrastructure as Code (Terraform)

```hcl
# main.tf
provider "aws" {
  region = "eu-west-1"
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name = "jlc-vpc"
  cidr = "10.0.0.0/16"
  azs  = ["eu-west-1a", "eu-west-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  enable_nat_gateway = true
}

# ECS Cluster
resource "aws_ecs_cluster" "jlc" {
  name = "jlc-cluster"
}

# DocumentDB
resource "aws_docdb_cluster" "jlc" {
  cluster_identifier     = "jlc-docdb"
  engine                 = "docdb"
  master_username        = var.db_username
  master_password        = var.db_password
  backup_retention_period = 7
  preferred_backup_window = "02:00-03:00"
}
```

### Estimation de Coûts AWS (mensuel)

| Service | Configuration | Coût/mois |
|---------|---------------|-----------|
| ECS Fargate | 3 conteneurs | $50-80 |
| DocumentDB | db.t3.medium | $90-120 |
| ALB | 1 instance | $20-25 |
| CloudFront | CDN | $10-15 |
| S3 | 50GB stockage | $5 |
| Route 53 | DNS hosting | $1 |
| **Total** | | **$176-246** |

---

## 🔷 Architecture Azure

### Vue d'ensemble

```
Internet
   ↓
Azure Front Door (CDN + WAF)
   ↓
Azure DNS
   ↓
Application Gateway
   ├─→ Container Instances (Frontend)
   ├─→ Container Instances (API)
   ├─→ Container Instances (Auth)
   ↓
Cosmos DB (MongoDB API)
```

### Services Recommandés

#### 1. **Computing & Containers**
**Option A: Azure Container Instances (ACI)** - Plus simple
- Frontend: 1 vCPU, 1.5GB RAM
- API Backend: 2 vCPU, 4GB RAM
- Auth Service: 1 vCPU, 2GB RAM

**Option B: Azure Kubernetes Service (AKS)** - Plus scalable
- Cluster managé avec auto-scaling

#### 2. **Base de Données**
- **Azure Cosmos DB** avec API MongoDB
  - Throughput: 1000 RU/s
  - Réplication géographique possible
  - Backup automatique

**Alternative:**
- **Azure Database for MongoDB** (preview)

#### 3. **Réseau & Sécurité**
- **Virtual Network (VNet)**
- **Application Gateway** avec WAF
- **Azure Front Door** pour CDN global
- **Azure DNS** pour gestion DNS
- **Key Vault** pour secrets

#### 4. **Stockage**
- **Blob Storage** pour uploads
- **CDN** pour distribution

#### 5. **Monitoring**
- **Application Insights** pour APM
- **Log Analytics** pour logs centralisés
- **Azure Monitor** pour alertes

### Configuration ACI (YAML)

```yaml
# aci-deploy.yaml
apiVersion: 2021-09-01
location: westeurope
name: jlc-app
properties:
  containers:
  - name: frontend
    properties:
      image: <registry>.azurecr.io/jlc-frontend:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1.5
      ports:
      - port: 80
      environmentVariables:
      - name: VITE_API_BASE_URL
        value: https://api.votredomaine.com
        
  - name: api
    properties:
      image: <registry>.azurecr.io/jlc-api:latest
      resources:
        requests:
          cpu: 2
          memoryInGb: 4
      ports:
      - port: 8001
      environmentVariables:
      - name: MONGO_URL
        secureValue: <cosmos-connection-string>
        
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 80
    - protocol: tcp
      port: 8001
```

### Script de Déploiement Azure

```bash
#!/bin/bash
# deploy-azure.sh

# 1. Login Azure
az login

# 2. Créer le groupe de ressources
az group create --name jlc-rg --location westeurope

# 3. Créer le Container Registry
az acr create --resource-group jlc-rg --name jlcregistry --sku Basic

# 4. Build et push des images
az acr build --registry jlcregistry --image jlc-frontend:latest --file apps/web/Dockerfile.prod apps/web/

# 5. Déployer avec Container Instances
az container create --resource-group jlc-rg --file aci-deploy.yaml

# 6. Ou déployer avec AKS
az aks create --resource-group jlc-rg --name jlc-aks --node-count 2
kubectl apply -f k8s-manifests/
```

### Infrastructure as Code (ARM Template)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2021-09-01",
      "name": "jlc-app",
      "location": "[resourceGroup().location]",
      "properties": {
        "containers": [
          {
            "name": "frontend",
            "properties": {
              "image": "jlcregistry.azurecr.io/jlc-frontend:latest",
              "resources": {
                "requests": {
                  "cpu": 1,
                  "memoryInGB": 1.5
                }
              }
            }
          }
        ],
        "osType": "Linux"
      }
    }
  ]
}
```

### Estimation de Coûts Azure (mensuel)

| Service | Configuration | Coût/mois |
|---------|---------------|-----------|
| Container Instances | 3 conteneurs | $60-90 |
| Cosmos DB | 1000 RU/s | $70-100 |
| Application Gateway | Standard v2 | $25-35 |
| Front Door | CDN | $15-20 |
| Blob Storage | 50GB | $5 |
| **Total** | | **$175-250** |

---

## 🔷 Architecture GCP

### Vue d'ensemble

```
Internet
   ↓
Cloud CDN
   ↓
Cloud DNS
   ↓
Cloud Load Balancing
   ├─→ Cloud Run (Frontend)
   ├─→ Cloud Run (API)
   ├─→ Cloud Run (Auth)
   ↓
MongoDB Atlas (on GCP)
```

### Services Recommandés

#### 1. **Computing & Containers**
**Cloud Run** (Recommandé - Serverless)
- Auto-scaling automatique
- Pay-per-use (très économique)
- Frontend: 1 vCPU, 512MB RAM
- API: 2 vCPU, 2GB RAM
- Auth: 1 vCPU, 1GB RAM

**Alternative: GKE** (Kubernetes)
- Plus de contrôle mais plus complexe

#### 2. **Base de Données**
- **MongoDB Atlas sur GCP** (Recommandé)
  - M10 tier (2GB RAM)
  - Backup automatique
  - Support officiel MongoDB

**Alternative:**
- **Cloud Firestore** (NoSQL natif GCP)

#### 3. **Réseau & Sécurité**
- **Cloud Load Balancing** (HTTPS)
- **Cloud CDN** pour caching
- **Cloud DNS** pour gestion DNS
- **Secret Manager** pour credentials
- **Cloud Armor** pour WAF/DDoS

#### 4. **Stockage**
- **Cloud Storage** pour uploads
- **CDN** intégré

#### 5. **Monitoring**
- **Cloud Monitoring** (Stackdriver)
- **Cloud Logging** pour logs
- **Cloud Trace** pour tracing

### Configuration Cloud Run

```yaml
# cloudrun-frontend.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: jlc-frontend
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/<project-id>/jlc-frontend:latest
        ports:
        - containerPort: 80
        env:
        - name: VITE_API_BASE_URL
          value: https://api.votredomaine.com
        resources:
          limits:
            cpu: "1000m"
            memory: 512Mi
```

```yaml
# cloudrun-api.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: jlc-api
spec:
  template:
    spec:
      containers:
      - image: gcr.io/<project-id>/jlc-api:latest
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: mongo-connection
              key: url
        resources:
          limits:
            cpu: "2000m"
            memory: 2Gi
```

### Script de Déploiement GCP

```bash
#!/bin/bash
# deploy-gcp.sh

PROJECT_ID="votre-project-id"
REGION="europe-west1"

# 1. Configurer le projet
gcloud config set project $PROJECT_ID

# 2. Activer les APIs nécessaires
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com

# 3. Build et déploiement avec Cloud Build
gcloud builds submit --config cloudbuild.yaml

# 4. Déployer sur Cloud Run
gcloud run deploy jlc-frontend \
  --image gcr.io/$PROJECT_ID/jlc-frontend:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --max-instances 10 \
  --memory 512Mi

gcloud run deploy jlc-api \
  --image gcr.io/$PROJECT_ID/jlc-api:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --max-instances 5 \
  --memory 2Gi \
  --set-secrets MONGO_URL=mongo-connection:latest

# 5. Configurer le Load Balancer
gcloud compute backend-services create jlc-backend \
  --global \
  --load-balancing-scheme=EXTERNAL
```

### Cloud Build Configuration

```yaml
# cloudbuild.yaml
steps:
  # Build Frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/jlc-frontend:latest', 
           '-f', 'apps/web/Dockerfile.prod', 'apps/web/']
  
  # Build API
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/jlc-api:latest', 
           '-f', 'apps/api/Dockerfile.prod', 'apps/api/']
  
  # Build Auth
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/jlc-auth:latest', 
           '-f', 'auth-microservice/Dockerfile.prod', 'auth-microservice/']

images:
  - 'gcr.io/$PROJECT_ID/jlc-frontend:latest'
  - 'gcr.io/$PROJECT_ID/jlc-api:latest'
  - 'gcr.io/$PROJECT_ID/jlc-auth:latest'
```

### Infrastructure as Code (Terraform)

```hcl
# main.tf
provider "google" {
  project = var.project_id
  region  = "europe-west1"
}

# Cloud Run Frontend
resource "google_cloud_run_service" "frontend" {
  name     = "jlc-frontend"
  location = "europe-west1"

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/jlc-frontend:latest"
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        
        env {
          name  = "VITE_API_BASE_URL"
          value = "https://api.votredomaine.com"
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM pour accès public
resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

### Estimation de Coûts GCP (mensuel)

| Service | Configuration | Coût/mois |
|---------|---------------|-----------|
| Cloud Run | 3 services | $30-50 |
| MongoDB Atlas | M10 tier | $60-80 |
| Load Balancing | HTTPS LB | $20-25 |
| Cloud CDN | Cache | $10-15 |
| Cloud Storage | 50GB | $3 |
| **Total** | | **$123-173** |

---

## 📊 Comparaison Détaillée

### Facilité de Déploiement

**🥇 GCP (Cloud Run)** - Le plus simple
- Déploiement en une commande
- Auto-scaling natif
- Configuration minimale

**🥈 AWS (ECS Fargate)** - Moyen
- Configuration task definitions
- Bon écosystème d'outils
- Plus de concepts à maîtriser

**🥉 Azure (ACI)** - Moyen-Complex
- Configuration via YAML ou Portal
- Intégration avec Azure DevOps
- Courbe d'apprentissage moyenne

### Performance & Scalabilité

**🥇 Égalité** - Tous excellents
- Auto-scaling réactif
- Distribution globale
- CDN performant

### Coût

**🥇 GCP** - Le moins cher ($123-173/mois)
- Modèle pay-per-use optimal
- Pas de coûts fixes élevés

**🥈 AWS** - Moyen ($176-246/mois)
- DocumentDB coûteux
- Meilleure optimisation possible

**🥉 Azure** - Similaire ($175-250/mois)
- Cosmos DB premium
- Bons rabais entreprise

### Support & Documentation

**🥇 AWS** - Le plus mature
- Documentation exhaustive
- Grande communauté
- Nombreux tutoriels

**🥈 GCP** - Excellente
- Documentation claire
- Exemples pratiques

**🥉 Azure** - Bonne
- Documentation complète
- Support Microsoft

---

## 🎯 Recommandations par Cas d'Usage

### Startup / MVP
**→ GCP Cloud Run**
- Coût minimal au démarrage
- Scaling automatique
- Configuration simple
- Facture uniquement l'usage réel

### PME / Croissance
**→ AWS ECS/Fargate**
- Écosystème complet
- Services managés matures
- Flexibilité maximale

### Entreprise / Complexe
**→ Azure AKS**
- Intégration Active Directory
- Outils entreprise (DevOps)
- Support Microsoft

### Multi-région / Afrique
**→ AWS**
- Présence Cap Town, Afrique du Sud
- Latence optimisée
- Edge locations nombreuses

---

## 🚀 Architecture Hybride Recommandée

### Approche Multi-Cloud

```
┌─────────────────────────────────────────┐
│         Cloud Agnostic Layer            │
├─────────────────────────────────────────┤
│                                         │
│  Docker Containers (Portable)           │
│  ├─ Frontend (React + Nginx)            │
│  ├─ Backend API (FastAPI)               │
│  └─ Auth Service (FastAPI)              │
│                                         │
├─────────────────────────────────────────┤
│         MongoDB Atlas                   │
│    (Deploy on any cloud)                │
└─────────────────────────────────────────┘
```

**Avantages:**
- Indépendance vis-à-vis d'un provider
- Migration facile entre clouds
- Résilience maximale

**Configuration MongoDB Atlas:**
- Déploiement multi-cloud possible
- Backup cross-region
- Pas de vendor lock-in

---

## 📝 Checklist de Déploiement

### Avant le Déploiement

- [ ] Choisir le cloud provider
- [ ] Créer un compte et configurer billing
- [ ] Installer les CLI (aws-cli, az, gcloud)
- [ ] Configurer les domaines DNS
- [ ] Obtenir les certificats SSL
- [ ] Préparer les variables d'environnement
- [ ] Configurer MongoDB (Atlas recommandé)

### Déploiement Initial

- [ ] Créer les repositories de containers
- [ ] Builder et pusher les images Docker
- [ ] Configurer les secrets/credentials
- [ ] Déployer les services
- [ ] Configurer le load balancer
- [ ] Activer le CDN
- [ ] Configurer le monitoring

### Post-Déploiement

- [ ] Tester tous les endpoints
- [ ] Vérifier les logs
- [ ] Configurer les alertes
- [ ] Mettre en place les backups
- [ ] Documenter la configuration
- [ ] Former l'équipe

---

## 💡 Conseils Pratiques

### Sécurité

1. **Secrets Management**
   - AWS: Secrets Manager
   - Azure: Key Vault
   - GCP: Secret Manager

2. **Network Security**
   - Utiliser des VPC/VNet privés
   - Whitelisting d'IPs si possible
   - Activer WAF sur le load balancer

3. **Authentification**
   - IAM roles pour services
   - Ne jamais mettre de credentials en dur
   - Rotation des secrets régulière

### Performance

1. **CDN Configuration**
   - Cache statique: 1 an
   - Cache API: selon besoin
   - Compression activée (gzip/brotli)

2. **Database Optimization**
   - Indexes sur champs fréquents
   - Connection pooling
   - Read replicas si nécessaire

3. **Container Optimization**
   - Multi-stage builds
   - Images légères (Alpine Linux)
   - Health checks configurés

### Monitoring

1. **Métriques Clés**
   - CPU/RAM utilization
   - Request latency
   - Error rate
   - Database connections

2. **Alertes**
   - Service down
   - Latence > 2s
   - Error rate > 1%
   - Disk usage > 80%

---

## 📞 Support

Pour toute question sur le déploiement cloud :
- Documentation AWS: https://aws.amazon.com/documentation/
- Documentation Azure: https://docs.microsoft.com/azure/
- Documentation GCP: https://cloud.google.com/docs

---

## 🎓 Ressources Complémentaires

### Tutoriels Vidéo
- AWS ECS: https://www.youtube.com/watch?v=esISkPlnxL0
- Azure Container Instances: https://www.youtube.com/watch?v=jAWLQFi4USk
- GCP Cloud Run: https://www.youtube.com/watch?v=nhwYc4StHIc

### Cours Gratuits
- AWS Free Tier: https://aws.amazon.com/free/
- Azure Free Account: https://azure.microsoft.com/free/
- GCP Free Tier: https://cloud.google.com/free

### Certifications
- AWS Solutions Architect
- Azure Administrator
- GCP Cloud Engineer

---

**Dernière mise à jour:** Novembre 2024
**Version:** 1.0
