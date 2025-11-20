# Troubleshooting: 503 Service Unavailable sur /api/besoins

## Symptôme
```
GET https://dev-stabilizer.preview.emergentagent.com/api/besoins?page=1&page_size=12 
503 (Service Unavailable)
```

## Vérifications Effectuées

### 1. Services Backend ✅
- ✅ auth-microservice: RUNNING (uptime 52 min)
- ✅ backend: RUNNING (uptime 10 min)
- ✅ `curl http://localhost:8001/health` → 200 OK

### 2. Tests Locaux ✅
- ✅ Via backend (8001): 200 OK
- ✅ Via frontend (3000): 200 OK
- ✅ Temps de réponse: 0.031s (très rapide)

### 3. Logs Backend ✅
- ✅ Requêtes httpx vers auth-microservice: 200 OK
- ✅ Redirections 307 suivies correctement
- ✅ Pas d'erreur 503 dans les logs

## Causes Possibles

### A. Environnement Preview "Sleeping"
L'erreur 503 pourrait survenir quand:
- L'environnement Emergent est en mode "sleep"
- Les services se réveillent (premier appel peut échouer)
- **Solution**: Réessayer après quelques secondes

### B. Kubernetes Ingress Routing
Le problème pourrait être au niveau du routing Kubernetes:
```
Browser → Ingress → ???
                    ↓
              Backend (8001) ?
```

**Points à vérifier**:
1. L'ingress route-t-il `/api/*` vers le bon service?
2. Le backend est-il exposé sur le bon port?
3. Y a-t-il un timeout trop court au niveau ingress?

### C. Timeout Configuration
Si le backend prend trop de temps à répondre en production:
- Timeout ingress: généralement 30-60s
- Timeout Vite proxy: 30s (configuré)
- Timeout httpx: 30s (configuré)

### D. CORS ou Security Headers
Une réponse 503 au lieu de 404 ou 403 pourrait indiquer:
- Un problème de proxy en amont
- Un middleware de sécurité qui bloque

## Tests à Effectuer en Production

### Test 1: Vérifier si le Backend est Accessible
```bash
# Depuis le navigateur (DevTools Console)
fetch('https://dev-stabilizer.preview.emergentagent.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

**Résultat attendu**: `{status: "healthy", service: "jlc-api", version: "1.0.0"}`

### Test 2: Tester l'Authentification
```bash
# Login
fetch('https://dev-stabilizer.preview.emergentagent.com/api/auth/local/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'entreprise_test', password: 'Entreprise2025!'})
})
.then(r => r.json())
.then(data => {
  console.log('Token:', data.access_token);
  localStorage.setItem('access_token', data.access_token);
})
```

### Test 3: Tester /api/besoins avec Token
```bash
# Utiliser le token du test précédent
const token = localStorage.getItem('access_token');
fetch('https://dev-stabilizer.preview.emergentagent.com/api/besoins?page=1&page_size=12', {
  headers: {'Authorization': `Bearer ${token}`}
})
.then(r => {
  console.log('Status:', r.status);
  return r.json();
})
.then(console.log)
.catch(console.error)
```

**Si 503**: Le problème est au niveau du routing Kubernetes/Ingress
**Si 200**: Le problème était temporaire (sleep mode)

## Solutions Possibles

### Solution 1: Augmenter les Timeouts
Si le problème est lié aux timeouts, modifier:

**Backend proxy** (`besoins_proxy_routes.py`):
```python
async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
```

**Vite config** (moins probable, car déjà 30s par défaut):
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    timeout: 60000,  // 60 secondes
  }
}
```

### Solution 2: Vérifier la Configuration Kubernetes
S'assurer que l'ingress route correctement:
```yaml
# Configuration attendue
- path: /api/*
  backend:
    serviceName: backend
    servicePort: 8001
```

### Solution 3: Health Check
Ajouter un endpoint de health check spécifique pour Kubernetes:
```python
@app.get("/api/health")
async def api_health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}
```

## Monitoring

Pour diagnostiquer en temps réel:

1. **Logs Backend**:
   ```bash
   tail -f /var/log/supervisor/backend.err.log | grep "besoin"
   ```

2. **Logs Auth-Microservice**:
   ```bash
   tail -f /var/log/supervisor/auth-microservice.err.log | grep "besoin"
   ```

3. **Network Tab** (Browser DevTools):
   - Timing de la requête
   - Headers de réponse
   - Message d'erreur exact

## Prochaines Étapes

1. ✅ Code backend/frontend: **OK**
2. ⚠️ Tests en production: **À FAIRE**
3. ❓ Configuration Kubernetes: **À VÉRIFIER**

---

**Note**: Les tests locaux (localhost) fonctionnent parfaitement. Le problème semble spécifique à l'environnement de production/preview Emergent.
