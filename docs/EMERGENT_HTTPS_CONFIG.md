# Configuration HTTPS pour Emergent Platform

## Problème
Sur les environnements `*.preview.emergentagent.com`, l'erreur Mixed Content persiste:
```
Mixed Content: The page at 'https://identity-manager-5.preview.emergentagent.com/admin/countries' 
was loaded over HTTPS, but requested an insecure resource 
'http://xxx.preview.emergentagent.com/api/config/countries'
```

## Cause
La plateforme Emergent peut injecter des variables d'environnement au moment du build avec des URLs HTTP qui écrasent nos configurations.

## Solution Appliquée

### 1. Code Modifié: `baseQueryWithAuth.ts`

Nous avons modifié la logique pour **FORCER** l'utilisation d'URLs relatives en production:

```typescript
const getBaseUrl = (): string | undefined => {
  // Détection de l'environnement de production
  const isProduction = typeof window !== 'undefined' && 
    (window.location.hostname.includes('preview.emergentagent.com') ||
     window.location.hostname.includes('emergentagent.com') ||
     window.location.protocol === 'https:')
  
  // En production: TOUJOURS retourner undefined (URLs relatives)
  if (isProduction) {
    return undefined
  }
  
  // En développement: permettre les variables d'environnement
  const envUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL
  
  // Bloquer les URLs HTTP même en dev
  if (envUrl && envUrl.trim() !== '' && !envUrl.startsWith('http://')) {
    return envUrl
  }
  
  return undefined
}
```

### 2. Vérifications à Faire sur Emergent

#### A. Variables d'Environnement de Build

Vérifier que ces variables ne sont **PAS** définies avec des URLs HTTP:
- `VITE_BACKEND_URL`
- `REACT_APP_BACKEND_URL`
- `VITE_API_BASE_URL`
- `REACT_APP_API_URL`
- `NEXT_PUBLIC_API_URL`

**Recommandation**: Ces variables doivent être:
- Soit **vides** (valeur recommandée)
- Soit **non définies**
- Soit définies avec des URLs relatives (ex: `/api`)
- **JAMAIS** avec des URLs HTTP absolues

#### B. Configuration du Build

Si Emergent a des settings de build, s'assurer que:
```bash
# ✅ BON
VITE_BACKEND_URL=

# ❌ MAUVAIS
VITE_BACKEND_URL=http://xxx.preview.emergentagent.com
```

### 3. Test de Validation

Pour vérifier que le fix fonctionne en production:

1. **Ouvrir la Console DevTools** sur `https://identity-manager-5.preview.emergentagent.com`

2. **Vérifier les requêtes dans l'onglet Network**:
   ```
   ✅ BON: https://identity-manager-5.preview.emergentagent.com/api/config/countries
   ❌ MAUVAIS: http://xxx.preview.emergentagent.com/api/config/countries
   ```

3. **Vérifier la console**:
   - Aucune erreur "Mixed Content"
   - Aucune erreur CORS

4. **Test JavaScript dans la console**:
   ```javascript
   // Tester la valeur utilisée par le code
   console.log(window.location.protocol)  // Doit afficher "https:"
   console.log(window.location.hostname)  // Doit contenir ".emergentagent.com"
   ```

### 4. Architecture de Routage en Production

```
┌──────────────────────────────────────────────────────────────┐
│ User Browser (HTTPS)                                         │
│   ↓                                                          │
│ https://identity-manager-5.preview.emergentagent.com/admin/countries       │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ Nginx/Ingress (SSL Termination)                             │
│   - Termine le SSL/TLS                                       │
│   - Route vers les services internes                         │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ Frontend (React/Vite) - Port 3000                           │
│   - Requête: /api/config/countries (URL relative)           │
│   - Résolu automatiquement en HTTPS par le navigateur       │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ Backend Proxy (Port 8001)                                    │
│   - Route /api/config/* → Auth-Microservice                 │
│   - Communication interne HTTP (acceptable)                  │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ Auth-Microservice (Port 8000)                               │
│   - country_config_routes.py                                │
│   - Retourne les données                                     │
└──────────────────────────────────────────────────────────────┘
```

### 5. Fichier .env de Production

Le fichier `/app/apps/web/.env` doit contenir:

```env
# JLC API Backend URL
# Leave empty for production (uses relative URLs with same origin)
# In development with Vite proxy: empty string works with proxy rules
# In production: requests go to same origin and are routed by Kubernetes/nginx
VITE_BACKEND_URL=
VITE_API_BASE_URL=
```

**IMPORTANT**: Ces valeurs vides sont CORRECTES et nécessaires!

### 6. Checklist pour Emergent Platform

Si le problème persiste après nos modifications, vérifier:

- [ ] Aucune variable d'environnement Emergent ne contient des URLs HTTP
- [ ] Le build ne hardcode pas d'URLs HTTP
- [ ] Le reverse proxy Nginx/Ingress est correctement configuré
- [ ] Les headers `X-Forwarded-Proto: https` sont transmis (pour que l'app sache qu'elle est en HTTPS)
- [ ] Le fichier `.env` n'est pas écrasé par des configs Emergent

### 7. Solution Alternative (Si Problème Persiste)

Si le problème continue, il peut être nécessaire de:

1. **Forcer HTTPS dans le build Vite**:
   ```typescript
   // vite.config.ts
   export default defineConfig({
     define: {
       'import.meta.env.FORCE_HTTPS': JSON.stringify('true')
     }
   })
   ```

2. **Ajouter un middleware frontend** qui force les URLs HTTPS:
   ```typescript
   // Intercepter toutes les requêtes fetch
   const originalFetch = window.fetch
   window.fetch = (url, options) => {
     if (typeof url === 'string' && url.startsWith('http://')) {
       url = url.replace('http://', 'https://')
     }
     return originalFetch(url, options)
   }
   ```

## Contact Support Emergent

Si après toutes ces vérifications le problème persiste, contacter le support Emergent avec:
- Les logs de la console (erreurs Mixed Content)
- L'onglet Network (montrant les URLs HTTP appelées)
- Ce document de configuration
- La question spécifique: "Y a-t-il des variables d'environnement injectées au build qui pourraient contenir des URLs HTTP?"

## Résumé

**Notre code est maintenant configuré pour:**
✅ Détecter automatiquement l'environnement de production (HTTPS)
✅ Forcer l'utilisation d'URLs relatives en production
✅ Ignorer toute variable d'environnement HTTP en production
✅ Permettre la flexibilité en développement local

**La clé**: Le code force `baseUrl: undefined` en production, ce qui génère des URLs relatives comme `/api/config/countries` qui sont automatiquement résolues en HTTPS par le navigateur.
