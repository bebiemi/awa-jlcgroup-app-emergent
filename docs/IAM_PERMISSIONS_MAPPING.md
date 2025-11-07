# IAM Permissions Mapping Guide

Ce document définit le mapping entre les anciens rôles et les nouvelles permissions IAM.

## 📋 Structure des Permissions

Format: `resource.action`

Exemples:
- `users.read` - Lire les utilisateurs
- `users.manage` - Gérer les utilisateurs (CRUD complet)
- `missions.create` - Créer des missions
- `admin.access` - Accès administrateur

## 🔐 Profils Système Intégrés

### SuperAdmin
**Code:** `super_admin`
**Permissions:** Toutes les permissions (bypass)
**Description:** Accès complet au système

### Admin  
**Code:** `admin`
**Permissions:**
- `users.read`
- `users.manage` 
- `groups.manage`
- `locations.manage`
- `validations.manage`
- `missions.manage`
- `references.manage`
- `rules.manage`
- `config.manage`
- `emails.manage`

### Interim
**Code:** `interim`
**Permissions:**
- `missions.browse` - Consulter les offres
- `missions.apply` - Postuler aux missions
- `applications.read_own` - Voir ses candidatures
- `profile.manage_own` - Gérer son profil

### Company
**Code:** `company`
**Permissions:**
- `missions.create` - Créer des missions
- `missions.read_own` - Voir ses missions
- `missions.edit_own` - Modifier ses missions
- `applications.read_own` - Voir les candidatures
- `profile.manage_own` - Gérer son profil

### Commercial
**Code:** `commercial`
**Permissions:**
- `missions.manage` - Gérer toutes les missions
- `applications.manage` - Gérer les candidatures
- `validations.perform` - Valider des éléments
- `users.read` - Voir les utilisateurs

### Validator
**Code:** `validator`
**Permissions:**
- `validations.perform` - Valider des éléments
- `applications.review` - Examiner les candidatures

## 🗺️ Mapping Rôles → Permissions

### Module: Users Management

| Ancien Check | Nouveau Check IAM |
|--------------|-------------------|
| `if "admin" in user.roles` | `await checker.user_has_permission(user_id, "users.manage")` |
| `if "super_admin" in user.roles` | `await checker.user_has_permission(user_id, "admin.access")` |

**Endpoints à migrer:**
- `GET /auth/users` → `users.read`
- `POST /auth/users` → `users.create`
- `PATCH /auth/users/{id}` → `users.edit`
- `DELETE /auth/users/{id}` → `users.delete`
- `PATCH /auth/users/{id}/status` → `users.manage_status`

### Module: Missions

| Ancien Check | Nouveau Check IAM |
|--------------|-------------------|
| `if role in ["admin", "commercial", "company"]` | `await checker.user_has_any_permission(user_id, ["missions.manage", "missions.create"])` |

**Endpoints à migrer:**
- `GET /missions` → `missions.read` or `missions.browse`
- `POST /missions` → `missions.create`
- `PUT /missions/{id}` → `missions.edit`
- `DELETE /missions/{id}` → `missions.delete`
- `POST /missions/{id}/publish` → `missions.publish`

### Module: Validations

| Ancien Check | Nouveau Check IAM |
|--------------|-------------------|
| `if role in ["admin", "validator", "commercial"]` | `await checker.user_has_permission(user_id, "validations.perform")` |

**Endpoints à migrer:**
- `GET /validations` → `validations.read`
- `POST /validations/{id}/approve` → `validations.approve`
- `POST /validations/{id}/reject` → `validations.reject`

### Module: Email Settings

| Ancien Check | Nouveau Check IAM |
|--------------|-------------------|
| `if "super_admin" not in user.roles` | `await checker.user_has_permission(user_id, "emails.configure")` |

**Endpoints à migrer:**
- `GET /api/emails/config` → `emails.read_config`
- `PATCH /api/emails/config` → `emails.configure`
- `POST /api/emails/test` → `emails.test`

### Module: IAM (New)

**Permissions:**
- `iam.permissions.read` - Lire les permissions
- `iam.permissions.manage` - Gérer les permissions
- `iam.profiles.read` - Lire les profils
- `iam.profiles.manage` - Gérer les profils
- `iam.groups.read` - Lire les groupes
- `iam.groups.manage` - Gérer les groupes

## 📝 Frontend - Composants UI

### Ancienne Méthode (À Supprimer)

```typescript
// ❌ DEPRECATED
const isAdmin = user.roles.includes('admin')
if (isAdmin) {
  return <AdminPanel />
}
```

### Nouvelle Méthode (IAM)

```typescript
// ✅ IAM
import { usePermission } from '@/hooks/usePermission'
import PermissionGate from '@/components/PermissionGate'

// Hook
const { hasPermission, isLoading } = usePermission('users.manage')

// Component
<PermissionGate permission="users.manage">
  <AdminPanel />
</PermissionGate>
```

## 🔄 Migration des Routes Frontend

### App.tsx - Avant

```typescript
<Route
  path="/admin/users"
  element={
    <ProtectedRoute requiredRoles={['admin', 'super_admin']}>
      <UserManagementPage />
    </ProtectedRoute>
  }
/>
```

### App.tsx - Après

```typescript
<Route
  path="/admin/users"
  element={
    <ProtectedRoute requiredPermissions={['users.manage']}>
      <UserManagementPage />
    </ProtectedRoute>
  }
/>
```

## 🎯 Liste Complète des Permissions

### Administration
- `admin.access` - Accès zone admin
- `admin.dashboard` - Tableau de bord admin

### Users
- `users.read` - Lire utilisateurs
- `users.create` - Créer utilisateurs
- `users.edit` - Modifier utilisateurs
- `users.delete` - Supprimer utilisateurs
- `users.manage` - Gestion complète (alias pour tous)
- `users.manage_status` - Gérer statuts
- `users.reset_mfa` - Réinitialiser MFA

### Groups & Profiles
- `groups.read` - Lire groupes
- `groups.manage` - Gérer groupes
- `profiles.read` - Lire profils (anciens)
- `profiles.manage` - Gérer profils (anciens)

### IAM (Nouveau)
- `iam.permissions.read` - Lire permissions
- `iam.permissions.manage` - Gérer permissions
- `iam.profiles.read` - Lire profils IAM
- `iam.profiles.manage` - Gérer profils IAM
- `iam.groups.read` - Lire groupes IAM
- `iam.groups.manage` - Gérer groupes IAM

### Missions
- `missions.browse` - Parcourir offres
- `missions.read` - Lire missions
- `missions.create` - Créer missions
- `missions.edit` - Modifier missions
- `missions.delete` - Supprimer missions
- `missions.publish` - Publier missions
- `missions.manage` - Gestion complète

### Applications
- `applications.read` - Lire candidatures
- `applications.read_own` - Lire ses candidatures
- `applications.create` - Postuler
- `applications.manage` - Gérer candidatures
- `applications.review` - Examiner candidatures

### Validations
- `validations.read` - Lire validations
- `validations.perform` - Effectuer validations
- `validations.approve` - Approuver
- `validations.reject` - Rejeter
- `validations.manage` - Gestion complète

### Configuration
- `config.read` - Lire config
- `config.edit` - Modifier config
- `config.manage` - Gestion complète
- `references.manage` - Gérer référentiels
- `rules.manage` - Gérer règles métier
- `locations.manage` - Gérer localisations
- `flags.manage` - Gérer feature flags

### Emails
- `emails.read_config` - Lire config emails
- `emails.configure` - Configurer emails
- `emails.test` - Tester emails
- `emails.read_history` - Lire historique
- `emails.manage_templates` - Gérer templates

### Profile (Own)
- `profile.read_own` - Lire son profil
- `profile.manage_own` - Gérer son profil

## ⚠️ Notes de Migration

1. **SuperAdmin Bypass**: Les utilisateurs avec rôle `super_admin` ont automatiquement TOUTES les permissions
2. **Cache**: Les permissions sont cachées 5 minutes côté backend
3. **Wildcard**: Support des wildcards (ex: `users.*` inclut `users.read`, `users.create`, etc.)
4. **Legacy Support**: Le système supporte temporairement les rôles ET les permissions pendant la migration
5. **Warnings**: En mode développement, des warnings s'affichent pour les usages deprecated

## 🚀 Ordre de Migration Recommandé

1. ✅ Créer les outils IAM (hooks, composants, services)
2. 🔄 Migrer les endpoints critiques (users, auth)
3. 🔄 Migrer les pages admin
4. 🔄 Migrer les autres modules
5. 🔄 Supprimer le code legacy
6. 🔄 Tests complets
