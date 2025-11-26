# 📊 Progression de la Refactorisation IAM

## ✅ Fichiers Refactorés (11 fichiers)

### Frontend (7 fichiers)
1. ✅ **ValidationsPage.tsx** - 15+ occurrences refactorées
   - Import: `ValidationTypes`, `UserRoles`, `getRoleLabel`
   - Remplacements: candidat, interim, company, collaborateur, admin, super_admin

2. ✅ **RoleSelectionPage.tsx** - 7 occurrences refactorées
   - Import: `UserRoles`
   - Remplacements: 'interim' → UserRoles.INTERIM, 'company' → UserRoles.COMPANY

3. ✅ **RegisterPage.tsx** - 5 occurrences refactorées
   - Import: `ValidationTypes`
   - Remplacements: 'candidat' → ValidationTypes.CANDIDAT, 'company' → ValidationTypes.COMPANY

4. ✅ **LoginPage.tsx** - Redirections basées sur rôles config-driven
   - Utilise `useRoles` pour récupérer admin/super_admin/interim/company/agency/commercial
   - Les rôles postulant/candidat utilisent `UserRoles` (legacy) pour éviter les chaînes inline

5. ✅ **GoogleCallback.tsx** - Redirections OAuth sans rôles hardcodés
   - Mapping admin/super_admin/interim/company/agency/commercial via `useRoles`
   - Ajout des constantes IAM pour les comparaisons de rôles

6. ✅ **MfaVerificationPage.tsx** - Navigation post-MFA alignée IAM/config
   - Repose sur `useRoles` + `UserRoles` pour éliminer les comparaisons en dur
   - Couvre les flux commercial/admin/interim/company/agency/postulant/candidat

7. ✅ **CreateUserPage.tsx** - Liste des rôles alimentée par la configuration
   - Les cases à cocher admin/super_admin/interim/company/agency utilisent `useRoles`
   - Supprime les valeurs en dur dans la création d'utilisateur

### Backend (4 fichiers)
4. ✅ **initialize_candidat_iam.py** - 17 occurrences refactorées
   - Import: `IAMGroups`, `IAMProfiles`, `IAMPermissions`
   - Tous les codes hardcodés remplacés par constantes
   - Fix de connexion MongoDB

5. ✅ **awana_auth_routes.py** - Partiellement refactoré (déjà fait avant)
   - Import: `IAMGroups`, `IAMProfiles`, `UserRoles`, `ValidationTypes`
   - Rôle/validation « candidat » et codes de groupes intérimaires désormais issus des constantes IAM

6. ✅ **validation_routes.py** - Statuts/types de validation centralisés
   - Utilise `cfg.get_validation_status` et `cfg.get_validation_type`
   - Remplace les valeurs en dur dans les stats et transitions d'approbation/rejet

7. ✅ **system_references_routes.py** - Rôles admin/super_admin pilotés par la config
   - Utilise `cfg.get_admin_role` / `cfg.get_super_admin_role` pour les contrôles d'accès publics
   - Mutualise la vérification via `_ensure_admin_or_manage_permission`

8. ✅ **security_routes.py** - Attribution automatique des profils pilotée par la config
   - Mappe les rôles issus de `cfg` vers les profils IAM (`IAMProfiles`)
   - Supprime les chaînes en dur `admin`/`super_admin`/`interim`/`company`/`commercial` dans la création d'utilisateurs

---

## 🔄 Fichiers Restants à Refactorer

### Frontend Prioritaires (~13 fichiers)
- [ ] **EditUserModal.tsx** (1 occurrence)
- [ ] **ValidationsList.tsx** (2 occurrences)
- [ ] **ProfilePage.tsx** (2 occurrences)
- [ ] **MfaVerificationPage.tsx** (2 occurrences)
- [ ] **Breadcrumb.tsx**
- [ ] **LoginModal.tsx** (2 occurrences)
- [ ] **LandingPage.tsx** (2 occurrences)
- [ ] **types/index.ts** (2 occurrences)
- [ ] **hooks/useAppConfig.ts** (6 occurrences)
- [ ] **features/profile/api/profileApi.ts** (1 occurrence)
- [ ] **features/admin/pages/FeatureFlagsPage.tsx**
- [ ] **features/admin/pages/EmailSettingsPage.tsx**
- [ ] **features/missions/pages/MissionDetailPage.tsx**
- [ ] **ProfilesManagementPage.tsx** - Déjà propre
- [ ] **IAMControlPage.tsx** - Déjà propre

### Backend Prioritaires (~11 fichiers)
- [ ] **scripts/initialize_iam_system.py** (GROS fichier - ~13KB)
- [ ] **scripts/migrate_users_to_iam.py**
- [ ] **scripts/update_iam_permissions.py**
- [ ] **scripts/diagnose_login.py** (1 occurrence)
- [ ] **profile_routes.py** (2 occurrences)
- [ ] **contract_routes.py** (2 occurrences)
- [ ] **configuration_routes.py** (2 occurrences)
- [ ] **scripts/seed_mission_references.py** (4 occurrences)
- [ ] **scripts/seed_additional_references.py** (2 occurrences)
- [ ] **scripts/migrate_users_to_iam.py** (2 occurrences)
- [ ] **scripts/add_missing_references.py** (2 occurrences)
- [ ] **awana_auth/core/location_models.py** (1 occurrence)
- [ ] **awana_auth/core/reference_models.py** (1 occurrence)
- [ ] **awana_auth/core/version_models.py** (1 occurrence)

---

## 📈 Statistiques

### Total
- **Fichiers refactorés**: 11 / ~34 (~32%)
- **Occurrences éliminées**: ~70 + statuts/types centralisés dans `validation_routes.py`
- **Tests de sync**: ✅ 100% passés

### Par Catégorie
- **Frontend**: 7 fichiers refactorés / ~17 restants
- **Backend**: 4 fichiers refactorés / ~11 restants

---

## 🎯 Prochaines Actions

### Étape 1: Frontend (Fichiers simples)
1. EditUserModal.tsx (1 occurrence) - 3 min
2. ValidationsList.tsx (2 occurrences) - 5 min
3. ProfilePage.tsx (2 occurrences) - 5 min

**Temps estimé**: ~13 min pour 3 fichiers

### Étape 2: Backend (Scripts importants)
1. initialize_iam_system.py - Fichier critique, beaucoup d'occurrences
2. Scripts de migration et seed

**Temps estimé**: ~30 min

### Étape 3: Tests Unitaires
1. Créer tests backend pour constantes
2. Créer tests frontend pour constantes

**Temps estimé**: ~20 min

### Étape 4: Intégration CI/CD
1. Ajouter test_iam_constants_sync.py au pipeline
2. Configurer pour bloquer les merges si désynchronisé

**Temps estimé**: ~10 min

---

## 🔧 Commandes de Vérification

```bash
# Vérifier la synchronisation
python /app/scripts/test_iam_constants_sync.py

# Trouver les fichiers restants
bash /app/scripts/migrate_to_constants.sh

# Compter les occurrences hardcodées
grep -r "'candidat'\|'interim'\|'company'" /app/apps/web/src --include="*.tsx" | wc -l
grep -r '"candidat"\|"interim"\|"company"' /app/auth-microservice --include="*.py" | wc -l
```

---

**Dernière mise à jour**: 2025-11-27 (ajout redirections auth config-driven + CreateUserPage)
**Statut**: 🔄 En progression (~32% complété)
