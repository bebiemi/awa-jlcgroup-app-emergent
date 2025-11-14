# Standard des Endpoints API

## 📋 Vue d'ensemble

Ce document définit le standard obligatoire pour tous les endpoints API dans l'application.

## ✅ Règles absolues

### 1. Format des endpoints

**TOUS les endpoints doivent suivre ce format :**
```
/api/<service>/<resource>/<action?>
```

**Exemples valides :**
```typescript
/api/auth/local/login
/api/users/me
/api/iam/permissions
/api/auth/config/all
/api/emails/settings
```

**Exemples INVALIDES :**
```typescript
/auth/login              // ❌ Manque /api
/api/api/users/me        // ❌ Duplication /api
/auth-api/config         // ❌ Format incorrect
```

### 2. Utilisation de createBaseQueryWithAuth

**✅ Correct :**
```typescript
import { createBaseQueryWithAuth } from '@/utils/baseQueryWithAuth'

export const myApi = createApi({
  reducerPath: 'myApi',
  baseQuery: createBaseQueryWithAuth(),  // Pas de paramètre !
  endpoints: (builder) => ({
    getData: builder.query({
      query: () => '/users/me',  // Chemin relatif sans /api
    }),
  }),
})
```

**❌ Incorrect :**
```typescript
// NE JAMAIS FAIRE ÇA :
createBaseQueryWithAuth('/api')
createBaseQueryWithAuth('/auth/config')
createBaseQueryWithAuth('') 
```

### 3. Construction des endpoints

**Utiliser la configuration globale :**
```typescript
import { buildEndpoint } from '@/config/api.config'

// Construction typée et sécurisée
const endpoint = buildEndpoint('AUTH', 'local/login')
// Résultat: '/api/auth/local/login'
```

**Dans les queries RTK Query :**
```typescript
endpoints: (builder) => ({
  login: builder.mutation({
    query: (credentials) => ({
      url: '/auth/local/login',  // Relatif, sans /api
      method: 'POST',
      body: credentials,
    }),
  }),
})
```

## 🛡️ Validation automatique

### Tests unitaires

Tous les nouveaux endpoints doivent être testés :
```typescript
import { validateEndpoint } from '@/config/api.config'

it('should have valid endpoint', () => {
  expect(validateEndpoint('/api/users/me')).toBe(true)
})
```

### Linter ESLint

Le linter détecte automatiquement :
- ❌ Duplications `/api/api/`
- ❌ Endpoints sans `/api`
- ❌ `createBaseQueryWithAuth()` avec paramètres

### Exécuter la validation

```bash
# Tester les endpoints
npm run test:api-endpoints

# Linter
npm run lint
```

## 📚 Services disponibles

Liste complète dans `/app/apps/web/src/config/api.config.ts` :

```typescript
API_SERVICES = {
  AUTH: 'auth',
  IAM: 'iam',
  USERS: 'users',
  PROFILES: 'profiles',
  SECURITY: 'security',
  EMAILS: 'emails',
  CONFIG: 'auth/config',
  BESOINS: 'besoins',
  ENTREPRISES: 'entreprises',
  MISSIONS: 'missions',
  CONTRACTS: 'contracts',
  APPLICATIONS: 'applications',
  VALIDATIONS: 'validations',
  NOTIFICATIONS: 'notifications',
  LOCATIONS: 'locations',
  FEATURE_FLAGS: 'feature-flags',
  VERSIONS: 'versions',
}
```

## 🚫 Erreurs courantes et solutions

### Erreur 404 avec `/api/api/...`

**Cause :** Double concaténation du préfixe

**Solution :**
```typescript
// ❌ Avant
baseQuery: createBaseQueryWithAuth('/api'),
endpoints: { query: () => '/api/users/me' }

// ✅ Après
baseQuery: createBaseQueryWithAuth(),
endpoints: { query: () => '/users/me' }
```

### Mixed Content (HTTP/HTTPS)

**Cause :** URL absolue construite avec `http://`

**Solution :** Toujours utiliser des URLs relatives
```typescript
// ❌ Éviter
const url = `http://${window.location.host}/api/users/me`

// ✅ Utiliser
const url = '/users/me'  // Le baseQuery gère le protocole
```

## 📝 Checklist pour nouveau endpoint

- [ ] L'endpoint commence par `/api/`
- [ ] Pas de duplication `/api/api/`
- [ ] Utilise `createBaseQueryWithAuth()` sans paramètre
- [ ] Le chemin dans query() est relatif (sans `/api`)
- [ ] Tests unitaires ajoutés
- [ ] Passe le linter sans erreur

## 🔧 Migration d'un ancien endpoint

1. **Identifier le service** : AUTH, IAM, USERS, etc.
2. **Retirer le préfixe** du query si présent
3. **Vérifier le baseQuery** : doit être `createBaseQueryWithAuth()`
4. **Tester** : `npm run test:api-endpoints`

**Exemple de migration :**
```typescript
// ❌ Avant
export const oldApi = createApi({
  baseQuery: createBaseQueryWithAuth('/api/auth'),
  endpoints: (builder) => ({
    login: builder.query({
      query: () => '/auth/local/login',  // Duplication !
    }),
  }),
})

// ✅ Après
export const newApi = createApi({
  baseQuery: createBaseQueryWithAuth(),
  endpoints: (builder) => ({
    login: builder.query({
      query: () => '/auth/local/login',  // Propre !
    }),
  }),
})
```

## 🆘 Aide

En cas de doute :
1. Consulter `/app/apps/web/src/config/api.config.ts`
2. Regarder les exemples dans `/app/apps/web/src/features/auth/api/authApi.ts`
3. Exécuter `npm run lint` pour détecter les problèmes
