# 🔍 Audit des Valeurs en Dur - Rapport Complet

**Date**: 2025-11-05 03:32:21

---

## 📊 Résumé Exécutif

**Total de valeurs en dur trouvées**: 684

### Par Sévérité

| Sévérité | Nombre | Pourcentage |
|----------|--------|-------------|
| 🔴 CRITICAL | 343 | 50.1% |
| 🟠 HIGH | 75 | 11.0% |
| 🟡 MEDIUM | 82 | 12.0% |
| 🟢 LOW | 184 | 26.9% |

### Par Catégorie

| Catégorie | Nombre |
|-----------|--------|
| messages | 168 |
| roles | 164 |
| validation_types | 105 |
| application_status | 74 |
| contract_types | 54 |
| user_status | 49 |
| mission_status | 26 |
| delays_days | 17 |
| numeric_limits | 16 |
| document_types | 11 |

### Top 15 Fichiers

| Fichier | Nombre de valeurs en dur |
|---------|--------------------------|
| `auth-microservice/awana_auth_routes.py` | 77 |
| `apps/web/src/features/admin/pages/ValidationsPage.tsx` | 75 |
| `apps/web/src/hooks/useAppConfig.ts` | 65 |
| `auth-microservice/scripts/seed_mission_references.py` | 32 |
| `auth-microservice/google_auth_routes.py` | 29 |
| `auth-microservice/mission_routes.py` | 26 |
| `apps/web/src/features/auth/pages/RoleSelectionPage.tsx` | 20 |
| `auth-microservice/mfa_routes.py` | 19 |
| `auth-microservice/awana_auth/rbac/models.py` | 18 |
| `auth-microservice/validation_routes.py` | 17 |
| `apps/web/src/types/index.ts` | 17 |
| `auth-microservice/security_routes.py` | 16 |
| `auth-microservice/awana_auth/core/dependencies.py` | 14 |
| `apps/web/src/features/admin/pages/UserManagementPage.tsx` | 14 |
| `auth-microservice/awana_auth/core/models.py` | 13 |

---

## 🔴 Sévérité: CRITICAL

**Total**: 343 occurrences

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

**1. Ligne 110** | Catégorie: `application_status`

```
onClick={() => setStatusFilter('rejected')}
```

**Valeur en dur**: `'rejected'`

**2. Ligne 113** | Catégorie: `application_status`

```
statusFilter === 'rejected'
```

**Valeur en dur**: `'rejected'`

**3. Ligne 178** | Catégorie: `roles`

```
validation.validation_type === 'interim'
```

**Valeur en dur**: `'interim'`

**4. Ligne 178** | Catégorie: `validation_types`

```
validation.validation_type === 'interim'
```

**Valeur en dur**: `'interim'`

**5. Ligne 182** | Catégorie: `roles`

```
{validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
```

**Valeur en dur**: `'interim'`

**6. Ligne 182** | Catégorie: `validation_types`

```
{validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
```

**Valeur en dur**: `'interim'`

**7. Ligne 190** | Catégorie: `application_status`

```
validation.status === 'rejected' && 'bg-red-100 text-red-800'
```

**Valeur en dur**: `'rejected'`

**8. Ligne 194** | Catégorie: `application_status`

```
{validation.status === 'rejected' && 'Refusé'}
```

**Valeur en dur**: `'rejected'`


### 📄 `apps/web/src/features/admin/pages/ValidationsPage.tsx`

**1. Ligne 28** | Catégorie: `roles`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'company'`

**2. Ligne 28** | Catégorie: `roles`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**3. Ligne 28** | Catégorie: `validation_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**4. Ligne 28** | Catégorie: `validation_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'company'`

**5. Ligne 28** | Catégorie: `validation_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**6. Ligne 36** | Catégorie: `roles`

```
interim: validationTypes.find(vt => vt.code === 'interim')?.code || 'interim',
```

**Valeur en dur**: `'interim'`

**7. Ligne 36** | Catégorie: `roles`

```
interim: validationTypes.find(vt => vt.code === 'interim')?.code || 'interim',
```

**Valeur en dur**: `'interim'`

**8. Ligne 36** | Catégorie: `validation_types`

```
interim: validationTypes.find(vt => vt.code === 'interim')?.code || 'interim',
```

**Valeur en dur**: `'interim'`

**9. Ligne 36** | Catégorie: `validation_types`

```
interim: validationTypes.find(vt => vt.code === 'interim')?.code || 'interim',
```

**Valeur en dur**: `'interim'`

**10. Ligne 37** | Catégorie: `roles`

```
company: validationTypes.find(vt => vt.code === 'company')?.code || 'company',
```

**Valeur en dur**: `'company'`

**11. Ligne 37** | Catégorie: `roles`

```
company: validationTypes.find(vt => vt.code === 'company')?.code || 'company',
```

**Valeur en dur**: `'company'`

**12. Ligne 37** | Catégorie: `validation_types`

```
company: validationTypes.find(vt => vt.code === 'company')?.code || 'company',
```

**Valeur en dur**: `'company'`

**13. Ligne 37** | Catégorie: `validation_types`

```
company: validationTypes.find(vt => vt.code === 'company')?.code || 'company',
```

**Valeur en dur**: `'company'`

**14. Ligne 38** | Catégorie: `validation_types`

```
collaborator: validationTypes.find(vt => vt.code === 'collaborator')?.code || 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**15. Ligne 38** | Catégorie: `validation_types`

```
collaborator: validationTypes.find(vt => vt.code === 'collaborator')?.code || 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**16. Ligne 44** | Catégorie: `application_status`

```
rejected: validationStatuses.find(vs => vs.code === 'rejected')?.code || 'rejected'
```

**Valeur en dur**: `'rejected'`

**17. Ligne 44** | Catégorie: `application_status`

```
rejected: validationStatuses.find(vs => vs.code === 'rejected')?.code || 'rejected'
```

**Valeur en dur**: `'rejected'`

**18. Ligne 47** | Catégorie: `roles`

```
const [activeTab, setActiveTab] = useState<TabType>('interim')
```

**Valeur en dur**: `'interim'`

**19. Ligne 47** | Catégorie: `validation_types`

```
const [activeTab, setActiveTab] = useState<TabType>('interim')
```

**Valeur en dur**: `'interim'`

**20. Ligne 53** | Catégorie: `roles`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'company'`

**21. Ligne 53** | Catégorie: `roles`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'interim'`

**22. Ligne 53** | Catégorie: `validation_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'interim'`

**23. Ligne 53** | Catégorie: `validation_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'company'`

**24. Ligne 53** | Catégorie: `validation_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'collaborator'`

**25. Ligne 58** | Catégorie: `roles`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'company'`

**26. Ligne 58** | Catégorie: `roles`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'interim'`

**27. Ligne 58** | Catégorie: `validation_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'interim'`

**28. Ligne 58** | Catégorie: `validation_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'company'`

**29. Ligne 58** | Catégorie: `validation_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'collaborator'`

**30. Ligne 61** | Catégorie: `roles`

```
if (type === 'interim') {
```

**Valeur en dur**: `'interim'`

**31. Ligne 61** | Catégorie: `validation_types`

```
if (type === 'interim') {
```

**Valeur en dur**: `'interim'`

**32. Ligne 63** | Catégorie: `roles`

```
} else if (type === 'company') {
```

**Valeur en dur**: `'company'`

**33. Ligne 63** | Catégorie: `validation_types`

```
} else if (type === 'company') {
```

**Valeur en dur**: `'company'`

**34. Ligne 65** | Catégorie: `validation_types`

```
} else if (type === 'collaborator') {
```

**Valeur en dur**: `'collaborator'`

**35. Ligne 103** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin'].includes(role)) ||
```

**Valeur en dur**: `'admin'`

**36. Ligne 103** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin'].includes(role)) ||
```

**Valeur en dur**: `'super_admin'`

**37. Ligne 106** | Catégorie: `roles`

```
user.email?.toLowerCase().includes('commercial')
```

**Valeur en dur**: `'commercial'`

**38. Ligne 112** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
```

**Valeur en dur**: `'admin'`

**39. Ligne 112** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
```

**Valeur en dur**: `'super_admin'`

**40. Ligne 112** | Catégorie: `roles`

```
user.roles?.some((role: string) => ['admin', 'super_admin', 'commercial'].includes(role))
```

**Valeur en dur**: `'commercial'`

**41. Ligne 244** | Catégorie: `roles`

```
onClick={() => handleTileClick('interim')}
```

**Valeur en dur**: `'interim'`

**42. Ligne 244** | Catégorie: `validation_types`

```
onClick={() => handleTileClick('interim')}
```

**Valeur en dur**: `'interim'`

**43. Ligne 257** | Catégorie: `roles`

```
onClick={() => handleTileClick('company')}
```

**Valeur en dur**: `'company'`

**44. Ligne 257** | Catégorie: `validation_types`

```
onClick={() => handleTileClick('company')}
```

**Valeur en dur**: `'company'`

**45. Ligne 270** | Catégorie: `validation_types`

```
onClick={() => handleTileClick('collaborator')}
```

**Valeur en dur**: `'collaborator'`

**46. Ligne 301** | Catégorie: `roles`

```
onClick={() => setActiveTab('interim')}
```

**Valeur en dur**: `'interim'`

**47. Ligne 301** | Catégorie: `validation_types`

```
onClick={() => setActiveTab('interim')}
```

**Valeur en dur**: `'interim'`

**48. Ligne 303** | Catégorie: `roles`

```
activeTab === 'interim'
```

**Valeur en dur**: `'interim'`

**49. Ligne 303** | Catégorie: `validation_types`

```
activeTab === 'interim'
```

**Valeur en dur**: `'interim'`

**50. Ligne 311** | Catégorie: `roles`

```
onClick={() => setActiveTab('company')}
```

**Valeur en dur**: `'company'`

**51. Ligne 311** | Catégorie: `validation_types`

```
onClick={() => setActiveTab('company')}
```

**Valeur en dur**: `'company'`

**52. Ligne 313** | Catégorie: `roles`

```
activeTab === 'company'
```

**Valeur en dur**: `'company'`

**53. Ligne 313** | Catégorie: `validation_types`

```
activeTab === 'company'
```

**Valeur en dur**: `'company'`

**54. Ligne 321** | Catégorie: `validation_types`

```
onClick={() => setActiveTab('collaborator')}
```

**Valeur en dur**: `'collaborator'`

**55. Ligne 323** | Catégorie: `validation_types`

```
activeTab === 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**56. Ligne 342** | Catégorie: `application_status`

```
<option value="rejected">Rejetées</option>
```

**Valeur en dur**: `"rejected"`

**57. Ligne 587** | Catégorie: `roles`

```
bulkActionType === 'interim' ? 'Intérimaires' :
```

**Valeur en dur**: `'interim'`

**58. Ligne 587** | Catégorie: `validation_types`

```
bulkActionType === 'interim' ? 'Intérimaires' :
```

**Valeur en dur**: `'interim'`

**59. Ligne 588** | Catégorie: `roles`

```
bulkActionType === 'company' ? 'Entreprises' :
```

**Valeur en dur**: `'company'`

**60. Ligne 588** | Catégorie: `validation_types`

```
bulkActionType === 'company' ? 'Entreprises' :
```

**Valeur en dur**: `'company'`

**61. Ligne 589** | Catégorie: `validation_types`

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

**1. Ligne 86** | Catégorie: `roles`

```
if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'admin'`

**2. Ligne 86** | Catégorie: `roles`

```
if (userRoles.includes('admin') || userRoles.includes('super_admin')) {
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 88** | Catégorie: `roles`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**4. Ligne 88** | Catégorie: `validation_types`

```
} else if (userRoles.includes('interim')) {
```

**Valeur en dur**: `'interim'`

**5. Ligne 90** | Catégorie: `roles`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**6. Ligne 90** | Catégorie: `validation_types`

```
} else if (userRoles.includes('company')) {
```

**Valeur en dur**: `'company'`

**7. Ligne 92** | Catégorie: `roles`

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

**1. Ligne 69** | Catégorie: `application_status`

```
validation.status === 'rejected' && 'border-red-500 bg-red-50'
```

**Valeur en dur**: `'rejected'`

**2. Ligne 80** | Catégorie: `application_status`

```
{validation.status === 'rejected' && (
```

**Valeur en dur**: `'rejected'`

**3. Ligne 107** | Catégorie: `application_status`

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


### 📄 `apps/web/src/hooks/useAppConfig.ts`

**1. Ligne 39** | Catégorie: `roles`

```
admin: 'admin',
```

**Valeur en dur**: `'admin'`

**2. Ligne 40** | Catégorie: `roles`

```
super_admin: 'super_admin',
```

**Valeur en dur**: `'super_admin'`

**3. Ligne 41** | Catégorie: `roles`

```
company: 'company',
```

**Valeur en dur**: `'company'`

**4. Ligne 41** | Catégorie: `validation_types`

```
company: 'company',
```

**Valeur en dur**: `'company'`

**5. Ligne 42** | Catégorie: `roles`

```
interim: 'interim',
```

**Valeur en dur**: `'interim'`

**6. Ligne 42** | Catégorie: `validation_types`

```
interim: 'interim',
```

**Valeur en dur**: `'interim'`

**7. Ligne 43** | Catégorie: `roles`

```
agency: 'agency',
```

**Valeur en dur**: `'agency'`

**8. Ligne 44** | Catégorie: `roles`

```
commercial: 'commercial',
```

**Valeur en dur**: `'commercial'`

**9. Ligne 45** | Catégorie: `roles`

```
validator: 'validator'
```

**Valeur en dur**: `'validator'`

**10. Ligne 80** | Catégorie: `application_status`

```
submitted: 'submitted',
```

**Valeur en dur**: `'submitted'`

**11. Ligne 81** | Catégorie: `application_status`

```
review: 'review',
```

**Valeur en dur**: `'review'`

**12. Ligne 82** | Catégorie: `application_status`

```
interview_scheduled: 'interview_scheduled',
```

**Valeur en dur**: `'interview_scheduled'`

**13. Ligne 83** | Catégorie: `application_status`

```
interviewed: 'interviewed',
```

**Valeur en dur**: `'interviewed'`

**14. Ligne 84** | Catégorie: `application_status`

```
selected: 'selected',
```

**Valeur en dur**: `'selected'`

**15. Ligne 85** | Catégorie: `application_status`

```
rejected: 'rejected',
```

**Valeur en dur**: `'rejected'`

**16. Ligne 86** | Catégorie: `application_status`

```
medical_pending: 'medical_pending',
```

**Valeur en dur**: `'medical_pending'`

**17. Ligne 87** | Catégorie: `application_status`

```
medical_completed: 'medical_completed',
```

**Valeur en dur**: `'medical_completed'`

**18. Ligne 88** | Catégorie: `application_status`

```
contract_pending: 'contract_pending',
```

**Valeur en dur**: `'contract_pending'`

**19. Ligne 89** | Catégorie: `application_status`

```
contract_signed: 'contract_signed'
```

**Valeur en dur**: `'contract_signed'`

**20. Ligne 98** | Catégorie: `roles`

```
interim: 'interim',
```

**Valeur en dur**: `'interim'`

**21. Ligne 98** | Catégorie: `validation_types`

```
interim: 'interim',
```

**Valeur en dur**: `'interim'`

**22. Ligne 99** | Catégorie: `roles`

```
company: 'company',
```

**Valeur en dur**: `'company'`

**23. Ligne 99** | Catégorie: `validation_types`

```
company: 'company',
```

**Valeur en dur**: `'company'`

**24. Ligne 100** | Catégorie: `validation_types`

```
collaborator: 'collaborator'
```

**Valeur en dur**: `'collaborator'`

**25. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'submitted'`

**26. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'review'`

**27. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'interview_scheduled'`

**28. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'interviewed'`

**29. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'selected'`

**30. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'rejected'`

**31. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'medical_pending'`

**32. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'medical_completed'`

**33. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'contract_pending'`

**34. Ligne 115** | Catégorie: `application_status`

```
applicationStatuses: ['submitted', 'review', 'interview_scheduled', 'interviewed', 'selected', 'rejected', 'medical_pending', 'medical_completed', 'contract_pending', 'contract_signed'],
```

**Valeur en dur**: `'contract_signed'`

**35. Ligne 116** | Catégorie: `application_status`

```
validationStatuses: ['pending', 'approved', 'rejected'],
```

**Valeur en dur**: `'rejected'`

**36. Ligne 117** | Catégorie: `roles`

```
validationTypes: ['interim', 'company', 'collaborator'],
```

**Valeur en dur**: `'company'`

**37. Ligne 117** | Catégorie: `roles`

```
validationTypes: ['interim', 'company', 'collaborator'],
```

**Valeur en dur**: `'interim'`

**38. Ligne 117** | Catégorie: `validation_types`

```
validationTypes: ['interim', 'company', 'collaborator'],
```

**Valeur en dur**: `'interim'`

**39. Ligne 117** | Catégorie: `validation_types`

```
validationTypes: ['interim', 'company', 'collaborator'],
```

**Valeur en dur**: `'company'`

**40. Ligne 117** | Catégorie: `validation_types`

```
validationTypes: ['interim', 'company', 'collaborator'],
```

**Valeur en dur**: `'collaborator'`

**41. Ligne 118** | Catégorie: `roles`

```
contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
```

**Valeur en dur**: `'interim'`

**42. Ligne 118** | Catégorie: `validation_types`

```
contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
```

**Valeur en dur**: `'interim'`


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

**1. Ligne 171** | Catégorie: `validation_types`

```
validation_type = "collaborator"
```

**Valeur en dur**: `"collaborator"`

**2. Ligne 314** | Catégorie: `roles`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**3. Ligne 314** | Catégorie: `validation_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**4. Ligne 328** | Catégorie: `roles`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**5. Ligne 328** | Catégorie: `validation_types`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**6. Ligne 343** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'admin'`

**7. Ligne 343** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'super_admin'`

**8. Ligne 783** | Catégorie: `roles`

```
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
```

**Valeur en dur**: `'admin'`

**9. Ligne 1157** | Catégorie: `roles`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**10. Ligne 1157** | Catégorie: `roles`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**11. Ligne 1157** | Catégorie: `validation_types`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**12. Ligne 1157** | Catégorie: `validation_types`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**13. Ligne 1160** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**14. Ligne 1160** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**15. Ligne 1160** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**16. Ligne 1160** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**17. Ligne 1510** | Catégorie: `roles`

```
"admin": admin_users,
```

**Valeur en dur**: `"admin"`

**18. Ligne 1511** | Catégorie: `roles`

```
"super_admin": super_admin_users,
```

**Valeur en dur**: `"super_admin"`

**19. Ligne 1512** | Catégorie: `roles`

```
"interim": interim_users,
```

**Valeur en dur**: `"interim"`

**20. Ligne 1512** | Catégorie: `validation_types`

```
"interim": interim_users,
```

**Valeur en dur**: `"interim"`

**21. Ligne 1513** | Catégorie: `roles`

```
"company": company_users,
```

**Valeur en dur**: `"company"`

**22. Ligne 1513** | Catégorie: `validation_types`

```
"company": company_users,
```

**Valeur en dur**: `"company"`

**23. Ligne 1514** | Catégorie: `roles`

```
"agency": agency_users
```

**Valeur en dur**: `"agency"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 155** | Catégorie: `roles`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**2. Ligne 155** | Catégorie: `validation_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**3. Ligne 169** | Catégorie: `roles`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**4. Ligne 169** | Catégorie: `validation_types`

```
elif profile_type == 'company':
```

**Valeur en dur**: `'company'`

**5. Ligne 184** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'admin'`

**6. Ligne 184** | Catégorie: `roles`

```
elif profile_type in ['admin', 'super_admin']:
```

**Valeur en dur**: `'super_admin'`

**7. Ligne 539** | Catégorie: `roles`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**8. Ligne 539** | Catégorie: `roles`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**9. Ligne 539** | Catégorie: `validation_types`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**10. Ligne 539** | Catégorie: `validation_types`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'company'`

**11. Ligne 542** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`

**12. Ligne 542** | Catégorie: `roles`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**13. Ligne 542** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**14. Ligne 542** | Catégorie: `validation_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'company'`


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

**1. Ligne 110** | Catégorie: `application_status`

```
if existing_app["status"] in ["rejected", "rejected_initial"]:
```

**Valeur en dur**: `"rejected"`


### 📄 `auth-microservice/profile_routes.py`

**1. Ligne 40** | Catégorie: `roles`

```
if profile_type == "interim":
```

**Valeur en dur**: `"interim"`

**2. Ligne 40** | Catégorie: `validation_types`

```
if profile_type == "interim":
```

**Valeur en dur**: `"interim"`

**3. Ligne 60** | Catégorie: `roles`

```
elif profile_type == "company":
```

**Valeur en dur**: `"company"`

**4. Ligne 60** | Catégorie: `validation_types`

```
elif profile_type == "company":
```

**Valeur en dur**: `"company"`

**5. Ligne 121** | Catégorie: `validation_types`

```
return {"profile_type": "collaborator", "profile": profile}
```

**Valeur en dur**: `"collaborator"`

**6. Ligne 144** | Catégorie: `validation_types`

```
profile_type = "collaborator"
```

**Valeur en dur**: `"collaborator"`


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

**1. Ligne 80** | Catégorie: `validation_types`

```
pending_collaborator = await db.validations.count_documents({"status": cfg.get_pending_status(), "validation_type": "collaborator"})
```

**Valeur en dur**: `"collaborator"`

**2. Ligne 88** | Catégorie: `application_status`

```
total_rejected = await db.validations.count_documents({"status": "rejected"})
```

**Valeur en dur**: `"rejected"`

**3. Ligne 223** | Catégorie: `application_status`

```
"status": "rejected",
```

**Valeur en dur**: `"rejected"`


## 🟠 Sévérité: HIGH

**Total**: 75 occurrences

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

**1. Ligne 13** | Catégorie: `user_status`

```
const pendingStatus = validationStatuses.find(vs => vs.code === 'pending')?.code || 'pending'
```

**Valeur en dur**: `'pending'`

**2. Ligne 13** | Catégorie: `user_status`

```
const pendingStatus = validationStatuses.find(vs => vs.code === 'pending')?.code || 'pending'
```

**Valeur en dur**: `'pending'`

**3. Ligne 225** | Catégorie: `user_status`

```
{validation.status !== 'pending' && (
```

**Valeur en dur**: `'pending'`


### 📄 `apps/web/src/features/admin/pages/ValidationsPage.tsx`

**1. Ligne 42** | Catégorie: `user_status`

```
pending: validationStatuses.find(vs => vs.code === 'pending')?.code || 'pending',
```

**Valeur en dur**: `'pending'`

**2. Ligne 42** | Catégorie: `user_status`

```
pending: validationStatuses.find(vs => vs.code === 'pending')?.code || 'pending',
```

**Valeur en dur**: `'pending'`

**3. Ligne 340** | Catégorie: `user_status`

```
<option value="pending">En attente</option>
```

**Valeur en dur**: `"pending"`


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


### 📄 `apps/web/src/hooks/useAppConfig.ts`

**1. Ligne 54** | Catégorie: `user_status`

```
active: 'active',
```

**Valeur en dur**: `'active'`

**2. Ligne 55** | Catégorie: `user_status`

```
pending: 'pending',
```

**Valeur en dur**: `'pending'`

**3. Ligne 56** | Catégorie: `user_status`

```
suspended: 'suspended',
```

**Valeur en dur**: `'suspended'`

**4. Ligne 57** | Catégorie: `user_status`

```
deleted: 'deleted',
```

**Valeur en dur**: `'deleted'`

**5. Ligne 58** | Catégorie: `user_status`

```
blocked: 'blocked'
```

**Valeur en dur**: `'blocked'`

**6. Ligne 67** | Catégorie: `mission_status`

```
draft: 'draft',
```

**Valeur en dur**: `'draft'`

**7. Ligne 68** | Catégorie: `mission_status`

```
published: 'published',
```

**Valeur en dur**: `'published'`

**8. Ligne 69** | Catégorie: `mission_status`

```
closed: 'closed',
```

**Valeur en dur**: `'closed'`

**9. Ligne 70** | Catégorie: `mission_status`

```
cancelled: 'cancelled',
```

**Valeur en dur**: `'cancelled'`

**10. Ligne 71** | Catégorie: `mission_status`

```
archived: 'archived'
```

**Valeur en dur**: `'archived'`

**11. Ligne 114** | Catégorie: `mission_status`

```
missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
```

**Valeur en dur**: `'draft'`

**12. Ligne 114** | Catégorie: `mission_status`

```
missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
```

**Valeur en dur**: `'published'`

**13. Ligne 114** | Catégorie: `mission_status`

```
missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
```

**Valeur en dur**: `'closed'`

**14. Ligne 114** | Catégorie: `mission_status`

```
missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
```

**Valeur en dur**: `'cancelled'`

**15. Ligne 114** | Catégorie: `mission_status`

```
missionStatuses: ['draft', 'published', 'closed', 'cancelled', 'archived'],
```

**Valeur en dur**: `'archived'`

**16. Ligne 116** | Catégorie: `user_status`

```
validationStatuses: ['pending', 'approved', 'rejected'],
```

**Valeur en dur**: `'pending'`


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

**1. Ligne 1472** | Catégorie: `user_status`

```
suspended_users = await db.users.count_documents({"status": "suspended"})
```

**Valeur en dur**: `"suspended"`

**2. Ligne 1505** | Catégorie: `user_status`

```
"active": active_users,
```

**Valeur en dur**: `"active"`

**3. Ligne 1506** | Catégorie: `user_status`

```
"pending": pending_users,
```

**Valeur en dur**: `"pending"`

**4. Ligne 1507** | Catégorie: `user_status`

```
"suspended": suspended_users
```

**Valeur en dur**: `"suspended"`


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


## 🟡 Sévérité: MEDIUM

**Total**: 82 occurrences

### 📄 `apps/web/src/components/LoginModal.tsx`

**1. Ligne 43** | Catégorie: `contract_types`

```
} else if (result.user.roles.includes('interim')) {
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

**1. Ligne 178** | Catégorie: `contract_types`

```
validation.validation_type === 'interim'
```

**Valeur en dur**: `'interim'`

**2. Ligne 182** | Catégorie: `contract_types`

```
{validation.validation_type === 'interim' ? 'Intérimaire' : 'Entreprise'}
```

**Valeur en dur**: `'interim'`


### 📄 `apps/web/src/features/admin/pages/ValidationsPage.tsx`

**1. Ligne 28** | Catégorie: `contract_types`

```
type TabType = 'interim' | 'company' | 'collaborator'
```

**Valeur en dur**: `'interim'`

**2. Ligne 36** | Catégorie: `contract_types`

```
interim: validationTypes.find(vt => vt.code === 'interim')?.code || 'interim',
```

**Valeur en dur**: `'interim'`

**3. Ligne 36** | Catégorie: `contract_types`

```
interim: validationTypes.find(vt => vt.code === 'interim')?.code || 'interim',
```

**Valeur en dur**: `'interim'`

**4. Ligne 47** | Catégorie: `contract_types`

```
const [activeTab, setActiveTab] = useState<TabType>('interim')
```

**Valeur en dur**: `'interim'`

**5. Ligne 53** | Catégorie: `contract_types`

```
const [bulkActionType, setBulkActionType] = useState<'all' | 'interim' | 'company' | 'collaborator' | 'warnings'>('all')
```

**Valeur en dur**: `'interim'`

**6. Ligne 58** | Catégorie: `contract_types`

```
const handleTileClick = (type: 'all' | 'interim' | 'company' | 'collaborator' | 'warnings') => {
```

**Valeur en dur**: `'interim'`

**7. Ligne 61** | Catégorie: `contract_types`

```
if (type === 'interim') {
```

**Valeur en dur**: `'interim'`

**8. Ligne 244** | Catégorie: `contract_types`

```
onClick={() => handleTileClick('interim')}
```

**Valeur en dur**: `'interim'`

**9. Ligne 301** | Catégorie: `contract_types`

```
onClick={() => setActiveTab('interim')}
```

**Valeur en dur**: `'interim'`

**10. Ligne 303** | Catégorie: `contract_types`

```
activeTab === 'interim'
```

**Valeur en dur**: `'interim'`

**11. Ligne 587** | Catégorie: `contract_types`

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

**1. Ligne 88** | Catégorie: `contract_types`

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


### 📄 `apps/web/src/hooks/useAppConfig.ts`

**1. Ligne 42** | Catégorie: `contract_types`

```
interim: 'interim',
```

**Valeur en dur**: `'interim'`

**2. Ligne 98** | Catégorie: `contract_types`

```
interim: 'interim',
```

**Valeur en dur**: `'interim'`

**3. Ligne 117** | Catégorie: `contract_types`

```
validationTypes: ['interim', 'company', 'collaborator'],
```

**Valeur en dur**: `'interim'`

**4. Ligne 118** | Catégorie: `contract_types`

```
contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
```

**Valeur en dur**: `'cdi'`

**5. Ligne 118** | Catégorie: `contract_types`

```
contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
```

**Valeur en dur**: `'cdd'`

**6. Ligne 118** | Catégorie: `contract_types`

```
contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
```

**Valeur en dur**: `'interim'`

**7. Ligne 118** | Catégorie: `contract_types`

```
contractTypes: ['cdi', 'cdd', 'interim', 'freelance', 'stage'],
```

**Valeur en dur**: `'freelance'`


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

**1. Ligne 314** | Catégorie: `contract_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**2. Ligne 540** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**3. Ligne 746** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**4. Ligne 1015** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**5. Ligne 1123** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**6. Ligne 1157** | Catégorie: `contract_types`

```
if register_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**7. Ligne 1160** | Catégorie: `contract_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**8. Ligne 1324** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**9. Ligne 1436** | Catégorie: `delays_days`

```
expires_in=auth_config.jwt_access_token_expire_minutes * 60,
```

**Valeur en dur**: `expires_in=auth_config.jwt_access_token_expire_minutes * 60`

**10. Ligne 1489** | Catégorie: `delays_days`

```
seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
```

**Valeur en dur**: `days=7`

**11. Ligne 1493** | Catégorie: `delays_days`

```
one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
```

**Valeur en dur**: `days=1`

**12. Ligne 1512** | Catégorie: `contract_types`

```
"interim": interim_users,
```

**Valeur en dur**: `"interim"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 93** | Catégorie: `delays_days`

```
"expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
```

**Valeur en dur**: `expires_at": datetime.now(timezone.utc) + timedelta(minutes=10`

**2. Ligne 97** | Catégorie: `delays_days`

```
await db.oauth_states.create_index("expires_at", expireAfterSeconds=0)
```

**Valeur en dur**: `expires_at", expireAfterSeconds=0`

**3. Ligne 155** | Catégorie: `contract_types`

```
if profile_type == 'interim':
```

**Valeur en dur**: `'interim'`

**4. Ligne 539** | Catégorie: `contract_types`

```
if registration_data.role not in ['interim', 'company']:
```

**Valeur en dur**: `'interim'`

**5. Ligne 542** | Catégorie: `contract_types`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `'interim'`

**6. Ligne 646** | Catégorie: `delays_days`

```
"expires_in": 1800,
```

**Valeur en dur**: `expires_in": 1800`


### 📄 `auth-microservice/profile_routes.py`

**1. Ligne 40** | Catégorie: `contract_types`

```
if profile_type == "interim":
```

**Valeur en dur**: `"interim"`

**2. Ligne 224** | Catégorie: `document_types`

```
if document_type == "cv":
```

**Valeur en dur**: `"cv"`

**3. Ligne 292** | Catégorie: `document_types`

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


## 🟢 Sévérité: LOW

**Total**: 184 occurrences

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

**1. Ligne 579** | Catégorie: `messages`

```
detail="ID token is required"
```

**Valeur en dur**: `detail="ID token is required"`

**2. Ligne 620** | Catégorie: `messages`

```
detail="Invalid Microsoft token"
```

**Valeur en dur**: `detail="Invalid Microsoft token"`

**3. Ligne 631** | Catégorie: `messages`

```
detail="Missing required user information from Microsoft"
```

**Valeur en dur**: `detail="Missing required user information from Microsoft"`

**4. Ligne 831** | Catégorie: `messages`

```
detail="Account is not active"
```

**Valeur en dur**: `detail="Account is not active"`

**5. Ligne 864** | Catégorie: `messages`

```
detail="Incorrect username or password"
```

**Valeur en dur**: `detail="Incorrect username or password"`

**6. Ligne 1056** | Catégorie: `messages`

```
detail="Session MFA invalide ou expirée"
```

**Valeur en dur**: `detail="Session MFA invalide ou expirée"`

**7. Ligne 1062** | Catégorie: `messages`

```
detail="MFA n'a pas été vérifiée"
```

**Valeur en dur**: `detail="MFA n'a pas été vérifiée"`

**8. Ligne 1070** | Catégorie: `messages`

```
detail="Utilisateur non trouvé"
```

**Valeur en dur**: `detail="Utilisateur non trouvé"`

**9. Ligne 1160** | Catégorie: `messages`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `detail="Invalid role. Must be 'interim' or 'company'"`

**10. Ligne 1171** | Catégorie: `messages`

```
detail="Ce nom d'utilisateur est déjà utilisé"
```

**Valeur en dur**: `detail="Ce nom d'utilisateur est déjà utilisé"`

**11. Ligne 1182** | Catégorie: `messages`

```
detail="Cet email est déjà utilisé"
```

**Valeur en dur**: `detail="Cet email est déjà utilisé"`

**12. Ligne 1374** | Catégorie: `messages`

```
detail="Logout failed"
```

**Valeur en dur**: `detail="Logout failed"`

**13. Ligne 1399** | Catégorie: `messages`

```
detail="Session not found or expired"
```

**Valeur en dur**: `detail="Session not found or expired"`

**14. Ligne 1408** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**15. Ligne 1446** | Catégorie: `messages`

```
detail="Token refresh failed"
```

**Valeur en dur**: `detail="Token refresh failed"`

**16. Ligne 1531** | Catégorie: `messages`

```
detail="Error retrieving statistics"
```

**Valeur en dur**: `detail="Error retrieving statistics"`

**17. Ligne 1571** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**18. Ligne 1593** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**19. Ligne 1658** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**20. Ligne 1667** | Catégorie: `messages`

```
detail="Cannot delete your own account"
```

**Valeur en dur**: `detail="Cannot delete your own account"`

**21. Ligne 1713** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**22. Ligne 1722** | Catégorie: `messages`

```
detail="Cannot reset your own MFA through admin endpoint. Use the profile settings."
```

**Valeur en dur**: `detail="Cannot reset your own MFA through admin endpoint. Use the profile settings."`

**23. Ligne 1729** | Catégorie: `messages`

```
detail="User does not have MFA enabled"
```

**Valeur en dur**: `detail="User does not have MFA enabled"`

**24. Ligne 1804** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**25. Ligne 1857** | Catégorie: `messages`

```
detail="User not found"
```

**Valeur en dur**: `detail="User not found"`

**26. Ligne 1949** | Catégorie: `messages`

```
detail="Erreur lors de la récupération des utilisateurs"
```

**Valeur en dur**: `detail="Erreur lors de la récupération des utilisateurs"`

**27. Ligne 1981** | Catégorie: `messages`

```
detail="Utilisateur non trouvé"
```

**Valeur en dur**: `detail="Utilisateur non trouvé"`

**28. Ligne 2021** | Catégorie: `messages`

```
detail="Erreur lors de la mise à jour du statut"
```

**Valeur en dur**: `detail="Erreur lors de la mise à jour du statut"`

**29. Ligne 2044** | Catégorie: `messages`

```
detail="Utilisateur non trouvé"
```

**Valeur en dur**: `detail="Utilisateur non trouvé"`

**30. Ligne 2064** | Catégorie: `messages`

```
detail="Cet email est déjà utilisé par un autre utilisateur"
```

**Valeur en dur**: `detail="Cet email est déjà utilisé par un autre utilisateur"`

**31. Ligne 2075** | Catégorie: `messages`

```
detail="Les rôles doivent être une liste"
```

**Valeur en dur**: `detail="Les rôles doivent être une liste"`

**32. Ligne 2088** | Catégorie: `messages`

```
detail="Aucune donnée à mettre à jour"
```

**Valeur en dur**: `detail="Aucune donnée à mettre à jour"`

**33. Ligne 2125** | Catégorie: `messages`

```
detail="Erreur lors de la mise à jour de l'utilisateur"
```

**Valeur en dur**: `detail="Erreur lors de la mise à jour de l'utilisateur"`

**34. Ligne 2211** | Catégorie: `messages`

```
detail="Erreur lors de l'envoi de l'email"
```

**Valeur en dur**: `detail="Erreur lors de l'envoi de l'email"`

**35. Ligne 2240** | Catégorie: `messages`

```
detail="Token invalide ou déjà utilisé"
```

**Valeur en dur**: `detail="Token invalide ou déjà utilisé"`

**36. Ligne 2257** | Catégorie: `messages`

```
detail="Le token a expiré. Veuillez demander un nouveau lien"
```

**Valeur en dur**: `detail="Le token a expiré. Veuillez demander un nouveau lien"`

**37. Ligne 2264** | Catégorie: `messages`

```
detail="Le mot de passe doit contenir au moins 8 caractères"
```

**Valeur en dur**: `detail="Le mot de passe doit contenir au moins 8 caractères"`

**38. Ligne 2322** | Catégorie: `messages`

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

**1. Ligne 55** | Catégorie: `numeric_limits`

```
max_file_size_mb = config.get("storage.uploads.max_file_size_mb", default=10)
```

**Valeur en dur**: `max_file_size_mb = config.get("storage.uploads.max_file_size_mb", default=10`

**2. Ligne 151** | Catégorie: `messages`

```
detail="Document non trouvé"
```

**Valeur en dur**: `detail="Document non trouvé"`

**3. Ligne 162** | Catégorie: `messages`

```
detail="Vous n'avez pas accès à ce document"
```

**Valeur en dur**: `detail="Vous n'avez pas accès à ce document"`

**4. Ligne 169** | Catégorie: `messages`

```
detail="Fichier non trouvé sur le serveur"
```

**Valeur en dur**: `detail="Fichier non trouvé sur le serveur"`

**5. Ligne 215** | Catégorie: `messages`

```
detail="Document non trouvé"
```

**Valeur en dur**: `detail="Document non trouvé"`

**6. Ligne 226** | Catégorie: `messages`

```
detail="Vous ne pouvez supprimer que vos propres documents"
```

**Valeur en dur**: `detail="Vous ne pouvez supprimer que vos propres documents"`


### 📄 `auth-microservice/google_auth_routes.py`

**1. Ligne 59** | Catégorie: `messages`

```
detail="Google OAuth est désactivé"
```

**Valeur en dur**: `detail="Google OAuth est désactivé"`

**2. Ligne 69** | Catégorie: `messages`

```
detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
```

**Valeur en dur**: `detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"`

**3. Ligne 244** | Catégorie: `messages`

```
detail="Failed to initiate Google login"
```

**Valeur en dur**: `detail="Failed to initiate Google login"`

**4. Ligne 269** | Catégorie: `messages`

```
detail="Invalid or expired state parameter"
```

**Valeur en dur**: `detail="Invalid or expired state parameter"`

**5. Ligne 373** | Catégorie: `messages`

```
detail="User not found after creation"
```

**Valeur en dur**: `detail="User not found after creation"`

**6. Ligne 522** | Catégorie: `messages`

```
detail="Missing or invalid authorization header"
```

**Valeur en dur**: `detail="Missing or invalid authorization header"`

**7. Ligne 535** | Catégorie: `messages`

```
detail="Invalid or expired token"
```

**Valeur en dur**: `detail="Invalid or expired token"`

**8. Ligne 542** | Catégorie: `messages`

```
detail="Invalid role. Must be 'interim' or 'company'"
```

**Valeur en dur**: `detail="Invalid role. Must be 'interim' or 'company'"`

**9. Ligne 552** | Catégorie: `messages`

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

**1. Ligne 78** | Catégorie: `numeric_limits`

```
max_applications = config.get("workflows.application.restrictions.max_applications_per_candidate", default=10)
```

**Valeur en dur**: `max_applications = config.get("workflows.application.restrictions.max_applications_per_candidate", default=10`

**2. Ligne 88** | Catégorie: `numeric_limits`

```
min_days_between = config.get("workflows.application.restrictions.min_days_between_applications", default=1)
```

**Valeur en dur**: `min_days_between = config.get("workflows.application.restrictions.min_days_between_applications", default=1`

**3. Ligne 127** | Catégorie: `messages`

```
detail="Vous avez déjà candidaté à cette mission"
```

**Valeur en dur**: `detail="Vous avez déjà candidaté à cette mission"`

**4. Ligne 163** | Catégorie: `messages`

```
detail="Vous n'avez pas la permission de créer une mission"
```

**Valeur en dur**: `detail="Vous n'avez pas la permission de créer une mission"`

**5. Ligne 251** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**6. Ligne 261** | Catégorie: `messages`

```
detail="Mission non accessible"
```

**Valeur en dur**: `detail="Mission non accessible"`

**7. Ligne 267** | Catégorie: `messages`

```
detail="Vous ne pouvez voir que vos missions"
```

**Valeur en dur**: `detail="Vous ne pouvez voir que vos missions"`

**8. Ligne 289** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**9. Ligne 306** | Catégorie: `messages`

```
detail="Vous n'avez pas la permission de modifier cette mission"
```

**Valeur en dur**: `detail="Vous n'avez pas la permission de modifier cette mission"`

**10. Ligne 344** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**11. Ligne 360** | Catégorie: `messages`

```
detail="Vous n'avez pas la permission de supprimer cette mission"
```

**Valeur en dur**: `detail="Vous n'avez pas la permission de supprimer cette mission"`

**12. Ligne 385** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**13. Ligne 395** | Catégorie: `messages`

```
detail="Seuls les commerciaux et admins peuvent publier"
```

**Valeur en dur**: `detail="Seuls les commerciaux et admins peuvent publier"`

**14. Ligne 432** | Catégorie: `messages`

```
detail="Seuls les intérimaires peuvent postuler"
```

**Valeur en dur**: `detail="Seuls les intérimaires peuvent postuler"`

**15. Ligne 440** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**16. Ligne 446** | Catégorie: `messages`

```
detail="Cette mission n'accepte plus de candidatures"
```

**Valeur en dur**: `detail="Cette mission n'accepte plus de candidatures"`

**17. Ligne 458** | Catégorie: `messages`

```
detail="Vous avez déjà postulé à cette mission"
```

**Valeur en dur**: `detail="Vous avez déjà postulé à cette mission"`

**18. Ligne 502** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`

**19. Ligne 519** | Catégorie: `messages`

```
detail="Vous n'avez pas accès aux candidatures"
```

**Valeur en dur**: `detail="Vous n'avez pas accès aux candidatures"`

**20. Ligne 563** | Catégorie: `messages`

```
detail="Candidature non trouvée"
```

**Valeur en dur**: `detail="Candidature non trouvée"`

**21. Ligne 573** | Catégorie: `messages`

```
detail="Permission insuffisante"
```

**Valeur en dur**: `detail="Permission insuffisante"`

**22. Ligne 633** | Catégorie: `messages`

```
detail="Candidature non trouvée"
```

**Valeur en dur**: `detail="Candidature non trouvée"`

**23. Ligne 674** | Catégorie: `messages`

```
detail="Candidature non trouvée"
```

**Valeur en dur**: `detail="Candidature non trouvée"`

**24. Ligne 681** | Catégorie: `messages`

```
detail="Vous ne pouvez modifier que vos propres candidatures"
```

**Valeur en dur**: `detail="Vous ne pouvez modifier que vos propres candidatures"`

**25. Ligne 716** | Catégorie: `messages`

```
detail="Mission non trouvée"
```

**Valeur en dur**: `detail="Mission non trouvée"`


### 📄 `auth-microservice/profile_routes.py`

**1. Ligne 185** | Catégorie: `messages`

```
raise HTTPException(status_code=400, detail="File too large. Maximum size: 5MB")
```

**Valeur en dur**: `detail="File too large. Maximum size: 5MB"`

**2. Ligne 240** | Catégorie: `messages`

```
message="Document uploadé avec succès"
```

**Valeur en dur**: `message="Document uploadé avec succès"`

**3. Ligne 272** | Catégorie: `messages`

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

**1. Ligne 37** | Catégorie: `messages`

```
validation_type: Optional[str] = Query(None, description="Filter by type: interim or company"),
```

**Valeur en dur**: `description="Filter by type: interim or company"`

**2. Ligne 38** | Catégorie: `messages`

```
status: Optional[ValidationStatus] = Query(None, description="Filter by status"),
```

**Valeur en dur**: `description="Filter by status"`

**3. Ligne 39** | Catégorie: `messages`

```
has_location_warning: Optional[bool] = Query(None, description="Filter by location warning"),
```

**Valeur en dur**: `description="Filter by location warning"`

**4. Ligne 40** | Catégorie: `messages`

```
assigned_to: Optional[str] = Query(None, description="Filter by assigned validator"),
```

**Valeur en dur**: `description="Filter by assigned validator"`

**5. Ligne 129** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**6. Ligne 146** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**7. Ligne 152** | Catégorie: `messages`

```
detail="Validation already processed"
```

**Valeur en dur**: `detail="Validation already processed"`

**8. Ligne 198** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**9. Ligne 204** | Catégorie: `messages`

```
detail="Validation already processed"
```

**Valeur en dur**: `detail="Validation already processed"`

**10. Ligne 252** | Catégorie: `messages`

```
detail="Validator not found"
```

**Valeur en dur**: `detail="Validator not found"`

**11. Ligne 260** | Catégorie: `messages`

```
detail="User does not have validator role (admin, super_admin, or commercial)"
```

**Valeur en dur**: `detail="User does not have validator role (admin, super_admin, or commercial)"`

**12. Ligne 277** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**13. Ligne 297** | Catégorie: `messages`

```
detail="Validation not found"
```

**Valeur en dur**: `detail="Validation not found"`

**14. Ligne 303** | Catégorie: `messages`

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
