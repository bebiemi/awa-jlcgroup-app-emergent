# 🔎 Audit des valeurs en dur – État d'avancement (28/11/2025)

## Synthèse rapide
- L'audit initial recense **886 occurrences** à supprimer et reste la référence (voir `docs/AUDIT_INDEX.md`).
- Les statuts et types de validation utilisés par l'API d'authentification sont désormais **pilotés par la configuration** (`validation_routes.py`).
- Les parcours d'authentification web (login, callback Google, MFA) et la création d'utilisateurs côté admin consomment maintenant les rôles issus de la configuration/IAM, éliminant les comparaisons inline.
- La trajectoire reste inchangée : suppression des valeurs en dur, factorisation via la config, et préparation à l'usage mobile.

## Travaux déjà effectués
- **Centralisation des statuts/types de validation** : `auth-microservice/validation_routes.py` lit désormais les statuts (`pending`, `approved`, `rejected`) et types (`interim`, `company`, `collaborator`) via `cfg.get_validation_status` / `cfg.get_validation_type`, couvrant les statistiques, les flux d'approbation/rejet et les contrôles spécifiques aux entreprises.
- **Dé-hardcodage du flux candidat → intérimaire** : `auth-microservice/awana_auth_routes.py` s’appuie sur `IAMGroups`, `IAMProfiles`, `UserRoles` et `get_validation_type_for_role` pour éviter les chaînes `candidat`/`grp.*` codées en dur (création des validations, promotion interimaire, mise à jour des rôles).
- **Frontends auth alignés sur la config** : `LoginPage.tsx`, `GoogleCallback.tsx` et `MfaVerificationPage.tsx` redirigent selon les rôles issus de `useRoles`/`UserRoles`, sans dépendre de chaînes `admin`/`super_admin`/`interim`/`company`/`agency` en dur.
- **Création utilisateur admin sans rôles inline** : `CreateUserPage.tsx` construit la liste des rôles proposés à partir de la configuration (admin/super_admin/interim/company/agency).
- **Constantes IAM synchronisées** : `apps/web/src/constants/iamConstants.ts` inclut désormais les valeurs `POSTULANT` pour refléter les constantes backend (`iam_constants.py`).
- **ValidationsList.tsx alignée sur la config** : les filtres « En attente/Approuvées/Refusées » consomment désormais les statuts issus de la configuration/référentiels au lieu des chaînes `pending/approved/rejected` en dur.
- **Documentation de progression mise à jour** : `REFACTORING_PROGRESS.md` reflète 15 fichiers refactorés (~44% du périmètre) dont les flux auth frontend, la création d'utilisateur, la page profil et les filtres de validations alignés sur la config.
- **Contrôles d'accès référentiels alignés IAM** : `auth-microservice/system_references_routes.py` n’utilise plus les rôles `admin`/`super_admin` en dur et s'appuie sur `cfg.get_admin_role` / `cfg.get_super_admin_role` pour sécuriser l'accès public aux référentiels.
- **Attribution de profils IAM sans valeurs en dur** : `auth-microservice/security_routes.py` mappe désormais les rôles issus de la configuration (`cfg`) vers les profils `IAMProfiles`, supprimant les chaînes inline `admin`/`super_admin`/`interim`/`company`/`commercial` lors de la création d'utilisateurs.
- **Profils utilisateur alignés IAM côté web** : la page profil (`ProfilePage.tsx`) et le widget de complétion (`ProfileCompletionWidget.tsx`) s'appuient sur `useRoles`/`useValidationTypes` pour sélectionner les formulaires et champs à afficher au lieu de valeurs en dur (`candidat`, `postulant`, `interim`, `company`, `collaborator`).
- **API profil typée sur les constantes** : `profileApi.ts` déclare désormais `profile_type` via `ValidationType`, garantissant la cohérence des types avec le backend.
- **Google OAuth sans rôles inline** : `auth-microservice/google_auth_routes.py` crée les profils `interim`/`company`/`admin`/`super_admin` à partir des rôles configurés au lieu de littéraux.
- **Permissions temporaires/IAM sans chaînes admin** : `auth-microservice/temporary_permissions_routes.py` et `auth-microservice/iam_routes.py` utilisent `cfg.get_admin_role`/`cfg.get_super_admin_role` pour sécuriser l'accès aux permissions, évitant les comparaisons en dur.

## Actions prioritaires restantes
1. **Externaliser les rôles/statuts auth** : déplacer les comparaisons en dur dans `apps/api/**/awana_auth_routes.py` vers la configuration (`config/base.yaml`).
2. **Centraliser les permissions mission** : consommer des listes de rôles configurées dans `apps/api/**/mission_routes.py` pour la création/publication/édition/lecture globale.
3. **Finaliser la paramétrisation des validations** : s'assurer que les statuts/types restants et les rôles validateurs sont tous lus depuis la config dans `apps/api/**/validation_routes.py`.
4. **Automatiser l'audit en CI** : exécuter `scripts/audit_hardcoded_values.py` sur chaque PR et échouer en cas de nouvelles occurrences.
5. **Préparer l'exposition mobile** : stabiliser un contrat API v1, ajouter pagination/filtrage systématiques, timeouts et rate limiting pour la résilience.

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
