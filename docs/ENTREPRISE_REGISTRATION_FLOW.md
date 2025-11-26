# 📋 Flow d'Inscription des Entreprises

## 🎯 Vue d'Ensemble

L'inscription des entreprises suit un workflow de validation en deux temps :
1. **Inscription initiale** : Création du compte utilisateur avec statut PENDING
2. **Validation admin** : Approbation manuelle puis création automatique de l'entreprise

---

## 🔄 Flow Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSCRIPTION ENTREPRISE                        │
└─────────────────────────────────────────────────────────────────┘

1. FRONTEND : Formulaire d'inscription
   ↓
2. POST /api/auth/local/register
   │
   ├─→ Validation des données
   ├─→ Vérification unicité username/email
   ├─→ Détection du type (company_name fourni)
   ├─→ Création user (status: PENDING)
   ├─→ Assignment groupe IAM (grp.company)
   ├─→ Assignment rôle (company)
   ├─→ Création validation record
   └─→ Retour JWT (accès limité)
   
3. ADMIN : Dashboard de validation
   ↓
4. GET /api/admin/validations (liste en attente)
   ↓
5. POST /api/admin/{validation_id}/approve
   │
   ├─→ Mise à jour user (status: ACTIVE)
   ├─→ Création entreprise dans jlc_db
   ├─→ Création user_entreprise (lien)
   ├─→ Envoi email confirmation
   └─→ Mise à jour validation (status: approved)

6. UTILISATEUR : Email de confirmation
   ↓
7. LOGIN : Accès complet activé
```

---

## 📡 Endpoint Principal : POST /api/auth/local/register

### URL
```
POST https://[domain]/api/auth/local/register
```

### Headers
```json
{
  "Content-Type": "application/json"
}
```

### Body (Inscription Entreprise)
```json
{
  "username": "entreprise_test",
  "email": "contact@entreprise.com",
  "password": "SecurePassword123!",
  "full_name": "Jean Dupont",
  
  // Champs spécifiques entreprise
  "company_name": "Entreprise Test SA",
  "legal_representative": "Jean Dupont",
  "nif": "FR12345678901",
  
  // Optional: Location
  "location": {
    "country_id": "country_123",
    "province_id": "province_456",
    "city_id": "city_789"
  }
}
```

### Response Success (201)
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "username": "entreprise_test",
    "email": "contact@entreprise.com",
    "full_name": "Jean Dupont",
    "status": "pending",
    "roles": ["company"],
    "is_collaborator": false
  }
}
```

### Erreurs Possibles

**400 - Username déjà utilisé**
```json
{
  "detail": "Ce nom d'utilisateur est déjà utilisé"
}
```

**400 - Email déjà utilisé**
```json
{
  "detail": "Cet email est déjà utilisé"
}
```

---

## 🔐 Logique Implémentée

### Phase 1: Détection du Type d'Inscription

**Fichier:** `/app/auth-microservice/awana_auth_routes.py` (ligne 1302-1319)

```python
if register_data.company_name:
    # Company registration → needs validation
    user_status = UserStatus.PENDING
    assigned_role = UserRoles.COMPANY
    iam_group_code = IAMGroups.COMPANY
    logger.info(f"Company registration detected for {register_data.email}")
elif is_collaborator:
    # Collaborator email → needs validation
    user_status = UserStatus.PENDING
    assigned_role = UserRoles.COLLABORATEUR
    iam_group_code = IAMGroups.COLLABORATEUR
else:
    # Public email → candidat with immediate access
    user_status = UserStatus.ACTIVE
    assigned_role = UserRoles.CANDIDAT
    iam_group_code = IAMGroups.CANDIDAT
```

**Critères de détection:**
- ✅ `company_name` fourni → Type: COMPANY, Status: PENDING
- ✅ Email @jlcgroup.* → Type: COLLABORATEUR, Status: PENDING
- ✅ Sinon → Type: CANDIDAT, Status: ACTIVE

### Phase 2: Création de l'Utilisateur

**Actions (lignes 1322-1341):**
1. Création objet User avec:
   - `status`: PENDING (pour entreprises)
   - `roles`: ["company"]
   - `password_hash`: BCrypt du mot de passe
   - `provider`: "local"
   - `is_collaborator`: false

2. Insertion dans `auth_db.users`

### Phase 3: Assignment IAM

**Groupe IAM (lignes 1343-1365):**
```python
target_group = await db.iam_groups.find_one({"code": "grp.company"})
if target_group:
    await db.iam_groups.update_one(
        {"id": target_group["id"]},
        {"$addToSet": {"user_ids": user.id}}
    )
```

**Permissions obtenues:**
- Via le groupe `grp.company`
- Profil par défaut: `company_admin`
- Permissions limitées en attendant validation

### Phase 4: Création Validation Record

**Fichier:** `/app/auth-microservice/awana_auth_routes.py` fonction `create_validation_record()`

**Données collectées (lignes 204-230):**
```python
validation = {
    "id": str(uuid.uuid4()),
    "user_id": user.id,
    "user_email": user.email,
    "user_full_name": register_data.full_name,
    "validation_type": "company",
    "status": "pending",
    
    # Informations entreprise
    "representant_legal_nom": register_data.legal_representative or register_data.full_name,
    "representant_legal_email": register_data.email,
    
    # Détection représentant existant
    "has_existing_representant": false,
    "existing_representant_user_id": null,
    "existing_representant_entreprises": [],
    
    # Workflow
    "contact_confirmation": false,
    "rattachement_status": null,
    "rattachement_to_entreprise_id": null,
    
    # Location
    "has_location_warning": false,
    "location_warning_message": null,
    "country_name": "...",
    "province_name": "...",
    "city_name": "...",
    
    "created_at": "2025-11-24T...",
    "updated_at": "2025-11-24T..."
}
```

**Insertion dans:** `jlc_db.validations`

### Phase 5: Détection Représentant Existant

**Service:** `representant_detection_service.detect_existing_representant()`

**Logique (lignes 189-202):**
1. Recherche dans `auth_db.users` par:
   - Nom exact (full_name)
   - Email exact
2. Si trouvé, récupère:
   - `user_id` du représentant existant
   - Liste des entreprises déjà liées
3. Marque la validation avec un warning

**But:** Détecter si quelqu'un crée une 2ème entreprise pour rattachement

### Phase 6: Création du Profil

**Fonction:** `create_user_profile_if_not_exists()` (lignes 1425-1432)

**Actions:**
- Crée un profil dans `auth_db.collaborator_profiles`
- Type: "company"
- Associe au user_id

---

## 🎫 Tokens JWT

### Access Token

**Contenu (après inscription PENDING):**
```json
{
  "sub": "user_123",
  "email": "contact@entreprise.com",
  "roles": ["company"],
  "permissions": [
    "entreprises.view.own",
    "entreprises.edit.own",
    "dashboard.view.own"
  ],
  "profile_ids": ["profile_123"],
  "session_id": "session_456",
  "exp": 1732450000,
  "iat": 1732446400,
  "type": "access"
}
```

**Permissions limitées:**
- ❌ Pas d'accès aux missions
- ❌ Pas de création d'entreprise (elle n'existe pas encore)
- ✅ Vue limitée du dashboard
- ✅ Modification de son profil utilisateur

### Après Validation Admin

**Permissions étendues:**
- ✅ `missions.read.own` : Voir ses missions
- ✅ `applications.read.all` : Voir les candidatures
- ✅ `entreprises.view.own` : Voir son entreprise
- ✅ `entreprises.edit.own` : Modifier son entreprise
- ✅ `dashboard.view.own` : Tableau de bord complet

---

## 📋 Validation Admin

### Endpoint d'Approbation

```
POST /api/admin/{validation_id}/approve
```

**Fichier:** `/app/apps/api/src/presentation/routes/validation_routes.py` (ligne 97)

**Permissions requises:**
```python
current_user: User = Depends(require_permission("validations.manage", scope="all"))
```

### Logique d'Approbation

**Actions automatiques:**

1. **Mise à jour User**
   ```python
   await db.users.update_one(
       {"id": user_id},
       {"$set": {"status": "active"}}
   )
   ```

2. **Création Entreprise**
   ```python
   entreprise = {
       "id": str(uuid4()),
       "nom": validation["user_full_name"],  # Ou company_name si fourni
       "representant_legal": validation["representant_legal_nom"],
       "email": validation["user_email"],
       "nif": validation.get("nif"),
       "statut": "actif",
       "created_by": admin_user_id,
       "created_at": datetime.now(timezone.utc).isoformat()
   }
   
   await jlc_db.entreprises.insert_one(entreprise)
   ```

3. **Création Lien User-Entreprise**
   ```python
   user_entreprise = {
       "id": str(uuid4()),
       "user_id": user_id,
       "entreprise_id": entreprise_id,
       "role": "admin",
       "created_at": datetime.now(timezone.utc).isoformat()
   }
   
   await jlc_db.user_entreprises.insert_one(user_entreprise)
   ```

4. **Envoi Email de Confirmation**
   - Template: "account_approved"
   - Lien de connexion inclus

5. **Mise à jour Validation**
   ```python
   await jlc_db.validations.update_one(
       {"id": validation_id},
       {"$set": {
           "status": "approved",
           "approved_by": admin_user_id,
           "approved_at": datetime.now(timezone.utc).isoformat()
       }}
   )
   ```

---

## 🔍 Collections MongoDB Impactées

### 1. auth_db.users
```json
{
  "id": "user_123",
  "username": "entreprise_test",
  "email": "contact@entreprise.com",
  "full_name": "Jean Dupont",
  "status": "pending",  // → "active" après approbation
  "roles": ["company"],
  "is_collaborator": false,
  "password_hash": "...",
  "provider": "local",
  "created_at": "2025-11-24T10:00:00Z"
}
```

### 2. auth_db.iam_groups
```json
{
  "id": "group_company",
  "code": "grp.company",
  "name": "Groupe Entreprises",
  "user_ids": ["user_123", "user_456", ...],  // user ajouté ici
  "profile_ids": ["profile_company_admin"],
  "updated_at": "2025-11-24T10:00:01Z"
}
```

### 3. jlc_db.validations
```json
{
  "id": "validation_789",
  "user_id": "user_123",
  "user_email": "contact@entreprise.com",
  "validation_type": "company",
  "status": "pending",  // → "approved" après validation
  "representant_legal_nom": "Jean Dupont",
  "representant_legal_email": "contact@entreprise.com",
  "has_existing_representant": false,
  "contact_confirmation": false,
  "created_at": "2025-11-24T10:00:02Z"
}
```

### 4. jlc_db.entreprises (créé après approbation)
```json
{
  "id": "entreprise_456",
  "nom": "Entreprise Test SA",
  "representant_legal": "Jean Dupont",
  "email": "contact@entreprise.com",
  "nif": "FR12345678901",
  "statut": "actif",
  "created_by": "admin_user_id",
  "created_at": "2025-11-24T11:00:00Z"
}
```

### 5. jlc_db.user_entreprises (lien créé après approbation)
```json
{
  "id": "link_789",
  "user_id": "user_123",
  "entreprise_id": "entreprise_456",
  "role": "admin",
  "created_at": "2025-11-24T11:00:01Z"
}
```

---

## ⚡ Points Clés

### ✅ Ce qui fonctionne bien

1. **Séparation claire** : User créé immédiatement, entreprise créée après validation
2. **Sécurité** : Status PENDING empêche l'accès complet avant validation
3. **Traçabilité** : Validation record conserve toute l'historique
4. **Détection doublons** : Vérification représentant existant

### ⚠️ Points d'attention

1. **Entreprise non créée immédiatement**
   - L'utilisateur ne peut pas voir "son" entreprise tant qu'elle n'est pas approuvée
   - Peut créer confusion UX

2. **Permissions limitées en PENDING**
   - L'utilisateur a un accès très limité
   - Dashboard peut sembler vide

3. **Validation manuelle obligatoire**
   - Pas de création automatique d'entreprise
   - Dépend de la disponibilité admin

### 🔄 Améliorations Possibles

1. **Auto-validation conditionnelle**
   - Valider automatiquement si email vérifié + NIF valide
   - Rester en validation manuelle si données suspectes

2. **Pré-création entreprise en draft**
   - Créer l'entreprise en statut "draft" dès l'inscription
   - Passer en "actif" après validation
   - Permettrait à l'utilisateur de voir/modifier son entreprise

3. **Notifications temps réel**
   - WebSocket pour notifier l'utilisateur de l'approbation
   - Pas besoin d'attendre l'email

---

## 🧪 Tests

### Test 1: Inscription Entreprise

```bash
curl -X POST "http://localhost:8001/api/auth/local/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_company",
    "email": "test@company.com",
    "password": "Test123!",
    "full_name": "Test User",
    "company_name": "Test Company SA",
    "nif": "FR123456789"
  }'
```

**Vérifications:**
```bash
# 1. User créé avec status PENDING
mongo auth_db --eval 'db.users.findOne({email: "test@company.com"})'

# 2. Validation record créée
mongo jlc_db --eval 'db.validations.findOne({user_email: "test@company.com"})'

# 3. User dans groupe IAM
mongo auth_db --eval 'db.iam_groups.findOne({code: "grp.company"})'
```

### Test 2: Token Permissions

```bash
# Extraire et décoder le JWT
TOKEN="eyJhbGc..."
echo $TOKEN | cut -d. -f2 | base64 -d | jq .
```

**Vérifier:**
- `roles` contient "company"
- `permissions` limitées (view.own, edit.own)
- `status` non présent dans token (vérification côté serveur)

---

## 📚 Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `/app/auth-microservice/awana_auth_routes.py` | Endpoint d'inscription (ligne 1247) |
| `/app/auth-microservice/services/representant_detection_service.py` | Détection doublons représentant |
| `/app/apps/api/src/presentation/routes/validation_routes.py` | Endpoints validation admin |
| `/app/auth-microservice/awana_auth/core/iam_constants.py` | Constantes IAM (rôles, groupes) |

---

*Documentation générée le 24 Novembre 2025*
