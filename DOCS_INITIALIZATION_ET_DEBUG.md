# 📚 Documentation - Initialisation et Débogage

## Table des Matières

1. [Initialisation Complète de l'Application](#initialisation-complète-de-lapplication)
2. [Problème de Connexion Local Docker - Post-Mortem](#problème-de-connexion-local-docker---post-mortem)
3. [Collections MongoDB Requises](#collections-mongodb-requises)
4. [Procédures de Maintenance](#procédures-de-maintenance)
5. [Résolution des Problèmes Courants](#résolution-des-problèmes-courants)

---

## 1. Initialisation Complète de l'Application

### 🎯 Objectif

Initialiser toutes les collections MongoDB et les données de base nécessaires au fonctionnement de l'application JLC après la création du super utilisateur.

### 📋 Pré-requis

- Docker et Docker Compose installés
- Conteneurs MongoDB et Auth démarrés
- Super utilisateur créé (`adminbe`)

### 🚀 Procédure d'Initialisation

#### Étape 1: Vérifier l'état des conteneurs

```bash
# Vérifier que les conteneurs sont démarrés
docker ps

# Vous devriez voir :
# - jlc-mongo (MongoDB)
# - jlc-auth-dev (Backend Auth)
# - jlc-web (Frontend - optionnel)
```

#### Étape 2: Exécuter le script d'initialisation complet

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/complete_database_initialization.py
```

**Ce script crée automatiquement :**

✅ **Collections Legacy :**
- `permissions` - Permissions système (users, missions, contracts, IAM, admin, reports)
- `profiles` - Profils utilisateurs (super_admin, admin, company, interim, candidat)
- `groups` - Groupes d'utilisateurs

✅ **Collections IAM (Nouveau Système) :**
- `iam_permissions` - Permissions granulaires du nouveau système IAM
- `iam_profiles` - Profils IAM (role.super_admin, role.admin, role.candidat, role.company)
- `iam_groups` - Groupes IAM (grp.super_admin, grp.admin, grp.candidat, grp.company)

✅ **Collections Système :**
- `system_references` - Références système (statuts utilisateurs, statuts missions, rôles)
- `locations` - Données géographiques (pays, provinces, villes)
- `validations` - Validations des utilisateurs

✅ **Collections Existantes (mises à jour) :**
- `users` - Utilisateurs (champs IAM ajoutés)
- `audit_logs` - Journaux d'audit
- `sessions` - Sessions utilisateurs

#### Étape 3: Vérifier l'initialisation

```bash
# Se connecter à MongoDB
docker exec -it jlc-mongo mongosh

# Dans mongosh :
use auth_db
show collections

# Vérifier le nombre de documents par collection
db.permissions.countDocuments()
db.profiles.countDocuments()
db.iam_permissions.countDocuments()
db.iam_profiles.countDocuments()
db.iam_groups.countDocuments()
db.system_references.countDocuments()

# Vérifier que le super_admin a bien tous les accès
db.users.findOne({username: "adminbe"})
db.iam_groups.findOne({code: "grp.super_admin"})
```

#### Étape 4: Tester la connexion et l'accès IAM

```bash
# Test de connexion
curl -X POST http://localhost:8001/auth-api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adminbe",
    "password": "Awana2025!"
  }'

# Devrait retourner un token JWT
```

### 📊 Résultat Attendu

```
============================================================
 ✅ INITIALISATION TERMINÉE AVEC SUCCÈS
============================================================

📊 Résumé:
   ✓ Permissions (Legacy): 30
   ✓ Profils (Legacy): 5
   ✓ Groupes (Legacy): 1
   ✓ Permissions IAM: 12
   ✓ Profils IAM: 4
   ✓ Groupes IAM: 4
   ✓ Références Système: 14
   ✓ Collections: 12
```

### 🔄 Scripts d'Initialisation Spécifiques

Si vous avez besoin d'initialiser uniquement certaines parties :

```bash
# Initialisation IAM uniquement
docker exec jlc-auth-dev python /app/auth-microservice/scripts/initialize_iam_system.py

# Initialisation des domaines d'emails
docker exec jlc-auth-dev python /app/auth-microservice/scripts/initialize_email_domains.py

# Initialisation des statuts utilisateurs
docker exec jlc-auth-dev python /app/auth-microservice/scripts/initialize_user_status_references.py

# Initialisation du système candidat
docker exec jlc-auth-dev python /app/auth-microservice/scripts/initialize_candidat_iam.py
```

---

## 2. Problème de Connexion Local Docker - Post-Mortem

### 🐛 Symptôme

Échec de la connexion avec le message :
```json
{
  "detail": "Incorrect username or password"
}
```

**Credentials utilisés :**
- Username: `adminbe`
- Password: `Awana2025!`

### 🔍 Cause Racine

Le champ `status` de l'utilisateur `adminbe` était à `None` au lieu de `"active"`.

**Contexte technique :**

Dans le fichier `/app/auth-microservice/awana_auth_routes.py`, ligne 820, le code vérifie :

```python
if user_status != UserStatus.ACTIVE.value:  # UserStatus.ACTIVE.value = "active"
    logger.warning(f"Login attempt for inactive user...")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Account is not active"
    )
```

Lorsque `user_status = None`, la condition `None != "active"` est vraie, ce qui déclenche le rejet de la connexion.

### 🛠️ Solution Appliquée

Le script `diagnose_and_fix_login.py` a corrigé automatiquement le problème en :

1. Détectant que `status` était `None`
2. Mettant à jour le document utilisateur pour définir `status: "active"`
3. Vérifiant que `is_active: true` et `is_verified: true`
4. Validant le hash du mot de passe

```python
await db.users.update_one(
    {"_id": user_doc["_id"]},
    {"$set": {"status": "active"}}
)
```

### 📝 Problèmes Secondaires Identifiés

#### 1. Doublon de champs de mot de passe

Le document utilisateur contenait **deux champs** :
- `password_hash` : Utilisé par le code
- `hashed_password` : Doublon non utilisé

**Recommandation :** Nettoyer le champ `hashed_password` pour éviter la confusion.

```bash
# Script de nettoyage
docker exec jlc-mongo mongosh << 'EOF'
use auth_db
db.users.updateMany(
  { hashed_password: { $exists: true } },
  { $unset: { hashed_password: "" } }
)
EOF
```

#### 2. Champ `provider` manquant

Dans certains cas, le champ `provider` peut être manquant ou incorrect.

**Le code recherche :**
```python
user_doc = await db.users.find_one({
    "$or": [
        {"username": username},
        {"email": username}
    ],
    "provider": AuthProviderEnum.LOCAL.value  # "local"
}, {"_id": 0})
```

**Solution :** Le script de diagnostic corrige automatiquement :
```python
await db.users.update_one(
    {"_id": user_doc["_id"]},
    {"$set": {"provider": "local"}}
)
```

### 🎯 Prévention

Pour éviter ce problème à l'avenir :

1. **Toujours définir le `status` lors de la création d'utilisateur**

```python
user = User(
    username="...",
    email="...",
    status=UserStatus.ACTIVE,  # ✅ Important !
    ...
)
```

2. **Utiliser le script de validation avant mise en production**

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/diagnose_and_fix_login.py
```

3. **Contrôles de qualité sur les scripts de création d'utilisateurs**

Vérifier que tous les scripts incluent les champs obligatoires :
- `status: "active"`
- `provider: "local"`
- `is_active: true`
- `is_verified: true`
- `password_hash` (pas `hashed_password`)

### 📚 Scripts de Diagnostic Disponibles

```bash
# Diagnostic complet avec corrections automatiques
docker exec jlc-auth-dev python /app/auth-microservice/scripts/diagnose_and_fix_login.py

# Test détaillé sans modification
docker exec jlc-auth-dev python /app/auth-microservice/scripts/test_login_detailed.py

# Vérification rapide
docker exec jlc-auth-dev python /app/auth-microservice/scripts/check_adminbe_user.py
```

Documentation détaillée : `/app/auth-microservice/scripts/README_DOCKER_DEBUG.md`

---

## 3. Collections MongoDB Requises

### 📦 Vue d'Ensemble

L'application JLC nécessite **12 collections principales** dans la base de données `auth_db` :

| Collection | Description | Créée par |
|------------|-------------|-----------|
| `users` | Utilisateurs de l'application | Système |
| `permissions` | Permissions système (legacy) | Script init |
| `profiles` | Profils utilisateurs (legacy) | Script init |
| `groups` | Groupes d'utilisateurs (legacy) | Script init |
| `iam_permissions` | Permissions IAM (nouveau) | Script init |
| `iam_profiles` | Profils IAM (nouveau) | Script init |
| `iam_groups` | Groupes IAM (nouveau) | Script init |
| `system_references` | Références système | Script init |
| `audit_logs` | Journaux d'audit | Système |
| `sessions` | Sessions utilisateurs | Système |
| `locations` | Données géographiques | Import |
| `validations` | Validations utilisateurs | Inscription |

### 🗂️ Structure Détaillée

#### `users`
```javascript
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "password_hash": "string",  // bcrypt hash
  "provider": "local" | "entraid",
  "status": "active" | "pending" | "suspended" | "inactive",
  "roles": ["super_admin", "admin", "company", "interim", "candidat"],
  "is_active": true,
  "is_verified": true,
  "profile_ids": ["uuid"],  // Legacy IAM
  "group_ids": ["uuid"],    // Legacy IAM
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "last_login_at": "ISO datetime"
}
```

#### `iam_permissions`
```javascript
{
  "id": "uuid",
  "code": "perm.candidat.view_missions",
  "name": "Voir les missions",
  "resource": "missions",
  "action": "read",
  "scope": "all" | "own",
  "category": "missions",
  "is_system": true,
  "created_at": "ISO datetime"
}
```

#### `iam_profiles`
```javascript
{
  "id": "uuid",
  "code": "role.super_admin",
  "name": "Super Admin",
  "description": "Accès complet",
  "permission_ids": ["uuid"],
  "is_system_role": true,
  "color": "#DC2626",
  "icon": "shield-check",
  "created_at": "ISO datetime"
}
```

#### `iam_groups`
```javascript
{
  "id": "uuid",
  "code": "grp.super_admin",
  "name": "Super Administrateurs",
  "description": "Groupe des super administrateurs",
  "profile_ids": ["uuid"],
  "user_ids": ["uuid"],
  "is_system_group": true,
  "is_protected": true,
  "parent_group_id": null,
  "created_at": "ISO datetime"
}
```

#### `system_references`
```javascript
{
  "id": "uuid",
  "category": "user_status" | "mission_status" | "roles",
  "code": "active",
  "name": "Actif",
  "description": "Utilisateur actif",
  "is_hidden_from_admins": false,
  "created_at": "ISO datetime"
}
```

### 📊 Requêtes Utiles

```javascript
// Vérifier toutes les collections
use auth_db
show collections

// Compter les documents
db.users.countDocuments()
db.permissions.countDocuments()
db.iam_permissions.countDocuments()

// Trouver tous les super_admins
db.users.find({roles: "super_admin"})

// Lister tous les groupes IAM
db.iam_groups.find({}, {code: 1, name: 1, user_ids: 1})

// Vérifier les permissions d'un profil
db.iam_profiles.aggregate([
  { $match: { code: "role.super_admin" } },
  {
    $lookup: {
      from: "iam_permissions",
      localField: "permission_ids",
      foreignField: "id",
      as: "permissions"
    }
  }
])
```

---

## 4. Procédures de Maintenance

### 🔧 Nettoyage des Doublons

#### Supprimer le champ `hashed_password` en doublon

```bash
docker exec jlc-mongo mongosh << 'EOF'
use auth_db
db.users.updateMany(
  { hashed_password: { $exists: true } },
  { $unset: { hashed_password: "" } }
)
EOF
```

#### Synchroniser les permissions du super_admin

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/sync_superadmin_permissions.py
```

### 🔄 Réinitialisation Complète

**⚠️ ATTENTION : Cette opération supprime toutes les données !**

```bash
# Arrêter les conteneurs
docker-compose down

# Supprimer les volumes
docker volume rm jlc_mongo_data

# Redémarrer
docker-compose up -d

# Attendre que MongoDB soit prêt (30 secondes)
sleep 30

# Réinitialiser
docker exec jlc-auth-dev python /app/auth-microservice/scripts/complete_database_initialization.py
```

### 📥 Backup et Restauration

#### Backup

```bash
# Backup complet
docker exec jlc-mongo mongodump --db auth_db --out /backup

# Copier le backup localement
docker cp jlc-mongo:/backup ./mongodb_backup_$(date +%Y%m%d)
```

#### Restauration

```bash
# Copier le backup dans le conteneur
docker cp ./mongodb_backup_YYYYMMDD jlc-mongo:/backup

# Restaurer
docker exec jlc-mongo mongorestore --db auth_db /backup/auth_db
```

---

## 5. Résolution des Problèmes Courants

### ❌ Erreur 500 sur l'interface IAM

**Cause :** Collections IAM manquantes (`iam_permissions`, `iam_profiles`, `iam_groups`)

**Solution :**
```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/complete_database_initialization.py
```

### ❌ "Incorrect username or password"

**Causes possibles :**
1. `status` n'est pas `"active"`
2. `password_hash` manquant ou incorrect
3. `provider` n'est pas `"local"`

**Solution :**
```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/diagnose_and_fix_login.py
```

### ❌ Permissions manquantes pour le super_admin

**Cause :** Nouvelles permissions créées mais pas ajoutées au profil super_admin

**Solution :**
```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/sync_superadmin_permissions.py
```

### ❌ Backend ne démarre pas

**Diagnostics :**

```bash
# Vérifier les logs
docker logs jlc-auth-dev

# Vérifier que MongoDB est accessible
docker exec jlc-auth-dev python -c "from motor.motor_asyncio import AsyncIOMotorClient; import os; print(os.getenv('MONGO_URL'))"

# Tester la connexion MongoDB
docker exec jlc-auth-dev python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
async def test():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    print(await client.server_info())
asyncio.run(test())
"
```

### ❌ Frontend ne se connecte pas au backend

**Vérifications :**

1. Vérifier `REACT_APP_BACKEND_URL` dans `/app/apps/web/.env`
2. Vérifier le proxy Vite dans `/app/apps/web/vite.config.ts`
3. Tester l'API directement :

```bash
curl http://localhost:8001/auth-api/health
```

### 📞 Support

Pour tout problème non résolu :

1. **Capturer les logs :**
   ```bash
   docker logs jlc-auth-dev > auth_logs.txt 2>&1
   docker logs jlc-mongo > mongo_logs.txt 2>&1
   ```

2. **Exporter l'état de la base de données :**
   ```bash
   docker exec jlc-auth-dev python /app/auth-microservice/scripts/check_adminbe_user.py > user_state.txt
   ```

3. **Vérifier les collections :**
   ```bash
   docker exec jlc-mongo mongosh --eval "use auth_db; db.getCollectionNames()" > collections.txt
   ```

---

## 📚 Ressources Additionnelles

- **Scripts disponibles :** `/app/auth-microservice/scripts/`
- **Guide de débogage connexion :** `/app/auth-microservice/scripts/README_DOCKER_DEBUG.md`
- **Code source IAM :** `/app/auth-microservice/awana_auth/services/iam_service.py`
- **Routes d'authentification :** `/app/auth-microservice/awana_auth_routes.py`

---

**Dernière mise à jour :** 2025-01-XX  
**Version de l'application :** 1.0  
**Créé par :** Agent E1 (Fork)
