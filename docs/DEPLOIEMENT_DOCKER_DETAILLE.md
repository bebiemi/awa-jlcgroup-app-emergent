# 🚀 Procédure Détaillée de Déploiement Docker - Application JLC

## Table des Matières
1. [Prérequis](#prérequis)
2. [Préparation du Serveur](#préparation-du-serveur)
3. [Configuration des Fichiers](#configuration-des-fichiers)
4. [Déploiement](#déploiement)
5. [Vérification](#vérification)
6. [Maintenance](#maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 📋 Prérequis

### Serveur
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: Minimum 4GB (Recommandé 8GB)
- **CPU**: 2 cores minimum (Recommandé 4 cores)
- **Stockage**: 20GB minimum (Recommandé 50GB)
- **Accès**: SSH avec privilèges sudo

### Logiciels Requis
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Nginx (optionnel si vous utilisez le container nginx fourni)

### Domaine et SSL
- Nom de domaine configuré (ex: `votredomaine.com`)
- Sous-domaines (optionnels):
  - `api.votredomaine.com` (API)
  - `auth.votredomaine.com` (Auth)
- Certificats SSL (Let's Encrypt, Cloudflare, etc.)

### Clés et Identifiants
- [ ] MongoDB root username et password
- [ ] JWT Secret (32+ caractères)
- [ ] Google OAuth Client ID et Secret (si OAuth activé)
- [ ] SMTP credentials (pour les emails)

---

## 🖥️ Préparation du Serveur

### Étape 1: Connexion au Serveur

```bash
# Connexion SSH à votre serveur
ssh user@votre-serveur-ip

# Mise à jour du système
sudo apt update && sudo apt upgrade -y
```

### Étape 2: Installation de Docker

#### Sur Ubuntu/Debian:

```bash
# Suppression des anciennes versions
sudo apt remove docker docker-engine docker.io containerd runc

# Installation des dépendances
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajout de la clé GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajout du repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installation Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Vérification
docker --version
docker compose version
```

#### Sur CentOS/RHEL:

```bash
# Installation des dépendances
sudo yum install -y yum-utils

# Ajout du repository Docker
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Installation
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Démarrage de Docker
sudo systemctl start docker
sudo systemctl enable docker

# Vérification
docker --version
docker compose version
```

### Étape 3: Configuration Docker (Optionnel mais recommandé)

```bash
# Ajouter votre utilisateur au groupe docker (évite d'utiliser sudo)
sudo usermod -aG docker $USER

# Appliquer le changement (ou déconnectez-vous et reconnectez-vous)
newgrp docker

# Vérifier que vous pouvez lancer docker sans sudo
docker ps
```

### Étape 4: Installation de Git

```bash
# Ubuntu/Debian
sudo apt install -y git

# CentOS/RHEL
sudo yum install -y git

# Vérification
git --version
```

---

## 📁 Configuration des Fichiers

### Étape 1: Récupération du Code

```bash
# Créer un répertoire pour l'application
mkdir -p /opt/jlc-app
cd /opt/jlc-app

# Cloner le repository (remplacez par votre URL)
git clone https://github.com/votre-compte/jlc-app.git .

# Ou copier les fichiers depuis votre machine locale
# scp -r /local/path/to/jlc-app user@server:/opt/jlc-app
```

### Étape 2: Création du Fichier .env.prod

```bash
cd /opt/jlc-app/docker

# Créer le fichier .env.prod
nano .env.prod
```

**Contenu du fichier `.env.prod`:**

```bash
# ============================================
# CONFIGURATION PRODUCTION - JLC APPLICATION
# ============================================

# ===== BASE DE DONNÉES =====
MONGO_ROOT_USERNAME=admin_jlc
MONGO_ROOT_PASSWORD=VotreMotDePasseMongoDBTreSecurise123!@#

# ===== AUTHENTIFICATION =====
JWT_SECRET=votre-cle-jwt-super-secrete-minimum-32-caracteres-aleatoires-123456789
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# ===== DOMAINES ET CORS =====
# Remplacez par vos vrais domaines
CORS_ORIGINS=https://votredomaine.com,https://www.votredomaine.com,https://api.votredomaine.com
API_BASE_URL=https://api.votredomaine.com
AUTH_SERVICE_URL=https://auth.votredomaine.com

# ===== SMTP / EMAIL =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app-gmail
SMTP_FROM_EMAIL=noreply@votredomaine.com
SMTP_FROM_NAME=JLC Group

# ===== GOOGLE OAUTH (Si activé) =====
GOOGLE_CLIENT_ID=votre-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=votre-google-client-secret
GOOGLE_REDIRECT_URI=https://votredomaine.com/auth/google/callback

# ===== ENVIRONNEMENT =====
ENVIRONMENT=production
DEBUG=false

# ===== AUTRES =====
UPLOAD_MAX_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,doc,docx,jpg,jpeg,png
```

**💡 Important**: 
- Utilisez des mots de passe forts et uniques
- Ne commitez JAMAIS ce fichier dans Git
- Gardez une copie sécurisée de ce fichier

### Étape 3: Configuration SSL

#### Option A: Utiliser Let's Encrypt (Recommandé)

```bash
# Installation de Certbot
sudo apt install -y certbot

# Génération des certificats
sudo certbot certonly --standalone -d votredomaine.com -d www.votredomaine.com

# Les certificats seront dans:
# /etc/letsencrypt/live/votredomaine.com/fullchain.pem
# /etc/letsencrypt/live/votredomaine.com/privkey.pem

# Copier les certificats dans le dossier nginx
sudo mkdir -p /opt/jlc-app/docker/nginx/ssl
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem /opt/jlc-app/docker/nginx/ssl/key.pem
sudo chmod 644 /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo chmod 600 /opt/jlc-app/docker/nginx/ssl/key.pem
```

#### Option B: Certificats existants

```bash
# Créer le dossier SSL
mkdir -p /opt/jlc-app/docker/nginx/ssl

# Copier vos certificats
cp /path/to/your/certificate.crt /opt/jlc-app/docker/nginx/ssl/cert.pem
cp /path/to/your/private.key /opt/jlc-app/docker/nginx/ssl/key.pem

# Permissions
chmod 644 /opt/jlc-app/docker/nginx/ssl/cert.pem
chmod 600 /opt/jlc-app/docker/nginx/ssl/key.pem
```

### Étape 4: Vérification de la Configuration Nginx

```bash
# Éditer la configuration nginx si nécessaire
nano /opt/jlc-app/docker/nginx/nginx.conf
```

**Vérifiez que les domaines correspondent**:
```nginx
server_name votredomaine.com www.votredomaine.com;
```

### Étape 5: Vérification des Dockerfiles

```bash
# Vérifier que les Dockerfiles existent
ls -la /opt/jlc-app/apps/api/Dockerfile.prod
ls -la /opt/jlc-app/apps/web/Dockerfile.prod
ls -la /opt/jlc-app/auth-microservice/Dockerfile.prod
```

---

## 🚀 Déploiement

### Étape 1: Préparation

```bash
cd /opt/jlc-app/docker

# Rendre les scripts exécutables
chmod +x scripts/*.sh

# Vérifier la configuration avant le déploiement
./scripts/pre-deploy-check.sh
```

### Étape 2: Build des Images Docker

```bash
# Build de toutes les images (peut prendre 10-20 minutes)
docker compose -f docker-compose.prod.yml build

# Suivre la progression
# Vous verrez les étapes de build pour:
# - auth-microservice
# - jlc-api  
# - jlc-web
```

### Étape 3: Lancement des Conteneurs

```bash
# Lancer tous les services en arrière-plan
docker compose -f docker-compose.prod.yml up -d

# Suivre les logs en temps réel
docker compose -f docker-compose.prod.yml logs -f
```

**Ordre de démarrage automatique**:
1. MongoDB (premier)
2. Auth Microservice (dépend de MongoDB)
3. JLC API (dépend de MongoDB + Auth)
4. JLC Web (dépend de JLC API)
5. Nginx (dépend de tous)

### Étape 4: Alternative - Script de Déploiement Automatique

```bash
# Utiliser le script de déploiement fourni
./scripts/deploy.sh

# Ce script fait automatiquement:
# 1. Vérification des prérequis
# 2. Build des images
# 3. Démarrage des conteneurs
# 4. Vérification de santé
# 5. Affichage des logs
```

---

## ✅ Vérification

### Étape 1: Vérifier l'État des Conteneurs

```bash
# Lister tous les conteneurs
docker ps

# Vous devriez voir 5 conteneurs en état "Up":
# - jlc-mongodb-prod
# - jlc-auth-prod
# - jlc-api-prod
# - jlc-web-prod
# - jlc-nginx
```

**Exemple de sortie attendue**:
```
CONTAINER ID   IMAGE                    STATUS         PORTS
abc123         jlc-nginx               Up 2 minutes   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
def456         jlc-web-prod            Up 3 minutes   0.0.0.0:3000->3000/tcp
ghi789         jlc-api-prod            Up 4 minutes   0.0.0.0:8001->8001/tcp
jkl012         jlc-auth-prod           Up 5 minutes   0.0.0.0:8000->8000/tcp
mno345         jlc-mongodb-prod        Up 6 minutes   0.0.0.0:27017->27017/tcp
```

### Étape 2: Vérifier les Logs

```bash
# Logs de tous les services
docker compose -f docker-compose.prod.yml logs

# Logs d'un service spécifique
docker compose -f docker-compose.prod.yml logs auth-microservice
docker compose -f docker-compose.prod.yml logs jlc-api
docker compose -f docker-compose.prod.yml logs jlc-web

# Suivre les logs en temps réel
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

### Étape 3: Tester les Endpoints

```bash
# Test du health check auth
curl http://localhost:8000/health
# Attendu: {"status": "healthy"}

# Test du health check API
curl http://localhost:8001/health
# Attendu: {"status": "healthy"}

# Test du frontend
curl http://localhost:3000
# Attendu: HTML de la page React

# Test via HTTPS (depuis l'extérieur)
curl https://votredomaine.com
```

### Étape 4: Vérifier MongoDB

```bash
# Se connecter à MongoDB
docker exec -it jlc-mongodb-prod mongosh -u admin_jlc -p

# Vérifier les bases de données
show dbs

# Vous devriez voir:
# - auth_db
# - jlc_db

# Quitter
exit
```

### Étape 5: Test depuis le Navigateur

**Accédez aux URLs**:
- Frontend: `https://votredomaine.com`
- API: `https://api.votredomaine.com/docs` (Documentation API)
- Auth: `https://auth.votredomaine.com/docs`

**Test de connexion**:
1. Ouvrez `https://votredomaine.com`
2. Cliquez sur "Connexion"
3. Essayez de vous connecter avec: `admin / awana2025`
4. Vérifiez que vous êtes redirigé vers le dashboard

### Étape 6: Monitoring avec le Script

```bash
# Utiliser le script de monitoring
./scripts/monitor.sh

# Affiche:
# - État des conteneurs
# - Utilisation CPU/RAM
# - Logs récents
# - Endpoints de santé
```

---

## 🔧 Maintenance

### Mise à Jour de l'Application

```bash
cd /opt/jlc-app

# Sauvegarder la base de données avant la mise à jour
./docker/scripts/backup.sh

# Récupérer les dernières modifications
git pull origin main

# Rebuild et redémarrage
cd docker
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Ou utiliser le script de mise à jour
./scripts/update.sh
```

### Sauvegarde de la Base de Données

```bash
# Sauvegarde manuelle
./docker/scripts/backup.sh

# Les backups sont stockés dans:
# /opt/jlc-app/docker/backups/

# Automatiser les sauvegardes (cron)
crontab -e

# Ajouter cette ligne pour une sauvegarde quotidienne à 2h du matin:
0 2 * * * /opt/jlc-app/docker/scripts/backup.sh
```

### Restauration d'une Sauvegarde

```bash
# Lister les sauvegardes disponibles
ls -lh /opt/jlc-app/docker/backups/

# Restaurer une sauvegarde spécifique
./docker/scripts/restore.sh /opt/jlc-app/docker/backups/backup-2025-01-20-02-00.tar.gz
```

### Redémarrage des Services

```bash
cd /opt/jlc-app/docker

# Redémarrer tous les services
docker compose -f docker-compose.prod.yml restart

# Redémarrer un service spécifique
docker compose -f docker-compose.prod.yml restart jlc-api
docker compose -f docker-compose.prod.yml restart auth-microservice

# Arrêter tous les services
docker compose -f docker-compose.prod.yml down

# Démarrer tous les services
docker compose -f docker-compose.prod.yml up -d
```

### Nettoyage

```bash
# Supprimer les images inutilisées
docker image prune -a

# Supprimer les volumes inutilisés (ATTENTION: supprime les données)
docker volume prune

# Supprimer tout ce qui n'est pas utilisé
docker system prune -a
```

---

## 🐛 Troubleshooting

### Problème: Un conteneur ne démarre pas

**Diagnostic**:
```bash
# Vérifier l'état
docker ps -a

# Voir les logs d'erreur
docker compose -f docker-compose.prod.yml logs <nom-service>

# Exemple
docker compose -f docker-compose.prod.yml logs auth-microservice
```

**Solutions courantes**:
1. **Variables d'environnement manquantes**: Vérifiez `.env.prod`
2. **Port déjà utilisé**: Arrêtez le service qui utilise le port
3. **Problème de permissions**: Vérifiez les permissions des fichiers

### Problème: MongoDB ne se connecte pas

**Diagnostic**:
```bash
# Vérifier que MongoDB est running
docker ps | grep mongodb

# Tester la connexion
docker exec -it jlc-mongodb-prod mongosh -u admin_jlc -p

# Vérifier les logs
docker logs jlc-mongodb-prod
```

**Solutions**:
1. Vérifiez `MONGO_ROOT_USERNAME` et `MONGO_ROOT_PASSWORD` dans `.env.prod`
2. Vérifiez que le port 27017 n'est pas déjà utilisé
3. Vérifiez les permissions du volume MongoDB

### Problème: Erreur 502 Bad Gateway

**Causes possibles**:
1. Backend pas encore démarré (attendre 30-60 secondes)
2. Backend crash au démarrage
3. Configuration Nginx incorrecte

**Solutions**:
```bash
# Vérifier que les backends sont UP
docker ps

# Vérifier les logs backend
docker compose -f docker-compose.prod.yml logs jlc-api
docker compose -f docker-compose.prod.yml logs auth-microservice

# Redémarrer nginx
docker compose -f docker-compose.prod.yml restart nginx

# Tester les endpoints directement
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Problème: Certificats SSL invalides

**Solutions**:
```bash
# Vérifier que les certificats existent
ls -la /opt/jlc-app/docker/nginx/ssl/

# Vérifier les permissions
chmod 644 /opt/jlc-app/docker/nginx/ssl/cert.pem
chmod 600 /opt/jlc-app/docker/nginx/ssl/key.pem

# Renouveler Let's Encrypt (si expiré)
sudo certbot renew

# Copier les nouveaux certificats
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem /opt/jlc-app/docker/nginx/ssl/key.pem

# Redémarrer nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### Problème: Manque d'espace disque

**Diagnostic**:
```bash
# Vérifier l'espace disque
df -h

# Vérifier la taille des volumes Docker
docker system df
```

**Solutions**:
```bash
# Nettoyer les images inutilisées
docker image prune -a

# Nettoyer les conteneurs arrêtés
docker container prune

# Nettoyer le cache de build
docker builder prune

# Rotation des logs
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

### Problème: Performance lente

**Diagnostic**:
```bash
# Vérifier l'utilisation des ressources
docker stats

# Vérifier les processus système
top
htop
```

**Solutions**:
1. Augmenter les ressources serveur (RAM, CPU)
2. Optimiser la configuration MongoDB
3. Mettre en place un système de cache (Redis)
4. Optimiser les requêtes de base de données

---

## 📊 Commandes Utiles

### Docker Compose

```bash
# Voir l'état de tous les services
docker compose -f docker-compose.prod.yml ps

# Voir les logs de tous les services
docker compose -f docker-compose.prod.yml logs

# Logs en temps réel
docker compose -f docker-compose.prod.yml logs -f

# Redémarrer un service
docker compose -f docker-compose.prod.yml restart <service-name>

# Stopper tous les services
docker compose -f docker-compose.prod.yml stop

# Démarrer tous les services
docker compose -f docker-compose.prod.yml start

# Supprimer tous les conteneurs
docker compose -f docker-compose.prod.yml down

# Supprimer conteneurs + volumes (ATTENTION: perte de données)
docker compose -f docker-compose.prod.yml down -v
```

### Docker

```bash
# Lister tous les conteneurs
docker ps -a

# Inspecter un conteneur
docker inspect <container-id>

# Exécuter une commande dans un conteneur
docker exec -it <container-id> bash

# Copier des fichiers depuis/vers un conteneur
docker cp <container-id>:/path/in/container /path/on/host
docker cp /path/on/host <container-id>:/path/in/container

# Voir l'utilisation des ressources
docker stats

# Nettoyer le système
docker system prune -a
```

---

## 🔐 Sécurité

### Bonnes Pratiques

1. **Mots de passe forts**:
   - Minimum 16 caractères
   - Lettres majuscules/minuscules, chiffres, symboles
   - Générés aléatoirement

2. **Firewall**:
```bash
# Installer UFW (Ubuntu)
sudo apt install ufw

# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le firewall
sudo ufw enable
```

3. **Mise à jour régulière**:
```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Mettre à jour Docker
sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io

# Mettre à jour l'application
cd /opt/jlc-app && git pull && ./docker/scripts/update.sh
```

4. **Sauvegardes automatiques**:
```bash
# Configurer cron pour des sauvegardes quotidiennes
crontab -e

# Ajouter:
0 2 * * * /opt/jlc-app/docker/scripts/backup.sh
```

5. **Monitoring**:
```bash
# Installer un outil de monitoring (optionnel)
# Prometheus + Grafana, Netdata, etc.
```

---

## 📝 Checklist de Déploiement

Utilisez cette checklist pour vous assurer que tout est configuré correctement:

### Avant le Déploiement
- [ ] Serveur avec les ressources suffisantes
- [ ] Docker et Docker Compose installés
- [ ] Code récupéré sur le serveur
- [ ] Fichier `.env.prod` créé et configuré
- [ ] Certificats SSL générés et copiés
- [ ] Configuration nginx vérifiée
- [ ] DNS configuré pour pointer vers le serveur

### Pendant le Déploiement
- [ ] Build des images réussi
- [ ] Tous les conteneurs démarrés
- [ ] Pas d'erreurs dans les logs
- [ ] Health checks réussis

### Après le Déploiement
- [ ] Site accessible via HTTPS
- [ ] Connexion admin fonctionnelle
- [ ] API accessible
- [ ] Certificats SSL valides
- [ ] Sauvegardes configurées
- [ ] Monitoring en place
- [ ] Documentation à jour

---

## 📞 Support

Si vous rencontrez des problèmes:

1. **Vérifiez les logs**: `docker compose logs`
2. **Consultez le troubleshooting**: Section ci-dessus
3. **Vérifiez la documentation Docker**: `/app/docker/README.md`
4. **Contactez le support**: support@jlcgroup.com

---

## 🎉 Félicitations !

Votre application JLC est maintenant déployée en production avec Docker ! 🚀

Pour toute question ou amélioration de ce guide, n'hésitez pas à contribuer.
