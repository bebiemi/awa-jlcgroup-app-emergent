# 🔥 Bundle Permissions - Définition Officielle

## 📖 Définition

Une **permission BUNDLE** est :

> Un groupe cohérent de permissions atomiques regroupées sous un identifiant unique, permettant d'appliquer d'un seul coup plusieurs droits liés à une même fonctionnalité ou un même domaine métier.

---

## 🎯 Pourquoi utiliser les Bundles ?

### 1. Réduire la complexité
Au lieu de gérer 50 permissions atomiques individuellement, vous appliquez un bundle :
- ✅ `users.manage`
- ✅ `missions.full_access`

### 2. Séparer les rôles des privilèges
Les **rôles** utilisent les **bundles** (pas les permissions atomiques directement).

### 3. Donner une granularité élevée sans rendre la gestion infernale
Vous exposez les permissions fines si vous voulez faire du "per-role override" tout en gardant une gestion simple.

### 4. Supporter l'extensibilité
Vous pouvez ajouter une permission atomique dans un bundle sans casser les rôles existants.

---

## 🧱 Structure Hiérarchique

### Niveau 1 : Permissions Atomiques

Droits très fins, **non utilisés directement** par les utilisateurs :

```
users.read
users.update
users.block
users.unblock
users.archive
users.delete
users.restore
```

**Caractéristiques :**
- ✔ Très bas niveau
- ✔ Gérés par les développeurs
- ✔ Rarement exposés en UI

---

### Niveau 2 : Bundles de Permissions

Regroupent plusieurs permissions atomiques.

**Exemple - Bundle `users.manage` :**

```javascript
users.manage = [
  "users.read",
  "users.update",
  "users.block",
  "users.unblock",
  "users.archive",
  "users.delete",
  "users.restore"
]
```

**Avantages :**
- ✔ 1 bundle = 7 permissions
- ✔ Les routes exigent le bundle → simple
- ✔ Les rôles incluent des bundles → ultra propre

---

### Niveau 3 : Rôles = Somme de Bundles

Les rôles héritent automatiquement de **toutes les permissions atomiques** contenues dans leurs bundles.

| Rôle | Permissions (bundles) |
|------|----------------------|
| `super_admin` | `*` (all) |
| `admin` | `users.manage`, `missions.full_access`, `config.manage` |
| `company` | `missions.assign`, `users.read` |
| `interim` | `missions.read`, `profile.edit` |

---

## 🗂 Exemples Complets de Bundles

### 🟪 MODULE : USERS

#### Permissions Atomiques
```
users.view          → Lire les utilisateurs
users.update        → Modifier un utilisateur
users.block         → Bloquer un utilisateur
users.unblock       → Débloquer un utilisateur
users.archive       → Archiver un utilisateur
users.restore       → Restaurer un utilisateur archivé
users.delete        → Suppression logique
users.delete_hard   → Suppression définitive
```

#### Bundle
```javascript
users.manage = [
  "users.view",
  "users.update",
  "users.block",
  "users.unblock",
  "users.archive",
  "users.restore",
  "users.delete"
]
```

---

### 🟧 MODULE : MISSIONS

#### Permissions Atomiques
```
missions.read       → Consulter les missions
missions.create     → Créer une mission
missions.assign     → Assigner une mission
missions.update     → Modifier une mission
missions.validate   → Valider une mission
missions.reject     → Rejeter une mission
missions.archive    → Archiver une mission
```

#### Bundle
```javascript
missions.full_access = [
  "missions.read",
  "missions.create",
  "missions.assign",
  "missions.update",
  "missions.validate",
  "missions.reject",
  "missions.archive"
]
```

---

### 🟦 MODULE : CONFIG / SYSTÈME

#### Permissions Atomiques
```
config.read              → Lire la configuration
config.update            → Modifier la configuration
config.feature_flags     → Gérer les feature flags
config.email_templates   → Gérer les templates d'email
```

#### Bundle
```javascript
config.manage = [
  "config.read",
  "config.update",
  "config.feature_flags",
  "config.email_templates"
]
```

---

### 🟩 MODULE : ADMINISTRATION GÉNÉRALE

#### Permissions Atomiques
```
admin.dashboard      → Accès au tableau de bord admin
admin.statistics     → Voir les statistiques
admin.audit_logs     → Consulter les logs d'audit
admin.rbac           → Gérer les rôles et permissions (RBAC)
```

#### Bundle
```javascript
admin.access = [
  "admin.dashboard",
  "admin.statistics",
  "admin.audit_logs",
  "admin.rbac"
]
```

---

## 🔄 Flux d'Utilisation

```
1. Développeur crée les PERMISSIONS ATOMIQUES
   ↓
2. Développeur crée les BUNDLES regroupant ces permissions
   ↓
3. Admin système crée des RÔLES utilisant ces bundles
   ↓
4. Admin assigne des RÔLES aux utilisateurs
   ↓
5. Application vérifie si l'utilisateur a le BUNDLE requis
   ↓
6. Si oui → L'utilisateur hérite de toutes les permissions atomiques du bundle
```

---

## 💡 Bonnes Pratiques

### ✅ À FAIRE
- Nommer les bundles de façon descriptive : `users.manage`, `missions.full_access`
- Garder les bundles cohérents (même domaine métier)
- Documenter chaque bundle et ses permissions atomiques
- Utiliser les bundles dans les routes et middlewares

### ❌ À ÉVITER
- Créer des bundles trop larges (ex: `app.all_permissions`)
- Mélanger des domaines métiers différents dans un bundle
- Exposer directement les permissions atomiques aux utilisateurs finaux
- Utiliser des permissions atomiques dans les routes (préférer les bundles)

---

## 📋 Checklist Implémentation

- [ ] Créer toutes les permissions atomiques en base de données
- [ ] Définir les bundles dans le code (configuration)
- [ ] Créer un système de résolution bundle → permissions atomiques
- [ ] Adapter les middlewares pour vérifier les bundles
- [ ] Créer les rôles avec leurs bundles associés
- [ ] Migrer les permissions existantes vers le système de bundles
- [ ] Documenter tous les bundles disponibles
- [ ] Créer une UI d'administration des bundles (optionnel)

---

## 🔗 Documents Connexes

- `reset_local_db_with_160_permissions.py` - Script d'initialisation des permissions atomiques
- `auth-microservice/awana_auth/core/permissions.py` - Définition des permissions
- `auth-microservice/awana_auth/middleware/rbac.py` - Vérification des permissions

---

**Dernière mise à jour :** 23 Novembre 2025  
**Version :** 1.0
