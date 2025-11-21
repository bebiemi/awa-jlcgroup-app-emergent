# 📁 Structure Standard des Modules

**Date :** 21 novembre 2025  
**Statut :** ✅ STANDARD ÉTABLI

---

## 🎯 Architecture de Modules Imposée

Tous les modules de l'application **DOIVENT** respecter cette structure :

```
/features/{module}/
   ├── api/
   │     └── {module}Api.ts          # RTK Query API
   ├── components/
   │     ├── {Component1}.tsx         # Composants réutilisables
   │     └── {Component2}.tsx
   ├── config/
   │     └── {module}.config.ts       # Configuration Config-Driven
   ├── pages/
   │     └── {Module}Page.tsx         # Page principale
   └── index.ts                       # Exports du module
```

---

## 📋 Exemple : Module Users

### Structure Implémentée

```
/features/users/
   ├── api/
   │     ├── usersApi.ts              # RTK Query endpoints users
   │     └── userDetailsApi.ts        # RTK Query détails utilisateurs
   ├── components/
   │     ├── EditUserModal.tsx
   │     ├── DeleteUserModal.tsx
   │     ├── BlockUserModal.tsx
   │     ├── ArchiveUserModal.tsx
   │     ├── RestoreUserModal.tsx
   │     ├── UserDetailModal.tsx
   │     ├── ResetMfaModal.tsx
   │     ├── AdminUpdatePasswordModal.tsx
   │     ├── QuickAddUserModal.tsx
   │     ├── BulkImportUsersModal.tsx
   │     └── UserDetailTabs/
   │           ├── UserInfoTab.tsx
   │           ├── UserDocumentsTab.tsx
   │           ├── UserPermissionsTab.tsx
   │           └── UserActivityTab.tsx
   ├── config/
   │     └── users.config.ts          # Configuration de la page utilisateurs
   ├── pages/
   │     └── UsersPage.tsx            # Page principale de gestion des utilisateurs
   └── index.ts                       # Exports publics du module
```

### Fichier index.ts

```typescript
/**
 * Module Users - Exports
 * Architecture Config-Driven
 */

// Page principale
export { default as UsersPage } from './pages/UsersPage'

// Configuration
export { UsersPageConfig } from './config/users.config'

// API
export * from './api/usersApi'
export * from './api/userDetailsApi'

// Composants (si besoin d'être réutilisés ailleurs)
export { default as EditUserModal } from './components/EditUserModal'
export { default as DeleteUserModal } from './components/DeleteUserModal'
export { default as BlockUserModal } from './components/BlockUserModal'
export { default as ArchiveUserModal } from './components/ArchiveUserModal'
export { default as RestoreUserModal } from './components/RestoreUserModal'
export { default as UserDetailModal } from './components/UserDetailModal'
export { default as ResetMfaModal } from './components/ResetMfaModal'
export { default as AdminUpdatePasswordModal } from './components/AdminUpdatePasswordModal'
```

### Utilisation dans App.tsx

```typescript
// AVANT (❌ Mauvaise pratique)
import UsersPage from './features/users/pages/UsersPage'

// APRÈS (✅ Bonne pratique)
import { UsersPage } from './features/users'
```

---

## 🔧 Avantages de cette Structure

### 1. **Séparation des Responsabilités**
- `api/` : Logique de communication backend (RTK Query)
- `components/` : Composants UI réutilisables
- `config/` : Configuration Config-Driven (architecture imposée)
- `pages/` : Pages principales (wrappers/adaptateurs)

### 2. **Scalabilité**
- Ajout facile de nouveaux modules
- Structure cohérente dans toute l'application
- Facilite l'onboarding des nouveaux développeurs

### 3. **Maintenabilité**
- Tous les fichiers d'un module sont au même endroit
- Imports clairs et organisés
- Réduction des imports relatifs complexes (`../../..`)

### 4. **Testabilité**
- Chaque module est isolé
- Exports centralisés via `index.ts`
- Facilite les tests unitaires

---

## 📦 Modules à Restructurer (Prochaines Étapes)

### PHASE 2 : Entreprises
```
/features/entreprises/
   ├── api/
   │     └── entreprisesApi.ts
   ├── components/
   │     ├── CreateEntrepriseModal.tsx
   │     ├── EditEntrepriseModal.tsx
   │     └── ...
   ├── config/
   │     └── entreprises.config.ts
   ├── pages/
   │     └── EntreprisesPage.tsx
   └── index.ts
```

### PHASE 2 : Missions/Besoins
```
/features/besoins/
   ├── api/
   │     └── besoinsApi.ts
   ├── components/
   │     └── ...
   ├── config/
   │     └── besoins.config.ts
   ├── pages/
   │     └── BesoinsPage.tsx
   └── index.ts
```

### PHASE 2 : Validations
```
/features/validations/
   ├── api/
   │     └── validationsApi.ts
   ├── components/
   │     └── ...
   ├── config/
   │     └── validations.config.ts
   ├── pages/
   │     └── ValidationsPage.tsx
   └── index.ts
```

---

## 🚀 Checklist de Migration d'un Module

Lors de la restructuration d'un module, suivre ces étapes :

### 1. Créer la Structure de Dossiers
```bash
mkdir -p /app/apps/web/src/features/{module}/{api,components,config,pages}
```

### 2. Déplacer les Fichiers
- [ ] Déplacer l'API vers `api/`
- [ ] Déplacer les composants vers `components/`
- [ ] Déplacer/créer la config vers `config/`
- [ ] Déplacer/créer la page vers `pages/`

### 3. Créer index.ts
- [ ] Exporter la page principale
- [ ] Exporter la configuration
- [ ] Exporter les APIs
- [ ] Exporter les composants réutilisables

### 4. Mettre à Jour les Imports
- [ ] Mettre à jour les imports internes du module
- [ ] Mettre à jour `App.tsx`
- [ ] Mettre à jour `store.ts`
- [ ] Mettre à jour les autres fichiers qui utilisent ce module

### 5. Tester
- [ ] Vérifier la compilation TypeScript
- [ ] Tester le hot reload
- [ ] Tester la page dans le navigateur
- [ ] Vérifier qu'il n'y a pas de régression

---

## ⚠️ Règles Importantes

### ✅ À FAIRE
- Utiliser des imports absolus : `@/features/{module}/...`
- Exporter via `index.ts` pour les APIs publiques
- Garder une structure cohérente dans tous les modules
- Documenter les exports dans `index.ts`

### ❌ À ÉVITER
- Imports relatifs complexes : `../../../features/...`
- Fichiers éparpillés dans plusieurs dossiers
- Duplication de code entre modules
- Imports directs depuis les sous-dossiers (utiliser `index.ts`)

---

## 📊 Statut Actuel des Modules

| Module | Structure ✅ | Config ✅ | Template ✅ | Statut |
|--------|------------|----------|-----------|--------|
| **users** | ✅ | ✅ | ✅ | COMPLÉTÉ |
| entreprises | ❌ | ❌ | ❌ | À FAIRE |
| besoins | ❌ | ❌ | ❌ | À FAIRE |
| validations | ❌ | ❌ | ❌ | À FAIRE |
| missions | ⚠️ | ❌ | ❌ | PARTIEL |
| iam | ⚠️ | ❌ | ❌ | PARTIEL |

---

## 🎯 Conclusion

Cette structure standard garantit :
- **Cohérence** : Tous les modules suivent le même pattern
- **Clarté** : Chaque fichier a sa place bien définie
- **Maintenabilité** : Facilite les modifications futures
- **Scalabilité** : Permet d'ajouter facilement de nouveaux modules

**Cette structure est désormais le STANDARD pour tous les futurs développements.**
