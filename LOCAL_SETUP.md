# 🖥️ Configuration Développement Local

## Problèmes Courants et Solutions

### Erreur: `ERR_CONNECTION_REFUSED` sur https://127.0.0.1

**Symptôme:**
```
GET https://127.0.0.1/ net::ERR_CONNECTION_REFUSED
```

**Cause:** Configuration HMR (Hot Module Reload) de Vite configurée pour le déploiement cloud (WSS).

**Solution:**

1. **Vérifier que `vite.config.ts` est correctement configuré**

Le fichier doit contenir:
```typescript
hmr: {
  ...(process.env.NODE_ENV === 'production' && {
    clientPort: 443,
    protocol: 'wss',
  }),
},
```

2. **Vider le cache du navigateur**
```bash
# Chrome/Edge: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Del
# Ou en dur reload: Ctrl+Shift+R
```

3. **Redémarrer le frontend**
```bash
sudo supervisorctl restart frontend
# Attendre 5-10 secondes
```

---

### Erreur: 500 Internal Server Error sur `/auth-api/auth/local/login`

**Symptôme:**
```
POST http://127.0.0.1:5173/auth-api/auth/local/login 500 (Internal Server Error)
```

**Solutions:**

#### 1. Vérifier que les services backend tournent

```bash
# Vérifier le statut
sudo supervisorctl status

# Les services doivent être RUNNING:
# - auth-microservice
# - backend
# - mongodb
```

#### 2. Vérifier les logs backend

```bash
# Logs auth-microservice
tail -f /var/log/supervisor/auth-microservice.err.log

# Logs backend
tail -f /var/log/supervisor/backend.err.log
```

#### 3. Tester directement l'API

```bash
# Test auth service
curl http://localhost:8000/health

# Test login direct
curl -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"awana2025"}'
```

#### 4. Vérifier MongoDB

```bash
# Statut MongoDB
sudo systemctl status mongodb

# Démarrer si nécessaire
sudo systemctl start mongodb

# Test connexion
mongosh --eval "db.runCommand({ping: 1})"
```

#### 5. Redémarrer tous les services

```bash
sudo supervisorctl restart all
```

---

### Configuration Frontend (.env)

Le fichier `/app/apps/web/.env` doit contenir:

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_AUTH_SERVICE_URL=http://localhost:8000
```

**⚠️ Important:** Pas de variables avec des URLs externes en local !

---

### Configuration Vite (vite.config.ts)

Pour le développement local, le proxy doit pointer vers:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',  // ← Backend principal
    changeOrigin: true,
    secure: false,
  },
  '/auth-api': {
    target: 'http://localhost:8000',  // ← Auth service
    changeOrigin: true,
    secure: false,
    rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
  },
}
```

---

### Ports Utilisés

Assurez-vous qu'aucun autre processus n'utilise ces ports:

| Service | Port | Commande Test |
|---------|------|---------------|
| Frontend | 3000 | `lsof -i :3000` |
| Auth | 8000 | `lsof -i :8000` |
| Backend | 8001 | `lsof -i :8001` |
| MongoDB | 27017 | `lsof -i :27017` |

**Tuer un processus si nécessaire:**
```bash
# Trouver le PID
lsof -i :3000

# Tuer le processus
kill -9 <PID>
```

---

## Checklist de Démarrage

### ✅ Avant de démarrer

1. **MongoDB**
```bash
sudo systemctl status mongodb
# Si non actif:
sudo systemctl start mongodb
```

2. **Variables d'environnement**
```bash
# Vérifier .env
cat /app/apps/web/.env
cat /app/auth-microservice/.env
```

3. **Ports libres**
```bash
lsof -i :3000,8000,8001,27017
# Doit être vide ou montrer les bons services
```

### ✅ Démarrer les services

```bash
# Option 1: Supervisor
sudo supervisorctl start all
sudo supervisorctl status

# Option 2: Manuel (pour debug)
# Terminal 1: MongoDB
mongod --dbpath /data/db

# Terminal 2: Auth service
cd /app/auth-microservice
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Backend
cd /app/apps/api
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 4: Frontend
cd /app/apps/web
yarn dev
```

### ✅ Vérifier que tout fonctionne

```bash
# 1. Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health

# 2. Frontend accessible
curl http://localhost:3000

# 3. Login test
curl -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"awana2025"}'
```

### ✅ Accéder à l'application

Ouvrir dans le navigateur:
- **Frontend**: http://localhost:3000
- **API Docs Auth**: http://localhost:8000/docs
- **API Docs Backend**: http://localhost:8001/docs

---

## Troubleshooting Avancé

### Frontend ne charge pas

```bash
# 1. Vider le cache Vite
rm -rf /app/apps/web/node_modules/.vite

# 2. Réinstaller les dépendances
cd /app/apps/web
rm -rf node_modules
yarn install

# 3. Redémarrer
sudo supervisorctl restart frontend
```

### Erreur de proxy Vite

```bash
# 1. Vérifier que les backends sont accessibles
curl http://localhost:8000/health
curl http://localhost:8001/health

# 2. Vérifier la config Vite
cat /app/apps/web/vite.config.ts

# 3. Tester sans proxy
# Modifier temporairement le code pour appeler directement:
# http://localhost:8000/api/... au lieu de /auth-api/...
```

### CORS Errors

Si vous voyez des erreurs CORS:

```bash
# 1. Vérifier la config CORS du backend
# auth-microservice/main.py doit avoir:
allow_origins=["http://localhost:3000", ...]

# 2. Redémarrer les services backend
sudo supervisorctl restart auth-microservice backend
```

### Base de données vide

```bash
# 1. Vérifier les collections
mongosh auth_db --eval "db.getCollectionNames()"

# 2. Créer un super admin
./create-admin.sh

# 3. Vérifier
mongosh auth_db --eval "db.users.countDocuments()"
```

---

## Scripts Utiles

### Redémarrer tout
```bash
#!/bin/bash
sudo supervisorctl restart all
echo "Attente du démarrage..."
sleep 5
sudo supervisorctl status
echo "Services redémarrés!"
```

### Nettoyer et redémarrer
```bash
#!/bin/bash
# Arrêter
sudo supervisorctl stop all

# Nettoyer
rm -rf /app/apps/web/node_modules/.vite
rm -rf /app/apps/web/dist

# Redémarrer
sudo supervisorctl start all
echo "Nettoyage et redémarrage terminés!"
```

### Vérifier la santé
```bash
#!/bin/bash
echo "🔍 Vérification de la santé des services..."
echo ""

# MongoDB
echo -n "MongoDB: "
mongosh --quiet --eval "db.runCommand({ping: 1}).ok" && echo "✅" || echo "❌"

# Auth Service
echo -n "Auth Service: "
curl -s http://localhost:8000/health > /dev/null && echo "✅" || echo "❌"

# Backend
echo -n "Backend: "
curl -s http://localhost:8001/health > /dev/null && echo "✅" || echo "❌"

# Frontend
echo -n "Frontend: "
curl -s http://localhost:3000 > /dev/null && echo "✅" || echo "❌"

echo ""
echo "Statut Supervisor:"
sudo supervisorctl status
```

---

## Variables d'Environnement

### Frontend (apps/web/.env)
```env
VITE_API_BASE_URL=http://localhost:8001
VITE_AUTH_SERVICE_URL=http://localhost:8000
NODE_ENV=development
```

### Auth Service (auth-microservice/.env)
```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=auth_db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
JWT_SECRET=your-secret-key
ENVIRONMENT=local
```

### Backend (apps/api/.env)
```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=jlc_db
AUTH_SERVICE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ENVIRONMENT=local
```

---

## Support

Si les problèmes persistent:

1. **Vérifier les logs**
```bash
tail -f /var/log/supervisor/*.log
```

2. **Consulter la documentation**
- `DOCKER_GUIDE.md` - Pour Docker
- `ADMIN_SETUP.md` - Pour créer un admin
- `/docs` - Documentation complète

3. **Ouvrir une issue**
Fournir:
- Logs complets
- Commandes exécutées
- Configuration (.env, vite.config.ts)
- Capture d'écran des erreurs

---

**Version**: 1.0.0  
**Dernière mise à jour**: Novembre 2025
