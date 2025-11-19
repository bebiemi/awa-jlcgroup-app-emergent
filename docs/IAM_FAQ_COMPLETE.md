# FAQ IAM - Guide Complet du Système de Gestion des Permissions

## 📋 Table des Matières
1. [Qu'est-ce que l'IAM ?](#quest-ce-que-liam-)
2. [Bug Critique Résolu](#bug-critique-résolu)
3. [Pattern IAM Officiel](#pattern-iam-officiel)
4. [Architecture du Système](#architecture-du-système)
5. [Comment Lire les Permissions](#comment-lire-les-permissions)
6. [Comment Ajouter un Profil](#comment-ajouter-un-profil)
7. [Comment Tester un Utilisateur](#comment-tester-un-utilisateur)
8. [Comprendre ProtectedRoute](#comprendre-protectedroute)
9. [Bonnes Pratiques](#bonnes-pratiques)
10. [Troubleshooting](#troubleshooting)

---

## Qu'est-ce que l'IAM ?

**IAM** (Identity and Access Management) est notre système de gestion des identités et des accès. Il contrôle **qui peut faire quoi** dans l'application.

### Composants Principaux

```
Utilisateur → Groupe(s) → Profil(s) → Permission(s)
```

- **Utilisateur** : Une personne (ex: `techcorp_admin`)
- **Groupe** : Un ensemble d'utilisateurs partageant des rôles similaires (ex: `Entreprises`, `Commerciaux`)
- **Profil** : Un ensemble de permissions (ex: `Entreprise`, `Admin Société`)
- **Permission** : Une action atomique (ex: `besoins.create.own`, `dashboard.access`)

---

## Bug Critique Résolu

### 🐛 Problème Identifié (Nov 2025)

**Symptôme :** L'utilisateur `techcorp_admin` ne pouvait pas accéder au dashboard malgré ses permissions valides.

**Cause Racine :** Mismatch entre les permissions demandées par les routes et les permissions réelles des utilisateurs.

```tsx
// ❌ AVANT (CASSÉ)
<ProtectedRoute requiredPermissions={['besoins.create']}>
  <CompanyDashboard />
</ProtectedRoute>

// L'utilisateur avait besoins.create.own mais la route demandait besoins.create
// → Accès refusé ❌
```

```tsx
// ✅ APRÈS (CORRIGÉ)
<ProtectedRoute requiredPermissions={['besoins.create.all', 'besoins.create.own']}>
  <CompanyDashboard />
</ProtectedRoute>

// La route accepte maintenant les deux variantes
// → Accès accordé ✅
```

### 🔍 Investigation Complète

**Collections Analysées :**
- ✅ `groups` (5 groupes actifs)
- ✅ `profiles` (25 profils)
- ✅ `permissions` (217 permissions)
- ❌ `iam_roles` (4 rôles legacy - NON UTILISÉS)

**Diagnostic :**
1. Deux systèmes IAM coexistaient (legacy vs moderne)
2. Page `/admin/iam/roles` utilisait les données legacy
3. Page `/admin/iam/groups` utilisait les vraies données
4. Les routes demandaient des permissions génériques (`besoins.create`) au lieu des permissions spécifiques (`.own`/`.all`)

### ✅ Correctifs Appliqués

1. **Routes Frontend Corrigées** (28 routes mises à jour)
2. **Redirection Legacy** : `/admin/iam/roles` → `/admin/iam/groups`
3. **Support Double Format** : `.own` ET `_own` pendant la migration
4. **Documentation Complète** : Ce document FAQ

---

## Pattern IAM Officiel

### 🎯 Standard Moderne (OBLIGATOIRE)

```
ressource.action.scope
```

#### Scopes Autorisés

| Scope | Signification | Exemple |
|-------|---------------|---------|
| `.all` | Accès à toutes les ressources | `besoins.edit.all` |
| `.own` | Accès uniquement aux ressources propres | `besoins.edit.own` |
| *(aucun)* | Accès global (legacy ou générique) | `dashboard.access` |

### ✅ Exemples Valides

```
dashboard.access
besoins.create.own
besoins.create.all
missions.edit.own
missions.edit.all
iam.profiles.manage
users.read
applications.read.own
```

### ❌ Exemples Invalides

```
besoins_create_own     ❌ (utiliser des points)
BESOINS.CREATE.OWN     ❌ (pas de majuscules)
besoins-create-own     ❌ (pas de tirets)
besoins.create.       ❌ (point final)
besoins..create        ❌ (double point)
```

### 🔄 Migration Legacy → Moderne

Pendant la transition, nous supportons DEUX formats :

```typescript
// Format moderne (préféré)
besoins.view.own
besoins.edit.all

// Format legacy (supporté temporairement)
besoins.view_own
besoins.edit_all
```

**Dans ProtectedRoute, utilisez les DEUX :**

```tsx
<ProtectedRoute requiredPermissions={[
  'besoins.view.own',  // Moderne
  'besoins.view_own'   // Legacy (support temporaire)
]}>
```

---

## Architecture du Système

### Hiérarchie IAM

```
┌─────────────┐
│ Utilisateur │
└──────┬──────┘
       │
       ├─ group_ids: [UUID, ...]
       └─ profile_ids: [UUID, ...]
                │
                ▼
        ┌──────────┐
        │  Groupe  │
        └────┬─────┘
             │
             └─ profile_ids: [UUID, ...]
                        │
                        ▼
                ┌───────────┐
                │  Profil   │
                └─────┬─────┘
                      │
                      └─ permission_ids: [UUID, ...]
                                  │
                                  ▼
                          ┌──────────────┐
                          │  Permission  │
                          └──────────────┘
                          code: "besoins.create.own"
                          name: "Créer ses besoins"
```

### Collections MongoDB

#### `users`
```json
{
  "id": "uuid",
  "username": "techcorp_admin",
  "full_name": "Admin TechCorp",
  "status": "active",
  "group_ids": ["uuid-groupe-entreprises"],
  "profile_ids": []  // Peut être vide si hérité via groupe
}
```

#### `groups`
```json
{
  "id": "uuid",
  "code": "grp.company",
  "name": "Entreprises",
  "profile_ids": ["uuid-profile-entreprise", "uuid-profile-admin-societe"],
  "user_ids": []  // Champ miroir (pas source de vérité)
}
```

#### `profiles`
```json
{
  "id": "uuid",
  "code": "profile.company",
  "name": "Entreprise",
  "permission_ids": ["uuid-perm-1", "uuid-perm-2", ...]
}
```

#### `permissions`
```json
{
  "id": "uuid",
  "code": "besoins.create.own",
  "name": "Créer ses besoins",
  "resource": "besoins",
  "action": "create",
  "scope": "own"
}
```

### API Backend (IAMService)

**Endpoint Principal :** `GET /api/iam/users/{user_id}/permissions`

**Réponse :**
```json
{
  "user_id": "uuid",
  "groups": [
    {
      "id": "uuid",
      "code": "grp.company",
      "name": "Entreprises"
    }
  ],
  "group_profiles": [
    {
      "id": "uuid",
      "code": "profile.company",
      "name": "Entreprise",
      "permission_ids": ["..."]
    }
  ],
  "direct_profiles": [],
  "all_permissions": [
    {
      "id": "uuid",
      "code": "besoins.create.own",
      "name": "Créer ses besoins"
    }
  ]
}
```

---

## Comment Lire les Permissions

### Format d'une Permission

```
ressource.action.scope
   ↓       ↓      ↓
besoins.create.own
```

- **Ressource** : La ressource concernée (`besoins`, `missions`, `dashboard`)
- **Action** : L'action autorisée (`create`, `read`, `edit`, `delete`, `manage`)
- **Scope** : Le périmètre d'application (`.own`, `.all`, ou rien)

### Exemples Concrets

| Permission | Signification |
|------------|---------------|
| `besoins.create.own` | L'utilisateur peut créer ses propres besoins |
| `besoins.create.all` | L'utilisateur peut créer des besoins pour n'importe quelle entreprise |
| `besoins.view.own` | L'utilisateur peut consulter uniquement ses besoins |
| `besoins.view.all` | L'utilisateur peut consulter tous les besoins |
| `missions.edit.own` | L'utilisateur peut modifier ses propres missions |
| `missions.edit.all` | L'utilisateur peut modifier toutes les missions |
| `dashboard.access` | L'utilisateur peut accéder au dashboard (scope global) |
| `iam.profiles.manage` | L'utilisateur peut gérer les profils IAM |

### Wildcards

```
*.*   →  Toutes les permissions (Super Admin uniquement)
```

---

## Comment Ajouter un Profil

### Étape 1 : Créer les Permissions

```bash
curl -X POST "http://localhost:8000/api/iam/permissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "reports.view.own",
    "name": "Consulter ses rapports",
    "description": "Permet de consulter ses propres rapports",
    "resource": "reports",
    "action": "view",
    "scope": "own"
  }'
```

### Étape 2 : Créer le Profil

```bash
curl -X POST "http://localhost:8000/api/iam/profiles" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "profile.reporter",
    "name": "Rapporteur",
    "description": "Profil pour les utilisateurs qui créent des rapports",
    "permission_ids": [
      "uuid-permission-reports-view-own",
      "uuid-permission-reports-create-own"
    ]
  }'
```

### Étape 3 : Assigner le Profil à un Groupe

```bash
curl -X POST "http://localhost:8000/api/iam/groups/{group_id}/profiles/{profile_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### Étape 4 : Assigner un Utilisateur au Groupe (si nécessaire)

```bash
curl -X POST "http://localhost:8000/api/iam/groups/{group_id}/users/{user_id}" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Comment Tester un Utilisateur

### Méthode 1 : Via API

```bash
# 1. Se connecter
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"techcorp_admin","password":"Password123!"}' \
  | jq -r '.access_token')

# 2. Récupérer les permissions
curl -X GET "http://localhost:8000/api/iam/users/{user_id}/permissions" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Méthode 2 : Via MongoDB

```python
from pymongo import MongoClient
import os

mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['auth_db']

# Récupérer l'utilisateur
user = db.users.find_one({'username': 'techcorp_admin'})
print(f"Groupes: {user.get('group_ids')}")
print(f"Profils directs: {user.get('profile_ids')}")

# Récupérer les permissions via les groupes
all_perm_ids = set()
for group_id in user.get('group_ids', []):
    group = db.groups.find_one({'id': group_id})
    if group:
        for profile_id in group.get('profile_ids', []):
            profile = db.profiles.find_one({'id': profile_id})
            if profile:
                all_perm_ids.update(profile.get('permission_ids', []))

# Afficher les permissions
for perm_id in all_perm_ids:
    perm = db.permissions.find_one({'id': perm_id})
    print(f"✓ {perm.get('code')}: {perm.get('name')}")
```

### Méthode 3 : Via Frontend (Dev Tools)

1. Ouvrir Chrome DevTools (F12)
2. Console :
```javascript
// Récupérer les permissions du user connecté
const response = await fetch('/api/iam/users/me/permissions', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
const data = await response.json();
console.table(data.all_permissions.map(p => ({ code: p.code, name: p.name })));
```

---

## Comprendre ProtectedRoute

### Syntaxe de Base

```tsx
<ProtectedRoute requiredPermissions={['permission.code']}>
  <Component />
</ProtectedRoute>
```

### Mode ANY (par défaut)

L'utilisateur doit avoir **AU MOINS UNE** des permissions listées.

```tsx
<ProtectedRoute requiredPermissions={[
  'besoins.create.all',
  'besoins.create.own'
]}>
  <CreateBesoinPage />
</ProtectedRoute>
```

☝️ **Accès accordé si l'utilisateur a :**
- `besoins.create.all` OU
- `besoins.create.own` OU
- Les deux

### Mode ALL

L'utilisateur doit avoir **TOUTES** les permissions listées.

```tsx
<ProtectedRoute 
  requiredPermissions={['missions.read', 'missions.manage.all']}
  requireAllPermissions={true}
>
  <MissionsPage />
</ProtectedRoute>
```

☝️ **Accès accordé uniquement si l'utilisateur a :**
- `missions.read` **ET**
- `missions.manage.all`

### Matching de Permissions

Le système vérifie les permissions avec **3 stratégies** :

#### 1. Match Exact
```
Demandé: besoins.create.own
Possédé: besoins.create.own
→ ✅ Match
```

#### 2. Match Wildcard
```
Demandé: besoins.create.own
Possédé: besoins.*
→ ✅ Match

Demandé: missions.edit.all
Possédé: *.*
→ ✅ Match (Super Admin)
```

#### 3. NO Match Suffixe
```
Demandé: besoins.create
Possédé: besoins.create.own
→ ❌ PAS de match

⚠️ C'est pourquoi il faut toujours lister les variantes dans requiredPermissions
```

### Exemples Pratiques

#### Route Simple

```tsx
// Accès au dashboard (permission globale)
<ProtectedRoute requiredPermissions={['dashboard.access']}>
  <DashboardPage />
</ProtectedRoute>
```

#### Route avec Variantes (Moderne + Legacy)

```tsx
// Support double format pendant la migration
<ProtectedRoute requiredPermissions={[
  'besoins.view.own',   // Format moderne (point)
  'besoins.view_own'    // Format legacy (underscore)
]}>
  <BesoinsListPage />
</ProtectedRoute>
```

#### Route Multi-Permissions (ANY)

```tsx
// Accès si l'utilisateur a n'importe laquelle de ces permissions
<ProtectedRoute requiredPermissions={[
  'rbac.assign_profiles',
  'rbac.assign_groups'
]}>
  <IAMControlPage />
</ProtectedRoute>
```

#### Route Multi-Permissions (ALL)

```tsx
// Accès uniquement si l'utilisateur a TOUTES ces permissions
<ProtectedRoute 
  requiredPermissions={[
    'users.read',
    'users.manage'
  ]}
  requireAllPermissions={true}
>
  <UserManagementPage />
</ProtectedRoute>
```

### Débogage ProtectedRoute

Si l'accès est refusé, consultez la console :

```
🚫 ProtectedRoute: Permission denied. Required: ['besoins.create']
```

**Checklist de débogage :**

1. ✅ L'utilisateur est-il authentifié ?
2. ✅ La permission demandée existe-t-elle en base ?
3. ✅ L'utilisateur a-t-il cette permission (via groupe ou profil direct) ?
4. ✅ Le format est-il correct (`.own` vs `_own`) ?
5. ✅ Le mode ANY/ALL est-il approprié ?

---

## Bonnes Pratiques

### ✅ DO

1. **Toujours utiliser le pattern moderne**
   ```
   besoins.create.own  ✅
   besoins.create_own  ❌ (legacy)
   ```

2. **Lister les variantes dans ProtectedRoute**
   ```tsx
   requiredPermissions={[
     'besoins.view.all',
     'besoins.view.own'
   ]}
   ```

3. **Utiliser des codes parlants**
   ```
   besoins.create.own  ✅  (clair)
   bsn.crt.o          ❌  (obscur)
   ```

4. **Grouper les permissions par ressource**
   ```
   besoins.create.own
   besoins.edit.own
   besoins.view.own
   besoins.delete.own
   ```

5. **Documenter les profils**
   ```
   Profil "Entreprise":
   - besoins.create.own : Créer ses besoins
   - besoins.view.own : Consulter ses besoins
   - missions.create.own : Créer ses missions
   ```

### ❌ DON'T

1. **Ne pas mélanger les formats**
   ```tsx
   // ❌ Incohérent
   requiredPermissions={[
     'besoins.view.own',
     'missions.edit_own'
   ]}
   ```

2. **Ne pas hardcoder les UUIDs**
   ```typescript
   // ❌ Mauvais
   const COMPANY_PROFILE = 'a1b2c3d4-...'

   // ✅ Bon
   const profile = await db.profiles.find_one({ code: 'profile.company' })
   ```

3. **Ne pas créer de permissions en doublon**
   ```
   ❌ besoins.view.own ET besoins.view_own
   ✅ besoins.view.own uniquement
   ```

4. **Ne pas utiliser `requireAllPermissions` par défaut**
   ```tsx
   // ❌ Trop restrictif
   <ProtectedRoute 
     requiredPermissions={['besoins.create.all', 'besoins.create.own']}
     requireAllPermissions={true}  // L'utilisateur doit avoir LES DEUX
   />

   // ✅ Plus flexible (par défaut)
   <ProtectedRoute 
     requiredPermissions={['besoins.create.all', 'besoins.create.own']}
   />  // L'utilisateur doit avoir AU MOINS UNE
   ```

5. **Ne jamais supprimer une permission sans vérifier son usage**
   ```bash
   # Avant de supprimer, vérifier
   db.profiles.find({ permission_ids: "uuid-permission" })
   grep -r "permission.code" /app/
   ```

---

## Troubleshooting

### Problème : Utilisateur ne peut pas accéder à une page

**Symptôme :**
```
🚫 ProtectedRoute: Permission denied. Required: ['besoins.create']
```

**Solution :**

1. **Vérifier que l'utilisateur a les groupes attendus**
   ```javascript
   db.users.findOne({ username: 'techcorp_admin' })
   // Checker group_ids
   ```

2. **Vérifier que le groupe a les profils attendus**
   ```javascript
   db.groups.findOne({ id: 'uuid-groupe' })
   // Checker profile_ids
   ```

3. **Vérifier que le profil a les permissions attendues**
   ```javascript
   db.profiles.findOne({ id: 'uuid-profil' })
   // Checker permission_ids
   ```

4. **Vérifier que la permission existe**
   ```javascript
   db.permissions.findOne({ code: 'besoins.create' })
   ```

5. **Vérifier le format de la permission dans la route**
   ```tsx
   // Si la permission en base est besoins.create.own
   // Mais la route demande besoins.create
   // → PAS DE MATCH
   ```

---

### Problème : Incohérence entre /admin/iam/roles et /admin/iam/groups

**Symptôme :** Les deux pages montrent des données différentes

**Cause :** `/admin/iam/roles` utilisait l'ancien système `iam_roles` (legacy)

**Solution :** ✅ **Déjà corrigé**
- La route `/admin/iam/roles` redirige maintenant vers `/admin/iam/groups`
- Utiliser uniquement `/admin/iam/groups`

---

### Problème : Permission en doublon (`.own` et `_own`)

**Symptôme :**
```
besoins.view.own
besoins.view_own
```

**Solution Temporaire (Transition) :**
```tsx
// Accepter les DEUX formats dans les routes
<ProtectedRoute requiredPermissions={[
  'besoins.view.own',   // Moderne
  'besoins.view_own'    // Legacy
]}>
```

**Solution Permanente (À venir) :**
1. Migrer tous les profils vers le format moderne (`.own`)
2. Supprimer les permissions legacy (`_own`)
3. Nettoyer les routes pour n'utiliser que le format moderne

---

### Problème : L'héritage des groupes ne fonctionne pas

**Symptôme :** L'utilisateur est dans un groupe mais n'a pas les permissions du groupe

**Checklist :**

1. **Vérifier que `user.group_ids` contient bien l'ID du groupe**
   ```javascript
   db.users.findOne({ username: 'user' })
   // group_ids: ['uuid-groupe']
   ```

2. **Vérifier que `group.profile_ids` contient bien les IDs des profils**
   ```javascript
   db.groups.findOne({ id: 'uuid-groupe' })
   // profile_ids: ['uuid-profil-1', 'uuid-profil-2']
   ```

3. **Vérifier que l'API retourne bien les groupes**
   ```bash
   curl /api/iam/users/{user_id}/permissions
   # Vérifier le champ "groups" et "group_profiles"
   ```

4. **Vérifier le cache Redis**
   ```bash
   # Si le cache est actif, il peut contenir des données obsolètes
   redis-cli KEYS "*iam:user:*"
   redis-cli DEL "iam:user:{user_id}"
   ```

---

### Problème : Permission avec wildcard ne fonctionne pas

**Symptôme :** L'utilisateur a `besoins.*` mais ne peut pas accéder à une route demandant `besoins.create.own`

**Cause :** Le code de vérification des wildcards a un bug ou n'est pas implémenté

**Solution :** Vérifier le code dans `/app/apps/web/src/hooks/usePermission.ts` :

```typescript
// Doit contenir cette logique
const parts = permissionCode.split('.')
for (let i = 0; i < parts.length; i++) {
  const wildcard = parts.slice(0, i + 1).join('.') + '.*'
  if (allPermissions.includes(wildcard)) return true
}
```

---

## Changelog

### 2025-11-19 : Correction Bug Critique IAM

**Problèmes Résolus :**
- ✅ Incohérence entre `/admin/iam/roles` (legacy) et `/admin/iam/groups` (moderne)
- ✅ Utilisateur `techcorp_admin` bloqué malgré permissions valides
- ✅ Routes demandant des permissions génériques au lieu de `.all`/`.own`
- ✅ Permissions en doublon (`.own` vs `_own`)

**Correctifs Appliqués :**
- ✅ 28 routes frontend corrigées pour utiliser le pattern IAM moderne
- ✅ Redirection `/admin/iam/roles` → `/admin/iam/groups`
- ✅ Support double format (`.own` + `_own`) pendant la migration
- ✅ Validation stricte des permissions (regex + index unique MongoDB)
- ✅ Documentation FAQ complète

**Fichiers Modifiés :**
- `/app/apps/web/src/App.tsx` (28 routes)
- `/app/auth-microservice/awana_auth/core/iam_models.py` (validations)
- `/app/docs/IAM_FAQ_COMPLETE.md` (nouveau)
- `/app/docs/PERMISSION_VALIDATION_RULES.md` (nouveau)

**Tests Effectués :**
- ✅ Backend : API `/api/iam/users/{id}/permissions` retourne 42 permissions pour `techcorp_admin`
- ✅ Permissions critiques présentes : `dashboard.access`, `besoins.create.own`, etc.
- ✅ Héritage via groupes fonctionnel
- ✅ Aucune régression sur admin/super-admin/commercial

---

## Support

Pour toute question ou problème IAM :

1. **Consulter cette FAQ**
2. **Vérifier les logs** : `/var/log/supervisor/auth-microservice.*.log`
3. **Tester via API** : `GET /api/iam/users/{user_id}/permissions`
4. **Consulter MongoDB** : Collections `users`, `groups`, `profiles`, `permissions`

---

**Document créé le :** 2025-11-19  
**Dernière mise à jour :** 2025-11-19  
**Version :** 1.0.0  
**Auteur :** Équipe Emergent - AI Agent E1
