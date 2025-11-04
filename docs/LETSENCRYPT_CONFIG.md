# 🔐 Configuration HTTPS avec Let's Encrypt - Guide Complet

## ✅ Oui, la Configuration Fonctionne avec Let's Encrypt !

Votre configuration Nginx actuelle est compatible avec Let's Encrypt. Voici comment l'utiliser et l'optimiser.

---

## 📋 Table des Matières

1. [Méthode Rapide (Recommandée)](#méthode-rapide)
2. [Méthode Manuelle](#méthode-manuelle)
3. [Configuration Nginx Optimisée](#configuration-nginx-optimisée)
4. [Renouvellement Automatique](#renouvellement-automatique)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Méthode Rapide (Recommandée)

### Étape 1: Installation de Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y certbot

# CentOS/RHEL
sudo yum install -y certbot

# Vérification
certbot --version
```

### Étape 2: Génération des Certificats

**Important**: Arrêtez temporairement Nginx/Docker pour libérer les ports 80/443

```bash
# Arrêter les conteneurs Docker
cd /opt/jlc-app/docker
docker compose -f docker-compose.prod.yml down

# Générer les certificats (mode standalone)
sudo certbot certonly --standalone \
  -d votredomaine.com \
  -d www.votredomaine.com \
  -d api.votredomaine.com \
  -d auth.votredomaine.com \
  --agree-tos \
  --email votre-email@example.com

# Les certificats seront dans:
# /etc/letsencrypt/live/votredomaine.com/fullchain.pem
# /etc/letsencrypt/live/votredomaine.com/privkey.pem
```

### Étape 3: Copier les Certificats dans Docker

```bash
# Créer le dossier SSL dans le projet
sudo mkdir -p /opt/jlc-app/docker/nginx/ssl

# Copier les certificats
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem \
  /opt/jlc-app/docker/nginx/ssl/cert.pem

sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem \
  /opt/jlc-app/docker/nginx/ssl/key.pem

# Permissions correctes
sudo chmod 644 /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo chmod 600 /opt/jlc-app/docker/nginx/ssl/key.pem
```

### Étape 4: Modifier nginx.conf

```bash
# Éditer nginx.conf
nano /opt/jlc-app/docker/nginx/nginx.conf
```

**Remplacez** `yourdomain.com` par votre vrai domaine dans les 3 sections:
- Ligne 21: `server_name votredomaine.com www.votredomaine.com ...`
- Ligne 28: `server_name votredomaine.com www.votredomaine.com;`
- Ligne 48: `server_name api.votredomaine.com;`
- Ligne 70: `server_name auth.votredomaine.com;`

### Étape 5: Redémarrer Docker

```bash
# Redémarrer les conteneurs
docker compose -f docker-compose.prod.yml up -d

# Vérifier
docker ps
docker compose -f docker-compose.prod.yml logs nginx
```

### Étape 6: Test

```bash
# Test HTTPS
curl -I https://votredomaine.com
curl -I https://api.votredomaine.com
curl -I https://auth.votredomaine.com

# Vérifier le certificat
echo | openssl s_client -connect votredomaine.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 🔧 Méthode Manuelle (Certbot en Container)

Si vous ne voulez pas arrêter Docker, utilisez le plugin webroot:

### Étape 1: Ajouter le Volume Webroot

Modifiez `docker-compose.prod.yml`:

```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    - ./nginx/ssl:/etc/nginx/ssl
    - ./nginx/webroot:/var/www/certbot  # AJOUTER CETTE LIGNE
    - logs:/var/log/nginx
```

### Étape 2: Modifier nginx.conf

Ajoutez cette section dans le bloc `server` qui écoute sur le port 80 (ligne 19):

```nginx
server {
    listen 80;
    server_name votredomaine.com www.votredomaine.com api.votredomaine.com;
    
    # Ajoutez cette section pour Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirection HTTPS pour le reste
    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

### Étape 3: Créer le Dossier Webroot

```bash
mkdir -p /opt/jlc-app/docker/nginx/webroot
```

### Étape 4: Redémarrer Nginx

```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### Étape 5: Générer les Certificats avec Webroot

```bash
sudo certbot certonly --webroot \
  -w /opt/jlc-app/docker/nginx/webroot \
  -d votredomaine.com \
  -d www.votredomaine.com \
  -d api.votredomaine.com \
  -d auth.votredomaine.com \
  --agree-tos \
  --email votre-email@example.com
```

### Étape 6: Copier et Redémarrer

```bash
# Copier les certificats
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem \
  /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem \
  /opt/jlc-app/docker/nginx/ssl/key.pem

# Redémarrer
docker compose -f docker-compose.prod.yml restart nginx
```

---

## ⚙️ Configuration Nginx Optimisée pour Let's Encrypt

Voici une configuration Nginx complète et optimisée:

```nginx
events {
    worker_connections 1024;
}

http {
    # Configuration SSL optimale
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    upstream frontend {
        server jlc-web-prod:80;
    }

    upstream api {
        server jlc-api-prod:8001;
    }

    upstream auth {
        server jlc-auth-prod:8000;
    }

    # Redirection HTTP vers HTTPS + Challenge Let's Encrypt
    server {
        listen 80;
        server_name votredomaine.com www.votredomaine.com api.votredomaine.com auth.votredomaine.com;

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

    # Frontend HTTPS
    server {
        listen 443 ssl http2;
        server_name votredomaine.com www.votredomaine.com;

        # Certificats Let's Encrypt
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Configuration SSL sécurisée
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers on;
        
        # HSTS (optionnel mais recommandé)
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Sécurité headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # API Backend HTTPS
    server {
        listen 443 ssl http2;
        server_name api.votredomaine.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers on;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
            
            # CORS si nécessaire
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        }
    }

    # Auth Microservice HTTPS
    server {
        listen 443 ssl http2;
        server_name auth.votredomaine.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers on;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://auth;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**Sauvegardez** ce fichier dans: `/opt/jlc-app/docker/nginx/nginx.conf`

---

## 🔄 Renouvellement Automatique

Les certificats Let's Encrypt expirent après **90 jours**. Configurez le renouvellement automatique:

### Méthode 1: Cron Job (Recommandée)

```bash
# Créer le script de renouvellement
sudo nano /opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Contenu du script**:

```bash
#!/bin/bash

# Renouveler les certificats
certbot renew --quiet

# Copier les nouveaux certificats
cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem \
   /opt/jlc-app/docker/nginx/ssl/cert.pem

cp /etc/letsencrypt/live/votredomaine.com/privkey.pem \
   /opt/jlc-app/docker/nginx/ssl/key.pem

# Redémarrer Nginx
cd /opt/jlc-app/docker
docker compose -f docker-compose.prod.yml restart nginx

echo "SSL certificates renewed successfully at $(date)" >> /var/log/ssl-renewal.log
```

**Rendre le script exécutable**:

```bash
sudo chmod +x /opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Configurer le Cron**:

```bash
# Éditer crontab
sudo crontab -e

# Ajouter cette ligne (renouvellement tous les 1er du mois à 3h du matin)
0 3 1 * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

### Méthode 2: Systemd Timer

```bash
# Créer le service
sudo nano /etc/systemd/system/certbot-renewal.service
```

**Contenu**:

```ini
[Unit]
Description=Certbot Renewal

[Service]
Type=oneshot
ExecStart=/opt/jlc-app/docker/scripts/renew-ssl.sh
```

**Créer le timer**:

```bash
sudo nano /etc/systemd/system/certbot-renewal.timer
```

**Contenu**:

```ini
[Unit]
Description=Certbot Renewal Timer

[Timer]
OnCalendar=monthly
Persistent=true

[Install]
WantedBy=timers.target
```

**Activer**:

```bash
sudo systemctl enable certbot-renewal.timer
sudo systemctl start certbot-renewal.timer
sudo systemctl status certbot-renewal.timer
```

---

## 🐛 Troubleshooting

### Problème 1: Certificat Invalide

**Diagnostic**:
```bash
# Vérifier les dates du certificat
echo | openssl s_client -connect votredomaine.com:443 2>/dev/null | openssl x509 -noout -dates

# Vérifier le certificat chargé par Nginx
docker exec jlc-nginx cat /etc/nginx/ssl/cert.pem | openssl x509 -noout -dates
```

**Solution**:
```bash
# Renouveler le certificat
sudo certbot renew --force-renewal

# Copier les nouveaux certificats
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem \
  /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem \
  /opt/jlc-app/docker/nginx/ssl/key.pem

# Redémarrer
docker compose -f docker-compose.prod.yml restart nginx
```

### Problème 2: Erreur "Port 80 Already in Use"

**Solution**:
```bash
# Trouver ce qui utilise le port 80
sudo lsof -i :80

# Arrêter le service (exemple Apache)
sudo systemctl stop apache2

# Ou arrêter Docker temporairement
docker compose -f docker-compose.prod.yml down

# Générer les certificats
sudo certbot certonly --standalone -d votredomaine.com

# Redémarrer Docker
docker compose -f docker-compose.prod.yml up -d
```

### Problème 3: DNS Non Configuré

**Vérification**:
```bash
# Vérifier que le DNS pointe vers votre serveur
dig votredomaine.com
nslookup votredomaine.com
```

**Solution**:
- Configurez vos enregistrements DNS (A ou CNAME)
- Attendez la propagation DNS (jusqu'à 48h)
- Utilisez `dig @8.8.8.8 votredomaine.com` pour vérifier

### Problème 4: Permission Denied sur les Certificats

**Solution**:
```bash
# Corriger les permissions
sudo chmod 644 /opt/jlc-app/docker/nginx/ssl/cert.pem
sudo chmod 600 /opt/jlc-app/docker/nginx/ssl/key.pem
sudo chown root:root /opt/jlc-app/docker/nginx/ssl/*

# Redémarrer Nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### Problème 5: Certificat Expiré

**Vérifier**:
```bash
# Voir la date d'expiration
sudo certbot certificates
```

**Renouveler**:
```bash
# Forcer le renouvellement
sudo certbot renew --force-renewal

# Copier et redémarrer
sudo /opt/jlc-app/docker/scripts/renew-ssl.sh
```

---

## ✅ Checklist Let's Encrypt

Avant de déployer:

- [ ] DNS configuré et propagé
- [ ] Ports 80 et 443 ouverts sur le firewall
- [ ] Certbot installé
- [ ] Domaines préparés (votredomaine.com, api.votredomaine.com, etc.)
- [ ] Nginx configuré avec les bons domaines
- [ ] Certificats générés avec succès
- [ ] Certificats copiés dans `/opt/jlc-app/docker/nginx/ssl/`
- [ ] Permissions correctes sur les certificats
- [ ] Docker redémarré
- [ ] HTTPS fonctionne (test avec `curl -I https://votredomaine.com`)
- [ ] Renouvellement automatique configuré

---

## 🎯 Résumé Rapide

```bash
# 1. Installer Certbot
sudo apt install -y certbot

# 2. Arrêter Docker
cd /opt/jlc-app/docker && docker compose -f docker-compose.prod.yml down

# 3. Générer certificats
sudo certbot certonly --standalone -d votredomaine.com -d www.votredomaine.com

# 4. Copier dans Docker
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem nginx/ssl/key.pem

# 5. Modifier nginx.conf (remplacer yourdomain.com par votredomaine.com)
nano nginx/nginx.conf

# 6. Redémarrer
docker compose -f docker-compose.prod.yml up -d

# 7. Tester
curl -I https://votredomaine.com

# 8. Configurer renouvellement auto
sudo crontab -e
# Ajouter: 0 3 1 * * /opt/jlc-app/docker/scripts/renew-ssl.sh
```

---

## 📚 Ressources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/) - Testez votre configuration SSL

---

**Oui, votre configuration fonctionne parfaitement avec Let's Encrypt ! Suivez simplement les étapes ci-dessus. 🔐✅**
