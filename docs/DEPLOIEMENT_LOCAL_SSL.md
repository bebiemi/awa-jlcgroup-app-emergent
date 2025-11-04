# 🏠 Déploiement Local + SSL - Guide Complet

## 📋 Vue d'ensemble des Options

### Option 1 : Local pur (localhost) - Sans Let's Encrypt ❌
**Problème** : Let's Encrypt **ne fonctionne PAS** avec localhost car :
- Nécessite un domaine public accessible depuis internet
- Validation impossible pour 127.0.0.1 ou localhost

**Solutions alternatives** :
- ✅ Certificats auto-signés (warning navigateur)
- ✅ mkcert (certificats locaux de confiance)
- ✅ Développement en HTTP (pas de SSL)

---

### Option 2 : Sous-domaine + Let's Encrypt ⭐ RECOMMANDÉ
**Avec** : `jlc-dev.awana-group.com` pointant vers votre PC

**Prérequis** :
- ✅ Votre PC doit être accessible depuis internet
- ✅ Configuration port forwarding sur votre routeur
- ✅ IP publique (dynamique ou statique)
- ✅ DNS configuré dans OVH

**Avantages** :
- ✅ Vrai certificat SSL Let's Encrypt
- ✅ Pas de warning navigateur
- ✅ Configuration proche de la production
- ✅ Accès depuis n'importe où

---

## 🟢 OPTION 1 : Local Pur avec mkcert (Simple)

### Qu'est-ce que mkcert ?

**mkcert** crée des certificats SSL de confiance pour le développement local.

**Avantages** :
- ✅ HTTPS en local sans warning
- ✅ Pas besoin d'internet
- ✅ Installation en 5 minutes
- ✅ Gratuit

### Installation de mkcert

#### macOS
```bash
brew install mkcert
brew install nss # Pour Firefox
```

#### Linux (Ubuntu/Debian)
```bash
# Installer certutil
sudo apt install libnss3-tools

# Télécharger mkcert
wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert-v1.4.4-linux-amd64
sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert
```

#### Windows
```powershell
# Avec Chocolatey
choco install mkcert

# Ou télécharger depuis GitHub
# https://github.com/FiloSottile/mkcert/releases
```

### Configuration avec mkcert

#### Étape 1 : Installer la CA locale

```bash
# Installer le certificat racine local
mkcert -install

# Vous verrez quelque chose comme :
# Created a new local CA at "/Users/vous/Library/Application Support/mkcert"
# The local CA is now installed in the system trust store! ⚡️
```

#### Étape 2 : Générer les certificats

```bash
# Aller dans votre projet
cd /chemin/vers/jlc-app/docker/nginx/ssl

# Générer les certificats pour localhost
mkcert localhost 127.0.0.1 ::1

# Cela crée :
# - localhost+2.pem (certificat)
# - localhost+2-key.pem (clé privée)

# Renommer pour correspondre à la config nginx
mv localhost+2.pem cert.pem
mv localhost+2-key.pem key.pem
```

#### Étape 3 : Modifier nginx.conf

```bash
nano /chemin/vers/jlc-app/docker/nginx/nginx.conf
```

**Remplacer tous les domaines par localhost** :

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... reste de la config
}
```

#### Étape 4 : Démarrer Docker

```bash
cd /chemin/vers/jlc-app/docker

# Créer .env.local
cp .env.prod .env.local

# Modifier les URLs pour localhost
nano .env.local
```

**Contenu .env.local** :
```bash
MONGO_ROOT_USERNAME=admin_jlc
MONGO_ROOT_PASSWORD=awana2025
JWT_SECRET=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,https://localhost
API_BASE_URL=http://localhost:8001
REACT_APP_BACKEND_URL=http://localhost:8001
ENVIRONMENT=development
```

**Démarrer** :
```bash
docker compose -f docker-compose.yml up -d
```

#### Étape 5 : Accéder à l'application

```bash
# Avec SSL (mkcert)
https://localhost

# Sans SSL
http://localhost:3000
```

✅ **Pas de warning de sécurité !**

---

## 🔵 OPTION 2 : Sous-domaine + Let's Encrypt ⭐

### Architecture

```
Internet
   ↓
jlc-dev.awana-group.com (DNS OVH)
   ↓
Votre IP publique (ex: 82.123.45.67)
   ↓
Votre Routeur (Port forwarding 80, 443)
   ↓
Votre PC (192.168.x.x)
   ↓
Docker (Nginx, Frontend, API, Auth, MongoDB)
```

### Prérequis

#### 1. Vérifier votre IP publique

```bash
# Trouver votre IP publique
curl ifconfig.me

# Ou
curl https://api.ipify.org

# Exemple de sortie : 82.123.45.67
```

**Important** : Notez cette IP !

#### 2. Vérifier l'accès depuis internet

```bash
# Sur votre PC, démarrer un serveur web test
python3 -m http.server 8080

# Demander à quelqu'un d'accéder à http://VOTRE-IP:8080
# OU utiliser un service : https://www.yougetsignal.com/tools/open-ports/
```

Si ça ne fonctionne pas → Configurer le port forwarding

### Configuration du Routeur (Port Forwarding)

#### Étape 1 : Accéder à votre routeur

```
http://192.168.1.1
ou
http://192.168.0.1

Login: admin (ou celui de votre FAI)
```

#### Étape 2 : Trouver l'IP locale de votre PC

```bash
# Linux/macOS
ip addr show | grep inet
# ou
ifconfig | grep inet

# Windows
ipconfig

# Exemple : 192.168.1.100
```

#### Étape 3 : Configurer le Port Forwarding

**Dans l'interface du routeur** :

```
Port Forwarding / NAT / Redirection de port

Nouvelle règle :
Service Name: HTTP
External Port: 80
Internal IP: 192.168.1.100 (IP de votre PC)
Internal Port: 80
Protocol: TCP

Nouvelle règle :
Service Name: HTTPS
External Port: 443
Internal IP: 192.168.1.100
Internal Port: 443
Protocol: TCP
```

**Sauvegarder et redémarrer le routeur** si nécessaire.

### Configuration DNS sur OVH

#### Étape 1 : Se connecter à OVH

1. Aller sur https://www.ovh.com/manager/
2. Se connecter avec vos identifiants
3. Aller dans **Web Cloud** → **Domaines** → `awana-group.com`
4. Cliquer sur **Zone DNS**

#### Étape 2 : Ajouter un Enregistrement A

Cliquer sur **Ajouter une entrée** :

```
Type : A
Sous-domaine : jlc-dev
TTL : 3600 (1 heure)
Cible : VOTRE_IP_PUBLIQUE (ex: 82.123.45.67)
```

**Exemple** :
```
jlc-dev.awana-group.com → 82.123.45.67
```

Cliquer sur **Valider**

#### Étape 3 : Vérifier la Propagation DNS

```bash
# Attendre 5-10 minutes, puis tester
dig jlc-dev.awana-group.com

# Ou
nslookup jlc-dev.awana-group.com

# Doit retourner votre IP publique
```

**Outil en ligne** : https://dnschecker.org/

### Installation sur votre PC

#### Étape 1 : Prérequis

```bash
# Docker installé
docker --version

# Si pas installé :
# macOS
brew install docker

# Linux
curl -fsSL https://get.docker.com | sh

# Windows
# Télécharger Docker Desktop
```

#### Étape 2 : Préparer le projet

```bash
cd /chemin/vers/jlc-app/docker

# Créer .env.local pour le développement
nano .env.local
```

**Contenu .env.local** :
```bash
MONGO_ROOT_USERNAME=admin_jlc_dev
MONGO_ROOT_PASSWORD=dev_password_123
JWT_SECRET=dev-jwt-secret-change-in-production
CORS_ORIGINS=https://jlc-dev.awana-group.com
API_BASE_URL=https://jlc-dev.awana-group.com/api
REACT_APP_BACKEND_URL=https://jlc-dev.awana-group.com/api
AUTH_SERVICE_URL=https://jlc-dev.awana-group.com/auth
ENVIRONMENT=development
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password
```

#### Étape 3 : Modifier nginx.conf

```bash
nano nginx/nginx.conf
```

**Remplacer tous les `yourdomain.com` par `jlc-dev.awana-group.com`** :

```nginx
server {
    listen 80;
    server_name jlc-dev.awana-group.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }
    
    # Redirection HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name jlc-dev.awana-group.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... reste de la config
}
```

#### Étape 4 : Générer les Certificats Let's Encrypt

```bash
# Installer Certbot
# macOS
brew install certbot

# Linux
sudo apt install certbot

# Windows (WSL required)
# Install Ubuntu WSL first, then:
sudo apt install certbot
```

**Arrêter Docker temporairement** :
```bash
docker compose down
```

**Générer les certificats** :
```bash
sudo certbot certonly --standalone \
  -d jlc-dev.awana-group.com \
  --agree-tos \
  --email votre-email@awana-group.com
```

**Résultat** :
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/jlc-dev.awana-group.com/fullchain.pem
Key is saved at: /etc/letsencrypt/live/jlc-dev.awana-group.com/privkey.pem
```

**Copier les certificats** :
```bash
# Créer le dossier SSL
mkdir -p nginx/ssl

# Copier
sudo cp /etc/letsencrypt/live/jlc-dev.awana-group.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/jlc-dev.awana-group.com/privkey.pem nginx/ssl/key.pem

# Permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

#### Étape 5 : Démarrer Docker

```bash
# Build et démarrage
docker compose -f docker-compose.prod.yml --env-file .env.local build
docker compose -f docker-compose.prod.yml --env-file .env.local up -d

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs -f
```

#### Étape 6 : Tester

```bash
# Depuis votre PC
curl https://jlc-dev.awana-group.com

# Depuis un navigateur
https://jlc-dev.awana-group.com

# Test admin login
Username: admin
Password: awana2025
```

✅ **Certificat SSL valide !** Pas de warning.

### Renouvellement Automatique Let's Encrypt

#### Configuration du script

```bash
# Éditer le script de renouvellement
nano /chemin/vers/jlc-app/docker/scripts/renew-ssl.sh
```

**Modifier la ligne 9** :
```bash
DOMAIN="jlc-dev.awana-group.com"
```

**Configurer cron** :
```bash
# Ouvrir crontab
crontab -e

# Ajouter (renouvellement mensuel)
0 3 1 * * /chemin/vers/jlc-app/docker/scripts/renew-ssl.sh >> /var/log/ssl-renewal.log 2>&1
```

**Ou utiliser le script d'installation automatique** :
```bash
cd /chemin/vers/jlc-app/docker/scripts
chmod +x setup-ssl-renewal.sh
sudo ./setup-ssl-renewal.sh
```

---

## ⚡ IP Dynamique : Solution avec DynDNS

### Problème

Si votre IP publique change (ADSL/Fibre résidentielle), le DNS ne sera plus à jour.

### Solution 1 : Script de Mise à Jour OVH

```bash
nano /chemin/vers/update-dns-ovh.sh
```

**Contenu** :
```bash
#!/bin/bash

# Configuration OVH API (créer sur https://api.ovh.com/createToken/)
APP_KEY="votre_app_key"
APP_SECRET="votre_app_secret"
CONSUMER_KEY="votre_consumer_key"
DOMAIN="awana-group.com"
SUBDOMAIN="jlc-dev"

# Obtenir l'IP actuelle
CURRENT_IP=$(curl -s https://api.ipify.org)

# Appeler l'API OVH pour mettre à jour
# (Code complet à implémenter avec l'API OVH)

echo "DNS mis à jour : $SUBDOMAIN.$DOMAIN → $CURRENT_IP"
```

**Cron toutes les 10 minutes** :
```bash
*/10 * * * * /chemin/vers/update-dns-ovh.sh
```

### Solution 2 : DuckDNS (Gratuit et Simple)

1. Aller sur https://www.duckdns.org/
2. Créer un compte (login avec Google/GitHub)
3. Créer un domaine : `jlc-dev.duckdns.org`
4. Installer le client sur votre PC
5. Utiliser ce domaine au lieu de `jlc-dev.awana-group.com`

---

## 🔧 Troubleshooting Local

### Problème 1 : Port 80/443 déjà utilisé

```bash
# Trouver ce qui utilise le port
# macOS/Linux
sudo lsof -i :80
sudo lsof -i :443

# Windows
netstat -ano | findstr :80
netstat -ano | findstr :443

# Arrêter le service (exemple Apache)
sudo systemctl stop apache2

# Ou changer les ports dans docker-compose.yml
ports:
  - "8080:80"   # HTTP sur port 8080
  - "8443:443"  # HTTPS sur port 8443
```

### Problème 2 : Certificat mkcert non reconnu

```bash
# Réinstaller la CA
mkcert -uninstall
mkcert -install

# Redémarrer le navigateur
```

### Problème 3 : DNS ne se résout pas

```bash
# Vérifier la propagation
dig jlc-dev.awana-group.com

# Vider le cache DNS local
# macOS
sudo dscacheutil -flushcache

# Linux
sudo systemd-resolve --flush-caches

# Windows (CMD admin)
ipconfig /flushdns
```

### Problème 4 : Port forwarding ne fonctionne pas

```bash
# Test depuis l'extérieur
# Utiliser : https://www.yougetsignal.com/tools/open-ports/
# Port à tester : 80 et 443

# Vérifier le firewall local
# Linux
sudo ufw allow 80
sudo ufw allow 443

# macOS
# Système → Sécurité → Pare-feu → Autoriser les connexions

# Windows
# Panneau de configuration → Pare-feu Windows → Règles entrantes
```

### Problème 5 : Let's Encrypt échoue

```bash
# Test dry-run
sudo certbot certonly --standalone --dry-run -d jlc-dev.awana-group.com

# Vérifier que le port 80 est accessible depuis internet
# Vérifier le DNS
# Vérifier le port forwarding
```

---

## 📊 Comparaison des Options

| Critère | mkcert (localhost) | Let's Encrypt (sous-domaine) |
|---------|-------------------|------------------------------|
| **Complexité** | ⭐ Facile | ⭐⭐⭐ Moyen |
| **SSL Valide** | ⭐⭐⭐ Local uniquement | ⭐⭐⭐⭐⭐ Partout |
| **Accès externe** | ❌ Non | ✅ Oui |
| **Configuration routeur** | ❌ Non | ✅ Requis |
| **Renouvellement** | ❌ Pas nécessaire | ✅ Auto (cron) |
| **Production-like** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Temps setup** | 10 min | 30-60 min |

---

## 🎯 Recommandation

### Pour Développement Simple
**mkcert + localhost** ⭐
- Rapide (10 minutes)
- Pas besoin d'internet
- SSL sans warning

### Pour Développement Réaliste
**Let's Encrypt + jlc-dev.awana-group.com** ⭐⭐⭐
- Configuration identique à la production
- Vrai certificat SSL
- Accessible de n'importe où
- Bon pour tester avec des collègues/clients

---

## ✅ Checklist

### mkcert (Local)
- [ ] mkcert installé
- [ ] CA locale installée (`mkcert -install`)
- [ ] Certificats générés pour localhost
- [ ] nginx.conf modifié pour localhost
- [ ] Docker démarré
- [ ] Accessible sur https://localhost

### Let's Encrypt (Sous-domaine)
- [ ] IP publique identifiée
- [ ] Port forwarding configuré (80, 443)
- [ ] DNS configuré dans OVH
- [ ] Propagation DNS vérifiée
- [ ] Certbot installé
- [ ] Certificats Let's Encrypt générés
- [ ] nginx.conf modifié pour jlc-dev.awana-group.com
- [ ] Docker démarré
- [ ] Accessible sur https://jlc-dev.awana-group.com
- [ ] Renouvellement auto configuré

---

## 📁 Commandes Rapides

### Démarrage Rapide mkcert

```bash
# Installation et configuration (une seule fois)
brew install mkcert  # ou apt/choco selon OS
mkcert -install
cd /chemin/vers/jlc-app/docker/nginx/ssl
mkcert localhost 127.0.0.1
mv localhost+2.pem cert.pem
mv localhost+2-key.pem key.pem

# Démarrage
cd /chemin/vers/jlc-app/docker
docker compose up -d

# Accès
open https://localhost
```

### Démarrage Rapide Let's Encrypt

```bash
# Configuration DNS OVH (une seule fois)
# jlc-dev.awana-group.com → VOTRE_IP_PUBLIQUE

# Installation
brew install certbot  # ou apt selon OS
sudo certbot certonly --standalone -d jlc-dev.awana-group.com
sudo cp /etc/letsencrypt/live/jlc-dev.awana-group.com/*.pem nginx/ssl/
sudo chmod 644 nginx/ssl/cert.pem && sudo chmod 600 nginx/ssl/key.pem

# Démarrage
docker compose -f docker-compose.prod.yml up -d

# Accès
open https://jlc-dev.awana-group.com
```

---

**Vous êtes prêt pour un déploiement local sécurisé ! 🎉**

Quelle option préférez-vous ?
