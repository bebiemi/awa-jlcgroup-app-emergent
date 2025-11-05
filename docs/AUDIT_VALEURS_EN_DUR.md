# 🔍 Audit des Valeurs en Dur - Rapport Complet

**Date**: 2025-11-05 02:20:30

---

## 📊 Résumé Exécutif

**Total de valeurs en dur trouvées**: 886

### Par Sévérité

| Sévérité | Nombre | Pourcentage |
|----------|--------|-------------|
| 🔴 CRITICAL | 504 | 56.9% |
| 🟠 HIGH | 90 | 10.2% |
| 🟡 MEDIUM | 107 | 12.1% |
| 🟢 LOW | 185 | 20.9% |

### Par Catégorie

| Catégorie | Nombre |
|-----------|--------|
| roles | 294 |
| messages | 169 |
| validation_types | 159 |
| contract_types | 79 |
| user_status | 74 |
| application_status | 51 |
| delays_days | 17 |
| numeric_limits | 16 |
| mission_status | 16 |
| document_types | 11 |

### Top 15 Fichiers

| Fichier | Nombre de valeurs en dur |
|---------|--------------------------|
| `auth-microservice/awana_auth_routes.py` | 110 |
| `apps/web/src/features/admin/pages/ValidationsPage.tsx` | 76 |
| `apps/web/src/App.tsx` | 70 |
| `auth-microservice/mission_routes.py` | 61 |
| `auth-microservice/google_auth_routes.py` | 47 |
| `auth-microservice/profile_routes.py` | 42 |
| `auth-microservice/validation_routes.py` | 32 |
| `auth-microservice/scripts/seed_mission_references.py` | 32 |
| `apps/web/src/features/auth/pages/RegisterPage.tsx` | 32 |
| `apps/web/src/features/auth/pages/RoleSelectionPage.tsx` | 20 |
| `auth-microservice/mfa_routes.py` | 19 |
| `auth-microservice/awana_auth/rbac/models.py` | 18 |
| `apps/web/src/features/admin/pages/ValidationsList.tsx` | 18 |
| `apps/web/src/types/index.ts` | 17 |
| `auth-microservice/security_routes.py` | 16 |

---

## 🔴 Sévérité: CRITICAL

**Total**: 504 occurrences

### 📄 `apps/web/src/App.tsx`

**1. Ligne 45** | Catégorie: `roles`

```
if (user.roles.includes('admin')) return '/admin'
```

**Valeur en dur**: `'admin'`

**2. Ligne 46** | Catégorie: `roles`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**3. Ligne 46** | Catégorie: `validation_types`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**4. Ligne 47** | Catégorie: `roles`

```
if (user.roles.includes('company')) return '/entreprise'
```

**Valeur en dur**: `'company'`

**5. Ligne 47** | Catégorie: `validation_types`

```
if (user.roles.includes('company')) return '/entreprise'
```

**Valeur en dur**: `'company'`

**6. Ligne 48** | Catégorie: `roles`

```
if (user.roles.includes('agency')) return '/agence'
```

**Valeur en dur**: `'agency'`

**7. Ligne 67** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin']}>
```

**Valeur en dur**: `'admin'`

**8. Ligne 75** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin']}>
```

**Valeur en dur**: `'admin'`

**9. Ligne 83** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**10. Ligne 83** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**11. Ligne 91** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**12. Ligne 91** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**13. Ligne 99** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**14. Ligne 99** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**15. Ligne 107** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**16. Ligne 107** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**17. Ligne 115** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**18. Ligne 115** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**19. Ligne 123** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**20. Ligne 123** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**21. Ligne 131** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'admin'`

**22. Ligne 131** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
```

**Valeur en dur**: `'super_admin'`

**23. Ligne 141** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'admin'`

**24. Ligne 141** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'super_admin'`

**25. Ligne 141** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**26. Ligne 141** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'commercial'`

**27. Ligne 141** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**28. Ligne 149** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'admin'`

**29. Ligne 149** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'super_admin'`

**30. Ligne 149** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**31. Ligne 149** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'commercial'`

**32. Ligne 149** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**33. Ligne 157** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'admin'`

**34. Ligne 157** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'super_admin'`

**35. Ligne 157** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**36. Ligne 157** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'commercial'`

**37. Ligne 157** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**38. Ligne 165** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'admin'`

**39. Ligne 165** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'super_admin'`

**40. Ligne 165** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**41. Ligne 165** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'commercial'`

**42. Ligne 165** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial', 'company']}>
```

**Valeur en dur**: `'company'`

**43. Ligne 173** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial']}>
```

**Valeur en dur**: `'admin'`

**44. Ligne 173** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial']}>
```

**Valeur en dur**: `'super_admin'`

**45. Ligne 173** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['admin', 'super_admin', 'commercial']}>
```

**Valeur en dur**: `'commercial'`

**46. Ligne 183** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**47. Ligne 183** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**48. Ligne 191** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**49. Ligne 191** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**50. Ligne 199** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**51. Ligne 199** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**52. Ligne 207** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**53. Ligne 207** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**54. Ligne 216** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**55. Ligne 216** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**56. Ligne 224** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**57. Ligne 224** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**58. Ligne 232** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['company']}>
```

**Valeur en dur**: `'company'`

**59. Ligne 232** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['company']}>
```

**Valeur en dur**: `'company'`

**60. Ligne 240** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['company']}>
```

**Valeur en dur**: `'company'`

**61. Ligne 240** | Catégorie: `validation_types`

```
<ProtectedRoute requiredRoles={['company']}>
```

**Valeur en dur**: `'company'`

**62. Ligne 248** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['agency']}>
```

**Valeur en dur**: `'agency'`

**63. Ligne 256** | Catégorie: `roles`

```
<ProtectedRoute requiredRoles={['commercial']}>
```

**Valeur en dur**: `'commercial'`


### 📄 `apps/web/src/components/Breadcrumb.tsx`

**1. Ligne 11** | Catégorie: `roles`

```
'admin': 'Administration',
```

**Valeur en dur**: `'admin'`


### 📄 `apps/web/src/components/LoginModal.tsx`

**1. Ligne 41** | Catégorie: `roles`

```
if (result.user.roles.includes('admin') || result.user.roles.includes('super_admin')) {
```

**Valeur en dur**: `'admin'`

**2. Ligne 41** | Catégorie: `roles`

```
if (result.user.roles.includes('admin') || result.user.roles.includes('super_admin')) {
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 43** | Catégorie: `roles`

```
} else if (result.user.roles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**4. Ligne 43** | Catégorie: `validation_types`

```
} else if (result.user.roles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**5. Ligne 45** | Catégorie: `roles`

```
} else if (result.user.roles.includes('company')) {
```

**Valeur en dur**: `'company'`

**6. Ligne 45** | Catégorie: `validation_types`

```
} else if (result.user.roles.includes('company')) {
```

**Valeur en dur**: `'company'`


### 📄 `apps/web/src/components/Sidebar.tsx`

**1. Ligne 49** | Catégorie: `roles`

```
if (user.roles.includes('admin') || user.roles.includes('super_admin')) return '/admin'
```

**Valeur en dur**: `'admin'`

**2. Ligne 49** | Catégorie: `roles`

```
if (user.roles.includes('admin') || user.roles.includes('super_admin')) return '/admin'
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 50** | Catégorie: `roles`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**4. Ligne 50** | Catégorie: `validation_types`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**5. Ligne 51** | Catégorie: `roles`

```
if (user.roles.includes('company')) return '/entreprise'
```

**Valeur en dur**: `'company'`

**6. Ligne 51** | Catégorie: `validation_types`

```
if (user.roles.includes('company')) return '/entreprise'
```

**Valeur en dur**: `'company'`

**7. Ligne 52** | Catégorie: `roles`

```
if (user.roles.includes('agency')) return '/agence'
```

**Valeur en dur**: `'agency'`

**8. Ligne 58** | Catégorie: `roles`

```
const isAdmin = user.roles.includes('admin') || user.roles.includes('super_admin')
```

**Valeur en dur**: `'admin'`

**9. Ligne 58** | Catégorie: `roles`

```
const isAdmin = user.roles.includes('admin') || user.roles.includes('super_admin')
```

**Valeur en dur**: `'super_admin'`

**10. Ligne 59** | Catégorie: `roles`

```
const isInterim = user.roles.includes('interim')
```

**Valeur en dur**: `'interim'`

**11. Ligne 59** | Catégorie: `validation_types`

```
const isInterim = user.roles.includes('interim')
```

**Valeur en dur**: `'interim'`

**12. Ligne 60** | Catégorie: `roles`

```
const isCompany = user.roles.includes('company')
```

**Valeur en dur**: `'company'`

**13. Ligne 60** | Catégorie: `validation_types`

```
const isCompany = user.roles.includes('company')
```

**Valeur en dur**: `'company'`

**14. Ligne 61** | Catégorie: `roles`

```
const isCommercial = user.roles.includes('commercial')
```

**Valeur en dur**: `'commercial'`


### 📄 `apps/web/src/features/admin/api/validationApi.ts`

**1. Ligne 10** | Catégorie: `application_status`

```
status: 'pending' | 'approved' | 'rejected'
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/admin/components/EditUserModal.tsx`

**1. Ligne 115** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'admin'`

**2. Ligne 115** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 115** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'company'`

**4. Ligne 115** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'interim'`

**5. Ligne 115** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'agency'`

**6. Ligne 115** | Catégorie: `validation_types`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'interim'`

**7. Ligne 115** | Catégorie: `validation_types`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'company'`


### 📄 `apps/web/src/features/admin/pages/CreateUserPage.tsx`

**1. Ligne 266** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'admin'`

**2. Ligne 266** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 266** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'company'`

**4. Ligne 266** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'interim'`

**5. Ligne 266** | Catégorie: `roles`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'agency'`

**6. Ligne 266** | Catégorie: `validation_types`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'interim'`

**7. Ligne 266** | Catégorie: `validation_types`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'company'`


### 📄 `apps/web/src/features/admin/pages/UserManagementPage.tsx`

**1. Ligne 230** | Catégorie: `roles`

```
<option value="admin">Admin</option>
```

**Valeur en dur**: `"admin"`

**2. Ligne 231** | Catégorie: `roles`

```
<option value="super_admin">Super Admin</option>
```

**Valeur en dur**: `"super_admin"`

**3. Ligne 232** | Catégorie: `roles`

```
<option value="interim">Intérimaire</option>
```

**Valeur en dur**: `"interim"`

**4. Ligne 232** | Catégorie: `validation_types`

```
<option value="interim">Intérimaire</option>
```

**Valeur en dur**: `"interim"`

**5. Ligne 233** | Catégorie: `roles`

```
<option value="company">Société</option>
```

**Valeur en dur**: `"company"`

**6. Ligne 233** | Catégorie: `validation_types`

```
<option value="company">Société</option>
```

**Valeur en dur**: `"company"`

**7. Ligne 234** | Catégorie: `roles`

```
<option value="agency">Agence</option>
```

**Valeur en dur**: `"agency"`


### 📄 `apps/web/src/features/admin/pages/ValidationsList.tsx`

**1. Ligne 106** | Catégorie: `application_status`

```
onClick={() => setStatusFilter('rejected')}
```

**Valeur en dur**: `'rejected'`

**2. Ligne 109** | Catégorie: `application_status`

```
statusFilter === 'rejected'
```

**Valeur en dur**: `'rejected'`

**3. Ligne 174** | Catégorie: `roles`

```
validation.validation_type === 'interim'
```

**Valeur en dur**: `'interim'`

**4. Ligne 174** | Catégorie: `validation_types`

```
validation.validation_type === 'interim'
```

**Valeur en dur**: `'interim'`

**5. Ligne 178** | Catégorie: `roles`

```
{validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
```

**Valeur en dur**: `'interim'`

**6. Ligne 178** | Catégorie: `validation_types`

```
{validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
```

**Valeur en dur**: `'interim'`

**7. Ligne 186** | Catégorie: `application_status`

```
validation.status === 'rejected' && 'bg-red-100 text-red-800'
```

**Valeur en dur**: `'rejected'`

**8. Ligne 190** | Catégorie: `application_status`

```
{validation.status === 'rejected' && 'Refusé'}
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/admin/pages/ValidationsPage.tsx`

**1. Ligne 27** | Catégorie: `roles`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'company'`

**2. Ligne 27** | Catégorie: `roles`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**3. Ligne 27** | Catégorie: `validation_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**4. Ligne 27** | Catégorie: `validation_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'company'`

**5. Ligne 27** | Catégorie: `validation_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**6. Ligne 30** | Catégorie: `roles`

```
const [activeTab, setActiveTab] = useState<TabType>('interim')
```

**Valeur en dur**: `'interim'`

**7. Ligne 30** | Catégorie: `validation_types`

```
const [activeTab, setActiveTab] = useState<TabType>('interim')
```

**Valeur en dur**: `'interim'`

**8. Ligne 36** | Catégorie: `roles`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'company'`

**9. Ligne 36** | Catégorie: `roles`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'interim'`

**10. Ligne 36** | Catégorie: `validation_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'interim'`

**11. Ligne 36** | Catégorie: `validation_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'company'`

**12. Ligne 36** | Catégorie: `validation_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'collaborator'`

**13. Ligne 41** | Catégorie: `roles`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'company'`

**14. Ligne 41** | Catégorie: `roles`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'interim'`

**15. Ligne 41** | Catégorie: `validation_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'interim'`

**16. Ligne 41** | Catégorie: `validation_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'company'`

**17. Ligne 41** | Catégorie: `validation_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'collaborator'`

**18. Ligne 44** | Catégorie: `roles`

```
if (type === 'interim') {
```

**Valeur en dur**: `'interim'`

**19. Ligne 44** | Catégorie: `validation_types`

```
if (type === 'interim') {
```

**Valeur en dur**: `'interim'`

**20. Ligne 45** | Catégorie: `roles`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'interim' && v.status === 'pending')
```

**Valeur en dur**: `'interim'`

**21. Ligne 45** | Catégorie: `validation_types`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'interim' && v.status === 'pending')
```

**Valeur en dur**: `'interim'`

**22. Ligne 46** | Catégorie: `roles`

```
} else if (type === 'company') {
```

**Valeur en dur**: `'company'`

**23. Ligne 46** | Catégorie: `validation_types`

```
} else if (type === 'company') {
```

**Valeur en dur**: `'company'`

**24. Ligne 47** | Catégorie: `roles`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'company' && v.status === 'pending')
```

**Valeur en dur**: `'company'`

**25. Ligne 47** | Catégorie: `validation_types`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'company' && v.status === 'pending')
```

**Valeur en dur**: `'company'`

**26. Ligne 48** | Catégorie: `validation_types`

```
} else if (type === 'collaborator') {
```

**Valeur en dur**: `'collaborator'`

**27. Ligne 49** | Catégorie: `validation_types`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'collaborator' && v.status === 'pending')
```

**Valeur en dur**: `'collaborator'`

**28. Ligne 82** | Catégorie: `validation_types`

```
if (selectedValidation?.validation_type === 'collaborator') {
```

**Valeur en dur**: `'collaborator'`

**29. Ligne 86** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin'].includes(role)) ||
```

**Valeur en dur**: `'admin'`

**30. Ligne 86** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin'].includes(role)) ||
```

**Valeur en dur**: `'super_admin'`

**31. Ligne 89** | Catégorie: `roles`

```
user.email?.toLowerCase().includes('commercial')
```

**Valeur en dur**: `'commercial'`

**32. Ligne 95** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
```

**Valeur en dur**: `'admin'`

**33. Ligne 95** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
```

**Valeur en dur**: `'super_admin'`

**34. Ligne 95** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
```

**Valeur en dur**: `'commercial'`

**35. Ligne 227** | Catégorie: `roles`

```
onClick={() => handleTileClick('interim')}
```

**Valeur en dur**: `'interim'`

**36. Ligne 227** | Catégorie: `validation_types`

```
onClick={() => handleTileClick('interim')}
```

**Valeur en dur**: `'interim'`

**37. Ligne 240** | Catégorie: `roles`

```
onClick={() => handleTileClick('company')}
```

**Valeur en dur**: `'company'`

**38. Ligne 240** | Catégorie: `validation_types`

```
onClick={() => handleTileClick('company')}
```

**Valeur en dur**: `'company'`

**39. Ligne 253** | Catégorie: `validation_types`

```
onClick={() => handleTileClick('collaborator')}
```

**Valeur en dur**: `'collaborator'`

**40. Ligne 284** | Catégorie: `roles`

```
onClick={() => setActiveTab('interim')}
```

**Valeur en dur**: `'interim'`

**41. Ligne 284** | Catégorie: `validation_types`

```
onClick={() => setActiveTab('interim')}
```

**Valeur en dur**: `'interim'`

**42. Ligne 286** | Catégorie: `roles`

```
activeTab === 'interim'
```

**Valeur en dur**: `'interim'`

**43. Ligne 286** | Catégorie: `validation_types`

```
activeTab === 'interim'
```

**Valeur en dur**: `'interim'`

**44. Ligne 294** | Catégorie: `roles`

```
onClick={() => setActiveTab('company')}
```

**Valeur en dur**: `'company'`

**45. Ligne 294** | Catégorie: `validation_types`

```
onClick={() => setActiveTab('company')}
```

**Valeur en dur**: `'company'`

**46. Ligne 296** | Catégorie: `roles`

```
activeTab === 'company'
```

**Valeur en dur**: `'company'`

**47. Ligne 296** | Catégorie: `validation_types`

```
activeTab === 'company'
```

**Valeur en dur**: `'company'`

**48. Ligne 304** | Catégorie: `validation_types`

```
onClick={() => setActiveTab('collaborator')}
```

**Valeur en dur**: `'collaborator'`

**49. Ligne 306** | Catégorie: `validation_types`

```
activeTab === 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**50. Ligne 325** | Catégorie: `application_status`

```
<option value="rejected">Rejetées</option>
```

**Valeur en dur**: `"rejected"`

**51. Ligne 346** | Catégorie: `validation_types`

```
{validation.validation_type === 'collaborator' && (
```

**Valeur en dur**: `'collaborator'`

**52. Ligne 364** | Catégorie: `validation_types`

```
{validation.validation_type === 'collaborator' && (
```

**Valeur en dur**: `'collaborator'`

**53. Ligne 514** | Catégorie: `validation_types`

```
{selectedValidation?.validation_type === 'collaborator' && (
```

**Valeur en dur**: `'collaborator'`

**54. Ligne 570** | Catégorie: `roles`

```
bulkActionType === 'interim' ? 'Intérimaires' :
```

**Valeur en dur**: `'interim'`

**55. Ligne 570** | Catégorie: `validation_types`

```
bulkActionType === 'interim' ? 'Intérimaires' :
```

**Valeur en dur**: `'interim'`

**56. Ligne 571** | Catégorie: `roles`

```
bulkActionType === 'company' ? 'Entreprises' :
```

**Valeur en dur**: `'company'`

**57. Ligne 571** | Catégorie: `validation_types`

```
bulkActionType === 'company' ? 'Entreprises' :
```

**Valeur en dur**: `'company'`

**58. Ligne 572** | Catégorie: `validation_types`

```
bulkActionType === 'collaborator' ? 'Collaborateurs' :
```

**Valeur en dur**: `'collaborator'`


### 📄 `apps/web/src/features/auth/api/authApi.ts`

**1. Ligne 35** | Catégorie: `roles`

```
role: 'interim' | 'company'
```

**Valeur en dur**: `'company'`

**2. Ligne 35** | Catégorie: `roles`

```
role: 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**3. Ligne 35** | Catégorie: `validation_types`

```
role: 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**4. Ligne 35** | Catégorie: `validation_types`

```
role: 'interim' | 'company'
```

**Valeur en dur**: `'company'`


### 📄 `apps/web/src/features/auth/pages/GoogleCallback.tsx`

**1. Ligne 57** | Catégorie: `roles`

```
if (data.user.status === 'pending' && data.user.roles.length === 1 && data.user.roles[0] === 'interim') {
```

**Valeur en dur**: `'interim'`

**2. Ligne 57** | Catégorie: `validation_types`

```
if (data.user.status === 'pending' && data.user.roles.length === 1 && data.user.roles[0] === 'interim') {
```

**Valeur en dur**: `'interim'`

**3. Ligne 83** | Catégorie: `roles`

```
if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'admin'`

**4. Ligne 83** | Catégorie: `roles`

```
if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'super_admin'`

**5. Ligne 85** | Catégorie: `roles`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**6. Ligne 85** | Catégorie: `validation_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**7. Ligne 87** | Catégorie: `roles`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**8. Ligne 87** | Catégorie: `validation_types`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**9. Ligne 89** | Catégorie: `roles`

```
} else if (userRoles.includes('agency')) {
```

**Valeur en dur**: `'agency'`


### 📄 `apps/web/src/features/auth/pages/LoginPage.tsx`

**1. Ligne 48** | Catégorie: `roles`

```
if (userRoles.includes('commercial')) {
```

**Valeur en dur**: `'commercial'`

**2. Ligne 50** | Catégorie: `roles`

```
} else if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'admin'`

**3. Ligne 50** | Catégorie: `roles`

```
} else if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'super_admin'`

**4. Ligne 52** | Catégorie: `roles`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**5. Ligne 52** | Catégorie: `validation_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**6. Ligne 54** | Catégorie: `roles`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**7. Ligne 54** | Catégorie: `validation_types`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**8. Ligne 56** | Catégorie: `roles`

```
} else if (userRoles.includes('agency')) {
```

**Valeur en dur**: `'agency'`


### 📄 `apps/web/src/features/auth/pages/MfaVerificationPage.tsx`

**1. Ligne 43** | Catégorie: `roles`

```
if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'admin'`

**2. Ligne 43** | Catégorie: `roles`

```
if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 45** | Catégorie: `roles`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**4. Ligne 45** | Catégorie: `validation_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**5. Ligne 47** | Catégorie: `roles`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**6. Ligne 47** | Catégorie: `validation_types`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**7. Ligne 49** | Catégorie: `roles`

```
} else if (userRoles.includes('agency')) {
```

**Valeur en dur**: `'agency'`


### 📄 `apps/web/src/features/auth/pages/RegisterPage.tsx`

**1. Ligne 9** | Catégorie: `roles`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'company'`

**2. Ligne 9** | Catégorie: `roles`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**3. Ligne 9** | Catégorie: `validation_types`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**4. Ligne 9** | Catégorie: `validation_types`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'company'`

**5. Ligne 104** | Catégorie: `roles`

```
} else if (formData.role === 'company') {
```

**Valeur en dur**: `'company'`

**6. Ligne 104** | Catégorie: `validation_types`

```
} else if (formData.role === 'company') {
```

**Valeur en dur**: `'company'`

**7. Ligne 147** | Catégorie: `roles`

```
if (formData.role === 'interim' && !formData.isCollaborator) {
```

**Valeur en dur**: `'interim'`

**8. Ligne 147** | Catégorie: `validation_types`

```
if (formData.role === 'interim' && !formData.isCollaborator) {
```

**Valeur en dur**: `'interim'`

**9. Ligne 150** | Catégorie: `roles`

```
} else if (formData.role === 'company') {
```

**Valeur en dur**: `'company'`

**10. Ligne 150** | Catégorie: `validation_types`

```
} else if (formData.role === 'company') {
```

**Valeur en dur**: `'company'`

**11. Ligne 269** | Catégorie: `roles`

```
onClick={() => handleRoleSelect('interim')}
```

**Valeur en dur**: `'interim'`

**12. Ligne 269** | Catégorie: `validation_types`

```
onClick={() => handleRoleSelect('interim')}
```

**Valeur en dur**: `'interim'`

**13. Ligne 271** | Catégorie: `roles`

```
formData.role === 'interim'
```

**Valeur en dur**: `'interim'`

**14. Ligne 271** | Catégorie: `validation_types`

```
formData.role === 'interim'
```

**Valeur en dur**: `'interim'`

**15. Ligne 276** | Catégorie: `roles`

```
{formData.role === 'interim' && (
```

**Valeur en dur**: `'interim'`

**16. Ligne 276** | Catégorie: `validation_types`

```
{formData.role === 'interim' && (
```

**Valeur en dur**: `'interim'`

**17. Ligne 291** | Catégorie: `roles`

```
onClick={() => handleRoleSelect('company')}
```

**Valeur en dur**: `'company'`

**18. Ligne 291** | Catégorie: `validation_types`

```
onClick={() => handleRoleSelect('company')}
```

**Valeur en dur**: `'company'`

**19. Ligne 293** | Catégorie: `roles`

```
formData.role === 'company'
```

**Valeur en dur**: `'company'`

**20. Ligne 293** | Catégorie: `validation_types`

```
formData.role === 'company'
```

**Valeur en dur**: `'company'`

**21. Ligne 298** | Catégorie: `roles`

```
{formData.role === 'company' && (
```

**Valeur en dur**: `'company'`

**22. Ligne 298** | Catégorie: `validation_types`

```
{formData.role === 'company' && (
```

**Valeur en dur**: `'company'`

**23. Ligne 518** | Catégorie: `roles`

```
{formData.role === 'interim' && (
```

**Valeur en dur**: `'interim'`

**24. Ligne 518** | Catégorie: `validation_types`

```
{formData.role === 'interim' && (
```

**Valeur en dur**: `'interim'`

**25. Ligne 552** | Catégorie: `roles`

```
{formData.role === 'company' && (
```

**Valeur en dur**: `'company'`

**26. Ligne 552** | Catégorie: `validation_types`

```
{formData.role === 'company' && (
```

**Valeur en dur**: `'company'`


### 📄 `apps/web/src/features/auth/pages/RoleSelectionPage.tsx`

**1. Ligne 8** | Catégorie: `roles`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'company'`

**2. Ligne 8** | Catégorie: `roles`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**3. Ligne 8** | Catégorie: `validation_types`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**4. Ligne 8** | Catégorie: `validation_types`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'company'`

**5. Ligne 71** | Catégorie: `roles`

```
const dashboardPath = selectedRole === 'interim' ? '/interimaire' :
```

**Valeur en dur**: `'interim'`

**6. Ligne 71** | Catégorie: `validation_types`

```
const dashboardPath = selectedRole === 'interim' ? '/interimaire' :
```

**Valeur en dur**: `'interim'`

**7. Ligne 72** | Catégorie: `roles`

```
selectedRole === 'company' ? '/entreprise' : '/profile'
```

**Valeur en dur**: `'company'`

**8. Ligne 72** | Catégorie: `validation_types`

```
selectedRole === 'company' ? '/entreprise' : '/profile'
```

**Valeur en dur**: `'company'`

**9. Ligne 107** | Catégorie: `roles`

```
onClick={() => handleRoleSelect('interim')}
```

**Valeur en dur**: `'interim'`

**10. Ligne 107** | Catégorie: `validation_types`

```
onClick={() => handleRoleSelect('interim')}
```

**Valeur en dur**: `'interim'`

**11. Ligne 110** | Catégorie: `roles`

```
selectedRole === 'interim'
```

**Valeur en dur**: `'interim'`

**12. Ligne 110** | Catégorie: `validation_types`

```
selectedRole === 'interim'
```

**Valeur en dur**: `'interim'`

**13. Ligne 129** | Catégorie: `roles`

```
onClick={() => handleRoleSelect('company')}
```

**Valeur en dur**: `'company'`

**14. Ligne 129** | Catégorie: `validation_types`

```
onClick={() => handleRoleSelect('company')}
```

**Valeur en dur**: `'company'`

**15. Ligne 132** | Catégorie: `roles`

```
selectedRole === 'company'
```

**Valeur en dur**: `'company'`

**16. Ligne 132** | Catégorie: `validation_types`

```
selectedRole === 'company'
```

**Valeur en dur**: `'company'`


### 📄 `apps/web/src/features/interim/pages/InterimDashboard.tsx`

**1. Ligne 67** | Catégorie: `application_status`

```
validation.status === 'rejected' && 'border-red-500 bg-red-50'
```

**Valeur en dur**: `'rejected'`

**2. Ligne 78** | Catégorie: `application_status`

```
{validation.status === 'rejected' && (
```

**Valeur en dur**: `'rejected'`

**3. Ligne 105** | Catégorie: `application_status`

```
{validation.status === 'rejected' && (
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/missions/api/missionApi.ts`

**1. Ligne 19** | Catégorie: `application_status`

```
| 'contract_pending'
```

**Valeur en dur**: `'contract_pending'`

**2. Ligne 20** | Catégorie: `application_status`

```
| 'contract_signed'
```

**Valeur en dur**: `'contract_signed'`

**3. Ligne 26** | Catégorie: `application_status`

```
| 'submitted'
```

**Valeur en dur**: `'submitted'`

**4. Ligne 31** | Catégorie: `application_status`

```
| 'interview_scheduled'
```

**Valeur en dur**: `'interview_scheduled'`

**5. Ligne 42** | Catégorie: `application_status`

```
| 'contract_pending'
```

**Valeur en dur**: `'contract_pending'`

**6. Ligne 43** | Catégorie: `application_status`

```
| 'contract_signed'
```

**Valeur en dur**: `'contract_signed'`

**7. Ligne 45** | Catégorie: `application_status`

```
| 'rejected'
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/missions/pages/ApplicationsManagementPage.tsx`

**1. Ligne 28** | Catégorie: `application_status`

```
{ value: 'submitted', label: 'Nouvelles', count: 0 },
```

**Valeur en dur**: `'submitted'`

**2. Ligne 30** | Catégorie: `application_status`

```
{ value: 'interview_scheduled', label: 'Entretiens', count: 0 },
```

**Valeur en dur**: `'interview_scheduled'`

**3. Ligne 33** | Catégorie: `application_status`

```
{ value: 'rejected', label: 'Rejetées', count: 0 },
```

**Valeur en dur**: `'rejected'`

**4. Ligne 103** | Catégorie: `application_status`

```
if (selectedFilter === 'rejected') {
```

**Valeur en dur**: `'rejected'`

**5. Ligne 104** | Catégorie: `application_status`

```
return app.status.includes('rejected') || app.status === 'rejected'
```

**Valeur en dur**: `'rejected'`

**6. Ligne 104** | Catégorie: `application_status`

```
return app.status.includes('rejected') || app.status === 'rejected'
```

**Valeur en dur**: `'rejected'`

**7. Ligne 114** | Catégorie: `application_status`

```
: filter.value === 'rejected'
```

**Valeur en dur**: `'rejected'`

**8. Ligne 115** | Catégorie: `application_status`

```
? applications.filter(a => a.status.includes('rejected') || a.status === 'rejected').length
```

**Valeur en dur**: `'rejected'`

**9. Ligne 115** | Catégorie: `application_status`

```
? applications.filter(a => a.status.includes('rejected') || a.status === 'rejected').length
```

**Valeur en dur**: `'rejected'`

**10. Ligne 170** | Catégorie: `application_status`

```
status: 'interview_scheduled',
```

**Valeur en dur**: `'interview_scheduled'`

**11. Ligne 354** | Catégorie: `application_status`

```
{app.status === 'submitted' && (
```

**Valeur en dur**: `'submitted'`


### 📄 `apps/web/src/features/missions/pages/MissionDetailPage.tsx`

**1. Ligne 76** | Catégorie: `roles`

```
const isAdmin = user?.roles.includes('admin') || user?.roles.includes('super_admin')
```

**Valeur en dur**: `'admin'`

**2. Ligne 76** | Catégorie: `roles`

```
const isAdmin = user?.roles.includes('admin') || user?.roles.includes('super_admin')
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 77** | Catégorie: `roles`

```
const isCommercial = user?.roles.includes('commercial')
```

**Valeur en dur**: `'commercial'`

**4. Ligne 315** | Catégorie: `application_status`

```
app.status.includes('rejected') ? 'bg-red-100 text-red-800' :
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/missions/pages/MyApplicationsPage.tsx`

**1. Ligne 108** | Catégorie: `application_status`

```
!['rejected', 'withdrawn', 'hired'].includes(app.status)
```

**Valeur en dur**: `'rejected'`

**2. Ligne 114** | Catégorie: `application_status`

```
['rejected', 'withdrawn'].includes(app.status) ||
```

**Valeur en dur**: `'rejected'`

**3. Ligne 115** | Catégorie: `application_status`

```
app.status.includes('rejected')
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/profile/api/profileApi.ts`

**1. Ligne 48** | Catégorie: `roles`

```
profile_type: 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'company'`

**2. Ligne 48** | Catégorie: `roles`

```
profile_type: 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**3. Ligne 48** | Catégorie: `validation_types`

```
profile_type: 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**4. Ligne 48** | Catégorie: `validation_types`

```
profile_type: 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'company'`

**5. Ligne 48** | Catégorie: `validation_types`

```
profile_type: 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'collaborator'`


### 📄 `apps/web/src/features/profile/pages/ProfilePage.tsx`

**1. Ligne 89** | Catégorie: `roles`

```
{profileType === 'interim' && <InterimProfileForm profile={profile} />}
```

**Valeur en dur**: `'interim'`

**2. Ligne 89** | Catégorie: `validation_types`

```
{profileType === 'interim' && <InterimProfileForm profile={profile} />}
```

**Valeur en dur**: `'interim'`

**3. Ligne 90** | Catégorie: `roles`

```
{profileType === 'company' && <CompanyProfileForm profile={profile} />}
```

**Valeur en dur**: `'company'`

**4. Ligne 90** | Catégorie: `validation_types`

```
{profileType === 'company' && <CompanyProfileForm profile={profile} />}
```

**Valeur en dur**: `'company'`

**5. Ligne 91** | Catégorie: `validation_types`

```
{profileType === 'collaborator' && (
```

**Valeur en dur**: `'collaborator'`


### 📄 `apps/web/src/pages/LandingPage.tsx`

**1. Ligne 25** | Catégorie: `roles`

```
if (user.roles.includes('admin') || user.roles.includes('super_admin')) return '/admin'
```

**Valeur en dur**: `'admin'`

**2. Ligne 25** | Catégorie: `roles`

```
if (user.roles.includes('admin') || user.roles.includes('super_admin')) return '/admin'
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 26** | Catégorie: `roles`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**4. Ligne 26** | Catégorie: `validation_types`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**5. Ligne 27** | Catégorie: `roles`

```
if (user.roles.includes('company')) return '/entreprise'
```

**Valeur en dur**: `'company'`

**6. Ligne 27** | Catégorie: `validation_types`

```
if (user.roles.includes('company')) return '/entreprise'
```

**Valeur en dur**: `'company'`

**7. Ligne 28** | Catégorie: `roles`

```
if (user.roles.includes('agency')) return '/agence'
```

**Valeur en dur**: `'agency'`


### 📄 `apps/web/src/types/index.ts`

**1. Ligne 8** | Catégorie: `application_status`

```
status: 'active' | 'pending' | 'rejected'
```

**Valeur en dur**: `'rejected'`

**2. Ligne 14** | Catégorie: `roles`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'admin'`

**3. Ligne 14** | Catégorie: `roles`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'company'`

**4. Ligne 14** | Catégorie: `roles`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'interim'`

**5. Ligne 14** | Catégorie: `roles`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'agency'`

**6. Ligne 14** | Catégorie: `validation_types`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'interim'`

**7. Ligne 14** | Catégorie: `validation_types`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'company'`

**8. Ligne 58** | Catégorie: `roles`

```
export type ValidationType = 'company' | 'interim'
```

**Valeur en dur**: `'company'`

**9. Ligne 58** | Catégorie: `roles`

```
export type ValidationType = 'company' | 'interim'
```

**Valeur en dur**: `'interim'`

**10. Ligne 58** | Catégorie: `validation_types`

```
export type ValidationType = 'company' | 'interim'
```

**Valeur en dur**: `'interim'`

**11. Ligne 58** | Catégorie: `validation_types`

```
export type ValidationType = 'company' | 'interim'
```

**Valeur en dur**: `'company'`

**12. Ligne 59** | Catégorie: `application_status`

```
export type ValidationStatus = 'pending' | 'approved' | 'rejected'
```

**Valeur en dur**: `'rejected'`


### 📄 `auth-microservice/add_super_admin.py`

**1. Ligne 26** | Catégorie: `roles`

```
"roles": ["admin", "super_admin"],
```

**Valeur en dur**: `"admin"`

**2. Ligne 26** | Catégorie: `roles`

```
"roles": ["admin", "super_admin"],
```

**Valeur en dur**: `"super_admin"`


### 📄 `auth-microservice/awana_auth/core/dependencies.py`

**1. Ligne 190** | Catégorie: `roles`

```
admin_roles = {"admin", "super_admin"}
```

**Valeur en dur**: `"admin"`

**2. Ligne 190** | Catégorie: `roles`

```
admin_roles = {"admin", "super_admin"}
```

**Valeur en dur**: `"super_admin"`

**3. Ligne 194** | Catégorie: `roles`

```
has_role = await rbac_manager.has_any_role(current_user.id, ["admin", "super_admin"])
```

**Valeur en dur**: `"admin"`

**4. Ligne 194** | Catégorie: `roles`

```
has_role = await rbac_manager.has_any_role(current_user.id, ["admin", "super_admin"])
```

**Valeur en dur**: `"super_admin"`

**5. Ligne 214** | Catégorie: `roles`

```
if "super_admin" not in user_roles:
```

**Valeur en dur**: `"super_admin"`

**6. Ligne 216** | Catégorie: `roles`

```
has_role = await rbac_manager.has_role(current_user.id, "super_admin")
```

**Valeur en dur**: `"super_admin"`


### 📄 `auth-microservice/awana_auth/core/location_models.py`

**1. Ligne 120** | Catégorie: `roles`

```
COMMERCIAL = "commercial"
```

**Valeur en dur**: `"commercial"`

**2. Ligne 121** | Catégorie: `roles`

```
ADMIN = "admin"
```

**Valeur en dur**: `"admin"`

**3. Ligne 122** | Catégorie: `roles`

```
SUPER_ADMIN = "super_admin"
```

**Valeur en dur**: `"super_admin"`

**4. Ligne 130** | Catégorie: `application_status`

```
REJECTED = "rejected"
```

**Valeur en dur**: `"rejected"`


### 📄 `auth-microservice/awana_auth/core/mission_models.py`

**1. Ligne 331** | Catégorie: `application_status`

```
INTERVIEW_SCHEDULED = "interview_scheduled"
```

**Valeur en dur**: `"interview_scheduled"`


### 📄 `auth-microservice/awana_auth/core/models.py`

**1. Ligne 140** | Catégorie: `roles`

```
ADMIN = "admin"
```

**Valeur en dur**: `"admin"`


### 📄 `auth-microservice/awana_auth/core/reference_models.py`

**1. Ligne 44** | Catégorie: `roles`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`

**2. Ligne 44** | Catégorie: `validation_types`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/awana_auth/rbac/decorators.py`

**1. Ligne 17** | Catégorie: `roles`

```
@require_role("admin", "super_admin")
```

**Valeur en dur**: `"admin"`

**2. Ligne 17** | Catégorie: `roles`

```
@require_role("admin", "super_admin")
```

**Valeur en dur**: `"super_admin"`


### 📄 `auth-microservice/awana_auth/rbac/models.py`

**1. Ligne 84** | Catégorie: `roles`

```
name="super_admin",
```

**Valeur en dur**: `"super_admin"`

**2. Ligne 92** | Catégorie: `roles`

```
name="admin",
```

**Valeur en dur**: `"admin"`


### 📄 `auth-microservice/awana_auth_routes.py`

**1. Ligne 170** | Catégorie: `validation_types`

```
validation_type = "collaborator"
```

**Valeur en dur**: `"collaborator"`

**2. Ligne 313** | Catégorie: `roles`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**3. Ligne 313** | Catégorie: `validation_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**4. Ligne 327** | Catégorie: `roles`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**5. Ligne 327** | Catégorie: `validation_types`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**6. Ligne 342** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'admin'`

**7. Ligne 342** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'super_admin'`

**8. Ligne 647** | Catégorie: `roles`

```
if email in admin_emails and "admin" not in user.roles:
```

**Valeur en dur**: `"admin"`

**9. Ligne 648** | Catégorie: `roles`

```
user.roles.append("admin")
```

**Valeur en dur**: `"admin"`

**10. Ligne 674** | Catégorie: `roles`

```
user_roles = ["admin"] if email in admin_emails else ["user"]
```

**Valeur en dur**: `"admin"`

**11. Ligne 782** | Catégorie: `roles`

```
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
```

**Valeur en dur**: `'admin'`

**12. Ligne 884** | Catégorie: `roles`

```
if "admin" not in user.roles:
```

**Valeur en dur**: `"admin"`

**13. Ligne 885** | Catégorie: `roles`

```
user.roles.append("admin")
```

**Valeur en dur**: `"admin"`

**14. Ligne 906** | Catégorie: `roles`

```
roles=["admin"]
```

**Valeur en dur**: `"admin"`

**15. Ligne 918** | Catégorie: `roles`

```
await rbac_manager.grant_role(user.id, "admin", granted_by="system")
```

**Valeur en dur**: `"admin"`

**16. Ligne 1156** | Catégorie: `roles`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**17. Ligne 1156** | Catégorie: `roles`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**18. Ligne 1156** | Catégorie: `validation_types`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**19. Ligne 1156** | Catégorie: `validation_types`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**20. Ligne 1159** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**21. Ligne 1159** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**22. Ligne 1159** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**23. Ligne 1159** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**24. Ligne 1474** | Catégorie: `roles`

```
admin_users = await db.users.count_documents({"roles": "admin"})
```

**Valeur en dur**: `"admin"`

**25. Ligne 1475** | Catégorie: `roles`

```
super_admin_users = await db.users.count_documents({"roles": "super_admin"})
```

**Valeur en dur**: `"super_admin"`

**26. Ligne 1476** | Catégorie: `roles`

```
interim_users = await db.users.count_documents({"roles": "interim"})
```

**Valeur en dur**: `"interim"`

**27. Ligne 1476** | Catégorie: `validation_types`

```
interim_users = await db.users.count_documents({"roles": "interim"})
```

**Valeur en dur**: `"interim"`

**28. Ligne 1477** | Catégorie: `roles`

```
company_users = await db.users.count_documents({"roles": "company"})
```

**Valeur en dur**: `"company"`

**29. Ligne 1477** | Catégorie: `validation_types`

```
company_users = await db.users.count_documents({"roles": "company"})
```

**Valeur en dur**: `"company"`

**30. Ligne 1478** | Catégorie: `roles`

```
agency_users = await db.users.count_documents({"roles": "agency"})
```

**Valeur en dur**: `"agency"`

**31. Ligne 1509** | Catégorie: `roles`

```
"admin": admin_users,
```

**Valeur en dur**: `"admin"`

**32. Ligne 1510** | Catégorie: `roles`

```
"super_admin": super_admin_users,
```

**Valeur en dur**: `"super_admin"`

**33. Ligne 1511** | Catégorie: `roles`

```
"interim": interim_users,
```

**Valeur en dur**: `"interim"`

**34. Ligne 1511** | Catégorie: `validation_types`

```
"interim": interim_users,
```

**Valeur en dur**: `"interim"`

**35. Ligne 1512** | Catégorie: `roles`

```
"company": company_users,
```

**Valeur en dur**: `"company"`

**36. Ligne 1512** | Catégorie: `validation_types`

```
"company": company_users,
```

**Valeur en dur**: `"company"`

**37. Ligne 1513** | Catégorie: `roles`

```
"agency": agency_users
```

**Valeur en dur**: `"agency"`

**38. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"admin"`

**39. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"super_admin"`

**40. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"company"`

**41. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"interim"`

**42. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"agency"`

**43. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"commercial"`

**44. Ligne 2068** | Catégorie: `roles`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"validator"`

**45. Ligne 2068** | Catégorie: `validation_types`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"interim"`

**46. Ligne 2068** | Catégorie: `validation_types`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"company"`


### 📄 `auth-microservice/document_routes.py`

**1. Ligne 155** | Catégorie: `roles`

```
is_admin = any(role in user_roles for role in ["admin", "super_admin", "commercial"])
```

**Valeur en dur**: `"admin"`

**2. Ligne 155** | Catégorie: `roles`

```
is_admin = any(role in user_roles for role in ["admin", "super_admin", "commercial"])
```

**Valeur en dur**: `"super_admin"`

**3. Ligne 155** | Catégorie: `roles`

```
is_admin = any(role in user_roles for role in ["admin", "super_admin", "commercial"])
```

**Valeur en dur**: `"commercial"`

**4. Ligne 219** | Catégorie: `roles`

```
is_admin = any(role in user_roles for role in ["admin", "super_admin"])
```

**Valeur en dur**: `"admin"`

**5. Ligne 219** | Catégorie: `roles`

```
is_admin = any(role in user_roles for role in ["admin", "super_admin"])
```

**Valeur en dur**: `"super_admin"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 154** | Catégorie: `roles`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**2. Ligne 154** | Catégorie: `validation_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**3. Ligne 168** | Catégorie: `roles`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**4. Ligne 168** | Catégorie: `validation_types`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**5. Ligne 183** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'admin'`

**6. Ligne 183** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'super_admin'`

**7. Ligne 315** | Catégorie: `roles`

```
profile_type=roles[0] if roles else "interim",
```

**Valeur en dur**: `"interim"`

**8. Ligne 315** | Catégorie: `validation_types`

```
profile_type=roles[0] if roles else "interim",
```

**Valeur en dur**: `"interim"`

**9. Ligne 343** | Catégorie: `roles`

```
await rbac_manager.grant_role(user_id, "interim", granted_by="system")
```

**Valeur en dur**: `"interim"`

**10. Ligne 343** | Catégorie: `validation_types`

```
await rbac_manager.grant_role(user_id, "interim", granted_by="system")
```

**Valeur en dur**: `"interim"`

**11. Ligne 347** | Catégorie: `roles`

```
roles = ["interim"]
```

**Valeur en dur**: `"interim"`

**12. Ligne 347** | Catégorie: `validation_types`

```
roles = ["interim"]
```

**Valeur en dur**: `"interim"`

**13. Ligne 357** | Catégorie: `roles`

```
profile_type=roles[0] if roles else "interim",
```

**Valeur en dur**: `"interim"`

**14. Ligne 357** | Catégorie: `validation_types`

```
profile_type=roles[0] if roles else "interim",
```

**Valeur en dur**: `"interim"`

**15. Ligne 538** | Catégorie: `roles`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**16. Ligne 538** | Catégorie: `roles`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**17. Ligne 538** | Catégorie: `validation_types`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**18. Ligne 538** | Catégorie: `validation_types`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**19. Ligne 541** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**20. Ligne 541** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**21. Ligne 541** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**22. Ligne 541** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**23. Ligne 569** | Catégorie: `roles`

```
await rbac_manager.revoke_role(user_id, "interim")
```

**Valeur en dur**: `"interim"`

**24. Ligne 569** | Catégorie: `validation_types`

```
await rbac_manager.revoke_role(user_id, "interim")
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/init_permissions.py`

**1. Ligne 16** | Catégorie: `roles`

```
{"name": "gestion_utilisateurs", "label": "Gestion des utilisateurs", "description": "Créer, modifier, supprimer des utilisateurs", "module": "admin"},
```

**Valeur en dur**: `"admin"`

**2. Ligne 17** | Catégorie: `roles`

```
{"name": "gestion_groupes", "label": "Gestion des groupes", "description": "Créer, modifier, supprimer des groupes", "module": "admin"},
```

**Valeur en dur**: `"admin"`

**3. Ligne 18** | Catégorie: `roles`

```
{"name": "gestion_profils", "label": "Gestion des profils", "description": "Créer, modifier, supprimer des profils de permissions", "module": "admin"},
```

**Valeur en dur**: `"admin"`

**4. Ligne 19** | Catégorie: `roles`

```
{"name": "voir_utilisateurs", "label": "Voir les utilisateurs", "description": "Consulter la liste des utilisateurs", "module": "admin"},
```

**Valeur en dur**: `"admin"`


### 📄 `auth-microservice/mission_routes.py`

**1. Ligne 109** | Catégorie: `application_status`

```
if existing_app["status"] in ["rejected", "rejected_initial"]:
```

**Valeur en dur**: `"rejected"`

**2. Ligne 159** | Catégorie: `roles`

```
if not any(role in user_roles for role in ["admin", "super_admin", "company", "commercial"]):
```

**Valeur en dur**: `"admin"`

**3. Ligne 159** | Catégorie: `roles`

```
if not any(role in user_roles for role in ["admin", "super_admin", "company", "commercial"]):
```

**Valeur en dur**: `"super_admin"`

**4. Ligne 159** | Catégorie: `roles`

```
if not any(role in user_roles for role in ["admin", "super_admin", "company", "commercial"]):
```

**Valeur en dur**: `"company"`

**5. Ligne 159** | Catégorie: `roles`

```
if not any(role in user_roles for role in ["admin", "super_admin", "company", "commercial"]):
```

**Valeur en dur**: `"commercial"`

**6. Ligne 159** | Catégorie: `validation_types`

```
if not any(role in user_roles for role in ["admin", "super_admin", "company", "commercial"]):
```

**Valeur en dur**: `"company"`

**7. Ligne 216** | Catégorie: `roles`

```
if "interim" in user_roles:
```

**Valeur en dur**: `"interim"`

**8. Ligne 216** | Catégorie: `validation_types`

```
if "interim" in user_roles:
```

**Valeur en dur**: `"interim"`

**9. Ligne 219** | Catégorie: `roles`

```
elif "company" in user_roles:
```

**Valeur en dur**: `"company"`

**10. Ligne 219** | Catégorie: `validation_types`

```
elif "company" in user_roles:
```

**Valeur en dur**: `"company"`

**11. Ligne 226** | Catégorie: `roles`

```
if company_id and ("admin" in user_roles or "super_admin" in user_roles):
```

**Valeur en dur**: `"admin"`

**12. Ligne 226** | Catégorie: `roles`

```
if company_id and ("admin" in user_roles or "super_admin" in user_roles):
```

**Valeur en dur**: `"super_admin"`

**13. Ligne 257** | Catégorie: `roles`

```
if "interim" in user_roles and mission["status"] != MissionStatus.PUBLISHED:
```

**Valeur en dur**: `"interim"`

**14. Ligne 257** | Catégorie: `validation_types`

```
if "interim" in user_roles and mission["status"] != MissionStatus.PUBLISHED:
```

**Valeur en dur**: `"interim"`

**15. Ligne 263** | Catégorie: `roles`

```
if "company" in user_roles and mission["company_id"] != user_id:
```

**Valeur en dur**: `"company"`

**16. Ligne 263** | Catégorie: `validation_types`

```
if "company" in user_roles and mission["company_id"] != user_id:
```

**Valeur en dur**: `"company"`

**17. Ligne 296** | Catégorie: `roles`

```
"admin" in user_roles or
```

**Valeur en dur**: `"admin"`

**18. Ligne 297** | Catégorie: `roles`

```
"super_admin" in user_roles or
```

**Valeur en dur**: `"super_admin"`

**19. Ligne 351** | Catégorie: `roles`

```
"admin" in user_roles or
```

**Valeur en dur**: `"admin"`

**20. Ligne 352** | Catégorie: `roles`

```
"super_admin" in user_roles or
```

**Valeur en dur**: `"super_admin"`

**21. Ligne 389** | Catégorie: `roles`

```
can_publish = "admin" in user_roles or "super_admin" in user_roles or "commercial" in user_roles
```

**Valeur en dur**: `"admin"`

**22. Ligne 389** | Catégorie: `roles`

```
can_publish = "admin" in user_roles or "super_admin" in user_roles or "commercial" in user_roles
```

**Valeur en dur**: `"super_admin"`

**23. Ligne 389** | Catégorie: `roles`

```
can_publish = "admin" in user_roles or "super_admin" in user_roles or "commercial" in user_roles
```

**Valeur en dur**: `"commercial"`

**24. Ligne 428** | Catégorie: `roles`

```
if "interim" not in user_roles:
```

**Valeur en dur**: `"interim"`

**25. Ligne 428** | Catégorie: `validation_types`

```
if "interim" not in user_roles:
```

**Valeur en dur**: `"interim"`

**26. Ligne 509** | Catégorie: `roles`

```
"admin" in user_roles or
```

**Valeur en dur**: `"admin"`

**27. Ligne 510** | Catégorie: `roles`

```
"super_admin" in user_roles or
```

**Valeur en dur**: `"super_admin"`

**28. Ligne 511** | Catégorie: `roles`

```
"commercial" in user_roles or
```

**Valeur en dur**: `"commercial"`

**29. Ligne 512** | Catégorie: `roles`

```
(mission["company_id"] == user_id and "company" in user_roles)
```

**Valeur en dur**: `"company"`

**30. Ligne 512** | Catégorie: `validation_types`

```
(mission["company_id"] == user_id and "company" in user_roles)
```

**Valeur en dur**: `"company"`

**31. Ligne 567** | Catégorie: `roles`

```
can_update = "admin" in user_roles or "super_admin" in user_roles or "commercial" in user_roles
```

**Valeur en dur**: `"admin"`

**32. Ligne 567** | Catégorie: `roles`

```
can_update = "admin" in user_roles or "super_admin" in user_roles or "commercial" in user_roles
```

**Valeur en dur**: `"super_admin"`

**33. Ligne 567** | Catégorie: `roles`

```
can_update = "admin" in user_roles or "super_admin" in user_roles or "commercial" in user_roles
```

**Valeur en dur**: `"commercial"`


### 📄 `auth-microservice/profile_routes.py`

**1. Ligne 39** | Catégorie: `roles`

```
if profile_type == "interim":
```

**Valeur en dur**: `"interim"`

**2. Ligne 39** | Catégorie: `validation_types`

```
if profile_type == "interim":
```

**Valeur en dur**: `"interim"`

**3. Ligne 59** | Catégorie: `roles`

```
elif profile_type == "company":
```

**Valeur en dur**: `"company"`

**4. Ligne 59** | Catégorie: `validation_types`

```
elif profile_type == "company":
```

**Valeur en dur**: `"company"`

**5. Ligne 76** | Catégorie: `roles`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**6. Ligne 76** | Catégorie: `validation_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**7. Ligne 97** | Catégorie: `roles`

```
return {"profile_type": "interim", "profile": profile}
```

**Valeur en dur**: `"interim"`

**8. Ligne 97** | Catégorie: `validation_types`

```
return {"profile_type": "interim", "profile": profile}
```

**Valeur en dur**: `"interim"`

**9. Ligne 99** | Catégorie: `roles`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**10. Ligne 99** | Catégorie: `validation_types`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**11. Ligne 109** | Catégorie: `roles`

```
return {"profile_type": "company", "profile": profile}
```

**Valeur en dur**: `"company"`

**12. Ligne 109** | Catégorie: `validation_types`

```
return {"profile_type": "company", "profile": profile}
```

**Valeur en dur**: `"company"`

**13. Ligne 120** | Catégorie: `validation_types`

```
return {"profile_type": "collaborator", "profile": profile}
```

**Valeur en dur**: `"collaborator"`

**14. Ligne 135** | Catégorie: `roles`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**15. Ligne 135** | Catégorie: `validation_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**16. Ligne 137** | Catégorie: `roles`

```
profile_type = "interim"
```

**Valeur en dur**: `"interim"`

**17. Ligne 137** | Catégorie: `validation_types`

```
profile_type = "interim"
```

**Valeur en dur**: `"interim"`

**18. Ligne 138** | Catégorie: `roles`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**19. Ligne 138** | Catégorie: `validation_types`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**20. Ligne 140** | Catégorie: `roles`

```
profile_type = "company"
```

**Valeur en dur**: `"company"`

**21. Ligne 140** | Catégorie: `validation_types`

```
profile_type = "company"
```

**Valeur en dur**: `"company"`

**22. Ligne 143** | Catégorie: `validation_types`

```
profile_type = "collaborator"
```

**Valeur en dur**: `"collaborator"`

**23. Ligne 216** | Catégorie: `roles`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**24. Ligne 216** | Catégorie: `validation_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**25. Ligne 218** | Catégorie: `roles`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**26. Ligne 218** | Catégorie: `validation_types`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**27. Ligne 284** | Catégorie: `roles`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**28. Ligne 284** | Catégorie: `validation_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**29. Ligne 286** | Catégorie: `roles`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`

**30. Ligne 286** | Catégorie: `validation_types`

```
elif "company" in current_user.roles:
```

**Valeur en dur**: `"company"`


### 📄 `auth-microservice/scripts/seed_additional_references.py`

**1. Ligne 32** | Catégorie: `roles`

```
"code": "admin",
```

**Valeur en dur**: `"admin"`

**2. Ligne 50** | Catégorie: `roles`

```
"code": "super_admin",
```

**Valeur en dur**: `"super_admin"`

**3. Ligne 68** | Catégorie: `roles`

```
"code": "company",
```

**Valeur en dur**: `"company"`

**4. Ligne 68** | Catégorie: `validation_types`

```
"code": "company",
```

**Valeur en dur**: `"company"`

**5. Ligne 86** | Catégorie: `roles`

```
"code": "agency",
```

**Valeur en dur**: `"agency"`

**6. Ligne 104** | Catégorie: `roles`

```
"code": "commercial",
```

**Valeur en dur**: `"commercial"`

**7. Ligne 122** | Catégorie: `roles`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`

**8. Ligne 122** | Catégorie: `validation_types`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/scripts/seed_mission_references.py`

**1. Ligne 144** | Catégorie: `application_status`

```
"next_possible_statuses": ["interview_scheduled", "rejected"],
```

**Valeur en dur**: `"interview_scheduled"`

**2. Ligne 144** | Catégorie: `application_status`

```
"next_possible_statuses": ["interview_scheduled", "rejected"],
```

**Valeur en dur**: `"rejected"`

**3. Ligne 145** | Catégorie: `roles`

```
"requires_action_from": "company"
```

**Valeur en dur**: `"company"`

**4. Ligne 145** | Catégorie: `validation_types`

```
"requires_action_from": "company"
```

**Valeur en dur**: `"company"`

**5. Ligne 155** | Catégorie: `application_status`

```
"code": "interview_scheduled",
```

**Valeur en dur**: `"interview_scheduled"`

**6. Ligne 164** | Catégorie: `roles`

```
"requires_action_from": "company"
```

**Valeur en dur**: `"company"`

**7. Ligne 164** | Catégorie: `validation_types`

```
"requires_action_from": "company"
```

**Valeur en dur**: `"company"`

**8. Ligne 182** | Catégorie: `application_status`

```
"next_possible_statuses": ["selected", "rejected"],
```

**Valeur en dur**: `"selected"`

**9. Ligne 182** | Catégorie: `application_status`

```
"next_possible_statuses": ["selected", "rejected"],
```

**Valeur en dur**: `"rejected"`

**10. Ligne 183** | Catégorie: `roles`

```
"requires_action_from": "company"
```

**Valeur en dur**: `"company"`

**11. Ligne 183** | Catégorie: `validation_types`

```
"requires_action_from": "company"
```

**Valeur en dur**: `"company"`

**12. Ligne 193** | Catégorie: `application_status`

```
"code": "selected",
```

**Valeur en dur**: `"selected"`

**13. Ligne 201** | Catégorie: `application_status`

```
"next_possible_statuses": ["medical_pending"],
```

**Valeur en dur**: `"medical_pending"`

**14. Ligne 202** | Catégorie: `roles`

```
"requires_action_from": "agency"
```

**Valeur en dur**: `"agency"`

**15. Ligne 212** | Catégorie: `application_status`

```
"code": "medical_pending",
```

**Valeur en dur**: `"medical_pending"`

**16. Ligne 221** | Catégorie: `roles`

```
"requires_action_from": "agency",
```

**Valeur en dur**: `"agency"`

**17. Ligne 240** | Catégorie: `application_status`

```
"next_possible_statuses": ["contract_pending"],
```

**Valeur en dur**: `"contract_pending"`

**18. Ligne 241** | Catégorie: `roles`

```
"requires_action_from": "agency"
```

**Valeur en dur**: `"agency"`

**19. Ligne 270** | Catégorie: `application_status`

```
"code": "contract_pending",
```

**Valeur en dur**: `"contract_pending"`

**20. Ligne 278** | Catégorie: `application_status`

```
"next_possible_statuses": ["contract_signed"],
```

**Valeur en dur**: `"contract_signed"`

**21. Ligne 279** | Catégorie: `roles`

```
"requires_action_from": "agency",
```

**Valeur en dur**: `"agency"`

**22. Ligne 290** | Catégorie: `application_status`

```
"code": "contract_signed",
```

**Valeur en dur**: `"contract_signed"`

**23. Ligne 309** | Catégorie: `application_status`

```
"code": "rejected",
```

**Valeur en dur**: `"rejected"`

**24. Ligne 370** | Catégorie: `roles`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`

**25. Ligne 370** | Catégorie: `validation_types`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/validation_routes.py`

**1. Ligne 77** | Catégorie: `roles`

```
pending_interim = await db.validations.count_documents({"status": "pending", "validation_type": "interim"})
```

**Valeur en dur**: `"interim"`

**2. Ligne 77** | Catégorie: `validation_types`

```
pending_interim = await db.validations.count_documents({"status": "pending", "validation_type": "interim"})
```

**Valeur en dur**: `"interim"`

**3. Ligne 78** | Catégorie: `roles`

```
pending_company = await db.validations.count_documents({"status": "pending", "validation_type": "company"})
```

**Valeur en dur**: `"company"`

**4. Ligne 78** | Catégorie: `validation_types`

```
pending_company = await db.validations.count_documents({"status": "pending", "validation_type": "company"})
```

**Valeur en dur**: `"company"`

**5. Ligne 79** | Catégorie: `validation_types`

```
pending_collaborator = await db.validations.count_documents({"status": "pending", "validation_type": "collaborator"})
```

**Valeur en dur**: `"collaborator"`

**6. Ligne 87** | Catégorie: `application_status`

```
total_rejected = await db.validations.count_documents({"status": "rejected"})
```

**Valeur en dur**: `"rejected"`

**7. Ligne 222** | Catégorie: `application_status`

```
"status": "rejected",
```

**Valeur en dur**: `"rejected"`

**8. Ligne 256** | Catégorie: `roles`

```
if not any(role in validator_roles for role in ["admin", "super_admin", "commercial"]):
```

**Valeur en dur**: `"admin"`

**9. Ligne 256** | Catégorie: `roles`

```
if not any(role in validator_roles for role in ["admin", "super_admin", "commercial"]):
```

**Valeur en dur**: `"super_admin"`

**10. Ligne 256** | Catégorie: `roles`

```
if not any(role in validator_roles for role in ["admin", "super_admin", "commercial"]):
```

**Valeur en dur**: `"commercial"`


## 🟠 Sévérité: HIGH

**Total**: 90 occurrences

### 📄 `apps/web/src/components/ActionButton.tsx`

**1. Ligne 13** | Catégorie: `user_status`

```
type ActionType = 'edit' | 'delete' | 'view' | 'approve' | 'reject' | 'assign' | 'reset' | 'block' | 'pending' | 'custom'
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/admin/api/usersApi.ts`

**1. Ligne 10** | Catégorie: `user_status`

```
status: 'active' | 'pending' | 'suspended' | 'deleted'
```

**Valeur en dur**: `'active'`

**2. Ligne 10** | Catégorie: `user_status`

```
status: 'active' | 'pending' | 'suspended' | 'deleted'
```

**Valeur en dur**: `'pending'`

**3. Ligne 10** | Catégorie: `user_status`

```
status: 'active' | 'pending' | 'suspended' | 'deleted'
```

**Valeur en dur**: `'suspended'`

**4. Ligne 10** | Catégorie: `user_status`

```
status: 'active' | 'pending' | 'suspended' | 'deleted'
```

**Valeur en dur**: `'deleted'`


### 📄 `apps/web/src/features/admin/api/validationApi.ts`

**1. Ligne 10** | Catégorie: `user_status`

```
status: 'pending' | 'approved' | 'rejected'
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/admin/components/BlockUserModal.tsx`

**1. Ligne 16** | Catégorie: `user_status`

```
const isSuspended = user.status === 'suspended'
```

**Valeur en dur**: `'suspended'`

**2. Ligne 18** | Catégorie: `user_status`

```
const newStatus = isSuspended ? 'active' : 'suspended'
```

**Valeur en dur**: `'active'`

**3. Ligne 18** | Catégorie: `user_status`

```
const newStatus = isSuspended ? 'active' : 'suspended'
```

**Valeur en dur**: `'suspended'`


### 📄 `apps/web/src/features/admin/pages/BusinessRulesPage.tsx`

**1. Ligne 40** | Catégorie: `user_status`

```
actions: { set_status: 'active', skip_validation: true },
```

**Valeur en dur**: `'active'`


### 📄 `apps/web/src/features/admin/pages/UserManagementPage.tsx`

**1. Ligne 213** | Catégorie: `user_status`

```
<option value="active">Actif</option>
```

**Valeur en dur**: `"active"`

**2. Ligne 214** | Catégorie: `user_status`

```
<option value="pending">En attente</option>
```

**Valeur en dur**: `"pending"`

**3. Ligne 215** | Catégorie: `user_status`

```
<option value="suspended">Suspendu</option>
```

**Valeur en dur**: `"suspended"`

**4. Ligne 216** | Catégorie: `user_status`

```
<option value="deleted">Supprimé</option>
```

**Valeur en dur**: `"deleted"`

**5. Ligne 320** | Catégorie: `user_status`

```
user.status === 'suspended'
```

**Valeur en dur**: `'suspended'`

**6. Ligne 324** | Catégorie: `user_status`

```
title={user.status === 'suspended' ? 'Débloquer' : 'Bloquer'}
```

**Valeur en dur**: `'suspended'`


### 📄 `apps/web/src/features/admin/pages/ValidationsList.tsx`

**1. Ligne 11** | Catégorie: `user_status`

```
const [statusFilter, setStatusFilter] = useState<string>('pending')
```

**Valeur en dur**: `'pending'`

**2. Ligne 84** | Catégorie: `user_status`

```
onClick={() => setStatusFilter('pending')}
```

**Valeur en dur**: `'pending'`

**3. Ligne 87** | Catégorie: `user_status`

```
statusFilter === 'pending'
```

**Valeur en dur**: `'pending'`

**4. Ligne 92** | Catégorie: `user_status`

```
En attente ({data?.items.filter(v => v.status === 'pending').length || 0})
```

**Valeur en dur**: `'pending'`

**5. Ligne 184** | Catégorie: `user_status`

```
validation.status === 'pending' && 'bg-yellow-100 text-yellow-800',
```

**Valeur en dur**: `'pending'`

**6. Ligne 188** | Catégorie: `user_status`

```
{validation.status === 'pending' && 'En attente'}
```

**Valeur en dur**: `'pending'`

**7. Ligne 197** | Catégorie: `user_status`

```
{validation.status === 'pending' && (
```

**Valeur en dur**: `'pending'`

**8. Ligne 221** | Catégorie: `user_status`

```
{validation.status !== 'pending' && (
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/admin/pages/ValidationsPage.tsx`

**1. Ligne 31** | Catégorie: `user_status`

```
const [statusFilter, setStatusFilter] = useState<string>('pending')
```

**Valeur en dur**: `'pending'`

**2. Ligne 45** | Catégorie: `user_status`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'interim' && v.status === 'pending')
```

**Valeur en dur**: `'pending'`

**3. Ligne 47** | Catégorie: `user_status`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'company' && v.status === 'pending')
```

**Valeur en dur**: `'pending'`

**4. Ligne 49** | Catégorie: `user_status`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'collaborator' && v.status === 'pending')
```

**Valeur en dur**: `'pending'`

**5. Ligne 51** | Catégorie: `user_status`

```
filtered = validations.filter((v: Validation) => v.has_location_warning && v.status === 'pending')
```

**Valeur en dur**: `'pending'`

**6. Ligne 53** | Catégorie: `user_status`

```
filtered = validations.filter((v: Validation) => v.status === 'pending')
```

**Valeur en dur**: `'pending'`

**7. Ligne 323** | Catégorie: `user_status`

```
<option value="pending">En attente</option>
```

**Valeur en dur**: `"pending"`

**8. Ligne 420** | Catégorie: `user_status`

```
{validation.status === 'pending' && (
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/auth/pages/GoogleCallback.tsx`

**1. Ligne 57** | Catégorie: `user_status`

```
if (data.user.status === 'pending' && data.user.roles.length === 1 && data.user.roles[0] === 'interim') {
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/company/pages/CompanyDashboard.tsx`

**1. Ligne 29** | Catégorie: `user_status`

```
status: 'active',
```

**Valeur en dur**: `'active'`

**2. Ligne 36** | Catégorie: `mission_status`

```
status: 'draft',
```

**Valeur en dur**: `'draft'`

**3. Ligne 168** | Catégorie: `user_status`

```
mission.status === 'active'
```

**Valeur en dur**: `'active'`

**4. Ligne 173** | Catégorie: `user_status`

```
{mission.status === 'active' ? 'Active' : 'Brouillon'}
```

**Valeur en dur**: `'active'`


### 📄 `apps/web/src/features/interim/pages/InterimDashboard.tsx`

**1. Ligne 65** | Catégorie: `user_status`

```
validation.status === 'pending' && 'border-yellow-500 bg-yellow-50',
```

**Valeur en dur**: `'pending'`

**2. Ligne 72** | Catégorie: `user_status`

```
{validation.status === 'pending' && (
```

**Valeur en dur**: `'pending'`

**3. Ligne 83** | Catégorie: `user_status`

```
{validation.status === 'pending' && (
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/missions/api/missionApi.ts`

**1. Ligne 6** | Catégorie: `mission_status`

```
| 'draft'
```

**Valeur en dur**: `'draft'`

**2. Ligne 8** | Catégorie: `mission_status`

```
| 'published'
```

**Valeur en dur**: `'published'`

**3. Ligne 22** | Catégorie: `mission_status`

```
| 'cancelled'
```

**Valeur en dur**: `'cancelled'`

**4. Ligne 48** | Catégorie: `user_status`

```
export type MedicalStatus = 'not_required' | 'pending' | 'scheduled' | 'completed_apte' | 'completed_inapte' | 'document_uploaded'
```

**Valeur en dur**: `'pending'`

**5. Ligne 50** | Catégorie: `mission_status`

```
export type ContractStatus = 'not_generated' | 'draft' | 'sent' | 'signed_by_interim' | 'signed_by_company' | 'fully_signed'
```

**Valeur en dur**: `'draft'`


### 📄 `apps/web/src/features/missions/pages/MissionDetailPage.tsx`

**1. Ligne 128** | Catégorie: `mission_status`

```
{mission.status === 'draft' && (
```

**Valeur en dur**: `'draft'`


### 📄 `apps/web/src/features/missions/pages/MissionsPage.tsx`

**1. Ligne 158** | Catégorie: `mission_status`

```
{missions.filter(m => m.status === 'published').length}
```

**Valeur en dur**: `'published'`

**2. Ligne 172** | Catégorie: `mission_status`

```
{missions.filter(m => !['completed', 'cancelled'].includes(m.status)).length}
```

**Valeur en dur**: `'cancelled'`

**3. Ligne 211** | Catégorie: `mission_status`

```
<option value="draft">Brouillons</option>
```

**Valeur en dur**: `"draft"`

**4. Ligne 212** | Catégorie: `mission_status`

```
<option value="published">Publiées</option>
```

**Valeur en dur**: `"published"`

**5. Ligne 288** | Catégorie: `mission_status`

```
{mission.status === 'draft' && (
```

**Valeur en dur**: `'draft'`

**6. Ligne 298** | Catégorie: `mission_status`

```
{!['completed', 'cancelled'].includes(mission.status) && (
```

**Valeur en dur**: `'cancelled'`


### 📄 `apps/web/src/types/index.ts`

**1. Ligne 8** | Catégorie: `user_status`

```
status: 'active' | 'pending' | 'rejected'
```

**Valeur en dur**: `'active'`

**2. Ligne 8** | Catégorie: `user_status`

```
status: 'active' | 'pending' | 'rejected'
```

**Valeur en dur**: `'pending'`

**3. Ligne 59** | Catégorie: `user_status`

```
export type ValidationStatus = 'pending' | 'approved' | 'rejected'
```

**Valeur en dur**: `'pending'`


### 📄 `auth-microservice/add_super_admin.py`

**1. Ligne 27** | Catégorie: `user_status`

```
"status": "active"
```

**Valeur en dur**: `"active"`


### 📄 `auth-microservice/awana_auth/core/dependencies.py`

**1. Ligne 139** | Catégorie: `user_status`

```
if user.status != "active":
```

**Valeur en dur**: `"active"`


### 📄 `auth-microservice/awana_auth/core/location_models.py`

**1. Ligne 128** | Catégorie: `user_status`

```
PENDING = "pending"
```

**Valeur en dur**: `"pending"`


### 📄 `auth-microservice/awana_auth/core/mission_models.py`

**1. Ligne 84** | Catégorie: `user_status`

```
PENDING = "pending"
```

**Valeur en dur**: `"pending"`

**2. Ligne 94** | Catégorie: `mission_status`

```
DRAFT = "draft"
```

**Valeur en dur**: `"draft"`


### 📄 `auth-microservice/awana_auth/core/models.py`

**1. Ligne 23** | Catégorie: `user_status`

```
ACTIVE = "active"
```

**Valeur en dur**: `"active"`

**2. Ligne 25** | Catégorie: `user_status`

```
SUSPENDED = "suspended"
```

**Valeur en dur**: `"suspended"`

**3. Ligne 26** | Catégorie: `user_status`

```
PENDING = "pending"
```

**Valeur en dur**: `"pending"`


### 📄 `auth-microservice/awana_auth/providers/google.py`

**1. Ligne 92** | Catégorie: `user_status`

```
status="active",
```

**Valeur en dur**: `"active"`

**2. Ligne 175** | Catégorie: `user_status`

```
status="active",
```

**Valeur en dur**: `"active"`


### 📄 `auth-microservice/awana_auth_routes.py`

**1. Ligne 180** | Catégorie: `user_status`

```
"status": "pending",
```

**Valeur en dur**: `"pending"`

**2. Ligne 1469** | Catégorie: `user_status`

```
active_users = await db.users.count_documents({"status": "active"})
```

**Valeur en dur**: `"active"`

**3. Ligne 1470** | Catégorie: `user_status`

```
pending_users = await db.users.count_documents({"status": "pending"})
```

**Valeur en dur**: `"pending"`

**4. Ligne 1471** | Catégorie: `user_status`

```
suspended_users = await db.users.count_documents({"status": "suspended"})
```

**Valeur en dur**: `"suspended"`

**5. Ligne 1504** | Catégorie: `user_status`

```
"active": active_users,
```

**Valeur en dur**: `"active"`

**6. Ligne 1505** | Catégorie: `user_status`

```
"pending": pending_users,
```

**Valeur en dur**: `"pending"`

**7. Ligne 1506** | Catégorie: `user_status`

```
"suspended": suspended_users
```

**Valeur en dur**: `"suspended"`

**8. Ligne 1967** | Catégorie: `user_status`

```
if new_status not in ["active", "pending", "suspended", "deleted"]:
```

**Valeur en dur**: `"active"`

**9. Ligne 1967** | Catégorie: `user_status`

```
if new_status not in ["active", "pending", "suspended", "deleted"]:
```

**Valeur en dur**: `"pending"`

**10. Ligne 1967** | Catégorie: `user_status`

```
if new_status not in ["active", "pending", "suspended", "deleted"]:
```

**Valeur en dur**: `"suspended"`

**11. Ligne 1967** | Catégorie: `user_status`

```
if new_status not in ["active", "pending", "suspended", "deleted"]:
```

**Valeur en dur**: `"deleted"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 384** | Catégorie: `user_status`

```
status=user_doc.get("status", "pending"),
```

**Valeur en dur**: `"pending"`

**2. Ligne 446** | Catégorie: `user_status`

```
"status": existing_user["status"] if existing_user else "pending",
```

**Valeur en dur**: `"pending"`

**3. Ligne 621** | Catégorie: `user_status`

```
status=updated_user_doc.get("status", "pending"),
```

**Valeur en dur**: `"pending"`


### 📄 `auth-microservice/scripts/seed_mission_references.py`

**1. Ligne 32** | Catégorie: `mission_status`

```
"code": "draft",
```

**Valeur en dur**: `"draft"`

**2. Ligne 51** | Catégorie: `mission_status`

```
"code": "published",
```

**Valeur en dur**: `"published"`

**3. Ligne 108** | Catégorie: `mission_status`

```
"code": "cancelled",
```

**Valeur en dur**: `"cancelled"`

**4. Ligne 136** | Catégorie: `user_status`

```
"code": "pending",
```

**Valeur en dur**: `"pending"`


### 📄 `auth-microservice/validation_routes.py`

**1. Ligne 76** | Catégorie: `user_status`

```
total_pending = await db.validations.count_documents({"status": "pending"})
```

**Valeur en dur**: `"pending"`

**2. Ligne 77** | Catégorie: `user_status`

```
pending_interim = await db.validations.count_documents({"status": "pending", "validation_type": "interim"})
```

**Valeur en dur**: `"pending"`

**3. Ligne 78** | Catégorie: `user_status`

```
pending_company = await db.validations.count_documents({"status": "pending", "validation_type": "company"})
```

**Valeur en dur**: `"pending"`

**4. Ligne 79** | Catégorie: `user_status`

```
pending_collaborator = await db.validations.count_documents({"status": "pending", "validation_type": "collaborator"})
```

**Valeur en dur**: `"pending"`

**5. Ligne 82** | Catégorie: `user_status`

```
"status": "pending",
```

**Valeur en dur**: `"pending"`

**6. Ligne 148** | Catégorie: `user_status`

```
if validation["status"] != "pending":
```

**Valeur en dur**: `"pending"`

**7. Ligne 200** | Catégorie: `user_status`

```
if validation["status"] != "pending":
```

**Valeur en dur**: `"pending"`


## 🟡 Sévérité: MEDIUM

**Total**: 107 occurrences

### 📄 `apps/web/src/App.tsx`

**1. Ligne 46** | Catégorie: `contract_types`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**2. Ligne 183** | Catégorie: `contract_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**3. Ligne 191** | Catégorie: `contract_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**4. Ligne 199** | Catégorie: `contract_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**5. Ligne 207** | Catégorie: `contract_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**6. Ligne 216** | Catégorie: `contract_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`

**7. Ligne 224** | Catégorie: `contract_types`

```
<ProtectedRoute requiredRoles={['interim']}>
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/components/LoginModal.tsx`

**1. Ligne 43** | Catégorie: `contract_types`

```
} else if (result.user.roles.includes('interim')) {
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/components/Sidebar.tsx`

**1. Ligne 50** | Catégorie: `contract_types`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`

**2. Ligne 59** | Catégorie: `contract_types`

```
const isInterim = user.roles.includes('interim')
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/admin/components/EditUserModal.tsx`

**1. Ligne 115** | Catégorie: `contract_types`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/admin/pages/CreateUserPage.tsx`

**1. Ligne 266** | Catégorie: `contract_types`

```
{['admin', 'super_admin', 'interim', 'company', 'agency'].map((role) => (
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/admin/pages/UserManagementPage.tsx`

**1. Ligne 232** | Catégorie: `contract_types`

```
<option value="interim">Intérimaire</option>
```

**Valeur en dur**: `"interim"`


### 📄 `apps/web/src/features/admin/pages/ValidationsList.tsx`

**1. Ligne 174** | Catégorie: `contract_types`

```
validation.validation_type === 'interim'
```

**Valeur en dur**: `'interim'`

**2. Ligne 178** | Catégorie: `contract_types`

```
{validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/admin/pages/ValidationsPage.tsx`

**1. Ligne 27** | Catégorie: `contract_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**2. Ligne 30** | Catégorie: `contract_types`

```
const [activeTab, setActiveTab] = useState<TabType>('interim')
```

**Valeur en dur**: `'interim'`

**3. Ligne 36** | Catégorie: `contract_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'interim'`

**4. Ligne 41** | Catégorie: `contract_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'interim'`

**5. Ligne 44** | Catégorie: `contract_types`

```
if (type === 'interim') {
```

**Valeur en dur**: `'interim'`

**6. Ligne 45** | Catégorie: `contract_types`

```
filtered = validations.filter((v: Validation) => v.validation_type === 'interim' && v.status === 'pending')
```

**Valeur en dur**: `'interim'`

**7. Ligne 227** | Catégorie: `contract_types`

```
onClick={() => handleTileClick('interim')}
```

**Valeur en dur**: `'interim'`

**8. Ligne 284** | Catégorie: `contract_types`

```
onClick={() => setActiveTab('interim')}
```

**Valeur en dur**: `'interim'`

**9. Ligne 286** | Catégorie: `contract_types`

```
activeTab === 'interim'
```

**Valeur en dur**: `'interim'`

**10. Ligne 570** | Catégorie: `contract_types`

```
bulkActionType === 'interim' ? 'Intérimaires' :
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/auth/api/authApi.ts`

**1. Ligne 35** | Catégorie: `contract_types`

```
role: 'interim' | 'company'
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/auth/pages/GoogleCallback.tsx`

**1. Ligne 57** | Catégorie: `contract_types`

```
if (data.user.status === 'pending' && data.user.roles.length === 1 && data.user.roles[0] === 'interim') {
```

**Valeur en dur**: `'interim'`

**2. Ligne 85** | Catégorie: `contract_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/auth/pages/LoginPage.tsx`

**1. Ligne 52** | Catégorie: `contract_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/auth/pages/MfaVerificationPage.tsx`

**1. Ligne 45** | Catégorie: `contract_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/auth/pages/RegisterPage.tsx`

**1. Ligne 9** | Catégorie: `contract_types`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**2. Ligne 147** | Catégorie: `contract_types`

```
if (formData.role === 'interim' && !formData.isCollaborator) {
```

**Valeur en dur**: `'interim'`

**3. Ligne 269** | Catégorie: `contract_types`

```
onClick={() => handleRoleSelect('interim')}
```

**Valeur en dur**: `'interim'`

**4. Ligne 271** | Catégorie: `contract_types`

```
formData.role === 'interim'
```

**Valeur en dur**: `'interim'`

**5. Ligne 276** | Catégorie: `contract_types`

```
{formData.role === 'interim' && (
```

**Valeur en dur**: `'interim'`

**6. Ligne 518** | Catégorie: `contract_types`

```
{formData.role === 'interim' && (
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/auth/pages/RoleSelectionPage.tsx`

**1. Ligne 8** | Catégorie: `contract_types`

```
type UserRole = 'interim' | 'company'
```

**Valeur en dur**: `'interim'`

**2. Ligne 71** | Catégorie: `contract_types`

```
const dashboardPath = selectedRole === 'interim' ? '/interimaire' :
```

**Valeur en dur**: `'interim'`

**3. Ligne 107** | Catégorie: `contract_types`

```
onClick={() => handleRoleSelect('interim')}
```

**Valeur en dur**: `'interim'`

**4. Ligne 110** | Catégorie: `contract_types`

```
selectedRole === 'interim'
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/missions/pages/CreateMissionPage.tsx`

**1. Ligne 24** | Catégorie: `contract_types`

```
contract_type: 'cdd',
```

**Valeur en dur**: `'cdd'`


### 📄 `apps/web/src/features/profile/api/profileApi.ts`

**1. Ligne 48** | Catégorie: `contract_types`

```
profile_type: 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/profile/components/DocumentsSection.tsx`

**1. Ligne 11** | Catégorie: `document_types`

```
const [selectedDocType, setSelectedDocType] = useState('cv')
```

**Valeur en dur**: `'cv'`

**2. Ligne 92** | Catégorie: `document_types`

```
<option value="cv">CV</option>
```

**Valeur en dur**: `"cv"`


### 📄 `apps/web/src/features/profile/pages/ProfilePage.tsx`

**1. Ligne 89** | Catégorie: `contract_types`

```
{profileType === 'interim' && <InterimProfileForm profile={profile} />}
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/pages/LandingPage.tsx`

**1. Ligne 26** | Catégorie: `contract_types`

```
if (user.roles.includes('interim')) return '/interimaire'
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/types/index.ts`

**1. Ligne 14** | Catégorie: `contract_types`

```
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'
```

**Valeur en dur**: `'interim'`

**2. Ligne 58** | Catégorie: `contract_types`

```
export type ValidationType = 'company' | 'interim'
```

**Valeur en dur**: `'interim'`


### 📄 `auth-microservice/awana_auth/core/config.py`

**1. Ligne 34** | Catégorie: `delays_days`

```
jwt_access_token_expire_minutes: int = Field(default=30)
```

**Valeur en dur**: `expire_minutes: int = Field(default=30`

**2. Ligne 35** | Catégorie: `delays_days`

```
jwt_refresh_token_expire_days: int = Field(default=7)
```

**Valeur en dur**: `expire_days: int = Field(default=7`


### 📄 `auth-microservice/awana_auth/core/mission_models.py`

**1. Ligne 289** | Catégorie: `document_types`

```
CV = "cv"
```

**Valeur en dur**: `"cv"`

**2. Ligne 291** | Catégorie: `document_types`

```
MEDICAL_CERTIFICATE = "medical_certificate"
```

**Valeur en dur**: `"medical_certificate"`

**3. Ligne 292** | Catégorie: `document_types`

```
CONTRACT = "contract"
```

**Valeur en dur**: `"contract"`


### 📄 `auth-microservice/awana_auth/core/models.py`

**1. Ligne 236** | Catégorie: `delays_days`

```
expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=5))
```

**Valeur en dur**: `expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=5`


### 📄 `auth-microservice/awana_auth/core/profile_models.py`

**1. Ligne 36** | Catégorie: `contract_types`

```
CDD = "cdd"
```

**Valeur en dur**: `"cdd"`

**2. Ligne 37** | Catégorie: `contract_types`

```
CDI = "cdi"
```

**Valeur en dur**: `"cdi"`

**3. Ligne 38** | Catégorie: `contract_types`

```
FREELANCE = "freelance"
```

**Valeur en dur**: `"freelance"`

**4. Ligne 43** | Catégorie: `document_types`

```
CV = "cv"
```

**Valeur en dur**: `"cv"`


### 📄 `auth-microservice/awana_auth/core/reference_models.py`

**1. Ligne 44** | Catégorie: `contract_types`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/awana_auth/mfa/mfa_service.py`

**1. Ligne 165** | Catégorie: `delays_days`

```
'expires_at': datetime.now(timezone.utc).timestamp() + 600
```

**Valeur en dur**: `expires_at': datetime.now(timezone.utc).timestamp() + 600`


### 📄 `auth-microservice/awana_auth/providers/google.py`

**1. Ligne 108** | Catégorie: `delays_days`

```
"expires_in": tokens.get("expires_in", 3600)
```

**Valeur en dur**: `expires_in": tokens.get("expires_in", 3600`


### 📄 `auth-microservice/awana_auth/session/storage.py`

**1. Ligne 27** | Catégorie: `delays_days`

```
session_doc['expires_at'] = datetime.fromisoformat(session_doc['expires_at'].replace('Z', '+00:00'))
```

**Valeur en dur**: `expires_at'] = datetime.fromisoformat(session_doc['expires_at'].replace('Z', '+00:00`


### 📄 `auth-microservice/awana_auth_routes.py`

**1. Ligne 313** | Catégorie: `contract_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**2. Ligne 539** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**3. Ligne 745** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**4. Ligne 1014** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**5. Ligne 1122** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**6. Ligne 1156** | Catégorie: `contract_types`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**7. Ligne 1159** | Catégorie: `contract_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**8. Ligne 1323** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**9. Ligne 1435** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**10. Ligne 1476** | Catégorie: `contract_types`

```
interim_users = await db.users.count_documents({"roles": "interim"})
```

**Valeur en dur**: `"interim"`

**11. Ligne 1488** | Catégorie: `delays_days`

```
seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
```

**Valeur en dur**: `days=7`

**12. Ligne 1492** | Catégorie: `delays_days`

```
one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
```

**Valeur en dur**: `days=1`

**13. Ligne 1511** | Catégorie: `contract_types`

```
"interim": interim_users,
```

**Valeur en dur**: `"interim"`

**14. Ligne 2068** | Catégorie: `contract_types`

```
valid_roles = ["admin", "super_admin", "interim", "company", "agency", "commercial", "validator"]
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 92** | Catégorie: `delays_days`

```
"expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
```

**Valeur en dur**: `expires_at": datetime.now(timezone.utc) + timedelta(minutes=10`

**2. Ligne 96** | Catégorie: `delays_days`

```
await db.oauth_states.create_index("expires_at", expireAfterSeconds=0)
```

**Valeur en dur**: `expires_at", expireAfterSeconds=0`

**3. Ligne 154** | Catégorie: `contract_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**4. Ligne 315** | Catégorie: `contract_types`

```
profile_type=roles[0] if roles else "interim",
```

**Valeur en dur**: `"interim"`

**5. Ligne 343** | Catégorie: `contract_types`

```
await rbac_manager.grant_role(user_id, "interim", granted_by="system")
```

**Valeur en dur**: `"interim"`

**6. Ligne 347** | Catégorie: `contract_types`

```
roles = ["interim"]
```

**Valeur en dur**: `"interim"`

**7. Ligne 357** | Catégorie: `contract_types`

```
profile_type=roles[0] if roles else "interim",
```

**Valeur en dur**: `"interim"`

**8. Ligne 538** | Catégorie: `contract_types`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**9. Ligne 541** | Catégorie: `contract_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**10. Ligne 569** | Catégorie: `contract_types`

```
await rbac_manager.revoke_role(user_id, "interim")
```

**Valeur en dur**: `"interim"`

**11. Ligne 645** | Catégorie: `delays_days`

```
"expires_in": 1800,
```

**Valeur en dur**: `expires_in": 1800`


### 📄 `auth-microservice/mission_routes.py`

**1. Ligne 216** | Catégorie: `contract_types`

```
if "interim" in user_roles:
```

**Valeur en dur**: `"interim"`

**2. Ligne 257** | Catégorie: `contract_types`

```
if "interim" in user_roles and mission["status"] != MissionStatus.PUBLISHED:
```

**Valeur en dur**: `"interim"`

**3. Ligne 428** | Catégorie: `contract_types`

```
if "interim" not in user_roles:
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/profile_routes.py`

**1. Ligne 39** | Catégorie: `contract_types`

```
if profile_type == "interim":
```

**Valeur en dur**: `"interim"`

**2. Ligne 76** | Catégorie: `contract_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**3. Ligne 97** | Catégorie: `contract_types`

```
return {"profile_type": "interim", "profile": profile}
```

**Valeur en dur**: `"interim"`

**4. Ligne 135** | Catégorie: `contract_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**5. Ligne 137** | Catégorie: `contract_types`

```
profile_type = "interim"
```

**Valeur en dur**: `"interim"`

**6. Ligne 216** | Catégorie: `contract_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**7. Ligne 223** | Catégorie: `document_types`

```
if document_type == "cv":
```

**Valeur en dur**: `"cv"`

**8. Ligne 284** | Catégorie: `contract_types`

```
if "interim" in current_user.roles:
```

**Valeur en dur**: `"interim"`

**9. Ligne 291** | Catégorie: `document_types`

```
if document["type"] == "cv":
```

**Valeur en dur**: `"cv"`


### 📄 `auth-microservice/scripts/seed_additional_references.py`

**1. Ligne 122** | Catégorie: `contract_types`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`

**2. Ligne 344** | Catégorie: `document_types`

```
"code": "cv",
```

**Valeur en dur**: `"cv"`

**3. Ligne 384** | Catégorie: `document_types`

```
"code": "medical_certificate",
```

**Valeur en dur**: `"medical_certificate"`

**4. Ligne 404** | Catégorie: `document_types`

```
"code": "contract",
```

**Valeur en dur**: `"contract"`


### 📄 `auth-microservice/scripts/seed_mission_references.py`

**1. Ligne 336** | Catégorie: `contract_types`

```
"code": "cdi",
```

**Valeur en dur**: `"cdi"`

**2. Ligne 353** | Catégorie: `contract_types`

```
"code": "cdd",
```

**Valeur en dur**: `"cdd"`

**3. Ligne 370** | Catégorie: `contract_types`

```
"code": "interim",
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/validation_routes.py`

**1. Ligne 77** | Catégorie: `contract_types`

```
pending_interim = await db.validations.count_documents({"status": "pending", "validation_type": "interim"})
```

**Valeur en dur**: `"interim"`


## 🟢 Sévérité: LOW

**Total**: 185 occurrences

### 📄 `auth-microservice/awana_auth/core/config.py`

**1. Ligne 20** | Catégorie: `messages`

```
app_name: str = Field(default="AWANA GROUP", description="Application name")
```

**Valeur en dur**: `description="Application name"`

**2. Ligne 21** | Catégorie: `messages`

```
environment: str = Field(default="development", description="Environment (development/staging/production)")
```

**Valeur en dur**: `description="Environment (development/staging/production)"`

**3. Ligne 38** | Catégorie: `messages`

```
session_storage: str = Field(default="mongodb", description="Session storage backend (mongodb/redis)")
```

**Valeur en dur**: `description="Session storage backend (mongodb/redis)"`

**4. Ligne 42** | Catégorie: `numeric_limits`

```
password_min_length: int = Field(default=12)
```

**Valeur en dur**: `min_length: int = Field(default=12`

**5. Ligne 60** | Catégorie: `messages`

```
description="List of enabled auth providers (entraid, webauthn, totp, local)"
```

**Valeur en dur**: `description="List of enabled auth providers (entraid, webauthn, totp, local)"`


### 📄 `auth-microservice/awana_auth/core/dependencies.py`

**1. Ligne 42** | Catégorie: `numeric_limits`

```
minPoolSize=config.get("database.min_pool_size", default=5)
```

**Valeur en dur**: `min_pool_size", default=5`

**2. Ligne 107** | Catégorie: `messages`

```
detail="Not authenticated",
```

**Valeur en dur**: `detail="Not authenticated"`

**3. Ligne 123** | Catégorie: `messages`

```
detail="Session not found or expired",
```

**Valeur en dur**: `detail="Session not found or expired"`

**4. Ligne 133** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**5. Ligne 157** | Catégorie: `messages`

```
detail="Authentication failed",
```

**Valeur en dur**: `detail="Authentication failed"`

**6. Ligne 198** | Catégorie: `messages`

```
detail="Admin privileges required"
```

**Valeur en dur**: `detail="Admin privileges required"`

**7. Ligne 220** | Catégorie: `messages`

```
detail="Super admin privileges required"
```

**Valeur en dur**: `detail="Super admin privileges required"`


### 📄 `auth-microservice/awana_auth/core/mission_models.py`

**1. Ligne 105** | Catégorie: `numeric_limits`

```
title: str = Field(..., min_length=3, max_length=200)
```

**Valeur en dur**: `max_length=200`

**2. Ligne 105** | Catégorie: `numeric_limits`

```
title: str = Field(..., min_length=3, max_length=200)
```

**Valeur en dur**: `min_length=3, max_length=200`


### 📄 `auth-microservice/awana_auth/core/models.py`

**1. Ligne 247** | Catégorie: `numeric_limits`

```
code: str = Field(min_length=6, max_length=6)
```

**Valeur en dur**: `max_length=6`

**2. Ligne 247** | Catégorie: `numeric_limits`

```
code: str = Field(min_length=6, max_length=6)
```

**Valeur en dur**: `min_length=6, max_length=6`

**3. Ligne 257** | Catégorie: `numeric_limits`

```
phone_number: str = Field(min_length=10, max_length=20)
```

**Valeur en dur**: `max_length=20`

**4. Ligne 257** | Catégorie: `numeric_limits`

```
phone_number: str = Field(min_length=10, max_length=20)
```

**Valeur en dur**: `min_length=10, max_length=20`

**5. Ligne 262** | Catégorie: `numeric_limits`

```
code: str = Field(min_length=6, max_length=6)
```

**Valeur en dur**: `max_length=6`

**6. Ligne 262** | Catégorie: `numeric_limits`

```
code: str = Field(min_length=6, max_length=6)
```

**Valeur en dur**: `min_length=6, max_length=6`

**7. Ligne 269** | Catégorie: `numeric_limits`

```
code: str = Field(min_length=6, max_length=6)
```

**Valeur en dur**: `max_length=6`

**8. Ligne 269** | Catégorie: `numeric_limits`

```
code: str = Field(min_length=6, max_length=6)
```

**Valeur en dur**: `min_length=6, max_length=6`


### 📄 `auth-microservice/awana_auth/rbac/decorators.py`

**1. Ligne 30** | Catégorie: `messages`

```
detail="Authentication required"
```

**Valeur en dur**: `detail="Authentication required"`

**2. Ligne 73** | Catégorie: `messages`

```
detail="Authentication required"
```

**Valeur en dur**: `detail="Authentication required"`

**3. Ligne 79** | Catégorie: `messages`

```
detail="RBAC manager not available"
```

**Valeur en dur**: `detail="RBAC manager not available"`


### 📄 `auth-microservice/awana_auth/rbac/models.py`

**1. Ligne 86** | Catégorie: `messages`

```
description="Full system access with all permissions",
```

**Valeur en dur**: `description="Full system access with all permissions"`

**2. Ligne 94** | Catégorie: `messages`

```
description="Administrative access to manage users and content",
```

**Valeur en dur**: `description="Administrative access to manage users and content"`

**3. Ligne 108** | Catégorie: `messages`

```
description="Can create and edit content",
```

**Valeur en dur**: `description="Can create and edit content"`

**4. Ligne 119** | Catégorie: `messages`

```
description="Read-only access to content",
```

**Valeur en dur**: `description="Read-only access to content"`

**5. Ligne 132** | Catégorie: `messages`

```
Permission(name="users:read", resource="users", action="read", description="View users"),
```

**Valeur en dur**: `description="View users"`

**6. Ligne 133** | Catégorie: `messages`

```
Permission(name="users:write", resource="users", action="write", description="Create/edit users"),
```

**Valeur en dur**: `description="Create/edit users"`

**7. Ligne 134** | Catégorie: `messages`

```
Permission(name="users:delete", resource="users", action="delete", description="Delete users"),
```

**Valeur en dur**: `description="Delete users"`

**8. Ligne 137** | Catégorie: `messages`

```
Permission(name="roles:read", resource="roles", action="read", description="View roles"),
```

**Valeur en dur**: `description="View roles"`

**9. Ligne 138** | Catégorie: `messages`

```
Permission(name="roles:write", resource="roles", action="write", description="Create/edit roles"),
```

**Valeur en dur**: `description="Create/edit roles"`

**10. Ligne 139** | Catégorie: `messages`

```
Permission(name="roles:delete", resource="roles", action="delete", description="Delete roles"),
```

**Valeur en dur**: `description="Delete roles"`

**11. Ligne 142** | Catégorie: `messages`

```
Permission(name="content:read", resource="content", action="read", description="View content"),
```

**Valeur en dur**: `description="View content"`

**12. Ligne 143** | Catégorie: `messages`

```
Permission(name="content:write", resource="content", action="write", description="Create/edit content"),
```

**Valeur en dur**: `description="Create/edit content"`

**13. Ligne 144** | Catégorie: `messages`

```
Permission(name="content:delete", resource="content", action="delete", description="Delete content"),
```

**Valeur en dur**: `description="Delete content"`

**14. Ligne 147** | Catégorie: `messages`

```
Permission(name="analytics:read", resource="analytics", action="read", description="View analytics"),
```

**Valeur en dur**: `description="View analytics"`

**15. Ligne 150** | Catégorie: `messages`

```
Permission(name="audit:read", resource="audit", action="read", description="View audit logs"),
```

**Valeur en dur**: `description="View audit logs"`

**16. Ligne 153** | Catégorie: `messages`

```
Permission(name="*:*", resource="*", action="*", description="All permissions"),
```

**Valeur en dur**: `description="All permissions"`


### 📄 `auth-microservice/awana_auth_routes.py`

**1. Ligne 578** | Catégorie: `messages`

```
detail="ID token is required"
```

**Valeur en dur**: `detail="ID token is required"`

**2. Ligne 619** | Catégorie: `messages`

```
detail="Invalid Microsoft token"
```

**Valeur en dur**: `detail="Invalid Microsoft token"`

**3. Ligne 630** | Catégorie: `messages`

```
detail="Missing required user information from Microsoft"
```

**Valeur en dur**: `detail="Missing required user information from Microsoft"`

**4. Ligne 830** | Catégorie: `messages`

```
detail="Account is not active"
```

**Valeur en dur**: `detail="Account is not active"`

**5. Ligne 863** | Catégorie: `messages`

```
detail="Incorrect username or password"
```

**Valeur en dur**: `detail="Incorrect username or password"`

**6. Ligne 1055** | Catégorie: `messages`

```
detail="Session MFA invalide ou expirée"
```

**Valeur en dur**: `detail="Session MFA invalide ou expirée"`

**7. Ligne 1061** | Catégorie: `messages`

```
detail="MFA n'a pas été vérifiée"
```

**Valeur en dur**: `detail="MFA n'a pas été vérifiée"`

**8. Ligne 1069** | Catégorie: `messages`

```
detail="Utilisateur non trouvé"
```

**Valeur en dur**: `detail="Utilisateur non trouvé"`

**9. Ligne 1159** | Catégorie: `messages`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `detail="Invalid role. Must be 'interim' or 'company'"`

**10. Ligne 1170** | Catégorie: `messages`

```
detail="Ce nom d'utilisateur est déjà utilisé"
```

**Valeur en dur**: `detail="Ce nom d'utilisateur est déjà utilisé"`

**11. Ligne 1181** | Catégorie: `messages`

```
detail="Cet email est déjà utilisé"
```

**Valeur en dur**: `detail="Cet email est déjà utilisé"`

**12. Ligne 1373** | Catégorie: `messages`

```
detail="Logout failed"
```

**Valeur en dur**: `detail="Logout failed"`

**13. Ligne 1398** | Catégorie: `messages`

```
detail="Session not found or expired"
```

**Valeur en dur**: `detail="Session not found or expired"`

**14. Ligne 1407** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**15. Ligne 1445** | Catégorie: `messages`

```
detail="Token refresh failed"
```

**Valeur en dur**: `detail="Token refresh failed"`

**16. Ligne 1530** | Catégorie: `messages`

```
detail="Error retrieving statistics"
```

**Valeur en dur**: `detail="Error retrieving statistics"`

**17. Ligne 1570** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**18. Ligne 1592** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**19. Ligne 1657** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**20. Ligne 1666** | Catégorie: `messages`

```
detail="Cannot delete your own account"
```

**Valeur en dur**: `detail="Cannot delete your own account"`

**21. Ligne 1712** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**22. Ligne 1721** | Catégorie: `messages`

```
detail="Cannot reset your own MFA through admin endpoint. Use the profile settings."
```

**Valeur en dur**: `detail="Cannot reset your own MFA through admin endpoint. Use the profile settings."`

**23. Ligne 1728** | Catégorie: `messages`

```
detail="User does not have MFA enabled"
```

**Valeur en dur**: `detail="User does not have MFA enabled"`

**24. Ligne 1803** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**25. Ligne 1856** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**26. Ligne 1948** | Catégorie: `messages`

```
detail="Erreur lors de la récupération des utilisateurs"
```

**Valeur en dur**: `detail="Erreur lors de la récupération des utilisateurs"`

**27. Ligne 1970** | Catégorie: `messages`

```
detail="Status invalide. Valeurs autorisées: active, pending, suspended, deleted"
```

**Valeur en dur**: `detail="Status invalide. Valeurs autorisées: active, pending, suspended, deleted"`

**28. Ligne 1979** | Catégorie: `messages`

```
detail="Utilisateur non trouvé"
```

**Valeur en dur**: `detail="Utilisateur non trouvé"`

**29. Ligne 2019** | Catégorie: `messages`

```
detail="Erreur lors de la mise à jour du statut"
```

**Valeur en dur**: `detail="Erreur lors de la mise à jour du statut"`

**30. Ligne 2042** | Catégorie: `messages`

```
detail="Utilisateur non trouvé"
```

**Valeur en dur**: `detail="Utilisateur non trouvé"`

**31. Ligne 2062** | Catégorie: `messages`

```
detail="Cet email est déjà utilisé par un autre utilisateur"
```

**Valeur en dur**: `detail="Cet email est déjà utilisé par un autre utilisateur"`

**32. Ligne 2073** | Catégorie: `messages`

```
detail="Les rôles doivent être une liste"
```

**Valeur en dur**: `detail="Les rôles doivent être une liste"`

**33. Ligne 2086** | Catégorie: `messages`

```
detail="Aucune donnée à mettre à jour"
```

**Valeur en dur**: `detail="Aucune donnée à mettre à jour"`

**34. Ligne 2123** | Catégorie: `messages`

```
detail="Erreur lors de la mise à jour de l'utilisateur"
```

**Valeur en dur**: `detail="Erreur lors de la mise à jour de l'utilisateur"`

**35. Ligne 2209** | Catégorie: `messages`

```
detail="Erreur lors de l'envoi de l'email"
```

**Valeur en dur**: `detail="Erreur lors de l'envoi de l'email"`

**36. Ligne 2238** | Catégorie: `messages`

```
detail="Token invalide ou déjà utilisé"
```

**Valeur en dur**: `detail="Token invalide ou déjà utilisé"`

**37. Ligne 2255** | Catégorie: `messages`

```
detail="Le token a expiré. Veuillez demander un nouveau lien"
```

**Valeur en dur**: `detail="Le token a expiré. Veuillez demander un nouveau lien"`

**38. Ligne 2262** | Catégorie: `messages`

```
detail="Le mot de passe doit contenir au moins 8 caractères"
```

**Valeur en dur**: `detail="Le mot de passe doit contenir au moins 8 caractères"`

**39. Ligne 2320** | Catégorie: `messages`

```
detail="Erreur lors de la réinitialisation du mot de passe"
```

**Valeur en dur**: `detail="Erreur lors de la réinitialisation du mot de passe"`


### 📄 `auth-microservice/configuration_routes.py`

**1. Ligne 115** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Référentiel non trouvé")
```

**Valeur en dur**: `detail="Référentiel non trouvé"`

**2. Ligne 120** | Catégorie: `messages`

```
detail="Les référentiels système ne peuvent pas être désactivés"
```

**Valeur en dur**: `detail="Les référentiels système ne peuvent pas être désactivés"`

**3. Ligne 156** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Référentiel non trouvé")
```

**Valeur en dur**: `detail="Référentiel non trouvé"`

**4. Ligne 161** | Catégorie: `messages`

```
detail="Les référentiels système ne peuvent pas être supprimés"
```

**Valeur en dur**: `detail="Les référentiels système ne peuvent pas être supprimés"`

**5. Ligne 251** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Paramètre non trouvé")
```

**Valeur en dur**: `detail="Paramètre non trouvé"`


### 📄 `auth-microservice/document_routes.py`

**1. Ligne 54** | Catégorie: `numeric_limits`

```
max_file_size_mb = config.get("storage.uploads.max_file_size_mb", default=10)
```

**Valeur en dur**: `max_file_size_mb = config.get("storage.uploads.max_file_size_mb", default=10`

**2. Ligne 150** | Catégorie: `messages`

```
detail="Document non trouvé"
```

**Valeur en dur**: `detail="Document non trouvé"`

**3. Ligne 161** | Catégorie: `messages`

```
detail="Vous n'avez pas accès à ce document"
```

**Valeur en dur**: `detail="Vous n'avez pas accès à ce document"`

**4. Ligne 168** | Catégorie: `messages`

```
detail="Fichier non trouvé sur le serveur"
```

**Valeur en dur**: `detail="Fichier non trouvé sur le serveur"`

**5. Ligne 214** | Catégorie: `messages`

```
detail="Document non trouvé"
```

**Valeur en dur**: `detail="Document non trouvé"`

**6. Ligne 225** | Catégorie: `messages`

```
detail="Vous ne pouvez supprimer que vos propres documents"
```

**Valeur en dur**: `detail="Vous ne pouvez supprimer que vos propres documents"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 58** | Catégorie: `messages`

```
detail="Google OAuth est désactivé"
```

**Valeur en dur**: `detail="Google OAuth est désactivé"`

**2. Ligne 68** | Catégorie: `messages`

```
detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
```

**Valeur en dur**: `detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"`

**3. Ligne 243** | Catégorie: `messages`

```
detail="Failed to initiate Google login"
```

**Valeur en dur**: `detail="Failed to initiate Google login"`

**4. Ligne 268** | Catégorie: `messages`

```
detail="Invalid or expired state parameter"
```

**Valeur en dur**: `detail="Invalid or expired state parameter"`

**5. Ligne 372** | Catégorie: `messages`

```
detail="User not found after creation"
```

**Valeur en dur**: `detail="User not found after creation"`

**6. Ligne 521** | Catégorie: `messages`

```
detail="Missing or invalid authorization header"
```

**Valeur en dur**: `detail="Missing or invalid authorization header"`

**7. Ligne 534** | Catégorie: `messages`

```
detail="Invalid or expired token"
```

**Valeur en dur**: `detail="Invalid or expired token"`

**8. Ligne 541** | Catégorie: `messages`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `detail="Invalid role. Must be 'interim' or 'company'"`

**9. Ligne 551** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`


### 📄 `auth-microservice/location_routes.py`

**1. Ligne 80** | Catégorie: `messages`

```
detail="Location not found"
```

**Valeur en dur**: `detail="Location not found"`

**2. Ligne 98** | Catégorie: `messages`

```
detail="Parent location not found"
```

**Valeur en dur**: `detail="Parent location not found"`

**3. Ligne 143** | Catégorie: `messages`

```
detail="Location not found"
```

**Valeur en dur**: `detail="Location not found"`

**4. Ligne 182** | Catégorie: `messages`

```
detail="Location not found"
```

**Valeur en dur**: `detail="Location not found"`

**5. Ligne 207** | Catégorie: `messages`

```
detail="Location not found"
```

**Valeur en dur**: `detail="Location not found"`


### 📄 `auth-microservice/main.py`

**1. Ligne 54** | Catégorie: `numeric_limits`

```
minPoolSize=config.get('database.min_pool_size', default=5),
```

**Valeur en dur**: `min_pool_size', default=5`

**2. Ligne 75** | Catégorie: `messages`

```
description="Standalone Auth with JWT, OAuth2, RBAC",
```

**Valeur en dur**: `description="Standalone Auth with JWT, OAuth2, RBAC"`


### 📄 `auth-microservice/mfa_routes.py`

**1. Ligne 120** | Catégorie: `messages`

```
detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
```

**Valeur en dur**: `detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."`

**2. Ligne 153** | Catégorie: `messages`

```
message="Scannez le QR code avec votre application d'authentification"
```

**Valeur en dur**: `message="Scannez le QR code avec votre application d'authentification"`

**3. Ligne 176** | Catégorie: `messages`

```
detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
```

**Valeur en dur**: `detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."`

**4. Ligne 185** | Catégorie: `messages`

```
detail="Aucune configuration TOTP en attente"
```

**Valeur en dur**: `detail="Aucune configuration TOTP en attente"`

**5. Ligne 193** | Catégorie: `messages`

```
detail="Configuration expirée. Veuillez recommencer."
```

**Valeur en dur**: `detail="Configuration expirée. Veuillez recommencer."`

**6. Ligne 203** | Catégorie: `messages`

```
detail="Code invalide"
```

**Valeur en dur**: `detail="Code invalide"`

**7. Ligne 238** | Catégorie: `messages`

```
message="TOTP activé avec succès. Conservez vos codes de secours en lieu sûr."
```

**Valeur en dur**: `message="TOTP activé avec succès. Conservez vos codes de secours en lieu sûr."`

**8. Ligne 260** | Catégorie: `messages`

```
detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
```

**Valeur en dur**: `detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."`

**9. Ligne 306** | Catégorie: `messages`

```
detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
```

**Valeur en dur**: `detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."`

**10. Ligne 357** | Catégorie: `messages`

```
detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."
```

**Valeur en dur**: `detail="Trop de tentatives. Veuillez réessayer dans 15 minutes."`

**11. Ligne 366** | Catégorie: `messages`

```
detail="Code invalide ou expiré"
```

**Valeur en dur**: `detail="Code invalide ou expiré"`

**12. Ligne 376** | Catégorie: `messages`

```
detail="Numéro de téléphone non trouvé"
```

**Valeur en dur**: `detail="Numéro de téléphone non trouvé"`

**13. Ligne 395** | Catégorie: `messages`

```
message="SMS OTP activé avec succès"
```

**Valeur en dur**: `message="SMS OTP activé avec succès"`

**14. Ligne 418** | Catégorie: `messages`

```
detail="MFA n'est pas activé"
```

**Valeur en dur**: `detail="MFA n'est pas activé"`

**15. Ligne 439** | Catégorie: `messages`

```
message="Nouveaux codes de secours générés. Les anciens codes sont maintenant invalides."
```

**Valeur en dur**: `message="Nouveaux codes de secours générés. Les anciens codes sont maintenant invalides."`

**16. Ligne 460** | Catégorie: `messages`

```
detail="Méthode invalide"
```

**Valeur en dur**: `detail="Méthode invalide"`

**17. Ligne 493** | Catégorie: `messages`

```
detail="Session MFA invalide ou expirée"
```

**Valeur en dur**: `detail="Session MFA invalide ou expirée"`

**18. Ligne 502** | Catégorie: `messages`

```
detail="Trop de tentatives. Compte temporairement verrouillé."
```

**Valeur en dur**: `detail="Trop de tentatives. Compte temporairement verrouillé."`

**19. Ligne 538** | Catégorie: `messages`

```
detail="Code invalide"
```

**Valeur en dur**: `detail="Code invalide"`


### 📄 `auth-microservice/mission_routes.py`

**1. Ligne 77** | Catégorie: `numeric_limits`

```
max_applications = config.get("workflows.application.restrictions.max_applications_per_candidate", default=10)
```

**Valeur en dur**: `max_applications = config.get("workflows.application.restrictions.max_applications_per_candidate", default=10`

**2. Ligne 87** | Catégorie: `numeric_limits`

```
min_days_between = config.get("workflows.application.restrictions.min_days_between_applications", default=1)
```

**Valeur en dur**: `min_days_between = config.get("workflows.application.restrictions.min_days_between_applications", default=1`

**3. Ligne 126** | Catégorie: `messages`

```
detail="Vous avez déjà candidaté à cette mission"
```

**Valeur en dur**: `detail="Vous avez déjà candidaté à cette mission"`

**4. Ligne 162** | Catégorie: `messages`

```
detail="Vous n'avez pas la permission de créer une mission"
```

**Valeur en dur**: `detail="Vous n'avez pas la permission de créer une mission"`

**5. Ligne 250** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**6. Ligne 260** | Catégorie: `messages`

```
detail="Mission non accessible"
```

**Valeur en dur**: `detail="Mission non accessible"`

**7. Ligne 266** | Catégorie: `messages`

```
detail="Vous ne pouvez voir que vos missions"
```

**Valeur en dur**: `detail="Vous ne pouvez voir que vos missions"`

**8. Ligne 288** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**9. Ligne 305** | Catégorie: `messages`

```
detail="Vous n'avez pas la permission de modifier cette mission"
```

**Valeur en dur**: `detail="Vous n'avez pas la permission de modifier cette mission"`

**10. Ligne 343** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**11. Ligne 359** | Catégorie: `messages`

```
detail="Vous n'avez pas la permission de supprimer cette mission"
```

**Valeur en dur**: `detail="Vous n'avez pas la permission de supprimer cette mission"`

**12. Ligne 384** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**13. Ligne 394** | Catégorie: `messages`

```
detail="Seuls les commerciaux et admins peuvent publier"
```

**Valeur en dur**: `detail="Seuls les commerciaux et admins peuvent publier"`

**14. Ligne 431** | Catégorie: `messages`

```
detail="Seuls les intérimaires peuvent postuler"
```

**Valeur en dur**: `detail="Seuls les intérimaires peuvent postuler"`

**15. Ligne 439** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**16. Ligne 445** | Catégorie: `messages`

```
detail="Cette mission n'accepte plus de candidatures"
```

**Valeur en dur**: `detail="Cette mission n'accepte plus de candidatures"`

**17. Ligne 457** | Catégorie: `messages`

```
detail="Vous avez déjà postulé à cette mission"
```

**Valeur en dur**: `detail="Vous avez déjà postulé à cette mission"`

**18. Ligne 501** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**19. Ligne 518** | Catégorie: `messages`

```
detail="Vous n'avez pas accès aux candidatures"
```

**Valeur en dur**: `detail="Vous n'avez pas accès aux candidatures"`

**20. Ligne 562** | Catégorie: `messages`

```
detail="Candidature non trouvée"
```

**Valeur en dur**: `detail="Candidature non trouvée"`

**21. Ligne 572** | Catégorie: `messages`

```
detail="Permission insuffisante"
```

**Valeur en dur**: `detail="Permission insuffisante"`

**22. Ligne 632** | Catégorie: `messages`

```
detail="Candidature non trouvée"
```

**Valeur en dur**: `detail="Candidature non trouvée"`

**23. Ligne 673** | Catégorie: `messages`

```
detail="Candidature non trouvée"
```

**Valeur en dur**: `detail="Candidature non trouvée"`

**24. Ligne 680** | Catégorie: `messages`

```
detail="Vous ne pouvez modifier que vos propres candidatures"
```

**Valeur en dur**: `detail="Vous ne pouvez modifier que vos propres candidatures"`

**25. Ligne 715** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`


### 📄 `auth-microservice/profile_routes.py`

**1. Ligne 184** | Catégorie: `messages`

```
raise HTTPException(status_code=400, detail="File too large. Maximum size: 5MB")
```

**Valeur en dur**: `detail="File too large. Maximum size: 5MB"`

**2. Ligne 239** | Catégorie: `messages`

```
message="Document uploadé avec succès"
```

**Valeur en dur**: `message="Document uploadé avec succès"`

**3. Ligne 271** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Document not found")
```

**Valeur en dur**: `detail="Document not found"`


### 📄 `auth-microservice/scripts/encrypt_env.py`

**1. Ligne 106** | Catégorie: `messages`

```
description="Chiffrer/déchiffrer les fichiers .env",
```

**Valeur en dur**: `description="Chiffrer/déchiffrer les fichiers .env"`


### 📄 `auth-microservice/security_routes.py`

**1. Ligne 60** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Profile not found")
```

**Valeur en dur**: `detail="Profile not found"`

**2. Ligne 74** | Catégorie: `messages`

```
raise HTTPException(status_code=400, detail="Profile name already exists")
```

**Valeur en dur**: `detail="Profile name already exists"`

**3. Ligne 98** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Profile not found")
```

**Valeur en dur**: `detail="Profile not found"`

**4. Ligne 102** | Catégorie: `messages`

```
raise HTTPException(status_code=403, detail="Cannot modify system profiles")
```

**Valeur en dur**: `detail="Cannot modify system profiles"`

**5. Ligne 125** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Profile not found")
```

**Valeur en dur**: `detail="Profile not found"`

**6. Ligne 129** | Catégorie: `messages`

```
raise HTTPException(status_code=403, detail="Cannot delete system profiles")
```

**Valeur en dur**: `detail="Cannot delete system profiles"`

**7. Ligne 164** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Group not found")
```

**Valeur en dur**: `detail="Group not found"`

**8. Ligne 178** | Catégorie: `messages`

```
raise HTTPException(status_code=400, detail="Group name already exists")
```

**Valeur en dur**: `detail="Group name already exists"`

**9. Ligne 184** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Profile not found")
```

**Valeur en dur**: `detail="Profile not found"`

**10. Ligne 208** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Group not found")
```

**Valeur en dur**: `detail="Group not found"`

**11. Ligne 214** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Profile not found")
```

**Valeur en dur**: `detail="Profile not found"`

**12. Ligne 238** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Group not found")
```

**Valeur en dur**: `detail="Group not found"`

**13. Ligne 254** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Group not found")
```

**Valeur en dur**: `detail="Group not found"`

**14. Ligne 259** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="User not found")
```

**Valeur en dur**: `detail="User not found"`

**15. Ligne 281** | Catégorie: `messages`

```
raise HTTPException(status_code=404, detail="Group not found")
```

**Valeur en dur**: `detail="Group not found"`

**16. Ligne 311** | Catégorie: `messages`

```
raise HTTPException(status_code=400, detail="Email already registered")
```

**Valeur en dur**: `detail="Email already registered"`


### 📄 `auth-microservice/validation_routes.py`

**1. Ligne 36** | Catégorie: `messages`

```
validation_type: Optional[str] = Query(None, description="Filter by type: interim or company"),
```

**Valeur en dur**: `description="Filter by type: interim or company"`

**2. Ligne 37** | Catégorie: `messages`

```
status: Optional[ValidationStatus] = Query(None, description="Filter by status"),
```

**Valeur en dur**: `description="Filter by status"`

**3. Ligne 38** | Catégorie: `messages`

```
has_location_warning: Optional[bool] = Query(None, description="Filter by location warning"),
```

**Valeur en dur**: `description="Filter by location warning"`

**4. Ligne 39** | Catégorie: `messages`

```
assigned_to: Optional[str] = Query(None, description="Filter by assigned validator"),
```

**Valeur en dur**: `description="Filter by assigned validator"`

**5. Ligne 128** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**6. Ligne 145** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**7. Ligne 151** | Catégorie: `messages`

```
detail="Validation already processed"
```

**Valeur en dur**: `detail="Validation already processed"`

**8. Ligne 197** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**9. Ligne 203** | Catégorie: `messages`

```
detail="Validation already processed"
```

**Valeur en dur**: `detail="Validation already processed"`

**10. Ligne 251** | Catégorie: `messages`

```
detail="Validator not found"
```

**Valeur en dur**: `detail="Validator not found"`

**11. Ligne 259** | Catégorie: `messages`

```
detail="User does not have validator role (admin, super_admin, or commercial)"
```

**Valeur en dur**: `detail="User does not have validator role (admin, super_admin, or commercial)"`

**12. Ligne 276** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**13. Ligne 296** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**14. Ligne 302** | Catégorie: `messages`

```
detail="No missing country to add"
```

**Valeur en dur**: `detail="No missing country to add"`


---

## 💡 Recommandations

### Priorités de Correction

1. **🔴 CRITIQUE** - À corriger immédiatement
   - Rôles et permissions
   - Statuts de workflow
   - Types de validation

2. **🟠 HAUTE** - À corriger dans les 7 jours
   - Statuts utilisateur
   - Statuts mission

3. **🟡 MOYENNE** - À corriger dans les 14 jours
   - Types de document
   - Types de contrat
   - Délais configurables

4. **🟢 BASSE** - À corriger progressivement
   - Limites numériques
   - Messages et libellés

### Actions Recommandées

1. Ajouter les valeurs dans les fichiers de configuration YAML appropriés
2. Remplacer chaque valeur en dur par `config.get("path.to.value")`
3. Ajouter validation pour les valeurs critiques
4. Tester après chaque remplacement
