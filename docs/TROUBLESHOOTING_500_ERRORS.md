# 🔧 Résolution des Erreurs 500 - Guide Complet

## Vue d'ensemble

Les erreurs 500 sur les accès aux permissions et l'authentification étaient causées par plusieurs problèmes interconnectés dans le système IAM.

---

## 🐛 Problèmes Identifiés

### 1. Champs Utilisateurs Incorrects ou Manquants

#### Symptômes
```
500 Internal Server Error
KeyError: 'password_hash'
AttributeError: 'NoneType' object has no attribute 'get'
```

#### Causes Racines
- **Champ `password` au lieu de `password_hash`** : Les scripts legacy créaient les utilisateurs avec le mauvais nom de champ
- **Champ `provider` manquant** : Requis pour l'authentification locale
- **Champs de statut incohérents** : `status: null`, `is_active: null`, `is_verified: null`
- **Champs `roles` vide ou mal formé** : `roles: []` au lieu de `roles: ["role_name"]`

#### Solution Appliquée

**Script de correction :** `/app/scripts/verify_and_align_users.py`

```python
# Migration automatique des champs
db.users.updateMany(
  { password: { $exists: true } },
  {
    $rename: { "password": "password_hash" },
    $set: { 
      "provider": "local",
      "updated_at": new Date()
    }
  }
)

# Ajout des champs manquants avec valeurs par défaut
db.users.updateMany(
  { status: { $exists: false } },
  {
    $set: {
      "status": "pending",
      "is_active": false,
      "is_verified": false,
      "provider": "local"
    }
  }
)
```

**Règles de validation définies dans :** `/app/config/iam_config.yaml`

```yaml
user_validation_rules:
  required_fields:
    - username
    - email
    - password_hash
    - provider
    - status
    - is_active
    - roles
    
  default_values:
    provider: "local"
    status: "pending"
    is_active: false
    is_verified: false
    roles: []
    
  field_migrations:
    password: "password_hash"
```

---

### 2. Permissions Manquantes sur les Profils

#### Symptômes
```
403 Forbidden
"detail": "Vous n'avez pas la permission de consulter les missions"
500 Internal Server Error (lors de la vérification des permissions)
```

#### Causes Racines
- **Profils système vides** : Les profils `commercial`, `company_admin`, etc. avaient `permissions: []`
- **Bundles non résolus** : Les bundles existaient mais n'étaient pas convertis en permissions atomiques
- **Profils non assignés** : Utilisateurs avec `profile_ids: []`

#### Solution Appliquée

**Script unifié :** `/app/scripts/init_iam_from_config.py`

```python
# Résolution automatique des permissions depuis les bundles
for profile in profiles_config:
    if profile['permissions'] == "*":
        # Super Admin: toutes les permissions
        profile_permissions = all_permission_codes.copy()
    else:
        profile_permissions = profile['permissions'].copy()
        
        # Ajouter les permissions des bundles
        for bundle_code in profile.get('bundles', []):
            if bundle_code in bundles_map:
                profile_permissions.extend(bundles_map[bundle_code])
    
    # Supprimer les doublons
    profile_permissions = list(set(profile_permissions))
```

**Exemple - Profil Commercial avant/après :**

```python
# AVANT (cassé)
{
  "code": "commercial",
  "permissions": [],
  "bundles": ["missions.full_access", "entreprises.manage"]
}
# → Erreur 500 car pas de permissions réelles

# APRÈS (corrigé)
{
  "code": "commercial",
  "permissions": [
    "missions.read.all",
    "missions.create",
    "missions.update",
    "missions.assign",
    "missions.validate",
    "missions.reject",
    "missions.archive",
    "missions.publish",
    "missions.cancel",
    "entreprises.view.all",
    "entreprises.create",
    "entreprises.edit.all",
    "entreprises.delete",
    "entreprises.validate",
    "entreprises.approve"
  ],
  "bundles": ["missions.full_access", "entreprises.manage"]
}
# → 15 permissions résolues depuis les bundles
```

---

### 3. Problèmes de Sérialisation MongoDB

#### Symptômes
```
500 Internal Server Error
TypeError: Object of type ObjectId is not JSON serializable
```

#### Causes Racines
- **ObjectId MongoDB (`_id`) non exclu** : Les requêtes retournaient `_id` qui ne peut pas être sérialisé en JSON
- **Dates non converties** : Objets `datetime` Python non convertis en ISO string

#### Solution Appliquée

**Dans toutes les requêtes MongoDB :**

```python
# ❌ AVANT (cassé)
user = await db.users.find_one({"username": username})
# → Retourne _id (ObjectId) → Erreur 500 lors de la sérialisation

# ✅ APRÈS (corrigé)
user = await db.users.find_one(
    {"username": username},
    {"_id": 0}  # Exclure _id
)

# ✅ Pour les listes
users = await db.users.find({}, {"_id": 0}).to_list(1000)

# ✅ Avec Pydantic (solution robuste)
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    
    class Config:
        populate_by_name = True
```

**Documentation ajoutée dans les commentaires de code :**

```python
# MongoDB + Pydantic ObjectId Handling
# Toujours exclure _id des requêtes ou utiliser Pydantic
# Exemple:
#   user = await db.users.find_one({"id": user_id}, {"_id": 0})
```

---

### 4. Comptes Admin Inactifs

#### Symptômes
```
401 Unauthorized
"detail": "Account is not active"
```

#### Causes Racines
- **Status non défini** : `status: null` au lieu de `"active"`
- **is_active = false** : Même pour les super_admin
- **Script legacy** : Créait les comptes sans les activer

#### Solution Appliquée

**Activation automatique des admins :**

```python
# Dans init_iam_from_config.py
result = await db.users.update_many(
    {
        "roles": "super_admin",
        "$or": [
            {"status": {"$ne": "active"}},
            {"is_active": {"$ne": True}}
        ]
    },
    {
        "$set": {
            "status": "active",
            "is_active": True,
            "is_verified": True,
            "email_verified": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }
)
```

**Règle automatique dans la config :**

```yaml
user_validation_rules:
  active_user_requirements:
    status: "active"
    is_active: true
    is_verified: true
```

---

### 5. Routes Backend Incorrectes

#### Symptômes
```
404 Not Found
POST /api/auth/login → 404
```

#### Causes Racines
- **Route incorrecte** : `/api/auth/login` n'existait pas
- **Route correcte** : `/api/auth/local/login`

#### Solution
Identification de la bonne route dans les logs et mise à jour des tests.

---

## 🔧 Outils de Correction Créés

### 1. Script de Vérification et Alignement

**Fichier :** `/app/scripts/verify_and_align_users.py`

**Fonctionnalités :**
- ✅ Détecte tous les champs manquants
- ✅ Détecte les migrations nécessaires (password → password_hash)
- ✅ Détecte les champs obsolètes
- ✅ Détecte les comptes admin inactifs
- ✅ Applique les corrections automatiquement

**Usage :**
```bash
# Vérifier seulement
python3 verify_and_align_users.py

# Corriger automatiquement
python3 verify_and_align_users.py --fix

# Avec activation des admins
python3 verify_and_align_users.py --fix --activate-admins
```

### 2. Script d'Initialisation IAM Unifié

**Fichier :** `/app/scripts/init_iam_from_config.py`

**Fonctionnalités :**
- ✅ Crée les permissions atomiques
- ✅ Crée les bundles
- ✅ Résout les bundles en permissions pour chaque profil
- ✅ Crée/met à jour les profils système
- ✅ Aligne automatiquement les utilisateurs existants
- ✅ Active les comptes admin
- ✅ Corrige les champs legacy

### 3. Script de Correction des Configs

**Fichier :** `/app/scripts/ensure_app_configs.py`

**Fonctionnalités :**
- ✅ Crée les configurations app manquantes (ex: profiles.badge_new_user)
- ✅ Prévient les erreurs 404 sur les configs

---

## 📊 Méthode de Diagnostic

### Étape 1 : Identifier le Type d'Erreur

```bash
# Logs backend
tail -f /var/log/supervisor/backend.err.log

# Types d'erreurs courants
# KeyError → Champ manquant
# AttributeError → Objet None
# TypeError → Sérialisation (ObjectId)
# 401 → Authentification
# 403 → Permissions
# 500 → Erreur serveur (vérifier logs)
```

### Étape 2 : Vérifier les Utilisateurs

```bash
# Vérifier un utilisateur en DB
mongosh auth_db --eval 'db.users.findOne({username: "commercial1"})'

# Vérifier les champs requis
mongosh auth_db --eval '
db.users.find({}, {
  username: 1,
  password_hash: 1,
  provider: 1,
  status: 1,
  is_active: 1,
  roles: 1,
  _id: 0
}).limit(5)
'

# Trouver les utilisateurs avec champs manquants
mongosh auth_db --eval '
db.users.find({
  $or: [
    {password_hash: {$exists: false}},
    {provider: {$exists: false}},
    {status: {$exists: false}}
  ]
}, {username: 1, _id: 0})
'
```

### Étape 3 : Vérifier les Profils

```bash
# Vérifier les permissions d'un profil
mongosh auth_db --eval '
db.profiles.findOne(
  {code: "commercial"},
  {code: 1, permissions: 1, bundles: 1, _id: 0}
)
'

# Compter les profils sans permissions
mongosh auth_db --eval '
db.profiles.countDocuments({
  permissions: {$size: 0},
  bundles: {$size: 0}
})
'
```

### Étape 4 : Tester l'API

```bash
# Test de connexion
curl -X POST http://localhost:8001/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Awana2025!"}'

# Test d'accès à une ressource protégée
TOKEN="..." # Token obtenu ci-dessus
curl -X GET http://localhost:8001/api/missions \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛠️ Workflow de Correction

### Correction Rapide (Problème Mineur)

```bash
# 1. Vérifier les utilisateurs
python3 verify_and_align_users.py

# 2. Corriger automatiquement
python3 verify_and_align_users.py --fix --activate-admins

# 3. Tester
curl -X POST http://localhost:8001/api/auth/local/login \
  -d '{"username":"admin","password":"Awana2025!"}'
```

### Réinitialisation Complète (Problème Majeur)

```bash
# 1. Sauvegarder les données importantes
mongodump --db=auth_db --collection=users --out=/tmp/backup

# 2. Réinitialiser IAM
python3 init_iam_from_config.py

# 3. Vérifier et corriger les utilisateurs
python3 verify_and_align_users.py --fix

# 4. Vérifier les configs
python3 ensure_app_configs.py

# 5. Tester
python3 verify_and_align_users.py  # Doit afficher "tous conformes"
```

---

## 📋 Checklist de Prévention

### Avant de Créer un Utilisateur

- [ ] Utiliser `password_hash` (pas `password`)
- [ ] Définir `provider: "local"`
- [ ] Définir `status: "active"` ou `"pending"`
- [ ] Définir `is_active`, `is_verified`, `email_verified`
- [ ] Assigner au moins un rôle : `roles: ["role_name"]`
- [ ] Assigner un profil : `profile_ids: ["profile_id"]`
- [ ] Exclure `_id` dans les requêtes API : `{"_id": 0}`

### Après Modification des Profils

- [ ] Exécuter `init_iam_from_config.py`
- [ ] Vérifier que les permissions sont résolues
- [ ] Tester avec un utilisateur de ce profil
- [ ] Vérifier les logs pour les erreurs 500

### Scripts à Exécuter Régulièrement

```bash
# Tous les jours (automatiser via cron)
python3 verify_and_align_users.py --fix

# Après chaque modification de config IAM
python3 init_iam_from_config.py

# Après ajout de nouvelles configs app
python3 ensure_app_configs.py
```

---

## 🎯 Résumé des Solutions

| Problème | Cause | Solution | Script |
|----------|-------|----------|--------|
| KeyError: 'password_hash' | Champ `password` au lieu de `password_hash` | Migration automatique | `verify_and_align_users.py --fix` |
| 401 Account not active | Comptes inactifs | Activation auto des admins | `init_iam_from_config.py` |
| 403 Permission denied | Profils sans permissions | Résolution des bundles | `init_iam_from_config.py` |
| 500 ObjectId serialization | `_id` non exclu | `{"_id": 0}` dans queries | Code backend |
| 404 /api/auth/login | Route incorrecte | Utiliser `/api/auth/local/login` | Tests |
| 404 profiles.badge_new_user | Config manquante | Créer la config | `ensure_app_configs.py` |

---

## 💡 Leçons Apprises

1. **Toujours valider les champs utilisateurs** avant de les utiliser
2. **Exclure systématiquement `_id`** dans les requêtes MongoDB
3. **Résoudre les bundles en permissions** lors de la création des profils
4. **Utiliser les scripts d'alignement** après chaque modification
5. **Tester avec différents rôles** (pas seulement super_admin)
6. **Documenter les champs requis** dans la configuration YAML
7. **Automatiser les vérifications** avec des scripts

---

**Date de dernière mise à jour :** 23 Novembre 2025  
**Version :** 1.0
