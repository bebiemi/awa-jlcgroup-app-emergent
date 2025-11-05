# Dépannage - Système de Versioning

## Problème résolu: ERR_CONNECTION_REFUSED

### Symptôme
```
GET http://localhost:8000/api/versions/list net::ERR_CONNECTION_REFUSED
```

### Cause
Le composant `ConfigurationVersionsPage.tsx` faisait des appels directs à `http://localhost:8000` au lieu d'utiliser le proxy Vite configuré.

### Solution appliquée ✅
Les appels ont été modifiés pour utiliser le proxy Vite `/auth-api`:

**Avant:**
```typescript
fetch(`${import.meta.env.VITE_AUTH_SERVICE_URL}/api/versions/list`)
// Tentait d'appeler: http://localhost:8000/api/versions/list
```

**Après:**
```typescript
fetch('/auth-api/versions/list')
// Passe par le proxy Vite qui route vers http://localhost:8000/api/versions/list
```

### Configuration du proxy Vite
Dans `/apps/web/vite.config.ts`:
```typescript
proxy: {
  '/auth-api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
  },
}
```

### Endpoints corrigés
1. ✅ `GET /auth-api/versions/list` → Liste des versions
2. ✅ `POST /auth-api/versions/snapshot` → Création snapshot
3. ✅ `POST /auth-api/versions/rollback` → Rollback

## Vérification

### 1. Tester le proxy depuis le terminal
```bash
curl http://localhost:3000/auth-api/versions/list | jq '.'
```

**Résultat attendu:**
```json
{
  "versions": [...],
  "total": 4,
  "limit": 50,
  "skip": 0
}
```

### 2. Tester dans le navigateur

1. **Ouvrir DevTools** (F12)
2. **Aller dans Network tab**
3. **Naviguer vers** `/admin/versions`
4. **Vérifier** les requêtes:
   - ✅ URL: `/auth-api/versions/list` (pas `http://localhost:8000/...`)
   - ✅ Status: 200 OK
   - ✅ Response: JSON avec versions

### 3. Console logs
Ouvrir la console du navigateur et vérifier:
- ✅ Aucune erreur `ERR_CONNECTION_REFUSED`
- ✅ Aucune erreur CORS
- ✅ Message: Les données se chargent

## Si le problème persiste

### Vérifier les services
```bash
# Frontend
sudo supervisorctl status frontend
# Devrait être: RUNNING

# Auth-microservice
sudo supervisorctl status auth-microservice
# Devrait être: RUNNING

# Logs frontend
tail -f /var/log/supervisor/frontend.err.log

# Logs backend
tail -f /var/log/supervisor/auth-microservice.out.log
```

### Redémarrer si nécessaire
```bash
# Redémarrer tous les services
sudo supervisorctl restart all

# Attendre 5 secondes
sleep 5

# Vérifier les statuts
sudo supervisorctl status
```

### Vérifier le hot reload
```bash
# Voir les derniers hot reloads
tail -20 /var/log/supervisor/frontend.out.log | grep "hmr update"
```

**Devrait montrer:**
```
[vite] hmr update /src/features/admin/pages/ConfigurationVersionsPage.tsx
```

### Cache navigateur
Si le problème persiste:
1. **Hard refresh**: Ctrl+Shift+R (ou Cmd+Shift+R sur Mac)
2. **Vider le cache**: DevTools → Network → Disable cache (cocher)
3. **Mode incognito**: Tester dans une fenêtre privée

### Vérifier MongoDB
```bash
# Se connecter à MongoDB
mongosh

# Utiliser la base auth_db
use auth_db

# Compter les versions
db.configuration_history.count()
# Devrait retourner un nombre > 0

# Voir les versions
db.configuration_history.find().sort({created_at: -1}).limit(5).pretty()
```

## Tests manuels après correction

### 1. Accéder à la page
1. Se connecter avec `admin@awanagroup.com` / `awana2025`
2. Naviguer: **Paramètres** → **Versions Config**
3. **Vérifier:**
   - ✅ Page se charge sans erreur
   - ✅ Statistiques affichées (Total, Manuels, Rollbacks)
   - ✅ Liste des versions visible

### 2. Créer un snapshot
1. Cliquer sur **"Créer Snapshot"**
2. Entrer description: "Test UI - Snapshot manuel"
3. Cliquer **"Créer Snapshot"**
4. **Vérifier:**
   - ✅ Toast de succès
   - ✅ Liste se recharge automatiquement
   - ✅ Nouveau snapshot apparaît en haut

### 3. Tester le rollback (optionnel - environnement test uniquement)
1. Sélectionner une version plus ancienne
2. Cliquer **"Rollback"**
3. Entrer raison: "Test rollback UI"
4. Confirmer
5. **Vérifier:**
   - ✅ Toast de succès
   - ✅ Snapshot automatique créé (type: auto, pre-rollback)
   - ✅ Rollback enregistré

## Architecture des appels API

### Pattern à suivre
Tous les appels à l'auth-microservice doivent utiliser le préfixe `/auth-api`:

```typescript
// ✅ CORRECT
fetch('/auth-api/versions/list')
fetch('/auth-api/auth/login')
fetch('/auth-api/config/all')

// ❌ INCORRECT
fetch('http://localhost:8000/api/versions/list')
fetch(`${import.meta.env.VITE_AUTH_SERVICE_URL}/api/versions/list`)
```

### Pourquoi?
1. **Proxy Vite**: Route automatiquement vers le bon service
2. **CORS**: Évite les problèmes de cross-origin
3. **Production**: Fonctionne aussi en production sans changement
4. **Kubernetes**: Compatible avec l'architecture containerisée

### Autres API
Pour les appels au backend principal (port 8001):

```typescript
// ✅ CORRECT
fetch('/api/missions/list')
fetch('/api/documents/upload')

// ❌ INCORRECT
fetch('http://localhost:8001/api/missions/list')
```

## Fichiers modifiés

### `/apps/web/src/features/admin/pages/ConfigurationVersionsPage.tsx`

**Lignes modifiées:**
- Ligne 39: `loadVersions()` - URL changée
- Ligne 57: `createSnapshot()` - URL changée  
- Ligne 87: `rollbackToVersion()` - URL changée

**Changements:**
```diff
- fetch(`${import.meta.env.VITE_AUTH_SERVICE_URL}/api/versions/list`)
+ fetch('/auth-api/versions/list')

- fetch(`${import.meta.env.VITE_AUTH_SERVICE_URL}/api/versions/snapshot?...`)
+ fetch('/auth-api/versions/snapshot?...')

- fetch(`${import.meta.env.VITE_AUTH_SERVICE_URL}/api/versions/rollback`)
+ fetch('/auth-api/versions/rollback')
```

## Prochaines étapes

Une fois la page fonctionnelle:

1. ✅ **Tester création de snapshots** - Vérifier que tout fonctionne
2. ✅ **Documenter workflow** - Créer guide utilisateur si besoin
3. 📋 **Migrer vers RTK Query** (optionnel) - Pour cohérence avec le reste de l'app
4. 📋 **Ajouter tests E2E** - Automatiser les tests UI

## Support

Si vous rencontrez toujours des problèmes après avoir suivi ce guide:

1. **Copier les logs d'erreur** depuis la console navigateur
2. **Copier les logs backend** depuis terminal
3. **Prendre un screenshot** de l'erreur
4. **Partager** ces informations pour assistance
