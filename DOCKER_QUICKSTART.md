# 🚀 Démarrage Rapide Docker - JLC

## ⚡ En 3 Étapes

### 1️⃣ Installer Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
brew install --cask docker
```

**Windows:**
- Télécharger [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2️⃣ Démarrer l'application

**Option A: Script automatique (recommandé)**
```bash
./docker-start.sh dev
```

**Option B: Make**
```bash
make dev
```

**Option C: Docker Compose manuel**
```bash
cd docker
docker-compose up -d
```

### 3️⃣ Accéder à l'application

Ouvrez votre navigateur:
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8001/docs
- **Mailhog**: http://localhost:8025

---

## 📝 Commandes Essentielles

### Démarrage
```bash
./docker-start.sh dev          # Démarrer en mode développement
make dev                       # Alternative avec Make
```

### Voir les logs
```bash
./docker-start.sh logs         # Tous les logs
make dev-logs                  # Alternative avec Make
docker-compose logs -f         # Manuel
```

### Arrêter
```bash
./docker-start.sh stop         # Arrêter tous les services
make dev-down                  # Alternative avec Make
```

### Redémarrer un service
```bash
docker-compose restart jlc-web       # Frontend
docker-compose restart jlc-api       # API
docker-compose restart auth-microservice  # Auth
```

### Shell dans un container
```bash
make shell-frontend            # Entrer dans le container frontend
make shell-api                 # Entrer dans le container API
docker-compose exec jlc-web sh # Manuel
```

---

## 🔧 Résolution de Problèmes

### Erreur "port already in use"
```bash
# Trouver le processus
lsof -i :5173
# ou
sudo netstat -tulpn | grep 5173

# Tuer le processus ou changer le port dans docker-compose.yml
```

### Services ne démarrent pas
```bash
# Voir les logs détaillés
docker-compose logs mongodb
docker-compose logs jlc-web

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d --build
```

### Erreur de configuration manquante
```bash
# Vérifier que les fichiers de config existent
ls -la auth-microservice/config/
ls -la apps/web/.env

# Reconstruire les images
docker-compose up -d --build
```

### MongoDB ne démarre pas
```bash
# Supprimer les volumes et redémarrer
docker-compose down -v
docker volume prune
docker-compose up -d
```

---

## 📚 Guides Complets

- **Guide détaillé**: `DOCKER_GUIDE.md`
- **Documentation Docker**: `docker/README.md`
- **Commandes Make**: `make help`

---

## 🎯 Scénarios Courants

### Développement Frontend uniquement
```bash
# Démarrer seulement les dépendances
docker-compose up -d mongodb redis auth-microservice jlc-api

# Puis démarrer le frontend localement
cd apps/web
yarn dev
```

### Développement Backend uniquement
```bash
# Démarrer seulement MongoDB et Redis
docker-compose up -d mongodb redis

# Puis démarrer les services localement
cd auth-microservice
uvicorn main:app --reload --port 8000

cd apps/api
uvicorn server:app --reload --port 8001
```

### Réinitialiser complètement
```bash
# Tout supprimer
docker-compose down -v
docker system prune -a
docker volume prune

# Redémarrer
docker-compose up -d --build
```

---

## ✅ Checklist Post-Installation

- [ ] Docker installé et daemon actif
- [ ] Services démarrés sans erreur
- [ ] Frontend accessible sur http://localhost:5173
- [ ] API accessible sur http://localhost:8001/docs
- [ ] Mailhog accessible sur http://localhost:8025
- [ ] Logs s'affichent correctement
- [ ] MongoDB connecté (vérifier les logs)
- [ ] Redis actif (vérifier les logs)

---

## 🆘 Besoin d'aide?

1. Consulter `DOCKER_GUIDE.md` pour la documentation complète
2. Vérifier les logs: `docker-compose logs`
3. Vérifier le statut: `docker-compose ps`
4. Contacter l'équipe technique

---

**Version**: 1.0.0  
**Dernière mise à jour**: Novembre 2025
