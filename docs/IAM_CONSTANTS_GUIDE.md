# Guide des Constantes IAM

## 📋 Vue d'Ensemble

Ce guide documente le système de constantes centralisées pour le système IAM (Identity and Access Management) de l'application JLC. Ces constantes garantissent la cohérence entre le frontend et le backend.

## 🗂️ Emplacements des Fichiers

### Backend
**Fichier**: `/app/auth-microservice/awana_auth/core/iam_constants.py`

```python
from awana_auth.core.iam_constants import (
    IAMGroups,
    IAMProfiles,
    IAMPermissions,
    ValidationTypes,
    UserRoles,
    get_group_for_role,
    get_profile_for_role,
    get_validation_type_for_role
)
```

### Frontend
**Fichier**: `/app/apps/web/src/constants/iamConstants.ts`

```typescript
import {
  IAMGroups,
  IAMProfiles,
  IAMPermissions,
  ValidationTypes,
  UserRoles,
  RoleLabels,
  RoleColors,
  getGroupForRole,
  getProfileForRole,
  getRoleLabel,
  getRoleColor
} from '@/constants/iamConstants'
```

## 🏷️ Constantes Disponibles

### 1. Groupes IAM (IAMGroups)

Les groupes représentent des collections d'utilisateurs avec des permissions communes.

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `CANDIDAT` | `"grp.candidat"` | Groupe des candidats |
| `INTERIMAIRE` | `"grp.interimaire"` | Groupe des intérimaires (après contrat) |
| `COMPANY` | `"grp.company"` | Groupe des entreprises |
| `COLLABORATEUR` | `"grp.collaborateur"` | Groupe des collaborateurs JLC |
| `ADMIN` | `"grp.admin"` | Groupe des administrateurs |
| `SUPER_ADMIN` | `"grp.super_admin"` | Groupe des super administrateurs |

**Exemple d'utilisation (Backend)**:
```python
from awana_auth.core.iam_constants import IAMGroups

# Vérifier si un utilisateur appartient au groupe candidat
if user.group_id == IAMGroups.CANDIDAT:
    # Logique spécifique aux candidats
    pass
```

**Exemple d'utilisation (Frontend)**:
```typescript
import { IAMGroups } from '@/constants/iamConstants'

// Vérifier le groupe d'un utilisateur
if (user.group_id === IAMGroups.CANDIDAT) {
  // Logique spécifique aux candidats
}
```

### 2. Profils IAM (IAMProfiles)

Les profils définissent les rôles et permissions des utilisateurs.

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `CANDIDAT` | `"role.candidat"` | Profil candidat |
| `INTERIM_USER` | `"role.interim_user"` | Profil intérimaire |
| `COMPANY_ADMIN` | `"role.company_admin"` | Profil administrateur d'entreprise |
| `COLLABORATEUR` | `"role.collaborateur"` | Profil collaborateur JLC |
| `ADMIN` | `"role.admin"` | Profil administrateur |
| `SUPER_ADMIN` | `"role.super_admin"` | Profil super administrateur |

**Exemple d'utilisation (Backend)**:
```python
from awana_auth.core.iam_constants import IAMProfiles

# Assigner un profil à un utilisateur
user.profile_id = IAMProfiles.CANDIDAT
```

**Exemple d'utilisation (Frontend)**:
```typescript
import { IAMProfiles } from '@/constants/iamConstants'

// Filtrer les utilisateurs par profil
const admins = users.filter(u => u.profile_id === IAMProfiles.ADMIN)
```

### 3. Permissions IAM (IAMPermissions)

Les permissions définissent les actions autorisées.

#### Missions
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `MISSIONS_BROWSE` | `"missions.browse"` | Parcourir les missions |
| `MISSIONS_READ` | `"missions.read"` | Lire les détails des missions |
| `MISSIONS_CREATE` | `"missions.create"` | Créer des missions |
| `MISSIONS_UPDATE` | `"missions.update"` | Modifier des missions |
| `MISSIONS_DELETE` | `"missions.delete"` | Supprimer des missions |
| `MISSIONS_MANAGE` | `"missions.manage"` | Gérer toutes les missions |

#### Candidatures
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `APPLICATIONS_CREATE_OWN` | `"applications.create_own"` | Créer ses propres candidatures |
| `APPLICATIONS_READ_OWN` | `"applications.read_own"` | Lire ses propres candidatures |
| `APPLICATIONS_UPDATE_OWN` | `"applications.update_own"` | Modifier ses candidatures |
| `APPLICATIONS_READ` | `"applications.read"` | Lire toutes les candidatures |
| `APPLICATIONS_MANAGE` | `"applications.manage"` | Gérer toutes les candidatures |

#### Profils
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `PROFILE_MANAGE_OWN` | `"profile.manage_own"` | Gérer son propre profil |
| `PROFILE_READ` | `"profile.read"` | Lire les profils |
| `PROFILE_MANAGE` | `"profile.manage"` | Gérer tous les profils |

#### Auth & Sécurité
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `AUTH_MFA_MANAGE` | `"auth.mfa.manage"` | Gérer l'authentification MFA |
| `SECURITY_EMAIL_DOMAINS_READ` | `"security.email_domains.read"` | Lire les domaines email |
| `SECURITY_EMAIL_DOMAINS_MANAGE` | `"security.email_domains.manage"` | Gérer les domaines email |

#### Administration
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `ADMIN_DASHBOARD` | `"admin.dashboard"` | Accéder au tableau de bord admin |
| `USERS_READ` | `"users.read"` | Lire les utilisateurs |
| `USERS_MANAGE` | `"users.manage"` | Gérer les utilisateurs |

#### Email Settings
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `EMAIL_SETTINGS_READ` | `"email.settings.read"` | Lire la configuration email |
| `EMAIL_SETTINGS_MANAGE` | `"email.settings.manage"` | Gérer la configuration email |

#### IAM
| Constante | Valeur | Description |
|-----------|--------|-------------|
| `IAM_PROFILES_READ` | `"iam.profiles.read"` | Lire les profils IAM |
| `IAM_PROFILES_MANAGE` | `"iam.profiles.manage"` | Gérer les profils IAM |
| `IAM_GROUPS_READ` | `"iam.groups.read"` | Lire les groupes IAM |
| `IAM_GROUPS_MANAGE` | `"iam.groups.manage"` | Gérer les groupes IAM |
| `IAM_PERMISSIONS_READ` | `"iam.permissions.read"` | Lire les permissions IAM |

**Exemple d'utilisation (Backend)**:
```python
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.dependencies.permission_dependencies import require_permission

@router.get("/missions")
async def list_missions(
    user: dict = Depends(require_permission(IAMPermissions.MISSIONS_BROWSE))
):
    # Logique pour lister les missions
    pass
```

**Exemple d'utilisation (Frontend)**:
```typescript
import { IAMPermissions } from '@/constants/iamConstants'
import { usePermission } from '@/hooks/usePermission'

function MissionsList() {
  const canBrowse = usePermission(IAMPermissions.MISSIONS_BROWSE)
  
  if (!canBrowse) {
    return <div>Accès non autorisé</div>
  }
  
  return <div>Liste des missions</div>
}
```

### 4. Types de Validation (ValidationTypes)

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `CANDIDAT` | `"candidat"` | Validation pour candidat |
| `INTERIM` | `"interim"` | Validation pour intérimaire |
| `COMPANY` | `"company"` | Validation pour entreprise |
| `COLLABORATEUR` | `"collaborateur"` | Validation pour collaborateur |

### 5. Rôles Utilisateur (UserRoles - Legacy)

**⚠️ Note**: Ces constantes sont maintenues pour la rétrocompatibilité mais seront progressivement remplacées par les profils IAM.

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `CANDIDAT` | `"candidat"` | Rôle candidat |
| `INTERIM` | `"interim"` | Rôle intérimaire |
| `COMPANY` | `"company"` | Rôle entreprise |
| `COLLABORATEUR` | `"collaborateur"` | Rôle collaborateur |
| `ADMIN` | `"admin"` | Rôle administrateur |
| `SUPER_ADMIN` | `"super_admin"` | Rôle super administrateur |

## 🔧 Fonctions Utilitaires

### Backend

#### `get_group_for_role(role: str) -> str`
Convertit un rôle en groupe correspondant.

```python
from awana_auth.core.iam_constants import UserRoles, get_group_for_role

role = UserRoles.CANDIDAT
group = get_group_for_role(role)  # Returns "grp.candidat"
```

#### `get_profile_for_role(role: str) -> str`
Convertit un rôle en profil correspondant.

```python
from awana_auth.core.iam_constants import UserRoles, get_profile_for_role

role = UserRoles.ADMIN
profile = get_profile_for_role(role)  # Returns "role.admin"
```

#### `get_validation_type_for_role(role: str) -> str`
Convertit un rôle en type de validation.

```python
from awana_auth.core.iam_constants import UserRoles, get_validation_type_for_role

role = UserRoles.CANDIDAT
validation_type = get_validation_type_for_role(role)  # Returns "candidat"
```

### Frontend

#### `getGroupForRole(role: string): string`
Convertit un rôle en groupe correspondant.

```typescript
import { UserRoles, getGroupForRole } from '@/constants/iamConstants'

const role = UserRoles.CANDIDAT
const group = getGroupForRole(role)  // Returns "grp.candidat"
```

#### `getProfileForRole(role: string): string`
Convertit un rôle en profil correspondant.

```typescript
import { UserRoles, getProfileForRole } from '@/constants/iamConstants'

const role = UserRoles.ADMIN
const profile = getProfileForRole(role)  // Returns "role.admin"
```

#### `getRoleLabel(role: string): string`
Obtient le libellé lisible d'un rôle.

```typescript
import { UserRoles, getRoleLabel } from '@/constants/iamConstants'

const label = getRoleLabel(UserRoles.CANDIDAT)  // Returns "Candidat"
```

#### `getRoleColor(role: string): string`
Obtient les classes CSS de couleur pour un rôle.

```typescript
import { UserRoles, getRoleColor } from '@/constants/iamConstants'

const colorClass = getRoleColor(UserRoles.ADMIN)  
// Returns "bg-purple-100 text-purple-800"
```

## 📝 Bonnes Pratiques

### 1. Toujours Utiliser les Constantes

❌ **À ÉVITER** :
```typescript
// NE PAS faire ceci
if (user.role === 'candidat') { }
if (user.group === 'grp.admin') { }
```

✅ **RECOMMANDÉ** :
```typescript
// FAIRE ceci
import { UserRoles, IAMGroups } from '@/constants/iamConstants'

if (user.role === UserRoles.CANDIDAT) { }
if (user.group === IAMGroups.ADMIN) { }
```

### 2. Import Complet des Constantes

```typescript
// Frontend - Importation complète
import {
  IAMGroups,
  IAMProfiles,
  IAMPermissions,
  UserRoles,
  getRoleLabel,
  getRoleColor
} from '@/constants/iamConstants'
```

```python
# Backend - Importation complète
from awana_auth.core.iam_constants import (
    IAMGroups,
    IAMProfiles,
    IAMPermissions,
    UserRoles,
    get_group_for_role
)
```

### 3. Vérification des Permissions

**Backend**:
```python
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.dependencies.permission_dependencies import require_permission

@router.post("/missions")
async def create_mission(
    mission_data: MissionCreate,
    user: dict = Depends(require_permission(IAMPermissions.MISSIONS_CREATE))
):
    # Seuls les utilisateurs avec la permission missions.create peuvent accéder
    pass
```

**Frontend**:
```typescript
import { IAMPermissions } from '@/constants/iamConstants'
import { PermissionGate } from '@/components/PermissionGate'

function CreateMissionButton() {
  return (
    <PermissionGate requiredPermissions={[IAMPermissions.MISSIONS_CREATE]}>
      <button>Créer une mission</button>
    </PermissionGate>
  )
}
```

### 4. Affichage des Rôles

```typescript
import { UserRoles, getRoleLabel, getRoleColor } from '@/constants/iamConstants'

function UserRoleBadge({ role }: { role: string }) {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getRoleColor(role)}`}>
      {getRoleLabel(role)}
    </span>
  )
}
```

## 🔄 Synchronisation Frontend/Backend

### Processus de Synchronisation

1. **Toute modification des constantes doit être faite dans les deux fichiers**
   - `/app/auth-microservice/awana_auth/core/iam_constants.py` (Backend)
   - `/app/apps/web/src/constants/iamConstants.ts` (Frontend)

2. **Vérifier la synchronisation**
   ```bash
   # Exécuter le script de test de synchronisation
   python /app/scripts/test_iam_constants_sync.py
   ```

3. **Ajouter des tests**
   - Backend: Ajouter des tests dans `/app/auth-microservice/tests/test_iam_constants.py`
   - Frontend: Ajouter des tests dans `/app/apps/web/src/__tests__/iamConstants.test.ts`

### Checklist de Modification

Lorsque vous ajoutez ou modifiez une constante :

- [ ] Modifier `iam_constants.py` (Backend)
- [ ] Modifier `iamConstants.ts` (Frontend)
- [ ] Ajouter la documentation dans ce fichier
- [ ] Exécuter les tests de synchronisation
- [ ] Mettre à jour les fichiers utilisant les anciennes valeurs
- [ ] Vérifier que tous les tests passent

## 📚 Références

### Fichiers Backend Utilisant les Constantes
- `/app/auth-microservice/awana_auth_routes.py`
- `/app/auth-microservice/scripts/initialize_iam_system.py`
- `/app/auth-microservice/scripts/initialize_candidat_iam.py`
- `/app/auth-microservice/dependencies/permission_dependencies.py`

### Fichiers Frontend Utilisant les Constantes
- `/app/apps/web/src/features/admin/pages/UserManagementPage.tsx`
- `/app/apps/web/src/features/admin/pages/ValidationsPage.tsx`
- `/app/apps/web/src/features/iam/pages/ProfilesManagementPage.tsx`
- `/app/apps/web/src/features/iam/pages/IAMControlPage.tsx`
- `/app/apps/web/src/components/Sidebar.tsx`

## 🐛 Dépannage

### Problème : Constante non trouvée

**Erreur** : `Cannot find name 'IAMGroups'` ou `NameError: name 'IAMGroups' is not defined`

**Solution** : Vérifiez l'import
```typescript
// Frontend
import { IAMGroups } from '@/constants/iamConstants'
```
```python
# Backend
from awana_auth.core.iam_constants import IAMGroups
```

### Problème : Valeurs différentes entre frontend et backend

**Solution** : Exécutez le script de test de synchronisation
```bash
python /app/scripts/test_iam_constants_sync.py
```

## 🔐 Sécurité

- **Ne jamais hardcoder les valeurs des rôles ou permissions**
- **Toujours passer par les constantes**
- **Vérifier les permissions côté backend** même si le frontend les masque
- **Utiliser `require_permission` pour protéger les endpoints**

## 📊 Tableau Récapitulatif

| Type | Backend | Frontend | Description |
|------|---------|----------|-------------|
| Groupes | `IAMGroups` | `IAMGroups` | Collections d'utilisateurs |
| Profils | `IAMProfiles` | `IAMProfiles` | Rôles et permissions |
| Permissions | `IAMPermissions` | `IAMPermissions` | Actions autorisées |
| Types Validation | `ValidationTypes` | `ValidationTypes` | Types de validation |
| Rôles (Legacy) | `UserRoles` | `UserRoles` | Rôles utilisateur |

## 📞 Support

Pour toute question ou problème concernant les constantes IAM :
1. Consulter cette documentation
2. Vérifier les exemples de code dans les fichiers de référence
3. Exécuter les tests de synchronisation
4. Contacter l'équipe de développement

---

**Dernière mise à jour** : 2025-01-10  
**Version** : 1.0
