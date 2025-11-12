# Guide Docker - Application JLC

## 📋 Table des matières
- [Introduction](#introduction)
- [Prérequis](#prérequis)
- [Démarrage Rapide](#démarrage-rapide)
- [Environnement de Développement](#environnement-de-développement)
- [Environnement de Production](#environnement-de-production)
- [Commandes Utiles](#commandes-utiles)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

Cette application utilise Docker et Docker Compose pour faciliter le développement et le déploiement. Tous les services nécessaires (MongoDB, Redis, API, Frontend) sont orchestrés via Docker.

### Architecture des Services

```
┌─────────────────────────────────────────────┐
│            Nginx (Reverse Proxy)            │
│              Port 80/443                    │
└────────────┬────────────────────────────────┘
             │
       ┌─────┴────┬──────────────┐
       │          │              │
┌──────▼───┐ ┌────▼─────┐ ┌──────▼──────┐
│ Frontend │ │ API      │ │ Auth        │
│ (React)  │ │ (FastAPI)│ │ (FastAPI)   │
│ :5173    │ │ :8001    │ │ :8000       │
└──────────┘ └────┬─────┘ └──────┬──────┘
                  │              │
            ┌─────┴──────────────┴─────┐
            │                          │
       ┌────▼────┐               ┌─────▼────┐
       │ MongoDB │               │  Redis   │
       │ :27017  │               │  :6379   │
       └─────────┘               └──────────┘
```

---

## 📦 Prérequis

### Versions requises
- **Docker**: 20.10 ou supérieur
- **Docker Compose**: 2.0 ou supérieur
- **Make** (optionnel mais recommandé)

### Vérifier les installations

```bash
docker --version
# Docker version 20.10.x ou supérieur

docker-compose --version
# Docker Compose version 2.x ou supérieur

make --version
# GNU Make (optionnel)
```

---

## 🚀 Démarrage Rapide

### Option 1: Avec Make (Recommandé)

```bash
# Démarrer l'environnement de développement
make dev

# Voir l'aide pour toutes les commandes
make help
```

### Option 2: Sans Make

```bash
# Démarrer l'environnement de développement
cd docker
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

### Accéder aux services

Une fois démarrés, les services sont disponibles à :

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | - |
| **API Backend** | http://localhost:8001 | - |
| **Auth Service** | http://localhost:8000 | - |
| **Mailhog (Email test)** | http://localhost:8025 | - |
| **Mongo Express** | http://localhost:8081 | admin / admin |
| **MongoDB** | mongodb://localhost:27017 | - |
| **Redis** | redis://localhost:6379 | - |

---

## 💻 Environnement de Développement

### Démarrage

```bash
# Avec Make
make dev

# Sans Make
cd docker && docker-compose up -d
```

### Voir les logs

```bash
# Tous les services
make dev-logs
# ou
docker-compose logs -f

# Service spécifique
make logs-frontend
make logs-api
make logs-auth
```

### Redémarrer un service

```bash
# Avec Make
make restart-frontend
make restart-api
make restart-auth

# Sans Make
docker-compose restart jlc-web
docker-compose restart jlc-api
docker-compose restart auth-microservice
```

### Reconstruire après changement de code

```bash
# Reconstruire tout
make dev-build

# Reconstruire un service spécifique
docker-compose up -d --build jlc-web
```

### Ouvrir un shell dans un container

```bash
# Frontend
make shell-frontend
# ou: docker-compose exec jlc-web sh

# API
make shell-api
# ou: docker-compose exec jlc-api bash

# Auth
make shell-auth
# ou: docker-compose exec auth-microservice bash

# MongoDB
make shell-mongo
# ou: docker-compose exec mongodb mongosh
```

### Arrêter l'environnement

```bash
# Arrêter
make dev-down
# ou
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
make dev-clean
# ou
docker-compose down -v
```

---

## 🏭 Environnement de Production

### Configuration initiale

1. **Créer le fichier .env**

```bash
cd docker
cp .env.example .env
```

2. **Éditer .env avec vos valeurs de production**

```bash
# Minimum requis
MONGO_ROOT_USERNAME=votre_username
MONGO_ROOT_PASSWORD=votre_password_fort
REDIS_PASSWORD=votre_redis_password
JWT_SECRET=votre_jwt_secret_minimum_32_caracteres
CORS_ORIGINS=https://votredomaine.com
API_BASE_URL=https://api.votredomaine.com
AUTH_SERVICE_URL=https://auth.votredomaine.com
```

3. **Configurer SSL (optionnel mais recommandé)**

```bash
mkdir -p nginx/ssl
# Placer vos certificats SSL
cp /path/to/fullchain.pem nginx/ssl/
cp /path/to/privkey.pem nginx/ssl/
```

### Déploiement

```bash
# Build les images
make ci-build

# Démarrer en production
make prod

# Vérifier le statut
make status-prod
```

### Monitoring

```bash
# Logs en temps réel
make prod-logs

# Statut des services
make status-prod

# Utilisation des ressources
docker stats
```

### Backup & Restore

```bash
# Créer un backup MongoDB
make backup-mongo

# Restaurer un backup (remplacer la date)
make restore-mongo BACKUP_DATE=20231201_143000
```

### Mise à jour de l'application

```bash
# 1. Pull les dernières modifications
git pull origin main

# 2. Rebuild les images
make prod-build

# 3. Les services redémarrent automatiquement
```

---

## 🛠 Commandes Utiles

### Make Commands

```bash
# Aide
make help

# Développement
make dev              # Démarrer dev
make dev-build        # Rebuild et démarrer
make dev-logs         # Voir les logs
make dev-down         # Arrêter
make dev-clean        # Nettoyer tout

# Production
make prod             # Démarrer prod
make prod-build       # Rebuild et démarrer
make prod-logs        # Voir les logs
make prod-down        # Arrêter
make prod-clean       # Nettoyer tout

# Services
make restart-frontend # Redémarrer frontend
make restart-api      # Redémarrer API
make restart-auth     # Redémarrer Auth

# Logs
make logs-frontend    # Logs frontend
make logs-api         # Logs API
make logs-auth        # Logs Auth
make logs-mongo       # Logs MongoDB

# Shell
make shell-frontend   # Shell frontend
make shell-api        # Shell API
make shell-auth       # Shell Auth
make shell-mongo      # Shell MongoDB

# Backup
make backup-mongo     # Backup MongoDB
make restore-mongo    # Restore MongoDB

# Maintenance
make status           # Statut services
make prune            # Nettoyer Docker
make prune-all        # Nettoyer tout Docker
```

### Docker Compose Commands

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Rebuild
docker-compose up -d --build

# Logs
docker-compose logs -f [service]

# Status
docker-compose ps

# Exec command
docker-compose exec [service] [command]

# Scale (si configuré)
docker-compose up -d --scale jlc-api=3
```

---

## 🔧 Troubleshooting

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier l'état
docker-compose ps

# Vérifier les ports utilisés
netstat -tulpn | grep -E '5173|8000|8001|27017'
```

### MongoDB ne démarre pas

```bash
# Vérifier les logs
docker-compose logs mongodb

# Supprimer le volume et redémarrer (⚠️ perte de données)
docker-compose down -v
docker-compose up -d
```

### Frontend ne se connecte pas au backend

```bash
# Vérifier les variables d'environnement
docker-compose exec jlc-web env | grep VITE

# Vérifier la connectivité réseau
docker-compose exec jlc-web ping jlc-api -c 3
```

### Redis connection error

```bash
# Tester Redis
docker-compose exec redis redis-cli ping

# En production (avec mot de passe)
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a $REDIS_PASSWORD ping
```

### Container crash loop

```bash
# Voir les logs détaillés
docker logs [container_id]

# Vérifier les ressources
docker stats

# Vérifier les health checks
docker inspect [container_id] | grep -A 10 Health
```

### Erreur "port already in use"

```bash
# Trouver le processus utilisant le port
lsof -i :5173
# ou
netstat -tulpn | grep 5173

# Arrêter le processus ou changer le port dans docker-compose.yml
```

### Clean install (⚠️ supprime toutes les données)

```bash
# Arrêter tout
docker-compose down -v

# Nettoyer Docker
docker system prune -a --volumes

# Redémarrer
docker-compose up -d --build
```

---

## 📚 Ressources Supplémentaires

- [Documentation Docker](https://docs.docker.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Documentation MongoDB](https://docs.mongodb.com/)
- [Documentation Redis](https://redis.io/documentation)
- [Documentation Nginx](https://nginx.org/en/docs/)

---

## 🆘 Support

En cas de problème:

1. Vérifier ce guide
2. Consulter les logs: `make dev-logs` ou `docker-compose logs`
3. Vérifier la documentation dans `/docs`
4. Contacter l'équipe technique

---

## 🔒 Sécurité

### Bonnes pratiques

✅ **À FAIRE:**
- Utiliser des mots de passe forts (32+ caractères)
- Activer HTTPS en production
- Limiter les ports exposés
- Backups réguliers
- Mettre à jour les images régulièrement
- Utiliser `.env` pour les secrets
- Ne jamais commit `.env`

❌ **À NE PAS FAIRE:**
- Exposer MongoDB en production sans auth
- Utiliser des mots de passe par défaut
- Commit les secrets dans Git
- Désactiver les health checks
- Ignorer les mises à jour de sécurité

---

**Version:** 1.0.0  
**Dernière mise à jour:** $(date +%Y-%m-%d)
