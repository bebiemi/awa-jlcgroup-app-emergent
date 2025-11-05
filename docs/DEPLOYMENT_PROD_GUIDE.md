# 🚀 Guide de Déploiement - Environnement PRODUCTION

## ⚠️ ATTENTION : Production

Ce guide concerne l'environnement **production**. Toute erreur peut impacter les utilisateurs finaux.

**Règles d'or :**
- ✅ Tester sur dev d'abord
- ✅ Backup complet avant déploiement
- ✅ Plan de rollback préparé
- ✅ Fenêtre de maintenance annoncée
- ✅ Équipe en standby

---

## 📋 Prérequis

### Infrastructure
- ✅ Serveur prod configuré (EC2, ECS, ou équivalent)
- ✅ MongoDB production (Atlas ou auto-hébergé)
- ✅ AWS Account avec accès Secrets Manager
- ✅ Load Balancer / Reverse Proxy configuré
- ✅ SSL/TLS certificats valides
- ✅ Monitoring configuré (CloudWatch, Datadog, etc.)

### Accès
- ✅ Permissions AWS Secrets Manager
- ✅ SSH/accès au serveur prod
- ✅ Permissions deploy (GitHub Actions, CI/CD)

### Sécurité
- ✅ Secrets Manager configuré
- ✅ IAM Roles configurés
- ✅ Network Security Groups
- ✅ Backup automatique configuré

---

## 🔐 Étape 1 : Configuration AWS Secrets Manager

### Créer le secret

```bash
# 1. Préparer le fichier de secrets (sur machine sécurisée)
cat > prod-secrets.json << 'EOF'
{
  "MONGO_URL": "mongodb+srv://prod-user:STRONG_PASSWORD@prod-cluster.mongodb.net/auth_db_prod?retryWrites=true&w=majority",
  "DATABASE_NAME": "auth_db_prod",
  "JWT_SECRET_KEY": "PRODUCTION-JWT-SECRET-MIN-64-CHARS-VERY-STRONG-AND-RANDOM",
  "GOOGLE_CLIENT_ID": "123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com",
  "GOOGLE_CLIENT_SECRET": "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",
  "GOOGLE_REDIRECT_URI": "https://jlc-platform.com/auth/google/callback",
  "SENDGRID_API_KEY": "SG.ProductionSendGridAPIKey",
  "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "TWILIO_AUTH_TOKEN": "your-production-twilio-auth-token",
  "AWS_ACCESS_KEY_ID": "AKIAXXXXXXXXXXXXXXXX",
  "AWS_SECRET_ACCESS_KEY": "your-production-aws-secret-access-key"
}
EOF

# 2. Créer le secret dans AWS
aws secretsmanager create-secret \
  --name jlc-auth-prod \
  --description "JLC Auth Production Secrets" \
  --secret-string file://prod-secrets.json \
  --region eu-west-1

# 3. Supprimer le fichier local (sécurité)
shred -vfz -n 10 prod-secrets.json

# 4. Vérifier
aws secretsmanager describe-secret \
  --secret-id jlc-auth-prod \
  --region eu-west-1
```

### Configurer IAM Role

```bash
# 1. Créer la policy IAM
cat > jlc-auth-secrets-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:jlc-auth-prod-*"
    }
  ]
}
EOF

# 2. Créer la policy
aws iam create-policy \
  --policy-name JLCAuthSecretsReadPolicy \
  --policy-document file://jlc-auth-secrets-policy.json

# 3. Attacher au rôle EC2/ECS
aws iam attach-role-policy \
  --role-name JLCAuthServiceRole \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/JLCAuthSecretsReadPolicy
```

### Test de récupération

```bash
# Test depuis une machine avec les bonnes permissions
aws secretsmanager get-secret-value \
  --secret-id jlc-auth-prod \
  --region eu-west-1 \
  --query SecretString \
  --output text | jq .
```

---

## 🏗️ Étape 2 : Configuration du Serveur Production

### Variables d'environnement système

```bash
# Sur le serveur prod
sudo tee -a /etc/environment << 'EOF'
APP_ENV=prod
AWS_REGION=eu-west-1
AWS_SECRET_NAME=jlc-auth-prod
EOF

# Recharger
source /etc/environment
```

### Configuration Nginx (Reverse Proxy)

```nginx
# /etc/nginx/sites-available/jlc-prod
upstream jlc_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

upstream jlc_frontend {
    server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name jlc-platform.com www.jlc-platform.com;
    return 301 https://$host$request_uri;
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.jlc-platform.com;

    ssl_certificate /etc/letsencrypt/live/api.jlc-platform.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.jlc-platform.com/privkey.pem;
    
    # SSL Configuration (Mozilla Modern)
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://jlc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (pas de rate limit)
    location /health {
        proxy_pass http://jlc_backend/health;
        access_log off;
    }
}

# Frontend
server {
    listen 443 ssl http2;
    server_name jlc-platform.com www.jlc-platform.com;

    ssl_certificate /etc/letsencrypt/live/jlc-platform.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jlc-platform.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://jlc_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://jlc_frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/jlc-prod /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🚀 Étape 3 : Déploiement Docker (Recommandé)

### Dockerfile Production

```dockerfile
# /app/auth-microservice/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

### Docker Compose Production

```yaml
# /app/docker-compose.prod.yml
version: '3.8'

services:
  auth-microservice:
    build:
      context: ./auth-microservice
      dockerfile: Dockerfile
    environment:
      - APP_ENV=prod
      - AWS_REGION=eu-west-1
      - AWS_SECRET_NAME=jlc-auth-prod
    ports:
      - "8000:8000"
    volumes:
      - ./auth-microservice/config:/app/config:ro
      - upload-data:/app/uploads
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
      - VITE_API_BASE_URL=https://api.jlc-platform.com
    ports:
      - "3000:3000"
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  upload-data:
    driver: local
```

### Déploiement

```bash
# 1. Se connecter au serveur
ssh user@prod-server.jlc-platform.com

# 2. Clone/Update du code
cd /app
git pull origin main

# 3. Build et démarrage
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f auth-microservice

# Devrait afficher :
# 🚀 Starting AWANA Auth Microservice (env: prod)...
# 🔐 Secrets chargés depuis AWS Secrets Manager: jlc-auth-prod
# ✅ Connected to MongoDB: auth_db_prod
# ✅ Configuration chargée avec succès
```

---

## ✅ Étape 4 : Validation Post-Déploiement

### Tests de santé automatisés

```bash
#!/bin/bash
# /app/scripts/health-check-prod.sh

echo "🔍 Health Check Production"
echo "=========================="

# 1. Backend health
echo "1. Backend API..."
response=$(curl -s -o /dev/null -w "%{http_code}" https://api.jlc-platform.com/health)
if [ "$response" == "200" ]; then
    echo "✅ Backend OK"
else
    echo "❌ Backend FAILED (HTTP $response)"
    exit 1
fi

# 2. Frontend
echo "2. Frontend..."
response=$(curl -s -o /dev/null -w "%{http_code}" https://jlc-platform.com)
if [ "$response" == "200" ]; then
    echo "✅ Frontend OK"
else
    echo "❌ Frontend FAILED (HTTP $response)"
    exit 1
fi

# 3. OAuth configured
echo "3. OAuth Configuration..."
oauth_status=$(curl -s https://api.jlc-platform.com/api/auth/google/status | jq -r .configured)
if [ "$oauth_status" == "true" ]; then
    echo "✅ OAuth configured"
else
    echo "❌ OAuth NOT configured"
    exit 1
fi

# 4. Database connection
echo "4. Database..."
env_check=$(curl -s https://api.jlc-platform.com/health | jq -r .environment)
if [ "$env_check" == "prod" ]; then
    echo "✅ Database connected (env: prod)"
else
    echo "❌ Wrong environment: $env_check"
    exit 1
fi

echo ""
echo "✅ ALL CHECKS PASSED"
```

```bash
chmod +x /app/scripts/health-check-prod.sh
/app/scripts/health-check-prod.sh
```

### Tests de charge (optionnel)

```bash
# Utiliser Apache Bench
ab -n 1000 -c 10 https://api.jlc-platform.com/health

# Ou vegeta
echo "GET https://api.jlc-platform.com/health" | \
  vegeta attack -duration=30s -rate=50 | \
  vegeta report
```

---

## 📊 Étape 5 : Monitoring Production

### CloudWatch Logs (AWS)

```bash
# Configurer CloudWatch agent
sudo yum install amazon-cloudwatch-agent

# Configuration
cat > /opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-config.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/jlc/auth-service.log",
            "log_group_name": "/aws/jlc/auth-service",
            "log_stream_name": "{instance_id}",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
EOF

# Démarrer l'agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/cloudwatch-config.json
```

### Alarmes CloudWatch

```bash
# Créer une alarme pour les erreurs
aws cloudwatch put-metric-alarm \
  --alarm-name jlc-auth-high-error-rate \
  --alarm-description "Alert when error rate is high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:eu-west-1:ACCOUNT_ID:jlc-alerts
```

### Métriques Prometheus (Alternative)

```yaml
# /app/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'jlc-auth-prod'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
```

---

## 🔄 Mises à Jour Production

### Procédure de déploiement

```bash
#!/bin/bash
# /app/scripts/deploy-prod.sh

set -e

echo "🚀 Déploiement Production JLC"
echo "=============================="

# 1. Backup
echo "1. Backup de la base de données..."
mongodump --uri="${MONGO_URL}" --out=/backups/$(date +%Y%m%d_%H%M%S)

# 2. Pull du code
echo "2. Pull du nouveau code..."
cd /app
git fetch origin
git checkout main
git pull origin main

# 3. Build
echo "3. Build des images Docker..."
docker-compose -f docker-compose.prod.yml build

# 4. Test de santé pre-deploy
echo "4. Test de santé actuel..."
/app/scripts/health-check-prod.sh || {
    echo "❌ Health check pre-deploy failed"
    exit 1
}

# 5. Déploiement rolling
echo "5. Déploiement..."
docker-compose -f docker-compose.prod.yml up -d --no-deps --build auth-microservice

# 6. Attendre le démarrage
echo "6. Attente du démarrage (30s)..."
sleep 30

# 7. Test de santé post-deploy
echo "7. Test de santé post-deploy..."
/app/scripts/health-check-prod.sh || {
    echo "❌ Health check post-deploy failed"
    echo "🔄 Rollback..."
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    exit 1
}

# 8. Frontend
echo "8. Déploiement frontend..."
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend

echo ""
echo "✅ Déploiement réussi"
echo "📊 Monitoring: Surveiller les logs pendant 10 minutes"
```

### Rollback

```bash
#!/bin/bash
# /app/scripts/rollback-prod.sh

echo "🔄 Rollback Production"

# 1. Trouver le dernier commit déployé
LAST_COMMIT=$(git rev-parse HEAD~1)

# 2. Checkout
git checkout $LAST_COMMIT

# 3. Rebuild et redéployer
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Vérifier
sleep 30
/app/scripts/health-check-prod.sh

echo "✅ Rollback terminé"
```

---

## 🔐 Mise à Jour des Secrets

### Modifier un secret

```bash
# 1. Récupérer le secret actuel
aws secretsmanager get-secret-value \
  --secret-id jlc-auth-prod \
  --region eu-west-1 \
  --query SecretString \
  --output text > current-secrets.json

# 2. Éditer (avec un éditeur sécurisé)
vim current-secrets.json

# 3. Mettre à jour
aws secretsmanager update-secret \
  --secret-id jlc-auth-prod \
  --secret-string file://current-secrets.json \
  --region eu-west-1

# 4. Supprimer le fichier local
shred -vfz -n 10 current-secrets.json

# 5. Redémarrer l'application
docker-compose -f docker-compose.prod.yml restart auth-microservice
```

### Rotation des secrets

```bash
# Activer la rotation automatique (30 jours)
aws secretsmanager rotate-secret \
  --secret-id jlc-auth-prod \
  --rotation-lambda-arn arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:jlc-secret-rotation \
  --rotation-rules AutomaticallyAfterDays=30
```

---

## 📋 Checklist Déploiement Production

### Avant le déploiement
- [ ] Tests passent sur dev
- [ ] Code review approuvé
- [ ] Secrets Manager configuré
- [ ] IAM Roles vérifiés
- [ ] Backup BD complet
- [ ] Fenêtre de maintenance annoncée
- [ ] Équipe disponible

### Pendant le déploiement
- [ ] Code déployé
- [ ] Services redémarrés
- [ ] Health checks passent
- [ ] Logs vérifiés
- [ ] Métriques normales

### Après le déploiement
- [ ] Tests fonctionnels OK
- [ ] Performance normale
- [ ] Monitoring actif
- [ ] Alertes configurées
- [ ] Documentation mise à jour
- [ ] Équipe informée

---

## 🆘 Plan d'Urgence

### Incident de production

1. **Détection**
   - Alertes CloudWatch
   - Monitoring externe (UptimeRobot, Pingdom)
   - Rapports utilisateurs

2. **Réponse immédiate**
   ```bash
   # Vérifier les logs
   docker-compose -f docker-compose.prod.yml logs --tail=100 auth-microservice
   
   # Vérifier les métriques
   curl https://api.jlc-platform.com/health
   ```

3. **Rollback si critique**
   ```bash
   /app/scripts/rollback-prod.sh
   ```

4. **Communication**
   - Informer les utilisateurs (status page)
   - Informer l'équipe
   - Post-mortem après résolution

---

**Environnement PRODUCTION - Sécurisé et Monitored** ✅
