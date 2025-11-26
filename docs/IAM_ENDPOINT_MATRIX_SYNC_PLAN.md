# Plan de synchronisation IAM (Matrix Backend ↔ Front)

Objectif : régénérer la matrice des endpoints backend avec les permissions attendues côté front, puis aligner la base IAM.

## Étapes recommandées
1) Régénérer la matrice
- Depuis la racine du repo :
  - `cd scripts`
  - `python3 audit_iam_advanced.py --output ../docs/IAM_ENDPOINT_MATRIX.json`
  - (ou) `python3 audit_permissions_alignment.py --output ../docs/IAM_ENDPOINT_MATRIX.json`
- Vérifier que chaque endpoint FastAPI porte bien la permission attendue (voir `IAM_ENDPOINT_MATRIX_UPDATE_NOTES.md` pour la liste des codes côté front).

2) Contrôler manuellement les endpoints critiques
- Missions : read/create/edit/delete (.all/.own), publish/archive/cancel, applications.* (shortlist/reject/send_to_client).
- Besoins : read/create/edit/delete (.all/.own), submit.own, validate.all.
- Documents : read/create/delete/download/verify/view_cv (.own/.all).
- Users/IAM : users.* (read/manage/status/delete/import/reset_*), iam.groups.manage / iam.profiles.manage, security.email_domains.manage.
- Config/Refs/Flags/Emails/Rules/Locations : flags.manage, references.manage, config.manage, admin.settings|locations.manage, forms.enterprise.manage, emails.configure/manage_templates/read_history/test, rules.manage.

3) Aligner la base IAM
- Si besoin, exécuter le seed complet :
  - `cd scripts`
  - `python3 init_db_unified.py`
  - (optionnel) `python3 seed_new_permissions_and_bundles.py` ou scripts de migration si des codes sont absents.
- Vérifier en base que les permissions/bundles/profils contiennent bien les codes listés dans `IAM_ENDPOINT_MATRIX_UPDATE_NOTES.md`.

4) Validation
- Relancer l’audit (`audit_iam_advanced.py`) et comparer avec `IAM_ENDPOINT_MATRIX.json`.
- Smoke-tests multi-rôles (admin, commercial, entreprise, candidat/interim, lecture-only) pour s’assurer que les pages gardées côté front correspondent aux guards backend.

## Livrables à mettre à jour
- `docs/IAM_ENDPOINT_MATRIX.json` : replacer par la sortie du script d’audit.
- `docs/IAM_GUARDS_IMPLEMENTATION_REPORT.md` : déjà liste les gardes front.
- `docs/IAM_ENDPOINT_MATRIX_UPDATE_NOTES.md` : liste des permissions attendues côté front pour contrôle backend.
