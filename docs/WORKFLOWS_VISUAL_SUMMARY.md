# 🎨 Synthèse Visuelle des Workflows AWANA

## 🏗️ Architecture Globale du Système

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWANA BUSINESS SYSTEM                            │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  FRONTEND    │  │   API PROXY  │  │   BACKEND    │                 │
│  │   React      │──│   FastAPI    │──│   FastAPI    │                 │
│  │              │  │              │  │              │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                                              │                          │
│                                              ▼                          │
│                                       ┌──────────────┐                 │
│                                       │   MongoDB    │                 │
│                                       │ auth_db      │                 │
│                                       │ jlc_db       │                 │
│                                       └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 Parcours Utilisateur par Type

### 🔷 Candidat/Intérimaire

```
1️⃣ INSCRIPTION
   POST /api/auth/local/register
   ↓ (Status: ACTIVE immédiat)
   
2️⃣ CONNEXION
   POST /api/auth/local/login
   ↓ (JWT avec permissions candidat)
   
3️⃣ CONSULTATION MISSIONS
   GET /api/missions
   ↓
   
4️⃣ CANDIDATURE
   POST /api/applications
   ↓ (Upload CV)
   
5️⃣ SUIVI CANDIDATURE
   GET /api/applications/me
   ↓
   
6️⃣ SI ACCEPTÉ → Promotion Intérimaire
   POST /api/auth/promote-to-interimaire/{user_id}
```

**Collections impactées:**
- `auth_db.users` (compte)
- `auth_db.iam_groups` (grp.candidat)
- `jlc_db.collaborator_profiles` (profil)
- `jlc_db.applications` (candidatures)

---

### 🔶 Entreprise

```
1️⃣ INSCRIPTION
   POST /api/auth/local/register
   ↓ (Status: PENDING)
   
2️⃣ ATTENTE VALIDATION
   Record créé dans validations
   ↓
   
3️⃣ APPROBATION ADMIN
   POST /api/admin/{validation_id}/approve
   ↓ (Status: ACTIVE + Entreprise créée)
   
4️⃣ CONNEXION
   POST /api/auth/local/login
   ↓ (JWT avec permissions company)
   
5️⃣ CRÉATION MISSION
   POST /api/missions
   ↓
   
6️⃣ CONSULTATION CANDIDATURES
   GET /api/missions/{id}/applications
   ↓
   
7️⃣ VALIDATION CANDIDAT
   POST /api/applications/{id}/approve
```

**Collections impactées:**
- `auth_db.users` (compte)
- `jlc_db.validations` (validation)
- `jlc_db.entreprises` (entreprise créée après validation)
- `jlc_db.user_entreprises` (lien user ↔ entreprise)
- `jlc_db.missions` (offres publiées)
- `jlc_db.applications` (candidatures reçues)

---

### 🔵 Collaborateur JLC Group

```
1️⃣ INSCRIPTION
   POST /api/auth/local/register
   ↓ (Status: PENDING, détection @jlcgroup.*)
   
2️⃣ VALIDATION ADMIN
   POST /api/admin/{validation_id}/approve
   ↓ (Status: ACTIVE)
   
3️⃣ CONNEXION (ou SSO)
   POST /api/auth/local/login
   ou POST /api/auth/entraid/login
   ↓ (JWT avec permissions collaborateur)
   
4️⃣ GESTION BESOINS
   POST /api/besoins
   ↓
   
5️⃣ CONVERSION EN MISSION
   POST /api/besoins/{id}/convert-to-mission
   ↓
   
6️⃣ VALIDATION CANDIDATURES
   POST /api/applications/{id}/approve
```

**Collections impactées:**
- `auth_db.users` (compte)
- `auth_db.iam_groups` (grp.collaborateur)
- `jlc_db.besoins` (besoins RH)
- `jlc_db.missions` (missions converties)
- `jlc_db.applications` (validation)

---

### 🔴 Administrateur

```
1️⃣ CONNEXION
   POST /api/auth/local/login
   ↓ (JWT avec permissions admin)
   
2️⃣ GESTION VALIDATIONS
   GET /api/admin/validations
   POST /api/admin/{validation_id}/approve
   POST /api/admin/{validation_id}/reject
   ↓
   
3️⃣ GESTION IAM
   POST /api/iam/permissions (créer permissions)
   POST /api/iam/profiles (créer profils)
   POST /api/iam/groups (créer groupes)
   ↓
   
4️⃣ GESTION UTILISATEURS
   GET /api/auth/users
   PATCH /api/users/{user_id}/archive
   POST /api/users/{user_id}/password/admin-update
```

**Collections impactées:**
- `auth_db.iam_permissions` (droits)
- `auth_db.iam_profiles` (profils)
- `auth_db.iam_groups` (groupes)
- `jlc_db.validations` (approbations)
- `auth_db.users` (gestion comptes)

---

## 🔄 Workflows Transversaux

### 🔐 Sécurité

```
┌──────────────────────────────────────────┐
│       AUTHENTIFICATION WORKFLOW          │
└──────────────────────────────────────────┘

📧 Vérification Email
   POST /api/email/send → Token envoyé
   POST /api/email/verify → Activation
   
🔑 Réinitialisation MDP
   POST /api/auth/forgot-password → Token généré
   POST /api/auth/reset-password → MDP changé
   
🛡️ MFA (optionnel)
   POST /api/auth/mfa/setup → QR Code
   POST /api/auth/mfa/verify → Code TOTP
```

### 📨 Communication

```
┌──────────────────────────────────────────┐
│       COMMUNICATION WORKFLOW             │
└──────────────────────────────────────────┘

🔔 Notifications In-App
   Événement système
   ↓
   Création notification
   ↓
   GET /api/notifications → Affichage
   POST /api/notifications/mark-read → Marquage
   
📧 Emails Transactionnels
   Événement système
   ↓
   Sélection template
   ↓
   POST /api/email/send → Envoi SMTP
   ↓
   Log dans email_history
```

### 📄 Documents

```
┌──────────────────────────────────────────┐
│         DOCUMENTS WORKFLOW               │
└──────────────────────────────────────────┘

Upload Document
   POST /api/documents/upload
   ↓
   Validation type MIME
   ↓
   Stockage /app/uploads/
   ↓
   Référence en base jlc_db.documents
   
Récupération
   GET /api/documents/{id}
   ↓
   Vérification permissions
   ↓
   Retour fichier
```

---

## 📊 Matrice des Permissions par Workflow

| Workflow | Candidat | Intérimaire | Entreprise | Collaborateur | Admin |
|----------|----------|-------------|------------|---------------|-------|
| **Inscription** | ✅ Public | ✅ Public | ✅ Public | ✅ Public | ✅ |
| **Connexion** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Voir Missions** | ✅ | ✅ | ✅ Own | ✅ All | ✅ All |
| **Créer Mission** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Candidater** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Valider Candidature** | ❌ | ❌ | ✅ Own | ✅ All | ✅ All |
| **Gérer Besoins** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Gérer IAM** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Approuver Inscriptions** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Archiver Users** | ❌ | ❌ | ❌ | ❌ | ✅ |

**Légende:**
- ✅ = Autorisé
- ❌ = Interdit
- Own = Seulement ses propres données
- All = Toutes les données

---

## 🗄️ Schéma des Collections MongoDB

### auth_db

```
users
├── id (UUID)
├── username
├── email
├── password_hash
├── status (active, pending, suspended)
├── roles []
├── permissions []
├── profile_ids []
└── created_at

sessions
├── id (UUID)
├── user_id
├── access_token
├── refresh_token
├── expires_at
└── metadata

iam_permissions
├── id (UUID)
├── code (ex: missions.read.own)
├── name
├── description
└── resource

iam_profiles
├── id (UUID)
├── code (ex: role.candidat)
├── name
├── permission_ids []
└── bundle_ids []

iam_groups
├── id (UUID)
├── code (ex: grp.candidat)
├── name
├── user_ids []
└── profile_ids []
```

### jlc_db

```
entreprises
├── id (UUID)
├── nom
├── representant_legal
├── nif
├── email
└── statut

missions
├── id (UUID)
├── titre
├── description
├── entreprise_id
├── date_debut
├── date_fin
├── statut (draft, published, closed)
└── created_by

applications
├── id (UUID)
├── mission_id
├── candidat_id
├── cv_document_id
├── statut (submitted, approved, rejected)
└── created_at

besoins
├── id (UUID)
├── titre
├── description
├── statut
├── created_by
└── converted_mission_id

validations
├── id (UUID)
├── user_id
├── user_email
├── validation_type (company, collaborator)
├── statut (pending, approved, rejected)
└── approved_by

documents
├── id (UUID)
├── filename
├── filepath
├── mime_type
├── size
├── uploaded_by
└── created_at
```

---

## 🔗 Dépendances Entre Workflows

```
┌─────────────────────────────────────────────────────────┐
│                    SYSTÈME COMPLET                       │
└─────────────────────────────────────────────────────────┘

        IAM (Permissions, Profils, Groupes)
                    │
                    ▼
        ┌───────────────────────┐
        │    Inscription        │
        │ (Candidat/Collab/Ent) │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Vérification Email  │ (optionnel)
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Validation Admin    │ (si PENDING)
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Authentification    │
        │  (Local/SSO/Google)   │
        └───────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │Business│  │Profile │  │Comms   │
   │Flows   │  │Mgmt    │  │(Email/ │
   │        │  │        │  │Notif)  │
   └────────┘  └────────┘  └────────┘
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
            Documents Upload
```

---

## ⚡ Performance & Optimisation

### 🔥 Points Chauds (Hot Paths)

1. **POST /api/auth/local/login** (authentification)
   - Appelé à chaque connexion
   - Charge les permissions IAM
   - Crée session + JWT
   - **Optimisation:** Cache des permissions par profil

2. **GET /api/missions** (liste des missions)
   - Appelé fréquemment par candidats
   - Peut retourner beaucoup de données
   - **Optimisation:** Pagination + indexes MongoDB

3. **GET /api/notifications** (notifications)
   - Appelé régulièrement (polling)
   - **Optimisation:** WebSocket ou Server-Sent Events

### 📈 Indexes MongoDB Recommandés

```javascript
// auth_db.users
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })
db.users.createIndex({ status: 1 })

// auth_db.sessions
db.sessions.createIndex({ user_id: 1 })
db.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 })

// jlc_db.missions
db.missions.createIndex({ statut: 1 })
db.missions.createIndex({ entreprise_id: 1 })
db.missions.createIndex({ created_at: -1 })

// jlc_db.applications
db.applications.createIndex({ mission_id: 1 })
db.applications.createIndex({ candidat_id: 1 })
db.applications.createIndex({ statut: 1 })
```

---

## 🛡️ Sécurité - État Actuel

### ✅ Protections Implémentées

- ✅ BCrypt pour hash des mots de passe
- ✅ JWT avec expiration
- ✅ Rate limiting sur endpoints auth
- ✅ CORS configuré
- ✅ Validation des inputs (Pydantic)
- ✅ Audit logs pour actions critiques
- ✅ Sessions révocables

### ⚠️ Vulnérabilités Identifiées (À Corriger)

**Rapport d'audit complet:** `/app/docs/IAM_CORRECTIONS_IMMEDIATE.md`

**Résumé des problèmes:**
- 🔴 **Critique:** Routes admin sans protection
- 🔴 **Critique:** Endpoints IAM accessibles sans permissions
- 🟡 **Moyen:** Validation des fichiers uploadés insuffisante
- 🟡 **Moyen:** Pas de limitation de taille pour certains uploads

**Plan d'action:** `/app/docs/IAM_STEP_BY_STEP_FIX.md`

---

## 📈 Métriques Clés à Monitorer

### Business Metrics
- Nombre d'inscriptions par jour (par type: candidat/entreprise/collaborateur)
- Taux de validation des inscriptions (% approved vs rejected)
- Nombre de missions publiées
- Taux de conversion candidature → embauche
- Temps moyen de validation d'une candidature

### Technical Metrics
- Temps de réponse des endpoints critiques (< 200ms souhaité)
- Taux d'erreur sur authentification (< 1%)
- Nombre de sessions actives
- Utilisation mémoire / CPU backend
- Taille de la base de données

### Security Metrics
- Tentatives de connexion échouées
- Tokens JWT expirés
- Violations de permissions (tentatives d'accès non autorisé)
- Temps depuis dernier changement de mot de passe

---

## 🚀 Roadmap Évolution Workflows

### Court Terme (1-2 mois)
- [ ] Implémenter correctifs sécurité IAM
- [ ] Ajouter WebSocket pour notifications temps réel
- [ ] Optimiser requêtes missions avec pagination côté serveur
- [ ] Tests E2E pour workflows critiques

### Moyen Terme (3-6 mois)
- [ ] Signature électronique pour contrats
- [ ] Export PDF des candidatures
- [ ] Tableau de bord analytics pour entreprises
- [ ] API publique pour intégrations tierces

### Long Terme (6-12 mois)
- [ ] Machine Learning pour matching candidat-mission
- [ ] Application mobile (React Native)
- [ ] Multi-tenant support
- [ ] Internationalisation (i18n)

---

*Dernière mise à jour: 26 Novembre 2025*
