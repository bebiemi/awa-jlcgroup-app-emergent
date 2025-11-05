# 🚧 Phase A - Travail Restant

**Date**: 5 Novembre 2025  
**Progression**: 131 corrections appliquées / 504 critiques initiaux = **26% complété**

---

## 📊 État Actuel

### Avant Phase A
- 🔴 CRITIQUE: 504 occurrences
- Total: 886 occurrences

### Après Corrections Actuelles
- 🔴 CRITIQUE: **403 occurrences** (-101, **-20%**)
- Total: **753 occurrences** (-133, **-15%**)

### Corrections Appliquées: **131 occurrences**

---

## ✅ Travail Complété

### 1. Infrastructure ✅
- Configuration YAML complète et validée
- Helper `config_helpers.py` pour backend
- Hook `useAppConfig.ts` pour frontend
- Scripts automatisés de correction

### 2. Backend - Fichiers Corrigés ✅
- `awana_auth_routes.py` - Partiellement (rôles, statuts)
- `mission_routes.py` - Listes de rôles, permissions
- `validation_routes.py` - Types et statuts de validation
- `profile_routes.py` - Types de profil
- `google_auth_routes.py` - Rôles OAuth
- `document_routes.py` - Permissions admin

### 3. Tests ✅
- `test_config.py` - ✅ Tous les tests passent (11/11)
- Pas de régression introduite

---

## 🚧 Travail Restant (403 occurrences critiques)

### Catégories

| Catégorie | Occurrences | Action |
|-----------|-------------|---------|
| **roles** | 223 | Frontend + backend complexes |
| **validation_types** | 129 | Frontend surtout |
| **user_status** | 60 | Backend + frontend |
| **application_status** | 51 | Frontend workflow |
| **mission_status** | 16 | Frontend |

---

## 📋 Actions Requises par Fichier

### 🔴 PRIORITÉ 1 - Frontend Critique

#### 1. `/app/apps/web/src/App.tsx` (70 occurrences)

**Lignes à corriger**:
```typescript
// ❌ AVANT (lignes 45-49)
if (user.roles.includes('admin')) return '/admin'
if (user.roles.includes('interim')) return '/interimaire'
if (user.roles.includes('company')) return '/entreprise'
if (user.roles.includes('agency')) return '/agence'

// ✅ APRÈS
import { useRoles } from '@/hooks/useAppConfig'

const roles = useRoles()
if (user.roles.includes(roles.admin)) return '/admin'
if (user.roles.includes(roles.interim)) return '/interimaire'
if (user.roles.includes(roles.company)) return '/entreprise'
if (user.roles.includes(roles.agency)) return '/agence'
```

**Routes protégées** (lignes 60+):
```typescript
// ❌ AVANT
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>

// ✅ APRÈS
<ProtectedRoute requiredRoles={[roles.admin, roles.super_admin]}>
```

**Estimation**: 2-3 heures  
**Impact**: 🔴 Critique - Affecte tout le routing

---

#### 2. `/app/apps/web/src/features/admin/pages/ValidationsPage.tsx` (76 occurrences)

**Types de validation**:
```typescript
// ❌ AVANT
if (validation.validation_type === 'interim')
if (type === 'company')

// ✅ APRÈS
import { useValidationTypes } from '@/hooks/useAppConfig'

const validationTypes = useValidationTypes()
if (validation.validation_type === validationTypes.interim)
if (type === validationTypes.company)
```

**Statuts**:
```typescript
// ❌ AVANT
if (validation.status === 'pending')
if (status === 'approved')

// ✅ APRÈS
import { useValidationStatuses } from '@/hooks/useReferences'

const { data: statuses } = useReferences('validation_statuses')
const pendingStatus = statuses?.find(s => s.code === 'pending')
```

**Estimation**: 3-4 heures  
**Impact**: 🔴 Critique - Page principale de validation

---

#### 3. `/app/apps/web/src/features/auth/pages/RegisterPage.tsx` (32 occurrences)

**Sélection de rôle**:
```typescript
// ❌ AVANT
<option value="interim">Intérimaire</option>
<option value="company">Entreprise</option>
<option value="agency">Agence</option>

// ✅ APRÈS
import { useRoles } from '@/hooks/useAppConfig'

const roles = useRoles()
<option value={roles.interim}>Intérimaire</option>
<option value={roles.company}>Entreprise</option>
<option value={roles.agency}>Agence</option>
```

**Estimation**: 1-2 heures  
**Impact**: 🟠 Haute - Inscription utilisateur

---

#### 4. `/app/apps/web/src/features/auth/pages/RoleSelectionPage.tsx` (20 occurrences)

**Cartes de sélection de rôle**:
```typescript
// ❌ AVANT
onClick={() => selectRole('interim')}
onClick={() => selectRole('company')}

// ✅ APRÈS
const roles = useRoles()
onClick={() => selectRole(roles.interim)}
onClick={() => selectRole(roles.company)}
```

**Estimation**: 1 heure  
**Impact**: 🟠 Haute

---

#### 5. `/app/apps/web/src/components/Sidebar.tsx` (16 occurrences)

**Navigation conditionnelle**:
```typescript
// ❌ AVANT
{user?.roles.includes('admin') && (
  <NavLink to="/admin">Admin</NavLink>
)}

// ✅ APRÈS
const roles = useRoles()
{user?.roles.includes(roles.admin) && (
  <NavLink to="/admin">Admin</NavLink>
)}
```

**Estimation**: 1 heure  
**Impact**: 🟡 Moyenne

---

### 🟡 PRIORITÉ 2 - Backend Complexe

#### 6. `/app/auth-microservice/awana_auth_routes.py` (77 occurrences restantes)

**Types de corrections**:

**a) Clés JSON (OK - À garder)**:
```python
# ✅ Ces valeurs sont des clés de réponse JSON, pas du code
return {
    "admin": admin_count,  # OK
    "company": company_count,  # OK
}
```

**b) Comparaisons inline dans conditions complexes**:
```python
# ❌ À corriger
if user_email in admin_emails and user_role not in ["admin", "super_admin"]:

# ✅ Après
admin_roles = [cfg.get_admin_role(), cfg.get_super_admin_role()]
if user_email in admin_emails and user_role not in admin_roles:
```

**c) Default values dans création d'objets**:
```python
# ❌ À corriger
new_user = {
    "roles": ["interim"],  # Default role
    "status": "pending"
}

# ✅ Après
new_user = {
    "roles": [cfg.get_interim_role()],
    "status": cfg.get_pending_status()
}
```

**Estimation**: 3-4 heures  
**Impact**: 🟠 Haute

---

#### 7. `/app/auth-microservice/google_auth_routes.py` (32 occurrences)

**Assignation de rôles par défaut**:
```python
# ❌ À corriger
default_role = "interim"
roles = [default_role]

# ✅ Après
default_role = cfg.get_interim_role()
roles = [default_role]
```

**Estimation**: 1-2 heures  
**Impact**: 🟡 Moyenne

---

#### 8. `/app/auth-microservice/mission_routes.py` (26 occurrences)

**Permissions complexes**:
```python
# ❌ À corriger
can_manage = any(r in user_roles for r in ["admin", "super_admin", "commercial", "company"])

# ✅ Après
manage_roles = cfg.get_mission_permission_roles("manage")
can_manage = any(r in user_roles for r in manage_roles)
```

**Estimation**: 2 heures  
**Impact**: 🟠 Haute

---

### 🟢 PRIORITÉ 3 - Données de Seed (IGNORER)

#### 9. `/app/auth-microservice/scripts/seed_mission_references.py` (32 occurrences)

**⚠️ ACTION: AUCUNE - Ces valeurs sont les DONNÉES de référence**

Ces fichiers créent les données en base de données. Les "valeurs en dur" sont normales ici car ce sont les valeurs de référence elles-mêmes :

```python
{
    "code": "draft",  # ✅ OK - C'est la donnée
    "label_fr": "Brouillon",  # ✅ OK - C'est la donnée
}
```

**Fichiers concernés** (à IGNORER dans l'audit):
- `seed_mission_references.py`
- `seed_additional_references.py`
- `add_super_admin.py`

**Impact**: ⚪ Aucun - Pas de correction nécessaire

---

## 📊 Estimation Totale Restante

| Fichier | Occurrences | Heures | Priorité |
|---------|-------------|--------|----------|
| App.tsx | 70 | 2-3h | 🔴 |
| ValidationsPage.tsx | 76 | 3-4h | 🔴 |
| RegisterPage.tsx | 32 | 1-2h | 🟠 |
| RoleSelectionPage.tsx | 20 | 1h | 🟠 |
| Sidebar.tsx | 16 | 1h | 🟡 |
| awana_auth_routes.py | 40* | 3-4h | 🟠 |
| google_auth_routes.py | 20* | 1-2h | 🟡 |
| mission_routes.py | 26 | 2h | 🟠 |
| **TOTAL** | **~300** | **14-21h** | |

\* Après exclusion des clés JSON et données de seed

---

## 🎯 Plan d'Exécution Recommandé

### Jour 1 (4-6h) - Frontend Critique
1. **App.tsx** - Routing principal
2. **ValidationsPage.tsx** - Workflow validation
3. Tester l'application complète

### Jour 2 (3-4h) - Frontend Secondaire
4. **RegisterPage.tsx** - Inscription
5. **RoleSelectionPage.tsx** - Sélection rôle
6. **Sidebar.tsx** - Navigation
7. Tester parcours utilisateur complet

### Jour 3 (4-6h) - Backend Complexe
8. **awana_auth_routes.py** - Cas complexes
9. **mission_routes.py** - Permissions
10. **google_auth_routes.py** - OAuth
11. Tests backend complets

### Jour 4 (2-3h) - Validation & Documentation
12. Tests de régression complets
13. Audit final (objectif: 0 critiques)
14. Documentation des changements
15. Formation équipe

**Durée totale**: 13-19 heures de développement (2-3 jours)

---

## ✅ Critères de Validation Finale

La Phase A sera considérée **COMPLÈTE** quand:

- [ ] Audit retourne **0 occurrences critiques** (hors données de seed)
- [ ] Tous les tests automatisés passent
- [ ] Application frontend fonctionnelle (navigation, auth, validation)
- [ ] Application backend fonctionnelle (API, permissions, workflows)
- [ ] Code review effectuée
- [ ] Documentation mise à jour
- [ ] Équipe formée sur le nouveau système

---

## 🔧 Outils Disponibles

### Backend
```python
from awana_auth.utils.config_helpers import cfg

# Rôles
cfg.get_admin_role()
cfg.get_all_roles()

# Statuts
cfg.get_active_status()
cfg.get_all_user_statuses()

# Permissions
cfg.get_mission_permission_roles("create")
cfg.user_has_any_role(user_roles, [cfg.get_admin_role()])
```

### Frontend
```typescript
import { useRoles, useUserStatuses, useAppConfig } from '@/hooks/useAppConfig'

const roles = useRoles()
const userStatuses = useUserStatuses()
const config = useAppConfig()

// Utilisation
if (user.roles.includes(roles.admin))
if (status === userStatuses.active)
```

### Scripts
```bash
# Tester configuration
python scripts/test_config.py

# Corriger backend automatiquement
python scripts/fix_hardcoded_values.py

# Audit
python scripts/audit_hardcoded_values.py

# Services
sudo supervisorctl restart all
```

---

## 📞 Support

**Questions techniques**: Voir `CONFIGURATION_SYSTEM_GUIDE.md`  
**Exemples de code**: Voir fichiers déjà corrigés  
**Patterns**: Voir `config_helpers.py` et `useAppConfig.ts`

---

**Status**: 🟡 **Phase A en cours - 26% complété**  
**Prochaine étape**: Corriger `App.tsx` et `ValidationsPage.tsx` (Frontend critique)
