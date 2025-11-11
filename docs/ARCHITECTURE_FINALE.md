# Architecture Finale - Application JLC Group

## Vue d'Ensemble

L'application JLC Group est un système de gestion d'intérim basé sur une architecture microservices avec React frontend, FastAPI backends, et MongoDB.

---

## Architecture Technique

### Diagramme Complet

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │
│  │  Browser   │  │   Mobile   │  │  Desktop   │                 │
│  │    App     │  │    App     │  │    App     │                 │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘                 │
│         └────────────────┴────────────────┘                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     LOAD BALANCER / CDN                           │
│              (SSL Termination, DDoS Protection)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      NGINX REVERSE PROXY                          │
│                        (Port 80/443)                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Routing Rules:                                          │    │
│  │  • /api/*      → Backend Gateway (8001)                 │    │
│  │  • /auth-api/* → Backend Gateway (8001)                 │    │
│  │  • /*          → Frontend React App (3001)              │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────┬───────────────────────┬─────────────────────────┘
                 │                       │
        ┌────────┴────────┐      ┌──────┴──────┐
        │                 │      │             │
        ▼                 ▼      ▼             ▼
┌──────────────┐   ┌─────────────────┐  ┌──────────────┐
│   Frontend   │   │  Backend Gateway│  │ Static Files │
│  React App   │   │    (FastAPI)    │  │   (Assets)   │
│              │   │                 │  │              │
│  • React 18  │   │  Port: 8001     │  │  • Images    │
│  • TypeScript│   │                 │  │  • CSS/JS    │
│  • Vite      │   │  Routes:        │  │  • Fonts     │
│  • RTK Query │   │  • Proxy routes │  │              │
│  • Tailwind  │   │  • Health check │  └──────────────┘
│              │   │  • Monitoring   │
│  Port: 3001  │   │                 │
└──────────────┘   └────────┬────────┘
                            │
                            │ Internal HTTP
                            │ (No X-Forwarded headers)
                            ▼
                   ┌─────────────────┐
                   │ Auth Microservice│
                   │    (FastAPI)     │
                   │                  │
                   │  Port: 8000      │
                   │                  │
                   │  Modules:        │
                   │  • Authentication│
                   │  • IAM (RBAC)    │
                   │  • User mgmt     │
                   │  • Besoins       │
                   │  • Missions      │
                   │  • Config        │
                   │                  │
                   └────────┬─────────┘
                            │
                            │
                            ▼
                   ┌─────────────────┐
                   │    MongoDB       │
                   │                  │
                   │  Port: 27017     │
                   │                  │
                   │  Databases:      │
                   │  • auth_db       │
                   │  • jlc_db        │
                   │                  │
                   │  Collections:    │
                   │  • users         │
                   │  • permissions   │
                   │  • profiles      │
                   │  • besoins       │
                   │  • missions      │
                   │  • configs       │
                   │                  │
                   └──────────────────┘
```

---

## Stack Technologique Détaillée

### Frontend

| Composant | Version | Rôle |
|-----------|---------|------|
| React | 18.x | UI Library |
| TypeScript | 5.x | Type Safety |
| Vite | 5.x | Build Tool & Dev Server |
| Redux Toolkit | 2.x | State Management |
| RTK Query | 2.x | API Client & Cache |
| Tailwind CSS | 3.x | Styling |
| React Router | 6.x | Routing |
| i18next | 23.x | Internationalization |

### Backend

| Composant | Version | Rôle |
|-----------|---------|------|
| Python | 3.11 | Language |
| FastAPI | 0.104+ | Web Framework |
| Uvicorn | 0.24+ | ASGI Server |
| Pydantic | 2.x | Data Validation |
| Motor | 3.x | MongoDB Driver (Async) |
| PyJWT | 2.x | JWT Authentication |
| httpx | 0.25+ | HTTP Client (Async) |
| Passlib | 1.7+ | Password Hashing |

### Infrastructure

| Composant | Version | Rôle |
|-----------|---------|------|
| Nginx | 1.24+ | Reverse Proxy |
| MongoDB | 7.0+ | Database |
| Supervisor | 4.x | Process Manager |
| Docker | 24+ | Containerization |

---

## Flux de Données

### Requête API Typique

```
1. Client envoie requête
   GET https://app.jlc.com/api/besoins?page=1
   Header: Authorization: Bearer <token>

2. Load Balancer
   • Terminaison SSL
   • Forwarding vers Nginx

3. Nginx (Port 80)
   • Vérifie le routing: /api/besoins → Backend
   • Supprime headers problématiques
   • Proxy vers http://backend:8001/api/besoins

4. Backend Gateway (Port 8001)
   • Identifie route proxy: /api/besoins
   • Route vers auth-microservice
   • Supprime X-Forwarded-Proto headers
   • Proxy vers http://auth-microservice:8000/api/besoins

5. Auth Microservice (Port 8000)
   • Vérifie JWT token
   • Vérifie permissions IAM
   • Query MongoDB
   • Retourne données JSON

6. Réponse remonte la chaîne
   Auth → Backend → Nginx → Load Balancer → Client
```

### Gestion de l'Authentification

```
┌─────────────────────────────────────────────────────┐
│                 AUTHENTICATION FLOW                  │
└─────────────────────────────────────────────────────┘

1. Login Request
   POST /api/auth/local/login
   Body: {username, password}
        ↓
2. Auth Microservice
   • Vérifie credentials (bcrypt)
   • Vérifie status utilisateur
   • Charge profils IAM
   • Charge permissions
        ↓
3. JWT Generation
   • Claims: user_id, username, roles, exp
   • Sign with JWT_SECRET
   • Return: {access_token, user}
        ↓
4. Client Storage
   • localStorage.setItem('access_token', token)
   • Redux state update
        ↓
5. Subsequent Requests
   • Header: Authorization: Bearer <token>
   • Backend vérifie token
   • Extrait user_id
   • Vérifie permissions IAM
```

---

## Système IAM (Identity and Access Management)

### Modèle RBAC

```
Users → Profiles → Permissions → Resources

Exemple:
┌──────────────┐
│  User        │
│  john@jlc.fr │
└──────┬───────┘
       │ has
       ▼
┌──────────────┐
│  Profile     │
│  "entreprise"│
└──────┬───────┘
       │ contains
       ▼
┌──────────────┐
│ Permissions  │
│ • besoins.create     │
│ • besoins.read       │
│ • besoins.edit       │
│ • config.read        │
└──────────────┘
```

### Permissions Format

```typescript
{
  id: "uuid",
  code: "besoins.create",
  resource: "besoins",
  action: "CREATE",
  scope: "own",  // own | company | all
  name: {
    fr: "Créer un besoin",
    en: "Create a need"
  }
}
```

### Vérification des Permissions

```python
# Dans l'auth-microservice
@router.get("/api/besoins")
async def get_besoins(
    current_user: User = Depends(get_current_user),
    permissions: PermissionChecker = Depends(require_permission("besoins.read"))
):
    # L'utilisateur a la permission
    # Scope filtering automatique
    if permissions.scope == "own":
        # Filtrer par company_id de l'utilisateur
        return besoins.filter(company_id=current_user.company_id)
    elif permissions.scope == "company":
        # Filtrer par entreprise
        return besoins.filter(company_id=current_user.company_id)
    else:  # all
        # Admin voit tout
        return besoins.find_all()
```

---

## Configuration Nginx Critique

### Headers à Supprimer (CRITIQUE)

```nginx
location /api/ {
    proxy_pass http://backend:8001;
    
    # Headers standards
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    
    # ⚠️ IMPORTANT: Ne PAS transmettre X-Forwarded-Proto
    # Cela cause des erreurs SSL dans les proxies internes
    # Les proxies backend suppriment ces headers explicitement
}
```

### Raison Technique

Quand nginx définit `X-Forwarded-Proto: https`, le backend le transmet à auth-microservice via httpx. httpx voit ce header et pense qu'il doit utiliser HTTPS, mais auth-microservice écoute en HTTP → `[SSL: WRONG_VERSION_NUMBER]`.

**Solution:** Tous les proxies backend suppriment ces headers :

```python
headers.pop("x-forwarded-proto", None)
headers.pop("x-forwarded-for", None)
headers.pop("x-forwarded-host", None)
```

---

## Base de Données MongoDB

### Schéma Logique

#### Collection: users
```javascript
{
  _id: ObjectId,
  id: "uuid",
  username: "john@jlc.fr",
  email: "john@jlc.fr",
  full_name: "John Doe",
  password_hash: "bcrypt_hash",
  roles: ["company"],
  profile_ids: ["uuid-profile-entreprise"],
  group_ids: ["uuid-group-1"],
  company_id: "uuid-company",
  status: "active",
  created_at: ISODate,
  updated_at: ISODate
}
```

#### Collection: permissions
```javascript
{
  _id: ObjectId,
  id: "uuid",
  code: "besoins.create",
  resource: "besoins",
  action: "CREATE",
  scope: "own",
  name: { fr: "Créer un besoin", en: "Create need" },
  description: { fr: "...", en: "..." },
  is_system: true
}
```

#### Collection: profiles
```javascript
{
  _id: ObjectId,
  id: "uuid",
  code: "entreprise",
  name: { fr: "Entreprise", en: "Company" },
  description: { fr: "...", en: "..." },
  permission_ids: ["uuid-perm-1", "uuid-perm-2", ...],
  is_system: true
}
```

#### Collection: besoins
```javascript
{
  _id: ObjectId,
  id: "uuid",
  title: "Recherche développeur",
  description: "...",
  company_id: "uuid",
  status: "brouillon",
  status_history: [{
    status: "brouillon",
    changed_at: ISODate,
    changed_by: "uuid-user"
  }],
  fields: {...},  // Dynamic based on form config
  comments: [{
    id: "uuid",
    text: "...",
    author_id: "uuid",
    created_at: ISODate
  }],
  created_by: "uuid",
  created_at: ISODate,
  updated_at: ISODate
}
```

### Indexes

```javascript
// users
db.users.createIndex({ username: 1 }, { unique: true })
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ company_id: 1 })

// permissions
db.permissions.createIndex({ code: 1 }, { unique: true })

// profiles
db.profiles.createIndex({ code: 1 }, { unique: true })

// besoins
db.besoins.createIndex({ company_id: 1 })
db.besoins.createIndex({ status: 1 })
db.besoins.createIndex({ created_at: -1 })
```

---

## Variables d'Environnement

### Vue d'Ensemble

| Service | Variable | Exemple | Obligatoire |
|---------|----------|---------|-------------|
| All | MONGO_URL | mongodb://localhost:27017 | ✅ |
| All | DATABASE_NAME | auth_db | ✅ |
| Auth | JWT_SECRET | super-secret-key-32chars+ | ✅ |
| Auth | JWT_ALGORITHM | HS256 | ❌ |
| Auth | ACCESS_TOKEN_EXPIRE_MINUTES | 30 | ❌ |
| Backend | AUTH_SERVICE_URL | http://localhost:8000 | ✅ |
| Frontend | VITE_BACKEND_URL | (empty for relative) | ❌ |

---

## Sécurité

### Mesures Implémentées

1. **Authentication**
   - JWT tokens avec expiration
   - Bcrypt pour hash passwords
   - Refresh tokens (à implémenter)

2. **Authorization**
   - RBAC avec profiles et permissions
   - Scope filtering (own/company/all)
   - Endpoint protection avec decorators

3. **Network**
   - HTTPS obligatoire en production
   - CORS configuré
   - Rate limiting (nginx)
   - Headers sécurité (X-Frame-Options, etc.)

4. **Data**
   - Validation Pydantic
   - SQL injection impossible (MongoDB)
   - XSS protection (React auto-escape)
   - CSRF protection (JWT stateless)

### Checklist Production

- [ ] HTTPS avec certificats valides
- [ ] JWT_SECRET fort (32+ chars random)
- [ ] MongoDB avec authentication
- [ ] Firewall configuré
- [ ] Logs centralisés
- [ ] Monitoring actif
- [ ] Backups automatiques
- [ ] Rate limiting actif
- [ ] CORS restreint aux domaines connus
- [ ] Secrets dans vault (pas en .env)

---

## Performance

### Optimisations

1. **Frontend**
   - Code splitting (Vite)
   - Lazy loading components
   - RTK Query caching
   - Image optimization

2. **Backend**
   - Async/await partout
   - Connection pooling MongoDB
   - HTTP/2 (nginx)
   - Gzip compression

3. **Database**
   - Indexes sur champs fréquents
   - Pagination obligatoire
   - Projection (select fields)
   - Aggregation pipelines

### Métriques Cibles

- Time to First Byte (TTFB): < 200ms
- API Response Time: < 500ms (p95)
- Frontend Load Time: < 2s
- Database Queries: < 100ms (p95)

---

## Monitoring et Observabilité

### Logs

```
# Structure des logs
{
  timestamp: "2025-11-11T10:30:00Z",
  level: "INFO",
  service: "auth-microservice",
  endpoint: "/api/auth/login",
  user_id: "uuid",
  duration_ms: 45,
  status_code: 200,
  message: "User logged in successfully"
}
```

### Métriques à Suivre

1. **Application**
   - Requests per second (RPS)
   - Response times (p50, p95, p99)
   - Error rates (4xx, 5xx)
   - Active users

2. **Infrastructure**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

3. **Business**
   - Besoins created
   - Missions converted
   - User registrations
   - Login success rate

---

## Disaster Recovery

### Backup Strategy

1. **MongoDB**
   - Daily full backup
   - Point-in-time recovery (15 min)
   - Retention: 30 days

2. **Application**
   - Git repository (code)
   - Docker images (registry)
   - Configuration files (encrypted)

### Recovery Plan

1. Database corruption
   - Restore from last backup
   - Replay transaction logs
   - Verify data integrity

2. Service down
   - Auto-restart (supervisor)
   - Failover to standby
   - Alert monitoring team

3. Complete disaster
   - Deploy from scratch
   - Restore database
   - Verify all services
   - DNS cutover

---

## Évolution Future

### Améliorations Prévues

1. **Architecture**
   - Service mesh (Istio)
   - Event-driven (Kafka)
   - Microservices additionnels

2. **Fonctionnalités**
   - Notifications push
   - Analytics dashboard
   - Mobile apps (React Native)
   - API GraphQL

3. **Performance**
   - Redis cache layer
   - CDN pour assets
   - Database read replicas
   - Horizontal scaling

---

## Documentation Associée

- `CHANGELOG_FIXES_COMPLETS.md` - Tous les changements récents
- `DEPLOIEMENT_DOCKER.md` - Déploiement avec Docker
- `DEPLOIEMENT_WEBAPP.md` - Déploiement Cloud (Azure/AWS/GCP)
- `README.md` - Guide de démarrage rapide
