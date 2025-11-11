# Guide de Déploiement Docker - Application JLC

## Vue d'Ensemble

Ce guide explique comment déployer l'application JLC en environnement Docker avec docker-compose.

## Architecture Docker

```
┌─────────────────────────────────────────────┐
│  Docker Network: jlc-network                │
│                                             │
│  ┌────────────┐  ┌────────────┐           │
│  │   Nginx    │  │  Frontend  │           │
│  │   (80)     │  │  (3001)    │           │
│  └─────┬──────┘  └────────────┘           │
│        │                                    │
│  ┌─────┴──────┐  ┌────────────┐           │
│  │  Backend   │  │   Auth     │           │
│  │  (8001)    │  │   (8000)   │           │
│  └─────┬──────┘  └─────┬──────┘           │
│        │                │                   │
│  ┌─────┴────────────────┴──────┐          │
│  │        MongoDB               │          │
│  │        (27017)               │          │
│  └──────────────────────────────┘          │
└─────────────────────────────────────────────┘
```

---

## Fichiers Docker Requis

### 1. docker-compose.yml

```yaml
version: '3.8'

services:
  # MongoDB
  mongodb:
    image: mongo:7.0
    container_name: jlc-mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USERNAME:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD:-admin123}
    volumes:
      - mongodb_data:/data/db
    networks:
      - jlc-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  # Auth Microservice
  auth-microservice:
    build:
      context: ./auth-microservice
      dockerfile: Dockerfile
    container_name: jlc-auth-service
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://${MONGO_ROOT_USERNAME:-admin}:${MONGO_ROOT_PASSWORD:-admin123}@mongodb:27017
      - DATABASE_NAME=auth_db
      - JWT_SECRET=${JWT_SECRET}
      - JWT_ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
    ports:
      - "8000:8000"
    depends_on:
      mongodb:
        condition: service_healthy
    networks:
      - jlc-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Backend (API Gateway)
  backend:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    container_name: jlc-backend
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://${MONGO_ROOT_USERNAME:-admin}:${MONGO_ROOT_PASSWORD:-admin123}@mongodb:27017
      - DATABASE_NAME=jlc_db
      - AUTH_SERVICE_URL=http://auth-microservice:8000
    ports:
      - "8001:8001"
    depends_on:
      auth-microservice:
        condition: service_healthy
    networks:
      - jlc-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Frontend (React + Vite)
  frontend:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
      args:
        - NODE_ENV=production
    container_name: jlc-frontend
    restart: unless-stopped
    ports:
      - "3001:3001"
    networks:
      - jlc-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: jlc-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # Pour les certificats SSL
    depends_on:
      - backend
      - frontend
    networks:
      - jlc-network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  jlc-network:
    driver: bridge

volumes:
  mongodb_data:
    driver: local
```

---

### 2. Dockerfile - Auth Microservice

`/auth-microservice/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3. Dockerfile - Backend

`/apps/api/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

### 4. Dockerfile - Frontend

`/apps/web/Dockerfile`:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build for production (optional, si vous voulez du statique)
# RUN yarn build

# Runtime stage - Dev server pour HMR
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile --production=false

# Copy source code
COPY . .

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001 || exit 1

# Run Vite dev server
CMD ["yarn", "vite", "--host", "0.0.0.0", "--port", "3001"]
```

**Alternative pour production avec build statique:**

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

# Runtime stage - Serve avec nginx
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx-frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 3001

CMD ["nginx", "-g", "daemon off;"]
```

---

### 5. Nginx Configuration

`/nginx/nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;

    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
}
```

`/nginx/conf.d/jlc-app.conf`:

```nginx
# Upstream definitions
upstream backend {
    server backend:8001 max_fails=3 fail_timeout=30s;
}

upstream frontend {
    server frontend:3001 max_fails=3 fail_timeout=30s;
}

# HTTP Server
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # API Routes - Forward to backend
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Important: Do NOT set X-Forwarded-Proto to https for internal calls
        proxy_set_header Connection "";
        
        # CORS (if needed)
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept" always;
        add_header Access-Control-Allow-Credentials true always;
        
        # Handle OPTIONS
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin $http_origin always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept" always;
            add_header Access-Control-Allow-Credentials true always;
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }

    # Auth API Routes
    location /auth-api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }

    # Frontend - SPA routing
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        
        # WebSocket support for Vite HMR
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long timeout for HMR
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}

# HTTPS Server (optionnel, avec SSL)
# server {
#     listen 443 ssl http2;
#     server_name yourdomain.com;
#
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#
#     # SSL configuration
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#
#     # Include same location blocks as HTTP
#     include /etc/nginx/conf.d/jlc-locations.conf;
# }
```

---

### 6. Fichier .env

`.env`:

```bash
# MongoDB
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=SecurePassword123!

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Application
NODE_ENV=production
```

---

## Déploiement

### 1. Préparation

```bash
# Cloner le projet
git clone <repository-url>
cd jlc-app

# Créer le fichier .env
cp .env.example .env
# Éditer .env avec vos valeurs

# Créer les dossiers nginx si nécessaire
mkdir -p nginx/conf.d nginx/ssl
```

### 2. Build et Démarrage

```bash
# Build les images
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Vérifier l'état
docker-compose ps
```

### 3. Initialisation de la Base de Données

```bash
# Exécuter les scripts d'initialisation
docker-compose exec auth-microservice python scripts/init_default_configs.py
docker-compose exec auth-microservice python scripts/assign_profiles_to_users.py
docker-compose exec auth-microservice python scripts/init_test_users_profiles.py
```

### 4. Tests

```bash
# Test health checks
curl http://localhost/health
curl http://localhost/api/health

# Test login
curl -X POST http://localhost/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Accéder au frontend
open http://localhost
```

---

## Commandes Utiles

### Gestion des Services

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer un service
docker-compose restart nginx
docker-compose restart backend

# Voir les logs
docker-compose logs -f nginx
docker-compose logs -f backend --tail=100

# Entrer dans un container
docker-compose exec backend bash
docker-compose exec mongodb mongosh
```

### Maintenance

```bash
# Nettoyer les volumes (ATTENTION: supprime les données)
docker-compose down -v

# Rebuild après changements
docker-compose build --no-cache
docker-compose up -d

# Vérifier l'utilisation des ressources
docker stats
```

---

## Monitoring

### Health Checks

Tous les services ont des health checks configurés:

```bash
# Vérifier la santé
docker-compose ps

# Résultat attendu: tous "healthy"
```

### Logs Centralisés

```bash
# Tous les logs
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f nginx backend auth-microservice
```

---

## Scaling (Optionnel)

Pour scaler horizontalement:

```yaml
# Dans docker-compose.yml
services:
  backend:
    # ...
    deploy:
      replicas: 3
```

Puis:
```bash
docker-compose up -d --scale backend=3
```

---

## Sécurité

### Production Checklist

- [ ] Changer MONGO_ROOT_PASSWORD
- [ ] Changer JWT_SECRET (minimum 32 caractères)
- [ ] Configurer SSL/TLS (certificats)
- [ ] Limiter l'exposition des ports
- [ ] Activer les firewalls
- [ ] Configurer les backups MongoDB
- [ ] Mettre en place le monitoring
- [ ] Configurer les rate limits dans nginx

---

## Dépannage

### Le service ne démarre pas

```bash
# Voir les logs
docker-compose logs <service-name>

# Vérifier la configuration
docker-compose config

# Redémarrer proprement
docker-compose down
docker-compose up -d
```

### Erreur de connexion MongoDB

```bash
# Vérifier que MongoDB est healthy
docker-compose ps mongodb

# Tester la connexion
docker-compose exec mongodb mongosh -u admin -p <password>
```

### Nginx ne route pas correctement

```bash
# Tester la configuration
docker-compose exec nginx nginx -t

# Recharger nginx
docker-compose exec nginx nginx -s reload
```

---

## Backup et Restore

### Backup MongoDB

```bash
# Backup
docker-compose exec mongodb mongodump --out=/backup

# Copier hors du container
docker cp jlc-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)
```

### Restore MongoDB

```bash
# Copier dans le container
docker cp ./mongodb-backup jlc-mongodb:/restore

# Restore
docker-compose exec mongodb mongorestore /restore
```

---

## Support

Pour plus d'informations:
- Architecture: `CHANGELOG_FIXES_COMPLETS.md`
- Webapp deployment: `DEPLOIEMENT_WEBAPP.md`
