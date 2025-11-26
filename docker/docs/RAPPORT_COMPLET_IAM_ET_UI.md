# Rapport complet — IAM, UI/UX, Guards & Endpoints

## 1. Synthèse globale
- Alignement IAM front/back : permissions .own/.all, bundles, profils système, routes proxifiées, normalisation des codes (points vs underscores).
- Durcissement sécurité : guards frontend sur CTA (missions, besoins, entreprises, documents, config/refs/flags/emails/règles), guards backend (FastAPI) via `require_permission`.
- Expérience UI : sidebar harmonisée (thèmes dynamiques, fluidité, auto-ajustement hauteur), Layout aligné, pages Users avec actions rapides, filtres dynamiques, modales affinées.
- Gestion rétention/suppression : front passe par archive avec rétention, normalisation des routes IAM users, support des politiques de rétention.

## 2. Backend (FastAPI auth-microservice)
- Routes auditées/alignées (extraits) :
  - IAM : `iam_routes.py`, `iam_unified_routes.py`, `iam_bundles_routes.py`, `iam_advanced_routes.py`, `iam_audit_routes.py`, `iam_expiration_routes.py`, `iam_cache_routes.py`.
  - Users : `awana_auth_routes.py` (CRUD, stats), `user_archive_routes.py` (archive + purge rétention), `user_detail_routes.py`, `bulk_operations_routes.py`, `admin_email_verification_routes.py`.
  - Missions/Besoins/Entreprises : `mission_routes.py`, `besoin_routes.py`, `entreprise_routes.py`, `entreprise_form_config_routes.py`, `entreprise_grouping_routes.py`.
  - Documents : `documents_routes_v2.py` (download/upload/delete/verify/view_cv), vérification des scopes.
  - Config/Refs/Flags : `configuration_routes.py`, `version_routes.py`, `feature_flag_routes.py`, `system_references_routes.py`.
  - Support/Contracts/Notifications/Presence/Payroll : `support_routes.py`, `contract_routes.py`, `notification_routes.py`, `presence_routes.py`, `payroll_routes.py`.
- Normalisation permissions : usage de `IAMPermissions` (modern), pas de hardcode, scopes `.own/.all` lorsqu’applicable.
- Rétention : `user_archive_routes.py` applique `retention_days` (DB override ou YAML), archive -> `deletion_scheduled_at`, purge via `/purge/expired`.
- Proxy : `/api/config` / `/api/auth/config` normalisés côté front; IAM users `/api/iam/users` inclus via `main.py` (prefix `/api/iam/users`).

## 3. Frontend (React)
- Routing : refonte modulaire (`apps/web/src/routes/*.routes.tsx`, `RootLayout`, `SidebarResolver`, `SidebarUltimate`).
- Guards : partout sur CTA sensibles (missions, besoins, entreprises, documents, config/refs/flags/emails/règles, admin pages, modals). Vérifications `.own/.all` et permissions exactes (documents.view_cv.all, flags.manage/read, config.manage/read, references.manage/read, etc.).
- Pages clés :
  - Missions/Besoins/Applications : `MissionsListPageNew`, `MissionDetailPage`, `ApplicationsManagementPage`, `OffresPage`, `BesoinsPage`, `BesoinDetailPage`.
  - Admin : `UserManagementPage` (actions rapides, filtres dynamiques, archive via rétention), `ReferencesManagementPage`, `LocationManagementPage`, `EntrepriseFormConfigPage`, `FeatureFlagsPage`, `EmailSettings/Templates/History`, `BusinessRulesPage`, `ConfigurationVersionsPage`, `CountryConfigPage`.
  - IAM : `ProfilesManagementPage` (groupement par catégorie, protection profils système), `IAMControlPage`, `IAMAdminDashboard`, modales Create/Edit/Assign avec guards.
  - Profile/Permissions : `MyPermissionsSection` stabilisé, affichage des permissions effectives.
- Sidebar/UX : `SidebarUltimate` (thèmes dynamiques, fluidité, auto-height, hover/compact tooltips), Layout aligné avec topbar/breadcrumb, palettes synchronisées.
- Users (UI) : boutons icon-only alignés avec recherche, tabs Actifs/Archives/Super Admin sous la search, actions rapides contextuelles, modales réduites, filtres rôles/statuts dynamiques.

## 4. Données IAM, scripts et seeds
- Scripts ajoutés/mis à jour : `scripts/update_system_profiles.py` (profils système + candidat, permissions + permission_ids, bundles optionnels), `seed_new_permissions_and_bundles.py`, `assign_bundles_to_profile.py`.
- Plan de synchronisation : `docs/IAM_ENDPOINT_MATRIX_SYNC_PLAN.md` (commande `audit_iam_advanced.py`, update `IAM_ENDPOINT_MATRIX.json`, align DB via `init_db_unified.py` / `init_iam_from_config.py`).
- Notes de mapping : `docs/IAM_ENDPOINT_MATRIX_UPDATE_NOTES.md` (codes attendus par domaine), `docs/IAM_GUARDS_IMPLEMENTATION_REPORT.md` (résumé guards front).

## 5. Corrections réseau/proxy et normalisations front
- `baseQueryWithAuth` : normalisation `/api/auth/config -> /api/config`, `/api/auth/iam/users -> /api/iam/users`, fallback public config si pas de token, détection double `/api/api`.
- Users API : `baseUrl` corrigé (`/api`), endpoints `/auth/users/...` pour CRUD, `/iam/users/{id}/archive` pour archivage avec motif.
- Erreurs résolues : 404/405 sur delete user (passage à archive), 401/404 config, doublons sidebar, hover manquants en thème light.

## 6. Points d’attention / prochaines étapes
- Régénérer la matrice IAM : `python3 auth-microservice/scripts/audit_iam_advanced.py --output docs/IAM_ENDPOINT_MATRIX.json` puis appliquer via scripts init/seed si besoin.
- Vérifier les politiques de rétention dans `app_settings` (`security.user_retention_days`) si modification future.
- Recompiler/refresh front pour voir les derniers ajustements UI (users page).

## 7. Fichiers clés créés/mis à jour
- Backend : multiples routes FastAPI (cf. section 2), `main.py` inclut proxy/config/user_archive/iam.
- Front : `apps/web/src/features/...` (users, admin, missions/besoins, documents, IAM), `SidebarUltimate`, `baseQueryWithAuth`.
- Docs : `docs/IAM_ENDPOINT_MATRIX_SYNC_PLAN.md`, `docs/IAM_ENDPOINT_MATRIX_UPDATE_NOTES.md`, `docs/IAM_GUARDS_IMPLEMENTATION_REPORT.md`, `docs/IAM_ENDPOINT_MATRIX.json`, `docs/RAPPORT_COMPLET_IAM_ET_UI.md` (ce fichier).
- Scripts : `scripts/update_system_profiles.py`, `seed_new_permissions_and_bundles.py`, `assign_bundles_to_profile.py` (racine et auth-microservice).
