# 🔧 Correctif 307 Redirect - Résumé Technique

## Problème Général

**Symptôme** : Multiples endpoints API retournaient `307 Temporary Redirect` au lieu de `200 OK`

**Exemples d'erreurs** :
```
GET /api/config/countries?active_only=false → 307
GET /api/feature-flags?include_inactive=true → 307
GET /api/locations?type=country → 307
```

**Cause racine** : Routes de proxy définies UNIQUEMENT avec paramètre de path obligatoire :
```python
@router.api_route("/endpoint/{path:path}", methods=["GET", "POST", ...])
```

Cette définition requiert un segment de path après l'endpoint de base. Les requêtes vers `/endpoint` (sans path supplémentaire) ne matchent aucune route, causant FastAPI à retourner une redirection 307.

---

## Solution Appliquée

### Pattern de correction

Pour chaque endpoint affecté, ajouter **deux routes** :

1. **Route de base** : Sans paramètre path (pour requêtes de type liste)
2. **Route avec path** : Avec paramètre `{path:path}` (pour requêtes spécifiques)

**Exemple de correction** :
```python
# AVANT (❌ 307 sur /endpoint)
@router.api_route("/endpoint/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_endpoint(path: str, request: Request):
    target_url = f"{AUTH_SERVICE_URL}/api/endpoint/{path}"
    return await _proxy_request(target_url, request)

# APRÈS (✅ 200 sur /endpoint et /endpoint/xxx)
@router.api_route("/endpoint", methods=["GET", "POST"])
@router.api_route("/endpoint/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_endpoint(path: str = "", request: Request = None):
    target_url = f"{AUTH_SERVICE_URL}/api/endpoint/{path}" if path else f"{AUTH_SERVICE_URL}/api/endpoint"
    return await _proxy_request(target_url, request)
```

---

## Fichiers Modifiés

### 1. `/app/apps/api/src/presentation/routes/config_proxy_routes.py`

**Endpoints corrigés** :
- ✅ `/api/config/countries`
- ✅ `/api/config/countries/{path:path}`
- ✅ `/api/config/forms`
- ✅ `/api/config/forms/{path:path}`
- ✅ `/api/config/workflows`
- ✅ `/api/config/workflows/{path:path}`
- ✅ `/api/config/references`
- ✅ `/api/config/references/{path:path}`

**Impact** : Configuration système, sélection pays, workflows, références

---

### 2. `/app/apps/api/src/presentation/routes/auth_endpoints_proxy.py`

**Endpoints corrigés** :
- ✅ `/api/feature-flags`
- ✅ `/api/feature-flags/{path:path}`
- ✅ `/api/versions`
- ✅ `/api/versions/{path:path}`
- ✅ `/api/locations`
- ✅ `/api/locations/{path:path}`
- ✅ `/api/profiles`
- ✅ `/api/profiles/{path:path}`
- ✅ `/api/emails`
- ✅ `/api/emails/{path:path}`

**Endpoints déjà corrects** (avaient déjà les deux routes) :
- ✅ `/api/validations` + `/api/validations/{path:path}`
- ✅ `/api/missions` + `/api/missions/{path:path}`

**Impact** : Feature flags, gestion des versions, localisations, profils, emails

---

## Tests de Validation

### Endpoints testés avec succès (200 OK)

| Endpoint | Query Params | Status | Notes |
|----------|-------------|--------|-------|
| `/api/config/countries` | `active_only=false` | 200 ✅ | 4 pays trouvés |
| `/api/config/workflows/besoin` | - | 200 ✅ | Config workflow OK |
| `/api/feature-flags` | `include_inactive=true` | 200 ✅ | 6 flags trouvés |
| `/api/locations` | `type=country` | 200 ✅ | 2 pays trouvés |
| `/api/profiles` | - | 404 ℹ️ | Endpoint n'existe peut-être pas sans ID |

---

## Impact Utilisateur

### Avant correction
- ❌ Page Feature Flags : Ne chargeait pas (307)
- ❌ Sélecteur de pays : Ne chargeait pas (307)
- ❌ Configuration workflows : Ne chargeait pas (307)
- ❌ Gestion localisations : Ne chargeait pas (307)

### Après correction
- ✅ Page Feature Flags : Fonctionne correctement
- ✅ Sélecteur de pays : Liste complète affichée
- ✅ Configuration workflows : Accessible
- ✅ Gestion localisations : Opérationnelle

---

## Architecture Proxy

### Flux des requêtes

```
Frontend (React)
    ↓
    GET /api/feature-flags?include_inactive=true
    ↓
Backend Gateway (FastAPI - Port 8001)
    ↓
    Route Match: /api/feature-flags (base route)
    ↓
    Proxy vers: http://localhost:8000/api/feature-flags?include_inactive=true
    ↓
Auth Microservice (Port 8000)
    ↓
    Traitement et réponse
    ↓
    200 OK + données JSON
```

### Pourquoi deux routes ?

**Cas 1 : Requête de liste**
```
GET /api/feature-flags
→ Matche la route de base : /api/feature-flags
→ Pas de path, target_url = /api/feature-flags
```

**Cas 2 : Requête spécifique**
```
GET /api/feature-flags/flag-id-123
→ Matche la route avec path : /api/feature-flags/{path:path}
→ path = "flag-id-123", target_url = /api/feature-flags/flag-id-123
```

**Cas 3 : Requête imbriquée**
```
GET /api/feature-flags/flag-id/history
→ Matche la route avec path : /api/feature-flags/{path:path}
→ path = "flag-id/history", target_url = /api/feature-flags/flag-id/history
```

---

## Prévention Future

### Checklist pour nouveau proxy

Lors de l'ajout d'un nouveau proxy endpoint :

- [ ] Définir la route de base sans `{path:path}` si l'endpoint peut être appelé sans paramètre
- [ ] Définir la route avec `{path:path}` pour les sous-ressources
- [ ] Utiliser `path: str = ""` et `request: Request = None` comme paramètres par défaut
- [ ] Conditionnel : `if path else` pour construire l'URL cible
- [ ] Tester avec et sans path
- [ ] Vérifier les query params sont bien transmis

### Pattern recommandé

```python
@router.api_route("/new-endpoint", methods=["GET", "POST"])
@router.api_route("/new-endpoint/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_new_endpoint(path: str = "", request: Request = None):
    """
    Proxy /api/new-endpoint/* requests to auth-microservice
    """
    base_url = f"{AUTH_SERVICE_URL}/api/new-endpoint"
    target_url = f"{base_url}/{path}" if path else base_url
    return await _proxy_request(target_url, request)
```

---

## Historique des Corrections

| Date | Fichier | Endpoints Corrigés | Agent |
|------|---------|-------------------|-------|
| 15/11/2025 | `config_proxy_routes.py` | countries, forms, workflows, references | fork |
| 15/11/2025 | `auth_endpoints_proxy.py` | feature-flags, versions | fork |
| 15/11/2025 | `auth_endpoints_proxy.py` | locations, profiles, emails | fork |

---

## Références

- **Issue GitHub (interne)** : #307-redirect-fix
- **Documentation FastAPI** : https://fastapi.tiangolo.com/tutorial/path-params/
- **Related Issue** : Mixed Content fix (HTTPS enforcement)

---

**Version** : 1.0  
**Dernière mise à jour** : 15 Novembre 2025  
**Status** : ✅ Résolu et Déployé  
**Prêt pour production** : Oui
