# Guide de Déploiement Docker - Application JLC

## 📋 Prérequis

### Système
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB espace disque

### Domaines et SSL
- Nom de domaine configuré
- Certificats SSL (Let's Encrypt recommandé)
- Accès DNS pour configuration

## 🚀 Déploiement Rapide

### 1. Préparation

```bash
# Cloner le projet
git clone <your-repo>
cd jlc-app/docker

# Copier et configurer les variables d'environnement
cp .env.prod.example .env.prod
nano .env.prod
```

### 2. Configuration des Variables

Éditez `.env.prod` avec vos valeurs :

```bash
# Base de données
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=VotreMotDePasseSecurise123!

# JWT
JWT_SECRET=votre-cle-jwt-super-secrete-minimum-32-caracteres

# Domaines
CORS_ORIGINS=https://votredomaine.com,https://api.votredomaine.com
API_BASE_URL=https://api.votredomaine.com
AUTH_SERVICE_URL=https://auth.votredomaine.com

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# Google OAuth
GOOGLE_CLIENT_ID=votre-client-id
GOOGLE_CLIENT_SECRET=votre-client-secret
```

### 3. Configuration SSL

```bash
# Créer le dossier SSL
mkdir -p nginx/ssl

# Copier vos certificats
cp /path/to/your/cert.pem nginx/ssl/
cp /path/to/your/key.pem nginx/ssl/
```

### 4. Déploiement

```bash
# Rendre le script exécutable
chmod +x scripts/deploy.sh

# Lancer le déploiement
./scripts/deploy.sh
```

## 🔧 Configuration Détaillée

### Structure des Services

```
jlc-app/
├── docker/
│   ├── docker-compose.prod.yml    # Configuration production
│   ├── .env.prod                  # Variables d'environnement
│   ├── nginx/
│   │   ├── nginx.conf            # Configuration Nginx
│   │   └── ssl/                  # Certificats SSL
│   ├── mongo-init/
│   │   └── init-mongo.js         # Initialisation MongoDB
│   └── scripts/
│       ├── deploy.sh             # Script de déploiement
│       ├── backup.sh             # Script de sauvegarde
│       └── restore.sh            # Script de restauration
├── apps/
│   ├── api/
│   │   └── Dockerfile.prod       # Dockerfile API production
│   └── web/
│       ├── Dockerfile.prod       # Dockerfile Frontend production
│       └── nginx.conf            # Config Nginx frontend
└── auth-microservice/
    └── Dockerfile.prod           # Dockerfile Auth production
```

### Services Déployés

| Service | Port | Description |
|---------|------|-------------|
| nginx | 80, 443 | Reverse proxy et SSL |
| jlc-web | 80 | Frontend React |
| jlc-api | 8001 | API FastAPI |
| auth-microservice | 8000 | Service d'authentification |
| mongodb | 27017 | Base de données |

## 🛡️ Sécurité

### Bonnes Pratiques Implémentées

1. **Utilisateurs non-root** dans les conteneurs
2. **Authentification MongoDB** activée
3. **SSL/TLS** pour toutes les communications
4. **Variables d'environnement** sécurisées
5. **Health checks** pour tous les services
6. **Logs centralisés**

### Configuration SSL avec Let's Encrypt

```bash
# Installation Certbot
sudo apt install certbot

# Génération des certificats
sudo certbot certonly --standalone -d votredomaine.com -d api.votredomaine.com -d auth.votredomaine.com

# Copie des certificats
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem nginx/ssl/key.pem
```

## 📊 Monitoring et Logs

### Consultation des Logs

```bash
# Logs de tous les services
docker-compose -f docker-compose.prod.yml logs -f

# Logs d'un service spécifique
docker-compose -f docker-compose.prod.yml logs -f jlc-api

# Logs des 100 dernières lignes
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Monitoring des Services

```bash
# État des conteneurs
docker-compose -f docker-compose.prod.yml ps

# Utilisation des ressources
docker stats

# Health checks
docker-compose -f docker-compose.prod.yml exec jlc-api curl http://localhost:8001/health
```

## 💾 Sauvegarde et Restauration

### Sauvegarde Automatique

```bash
# Sauvegarde manuelle
./scripts/backup.sh

# Programmation avec cron (quotidienne à 2h)
echo "0 2 * * * /path/to/jlc-app/docker/scripts/backup.sh" | crontab -
```

### Restauration

```bash
# Lister les sauvegardes
ls -la backups/

# Restaurer une sauvegarde
./scripts/restore.sh backups/jlc_backup_20240101_020000.tar.gz
```

## 🔄 Mise à Jour

### Déploiement d'une Nouvelle Version

```bash
# 1. Sauvegarde préventive
./scripts/backup.sh

# 2. Récupération du nouveau code
git pull origin main

# 3. Redéploiement
./scripts/deploy.sh
```

### Rollback en Cas de Problème

```bash
# Arrêt des services
docker-compose -f docker-compose.prod.yml down

# Retour à la version précédente
git checkout <previous-commit>

# Redéploiement
./scripts/deploy.sh

# Restauration de la base si nécessaire
./scripts/restore.sh backups/jlc_backup_<timestamp>.tar.gz
```

## 🐛 Dépannage

### Problèmes Courants

#### Service ne démarre pas
```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs <service-name>

# Vérifier la configuration
docker-compose -f docker-compose.prod.yml config
```

#### Problème de connexion MongoDB
```bash
# Vérifier l'état de MongoDB
docker exec jlc-mongodb-prod mongo --eval "db.adminCommand('ismaster')"

# Vérifier les utilisateurs
docker exec jlc-mongodb-prod mongo admin --eval "db.getUsers()"
```

#### Problème SSL
```bash
# Vérifier les certificats
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Tester la configuration SSL
openssl s_client -connect votredomaine.com:443
```

### Commandes Utiles

```bash
# Redémarrer un service
docker-compose -f docker-compose.prod.yml restart <service-name>

# Reconstruire un service
docker-compose -f docker-compose.prod.yml up -d --build <service-name>

# Accéder à un conteneur
docker exec -it <container-name> /bin/bash

# Nettoyer le système
docker system prune -a
```

## 📈 Optimisation Performance

### Configuration Recommandée

1. **Serveur de Production**
   - 4 CPU cores minimum
   - 8GB RAM minimum
   - SSD pour la base de données

2. **Optimisations Docker**
   - Limites de ressources par conteneur
   - Multi-stage builds pour réduire la taille
   - Cache des layers Docker

3. **Optimisations Base de Données**
   - Index appropriés
   - Connection pooling
   - Monitoring des requêtes lentes

## 🆘 Support

En cas de problème :

1. Consultez les logs détaillés
2. Vérifiez la configuration des variables d'environnement
3. Testez les health checks de chaque service
4. Consultez la documentation Docker Compose

---

**Note** : Ce guide suppose une installation sur un serveur Linux. Adaptez les commandes selon votre environnement.
