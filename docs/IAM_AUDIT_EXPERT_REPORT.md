# 🔒 AUDIT IAM EXPERT - Rapport Complet

**Date:** 92389.650435398
**Endpoints analysés:** 378
**Issues détectés:** 323

## 📊 Vue d'Ensemble

### Protection IAM
- ✅ Endpoints avec permissions IAM: 152 (40.2%)
- ⚠️  Endpoints avec auth seulement: 110 (29.1%)
- ❌ Endpoints non protégés: 116 (30.7%)

### Issues par Type

- **MISSING_SCOPE**: 149
- **AUTH_ONLY_MODIFICATION**: 55
- **HARDCODED_PERMISSION**: 49
- **MISSING_PERMISSION**: 49
- **HARDCODED_ROLE_CHECK**: 17
- **NO_PROTECTION**: 4

## 🔴 ISSUES BLOQUANTS (Action Immédiate Requise)

### POST /{user_id}/password/admin-update
**Fichier:** `user_detail_routes.py` (ligne 516)

**Type:** NO_PROTECTION

**État actuel:** Aucune protection IAM

**Attendu:** require_permission('users.create')

**Scope attendu:** `organization`

**Action:**
```python
Ajouter: Depends(require_permission('users.create', scope='organization'))
```

**Justification:** Endpoint critique expose sans protection

**Impact:** SECURITE - Acces non autorise possible

---

### GET /admin
**Fichier:** `validation_routes.py` (ligne 66)

**Type:** NO_PROTECTION

**État actuel:** Aucune protection IAM

**Attendu:** require_permission('admin.read')

**Scope attendu:** `all`

**Action:**
```python
Ajouter: Depends(require_permission('admin.read', scope='all'))
```

**Justification:** Endpoint critique expose sans protection

**Impact:** SECURITE - Acces non autorise possible

---

### POST /admin/{validation_id}/approve
**Fichier:** `validation_routes.py` (ligne 97)

**Type:** NO_PROTECTION

**État actuel:** Aucune protection IAM

**Attendu:** require_permission('admin.create')

**Scope attendu:** `all`

**Action:**
```python
Ajouter: Depends(require_permission('admin.create', scope='all'))
```

**Justification:** Endpoint critique expose sans protection

**Impact:** SECURITE - Acces non autorise possible

---

### POST /admin/{validation_id}/reject
**Fichier:** `validation_routes.py` (ligne 186)

**Type:** NO_PROTECTION

**État actuel:** Aucune protection IAM

**Attendu:** require_permission('admin.create')

**Scope attendu:** `all`

**Action:**
```python
Ajouter: Depends(require_permission('admin.create', scope='all'))
```

**Justification:** Endpoint critique expose sans protection

**Impact:** SECURITE - Acces non autorise possible

---

## 🟠 ISSUES IMPORTANTS

### POST /send
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `email_verification_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('send.create')

---

### POST /resend
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `email_verification_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('resend.create')

---

### GET /settings
**Type:** HARDCODED_PERMISSION | **Fichier:** `email_settings_routes.py`

**Problème:** Permission hardcodée: ['emails.read_config']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

### GET /settings
**Type:** MISSING_PERMISSION | **Fichier:** `email_settings_routes.py`

**Problème:** Permission référencée mais absente: emails.read_config

**Action:** Ajouter dans /app/config/iam_config.yaml:
  - code: emails.read_config
    name: '...'

---

### PUT /settings
**Type:** HARDCODED_PERMISSION | **Fichier:** `email_settings_routes.py`

**Problème:** Permission hardcodée: ['emails.configure']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

### PUT /settings
**Type:** MISSING_PERMISSION | **Fichier:** `email_settings_routes.py`

**Problème:** Permission référencée mais absente: emails.configure

**Action:** Ajouter dans /app/config/iam_config.yaml:
  - code: emails.configure
    name: '...'

---

### DELETE /settings
**Type:** HARDCODED_PERMISSION | **Fichier:** `email_settings_routes.py`

**Problème:** Permission hardcodée: ['emails.configure']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

### DELETE /settings
**Type:** MISSING_PERMISSION | **Fichier:** `email_settings_routes.py`

**Problème:** Permission référencée mais absente: emails.configure

**Action:** Ajouter dans /app/config/iam_config.yaml:
  - code: emails.configure
    name: '...'

---

### POST /{mission_id}/publish
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `mission_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('{mission_id}.create')

---

### POST /{mission_id}/apply
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `mission_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('{mission_id}.create')

---

### PUT /applications/{application_id}
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `mission_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('applications.update.all')

---

### POST /applications/{application_id}/shortlist
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `mission_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('applications.create')

---

### POST /applications/{application_id}/upload-medical
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `mission_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('applications.create')

---

### PATCH /me
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `presence_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('documents.edit')

---

### POST /activity
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `presence_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('activity.create')

---

### POST /tickets
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `support_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('tickets.create')

---

### POST /tickets/{ticket_id}/messages
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `support_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('tickets.create')

---

### PATCH /tickets/{ticket_id}/close
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `support_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('tickets.edit')

---

### GET /admin/tickets
**Type:** HARDCODED_ROLE_CHECK | **Fichier:** `support_routes.py`

**Problème:** Vérification de rôle hardcodée: admin

**Action:** Remplacer if role in roles par require_permission

---

### PATCH /admin/tickets/{ticket_id}
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `support_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('admin.edit')

---

### PATCH /admin/tickets/{ticket_id}
**Type:** HARDCODED_ROLE_CHECK | **Fichier:** `support_routes.py`

**Problème:** Vérification de rôle hardcodée: admin

**Action:** Remplacer if role in roles par require_permission

---

### POST /admin/tickets/{ticket_id}/messages
**Type:** AUTH_ONLY_MODIFICATION | **Fichier:** `support_routes.py`

**Problème:** Authentification seulement (get_current_user)

**Action:** Remplacer get_current_user par require_permission('admin.create')

---

### POST /admin/tickets/{ticket_id}/messages
**Type:** HARDCODED_ROLE_CHECK | **Fichier:** `support_routes.py`

**Problème:** Vérification de rôle hardcodée: admin

**Action:** Remplacer if role in roles par require_permission

---

### POST /{validation_id}/attach-to-existing
**Type:** HARDCODED_PERMISSION | **Fichier:** `validation_routes.py`

**Problème:** Permission hardcodée: ['entreprises.link_existing']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

### POST /{validation_id}/attach-to-existing
**Type:** MISSING_PERMISSION | **Fichier:** `validation_routes.py`

**Problème:** Permission référencée mais absente: entreprises.link_existing

**Action:** Ajouter dans /app/config/iam_config.yaml:
  - code: entreprises.link_existing
    name: '...'

---

### POST /fields
**Type:** HARDCODED_PERMISSION | **Fichier:** `entreprise_form_config_routes.py`

**Problème:** Permission hardcodée: ['forms.enterprise.manage']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

### POST /fields
**Type:** MISSING_PERMISSION | **Fichier:** `entreprise_form_config_routes.py`

**Problème:** Permission référencée mais absente: forms.enterprise.manage

**Action:** Ajouter dans /app/config/iam_config.yaml:
  - code: forms.enterprise.manage
    name: '...'

---

### GET /fields/{field_id}
**Type:** HARDCODED_PERMISSION | **Fichier:** `entreprise_form_config_routes.py`

**Problème:** Permission hardcodée: ['forms.enterprise.update']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

### GET /fields/{field_id}
**Type:** MISSING_PERMISSION | **Fichier:** `entreprise_form_config_routes.py`

**Problème:** Permission référencée mais absente: forms.enterprise.update

**Action:** Ajouter dans /app/config/iam_config.yaml:
  - code: forms.enterprise.update
    name: '...'

---

### PATCH /fields/{field_id}
**Type:** HARDCODED_PERMISSION | **Fichier:** `entreprise_form_config_routes.py`

**Problème:** Permission hardcodée: ['forms.enterprise.update']

**Action:** Créer permission dans iam_config.yaml et relancer init_iam_from_config.py

---

## 📋 Matrice Complète des Endpoints

| Endpoint | Méthode | Protection | Permissions | Scope | Criticité | Issue |
|----------|---------|------------|-------------|-------|-----------|-------|
| `/{user_id}/password/admin-update` | POST | none | - | - | 🔴 BLOQUANT | NO_PROTECTION |
| `/admin` | GET | none | - | - | 🔴 BLOQUANT | NO_PROTECTION |
| `/admin/{validation_id}/approve` | POST | none | - | - | 🔴 BLOQUANT | NO_PROTECTION |
| `/admin/{validation_id}/reject` | POST | none | - | - | 🔴 BLOQUANT | NO_PROTECTION |
| `/send` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/resend` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{mission_id}/publish` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{mission_id}/apply` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/applications/{application_id}` | PUT | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/applications/{application_id}/shortlist` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/applications/{application_id}/upload-medical` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/activity` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/tickets` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/tickets/{ticket_id}/messages` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/tickets/{ticket_id}/close` | PATCH | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/admin/tickets` | GET | auth_only | - | - | 🟠 IMPORTANT | HARDCODED_ROLE_CHECK |
| `/admin/tickets/{ticket_id}` | PATCH | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION, HARDCODED_ROLE_CHECK |
| `/admin/tickets/{ticket_id}/messages` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION, HARDCODED_ROLE_CHECK |
| `/me` | PUT | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/documents` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/documents/{document_id}` | DELETE | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{experience_id}` | PUT | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{experience_id}` | DELETE | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/check-permission` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/users/{user_id}/sync-legacy-roles` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION, HARDCODED_ROLE_CHECK |
| `/forms` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/forms/{form_type}` | DELETE | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/workflows` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{besoin_id}` | PATCH | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{besoin_id}/submit` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{besoin_id}/status` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{besoin_id}/comments` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{besoin_id}/jlc-analysis` | PATCH | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{besoin_id}/convert-to-mission` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/active` | GET | auth_only | - | - | 🟠 IMPORTANT | HARDCODED_ROLE_CHECK |
| `/logout` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{key}` | PATCH | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{key}` | DELETE | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/manual-verify` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/audit/all` | GET | auth_only | - | - | 🟠 IMPORTANT | HARDCODED_ROLE_CHECK |
| `/status` | GET | auth_only | - | - | 🟠 IMPORTANT | HARDCODED_ROLE_CHECK |
| `/{notification_id}/read` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/mark-all-read` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/{temp_perm_id}/extend` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION, HARDCODED_ROLE_CHECK |
| `/{temp_perm_id}/revoke` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION, HARDCODED_ROLE_CHECK |
| `/expiring-soon` | GET | auth_only | - | - | 🟠 IMPORTANT | HARDCODED_ROLE_CHECK |
| `/statistics` | GET | none | - | - | 🟠 IMPORTANT | HARDCODED_ROLE_CHECK |
| `/cleanup` | POST | none | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION, HARDCODED_ROLE_CHECK |
| `/setup/totp` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/setup/totp/verify` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/setup/email` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/setup/sms` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/setup/sms/verify` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/backup-codes/regenerate` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/method/{method}` | DELETE | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/me` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/me/avatar` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/mark-read` | POST | auth_only | - | - | 🟠 IMPORTANT | AUTH_ONLY_MODIFICATION |
| `/settings` | GET | single_permission | emails.read_config | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/settings` | PUT | single_permission | emails.configure | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/settings/test` | POST | single_permission | emails.test | - | 🟡 MINEUR | MISSING_SCOPE |
| `/settings` | DELETE | single_permission | emails.configure | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/admin/backfill-application-history` | POST | single_permission | applications.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/me` | PATCH | auth_only | - | - | 🟠 IMPORTANT | MISSING_SCOPE, AUTH_ONLY_MODIFICATION |
| `/stats` | GET | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/my-validation` | GET | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{validation_id}` | GET | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{validation_id}/approve` | POST | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{validation_id}/reject` | POST | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{validation_id}/check-representant` | GET | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/representant/{user_id}/details` | GET | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{validation_id}/attach-to-existing` | POST | single_permission | entreprises.link_existing | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/{validation_id}/assign` | POST | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{validation_id}/add-country` | POST | single_permission | validations.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/fields` | POST | single_permission | forms.enterprise.manage | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/fields/{field_id}` | GET | single_permission | forms.enterprise.update | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/fields/{field_id}` | PATCH | single_permission | forms.enterprise.update | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/fields/{field_id}` | DELETE | single_permission | forms.enterprise.manage | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/fields/reorder` | POST | single_permission | forms.enterprise.update | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/upload` | POST | single_permission | documents.create | - | 🟠 IMPORTANT | MISSING_SCOPE, AUTH_ONLY_MODIFICATION |
| `/` | GET | single_permission | documents.read | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{document_id}` | GET | single_permission | documents.read | - | 🟡 MINEUR | MISSING_SCOPE |
| `/{document_id}` | DELETE | single_permission | documents.delete | - | 🟠 IMPORTANT | MISSING_SCOPE, AUTH_ONLY_MODIFICATION |
| `/{document_id}` | PATCH | single_permission | documents.update | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/{document_id}/download` | GET | single_permission | documents.download | - | 🟡 MINEUR | MISSING_SCOPE |
| `/admin/all` | GET | single_permission | documents.read.all | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/admin/{document_id}/verify` | PATCH | single_permission | documents.verify | - | 🟠 IMPORTANT | MISSING_PERMISSION, MISSING_SCOPE, HARDCODED_PERMISSION |
| `/permissions` | GET | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/profiles` | GET | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/profiles/{profile_id}` | GET | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/profiles` | POST | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/profiles/{profile_id}` | PUT | single_permission | users.manage | - | 🟠 IMPORTANT | MISSING_SCOPE, MISSING_PERMISSION, HARDCODED_PERMISSION |
| `/profiles/{profile_id}` | DELETE | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/groups` | GET | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/groups/{group_id}` | GET | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/groups` | POST | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/groups/{group_id}` | PUT | single_permission | users.manage | - | 🟠 IMPORTANT | MISSING_SCOPE, MISSING_PERMISSION, HARDCODED_PERMISSION |
| `/groups/{group_id}` | DELETE | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/groups/{group_id}/members/{user_id}` | POST | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
| `/groups/{group_id}/members/{user_id}` | DELETE | single_permission | users.manage | - | 🟡 MINEUR | MISSING_SCOPE |
