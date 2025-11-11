# Changelog Complet - Résolution des Problèmes 403/503

## Date: 11 Novembre 2025

## Résumé Exécutif

Application JLC Group - Système de gestion d'intérim avec architecture microservices.

**Problèmes résolus:**
1. ✅ Erreur 403 Forbidden sur endpoints de configuration
2. ✅ Erreur ERR_SSL_PROTOCOL_ERROR (localhost:8000)
3. ✅ Erreur 404 sur routes /auth-api/*
4. ✅ Erreur 503 Service Unavailable sur /api/besoins

---

## Architecture Finale

### Stack Technologique
- **Frontend:** React 18 + TypeScript + Vite + Redux Toolkit (RTK Query)
- **Backend:** FastAPI (Python) - Gateway API (port 8001)
- **Auth-Microservice:** FastAPI (Python) - Service d'authentification (port 8000)
- **Base de données:** MongoDB
- **Reverse Proxy:** Nginx (ports 80 et 3000)

### Flux des Requêtes

```
┌─────────────────────────────────────────────┐
│  Client (Browser/App)                        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Nginx (ports 80 + 3000)                    │
│  ┌─────────────────────────────────────┐   │
│  │ /api/*      → Backend (8001)        │   │
│  │ /auth-api/* → Backend (8001)        │   │
│  │ /*          → Frontend Vite (3001)  │   │
│  └─────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   Backend    │      │   Frontend   │
│   (8001)     │      │   Vite       │
│   FastAPI    │      │   (3001)     │
└──────┬───────┘      └──────────────┘
       │
       │ Proxy vers
       ▼
┌──────────────┐
│ Auth-Micro   │
│ service      │
│ (8000)       │
│ FastAPI      │
└──────────────┘
       │
       │
       ▼
┌──────────────┐
│   MongoDB    │
│   (27017)    │
└──────────────┘
```

---

## Problème 1: Erreur 403 Forbidden

### Symptôme
```
GET /api/config/workflows/besoin → 403 Forbidden
```

### Cause
Utilisateurs avaient des rôles (`company`, `interim`, etc.) mais **aucun profil IAM assigné** (`profile_ids: []`). Sans profil, pas de permissions.

### Solution

**1. Scripts de Migration Créés:**
- `/app/auth-microservice/scripts/assign_profiles_to_users.py`
- `/app/auth-microservice/scripts/init_test_users_profiles.py`

**2. Mapping Rôles → Profils:**
```python
ROLE_TO_PROFILE_MAPPING = {
    'admin': 'admin',
    'super_admin': 'super_admin',
    'company': 'entreprise',
    'interim': 'interim_user',
    'commercial': 'commercial',
    'agency': 'company_admin',
}
```

**3. Modification Auto-Assignment:**
- Fichier: `/app/auth-microservice/security_routes.py`
- Lors de la création d'utilisateur, assigne automatiquement les profils basés sur les rôles

**4. Permission config.read:**
- Ajoutée dans `iam_constants.py`
- Assignée aux profils `entreprise` et `company_admin`

### Fichiers Modifiés
- `/app/auth-microservice/awana_auth/core/iam_constants.py`
- `/app/auth-microservice/security_routes.py`
- Scripts créés dans `/app/auth-microservice/scripts/`

---

## Problème 2: ERR_SSL_PROTOCOL_ERROR

### Symptôme
```
GET https://localhost:8000/api/besoins → net::ERR_SSL_PROTOCOL_ERROR
```

### Cause
Configuration Vite proxy trop spécifique avec routes directes vers auth-microservice (port 8000), causant des conflits HTTPS/HTTP.

### Solution

**Simplification du Proxy Vite:**

**Avant:**
```typescript
proxy: {
  '/api/iam': { target: 'http://localhost:8000' },
  '/api/auth': { target: 'http://localhost:8000' },
  '/api/config': { target: 'http://localhost:8000' },
  '/api/besoins': { target: 'http://localhost:8000' },
  '/api': { target: 'http://localhost:8001' },
}
```

**Après:**
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',  // Tout via backend
    changeOrigin: true,
    secure: false,
  },
  '/auth-api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
    secure: false,
  },
}
```

**Ajout Proxy Backend:**
- Créé `/app/apps/api/src/presentation/routes/auth_proxy_routes.py`
- Enregistré dans `server.py`

### Fichiers Modifiés
- `/app/apps/web/vite.config.ts`
- `/app/apps/api/src/presentation/routes/auth_proxy_routes.py` (créé)
- `/app/apps/api/server.py`

---

## Problème 3: Erreur 404 sur /auth-api/*

### Symptôme
```
GET /auth-api/auth/me → 404 Not Found
GET /auth-api/iam/users/{id}/permissions → 404
```

### Cause
Proxy Vite ne routait que `/api/*`, pas `/auth-api/*`.

### Solution
Ajouté le proxy `/auth-api` dans `vite.config.ts` (voir solution Problème 2).

### Fichiers Modifiés
- `/app/apps/web/vite.config.ts`

---

## Problème 4: Erreur 503 Service Unavailable

### Symptôme
```
GET /api/besoins → 503 Service Unavailable
Error: [SSL: WRONG_VERSION_NUMBER]
```

### Cause Racine
Headers `X-Forwarded-Proto: https` transmis par nginx au backend, puis au proxy httpx, qui essayait ensuite d'utiliser HTTPS pour contacter auth-microservice (port 8000 en HTTP).

### Solution

**1. Configuration Nginx Reverse Proxy:**

Créé `/etc/nginx/sites-available/jlc-app`:
```nginx
server {
    listen 80;
    listen 3000;  # Port exposé par Emergent
    
    # API → Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        # Headers, CORS, timeouts...
    }
    
    # Frontend → Vite
    location / {
        proxy_pass http://127.0.0.1:3001;
        # WebSocket support for HMR
    }
}
```

**2. Frontend déplacé sur port 3001:**
- Créé script: `/app/apps/web/start-frontend.sh`
- Supervisord: `frontend-custom` service

**3. Suppression Headers X-Forwarded dans TOUS les proxies backend:**

Dans tous les fichiers `*_proxy_routes.py`:
```python
headers.pop("x-forwarded-proto", None)
headers.pop("x-forwarded-for", None)
headers.pop("x-forwarded-host", None)
```

**4. Ajout follow_redirects dans httpx:**
```python
async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
```

### Fichiers Modifiés
- `/etc/nginx/sites-available/jlc-app` (créé)
- `/etc/supervisor/conf.d/nginx-app.conf` (créé)
- `/etc/supervisor/conf.d/frontend-custom.conf` (créé)
- `/app/apps/web/start-frontend.sh` (créé)
- `/app/apps/web/vite.config.ts` (port changé à 3001)
- Tous les fichiers `/app/apps/api/src/presentation/routes/*_proxy_routes.py`:
  - `auth_proxy_routes.py`
  - `auth_api_proxy_routes.py`
  - `besoins_proxy_routes.py`
  - `config_proxy_routes.py`
  - `iam_proxy_routes.py`
  - `security_proxy_routes.py`

---

## Changements Additionnels

### Backend Health Endpoint
Ajouté endpoint `/api/health` dans `/app/apps/api/server.py` pour monitoring.

### Base URL Query
Modifié `/app/apps/web/src/utils/baseQueryWithAuth.ts` pour utiliser `undefined` (URLs relatives).

---

## Variables d'Environnement Critiques

### Backend (.env)
```bash
AUTH_SERVICE_URL=http://localhost:8000
MONGO_URL=mongodb://localhost:27017
```

### Frontend (.env)
```bash
# Vides pour forcer les URLs relatives
VITE_BACKEND_URL=
VITE_API_BASE_URL=
```

### Important
- ❌ Ne jamais hardcoder `localhost:8000` ou `localhost:8001`
- ✅ Toujours utiliser les variables d'environnement
- ✅ Les proxies backend utilisent HTTP en interne
- ✅ Nginx gère le HTTPS/HTTP pour l'externe

---

## Tests de Validation

### En Local
```bash
✅ curl http://localhost:3000/api/health
✅ curl http://localhost:3000/api/auth/local/login
✅ curl http://localhost:3000/api/besoins
✅ curl http://localhost:3000/
```

### En Production
```bash
✅ GET https://preview.emergentagent.com/api/health → 200
✅ POST https://preview.emergentagent.com/api/auth/local/login → 200
✅ GET https://preview.emergentagent.com/api/besoins → 200
```

---

## Services Supervisord

```ini
[program:nginx-app]
command=/usr/sbin/nginx -g "daemon off;" -c /etc/nginx/nginx.conf
priority=10

[program:backend]
command=uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
priority=20

[program:auth-microservice]
command=uvicorn main:app --host 0.0.0.0 --port 8000
directory=/app/auth-microservice
priority=20

[program:frontend-custom]
command=/app/apps/web/start-frontend.sh
directory=/app/apps/web
priority=30

[program:mongodb]
command=/usr/bin/mongod --bind_ip_all
priority=5
```

---

## Commandes Utiles

### Redémarrer les services
```bash
sudo supervisorctl restart all
sudo supervisorctl restart nginx-app
sudo supervisorctl restart backend
sudo supervisorctl restart frontend-custom
```

### Vérifier les logs
```bash
tail -f /var/log/supervisor/nginx-app.err.log
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend-custom.out.log
```

### Vérifier l'état
```bash
sudo supervisorctl status
netstat -tlnp | grep -E "80|3000|3001|8000|8001"
```

---

## Points d'Attention pour Production

1. **Nginx est OBLIGATOIRE** - Point d'entrée unique pour le routing
2. **Headers X-Forwarded supprimés** - Critiques pour éviter SSL errors
3. **Ports internes:** Backend (8001), Auth (8000), Frontend (3001)
4. **Port externe:** 80 ou 3000 (selon plateforme)
5. **Variables d'environnement** - Jamais de hardcoding
6. **MongoDB:** Utiliser MONGO_URL de l'environnement
7. **Timeouts:** 30-60 secondes configurés partout

---

**Documentation complète:** Voir guides de déploiement spécifiques
- `DEPLOIEMENT_DOCKER.md`
- `DEPLOIEMENT_WEBAPP.md`
