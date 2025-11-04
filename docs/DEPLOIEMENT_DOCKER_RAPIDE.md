# 🚀 Déploiement Docker - Guide Rapide

## ⚡ Installation en 5 Minutes

### 1. Prérequis
```bash
# Installer Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Récupérer le Code
```bash
git clone <votre-repo> /opt/jlc-app
cd /opt/jlc-app/docker
```

### 3. Configuration
```bash
# Créer le fichier .env.prod
cat > .env.prod << 'EOF'
MONGO_ROOT_USERNAME=admin_jlc
MONGO_ROOT_PASSWORD=ChangezCeMotDePasse123!
JWT_SECRET=votre-secret-jwt-minimum-32-caracteres-aleatoires
CORS_ORIGINS=https://votredomaine.com
API_BASE_URL=https://api.votredomaine.com
AUTH_SERVICE_URL=https://auth.votredomaine.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
GOOGLE_CLIENT_ID=votre-client-id
GOOGLE_CLIENT_SECRET=votre-client-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=production
EOF
```

### 4. SSL (Let's Encrypt)
```bash
# Installer certbot
sudo apt install -y certbot

# Générer les certificats
sudo certbot certonly --standalone -d votredomaine.com

# Copier dans le projet
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/votredomaine.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/votredomaine.com/privkey.pem nginx/ssl/key.pem
```

### 5. Déploiement
```bash
# Build et démarrage
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Vérifier
docker ps
docker compose -f docker-compose.prod.yml logs -f
```

### 6. Test
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health

# Accès web
https://votredomaine.com
```

---

## 📋 Commandes Essentielles

```bash
# Voir l'état
docker compose -f docker-compose.prod.yml ps

# Logs
docker compose -f docker-compose.prod.yml logs -f

# Redémarrer
docker compose -f docker-compose.prod.yml restart

# Arrêter
docker compose -f docker-compose.prod.yml down

# Mise à jour
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Sauvegarde
./scripts/backup.sh
```

---

## 🐛 Problèmes Courants

### Conteneur ne démarre pas
```bash
docker compose -f docker-compose.prod.yml logs <service-name>
```

### Port déjà utilisé
```bash
sudo lsof -i :<port>
sudo kill -9 <PID>
```

### Manque d'espace
```bash
docker system prune -a
```

### Certificat SSL invalide
```bash
sudo certbot renew
sudo cp /etc/letsencrypt/live/votredomaine.com/* nginx/ssl/
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 📚 Documentation Complète

Pour plus de détails, consultez:
- `/app/docs/DEPLOIEMENT_DOCKER_DETAILLE.md` - Guide complet
- `/app/docker/DEPLOYMENT_GUIDE.md` - Guide original
- `/app/docker/README.md` - Overview Docker

---

## ✅ Checklist

- [ ] Docker installé
- [ ] Code cloné
- [ ] `.env.prod` configuré
- [ ] SSL configuré
- [ ] Build réussi
- [ ] Tous les conteneurs UP
- [ ] Site accessible en HTTPS
- [ ] Login admin fonctionne

---

**Support**: support@jlcgroup.com
