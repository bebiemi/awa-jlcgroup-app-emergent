# Fix Mixed Content & CORS Issues - Production Guide

## Problème Identifié

En production HTTPS, les pages chargeaient avec des erreurs:
```
Mixed Content: The page at 'https://xxx.preview.emergentagent.com/admin/countries' 
was loaded over HTTPS, but requested an insecure resource 
'http://xxx.preview.emergentagent.com/api/config/countries/?active_only=false'. 
This request has been blocked; the content must be served over HTTPS.
```

Et aussi des erreurs CORS:
```
Access to fetch at 'http://localhost:8000/api/security/email-domains' 
from origin 'https://xxx.preview.emergentagent.com' has been blocked by CORS policy
```

## Cause Racine

**Problème 1**: Certaines APIs (comme `emailDomainsApi`) utilisaient un fallback vers `http://localhost:8000` au lieu d'URLs relatives
**Problème 2**: En production, seul le backend (port 8001) est exposé, pas l'auth-microservice (port 8000)
**Problème 3**: Les URLs relatives n'étaient pas correctement configurées

## Solution Appliquée

### 1. Configuration des Variables d'Environnement (.env)

**Avant:**
```env
VITE_API_BASE_URL=http://localhost:8001
```

**Après:**
```env
# Leave empty for production (uses relative URLs with same origin)
VITE_BACKEND_URL=
VITE_API_BASE_URL=
```

### 2. Création de Proxies Backend pour Production

Créé des routes proxy dans le backend principal (`/app/apps/api/server.py`) pour router les requêtes vers l'auth-microservice:

#### A. Proxy IAM (déjà existant)
- Route: `/api/iam/*` → auth-microservice:8000

#### B. Proxy Config (nouveau)
- Route: `/api/config/*` → auth-microservice:8000
- Fichier: `/app/apps/api/src/presentation/routes/config_proxy_routes.py`

#### C. Proxy Security (nouveau)
- Route: `/api/security/*` → auth-microservice:8000
- Fichier: `/app/apps/api/src/presentation/routes/security_proxy_routes.py`

### 3. Configuration Vite Proxy pour Développement

Ajout de règles proxy dans `/app/apps/web/vite.config.ts`:

```typescript
proxy: {
  '/api/iam': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  },
  '/api/auth': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  },
  '/api/config': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  },
  '/api/security': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  },
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
    secure: false,
  },
}
```

### 4. Correction des APIs Frontend

**Avant (emailDomainsApi.ts):**
```typescript
const baseUrl = import.meta.env.VITE_BACKEND_URL || 
                import.meta.env.REACT_APP_BACKEND_URL || 
                'http://localhost:8000'  // ❌ Problème!

export const emailDomainsApi = createApi({
  baseQuery: createBaseQueryWithAuth(baseUrl),
  ...
})
```

**Après:**
```typescript
import { baseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export const emailDomainsApi = createApi({
  baseQuery: baseQueryWithAuth,  // ✅ Utilise URLs relatives
  ...
})
```

## Architecture Finale

### Développement Local
```
Frontend (3000) → Vite Proxy → Auth-Microservice (8000)
                              → Backend (8001)
```

### Production HTTPS
```
Frontend (HTTPS) → Backend (8001) → Proxies → Auth-Microservice (8000 internal)
                   └─ /api/iam/*     → iam_proxy_routes
                   └─ /api/config/*  → config_proxy_routes
                   └─ /api/security/* → security_proxy_routes
```

## Fichiers Modifiés

### Backend
1. `/app/apps/api/server.py` - Ajout de security_proxy_routes
2. `/app/apps/api/src/presentation/routes/security_proxy_routes.py` - Nouveau proxy
3. `/app/apps/api/src/presentation/routes/config_proxy_routes.py` - Proxy existant

### Frontend
1. `/app/apps/web/.env` - Variables vides pour URLs relatives
2. `/app/apps/web/vite.config.ts` - Ajout proxy /api/security/*
3. `/app/apps/web/src/features/admin/api/emailDomainsApi.ts` - Utilisation baseQueryWithAuth

## Vérification

### Tests Locaux
✅ Page countries charge correctement
✅ Page email domains charge correctement
✅ Page retention config charge correctement
✅ Modal user details fonctionne
✅ Pas d'erreur Mixed Content
✅ Pas d'erreur CORS

### Tests Production
- Les URLs relatives fonctionnent avec HTTPS
- Les proxies backend routent correctement vers auth-microservice
- Pas de hardcoded localhost URLs

## Principe Général pour Futures APIs

Pour toute nouvelle API qui appelle l'auth-microservice:

1. **Frontend**: Toujours utiliser `baseQueryWithAuth` (pas de baseUrl custom)
2. **Backend**: Créer un proxy si nécessaire pour les nouveaux préfixes
3. **Vite**: Ajouter la règle proxy pour le développement local
4. **Production**: Les proxies backend gèrent le routing

## Notes Importantes

- Ne JAMAIS hardcoder `http://localhost:8000` dans le code frontend
- Ne JAMAIS utiliser `VITE_BACKEND_URL=http://...` en production
- Toujours utiliser des URLs relatives (`/api/...`)
- Les proxies backend permettent la communication interne entre services
- Vite proxy est uniquement pour le développement local
