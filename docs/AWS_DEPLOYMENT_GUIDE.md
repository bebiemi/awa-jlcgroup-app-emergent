# 🚀 Guide de Déploiement AWS - Application JLC
## Production-Ready Step by Step

---

## 📋 Table des Matières

1. [Vue d'ensemble des Options](#vue-densemble-des-options)
2. [Option 1 : EC2 + Docker Compose (Simple)](#option-1--ec2--docker-compose)
3. [Option 2 : ECS Fargate (Recommandé)](#option-2--ecs-fargate)
4. [Option 3 : EKS Kubernetes (Avancé)](#option-3--eks-kubernetes)
5. [Configuration SSL avec AWS](#configuration-ssl-aws)
6. [Estimation des Coûts](#estimation-des-coûts)
7. [Checklist de Déploiement](#checklist-de-déploiement)

---

## 🎯 Vue d'ensemble des Options

### Comparaison Rapide

| Critère | EC2 Simple | ECS Fargate | EKS |
|---------|-----------|-------------|-----|
| **Complexité** | ⭐ Facile | ⭐⭐ Moyen | ⭐⭐⭐⭐ Avancé |
| **Coût/mois** | $50-80 | $100-150 | $150-250 |
| **Scalabilité** | ⭐⭐ Manuelle | ⭐⭐⭐⭐ Auto | ⭐⭐⭐⭐⭐ Max |
| **Maintenance** | ⭐⭐ Élevée | ⭐⭐⭐⭐ Faible | ⭐⭐⭐ Moyenne |
| **Temps setup** | 2-4h | 4-8h | 8-16h |
| **Production** | ⭐⭐⭐ OK | ⭐⭐⭐⭐⭐ Parfait | ⭐⭐⭐⭐⭐ Entreprise |

### Recommandation par Cas d'Usage

**🟢 Débutant / MVP** : EC2 Simple
**🔵 Production Standard** : ECS Fargate ⭐ **RECOMMANDÉ**
**🟣 Grande Échelle** : EKS

---

## 🟢 Option 1 : EC2 + Docker Compose (Simple)

### Architecture

```
Internet → Route 53 → EC2 Instance
                      ├── Docker (Nginx)
                      ├── Docker (Frontend)
                      ├── Docker (API)
                      ├── Docker (Auth)
                      └── Docker (MongoDB)
```

### Étape 1 : Créer une Instance EC2

#### 1.1 Connexion à AWS Console
```
https://console.aws.amazon.com/
→ Services → EC2 → Launch Instance
```

#### 1.2 Configuration Instance

**Nom** : `jlc-app-production`

**AMI** : Ubuntu Server 22.04 LTS (Free Tier eligible)

**Type d'instance** :
- **MVP/Test** : `t3.medium` (2 vCPU, 4GB RAM) - ~$30/mois
- **Production** : `t3.large` (2 vCPU, 8GB RAM) - ~$60/mois
- **Recommandé** : `t3.xlarge` (4 vCPU, 16GB RAM) - ~$120/mois

**Key pair** : 
- Créer une nouvelle paire de clés
- Nom : `jlc-app-key`
- Type : RSA
- Format : `.pem`
- **TÉLÉCHARGER et SAUVEGARDER** en lieu sûr

**Réseau** :
- VPC : Default (ou créer un nouveau)
- Sous-réseau : Public
- IP publique : Activer

**Pare-feu (Security Group)** :
Créer un nouveau groupe nommé `jlc-app-sg` avec :
```
Type          | Port | Source        | Description
SSH           | 22   | Mon IP        | Accès SSH
HTTP          | 80   | 0.0.0.0/0     | Trafic HTTP
HTTPS         | 443  | 0.0.0.0/0     | Trafic HTTPS
Custom TCP    | 8001 | 10.0.0.0/16   | API (interne)
Custom TCP    | 27017| 10.0.0.0/16   | MongoDB (interne)
```

**Stockage** :
- Type : gp3 (SSD)
- Taille : 50 GB (minimum)
- Recommandé : 100 GB

#### 1.3 Lancer l'Instance

Cliquez sur "Launch Instance" et attendez 2-3 minutes.

### Étape 2 : Connexion à l'Instance

```bash
# Permissions sur la clé
chmod 400 jlc-app-key.pem

# Connexion SSH
ssh -i jlc-app-key.pem ubuntu@<VOTRE-IP-PUBLIQUE-EC2>

# Exemple
ssh -i jlc-app-key.pem ubuntu@54.123.45.67
```

### Étape 3 : Installation Docker sur EC2

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker ubuntu
newgrp docker

# Vérification
docker --version
docker compose version
```

### Étape 4 : Déploiement de l'Application

```bash
# Créer le dossier application
sudo mkdir -p /opt/jlc-app
sudo chown ubuntu:ubuntu /opt/jlc-app
cd /opt/jlc-app

# Cloner le code (option 1 - si vous avez un repo Git)
git clone https://github.com/votre-compte/jlc-app.git .

# OU transférer depuis votre machine locale (option 2)
# Sur votre machine locale :
# scp -i jlc-app-key.pem -r /chemin/local/jlc-app/* ubuntu@54.123.45.67:/opt/jlc-app/
```

### Étape 5 : Configuration

```bash
cd /opt/jlc-app/docker

# Créer .env.prod
nano .env.prod
```

**Contenu minimal** :
```bash
MONGO_ROOT_USERNAME=admin_jlc_prod
MONGO_ROOT_PASSWORD=VotreMotDePasseTresSecurise123!@#
JWT_SECRET=votre-secret-jwt-tres-long-et-aleatoire-minimum-32-caracteres
CORS_ORIGINS=https://votredomaine.com,https://www.votredomaine.com
API_BASE_URL=https://api.votredomaine.com
SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=votre-smtp-user
SMTP_PASSWORD=votre-smtp-password
ENVIRONMENT=production
```

### Étape 6 : SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install -y certbot

# Arrêter Docker temporairement
docker compose -f docker-compose.prod.yml down

# Générer les certificats
sudo certbot certonly --standalone \
  -d votredomaine.com \
  -d www.votredomaine.com \
  -d api.votredomaine.com \
  -d auth.votredomaine.com \
  --agree-tos \
  --email votre-email@example.com

# Copier les certificats
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem nginx/ssl/key.pem
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

### Étape 7 : Lancement

```bash
# Build et démarrage
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs -f

# Vérifier l'état
docker ps
```

### Étape 8 : Configuration DNS

**Dans Route 53** (ou votre fournisseur DNS) :

```
Type A : votredomaine.com → <IP-PUBLIQUE-EC2>
Type A : www.votredomaine.com → <IP-PUBLIQUE-EC2>
Type A : api.votredomaine.com → <IP-PUBLIQUE-EC2>
Type A : auth.votredomaine.com → <IP-PUBLIQUE-EC2>
```

### Étape 9 : Renouvellement SSL Automatique

```bash
# Configurer le script de renouvellement
cd /opt/jlc-app/docker/scripts
chmod +x setup-ssl-renewal.sh
sudo ./setup-ssl-renewal.sh
```

### ✅ Vérification EC2

```bash
# Test local
curl http://localhost:3000
curl http://localhost:8001/health

# Test externe
curl https://votredomaine.com
curl https://api.votredomaine.com/health
```

---

## 🔵 Option 2 : ECS Fargate (Recommandé Production) ⭐

### Architecture

```
Internet
   ↓
Route 53 (DNS)
   ↓
CloudFront (CDN) [Optionnel]
   ↓
Application Load Balancer (ALB)
   ├─→ ECS Service (Frontend - 2 tasks)
   ├─→ ECS Service (API - 2 tasks)
   └─→ ECS Service (Auth - 2 tasks)
        ↓
   DocumentDB ou MongoDB Atlas
```

### Avantages
- ✅ **Sans serveur** : Pas de gestion d'infrastructure
- ✅ **Auto-scaling** : S'adapte à la charge
- ✅ **Haute disponibilité** : Multi-AZ automatique
- ✅ **Certificats SSL gratuits** : AWS Certificate Manager
- ✅ **Monitoring intégré** : CloudWatch

### Étape 1 : Prérequis

#### 1.1 Installer AWS CLI

```bash
# Sur votre machine locale
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Télécharger depuis https://aws.amazon.com/cli/
```

#### 1.2 Configurer AWS CLI

```bash
aws configure

# Entrer :
# AWS Access Key ID: (créer dans IAM)
# AWS Secret Access Key: (créer dans IAM)
# Default region: eu-west-1 (ou votre région)
# Default output format: json
```

#### 1.3 Installer ECS CLI (optionnel)

```bash
# macOS
brew install amazon-ecs-cli

# Linux
sudo curl -Lo /usr/local/bin/ecs-cli \
  https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest
sudo chmod +x /usr/local/bin/ecs-cli
```

### Étape 2 : Créer un Repository ECR (Elastic Container Registry)

```bash
# Créer les repositories pour chaque service
aws ecr create-repository --repository-name jlc-frontend --region eu-west-1
aws ecr create-repository --repository-name jlc-api --region eu-west-1
aws ecr create-repository --repository-name jlc-auth --region eu-west-1

# Noter les URLs retournées, exemple:
# 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-frontend
```

### Étape 3 : Build et Push des Images Docker

```bash
# Se connecter à ECR
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.eu-west-1.amazonaws.com

# Build des images
cd /chemin/vers/jlc-app

# Frontend
docker build -t jlc-frontend:latest -f apps/web/Dockerfile.prod .
docker tag jlc-frontend:latest 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-frontend:latest
docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-frontend:latest

# API
docker build -t jlc-api:latest -f apps/api/Dockerfile.prod .
docker tag jlc-api:latest 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-api:latest
docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-api:latest

# Auth
docker build -t jlc-auth:latest -f auth-microservice/Dockerfile.prod .
docker tag jlc-auth:latest 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-auth:latest
docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-auth:latest
```

### Étape 4 : Configuration de la Base de Données

#### Option A : MongoDB Atlas (Recommandé)

1. **Aller sur** : https://cloud.mongodb.com
2. **Créer un cluster** dans AWS région `eu-west-1`
3. **Plan** : M10 ou M20 (environ $50-100/mois)
4. **Whitelist IP** : 0.0.0.0/0 (pour ECS)
5. **Créer un utilisateur** et noter la connection string

#### Option B : Amazon DocumentDB

```bash
# Via Console AWS
# Services → DocumentDB → Create cluster
# Instance class: db.t3.medium
# Number of instances: 1 (ou 3 pour HA)
# VPC: Même que ECS
```

### Étape 5 : Créer un Cluster ECS

#### Via Console AWS

1. **Services → ECS → Clusters → Create Cluster**
2. **Nom** : `jlc-app-cluster`
3. **Infrastructure** : AWS Fargate
4. **VPC** : Créer nouveau ou utiliser existant
5. **Subnets** : Sélectionner au moins 2 AZ
6. **Create**

#### Via CLI

```bash
aws ecs create-cluster --cluster-name jlc-app-cluster --region eu-west-1
```

### Étape 6 : Créer Task Definitions

#### Frontend Task Definition

Créer `task-def-frontend.json` :

```json
{
  "family": "jlc-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "123456789.dkr.ecr.eu-west-1.amazonaws.com/jlc-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REACT_APP_BACKEND_URL",
          "value": "https://api.votredomaine.com"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jlc-frontend",
          "awslogs-region": "eu-west-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Enregistrer** :
```bash
aws ecs register-task-definition --cli-input-json file://task-def-frontend.json
```

#### API & Auth Task Definitions

Créer de même pour API et Auth (voir template complet dans le guide).

### Étape 7 : Créer un Application Load Balancer

#### Via Console AWS

1. **EC2 → Load Balancers → Create Load Balancer**
2. **Type** : Application Load Balancer
3. **Nom** : `jlc-app-alb`
4. **Scheme** : Internet-facing
5. **IP address type** : IPv4
6. **Availability Zones** : Sélectionner au moins 2
7. **Security Group** :
   - Port 80 (HTTP) : 0.0.0.0/0
   - Port 443 (HTTPS) : 0.0.0.0/0
8. **Target Groups** : Créer 3 groupes
   - `jlc-frontend-tg` (Port 80)
   - `jlc-api-tg` (Port 8001)
   - `jlc-auth-tg` (Port 8000)

### Étape 8 : Configuration SSL avec AWS Certificate Manager

```bash
# Via Console AWS
# Certificate Manager → Request certificate
# Type: Public
# Domain names:
#   - votredomaine.com
#   - *.votredomaine.com
# Validation: DNS (recommandé) ou Email
```

**Valider** : Ajouter les CNAME records dans Route 53

**Associer au ALB** :
1. ALB → Listeners → Add HTTPS:443
2. Certificate : Sélectionner votre certificat ACM
3. Default action : Forward to target group

### Étape 9 : Créer les Services ECS

```bash
# Frontend Service
aws ecs create-service \
  --cluster jlc-app-cluster \
  --service-name jlc-frontend-service \
  --task-definition jlc-frontend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=frontend,containerPort=80"

# Répéter pour API et Auth
```

### Étape 10 : Configuration Route 53

```bash
# Créer des enregistrements ALIAS pointant vers l'ALB
# votredomaine.com → ALB
# api.votredomaine.com → ALB (avec routing rules)
# auth.votredomaine.com → ALB (avec routing rules)
```

### ✅ Vérification ECS

```bash
# Vérifier les services
aws ecs list-services --cluster jlc-app-cluster

# Vérifier les tasks
aws ecs list-tasks --cluster jlc-app-cluster --service-name jlc-frontend-service

# Logs
aws logs tail /ecs/jlc-frontend --follow
```

---

## 📊 Estimation des Coûts AWS

### Option 1 : EC2 Simple

| Service | Configuration | Coût/mois |
|---------|--------------|-----------|
| EC2 t3.large | 2 vCPU, 8GB RAM | $60 |
| EBS Storage | 100 GB gp3 | $8 |
| Data Transfer | 100 GB sortant | $9 |
| **TOTAL** | | **~$77/mois** |

### Option 2 : ECS Fargate

| Service | Configuration | Coût/mois |
|---------|--------------|-----------|
| ECS Fargate | 3 services × 2 tasks | $90 |
| ALB | 1 load balancer | $16 |
| DocumentDB | db.t3.medium | $80 |
| ECR | 10 GB images | $1 |
| CloudWatch | Logs standard | $5 |
| Data Transfer | 100 GB | $9 |
| **TOTAL** | | **~$201/mois** |

**Alternative avec MongoDB Atlas** : ~$150/mois

### Réduction des Coûts

- ✅ **Reserved Instances** : -40% sur EC2/RDS
- ✅ **Savings Plans** : -30-50% sur Fargate
- ✅ **Auto-scaling** : Payer uniquement ce qui est utilisé
- ✅ **S3 Intelligent-Tiering** : Optimisation automatique

---

## ✅ Checklist de Déploiement AWS

### Avant le Déploiement

- [ ] Compte AWS créé et vérifié
- [ ] Domaine acheté et configuré
- [ ] AWS CLI installé et configuré
- [ ] Docker installé localement
- [ ] Code source prêt à déployer
- [ ] Variables d'environnement documentées
- [ ] Budget AWS défini

### Pendant le Déploiement

- [ ] Instance EC2 ou Cluster ECS créé
- [ ] Security Groups configurés
- [ ] Images Docker buildées et pushées (ECS)
- [ ] Base de données créée (DocumentDB/Atlas)
- [ ] Load Balancer configuré (ECS)
- [ ] Certificat SSL créé (ACM ou Let's Encrypt)
- [ ] DNS configuré dans Route 53
- [ ] Services démarrés et running

### Après le Déploiement

- [ ] Site accessible via HTTPS
- [ ] Connexion admin fonctionne
- [ ] API répond correctement
- [ ] Base de données accessible
- [ ] Logs visibles dans CloudWatch
- [ ] Monitoring configuré
- [ ] Sauvegardes configurées
- [ ] Alertes configurées

---

## 🎯 Recommandation Finale

Pour votre application JLC en production sur AWS, je recommande :

**🥇 Option Idéale** : **ECS Fargate + MongoDB Atlas**
- Coût : ~$150-200/mois
- Scalabilité automatique
- Maintenance minimale
- Production-ready

**🥈 Option Budget** : **EC2 t3.large + Docker Compose**
- Coût : ~$70-100/mois
- Simple à gérer
- Parfait pour démarrer

**🥉 Option Entreprise** : **EKS + Terraform**
- Coût : ~$250-400/mois
- Maximum de contrôle
- Pour croissance importante

---

Voulez-vous que je crée :
1. ✅ **Scripts d'automatisation** pour le déploiement ECS
2. ✅ **Terraform config** pour infrastructure as code
3. ✅ **CI/CD Pipeline** avec GitHub Actions
4. ✅ **Guide de migration** depuis Emergent vers AWS

Quelle option AWS préférez-vous utiliser ?
