# 🔎 Audit des valeurs en dur – État d'avancement (28/11/2025)

## Synthèse rapide
- L'audit initial recense **886 occurrences** à supprimer et reste la référence (voir `docs/AUDIT_INDEX.md`).
- Les statuts et types de validation utilisés par l'API d'authentification sont désormais **pilotés par la configuration** (`validation_routes.py`).
- Les parcours d'authentification web (login, callback Google, MFA, modal de connexion) et la création d'utilisateurs côté admin consomment maintenant les rôles issus de la configuration/IAM, éliminant les comparaisons inline.
- La trajectoire reste inchangée : suppression des valeurs en dur, factorisation via la config, et préparation à l'usage mobile.

## Travaux déjà effectués
- **Centralisation des statuts/types de validation** : `auth-microservice/validation_routes.py` lit désormais les statuts (`pending`, `approved`, `rejected`) et types (`interim`, `company`, `collaborator`) via `cfg.get_validation_status` / `cfg.get_validation_type`, couvrant les statistiques, les flux d'approbation/rejet et les contrôles spécifiques aux entreprises.
- **Filtres admin compatibles codes config** : `apps/api/src/presentation/routes/validation_routes.py` accepte désormais les statuts/types issus de la configuration (clé ou valeur) pour les filtres de liste, et applique les transitions d'approbation/rejet avec résolution des codes configurés.
- **Assignation de validations pilotée par la config** : l'attribution d'un validateur dans `auth-microservice/validation_routes.py` s'appuie maintenant sur `cfg.get_validator_roles()` (avec fallback admin/super_admin/commercial), supprimant les listes en dur.
- **Dé-hardcodage du flux candidat → intérimaire** : `auth-microservice/awana_auth_routes.py` s’appuie sur `IAMGroups`, `IAMProfiles`, `UserRoles` et `get_validation_type_for_role` pour éviter les chaînes `candidat`/`grp.*` codées en dur (création des validations, promotion interimaire, mise à jour des rôles).
- **Frontends auth alignés sur la config** : `LoginPage.tsx`, `GoogleCallback.tsx`, `LoginModal.tsx` et `MfaVerificationPage.tsx` redirigent selon les rôles issus de `useRoles`/`UserRoles`, sans dépendre de chaînes `admin`/`super_admin`/`interim`/`company`/`agency` en dur.
- **Création utilisateur admin sans rôles inline** : `CreateUserPage.tsx` construit la liste des rôles proposés à partir de la configuration (admin/super_admin/interim/company/agency).
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

## Actions prioritaires restantes
1. **Externaliser les rôles/statuts auth** : déplacer les comparaisons en dur dans `apps/api/**/awana_auth_routes.py` vers la configuration (`config/base.yaml`).
2. **Centraliser les permissions mission** : consommer des listes de rôles configurées dans `apps/api/**/mission_routes.py` pour la création/publication/édition/lecture globale.
3. **Automatiser l'audit en CI** : exécuter `scripts/audit_hardcoded_values.py` sur chaque PR et échouer en cas de nouvelles occurrences.
4. **Préparer l'exposition mobile** : stabiliser un contrat API v1, ajouter pagination/filtrage systématiques, timeouts et rate limiting pour la résilience.

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
