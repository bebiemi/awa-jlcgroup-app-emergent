# 🐳 Docker vs Local - Différences Importantes

## Configuration Proxy Vite

### ⚠️ Différence Critique

La configuration du proxy Vite **DOIT être différente** selon l'environnement :

| Environnement | Target API | Target Auth | Raison |
|---------------|------------|-------------|--------|
| **Local (Supervisor)** | `http://localhost:8001` | `http://localhost:8000` | Services sur la machine locale |
| **Docker** | `http://jlc-api:8001` | `http://auth-microservice:8000` | Résolution DNS Docker par nom de service |

### 📁 Fichiers de Configuration

#### Local: `vite.config.ts`

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001',  // ✅ localhost pour local
        changeOrigin: true,
        secure: false,
      },
      '/auth-api': {
        target: 'http://localhost:8000',  // ✅ localhost pour local
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
      },
    },
  },
})
```

#### Docker: `vite.config.docker.ts`

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://jlc-api:8001',  // ✅ Nom du service Docker
        changeOrigin: true,
        secure: false,
      },
      '/auth-api': {
        target: 'http://auth-microservice:8000',  // ✅ Nom du service Docker
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
      },
    },
  },
})
```

### 🔧 Utilisation avec Docker

Modifier le `Dockerfile` pour utiliser la bonne config :

```dockerfile
# Development Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .

# Utiliser la config Docker
RUN cp vite.config.docker.ts vite.config.ts

EXPOSE 5173

CMD ["yarn", "dev", "--host", "0.0.0.0"]
```

---

## Configuration CORS

### ⚠️ Format Requis

Dans `docker-compose.yml`, `CORS_ORIGINS` **DOIT être une liste JSON** :

#### ❌ Incorrect (String avec virgules)

```yaml
environment:
  - CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### ✅ Correct (Liste JSON)

```yaml
environment:
  - CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://jlc-web:3000"]
```

### 📝 Exemple Complet

```yaml
# docker-compose.yml
services:
  auth-microservice:
    environment:
      - CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://jlc-web:3000"]
      
  jlc-api:
    environment:
      - CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://jlc-web:3000"]
```

### 🐍 Parsing Backend Python

Le backend parse automatiquement :

```python
# main.py
cors_origins_str = os.getenv("CORS_ORIGINS", "[]")

# Parse la liste JSON
import json
cors_origins = json.loads(cors_origins_str)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Réseau Docker

### 🌐 Résolution DNS

Dans Docker, les services communiquent via le **nom du service** défini dans `docker-compose.yml` :

```yaml
services:
  jlc-web:        # ✅ Accessible via http://jlc-web:3000
  jlc-api:        # ✅ Accessible via http://jlc-api:8001
  auth-microservice:  # ✅ Accessible via http://auth-microservice:8000
  mongodb:        # ✅ Accessible via mongodb://mongodb:27017
```

### 🔗 Connexions

| Source | Destination | URL |
|--------|-------------|-----|
| Frontend → API | Backend | `http://jlc-api:8001` |
| Frontend → Auth | Auth Service | `http://auth-microservice:8000` |
| Backend → MongoDB | Database | `mongodb://mongodb:27017` |
| Auth → MongoDB | Database | `mongodb://mongodb:27017` |

**Important:** `localhost` ne fonctionne PAS dans Docker (sauf pour accès externe).

---

## Variables d'Environnement

### Local (.env)

```env
# apps/web/.env
VITE_API_BASE_URL=http://localhost:8001
VITE_AUTH_SERVICE_URL=http://localhost:8000

# auth-microservice/.env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=auth_db

# apps/api/.env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=jlc_db
```

Les valeurs par défaut du backend (MongoDB, AUTH_SERVICE_URL, SMTP_*, etc.) sont désormais centralisées et validées dans `backend/src/infrastructure/config.py` afin d'aligner l'API, les proxys d'authentification et le proxy email quelle que soit la cible (local ou Docker).

### Docker (docker-compose.yml)

```yaml
services:
  jlc-web:
    environment:
      - VITE_API_BASE_URL=http://localhost:8001  # Pour l'accès browser
      - VITE_AUTH_SERVICE_URL=http://localhost:8000
      
  auth-microservice:
    environment:
      - MONGO_URL=mongodb://mongodb:27017  # ✅ Nom du service
      - DATABASE_NAME=auth_db
      
  jlc-api:
    environment:
      - MONGO_URL=mongodb://mongodb:27017  # ✅ Nom du service
      - DATABASE_NAME=jlc_db
```

---

## Checklist de Migration Local → Docker

### ✅ Avant de Démarrer avec Docker

1. **Créer `vite.config.docker.ts`**
   ```bash
   cp vite.config.ts vite.config.docker.ts
   # Puis modifier les targets vers les noms de services
   ```

2. **Vérifier `docker-compose.yml`**
   ```yaml
   # CORS_ORIGINS doit être une liste JSON
   - CORS_ORIGINS=["http://localhost:3000","http://jlc-web:3000"]
   ```

3. **Vérifier les Dockerfiles**
   ```dockerfile
   # Copier la bonne config
   RUN cp vite.config.docker.ts vite.config.ts
   ```

4. **Tester la connectivité**
   ```bash
   docker-compose up -d
   docker-compose exec jlc-web ping jlc-api -c 3
   docker-compose exec jlc-web ping auth-microservice -c 3
   ```

---

## Troubleshooting

### Problème: ERR_CONNECTION_REFUSED en Docker

**Symptôme:**
```
GET http://localhost:8000/api/... net::ERR_CONNECTION_REFUSED
```

**Cause:** Le proxy Vite utilise `localhost` au lieu du nom du service Docker.

**Solution:**
```typescript
// vite.config.ts (dans Docker)
proxy: {
  '/auth-api': {
    target: 'http://auth-microservice:8000',  // ✅ Pas localhost
    changeOrigin: true,
  }
}
```

### Problème: CORS Error en Docker

**Symptôme:**
```
Access to fetch at '...' has been blocked by CORS policy
```

**Cause:** `CORS_ORIGINS` mal formaté ou nom de service manquant.

**Solution:**
```yaml
environment:
  - CORS_ORIGINS=["http://localhost:3000","http://jlc-web:3000"]
  #                                       ^^^ Ajouter le nom du service
```

### Problème: Services ne se voient pas

**Symptôme:**
```
getaddrinfo ENOTFOUND jlc-api
```

**Cause:** Les services ne sont pas sur le même réseau Docker.

**Solution:**
```yaml
networks:
  jlc-network:
    driver: bridge

services:
  jlc-web:
    networks:
      - jlc-network  # ✅ Tous les services sur le même réseau
      
  jlc-api:
    networks:
      - jlc-network
```

---

## Résumé

| Aspect | Local | Docker |
|--------|-------|--------|
| **Proxy Vite** | `localhost:8001` | `jlc-api:8001` |
| **CORS** | String avec virgules | Liste JSON |
| **MongoDB** | `localhost:27017` | `mongodb:27017` |
| **Réseau** | Loopback | Bridge Docker |
| **Config File** | `vite.config.ts` | `vite.config.docker.ts` |

**Règle d'or:** En Docker, utilisez TOUJOURS les noms de services, jamais `localhost`.

---

**Version:** 1.0.0  
**Dernière mise à jour:** Novembre 2025
