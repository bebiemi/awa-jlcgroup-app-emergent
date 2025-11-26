# 📊 Progression de la Refactorisation IAM

## ✅ Fichiers Refactorés (48 fichiers)

### Frontend (23 fichiers)
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

8. ✅ **ProfilePage.tsx** - Sélecteurs de profils basés sur la config
   - Utilise `useRoles` et `useValidationTypes` pour déterminer les expériences et formulaires affichés
   - Remplace les chaînes `candidat`/`postulant`/`interim`/`company`/`collaborator` en dur

9. ✅ **ProfileCompletionWidget.tsx** - Widgets alignés sur les types configurés
   - Détecte les profils intérim via les types de validation configurés
   - Supprime la dépendance au statut inline `interim`

10. ✅ **profileApi.ts** - Typage aligné sur les constantes IAM
    - `profile_type` repose sur `ValidationType` plutôt que sur des littéraux inline

11. ✅ **LoginModal.tsx** - Redirections configurées sur les rôles IAM
    - Les chemins `/admin`/`/interimaire`/`/entreprise`/`/agence`/`/commercial` utilisent `useRoles`
    - Supprime les comparaisons inline `admin`/`super_admin`/`interim`/`company`/`agency`

12. ✅ **LandingPage.tsx** - Bouton « Accéder à mon espace » aligné IAM
    - Résout les redirections via les rôles configurés (admin/super_admin/interim/company/agency/commercial)
    - Évite les chaînes en dur pour déterminer le tableau de bord cible

13. ✅ **types/index.ts** - Typage relié aux constantes IAM
    - `ProfileType` s'appuie sur `IAMProfiles`/`UserRoles` au lieu de littéraux
    - `ValidationType` réutilise le type exporté par `iamConstants.ts`

14. ✅ **FeatureFlagsPage.tsx** - Formulaire aligné sur les rôles configurés
    - Le placeholder de ciblage par rôle réutilise `useRoles()` (fallback configuré)
    - Évite la chaîne inline `admin` dans les formulaires de création/édition
15. ✅ **MissionDetailPage.tsx** - Statuts mission/candidature pilotés par la configuration
    - Cartographie des labels basée sur `useMissionStatuses` / `useApplicationStatuses`
    - Bouton de publication et badges de candidatures sans chaînes de statut en dur
16. ✅ **useAppConfig.ts** - Fallbacks des statuts mission/candidature retournés en dictionnaire
    - Les statuts de mission et de candidature sont normalisés en map pour éviter les accès sur tableaux
    - Prépare les composants à consommer des codes configurés sans dépendre des valeurs par défaut
17. ✅ **UsersPage.tsx** - Filtres rôle/statut alimentés par la configuration
    - Options de filtres construites via `useRoles` et `useUserStatuses`
    - Badges de statut colorés sur les statuts configurés (fallback inclus pour archived/blocked)
18. ✅ **BulkImportUsersModal.tsx** - Instructions d’import synchronisées sur les rôles configurés
    - Liste des rôles autorisés générée depuis la configuration + `getRoleLabel`
    - Évite les listes de rôles en dur dans les consignes CSV

19. ✅ **EditUserModal.tsx** - Edition utilisateur alignée IAM
    - Utilise `IAMPermissions.USERS_EDIT/USERS_MANAGE` pour les contrôles d'accès
    - Les rôles hérités affichent les labels/couleurs issus des constantes IAM au lieu des codes bruts

20. ✅ **EmailSettingsPage.tsx** - Configuration email pilotée par les permissions IAM
    - Permissions `emails.configure`/`emails.read_config`/`emails.test` injectées via `IAMPermissions`
    - Prépare les contrôles d'accès à suivre la configuration centrale

21. ✅ **EmailHistoryPage.tsx** - Historique email sécurisé par les permissions configurées
    - Lecture conditionnée par `IAMPermissions.EMAILS_READ_HISTORY`

22. ✅ **EmailTemplatesPage.tsx** - Gestion des templates alignée sur IAM
    - Permissions `emails.manage_templates`/`emails.read_config` issues des constantes front synchronisées

23. ✅ **Navigation/Routes admin (Sidebar.tsx, admin.routes.tsx, navigation.config.ts)**
    - Les routes et menus email consomment `IAMPermissions` au lieu des codes inline
    - Le breadcrumb récupère la racine contextuelle depuis la configuration de navigation plutôt que le chemin `/` codé en dur

### Backend (25 fichiers)
1. ✅ **initialize_candidat_iam.py** - 17 occurrences refactorées
   - Import: `IAMGroups`, `IAMProfiles`, `IAMPermissions`
   - Tous les codes hardcodés remplacés par constantes
   - Fix de connexion MongoDB

2. ✅ **awana_auth_routes.py** - Partiellement refactoré (déjà fait avant)
   - Import: `IAMGroups`, `IAMProfiles`, `UserRoles`, `ValidationTypes`
   - Rôle/validation « candidat » et codes de groupes intérimaires désormais issus des constantes IAM

3. ✅ **validation_routes.py** - Statuts/types de validation centralisés
   - Utilise `cfg.get_validation_status` et `cfg.get_validation_type`
   - Remplace les valeurs en dur dans les stats, transitions d'approbation/rejet et filtres admin
   - Les filtres de liste acceptent désormais les codes configurés (mappés vers enums si présents)
   - L'assignation d'un validateur consomme `cfg.get_validator_roles()` (fallback admin/super_admin/commercial)

4. ✅ **system_references_routes.py** - Rôles admin/super_admin pilotés par la config
   - Utilise `cfg.get_admin_role` / `cfg.get_super_admin_role` pour les contrôles d'accès publics
   - Mutualise la vérification via `_ensure_admin_or_manage_permission`

5. ✅ **security_routes.py** - Attribution automatique des profils pilotée par la config
   - Mappe les rôles issus de `cfg` vers les profils IAM (`IAMProfiles`)
   - Supprime les chaînes en dur `admin`/`super_admin`/`interim`/`company`/`commercial` dans la création d'utilisateurs

6. ✅ **google_auth_routes.py** - Création de profils OAuth alignée sur les rôles configurés
   - Les profils `interim`/`company`/`admin`/`super_admin` reposent sur `cfg` plutôt que sur des littéraux
   - Les flux Google continuent de provisionner les comptes avec les rôles configurés par défaut

7. ✅ **temporary_permissions_routes.py** - Vérifications admin centralisées
   - Les contrôles d'accès utilisent `cfg.get_admin_role` et `cfg.get_super_admin_role`
   - Évite les comparaisons inline pour l'affichage et la gestion des permissions temporaires

8. ✅ **iam_routes.py** - Lecture des permissions utilisateur sans rôles en dur
   - L'accès administrateur au listing des permissions s'appuie sur les rôles configurés
   - Prépare la factorisation des contrôles IAM restants

9. ✅ **scripts/migrate_users_to_iam.py** - Migration des utilisateurs basée sur la config
   - Les rôles sources s'appuient sur `ConfigHelper` pour éviter les littéraux `admin`/`interim`/`company`
   - Le mapping rôles → profils ignore automatiquement les rôles non définis

10. ✅ **dependencies.py** - Rôles admin/validator lus depuis la configuration
    - Les rôles `admin`/`super_admin`/`commercial` par défaut proviennent des clés `security.roles`
    - Fournit des listes dédupliquées pour les dépendances `require_admin` / `require_validator`

11. ✅ **notification_routes.py** - Création de notifications sécurisée via les rôles configurés
    - Le contrôle d'accès admin repose sur la dépendance `require_admin` alimentée par la configuration

12. ✅ **profile_routes.py** - Accès profil admin/self aligné sur la config
    - Vérifie l'appartenance aux rôles admin/super_admin issus de `security.roles` avant l'accès aux profils tiers

13. ✅ **scripts/diagnose_login.py** - Diagnostic IAM basé sur les constantes
    - Vérifie le groupe candidat via `IAMGroups.CANDIDAT` plutôt que la chaîne `grp.candidat`

14. ✅ **mission_routes.py** - Restrictions de re-candidature alignées sur les statuts référentiels
    - Les contrôles de re-candidature utilisent `ApplicationStatus.REJECTED`/`REJECTED_INITIAL` au lieu de chaînes inline

15. ✅ **admin_routes.py** - KPIs admin calculés via statuts/types/profils configurés
    - Les compteurs pending/approved/rejected lisent les statuts du workflow de validation depuis la configuration
    - Les filtres par type de validation et les totaux de profils consomment les codes de config (fallback enum)
    - Expose la liste des codes de profils configurés pour faciliter le suivi dashboard

16. ✅ **contract_routes.py** - Contrats alignés sur les statuts configurés
    - Les vérifications d'accès intérim utilisent le rôle configuré (fallback `interim`)
    - Les filtres/contrôles de contrats consomment les statuts d'application `contract_signed`/`contract_pending` depuis la configuration
    - Supprime les chaînes inline dans les requêtes MongoDB et la détection de contrats actifs
17. ✅ **awana_auth/core/location_models.py** - Statuts/roles de validation pilotés par la config
    - Les enums `ValidationStatus` et `ValidatorRole` utilisent les valeurs issues de `ConfigHelper` (fallback sur les valeurs historiques)
    - Centralise les imports manquants et prépare les modèles de localisation à consommer les codes configurés
18. ✅ **configuration_routes.py** - Rôles/statuts exposés sans clés inline
    - Les routes `/config/all` lisent les rôles et statuts utilisateur via `ConfigHelper` pour éviter les clés codées en dur
    - Prépare les réponses front à s'aligner automatiquement sur les valeurs configurées

19. ✅ **scripts/seed_mission_references.py** - Référentiels mission pilotés par la config
    - Les statuts de mission/candidature et rôles d'action sont lus via `ConfigHelper`
    - Supprime les chaînes inline `company`/`agency` et aligne les transitions sur les codes configurés
20. ✅ **scripts/initialize_iam_system.py** - Profils/groupes IAM dérivés de la configuration
    - Codes de rôles super_admin/admin/interim/company/commercial/postulant lus via `ConfigHelper` (fallbacks hérités)
    - Le groupe super admin est créé à partir du code configuré, supprimant les littéraux inline
21. ✅ **awana_auth/core/reference_models.py** - Exemple de référentiel aligné sur les rôles configurés
    - Les imports manquants sont restaurés
    - L'exemple JSON s'appuie sur le rôle intérim issu de la configuration (fallback `interim`)
22. ✅ **scripts/update_iam_permissions.py** - Mise à jour des profils admins sans code inline
    - Le profil admin ciblé est récupéré via `ConfigHelper` avant d'assigner toutes les permissions
    - Évite la chaîne `admin` codée en dur dans la mise à jour des permissions systèmes
23. ✅ **scripts/seed_additional_references.py** - Rôles référentiels dérivés de la configuration
    - Les codes admin/super_admin/company/agency/commercial/interim sont injectés depuis `ConfigHelper`
    - Supprime les valeurs en dur tout en conservant les métadonnées de permissions/rendu
24. ✅ **scripts/add_missing_references.py** - Statuts/types/roles de validation paramétrés
    - Les statuts utilisateur, validation et mission utilisent les codes issus de la configuration (fallbacks inclus)
    - Le rôle validator et les statuts de candidature sont alignés sur la configuration centrale
25. ✅ **awana_auth/core/version_models.py** - Exemple de snapshot aligné sur les rôles/statuts configurés
    - L'exemple `config_data` lit les rôles et statuts via `ConfigHelper` (fallback admin/company/interim/active/pending)
    - L'import `uuid` est repositionné pour éviter les erreurs de référence

---

## 🔄 Fichiers Restants à Refactorer

- Aucun fichier prioritaire restant identifié sur le scope IAM (scripts/refs mis à jour)

---

## 📈 Statistiques

### Total
- **Fichiers refactorés**: 48 / ~48 (~100%)
- **Occurrences éliminées**: ~100 + statuts/types centralisés dans `validation_routes.py`
- **Tests de sync**: ✅ 100% passés

### Par Catégorie
- **Frontend**: 23 fichiers refactorés / 0 restant
- **Backend**: 25 fichiers refactorés / 0 restant prioritaire

---

## 🎯 Prochaines Actions

- 🔍 **Suivi audit automatisé** : le workflow `.github/workflows/audit-hardcoded-values.yml` tourne sur `main` et les PR avec un seuil d'augmentation des occurrences fixé à 0 et un plafond global à 2100. La dernière exécution locale reporte **1934 occurrences** (dont 788 critiques).
- 🧹 **Réduction progressive des occurrences critiques/hautes** : prioriser les messages d'erreur et textes codés en dur listés dans `docs/AUDIT_VALEURS_EN_DUR.md` (ex. routes MFA, invitations, validations) en les externalisant dans la configuration ou les fichiers de traduction.

---

## 🔧 Commandes de Vérification

```bash
# Vérifier la synchronisation IAM
python scripts/test_iam_constants_sync.py

# Relancer l'audit des valeurs en dur
python scripts/audit_hardcoded_values.py --markdown-output docs/AUDIT_VALEURS_EN_DUR.md --stats-output audit_reports/stats.json
```

---

**Dernière mise à jour**: 2025-11-29 (Audit automatisé en place, 1934 occurrences restantes identifiées)
**Statut**: ✅ Phase IAM terminée – suivi audit en cours (100% fichiers IAM refactorés)
