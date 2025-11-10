# 🔐 Système de Constantes IAM - Guide Rapide

## 📚 Documentation Complète

Pour la documentation détaillée, consultez :
- **Guide Complet** : [`/app/docs/IAM_CONSTANTS_GUIDE.md`](./docs/IAM_CONSTANTS_GUIDE.md)
- **Résumé de Refactorisation** : [`/app/IAM_REFACTORING_COMPLETE.md`](./IAM_REFACTORING_COMPLETE.md)

## 🚀 Démarrage Rapide

### Backend (Python)
```python
from awana_auth.core.iam_constants import (
    IAMGroups,          # Groupes d'utilisateurs
    IAMProfiles,        # Profils/Rôles
    IAMPermissions,     # Permissions
    ValidationTypes,    # Types de validation
    UserRoles,          # Rôles legacy
    get_group_for_role, # Helper function
    get_profile_for_role
)

# Exemple d'utilisation
if user.group_id == IAMGroups.CANDIDAT:
    print("User is a candidat")
```

### Frontend (TypeScript)
```typescript
import {
  IAMGroups,          // Groupes d'utilisateurs
  IAMProfiles,        // Profils/Rôles
  IAMPermissions,     // Permissions
  ValidationTypes,    // Types de validation
  UserRoles,          // Rôles legacy
  getRoleLabel,       // Helper function
  getRoleColor,       // Helper function
  getGroupForRole,
  getProfileForRole
} from '@/constants/iamConstants'

// Exemple d'utilisation
if (user.role === UserRoles.CANDIDAT) {
  console.log("User is a candidat")
}
```

## 📊 Constantes Disponibles (49 au total)

### Groupes IAM (6)
- `CANDIDAT`, `INTERIMAIRE`, `COMPANY`, `COLLABORATEUR`, `ADMIN`, `SUPER_ADMIN`

### Profils IAM (6)
- `CANDIDAT`, `INTERIM_USER`, `COMPANY_ADMIN`, `COLLABORATEUR`, `ADMIN`, `SUPER_ADMIN`

### Permissions IAM (27)
- **Missions** : BROWSE, READ, CREATE, UPDATE, DELETE, MANAGE
- **Applications** : CREATE_OWN, READ_OWN, UPDATE_OWN, READ, MANAGE
- **Profile** : MANAGE_OWN, READ, MANAGE
- **Auth/Security** : MFA_MANAGE, EMAIL_DOMAINS_READ, EMAIL_DOMAINS_MANAGE
- **Admin** : DASHBOARD, USERS_READ, USERS_MANAGE
- **Email** : SETTINGS_READ, SETTINGS_MANAGE
- **IAM** : PROFILES_READ, PROFILES_MANAGE, GROUPS_READ, GROUPS_MANAGE, PERMISSIONS_READ

### Types de Validation (4)
- `CANDIDAT`, `INTERIM`, `COMPANY`, `COLLABORATEUR`

### Rôles Legacy (6)
- `CANDIDAT`, `INTERIM`, `COMPANY`, `COLLABORATEUR`, `ADMIN`, `SUPER_ADMIN`

## 🧪 Tests de Synchronisation

### Exécuter les Tests
```bash
python /app/scripts/test_iam_constants_sync.py
```

### Résultats Attendus
```
✅ ALL TESTS PASSED
Frontend and Backend constants are perfectly synchronized!
```

## 🔍 Trouver les Valeurs Hardcodées

### Utiliser le Script de Migration
```bash
bash /app/scripts/migrate_to_constants.sh
```

Ce script identifie tous les fichiers qui contiennent encore des valeurs hardcodées et doivent être refactorés.

## 📝 Exemples d'Utilisation

### 1. Vérifier les Permissions (Backend)
```python
from awana_auth.core.iam_constants import IAMPermissions
from awana_auth.dependencies.permission_dependencies import require_permission

@router.get("/missions")
async def list_missions(
    user: dict = Depends(require_permission(IAMPermissions.MISSIONS_BROWSE))
):
    return {"missions": []}
```

### 2. Protéger un Composant (Frontend)
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

### 3. Afficher un Badge de Rôle (Frontend)
```typescript
import { getRoleLabel, getRoleColor } from '@/constants/iamConstants'

function UserBadge({ role }: { role: string }) {
  return (
    <span className={getRoleColor(role)}>
      {getRoleLabel(role)}
    </span>
  )
}
```

### 4. Mapper un Rôle vers un Groupe
```python
# Backend
from awana_auth.core.iam_constants import UserRoles, get_group_for_role

user_role = UserRoles.CANDIDAT
group_id = get_group_for_role(user_role)  # Returns "grp.candidat"
```

```typescript
// Frontend
import { UserRoles, getGroupForRole } from '@/constants/iamConstants'

const userRole = UserRoles.CANDIDAT
const groupId = getGroupForRole(userRole)  // Returns "grp.candidat"
```

## ✅ Bonnes Pratiques

### ✅ À FAIRE
```typescript
// CORRECT
import { UserRoles } from '@/constants/iamConstants'
if (user.role === UserRoles.CANDIDAT) { }
```

### ❌ À ÉVITER
```typescript
// INCORRECT - Ne pas hardcoder les valeurs
if (user.role === 'candidat') { }
if (user.group === 'grp.admin') { }
```

## 🔧 Commandes Utiles

| Commande | Description |
|----------|-------------|
| `python /app/scripts/test_iam_constants_sync.py` | Tester la synchronisation |
| `bash /app/scripts/migrate_to_constants.sh` | Identifier les fichiers à refactorer |
| `grep -r "IAMGroups" /app --include="*.py"` | Trouver l'utilisation dans le backend |
| `grep -r "IAMGroups" /app --include="*.tsx"` | Trouver l'utilisation dans le frontend |

## 📁 Fichiers Importants

### Documentation
- [`/app/docs/IAM_CONSTANTS_GUIDE.md`](./docs/IAM_CONSTANTS_GUIDE.md) - Guide détaillé (4500+ lignes)
- [`/app/IAM_REFACTORING_COMPLETE.md`](./IAM_REFACTORING_COMPLETE.md) - Résumé de refactorisation

### Constantes
- **Backend** : `/app/auth-microservice/awana_auth/core/iam_constants.py`
- **Frontend** : `/app/apps/web/src/constants/iamConstants.ts`

### Scripts
- **Test Sync** : `/app/scripts/test_iam_constants_sync.py`
- **Migration Helper** : `/app/scripts/migrate_to_constants.sh`

## 🎯 État de la Refactorisation

### ✅ Complété
- [x] Constantes backend créées (49 constantes)
- [x] Constantes frontend créées (49 constantes)
- [x] Tests de synchronisation (100% passés)
- [x] Documentation complète
- [x] Scripts de migration

### 🔄 En Cours
- [ ] `ValidationsPage.tsx` (19 occurrences à refactorer)
- [ ] `ProfilesManagementPage.tsx`
- [ ] `IAMControlPage.tsx`
- [ ] Scripts d'initialisation backend

### 📊 Statistiques
- **Backend** : ~15 fichiers à refactorer
- **Frontend** : ~21 fichiers à refactorer
- **Tests** : 100% de synchronisation
- **Documentation** : Complète

## 🚦 Prochaines Étapes

1. **Refactorer ValidationsPage.tsx** (priorité haute)
   ```bash
   # Voir les occurrences
   grep -n "'candidat'\|'interim'\|'company'" /app/apps/web/src/features/admin/pages/ValidationsPage.tsx
   ```

2. **Refactorer les scripts d'initialisation**
   ```bash
   # initialize_candidat_iam.py
   # initialize_iam_system.py
   ```

3. **Ajouter des tests unitaires**
   ```python
   # Backend: tests/test_iam_constants.py
   # Frontend: __tests__/iamConstants.test.ts
   ```

4. **Intégration CI/CD**
   - Ajouter le test de sync dans le pipeline
   - Bloquer les merges si désynchronisé

## 📞 Support

Pour toute question :
1. Consulter la [documentation complète](./docs/IAM_CONSTANTS_GUIDE.md)
2. Exécuter les scripts de test et migration
3. Contacter l'équipe de développement

---

**Version** : 1.0  
**Dernière mise à jour** : 2025-01-10  
**Statut** : ✅ Phase 1 Complétée | 🔄 Phase 2 En Cours
