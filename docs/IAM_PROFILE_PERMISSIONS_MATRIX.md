# 📋 Matrice des Permissions par Profil

**Total profils:** 26
**Total permissions disponibles:** 182

## 📑 Table des Matières

1. [Super Administrateur (super_admin)](#profil-1-super-admin)
2. [Administrateur (admin)](#profil-2-admin)
3. [Responsable RH (hr_manager)](#profil-3-hr-manager)
4. [Commercial (commercial)](#profil-4-commercial)
5. [Auditeur (profile_auditor)](#profil-5-profile-auditor)
6. [Admin Société (company_admin)](#profil-6-company-admin)
7. [Responsable d'Équipe (team_manager)](#profil-7-team-manager)
8. [Candidat (Legacy - Ne plus utiliser) (candidat_legacy)](#profil-8-candidat-legacy)
9. [Intérimaire (interim_user)](#profil-9-interim-user)
10. [Candidat (candidat)](#profil-10-candidat)
11. [Lecture Seule (read_only)](#profil-11-read-only)
12. [Gestionnaire Commercial (gestionnaire_commercial)](#profil-12-gestionnaire-commercial)
13. [Test Profil (test_profils)](#profil-13-test-profils)
14. [Test Profile (test_profile)](#profil-14-test-profile)
15. [Commerciales Custom (commercial_custom)](#profil-15-commercial-custom)
16. [Updated Test Profile (test_custom_profile)](#profil-16-test-custom-profile)
17. [Postulant (role.postulant)](#profil-17-role-postulant)
18. [Restreint (profile.restricted)](#profil-18-profile-restricted)
19. [Utilisateur Défaut 15j (profile.candidat_temp)](#profil-19-profile-candidat-temp)
20. [Candidat/Postulant (profile.candidat_confirmed)](#profil-20-profile-candidat-confirmed)
21. [Entreprise (profile.company)](#profil-21-profile-company)
22. [Commercial (profile.commercial)](#profil-22-profile-commercial)
23. [Paie (profile.payroll)](#profil-23-profile-payroll)
24. [RRH (profile.hr_manager)](#profil-24-profile-hr-manager)
25. [Administrateur (profile.admin)](#profil-25-profile-admin)
26. [Super Administrateur (profile.super_admin)](#profil-26-profile-super-admin)

---

## Profil 1: Super Administrateur

**Code:** `super_admin`

**Description:** Accès complet à toutes les fonctionnalités

**Priorité:** 1000

**Permissions directes:** 182

### ✅ Total Permissions Effectives: 182

### 📊 Permissions par Catégorie

#### BESOINS (21 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `besoins.comment` | Commenter besoins | organization | Commenter besoins |
| `besoins.comment.all` | Commenter tous les besoins | all | Commenter tous les besoins |
| `besoins.convert_to_mission` | Convertir en mission | organization | Convertir en mission |
| `besoins.create` | Créer besoins | organization | Créer besoins |
| `besoins.create.all` | Créer besoins (tous) | all | Créer besoins (tous) |
| `besoins.create.own` | Créer ses besoins | own | Créer ses besoins |
| `besoins.delete` | Supprimer besoins | organization | Supprimer besoins |
| `besoins.delete.all` | Supprimer tous les besoins | all | Supprimer tous les besoins |
| `besoins.delete.own` | Supprimer ses besoins | own | Supprimer ses besoins |
| `besoins.edit` | Éditer besoins | organization | Éditer besoins |
| `besoins.edit.all` | Éditer tous les besoins | all | Éditer tous les besoins |
| `besoins.edit.own` | Éditer ses besoins | own | Éditer ses besoins |
| `besoins.read` | Lire besoins | organization | Lire besoins |
| `besoins.read.all` | Lire tous les besoins | all | Lire tous les besoins |
| `besoins.read.own` | Lire ses besoins | own | Lire ses besoins |
| `besoins.submit` | Soumettre besoins | organization | Soumettre besoins |
| `besoins.submit.own` | Soumettre ses besoins | own | Soumettre ses besoins |
| `besoins.validate` | Valider besoins | organization | Valider besoins |
| `besoins.validate.all` | Valider tous les besoins | all | Valider tous les besoins |
| `besoins.view.all` | Voir tous les besoins | all | Voir tous les besoins |
| `besoins.view.own` | Voir ses besoins | own | Voir ses besoins |

#### MISSIONS (21 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.archive` | Archiver une mission | organization | Archiver une mission |
| `missions.assign` | Assigner une mission | organization | Assigner une mission |
| `missions.browse` | Naviguer missions | organization | Naviguer missions |
| `missions.cancel` | Annuler une mission | organization | Annuler une mission |
| `missions.create` | Créer missions (générique) | organization | Créer missions (générique) |
| `missions.create.all` | Créer missions (toutes) | all | Créer missions (toutes) |
| `missions.create.own` | Créer ses missions | own | Créer ses missions |
| `missions.delete` | Supprimer missions | organization | Supprimer missions |
| `missions.delete.all` | Supprimer toutes les missions | all | Supprimer toutes les missions |
| `missions.delete.own` | Supprimer ses missions | own | Supprimer ses missions |
| `missions.edit.all` | Éditer toutes les missions | all | Éditer toutes les missions |
| `missions.edit.own` | Éditer ses missions | own | Éditer ses missions |
| `missions.manage` | Gérer missions | organization | Gérer missions |
| `missions.manage.all` | Gérer toutes les missions | all | Gérer toutes les missions |
| `missions.publish` | Publier une mission | organization | Publier une mission |
| `missions.read` | Lire missions (générique) | organization | Lire missions (générique) |
| `missions.read.all` | Lire toutes les missions | all | Lire toutes les missions |
| `missions.read.own` | Lire ses missions | own | Lire ses missions |
| `missions.reject` | Rejeter une mission | organization | Rejeter une mission |
| `missions.update` | Mettre à jour missions | organization | Mettre à jour missions |
| `missions.validate` | Valider une mission | organization | Valider une mission |

#### USERS (19 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `users.archive` | Archiver un utilisateur | organization | Archiver un utilisateur |
| `users.block` | Bloquer un utilisateur | organization | Bloquer un utilisateur |
| `users.create` | Créer utilisateurs | organization | Créer utilisateurs |
| `users.delete` | Suppression logique | organization | Suppression logique |
| `users.delete.all` | Supprimer utilisateurs | all | Supprimer utilisateurs |
| `users.delete_hard` | Suppression définitive | organization | Suppression définitive |
| `users.edit.all` | Éditer tous les utilisateurs | all | Éditer tous les utilisateurs |
| `users.edit.own` | Éditer son profil | own | Éditer son profil |
| `users.manage` | Gérer utilisateurs | organization | Gérer utilisateurs |
| `users.manage_status` | Gérer statut utilisateurs | organization | Gérer statut utilisateurs |
| `users.manage_status.all` | Gérer statut de tous | all | Gérer statut de tous |
| `users.read.all` | Lire tous les utilisateurs | all | Lire tous les utilisateurs |
| `users.reset_mfa` | Réinitialiser MFA | organization | Réinitialiser MFA |
| `users.reset_mfa.all` | Réinitialiser MFA de tous | all | Réinitialiser MFA de tous |
| `users.reset_password` | Réinitialiser mots de passe | organization | Réinitialiser mots de passe |
| `users.restore` | Restaurer un utilisateur | organization | Restaurer un utilisateur |
| `users.unblock` | Débloquer un utilisateur | organization | Débloquer un utilisateur |
| `users.view.all` | Voir tous les utilisateurs | all | Voir tous les utilisateurs |
| `users.view.own` | Voir son profil utilisateur | own | Voir son profil utilisateur |

#### IAM (18 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `iam.access_control.manage` | Gérer contrôle d'accès | organization | Gérer contrôle d'accès |
| `iam.access_control.read` | Lire contrôle d'accès | organization | Lire contrôle d'accès |
| `iam.assign_permissions` | Assigner permissions | organization | Assigner permissions |
| `iam.audit` | Auditer IAM | organization | Auditer IAM |
| `iam.groups.create` | Créer groupes IAM | organization | Créer groupes IAM |
| `iam.groups.delete` | Supprimer groupes IAM | organization | Supprimer groupes IAM |
| `iam.groups.edit` | Éditer groupes IAM | organization | Éditer groupes IAM |
| `iam.groups.read` | Lire groupes IAM | organization | Lire groupes IAM |
| `iam.manage` | Gérer IAM | organization | Gérer IAM |
| `iam.permissions.create` | Créer permissions IAM | organization | Créer permissions IAM |
| `iam.permissions.delete` | Supprimer permissions IAM | organization | Supprimer permissions IAM |
| `iam.permissions.edit` | Éditer permissions IAM | organization | Éditer permissions IAM |
| `iam.permissions.read` | Lire permissions IAM | organization | Lire permissions IAM |
| `iam.profiles.create` | Créer profils IAM | organization | Créer profils IAM |
| `iam.profiles.delete` | Supprimer profils IAM | organization | Supprimer profils IAM |
| `iam.profiles.edit` | Éditer profils IAM | organization | Éditer profils IAM |
| `iam.profiles.read` | Lire profils IAM | organization | Lire profils IAM |
| `iam.revoke_permissions` | Révoquer permissions | organization | Révoquer permissions |

#### ENTREPRISES (16 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `entreprises.approve` | Approuver entreprises | organization | Approuver entreprises |
| `entreprises.create` | Créer entreprises | organization | Créer entreprises |
| `entreprises.create.own` | Créer son entreprise | own | Créer son entreprise |
| `entreprises.delete` | Supprimer entreprises | organization | Supprimer entreprises |
| `entreprises.edit` | Éditer entreprises | organization | Éditer entreprises |
| `entreprises.edit.all` | Éditer toutes les entreprises | all | Éditer toutes les entreprises |
| `entreprises.edit.own` | Éditer son entreprise | own | Éditer son entreprise |
| `entreprises.grouping.approve` | Approuver regroupement | organization | Approuver regroupement |
| `entreprises.grouping.manage` | Gérer regroupement entreprises | organization | Gérer regroupement entreprises |
| `entreprises.grouping.reject` | Rejeter regroupement | organization | Rejeter regroupement |
| `entreprises.manage` | Gérer entreprises | organization | Gérer entreprises |
| `entreprises.read` | Lire entreprises | organization | Lire entreprises |
| `entreprises.read.all` | Lire toutes les entreprises | all | Lire toutes les entreprises |
| `entreprises.validate` | Valider entreprises | organization | Valider entreprises |
| `entreprises.view.all` | Voir toutes les entreprises | all | Voir toutes les entreprises |
| `entreprises.view.own` | Voir son entreprise | own | Voir son entreprise |

#### DOCUMENTS (15 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `documents.approve` | Approuver documents | organization | Approuver documents |
| `documents.create` | Créer documents | organization | Créer documents |
| `documents.delete` | Supprimer documents | organization | Supprimer documents |
| `documents.download` | Télécharger documents | organization | Télécharger documents |
| `documents.edit` | Éditer documents | organization | Éditer documents |
| `documents.manage` | Gérer documents | organization | Gérer documents |
| `documents.read` | Lire documents | organization | Lire documents |
| `documents.reject` | Rejeter documents | organization | Rejeter documents |
| `documents.upload_contracts.all` | Téléverser tous les contrats | all | Téléverser tous les contrats |
| `documents.upload_contracts.own` | Téléverser ses contrats | own | Téléverser ses contrats |
| `documents.upload_cv.own` | Téléverser son CV | own | Téléverser son CV |
| `documents.view_contracts.all` | Voir tous les contrats | all | Voir tous les contrats |
| `documents.view_contracts.own` | Voir ses contrats | own | Voir ses contrats |
| `documents.view_cv.all` | Voir tous les CV | all | Voir tous les CV |
| `documents.view_cv.own` | Voir son CV | own | Voir son CV |

#### APPLICATIONS (14 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `applications.create` | Créer candidatures | organization | Créer candidatures |
| `applications.create.all` | Créer candidatures (toutes) | all | Créer candidatures (toutes) |
| `applications.create.own` | Créer ses candidatures | own | Créer ses candidatures |
| `applications.delete.all` | Supprimer toutes les candidatures | all | Supprimer toutes les candidatures |
| `applications.delete.own` | Supprimer ses candidatures | own | Supprimer ses candidatures |
| `applications.edit.own` | Éditer ses candidatures | own | Éditer ses candidatures |
| `applications.manage` | Gérer candidatures | organization | Gérer candidatures |
| `applications.manage.all` | Gérer toutes les candidatures | all | Gérer toutes les candidatures |
| `applications.read` | Lire candidatures | organization | Lire candidatures |
| `applications.read.all` | Lire toutes les candidatures | all | Lire toutes les candidatures |
| `applications.read.own` | Lire ses candidatures | own | Lire ses candidatures |
| `applications.track` | Suivre candidatures | organization | Suivre candidatures |
| `applications.update.all` | Mettre à jour toutes les candidatures | all | Mettre à jour toutes les candidatures |
| `applications.update.own` | Mettre à jour ses candidatures | own | Mettre à jour ses candidatures |

#### PROFILE (12 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `profile.create` | Créer profils | organization | Créer profils |
| `profile.delete` | Supprimer profils | organization | Supprimer profils |
| `profile.edit.all` | Éditer tous les profils | all | Éditer tous les profils |
| `profile.edit.own` | Éditer son profil | own | Éditer son profil |
| `profile.manage` | Gérer profils | organization | Gérer profils |
| `profile.manage.all` | Gérer tous les profils | all | Gérer tous les profils |
| `profile.manage.own` | Gérer son profil | own | Gérer son profil |
| `profile.read` | Lire profils | organization | Lire profils |
| `profile.read.all` | Lire tous les profils | all | Lire tous les profils |
| `profile.read.own` | Lire son profil | own | Lire son profil |
| `profile.view.all` | Voir tous les profils | all | Voir tous les profils |
| `profile.view.own` | Voir son profil | own | Voir son profil |

#### EMAILS (7 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `email.settings.manage` | Gérer paramètres emails | organization | Gérer paramètres emails |
| `email.settings.read` | Lire paramètres emails | organization | Lire paramètres emails |
| `emails.manage` | Gérer emails | organization | Gérer emails |
| `emails.manage_templates` | Gérer templates emails | organization | Gérer templates emails |
| `emails.send` | Envoyer emails | organization | Envoyer emails |
| `emails.test` | Tester emails | organization | Tester emails |
| `emails.view_history` | Voir historique emails | organization | Voir historique emails |

#### RBAC (7 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `rbac.assign_roles` | Assigner rôles | organization | Assigner rôles |
| `rbac.manage` | Gérer RBAC | organization | Gérer RBAC |
| `rbac.revoke_roles` | Révoquer rôles | organization | Révoquer rôles |
| `rbac.roles.create` | Créer rôles | organization | Créer rôles |
| `rbac.roles.delete` | Supprimer rôles | organization | Supprimer rôles |
| `rbac.roles.edit` | Éditer rôles | organization | Éditer rôles |
| `rbac.roles.read` | Lire rôles | organization | Lire rôles |

#### ADMIN (6 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `admin.access` | Accès administration | organization | Accès administration |
| `admin.audit_logs` | Consulter les logs d'audit | organization | Consulter les logs d'audit |
| `admin.dashboard` | Dashboard administration | organization | Dashboard administration |
| `admin.rbac` | Gérer les rôles et permissions (RBAC) | organization | Gérer les rôles et permissions (RBAC) |
| `admin.settings` | Paramètres administration | organization | Paramètres administration |
| `admin.statistics` | Voir les statistiques | organization | Voir les statistiques |

#### DASHBOARD (6 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `dashboard.access` | Accéder au dashboard | organization | Accéder au dashboard |
| `dashboard.admin.access` | Accès dashboard admin | organization | Accès dashboard admin |
| `dashboard.candidat.access` | Accès dashboard candidat | organization | Accès dashboard candidat |
| `dashboard.commercial.access` | Accès dashboard commercial | organization | Accès dashboard commercial |
| `dashboard.company.access` | Accès dashboard entreprise | organization | Accès dashboard entreprise |
| `dashboard.customize.own` | Personnaliser son dashboard | own | Personnaliser son dashboard |

#### CONFIG (5 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `config.email_templates` | Gérer templates d'email | organization | Gérer templates d'email |
| `config.feature_flags` | Gérer feature flags | organization | Gérer feature flags |
| `config.manage` | Gérer configuration | organization | Gérer configuration |
| `config.read` | Lire configuration | organization | Lire configuration |
| `config.update` | Mettre à jour configuration | organization | Mettre à jour configuration |

#### FORMS (4 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `forms.create` | Créer formulaires | organization | Créer formulaires |
| `forms.edit` | Éditer formulaires | organization | Éditer formulaires |
| `forms.manage` | Gérer formulaires | organization | Gérer formulaires |
| `forms.read` | Lire formulaires | organization | Lire formulaires |

#### SECURITY (3 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `auth.mfa.manage` | Gérer MFA | organization | Gérer MFA |
| `security.email_domains.manage` | Gérer domaines emails | organization | Gérer domaines emails |
| `security.email_domains.read` | Lire domaines emails autorisés | organization | Lire domaines emails autorisés |

#### SYSTEM (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `*.*` | Toutes les permissions (SuperAdmin) | all | Toutes les permissions (SuperAdmin) |
| `system.feature_flags` | Gérer feature flags | organization | Gérer feature flags |

#### VALIDATIONS (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `validations.manage` | Gérer validations | organization | Gérer validations |
| `validations.manage.all` | Gérer toutes les validations | all | Gérer toutes les validations |

#### FLAGS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `flags.manage` | Gérer flags | organization | Gérer flags |

#### LOCATIONS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `locations.manage` | Gérer localisations | organization | Gérer localisations |

#### REFERENCES (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `references.manage` | Gérer référentiels | organization | Gérer référentiels |

#### RULES (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `rules.manage` | Gérer règles métier | organization | Gérer règles métier |

---

## Profil 2: Administrateur

**Code:** `admin`

**Description:** Administrateur avec accès étendu

**Priorité:** 900

**Permissions directes:** 31

**Bundles assignés:** 5

### 📦 Détail des Bundles

#### Bundle: Gérer les utilisateurs
**Code:** `users.manage`

**Permissions:** 8

- **users:** `users.archive`, `users.block`, `users.create`, `users.delete`, `users.edit.all`, `users.restore`, `users.unblock`, `users.view.all`

#### Bundle: Accès complet aux missions
**Code:** `missions.full_access`

**Permissions:** 9

- **missions:** `missions.archive`, `missions.assign`, `missions.cancel`, `missions.create`, `missions.publish`, `missions.read.all`, `missions.reject`, `missions.update`, `missions.validate`

#### Bundle: Gérer la configuration
**Code:** `config.manage`

**Permissions:** 4

- **config:** `config.email_templates`, `config.feature_flags`, `config.read`, `config.update`

#### Bundle: Accès administration
**Code:** `admin.access`

**Permissions:** 4

- **admin:** `admin.audit_logs`, `admin.dashboard`, `admin.rbac`, `admin.statistics`

#### Bundle: Gérer les entreprises
**Code:** `entreprises.manage`

**Permissions:** 6

- **entreprises:** `entreprises.approve`, `entreprises.create`, `entreprises.delete`, `entreprises.edit.all`, `entreprises.validate`, `entreprises.view.all`

### ✅ Total Permissions Effectives: 31

### 📊 Permissions par Catégorie

#### MISSIONS (9 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.archive` | Archiver une mission | organization | Archiver une mission |
| `missions.assign` | Assigner une mission | organization | Assigner une mission |
| `missions.cancel` | Annuler une mission | organization | Annuler une mission |
| `missions.create` | Créer missions (générique) | organization | Créer missions (générique) |
| `missions.publish` | Publier une mission | organization | Publier une mission |
| `missions.read.all` | Lire toutes les missions | all | Lire toutes les missions |
| `missions.reject` | Rejeter une mission | organization | Rejeter une mission |
| `missions.update` | Mettre à jour missions | organization | Mettre à jour missions |
| `missions.validate` | Valider une mission | organization | Valider une mission |

#### USERS (8 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `users.archive` | Archiver un utilisateur | organization | Archiver un utilisateur |
| `users.block` | Bloquer un utilisateur | organization | Bloquer un utilisateur |
| `users.create` | Créer utilisateurs | organization | Créer utilisateurs |
| `users.delete` | Suppression logique | organization | Suppression logique |
| `users.edit.all` | Éditer tous les utilisateurs | all | Éditer tous les utilisateurs |
| `users.restore` | Restaurer un utilisateur | organization | Restaurer un utilisateur |
| `users.unblock` | Débloquer un utilisateur | organization | Débloquer un utilisateur |
| `users.view.all` | Voir tous les utilisateurs | all | Voir tous les utilisateurs |

#### ENTREPRISES (6 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `entreprises.approve` | Approuver entreprises | organization | Approuver entreprises |
| `entreprises.create` | Créer entreprises | organization | Créer entreprises |
| `entreprises.delete` | Supprimer entreprises | organization | Supprimer entreprises |
| `entreprises.edit.all` | Éditer toutes les entreprises | all | Éditer toutes les entreprises |
| `entreprises.validate` | Valider entreprises | organization | Valider entreprises |
| `entreprises.view.all` | Voir toutes les entreprises | all | Voir toutes les entreprises |

#### ADMIN (4 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `admin.audit_logs` | Consulter les logs d'audit | organization | Consulter les logs d'audit |
| `admin.dashboard` | Dashboard administration | organization | Dashboard administration |
| `admin.rbac` | Gérer les rôles et permissions (RBAC) | organization | Gérer les rôles et permissions (RBAC) |
| `admin.statistics` | Voir les statistiques | organization | Voir les statistiques |

#### CONFIG (4 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `config.email_templates` | Gérer templates d'email | organization | Gérer templates d'email |
| `config.feature_flags` | Gérer feature flags | organization | Gérer feature flags |
| `config.read` | Lire configuration | organization | Lire configuration |
| `config.update` | Mettre à jour configuration | organization | Mettre à jour configuration |

---

## Profil 3: Responsable RH

**Code:** `hr_manager`

**Description:** Gestion RH et candidatures

**Priorité:** 600

**Permissions directes:** 6

### ✅ Total Permissions Effectives: 6

### 📊 Permissions par Catégorie

#### APPLICATIONS (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `applications.manage.all` | Gérer toutes les candidatures | all | Gérer toutes les candidatures |
| `applications.read.all` | Lire toutes les candidatures | all | Lire toutes les candidatures |

#### USERS (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `users.create` | Créer utilisateurs | organization | Créer utilisateurs |
| `users.view.all` | Voir tous les utilisateurs | all | Voir tous les utilisateurs |

#### DASHBOARD (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `dashboard.admin.access` | Accès dashboard admin | organization | Accès dashboard admin |

#### MISSIONS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.read.all` | Lire toutes les missions | all | Lire toutes les missions |

---

## Profil 4: Commercial

**Code:** `commercial`

**Description:** Gestion des missions et entreprises

**Priorité:** 500

**Permissions directes:** 15

**Bundles assignés:** 2

### 📦 Détail des Bundles

#### Bundle: Accès complet aux missions
**Code:** `missions.full_access`

**Permissions:** 9

- **missions:** `missions.archive`, `missions.assign`, `missions.cancel`, `missions.create`, `missions.publish`, `missions.read.all`, `missions.reject`, `missions.update`, `missions.validate`

#### Bundle: Gérer les entreprises
**Code:** `entreprises.manage`

**Permissions:** 6

- **entreprises:** `entreprises.approve`, `entreprises.create`, `entreprises.delete`, `entreprises.edit.all`, `entreprises.validate`, `entreprises.view.all`

### ✅ Total Permissions Effectives: 15

### 📊 Permissions par Catégorie

#### MISSIONS (9 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.archive` | Archiver une mission | organization | Archiver une mission |
| `missions.assign` | Assigner une mission | organization | Assigner une mission |
| `missions.cancel` | Annuler une mission | organization | Annuler une mission |
| `missions.create` | Créer missions (générique) | organization | Créer missions (générique) |
| `missions.publish` | Publier une mission | organization | Publier une mission |
| `missions.read.all` | Lire toutes les missions | all | Lire toutes les missions |
| `missions.reject` | Rejeter une mission | organization | Rejeter une mission |
| `missions.update` | Mettre à jour missions | organization | Mettre à jour missions |
| `missions.validate` | Valider une mission | organization | Valider une mission |

#### ENTREPRISES (6 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `entreprises.approve` | Approuver entreprises | organization | Approuver entreprises |
| `entreprises.create` | Créer entreprises | organization | Créer entreprises |
| `entreprises.delete` | Supprimer entreprises | organization | Supprimer entreprises |
| `entreprises.edit.all` | Éditer toutes les entreprises | all | Éditer toutes les entreprises |
| `entreprises.validate` | Valider entreprises | organization | Valider entreprises |
| `entreprises.view.all` | Voir toutes les entreprises | all | Voir toutes les entreprises |

---

## Profil 5: Auditeur

**Code:** `profile_auditor`

**Description:** Profil pour audit et conformité avec accès lecture seule

**Priorité:** 500

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 6: Admin Société

**Code:** `company_admin`

**Description:** Admin d'une société cliente

**Priorité:** 400

**Permissions directes:** 5

### ✅ Total Permissions Effectives: 5

### 📊 Permissions par Catégorie

#### ENTREPRISES (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `entreprises.edit.own` | Éditer son entreprise | own | Éditer son entreprise |
| `entreprises.view.own` | Voir son entreprise | own | Voir son entreprise |

#### APPLICATIONS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `applications.read.all` | Lire toutes les candidatures | all | Lire toutes les candidatures |

#### DASHBOARD (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `dashboard.company.access` | Accès dashboard entreprise | organization | Accès dashboard entreprise |

#### MISSIONS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.read.all` | Lire toutes les missions | all | Lire toutes les missions |

---

## Profil 7: Responsable d'Équipe

**Code:** `team_manager`

**Description:** Validation émargements et gestion groupe

**Priorité:** 400

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 8: Candidat (Legacy - Ne plus utiliser)

**Code:** `candidat_legacy`

**Description:** Consultation missions avant signature contrat

**Priorité:** 200

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 9: Intérimaire

**Code:** `interim_user`

**Description:** Utilisateur intérimaire/candidat

**Priorité:** 100

**Permissions directes:** 9

### ✅ Total Permissions Effectives: 9

### 📊 Permissions par Catégorie

#### APPLICATIONS (3 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `applications.create.own` | Créer ses candidatures | own | Créer ses candidatures |
| `applications.edit.own` | Éditer ses candidatures | own | Éditer ses candidatures |
| `applications.read.own` | Lire ses candidatures | own | Lire ses candidatures |

#### DOCUMENTS (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `documents.upload_cv.own` | Téléverser son CV | own | Téléverser son CV |
| `documents.view_cv.own` | Voir son CV | own | Voir son CV |

#### PROFILE (2 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `profile.edit.own` | Éditer son profil | own | Éditer son profil |
| `profile.view.own` | Voir son profil | own | Voir son profil |

#### DASHBOARD (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `dashboard.candidat.access` | Accès dashboard candidat | organization | Accès dashboard candidat |

#### MISSIONS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.read` | Lire missions (générique) | organization | Lire missions (générique) |

---

## Profil 10: Candidat

**Code:** `candidat`

**Description:** Profil pour les candidats (anciennement postulants)

**Priorité:** 100

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 11: Lecture Seule

**Code:** `read_only`

**Description:** Accès en lecture uniquement

**Priorité:** 50

**Permissions directes:** 4

### ✅ Total Permissions Effectives: 4

### 📊 Permissions par Catégorie

#### DASHBOARD (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `dashboard.access` | Accéder au dashboard | organization | Accéder au dashboard |

#### MISSIONS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `missions.read` | Lire missions (générique) | organization | Lire missions (générique) |

#### PROFILE (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `profile.view.own` | Voir son profil | own | Voir son profil |

#### USERS (1 permissions)

| Code | Nom | Scope | Description |
|------|-----|-------|-------------|
| `users.view.own` | Voir son profil utilisateur | own | Voir son profil utilisateur |

---

## Profil 12: Gestionnaire Commercial

**Code:** `gestionnaire_commercial`

**Description:** Gestion des entreprises et rapports

**Priorité:** 0

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 13: Test Profil

**Code:** `test_profils`

**Description:** Test Profil

**Priorité:** 0

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 14: Test Profile

**Code:** `test_profile`

**Description:** Test profile for IAM testing

**Priorité:** 0

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 15: Commerciales Custom

**Code:** `commercial_custom`

**Description:** Commerciales Custom

**Priorité:** 0

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 16: Updated Test Profile

**Code:** `test_custom_profile`

**Description:** Updated description

**Priorité:** 0

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 17: Postulant

**Code:** `role.postulant`

**Description:** Utilisateur postulant à des missions - Phase 3

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 18: Restreint

**Code:** `profile.restricted`

**Description:** Profil de sécurité minimum avec accès lecture seule. Assigné automatiquement à tous les utilisateurs (Zero Trust).

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 19: Utilisateur Défaut 15j

**Code:** `profile.candidat_temp`

**Description:** Profil temporaire pour nouveaux candidats. Expire après 15 jours glissants basés sur first_login_at. Downgrade automatique vers Restreint.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 20: Candidat/Postulant

**Code:** `profile.candidat_confirmed`

**Description:** Profil permanent pour candidats validés (email/téléphone/identité). Permissions identiques à Candidat 15j mais sans expiration.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 21: Entreprise

**Code:** `profile.company`

**Description:** Profil métier pour gestionnaires d'entreprise. Gérer entreprise, créer besoins, valider émargements. Ne peut pas modifier besoin soumis à JLC.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 22: Commercial

**Code:** `profile.commercial`

**Description:** Profil commercial avec permissions granulaires (own/all). Gestion missions, candidatures, besoins, entreprises. Accès CVTech.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 23: Paie

**Code:** `profile.payroll`

**Description:** Profil paie et facturation. Voir missions actives, gérer émargements, calculer paie, gérer facturation. Accès limité données entreprises.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 24: RRH

**Code:** `profile.hr_manager`

**Description:** Responsable Ressources Humaines. Gestion utilisateurs, recrutement, visites médicales, progression candidat→intérimaire, reporting RH.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 25: Administrateur

**Code:** `profile.admin`

**Description:** Profil administrateur système. Accès complet aux fonctionnalités d'administration. Conservation du profil existant.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## Profil 26: Super Administrateur

**Code:** `profile.super_admin`

**Description:** Profil super administrateur avec tous les pouvoirs. Conservation du profil existant.

**Priorité:** N/A

**Permissions directes:** 0

### ✅ Total Permissions Effectives: 0

---

## 📈 Matrice Comparative des Profils

| Profil | Code | Permissions Directes | Bundles | Total Effectif |
|--------|------|---------------------|---------|----------------|
| Super Administrateur | `super_admin` | 182 | 0 | **182** |
| Administrateur | `admin` | 31 | 5 | **31** |
| Responsable RH | `hr_manager` | 6 | 0 | **6** |
| Commercial | `commercial` | 15 | 2 | **15** |
| Auditeur | `profile_auditor` | 0 | 0 | **0** |
| Admin Société | `company_admin` | 5 | 0 | **5** |
| Responsable d'Équipe | `team_manager` | 0 | 0 | **0** |
| Candidat (Legacy - Ne plus utiliser) | `candidat_legacy` | 0 | 0 | **0** |
| Intérimaire | `interim_user` | 9 | 0 | **9** |
| Candidat | `candidat` | 0 | 0 | **0** |
| Lecture Seule | `read_only` | 4 | 0 | **4** |
| Gestionnaire Commercial | `gestionnaire_commercial` | 0 | 0 | **0** |
| Test Profil | `test_profils` | 0 | 0 | **0** |
| Test Profile | `test_profile` | 0 | 0 | **0** |
| Commerciales Custom | `commercial_custom` | 0 | 0 | **0** |
| Updated Test Profile | `test_custom_profile` | 0 | 0 | **0** |
| Postulant | `role.postulant` | 0 | 0 | **0** |
| Restreint | `profile.restricted` | 0 | 0 | **0** |
| Utilisateur Défaut 15j | `profile.candidat_temp` | 0 | 0 | **0** |
| Candidat/Postulant | `profile.candidat_confirmed` | 0 | 0 | **0** |
| Entreprise | `profile.company` | 0 | 0 | **0** |
| Commercial | `profile.commercial` | 0 | 0 | **0** |
| Paie | `profile.payroll` | 0 | 0 | **0** |
| RRH | `profile.hr_manager` | 0 | 0 | **0** |
| Administrateur | `profile.admin` | 0 | 0 | **0** |
| Super Administrateur | `profile.super_admin` | 0 | 0 | **0** |

