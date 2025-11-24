# 🔒 Audit de Sécurité des Endpoints
**Date:** 90853.314251535
**Routes analysées:** 378
**Problèmes détectés:** 235

## 📊 Statistiques
- Routes protégées: 241 (63.8%)
- Routes non protégées: 137 (36.2%)

### Par Sévérité
- 🔴 CRITICAL: 10
- 🟠 HIGH: 157
- 🟡 MEDIUM: 68

## 🔴 Problèmes CRITIQUES

### GET /{user_id}/profiles
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `Créer: profiles.read`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### POST /{user_id}/profiles
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `Créer: profiles.create`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### DELETE /{user_id}/profiles/{profile_id}
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `Créer: profiles.delete`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### POST /{user_id}/password/admin-update
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `Créer: password.create`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### GET /users/in-workflow
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `users.view.all (ou créer users.read)`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### PATCH /{user_id}/archive
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `Créer: archive.edit`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### GET /admin
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `admin.dashboard (ou créer admin.read)`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### POST /admin/{validation_id}/approve
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `admin.dashboard (ou créer admin.create)`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### POST /admin/{validation_id}/reject
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `admin.dashboard (ou créer admin.create)`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

### GET /users/{user_id}/audit
**Problème:** Route critique sans protection

**État actuel:** `Aucune protection`

**Recommandation:** `users.view.all (ou créer users.read)`

**Justification:** Cette route manipule des données sensibles et doit être protégée

---

## 🟠 Problèmes HIGH

### POST /send
**Problème:** Route de modification sans permission spécifique

**Recommandation:** `Créer: send.create`

---

### POST /verify
**Problème:** Route sans protection

**Recommandation:** `Créer: verify.create`

---

### POST /resend
**Problème:** Route de modification sans permission spécifique

**Recommandation:** `Créer: resend.create`

---

### GET /settings
**Problème:** Permission inexistante: emails.read_config

**Recommandation:** `Utiliser: emails.send (ou créer emails.read_config)`

---

### PUT /settings
**Problème:** Permission inexistante: emails.configure

**Recommandation:** `Utiliser: emails.send (ou créer emails.configure)`

---

### DELETE /settings
**Problème:** Permission inexistante: emails.configure

**Recommandation:** `Utiliser: emails.send (ou créer emails.configure)`

---

### POST /search
**Problème:** Route sans protection

**Recommandation:** `Créer: search.create`

---

### POST /cleanup
**Problème:** Route sans protection

**Recommandation:** `Créer: cleanup.create`

---

### POST /batch-matching
**Problème:** Route sans protection

**Recommandation:** `Créer: batch-matching.create`

---

### PUT /{mission_id}
**Problème:** Route sans protection

**Recommandation:** `Définir une permission appropriée`

---

## 📋 Tableau de Synthèse

| Route | Méthode | Protection Actuelle | Permissions | Criticité | Action |
|-------|---------|-------------------|-------------|-----------|--------|
| `/{user_id}/profiles` | GET | Aucune protection | - | 🔴 CRITICAL | Créer: profiles.read |
| `/{user_id}/profiles` | POST | Aucune protection | - | 🔴 CRITICAL | Créer: profiles.create |
| `/{user_id}/profiles/{profile_id}` | DELETE | Aucune protection | - | 🔴 CRITICAL | Créer: profiles.delete |
| `/{user_id}/password/admin-update` | POST | Aucune protection | - | 🔴 CRITICAL | Créer: password.create |
| `/users/in-workflow` | GET | Aucune protection | - | 🔴 CRITICAL | users.view.all (ou créer users.read) |
| `/{user_id}/archive` | PATCH | Aucune protection | - | 🔴 CRITICAL | Créer: archive.edit |
| `/admin` | GET | Aucune protection | - | 🔴 CRITICAL | admin.dashboard (ou créer admin.read) |
| `/admin/{validation_id}/approve` | POST | Aucune protection | - | 🔴 CRITICAL | admin.dashboard (ou créer admin.create) |
| `/admin/{validation_id}/reject` | POST | Aucune protection | - | 🔴 CRITICAL | admin.dashboard (ou créer admin.create) |
| `/users/{user_id}/audit` | GET | Aucune protection | - | 🔴 CRITICAL | users.view.all (ou créer users.read) |
| `/send` | POST | Authentification seulement | - | 🟠 HIGH | Créer: send.create |
| `/verify` | POST | Public | - | 🟠 HIGH | Créer: verify.create |
| `/resend` | POST | Authentification seulement | - | 🟠 HIGH | Créer: resend.create |
| `/settings` | GET | emails.read_config | - | 🟠 HIGH | Utiliser: emails.send (ou créer emails.read_config) |
| `/settings` | PUT | emails.configure | - | 🟠 HIGH | Utiliser: emails.send (ou créer emails.configure) |
| `/settings` | DELETE | emails.configure | - | 🟠 HIGH | Utiliser: emails.send (ou créer emails.configure) |
| `/actions/{action_type}` | GET | Public | - | 🟡 MEDIUM | Créer: actions.read |
| `/failed-actions` | GET | Public | - | 🟡 MEDIUM | Créer: failed-actions.read |
| `/security-alerts` | GET | Public | - | 🟡 MEDIUM | Créer: security-alerts.read |
| `/search` | POST | Public | - | 🟠 HIGH | Créer: search.create |
| `/statistics` | GET | Public | - | 🟡 MEDIUM | Créer: statistics.read |
| `/compliance-report` | GET | Public | - | 🟡 MEDIUM | Créer: compliance-report.read |
| `/cleanup` | POST | Public | - | 🟠 HIGH | Créer: cleanup.create |
| `/action-types` | GET | Public | - | 🟡 MEDIUM | Créer: action-types.read |
| `/severity-levels` | GET | Public | - | 🟡 MEDIUM | Créer: severity-levels.read |
| `/recommended` | GET | Public | - | 🟡 MEDIUM | Créer: recommended.read |
| `/batch-matching` | POST | Public | - | 🟠 HIGH | Créer: batch-matching.create |
| `/{mission_id}` | GET | Public | - | 🟡 MEDIUM | Définir une permission appropriée |
| `/{mission_id}` | PUT | Public | - | 🟠 HIGH | Définir une permission appropriée |
| `/{mission_id}` | DELETE | Public | - | 🟠 HIGH | Définir une permission appropriée |
| `/{mission_id}/publish` | POST | Authentification seulement | - | 🟠 HIGH | Créer: publish.create |
| `/{mission_id}/apply` | POST | Authentification seulement | - | 🟠 HIGH | Créer: apply.create |
| `/{mission_id}/applications` | GET | Public | - | 🟡 MEDIUM | applications.read |
| `/applications/{application_id}` | PUT | Authentification seulement | - | 🟠 HIGH | applications.read.all (ou créer applications.update) |
| `/applications/{application_id}/shortlist` | POST | Authentification seulement | - | 🟠 HIGH | applications.create |
| `/applications/{application_id}/upload-medical` | POST | Authentification seulement | - | 🟠 HIGH | applications.create |
| `/{mission_id}/matching` | GET | Public | - | 🟡 MEDIUM | Créer: matching.read |
| `/applications/me/{application_id}` | PATCH | Public | - | 🟠 HIGH | applications.read.all (ou créer applications.edit) |
| `/applications/me/{application_id}/cancel` | POST | Public | - | 🟠 HIGH | applications.create |
| `/applications/{application_id}/history` | GET | Public | - | 🟡 MEDIUM | applications.read |
| `/applications/{application_id}/timeline-stats` | GET | Public | - | 🟡 MEDIUM | applications.read |
| `/applications/my-applications/with-history` | GET | Public | - | 🟡 MEDIUM | applications.read |
| `/me` | PATCH | Authentification seulement | - | 🟠 HIGH | Créer: me.edit |
| `/activity` | POST | Authentification seulement | - | 🟠 HIGH | Créer: activity.create |
| `/tickets` | POST | Authentification seulement | - | 🟠 HIGH | Créer: tickets.create |
| `/tickets/{ticket_id}/messages` | POST | Authentification seulement | - | 🟠 HIGH | Créer: tickets.create |
| `/tickets/{ticket_id}/close` | PATCH | Authentification seulement | - | 🟠 HIGH | Créer: tickets.edit |
| `/admin/tickets/{ticket_id}` | PATCH | Authentification seulement | - | 🟠 HIGH | admin.dashboard (ou créer admin.edit) |
| `/admin/tickets/{ticket_id}/messages` | POST | Authentification seulement | - | 🟠 HIGH | admin.dashboard (ou créer admin.create) |
| `/{validation_id}/attach-to-existing` | POST | entreprises.link_existing | - | 🟠 HIGH | Utiliser: entreprises.view.all (ou créer entreprises.link_existing) |

## ✅ Exemples de Routes Bien Protégées

| Route | Méthode | Protection | Permissions |
|-------|---------|------------|-------------|
| `/settings` | GET | single_permission | emails.read_config |
| `/settings` | PUT | single_permission | emails.configure |
| `/settings/test` | POST | single_permission | emails.test |
| `/settings` | DELETE | single_permission | emails.configure |
| `/admin/backfill-application-history` | POST | single_permission | applications.manage |
| `/stats` | GET | single_permission | validations.manage |
| `/{validation_id}` | GET | single_permission | validations.manage |
| `/{validation_id}/approve` | POST | single_permission | validations.manage |
| `/{validation_id}/reject` | POST | single_permission | validations.manage |
| `/{validation_id}/check-representant` | GET | single_permission | validations.manage |
