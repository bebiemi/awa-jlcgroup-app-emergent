# 📘 Configuration IAM - Guide Complet

## Vue d'ensemble

Le système IAM est maintenant **config-driven** : toute la configuration est centralisée dans un fichier YAML qui sert de **source de vérité unique**.

**Fichier principal:** `/app/config/iam_config.yaml`

---

## 🏗️ Structure de la Configuration

### 1. Permissions Atomiques

```yaml
permissions:
  - code: "users.view.all"
    name: "Voir tous les utilisateurs"
    resource: "users"
    action: "view"
    scope: "all"
    category: "users"
```

**Champs:**
- `code` *(requis)*: Identifiant unique de la permission
- `name` *(requis)*: Nom descriptif
- `resource` *(requis)*: Ressource concernée (users, missions, etc.)
- `action` *(requis)*: Action permise (read, write, delete, etc.)
- `scope` *(optionnel)*: Portée (all, own, organization)
- `category` *(optionnel)*: Catégorie pour regroupement

### 2. Bundles de Permissions

```yaml
bundles:
  - code: "users.manage"
    name: "Gérer les utilisateurs"
    description: "Accès complet à la gestion des utilisateurs"
    category: "users"
    permissions:
      - "users.view.all"
      - "users.create"
      - "users.edit.all"
```

**Champs:**
- `code` *(requis)*: Identifiant unique du bundle
- `name` *(requis)*: Nom du bundle
- `description` *(requis)*: Description détaillée
- `category` *(requis)*: Catégorie du bundle
- `permissions` *(requis)*: Liste des codes de permissions

### 3. Profils Système

```yaml
profiles:
  - code: "admin"
    name: "Administrateur"
    description: "Administrateur avec accès étendu"
    permissions: []          # Permissions directes (optionnel)
    bundles:                # Bundles assignés
      - "users.manage"
      - "missions.full_access"
    priority: 900           # Priorité d'affichage
    is_protected: true      # Profil système protégé
```

**Types de profils:**
- **Super Admin** : `permissions: "*"` (toutes les permissions)
- **Profil avec bundles** : `bundles: [...]`
- **Profil avec permissions directes** : `permissions: [...]`
- **Profil mixte** : bundles + permissions directes

### 4. Règles de Validation des Utilisateurs

```yaml
user_validation_rules:
  required_fields:
    - "username"
    - "email"
    - "password_hash"
    
  default_values:
    provider: "local"
    status: "pending"
    
  field_migrations:
    password: "password_hash"
    
  deprecated_fields:
    - "old_password"
```

---

## 🚀 Utilisation

### Initialisation Complète

```bash
# Initialiser depuis la configuration
python3 /app/scripts/init_iam_from_config.py

# Avec suppression des utilisateurs de test
python3 /app/scripts/init_iam_from_config.py --delete-users

# Avec configuration personnalisée
python3 /app/scripts/init_iam_from_config.py --config /path/to/custom.yaml
```

### Vérification des Utilisateurs

```bash
# Vérifier la conformité (lecture seule)
python3 /app/scripts/verify_and_align_users.py

# Vérifier et corriger
python3 /app/scripts/verify_and_align_users.py --fix

# Avec activation des admins inactifs
python3 /app/scripts/verify_and_align_users.py --fix --activate-admins
```

---

## ✏️ Modifier la Configuration

### Ajouter une Permission

1. Ouvrir `/app/config/iam_config.yaml`
2. Ajouter dans la section `permissions`:

```yaml
permissions:
  - code: "reports.generate"
    name: "Générer des rapports"
    resource: "reports"
    action: "generate"
    scope: "organization"
    category: "reports"
```

3. Exécuter: `python3 init_iam_from_config.py`

### Créer un Bundle

```yaml
bundles:
  - code: "reports.full_access"
    name: "Accès complet rapports"
    description: "Tous les droits sur les rapports"
    category: "reports"
    permissions:
      - "reports.read"
      - "reports.generate"
      - "reports.export"
```

### Créer un Profil

```yaml
profiles:
  - code: "analyst"
    name: "Analyste"
    description: "Analyste de données"
    permissions: []
    bundles:
      - "reports.full_access"
    priority: 300
    is_protected: false
```

### Modifier un Profil Existant

**Exemple: Ajouter un bundle au profil commercial**

```yaml
profiles:
  - code: "commercial"
    name: "Commercial"
    description: "Gestion des missions et entreprises"
    permissions: []
    bundles:
      - "missions.full_access"
      - "entreprises.manage"
      - "reports.full_access"  # <-- Ajouté
    priority: 500
    is_protected: false
```

Puis: `python3 init_iam_from_config.py`

---

## 🔄 Workflow de Mise à Jour

### Scénario 1: Ajouter des Permissions

1. Éditer `/app/config/iam_config.yaml`
2. Ajouter les nouvelles permissions
3. Optionnellement, créer des bundles
4. Optionnellement, assigner aux profils
5. Exécuter: `python3 init_iam_from_config.py`
6. Vérifier: `python3 verify_and_align_users.py`

### Scénario 2: Modifier un Profil

1. Éditer le profil dans `iam_config.yaml`
2. Exécuter: `python3 init_iam_from_config.py`
3. Les utilisateurs avec ce profil héritent automatiquement des nouvelles permissions

### Scénario 3: Aligner les Utilisateurs

```bash
# Vérifier l'état actuel
python3 verify_and_align_users.py

# Corriger les problèmes
python3 verify_and_align_users.py --fix
```

---

## 📊 Exemples Pratiques

### Créer un Profil "Auditeur"

```yaml
profiles:
  - code: "auditor"
    name: "Auditeur"
    description: "Accès en lecture pour audit"
    permissions:
      - "users.view.all"
      - "missions.read.all"
      - "applications.read.all"
      - "admin.audit_logs"
    bundles: []
    priority: 200
    is_protected: false
```

### Créer un Bundle "Gestion Complète RH"

```yaml
bundles:
  - code: "hr.full_access"
    name: "Gestion complète RH"
    description: "Tous les droits RH"
    category: "hr"
    permissions:
      - "users.view.all"
      - "users.create"
      - "users.edit.all"
      - "applications.read.all"
      - "applications.manage.all"
      - "documents.view_cv.all"
      - "dashboard.admin.access"
```

Puis assigner au profil `hr_manager`:

```yaml
profiles:
  - code: "hr_manager"
    name: "Responsable RH"
    description: "Gestion RH et candidatures"
    permissions: []
    bundles:
      - "hr.full_access"
    priority: 600
    is_protected: false
```

---

## 🛡️ Bonnes Pratiques

### 1. Toujours Utiliser les Bundles

❌ **Mauvais:**
```yaml
profiles:
  - code: "manager"
    permissions:
      - "users.view.all"
      - "users.create"
      - "users.edit.all"
      # ... 20 permissions
```

✅ **Bon:**
```yaml
bundles:
  - code: "users.manage"
    permissions: [...]

profiles:
  - code: "manager"
    bundles:
      - "users.manage"
```

### 2. Nommer les Permissions de Manière Cohérente

**Format:** `resource.action.scope`

- ✅ `users.view.all`
- ✅ `missions.create.own`
- ❌ `viewAllUsers`
- ❌ `mission_create`

### 3. Documenter les Profils

Toujours inclure une description claire:

```yaml
profiles:
  - code: "custom_role"
    name: "Rôle Personnalisé"
    description: "Accès limité aux missions de la région Nord uniquement"
    permissions: [...]
```

### 4. Tester Après Modifications

```bash
# 1. Appliquer les changements
python3 init_iam_from_config.py

# 2. Vérifier les utilisateurs
python3 verify_and_align_users.py

# 3. Tester la connexion
curl -X POST http://localhost:8001/api/auth/local/login \
  -d '{"username":"test","password":"..."}'
```

---

## 🔍 Dépannage

### Problème: "Section manquante dans la configuration"

**Solution:** Vérifier que le fichier YAML contient les sections `permissions`, `bundles` et `profiles`.

### Problème: Permissions non appliquées aux utilisateurs

**Solution:**
1. Vérifier que le profil est assigné à l'utilisateur
2. Réexécuter: `python3 init_iam_from_config.py`
3. Vérifier en DB:
```bash
mongosh auth_db --eval 'db.users.findOne({username: "user"}, {roles: 1, profile_ids: 1})'
```

### Problème: Champs manquants sur les utilisateurs

**Solution:**
```bash
python3 verify_and_align_users.py --fix
```

---

## 📋 Checklist de Migration

- [ ] Sauvegarder la configuration actuelle
- [ ] Éditer `/app/config/iam_config.yaml`
- [ ] Valider le YAML (syntaxe correcte)
- [ ] Tester sur environnement de dev
- [ ] Exécuter `init_iam_from_config.py`
- [ ] Vérifier les profils en DB
- [ ] Vérifier les permissions en DB
- [ ] Tester la connexion avec différents rôles
- [ ] Exécuter `verify_and_align_users.py --fix`
- [ ] Valider en production

---

## 📚 Ressources

- **Configuration:** `/app/config/iam_config.yaml`
- **Scripts:**
  - `/app/scripts/init_iam_from_config.py`
  - `/app/scripts/verify_and_align_users.py`
- **Documentation:**
  - `/app/docs/BUNDLE_PERMISSIONS.md`
  - `/app/scripts/README_SCRIPTS_IAM.md`

---

**Dernière mise à jour:** 23 Novembre 2025  
**Version:** 2.0 (Config-Driven)
