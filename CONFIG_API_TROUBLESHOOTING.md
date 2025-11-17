# Config API Troubleshooting Guide

## ✅ Configuration Actuelle (VALIDÉE)

### Architecture
```
Frontend (3001) → Vite Proxy → Backend (8001) → Config Proxy → Auth Microservice (8000)
```

### Endpoints
- **Frontend URL**: `http://localhost:3001/api/config/app/value?key=xxx`
- **Backend Central**: `http://localhost:8001/api/config/app/value?key=xxx`
- **Auth Microservice**: `http://localhost:8000/api/config/app/value?key=xxx`

### Tests de Validation
```bash
# 1. Auth Microservice (8000) ✅
curl "http://localhost:8000/api/config/app/value?key=profiles.badge_new_user"
# → 200 OK avec {"value": {...}}

# 2. Backend Central (8001) ✅
curl "http://localhost:8001/api/config/app/value?key=profiles.badge_new_user"
# → 200 OK avec {"value": {...}}

# 3. Frontend via Vite Proxy (3001) ✅
curl "http://localhost:3001/api/config/app/value?key=profiles.badge_new_user"
# → 200 OK avec {"value": {...}}
```

---

## 📁 Fichiers Impliqués

### 1. Route Backend (Auth Microservice)
**Fichier**: `/app/auth-microservice/app_config_routes.py`
```python
# Ligne 13
router = APIRouter(prefix="/config/app", tags=["App Configuration"])

# Ligne 52-69
@router.get("/value")
async def get_config_value(
    key: str = Query(..., description="Configuration key"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get configuration value directly (without metadata)"""
    service = ConfigService(db)
    value = await service.get_config_value(key)
    
    if value is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"value": value}
```

### 2. Montage dans Auth Microservice
**Fichier**: `/app/auth-microservice/main.py`
```python
# Ligne 53
from app_config_routes import router as app_config_router

# Ligne 176
app.include_router(app_config_router, prefix="/api", tags=["App Configuration"])
```

**Route Finale**: `/api` + `/config/app` + `/value` = `/api/config/app/value`

### 3. Proxy Backend Central
**Fichier**: `/app/apps/api/src/presentation/routes/config_proxy_routes.py`
```python
# Ligne 15
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8000')

# Ligne 115-118
@router.api_route("/app/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def proxy_config_app_with_path(path: str, request: Request):
    """Proxy all /api/config/app/* requests to auth-microservice"""
    return await proxy_config_request(f"app/{path}", request)
```

**Fichier**: `/app/apps/api/server.py`
```python
# Ligne 103
app.include_router(config_proxy_routes.router, prefix="/api/config", tags=["Config Proxy"])
```

**Proxy Flow**:
1. Reçoit: `/api/config/app/value`
2. Matche avec prefix `/api/config` → reste `/app/value`
3. Route `/app/{path}` matche → `path = "value"`
4. Envoie à: `http://localhost:8000/api/config/app/value`

### 4. Proxy Frontend (Vite)
**Fichier**: `/app/apps/web/vite.config.ts`
```typescript
// Ligne 28-39
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
    secure: false,
    ws: true,
    agent: new http.Agent({ keepAlive: true }),
  }
}
```

### 5. RTK Query Base URL
**Fichier**: `/app/apps/web/src/utils/baseQueryWithAuth.ts`
```typescript
// Ligne 62-80
const getBaseUrl = () => {
  if (typeof window === 'undefined') return '/api'
  
  const isHTTPS = window.location.protocol === 'https:'
  const hostname = window.location.hostname
  const isEmergentPreview = hostname.includes('preview.emergentagent.com') || hostname.includes('emergent.host')
  
  if (isHTTPS && isEmergentPreview) {
    const httpsBaseUrl = `https://${hostname}/api`
    return httpsBaseUrl
  }
  
  return '/api'
}
```

---

## 🔍 Diagnostics

### Vérifier les Services
```bash
# 1. Status des services
sudo supervisorctl status | grep -E "backend|auth"

# 2. Logs auth-microservice
tail -f /var/log/supervisor/auth-microservice.err.log

# 3. Logs backend central
tail -f /var/log/supervisor/backend.err.log

# 4. Logs frontend
tail -f /var/log/supervisor/frontend.err.log
```

### Vérifier les Variables ENV
```bash
# Backend central
cat /app/apps/api/.env | grep AUTH_SERVICE_URL
# → AUTH_SERVICE_URL=http://localhost:8000

# Frontend
cat /app/apps/web/.env | grep VITE
# → VITE_BACKEND_URL= (vide car proxy Vite)
```

### Tester la Chaîne Complète
```bash
# 1. Test direct auth-microservice
curl "http://localhost:8000/api/config/app/value?key=test.key"

# 2. Test backend proxy
curl "http://localhost:8001/api/config/app/value?key=test.key"

# 3. Test frontend proxy (Vite)
curl "http://localhost:3001/api/config/app/value?key=test.key"
```

---

## ⚠️ Erreurs Communes

### 1. 404 Not Found
**Causes possibles**:
- Service auth-microservice DOWN
- Mauvais préfixe dans URL
- Route non montée dans main.py
- Proxy mal configuré

**Vérifications**:
```bash
# Service UP ?
sudo supervisorctl status auth-microservice

# Route existe ?
curl http://localhost:8000/api/config/app/value?key=test

# Proxy configuré ?
grep -A 10 "config_proxy_routes" /app/apps/api/server.py
```

### 2. 502 Bad Gateway
**Causes possibles**:
- Auth-microservice non accessible depuis backend
- Variable AUTH_SERVICE_URL incorrecte
- Port 8000 fermé

**Vérifications**:
```bash
# Backend peut atteindre auth-microservice ?
docker exec -it backend curl http://localhost:8000/health

# Variable ENV correcte ?
docker exec -it backend env | grep AUTH_SERVICE_URL
```

### 3. Double /api/api/
**Cause**: baseUrl RTK Query inclut `/api` ET endpoint aussi

**Solution**: Les endpoints RTK Query ne doivent PAS inclure `/api`
```typescript
// ❌ INCORRECT
endpoint: '/api/config/app/value'

// ✅ CORRECT
endpoint: '/config/app/value'
```

### 4. Mixed Content (HTTPS → HTTP)
**Cause**: Emergent Preview est en HTTPS mais appelle HTTP

**Solution**: Déjà géré dans `baseQueryWithAuth.ts` (lignes 27-59)
- Détecte automatiquement Emergent Preview
- Force HTTPS pour baseUrl

---

## 🔧 Corrections Courantes

### Redémarrer les Services
```bash
# Redémarrer auth-microservice
sudo supervisorctl restart auth-microservice

# Redémarrer backend central
sudo supervisorctl restart backend

# Redémarrer frontend (si changements .env)
sudo supervisorctl restart frontend
```

### Clear Cache Navigateur
```javascript
// Dans la console du navigateur
localStorage.clear()
sessionStorage.clear()
location.reload(true)
```

### Vérifier Ordre de Montage des Routes
**Important**: Dans `server.py`, les proxies génériques doivent être montés AVANT les routes locales spécifiques.

```python
# ✅ CORRECT (dans server.py)
# Ligne 92: Proxy générique pour auth endpoints
app.include_router(auth_endpoints_proxy.router, prefix="/api", tags=["Auth Endpoints Proxy"])

# Ligne 103: Proxy config (spécifique)
app.include_router(config_proxy_routes.router, prefix="/api/config", tags=["Config Proxy"])

# Lignes suivantes: Routes locales
```

---

## 📝 Checklist de Validation

- [ ] Services UP (auth-microservice, backend, frontend)
- [ ] AUTH_SERVICE_URL correcte (`http://localhost:8000`)
- [ ] Route `/api/config/app/value` répond sur port 8000
- [ ] Proxy backend (`config_proxy_routes`) configuré
- [ ] Proxy backend monté avec prefix `/api/config` dans server.py
- [ ] Proxy Vite configuré (`/api → http://localhost:8001`)
- [ ] RTK Query utilise baseUrl `/api` (relatif)
- [ ] Pas de double `/api/api/` dans les URLs
- [ ] Tests curl passent sur les 3 ports (8000, 8001, 3001)

---

## 🎯 Résumé

**Configuration Actuelle** : ✅ **FONCTIONNELLE**

Tous les tests curl passent :
- Auth Microservice (8000) ✅
- Backend Central (8001) ✅
- Frontend Vite Proxy (3001) ✅

Si une erreur 404 apparaît :
1. Vérifier que les services sont UP
2. Tester la chaîne avec curl (3 ports)
3. Vérifier cache navigateur
4. Consulter les logs des services

**Aucune modification nécessaire** - La configuration est correcte.
