# Rapport de sécurisation IAM (front) – Guards & Permissions

## Contexte
Objectif : aligner l’ensemble des pages front sensibles sur le modèle IAM `resource.action.scope`, éviter toute action sans droit et tracer les décisions. Les gardes sont désormais appliqués dans le front pour les modules Admin, Missions/Besoins, Users, Documents, Config/Feature Flags/Emails/Référentiels, etc.

## Actions réalisées (front)
- **Missions / Besoins / Applications**
  - Missions list/new/detail : actions `create/read/edit/delete` en `.all|.own`, publish/cancel protégés (`missions.publish.all|missions.manage.all`, `missions.delete.*|missions.manage.all`).
  - Offres (candidat/interim) : accès via `missions.browse|read.*`; postuler via `applications.create|applications.create.own`.
  - ApplicationsManagementPage : lecture `applications.read.all|manage`; shortlist `applications.shortlist|manage`; reject/interview `applications.manage|manage_status`; envoi client `applications.send_to_client|manage`.
  - Besoin détail (entreprise) : édition brouillon `besoins.edit.*`; soumission `besoins.submit.own` (ou edit.all).

- **Users / IAM**
  - UserManagementPage : toutes les actions/CTA conditionnées (read/manage/status/delete/import/reset MFA/password).
  - User detail tabs : documents (read/verify/delete/download), permissions tab (`iam.groups.manage`/`iam.profiles.manage`), activity tab (`users.read|manage|audit.read`).

- **Documents**
  - MyDocuments (perso) : lecture `documents.read.own|all`; upload `documents.create.own`; delete `documents.delete.own`; download conditionné.
  - Documents (bibliothèque/all) : lecture `documents.read.all`; upload `documents.create.all`; delete `documents.delete.all`; download conditionné.
  - UserDocumentsTab : lecture `documents.read.all`; verify `documents.verify.all`; delete `documents.delete.all`; preview si `documents.download.all|read.all`.

- **Config / Référentiels / Flags**
  - FeatureFlagsPage : rendu si `flags.read|manage`; actions (toggle/update/delete/rollout/import/export/create) réservées à `flags.manage`.
  - ReferencesManagementPage : rendu si `references.read|manage`; bouton “Nouveau” si `references.manage`; catégories désactivées sans read.
  - CountryConfigPage : accès si `admin.settings|locations.manage`; init/default/gestion villes bloqués sans droit.
  - ConfigurationVersionsPage : rendu si `config.read|manage`; snapshot/rollback nécessitent `config.manage`.
  - EntrepriseFormConfigPage : accès/actions (create/delete/toggle champ) réservées à `forms.enterprise.manage`.
  - EmailSettingsPage : lecture `emails.read_config|configure`; update `emails.configure`; test `emails.test|configure`.
  - EmailTemplatesPage : lecture `emails.read_config|manage_templates`; init templates par défaut `emails.manage_templates`.
  - EmailHistoryPage : accès `emails.read_history`.
  - BusinessRulesPage : accès `rules.read|manage`; création/activation/suppression réservées à `rules.manage`.
  - EmailDomainsPage : lecture `security.email_domains.read|manage`; CRUD réservé à `security.email_domains.manage`.
  - LocationManagementPage : accès/actions (create/edit/delete/toggle) réservées à `locations.manage` (requêtes skip sans droit).

## Points de vigilance restant à vérifier
- Écrans Admin complémentaires (ex. EntreprisesManagement) si des CTA supplémentaires existent.
- Scénarios read-only : confirmer que les pages masquées/CTA désactivés correspondent bien aux droits attendus côté IAM.
- Tests manuels par rôle (admin, lecture-only, commercial, entreprise, candidat/interim) pour valider la visibilité des pages/CTA.

## Prochaines étapes suggérées
1. Vérifier EntreprisesManagement/ValidationsList si des actions supplémentaires nécessitent un guard explicite.
2. Faire un smoke test multi-rôles : navigation, ouverture de modals sensibles, actions CRUD critiques.
3. Synchroniser la matrice IAM backend avec cette configuration (IAM_ENDPOINT_MATRIX.json déjà présent). 
