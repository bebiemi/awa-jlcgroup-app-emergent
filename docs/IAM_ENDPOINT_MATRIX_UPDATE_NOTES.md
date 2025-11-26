# Mise à jour de la matrice IAM (backend ↔ front)

Ce document liste les permissions désormais utilisées côté front et à synchroniser dans la matrice IAM backend (`docs/IAM_ENDPOINT_MATRIX.json` / audit IAM). Pour chaque domaine, vérifier que les endpoints FastAPI appliquent ces permissions (policy/guard) et mettre à jour la matrice en conséquence.

## Domaines et permissions attendues
- **Missions**
  - missions.read.all | missions.read.own | missions.browse
  - missions.create.all | missions.create.own
  - missions.edit.all | missions.edit.own
  - missions.delete.all | missions.delete.own
  - missions.publish.all (ou missions.manage.all)
  - missions.archive.all (ou missions.manage.all)
  - missions.cancel.all (ou missions.manage.all)
- **Applications (candidatures)**
  - applications.read.all
  - applications.manage | applications.manage_status
  - applications.shortlist
  - applications.send_to_client
  - applications.create | applications.create.own
- **Besoins**
  - besoins.read.all | besoins.read.own
  - besoins.create.all | besoins.create.own
  - besoins.edit.all | besoins.edit.own
  - besoins.delete.all | besoins.delete.own
  - besoins.submit.own
  - besoins.validate.all
- **Documents**
  - documents.read.all | documents.read.own
  - documents.create.all | documents.create.own
  - documents.delete.all | documents.delete.own
  - documents.download.all
  - documents.verify.all
  - documents.view_cv.all
- **Users / IAM**
  - users.read | users.manage
  - users.manage_status
  - users.delete
  - users.import | users.create
  - users.reset_mfa
  - users.reset_password
  - iam.groups.manage | iam.profiles.manage
  - security.email_domains.read | security.email_domains.manage
- **Config / Référentiels / Flags / Emails / Règles / Locations**
  - flags.read | flags.manage
  - references.read | references.manage
  - config.read | config.manage
  - admin.settings | locations.manage
  - forms.enterprise.manage
  - emails.read_config | emails.configure | emails.test
  - emails.manage_templates | emails.read_history
  - rules.read | rules.manage

## Actions à mener côté backend
1. **Re-générer la matrice** via l’audit IAM backend (script existant) pour inclure tous les endpoints FastAPI et mettre à jour `IAM_ENDPOINT_MATRIX.json`.
2. **Vérifier chaque endpoint** des domaines ci-dessus :
   - Le décorateur/policy doit appliquer la permission attendue (ou une policy équivalente) sans hardcode.
   - Les scopes `.own/.all` doivent être cohérents avec la logique business.
3. **Mettre à jour la matrice** (`IAM_ENDPOINT_MATRIX.json`) avec les permissions exactes après vérification backend.
4. **Aligner DB IAM** si nécessaire : s’assurer que les codes de permissions existent (cf. seed des permissions/bundles) et que les rôles/bundles sont attribués correctement.

## Contrôle final
- Exécuter l’audit IAM backend (scripts `audit_iam_*.py` si disponibles) et comparer la sortie avec les permissions ci-dessus.
- S’assurer que toutes les pages front gardées utilisent des permissions présentes et appliquées côté API.

