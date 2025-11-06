# 🔧 Guide de Dépannage - Machine Locale

## Erreurs Courantes et Solutions

### 1. ERR_CONNECTION_REFUSED sur https://127.0.0.1

**Erreur dans la console:**
```
GET https://127.0.0.1/ net::ERR_CONNECTION_REFUSED
```

**Cause:** Configuration HMR de Vite pour le cloud (WSS)

**Solution:**
1. Vérifier que `vite.config.ts` contient:
```typescript
hmr: {
  ...(process.env.NODE_ENV === 'production' && {
    clientPort: 443,
    protocol: 'wss',
  }),
},
```

2. Vider le cache:
   - Chrome: `Ctrl + Shift + Delete`
   - Cocher "Images et fichiers en cache"
   - Vider

3. Hard reload: `Ctrl + Shift + R`

---

### 2. 500 Internal Server Error sur /auth-api/...

**Erreur dans la console:**
```
POST http://localhost:3000/auth-api/auth/local/login 500 (Internal Server Error)
GET http://localhost:3000/auth-api/auth/config/all 500 (Internal Server Error)
```

#### Diagnostic Rapide

**1. Tester l'API directement:**
```bash
# Test auth service
curl http://localhost:8000/health

# Test config
curl http://localhost:8000/api/auth/config/all

# Test login
curl -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"awana2025"}'
```

Si ces commandes retournent 200 OK, le problème vient du frontend.

#### Solution A: Cache Navigateur

```bash
# 1. Vider complètement le cache
Ctrl + Shift + Delete (tout supprimer)

# 2. Fermer TOUS les onglets

# 3. Fermer le navigateur complètement

# 4. Rouvrir et aller sur http://localhost:3000

# 5. Si ça ne marche pas, essayer en navigation privée
Ctrl + Shift + N (Chrome)
```

#### Solution B: Redémarrer le Frontend

```bash
# Arrêter
sudo supervisorctl stop frontend

# Nettoyer le cache Vite
rm -rf /app/apps/web/node_modules/.vite
rm -rf /app/apps/web/dist

# Redémarrer
sudo supervisorctl start frontend

# Attendre 10 secondes
sleep 10

# Recharger le navigateur
```

#### Solution C: Vérifier les Services

```bash
# Diagnostic complet
./check-health.sh

# Voir les logs en temps réel
tail -f /var/log/supervisor/auth-microservice.err.log
tail -f /var/log/supervisor/frontend.err.log

# Redémarrer tout si nécessaire
sudo supervisorctl restart all
```

---

### 3. Proxy Vite ne Fonctionne Pas

**Symptôme:** Les appels API ne passent pas par le proxy

**Vérification:**

1. **Ouvrir DevTools (F12)**
2. **Onglet Network**
3. **Cocher "Disable cache"**
4. **Recharger la page**
5. **Vérifier les requêtes:**
   - `/auth-api/...` devrait être proxié vers `localhost:8000`
   - `/api/...` devrait être proxié vers `localhost:8001`

**Si le proxy ne fonctionne pas:**

```bash
# 1. Vérifier vite.config.ts
cat /app/apps/web/vite.config.ts | grep -A 10 "proxy:"

# 2. Redémarrer le frontend
sudo supervisorctl restart frontend

# 3. Vérifier que les services backend tournent
sudo supervisorctl status | grep -E "auth|backend"

# 4. Tester les backends directement
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

### 4. MongoDB Non Accessible

**Erreur:** Connection refused / Database not found

**Solution:**

```bash
# Vérifier le statut
sudo systemctl status mongodb

# Démarrer si nécessaire
sudo systemctl start mongodb

# Test connexion
mongosh --eval "db.runCommand({ping: 1})"

# Vérifier les utilisateurs
mongosh auth_db --eval "db.users.countDocuments()"
```

---

### 5. Services Ne Démarrent Pas

**Symptôme:** Supervisor affiche FATAL ou EXITED

**Diagnostic:**

```bash
# Voir les logs d'erreur
tail -f /var/log/supervisor/*.err.log

# Statut détaillé
sudo supervisorctl status

# Redémarrer un service spécifique
sudo supervisorctl restart frontend
sudo supervisorctl restart auth-microservice
sudo supervisorctl restart backend
```

**Problèmes communs:**

- **Port déjà utilisé:**
  ```bash
  # Trouver le processus
  lsof -i :3000
  lsof -i :8000
  lsof -i :8001
  
  # Tuer si nécessaire
  kill -9 <PID>
  ```

- **Dépendances manquantes:**
  ```bash
  # Frontend
  cd /app/apps/web
  yarn install
  
  # Backend
  cd /app/auth-microservice
  pip install -r requirements.txt
  ```

---

### 6. Page Blanche / Erreur de Compilation

**Solution:**

```bash
# 1. Nettoyer complètement
cd /app/apps/web
rm -rf node_modules
rm -rf .vite
rm -rf dist

# 2. Réinstaller
yarn install

# 3. Redémarrer
sudo supervisorctl restart frontend

# 4. Vérifier les logs
tail -f /var/log/supervisor/frontend.err.log
```

---

## Procédure de Redémarrage Complet

Si tout est cassé, suivez cette procédure:

```bash
# 1. Arrêter tous les services
sudo supervisorctl stop all

# 2. Vérifier qu'aucun port n'est utilisé
lsof -i :3000,8000,8001,27017

# 3. Nettoyer les caches
rm -rf /app/apps/web/node_modules/.vite
rm -rf /app/apps/web/dist

# 4. Démarrer MongoDB
sudo systemctl start mongodb

# 5. Démarrer tous les services
sudo supervisorctl start all

# 6. Attendre 15 secondes
sleep 15

# 7. Vérifier le statut
sudo supervisorctl status

# 8. Test de santé
./check-health.sh

# 9. Dans le navigateur:
#    - Vider le cache (Ctrl+Shift+Delete)
#    - Fermer tous les onglets
#    - Rouvrir http://localhost:3000
```

---

## Configuration Correcte

### vite.config.ts

```typescript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    allowedHosts: [
      '.preview.emergentagent.com',
      '.emergent.host',
      'localhost',
      '127.0.0.1'
    ],
    hmr: {
      ...(process.env.NODE_ENV === 'production' && {
        clientPort: 443,
        protocol: 'wss',
      }),
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/auth-api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
      },
    },
  },
})
```

### .env (apps/web/.env)

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_AUTH_SERVICE_URL=http://localhost:8000
NODE_ENV=development
```

---

## Commandes Utiles

### Diagnostic

```bash
# Santé complète
./check-health.sh

# Statut services
sudo supervisorctl status

# Logs en temps réel
tail -f /var/log/supervisor/*.log

# Test backends
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Redémarrage

```bash
# Un service
sudo supervisorctl restart frontend
sudo supervisorctl restart auth-microservice
sudo supervisorctl restart backend

# Tous
sudo supervisorctl restart all
```

### Nettoyage

```bash
# Cache frontend
rm -rf /app/apps/web/node_modules/.vite
rm -rf /app/apps/web/dist

# Logs
sudo rm -f /var/log/supervisor/*.log
```

---

## DevTools - Checklist

Quand vous déboguez dans le navigateur:

1. **Ouvrir DevTools** (F12)

2. **Onglet Console:**
   - Regarder les erreurs en rouge
   - Noter les URLs qui échouent

3. **Onglet Network:**
   - Cocher "Disable cache"
   - Cocher "Preserve log"
   - Recharger la page
   - Filtrer par "Fetch/XHR"
   - Regarder les requêtes en rouge
   - Cliquer dessus et voir:
     - Status code
     - Request headers
     - Response

4. **Vérifier les URLs:**
   - `/auth-api/...` → proxié vers `localhost:8000`
   - `/api/...` → proxié vers `localhost:8001`

---

## Mode Debug

Pour plus de détails sur les erreurs:

```bash
# 1. Arrêter le service frontend
sudo supervisorctl stop frontend

# 2. Aller dans le dossier
cd /app/apps/web

# 3. Lancer manuellement avec logs détaillés
yarn dev

# 4. Observer les erreurs dans le terminal
# 5. Ctrl+C pour arrêter

# 6. Redémarrer normalement
sudo supervisorctl start frontend
```

---

## Support

Si rien ne fonctionne:

1. **Copier les logs:**
   ```bash
   sudo supervisorctl status > status.txt
   tail -n 100 /var/log/supervisor/auth-microservice.err.log > auth-logs.txt
   tail -n 100 /var/log/supervisor/frontend.err.log > frontend-logs.txt
   ```

2. **Faire une capture d'écran:**
   - DevTools (F12) → Console
   - DevTools → Network (avec les requêtes en erreur)

3. **Documenter:**
   - Commandes exécutées
   - Erreurs exactes
   - Étapes pour reproduire

---

## Résumé des Solutions Rapides

| Problème | Solution Rapide |
|----------|-----------------|
| ERR_CONNECTION_REFUSED | Vider cache + Ctrl+Shift+R |
| 500 sur /auth-api | Navigation privée ou redémarrer frontend |
| Proxy ne marche pas | Redémarrer frontend |
| MongoDB erreur | `sudo systemctl start mongodb` |
| Page blanche | Nettoyer cache Vite + redémarrer |
| Services down | `sudo supervisorctl restart all` |

**Solution universelle:** 
```bash
sudo supervisorctl restart all && sleep 10
# Puis vider cache navigateur + Ctrl+Shift+R
```

---

**Version:** 1.0.0  
**Dernière mise à jour:** Novembre 2025
