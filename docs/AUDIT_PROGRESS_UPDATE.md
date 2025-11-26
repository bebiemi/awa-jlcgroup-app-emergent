# 🔎 Audit des valeurs en dur – État d'avancement (29/11/2025)

## Synthèse rapide
- Dernier audit automatisé : **1934 occurrences** détectées (788 critiques, 351 hautes, 156 moyennes, 639 basses) – voir `docs/AUDIT_VALEURS_EN_DUR.md` pour le détail.
- Le workflow CI `audit-hardcoded-values.yml` s'exécute sur `main` et PR avec un seuil de nouvelle occurrence à 0 et un plafond global à 2100.
- Les statuts/types IAM et permissions emails sont maintenant pilotés par la configuration sur l'ensemble web/API/auth ; la phase de refactorisation IAM est close, le focus passe à la dé-hardcodification des messages et références restantes.

## Travaux déjà effectués
- **Centralisation des statuts/types de validation** : `auth-microservice/validation_routes.py` lit désormais les statuts (`pending`, `approved`, `rejected`) et types (`interim`, `company`, `collaborator`) via `cfg.get_validation_status` / `cfg.get_validation_type`, couvrant les statistiques, les flux d'approbation/rejet et les contrôles spécifiques aux entreprises.
- **Audit automatisé en CI** : `.github/workflows/audit-hardcoded-values.yml` exécute `scripts/audit_hardcoded_values.py` sur `main`/PR, publie le rapport en artefact et bloque toute augmentation des occurrences au-delà du seuil configuré.
- **Filtres admin compatibles codes config** : `apps/api/src/presentation/routes/validation_routes.py` accepte désormais les statuts/types issus de la configuration (clé ou valeur) pour les filtres de liste, et applique les transitions d'approbation/rejet avec résolution des codes configurés.
- **Assignation de validations pilotée par la config** : l'attribution d'un validateur dans `auth-microservice/validation_routes.py` s'appuie maintenant sur `cfg.get_validator_roles()` (avec fallback admin/super_admin/commercial), supprimant les listes en dur.
- **Dé-hardcodage du flux candidat → intérimaire** : `auth-microservice/awana_auth_routes.py` s’appuie sur `IAMGroups`, `IAMProfiles`, `UserRoles` et `get_validation_type_for_role` pour éviter les chaînes `candidat`/`grp.*` codées en dur (création des validations, promotion interimaire, mise à jour des rôles).
- **Frontends auth alignés sur la config** : `LoginPage.tsx`, `GoogleCallback.tsx`, `LoginModal.tsx` et `MfaVerificationPage.tsx` redirigent selon les rôles issus de `useRoles`/`UserRoles`, sans dépendre de chaînes `admin`/`super_admin`/`interim`/`company`/`agency` en dur.
- **Création utilisateur admin sans rôles inline** : `CreateUserPage.tsx` construit la liste des rôles proposés à partir de la configuration (admin/super_admin/interim/company/agency).
- **Gestion utilisateur et import alignés configuration** : `UsersPage.tsx` construit les filtres rôle/statut depuis `useRoles`/`useUserStatuses` et applique les badges sur les statuts configurés, tandis que `BulkImportUsersModal.tsx` affiche les rôles autorisés issus de la configuration au lieu d'une liste en dur.
- **Constantes IAM synchronisées** : `apps/web/src/constants/iamConstants.ts` inclut désormais les valeurs `POSTULANT` pour refléter les constantes backend (`iam_constants.py`).
- **ValidationsList.tsx alignée sur la config** : les filtres « En attente/Approuvées/Refusées » consomment désormais les statuts issus de la configuration/référentiels au lieu des chaînes `pending/approved/rejected` en dur.
- **Documentation de progression mise à jour** : `REFACTORING_PROGRESS.md` reflète 28 fichiers refactorés (~82% du périmètre) dont les flux auth frontend (pages + modal), la création d'utilisateur, la page profil, les filtres de validations alignés sur la config et le typage partagé.

- **Re-candidature mission sans statuts en dur** : `auth-microservice/mission_routes.py` vérifie désormais les statuts de rejet via `ApplicationStatus.REJECTED`/`REJECTED_INITIAL` pour éviter les chaînes inline dans les contrôles de re-application.

- **LandingPage sans rôles inline** : le bouton « Accéder à mon espace » calcule la redirection via les rôles configurés (admin/super_admin/interim/company/agency/commercial) au lieu de chaînes en dur.

- **Typage partagé aligné IAM** : `apps/web/src/types/index.ts` réutilise les constantes `IAMProfiles`/`UserRoles` et le type `ValidationType` exporté, supprimant les littéraux `admin`/`company`/`interim`/`agency`/`company` dans les unions.
- **Contrôles d'accès référentiels alignés IAM** : `auth-microservice/system_references_routes.py` n’utilise plus les rôles `admin`/`super_admin` en dur et s'appuie sur `cfg.get_admin_role` / `cfg.get_super_admin_role` pour sécuriser l'accès public aux référentiels.
- **Attribution de profils IAM sans valeurs en dur** : `auth-microservice/security_routes.py` mappe désormais les rôles issus de la configuration (`cfg`) vers les profils `IAMProfiles`, supprimant les chaînes inline `admin`/`super_admin`/`interim`/`company`/`commercial` lors de la création d'utilisateurs.
- **Contrôles d'accès admin API centralisés** : `apps/api/src/presentation/dependencies.py` lit désormais les rôles admin/super_admin depuis la configuration, et les routes `notification_routes.py` / `profile_routes.py` s'appuient sur ces rôles configurés plutôt que sur les chaînes inline.
- **Profils utilisateur alignés IAM côté web** : la page profil (`ProfilePage.tsx`) et le widget de complétion (`ProfileCompletionWidget.tsx`) s'appuient sur `useRoles`/`useValidationTypes` pour sélectionner les formulaires et champs à afficher au lieu de valeurs en dur (`candidat`, `postulant`, `interim`, `company`, `collaborator`).
- **API profil typée sur les constantes** : `profileApi.ts` déclare désormais `profile_type` via `ValidationType`, garantissant la cohérence des types avec le backend.
- **Google OAuth sans rôles inline** : `auth-microservice/google_auth_routes.py` crée les profils `interim`/`company`/`admin`/`super_admin` à partir des rôles configurés au lieu de littéraux.
- **Permissions temporaires/IAM sans chaînes admin** : `auth-microservice/temporary_permissions_routes.py` et `auth-microservice/iam_routes.py` utilisent `cfg.get_admin_role`/`cfg.get_super_admin_role` pour sécuriser l'accès aux permissions, évitant les comparaisons en dur.
- **Migration IAM pilotée par la config** : `auth-microservice/scripts/migrate_users_to_iam.py` s'appuie désormais sur `ConfigHelper` pour traduire les rôles configurés en profils cibles, en filtrant automatiquement les rôles inconnus.
- **Diagnostic login aligné IAM** : `auth-microservice/scripts/diagnose_login.py` vérifie désormais le groupe candidat via `IAMGroups.CANDIDAT` au lieu de la chaîne `grp.candidat` en dur.
- **KPIs admin sans statuts/profils en dur** : `apps/api/src/presentation/routes/admin_routes.py` lit les statuts/types de validation et les profils depuis la configuration pour calculer les compteurs et totaux, avec fallback enum si nécessaire. Les dépôts validation/profil acceptent désormais les valeurs brutes issues de la config.
- **Contrats intérim configurables** : `auth-microservice/contract_routes.py` utilise le rôle intérim issu de la configuration et les statuts d'application configurés (`contract_signed`/`contract_pending`) pour filtrer les contrats et détecter les contrats actifs sans chaînes inline.
- **Modèles de validation/location alignés sur la config** : `awana_auth/core/location_models.py` utilise désormais les statuts/roles de validation issus de `ConfigHelper` (avec fallback sur les valeurs historiques) et centralise les imports pour préparer la consommation des codes configurés.
- **Configuration exposée sans clés inline** : `auth-microservice/configuration_routes.py` renvoie les rôles et statuts utilisateur directement depuis la configuration via `ConfigHelper`, éliminant les clés `admin`/`super_admin`/`interim`/`company` en dur dans la réponse.
- **Référentiels missions paramétrables** : `auth-microservice/scripts/seed_mission_references.py` lit désormais les statuts de mission/candidature et les rôles d'action (company/agency) via `ConfigHelper`, supprimant les chaînes inline dans les transitions et métadonnées.
- **Feature flags côté admin alignés IAM** : `apps/web/src/features/admin/pages/FeatureFlagsPage.tsx` utilise `useRoles()` pour préremplir la cible par rôle au lieu de la chaîne `admin` en dur.
- **Initialisation IAM pilotée par la config** : `auth-microservice/scripts/initialize_iam_system.py` crée les profils et le groupe super admin à partir des rôles configurés (fallbacks hérités), supprimant les codes inline.
- **Référentiels système alignés config** : l'exemple JSON de `awana_auth/core/reference_models.py` s'appuie sur le rôle intérim issu de la configuration et restaure les imports manquants pour assurer la validité du modèle.
- **Mises à jour IAM et seeds sans rôles en dur** : `auth-microservice/scripts/update_iam_permissions.py`, `scripts/seed_additional_references.py` et `scripts/add_missing_references.py` récupèrent désormais les rôles/statuts via `ConfigHelper`, évitant les codes `admin`/`interim`/`company`/`validator` inline lors des migrations et seeds.
- **Snapshots de configuration dynamiques** : `awana_auth/core/version_models.py` utilise les rôles/statuts configurés (avec fallback) dans l'exemple `config_data` et charge correctement `uuid` pour le `default_factory`.
- **MissionDetailPage alignée sur la configuration** : la page consomme `useMissionStatuses` / `useApplicationStatuses` pour cartographier les statuts mission et candidature, y compris pour les badges et le bouton de publication, sans chaînes de statuts en dur.
- **Hook de configuration mission/candidature** : `useAppConfig.ts` renvoie désormais des dictionnaires pour les statuts de mission/candidature en fallback, évitant les accès sur tableaux lorsqu'on lit les codes configurés.

- **Permissions email alignées IAM** : `EmailSettingsPage.tsx`, `EmailHistoryPage.tsx`, `EmailTemplatesPage.tsx`, la navigation admin (`Sidebar.tsx`, `admin.routes.tsx`, `navigation.config.ts`) consomment les codes `emails.*` via `IAMPermissions`, supprimant les chaînes inline pour les contrôles d'accès.
- **Breadcrumb sans chemin inline** : le fil d'Ariane utilise la racine contextuelle de `navigation.config` plutôt que le `/` codé en dur.

## Actions prioritaires restantes
1. **Réduire les occurrences critiques/hautes** : externaliser les messages d'erreur répétés dans `auth-microservice/mfa_routes.py`, `invitation_routes.py`, `validation_routes.py` et `location_routes.py` vers un référentiel de messages ou un fichier de configuration/i18n.
2. **Suivre le budget d'occurrences CI** : garder le total < `AUDIT_MAX_OCCURRENCES` (2100) et sans augmentation sur PR (`AUDIT_NEW_OCCURRENCES_THRESHOLD=0`) ; ajuster la configuration si le scope évolue.
3. **Préparer l'exposition mobile** : stabiliser un contrat API v1 (pagination/filtrage/tri homogènes), ajouter rate limiting/timeouts côté client et réponses prêtes pour l'offline-first.

## Commandes utiles
```bash
# Rejouer l'audit local des valeurs en dur
python scripts/audit_hardcoded_values.py --markdown-output audit_reports/AUDIT_VALEURS_EN_DUR.md --stats-output audit_reports/stats.json
```

```bash
# Vérifier la progression IAM (constantes synchronisées)
python scripts/test_iam_constants_sync.py
```

## Points de suivi
- Mettre en place un dashboard CI pour publier les rapports d'audit générés.
- Tenir la documentation de configuration à jour après chaque externalisation.
