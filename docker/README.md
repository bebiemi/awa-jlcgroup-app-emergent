# 🐳 Déploiement Docker - Application JLC

## 📋 Vue d'ensemble

Ce dossier contient tous les fichiers nécessaires pour déployer l'application JLC en production avec Docker. L'architecture comprend :

- **Frontend React** (Vite + TypeScript)
- **API FastAPI** (Python)
- **Microservice d'authentification** (FastAPI)
- **Base de données MongoDB**
- **Reverse Proxy Nginx** avec SSL

## 🚀 Démarrage Rapide

### 1. Préparation
```bash
cd docker
cp .env.prod.example .env.prod
nano .env.prod  # Configurer vos variables
```

### 2. Vérification pré-déploiement
```bash
./scripts/pre-deploy-check.sh
```

### 3. Déploiement
```bash
./scripts/deploy.sh
```

### 4. Monitoring
```bash
./scripts/monitor.sh
```

## 📁 Structure des Fichiers

```
docker/
├── 📄 docker-compose.yml          # Configuration développement
├── 📄 docker-compose.prod.yml     # Configuration production
├── 📄 .env.prod.example           # Template variables d'environnement
├── 📄 .env.prod                   # Variables de production (à créer)
├── 📂 nginx/
│   ├── nginx.conf                 # Configuration Nginx reverse proxy
│   └── ssl/                       # Certificats SSL (à ajouter)
├── 📂 mongo-init/
│   └── init-mongo.js              # Script d'initialisation MongoDB
├── 📂 scripts/
│   ├── 🔧 deploy.sh               # Script de déploiement
│   ├── 🔍 pre-deploy-check.sh     # Vérifications pré-déploiement
│   ├── 📊 monitor.sh              # Monitoring en temps réel
│   ├── 💾 backup.sh               # Sauvegarde automatique
│   ├── 🔄 restore.sh              # Restauration de sauvegarde
│   └── ⬆️ update.sh               # Mise à jour automatisée
└── 📚 Documentation/
    ├── DEPLOYMENT_GUIDE.md        # Guide complet de déploiement
    ├── DOCKER_COMMANDS.md         # Commandes Docker utiles
    └── README.md                  # Ce fichier
```

## ⚙️ Configuration

### Variables d'Environnement Critiques

```bash
# Sécurité
MONGO_ROOT_PASSWORD=VotreMotDePasseSecurise123!
JWT_SECRET=votre-cle-jwt-super-secrete-minimum-32-caracteres

# Domaines
API_BASE_URL=https://api.votredomaine.com
AUTH_SERVICE_URL=https://auth.votredomaine.com
CORS_ORIGINS=https://votredomaine.com,https://api.votredomaine.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# OAuth Google
GOOGLE_CLIENT_ID=votre-client-id
GOOGLE_CLIENT_SECRET=votre-client-secret
```

### Certificats SSL

```bash
# Créer le dossier SSL
mkdir -p nginx/ssl

# Avec Let's Encrypt
certbot certonly --standalone -d votredomaine.com
cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/votredomaine.com/privkey.pem nginx/ssl/key.pem

# Ou copier vos certificats existants
cp /path/to/your/cert.pem nginx/ssl/
cp /path/to/your/key.pem nginx/ssl/
```

## 🛠️ Scripts Disponibles

### 🔧 deploy.sh
Déploiement complet de l'application
```bash
./scripts/deploy.sh
```

### 🔍 pre-deploy-check.sh
Vérifications avant déploiement
```bash
./scripts/pre-deploy-check.sh
```
- Vérifie les prérequis système
- Valide la configuration
- Teste les ressources disponibles
- Contrôle les certificats SSL

### 📊 monitor.sh
Monitoring en temps réel
```bash
./scripts/monitor.sh                # Vérification unique
./scripts/monitor.sh --continuous   # Monitoring continu
```
- État des conteneurs
- Health checks des services
- Utilisation des ressources
- Analyse des logs d'erreur
- Score de santé global

### 💾 backup.sh
Sauvegarde automatique
```bash
./scripts/backup.sh
```
- Sauvegarde MongoDB complète
- Compression automatique
- Nettoyage des anciennes sauvegardes
- Programmable avec cron

### 🔄 restore.sh
Restauration de sauvegarde
```bash
./scripts/restore.sh backups/jlc_backup_20240101_020000.tar.gz
```

### ⬆️ update.sh
Mise à jour automatisée
```bash
./scripts/update.sh
```
- Sauvegarde préventive
- Mise à jour du code
- Reconstruction des images si nécessaire
- Tests post-déploiement
- Rollback automatique en cas d'erreur

## 🏗️ Architecture des Services

### Services de Production

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| **nginx** | 80, 443 | Reverse proxy, SSL, Load balancer | HTTP 200 |
| **jlc-web** | 80 | Frontend React (build de production) | HTTP 200 |
| **jlc-api** | 8001 | API FastAPI principale | `/health` |
| **auth-microservice** | 8000 | Service d'authentification | `/health` |
| **mongodb** | 27017 | Base de données principale | `ismaster` |

### Réseau Docker
- **Réseau interne** : `jlc-network`
- **Communication inter-services** par nom de service
- **Isolation** des services de la base de données

### Volumes Persistants
- **mongodb_data** : Données MongoDB
- **uploads** : Fichiers uploadés par les utilisateurs
- **logs** : Logs centralisés de tous les services

## 🔒 Sécurité

### Mesures Implémentées
- ✅ **Utilisateurs non-root** dans tous les conteneurs
- ✅ **Authentification MongoDB** avec utilisateurs dédiés
- ✅ **SSL/TLS** pour toutes les communications externes
- ✅ **Variables d'environnement** sécurisées
- ✅ **Health checks** pour tous les services
- ✅ **Isolation réseau** entre services
- ✅ **Logs centralisés** pour audit

### Recommandations
- 🔐 Changer tous les mots de passe par défaut
- 🔑 Utiliser des clés JWT de 32+ caractères
- 📜 Renouveler les certificats SSL régulièrement
- 🔍 Monitorer les logs d'erreur
- 💾 Programmer des sauvegardes automatiques

## 📊 Monitoring et Maintenance

### Surveillance Quotidienne
```bash
# Status rapide
docker-compose -f docker-compose.prod.yml ps

# Monitoring complet
./scripts/monitor.sh

# Logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f
```

### Maintenance Hebdomadaire
```bash
# Sauvegarde
./scripts/backup.sh

# Nettoyage système
docker system prune -f

# Vérification des certificats SSL
openssl x509 -in nginx/ssl/cert.pem -noout -dates
```

### Maintenance Mensuelle
```bash
# Mise à jour de sécurité
./scripts/update.sh

# Analyse des performances
docker stats --no-stream

# Rotation des logs
docker-compose -f docker-compose.prod.yml logs --since 30d > monthly_logs.txt
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

#### Problème de connectivité
```bash
# Tester la résolution DNS
docker-compose exec jlc-api nslookup mongodb

# Tester la connectivité réseau
docker-compose exec jlc-api ping mongodb
```

#### Base de données inaccessible
```bash
# Vérifier l'état de MongoDB
docker exec jlc-mongodb-prod mongo --eval "db.adminCommand('ismaster')"

# Vérifier les utilisateurs
docker exec jlc-mongodb-prod mongo admin --eval "db.getUsers()"
```

### Commandes de Diagnostic
```bash
# État détaillé des conteneurs
docker inspect <container-name>

# Utilisation des ressources
docker stats

# Espace disque
df -h
docker system df

# Réseau
docker network inspect docker_jlc-network
```

## 🔄 Procédures d'Urgence

### Rollback Rapide
```bash
# 1. Arrêter les services
docker-compose -f docker-compose.prod.yml down

# 2. Revenir à la version précédente
git checkout <previous-commit>

# 3. Redéployer
./scripts/deploy.sh

# 4. Restaurer la base si nécessaire
./scripts/restore.sh backups/latest_backup.tar.gz
```

### Récupération de Données
```bash
# Extraction manuelle des données
docker cp jlc-mongodb-prod:/data/db ./emergency_backup/

# Sauvegarde d'urgence
docker exec jlc-mongodb-prod mongodump --out /tmp/emergency
docker cp jlc-mongodb-prod:/tmp/emergency ./emergency_backup/
```

## 📞 Support

### Logs Importants
- **Application** : `docker-compose logs -f`
- **Système** : `/var/log/syslog`
- **Nginx** : Volume `logs:/var/log/nginx`
- **Monitoring** : `monitoring.log`

### Informations pour le Support
Avant de contacter le support, préparez :
1. Sortie de `./scripts/monitor.sh`
2. Logs des services en erreur
3. Configuration (sans les secrets)
4. Étapes pour reproduire le problème

---

## 📚 Documentation Complète

- 📖 **[Guide de Déploiement Complet](DEPLOYMENT_GUIDE.md)**
- 🐳 **[Commandes Docker Essentielles](DOCKER_COMMANDS.md)**
- 🔧 **Configuration des services individuels dans les dossiers respectifs**

---

**🎯 Objectif** : Déploiement sécurisé, monitored et maintenable de l'application JLC en production.