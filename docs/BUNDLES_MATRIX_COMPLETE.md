# 📦 Matrice Complète des Bundles de Permissions

**Date de création:** 26 Novembre 2025  
**Version:** 1.0  
**Projet:** AWANA Auth & Business System

---

## 📖 Qu'est-ce qu'un Bundle ?

Un **bundle** est un **groupe logique de permissions atomiques** regroupées sous un identifiant unique. Au lieu d'assigner 50 permissions individuellement, vous assignez un bundle qui les contient toutes.

**Exemple:**
```javascript
missions.full_access = [
  "missions.read.all",
  "missions.create.all",
  "missions.edit.all",
  "missions.delete.all",
  "missions.publish",
  "missions.archive"
]
```

---

## 🗂️ Table des Matières

1. [Bundles Authentification & Utilisateurs](#1-bundles-authentification--utilisateurs)
2. [Bundles Missions & Candidatures](#2-bundles-missions--candidatures)
3. [Bundles Besoins RH](#3-bundles-besoins-rh)
4. [Bundles Émargements & Signatures](#4-bundles-émargements--signatures) ⭐ NOUVEAU
5. [Bundles Entreprises](#5-bundles-entreprises)
6. [Bundles Documents](#6-bundles-documents)
7. [Bundles Communication](#7-bundles-communication)
8. [Bundles Administration IAM](#8-bundles-administration-iam)
9. [Bundles Configuration Système](#9-bundles-configuration-système)
10. [Bundles Audit & Logs](#10-bundles-audit--logs)
11. [Matrice des Bundles par Profil](#matrice-des-bundles-par-profil)

---

## 1. Bundles Authentification & Utilisateurs

### 🔵 Bundle: `auth.basic`
**Description:** Authentification de base pour tous les utilisateurs  
**Permissions incluses:**
```javascript
[
  "auth.login",
  "auth.logout",
  "auth.refresh_token",
  "profile.view.own",
  "profile.edit.own"
]
```
**Assigné aux profils:** Tous

---

### 🔵 Bundle: `users.read`
**Description:** Lecture des utilisateurs (liste, détails)  
**Permissions incluses:**
```javascript
[
  "users.view.all",
  "users.view.own",
  "users.read.all",
  "users.read.own",
  "users.browse"
]
```
**Assigné aux profils:** Admin, HR Manager, Commercial

---

### 🔵 Bundle: `users.manage`
**Description:** Gestion complète des utilisateurs  
**Permissions incluses:**
```javascript
[
  "users.view.all",
  "users.create",
  "users.update",
  "users.delete",
  "users.archive",
  "users.restore",
  "users.block",
  "users.unblock",
  "users.password.reset",
  "users.roles.assign"
]
```
**Assigné aux profils:** Admin, Super Admin

---

### 🔵 Bundle: `users.hr_access`
**Description:** Accès RH aux profils utilisateurs  
**Permissions incluses:**
```javascript
[
  "users.view.all",
  "users.update",
  "users.profiles.view",
  "users.contracts.view",
  "users.documents.view"
]
```
**Assigné aux profils:** HR Manager

---

## 2. Bundles Missions & Candidatures

### 🟢 Bundle: `missions.read`
**Description:** Consultation des missions  
**Permissions incluses:**
```javascript
[
  "missions.view.all",
  "missions.view.own",
  "missions.read.all",
  "missions.read.own",
  "missions.browse"
]
```
**Assigné aux profils:** Tous (candidats voient seulement publiques)

---

### 🟢 Bundle: `missions.create`
**Description:** Création de missions  
**Permissions incluses:**
```javascript
[
  "missions.create.own",
  "missions.create.all",
  "missions.draft",
  "missions.save_template"
]
```
**Assigné aux profils:** Entreprise, Commercial, HR Manager

---

### 🟢 Bundle: `missions.manage`
**Description:** Gestion complète des missions  
**Permissions incluses:**
```javascript
[
  "missions.read.all",
  "missions.create.all",
  "missions.edit.all",
  "missions.delete.all",
  "missions.publish",
  "missions.unpublish",
  "missions.archive",
  "missions.cancel",
  "missions.assign",
  "missions.close"
]
```
**Assigné aux profils:** Commercial, HR Manager, Admin

---

### 🟢 Bundle: `applications.submit`
**Description:** Soumettre des candidatures  
**Permissions incluses:**
```javascript
[
  "applications.create",
  "applications.submit",
  "applications.withdraw",
  "applications.view.own",
  "documents.upload.cv"
]
```
**Assigné aux profils:** Candidat, Intérimaire

---

### 🟢 Bundle: `applications.review`
**Description:** Révision des candidatures  
**Permissions incluses:**
```javascript
[
  "applications.view.all",
  "applications.view.own",
  "applications.read.all",
  "applications.comment",
  "applications.shortlist",
  "applications.rate"
]
```
**Assigné aux profils:** Entreprise, Commercial, HR Manager

---

### 🟢 Bundle: `applications.manage`
**Description:** Gestion complète des candidatures  
**Permissions incluses:**
```javascript
[
  "applications.view.all",
  "applications.read.all",
  "applications.approve",
  "applications.reject",
  "applications.comment",
  "applications.shortlist",
  "applications.archive",
  "applications.export"
]
```
**Assigné aux profils:** Entreprise, Commercial, HR Manager

---

## 3. Bundles Besoins RH

### 🟡 Bundle: `besoins.create`
**Description:** Création de besoins RH  
**Permissions incluses:**
```javascript
[
  "besoins.create.own",
  "besoins.create.all",
  "besoins.draft",
  "besoins.submit.own"
]
```
**Assigné aux profils:** HR Manager, Commercial

---

### 🟡 Bundle: `besoins.manage`
**Description:** Gestion complète des besoins  
**Permissions incluses:**
```javascript
[
  "besoins.read.all",
  "besoins.create.all",
  "besoins.edit.all",
  "besoins.delete.all",
  "besoins.validate.all",
  "besoins.comment.all",
  "besoins.convert_to_mission"
]
```
**Assigné aux profils:** HR Manager, Admin

---

## 4. Bundles Émargements & Signatures ⭐

### 🔴 Bundle: `emargements.submit`
**Description:** Soumettre des émargements (heures travaillées)  
**Permissions incluses:**
```javascript
[
  "emargements.create.own",
  "emargements.submit.own",
  "emargements.view.own",
  "emargements.edit.own",
  "emargements.draft.own"
]
```
**Assigné aux profils:** Intérimaire

---

### 🔴 Bundle: `emargements.validate_interim`
**Description:** Validation intérimaire des émargements  
**Permissions incluses:**
```javascript
[
  "emargements.view.own",
  "emargements.sign.own",
  "emargements.submit.own",
  "emargements.comment.own"
]
```
**Assigné aux profils:** Intérimaire  
**Note:** Signature de l'intérimaire sur ses propres heures

---

### 🔴 Bundle: `emargements.validate_client`
**Description:** Validation client (entreprise) des émargements  
**Permissions incluses:**
```javascript
[
  "emargements.view.all",
  "emargements.view.own",
  "emargements.sign.all",
  "emargements.approve",
  "emargements.reject",
  "emargements.comment"
]
```
**Assigné aux profils:** Entreprise  
**Note:** Le client valide les heures de ses intérimaires

---

### 🔴 Bundle: `emargements.consolidate`
**Description:** Consolidation et export des émargements signés  
**Permissions incluses:**
```javascript
[
  "emargements.view.all",
  "emargements.consolidate",
  "emargements.export",
  "emargements.generate_report",
  "emargements.statistics"
]
```
**Assigné aux profils:** HR Manager, Commercial, Paie  
**Note:** Accès en lecture à la consolidation après signatures

---

### 🔴 Bundle: `emargements.manage`
**Description:** Gestion administrative complète des émargements  
**Permissions incluses:**
```javascript
[
  "emargements.view.all",
  "emargements.edit.all",
  "emargements.delete.all",
  "emargements.approve.all",
  "emargements.reject.all",
  "emargements.consolidate",
  "emargements.export",
  "emargements.generate_report",
  "emargements.unlock",
  "emargements.archive"
]
```
**Assigné aux profils:** Admin, HR Manager

---

### 🔴 Bundle: `signatures.read`
**Description:** Lecture des signatures électroniques  
**Permissions incluses:**
```javascript
[
  "signatures.view.all",
  "signatures.view.own",
  "signatures.verify",
  "signatures.history.view"
]
```
**Assigné aux profils:** Admin, HR Manager, Commercial, Paie

---

### 🔴 Bundle: `signatures.manage`
**Description:** Gestion des signatures électroniques  
**Permissions incluses:**
```javascript
[
  "signatures.view.all",
  "signatures.create",
  "signatures.request",
  "signatures.cancel",
  "signatures.verify",
  "signatures.invalidate",
  "signatures.history.view",
  "signatures.audit"
]
```
**Assigné aux profils:** Admin, HR Manager

---

### 🔴 Bundle: `consolidation.read` ⭐ NOUVEAU
**Description:** Accès en lecture à la consolidation des émargements après signatures  
**Permissions incluses:**
```javascript
[
  "emargements.consolidate.view",
  "emargements.consolidate.export",
  "emargements.reports.view",
  "emargements.statistics.view",
  "signatures.verify",
  "signatures.history.view"
]
```
**Assigné aux profils:** Paie, Commercial, HR Manager, Admin  
**Cas d'usage:** Permet aux services RH, Paie, et Commercial de consulter les émargements validés par les clients

---

## 5. Bundles Entreprises

### 🟠 Bundle: `entreprises.view`
**Description:** Consultation des entreprises  
**Permissions incluses:**
```javascript
[
  "entreprises.view.all",
  "entreprises.view.own",
  "entreprises.read.all",
  "entreprises.browse"
]
```
**Assigné aux profils:** Commercial, HR Manager, Admin

---

### 🟠 Bundle: `entreprises.manage`
**Description:** Gestion complète des entreprises  
**Permissions incluses:**
```javascript
[
  "entreprises.view.all",
  "entreprises.create",
  "entreprises.edit.all",
  "entreprises.delete",
  "entreprises.archive",
  "entreprises.restore",
  "entreprises.validate"
]
```
**Assigné aux profils:** Admin, HR Manager

---

### 🟠 Bundle: `entreprises.own_manage`
**Description:** Gestion de sa propre entreprise  
**Permissions incluses:**
```javascript
[
  "entreprises.view.own",
  "entreprises.edit.own",
  "entreprises.users.manage",
  "entreprises.settings.edit"
]
```
**Assigné aux profils:** Entreprise

---

## 6. Bundles Documents

### 📄 Bundle: `documents.upload`
**Description:** Upload de documents  
**Permissions incluses:**
```javascript
[
  "documents.upload.cv",
  "documents.upload.contract",
  "documents.upload.general",
  "documents.view.own",
  "documents.delete.own"
]
```
**Assigné aux profils:** Tous (selon contexte)

---

### 📄 Bundle: `documents.manage`
**Description:** Gestion complète des documents  
**Permissions incluses:**
```javascript
[
  "documents.view.all",
  "documents.upload.all",
  "documents.edit.all",
  "documents.delete.all",
  "documents.download.all",
  "documents.archive",
  "documents.validate"
]
```
**Assigné aux profils:** Admin, HR Manager

---

### 📄 Bundle: `documents.recruitment_access`
**Description:** Accès recrutement aux documents (CV, lettres motivation)  
**Permissions incluses:**
```javascript
[
  "documents.view.all",
  "documents.download.all",
  "documents.cv.view",
  "documents.cv.download",
  "documents.motivation_letter.view"
]
```
**Assigné aux profils:** Recrutement

---

## 7. Bundles Recrutement ⭐

### 🟣 Bundle: `recruitment.users_view`
**Description:** Consultation des profils candidats/intérimaires  
**Permissions incluses:**
```javascript
[
  "users.view.all",
  "users.read.all",
  "users.profiles.view",
  "users.skills.view",
  "users.experience.view",
  "users.availability.view",
  "users.search",
  "users.filter"
]
```
**Assigné aux profils:** Recrutement

---

### 🟣 Bundle: `recruitment.evaluate`
**Description:** Évaluation et notation des candidats  
**Permissions incluses:**
```javascript
[
  "users.rate",
  "users.rating.view",
  "users.comment.create",
  "users.comment.view",
  "users.feedback.create",
  "users.feedback.view",
  "users.notes.create",
  "users.notes.view",
  "users.notes.edit.own"
]
```
**Assigné aux profils:** Recrutement

---

### 🟣 Bundle: `recruitment.assign`
**Description:** Attribution de candidats aux missions  
**Permissions incluses:**
```javascript
[
  "missions.view.all",
  "missions.read.all",
  "missions.assign",
  "missions.users.assign",
  "missions.users.unassign",
  "missions.matching.view",
  "applications.assign_candidate"
]
```
**Assigné aux profils:** Recrutement

---

### 🟣 Bundle: `recruitment.manage`
**Description:** Gestion complète recrutement (bundle complet)  
**Permissions incluses:**
```javascript
[
  // Utilisateurs
  "users.view.all",
  "users.read.all",
  "users.profiles.view",
  "users.skills.view",
  "users.experience.view",
  "users.availability.view",
  "users.search",
  "users.filter",
  
  // Évaluation
  "users.rate",
  "users.rating.view",
  "users.comment.create",
  "users.comment.view",
  "users.feedback.create",
  "users.feedback.view",
  "users.notes.create",
  "users.notes.view",
  "users.notes.edit.own",
  
  // Missions & Attribution
  "missions.view.all",
  "missions.read.all",
  "missions.assign",
  "missions.users.assign",
  "missions.users.unassign",
  "missions.matching.view",
  "applications.assign_candidate",
  
  // Documents
  "documents.cv.view",
  "documents.cv.download",
  "documents.motivation_letter.view",
  
  // Applications
  "applications.view.all",
  "applications.read.all",
  "applications.comment"
]
```
**Assigné aux profils:** Recrutement

---

## 8. Bundles Communication

### 📧 Bundle: `notifications.user`
**Description:** Notifications utilisateur standard  
**Permissions incluses:**
```javascript
[
  "notifications.view.own",
  "notifications.read.own",
  "notifications.mark_read",
  "notifications.delete.own"
]
```
**Assigné aux profils:** Tous

---

### 📧 Bundle: `notifications.send`
**Description:** Envoi de notifications  
**Permissions incluses:**
```javascript
[
  "notifications.create",
  "notifications.send",
  "notifications.broadcast",
  "notifications.schedule"
]
```
**Assigné aux profils:** Admin, HR Manager, Commercial

---

### 📧 Bundle: `emails.send`
**Description:** Envoi d'emails système  
**Permissions incluses:**
```javascript
[
  "emails.send",
  "emails.template.use",
  "emails.history.view.own"
]
```
**Assigné aux profils:** Commercial, HR Manager

---

### 📧 Bundle: `emails.manage`
**Description:** Gestion des emails système  
**Permissions incluses:**
```javascript
[
  "emails.send",
  "emails.template.create",
  "emails.template.edit",
  "emails.template.delete",
  "emails.settings.edit",
  "emails.history.view.all",
  "emails.logs.view"
]
```
**Assigné aux profils:** Admin

---

## 8. Bundles Administration IAM

### 🔐 Bundle: `iam.read`
**Description:** Lecture du système IAM  
**Permissions incluses:**
```javascript
[
  "iam.permissions.view",
  "iam.profiles.view",
  "iam.groups.view",
  "iam.bundles.view",
  "iam.users_permissions.view"
]
```
**Assigné aux profils:** Admin, Auditor

---

### 🔐 Bundle: `iam.manage`
**Description:** Gestion complète IAM  
**Permissions incluses:**
```javascript
[
  "iam.permissions.view",
  "iam.permissions.create",
  "iam.permissions.edit",
  "iam.permissions.delete",
  "iam.profiles.view",
  "iam.profiles.create",
  "iam.profiles.edit",
  "iam.profiles.delete",
  "iam.groups.view",
  "iam.groups.create",
  "iam.groups.edit",
  "iam.groups.delete",
  "iam.bundles.view",
  "iam.bundles.create",
  "iam.bundles.edit",
  "iam.users.assign_profile",
  "iam.users.assign_group"
]
```
**Assigné aux profils:** Super Admin

---

## 9. Bundles Configuration Système

### ⚙️ Bundle: `config.read`
**Description:** Lecture de la configuration  
**Permissions incluses:**
```javascript
[
  "config.view",
  "config.feature_flags.view",
  "config.email_templates.view",
  "config.references.view"
]
```
**Assigné aux profils:** Admin, Auditor

---

### ⚙️ Bundle: `config.manage`
**Description:** Gestion de la configuration  
**Permissions incluses:**
```javascript
[
  "config.view",
  "config.edit",
  "config.feature_flags.toggle",
  "config.email_templates.edit",
  "config.references.manage",
  "config.system.restart",
  "config.cache.clear"
]
```
**Assigné aux profils:** Super Admin

---

## 10. Bundles Audit & Logs

### 📊 Bundle: `audit.read`
**Description:** Lecture des logs d'audit  
**Permissions incluses:**
```javascript
[
  "audit.logs.view",
  "audit.logs.search",
  "audit.logs.export",
  "audit.statistics.view"
]
```
**Assigné aux profils:** Admin, Auditor

---

### 📊 Bundle: `analytics.view`
**Description:** Consultation des analytics  
**Permissions incluses:**
```javascript
[
  "analytics.dashboard.view",
  "analytics.reports.view",
  "analytics.statistics.view",
  "analytics.export"
]
```
**Assigné aux profils:** Admin, HR Manager, Commercial

---

## Matrice des Bundles par Profil

| Bundle | Candidat | Intérimaire | Entreprise | Commercial | HR Manager | Paie | Recrutement | Admin | Super Admin |
|--------|----------|-------------|------------|------------|------------|------|-------------|-------|-------------|
| **Authentification** |
| `auth.basic` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Utilisateurs** |
| `users.read` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `users.manage` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `users.hr_access` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Missions** |
| `missions.read` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `missions.create` | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `missions.manage` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Candidatures** |
| `applications.submit` | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `applications.review` | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `applications.manage` | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Besoins RH** |
| `besoins.create` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `besoins.manage` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Émargements & Signatures** ⭐ |
| `emargements.submit` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `emargements.validate_interim` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `emargements.validate_client` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `emargements.consolidate` | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `emargements.manage` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `signatures.read` | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `signatures.manage` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `consolidation.read` ⭐ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Entreprises** |
| `entreprises.view` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `entreprises.manage` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `entreprises.own_manage` | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Documents** |
| `documents.upload` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| `documents.manage` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `documents.recruitment_access` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Recrutement** ⭐ |
| `recruitment.users_view` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `recruitment.evaluate` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `recruitment.assign` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| `recruitment.manage` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Communication** |
| `notifications.user` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `notifications.send` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `emails.send` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ |
| `emails.manage` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Administration** |
| `iam.read` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `iam.manage` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `config.read` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `config.manage` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `audit.read` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `analytics.view` | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |

---

## 🔄 Workflow Émargements avec Bundles

### Cas d'Usage: Émargement Mission

```
1️⃣ INTÉRIMAIRE
   Bundle: emargements.submit
   ↓
   - Crée son émargement (heures travaillées)
   - Signe électroniquement son émargement
   - Soumet à validation client

2️⃣ ENTREPRISE (CLIENT)
   Bundle: emargements.validate_client
   ↓
   - Consulte l'émargement soumis
   - Vérifie les heures
   - Signe électroniquement pour validation
   - Approuve ou rejette

3️⃣ CONSOLIDATION (après double signature)
   Bundle: consolidation.read ⭐
   ↓
   - Commercial: Consulte pour suivi commercial
   - HR Manager: Consulte pour reporting RH
   - Paie: Consulte pour calcul salaire
   - Admin: Accès complet + export

4️⃣ GESTION ADMINISTRATIVE
   Bundle: emargements.manage
   ↓
   - HR Manager / Admin uniquement
   - Correction d'erreurs
   - Déblocage si nécessaire
   - Archive après traitement paie
```

---

## 📋 Permissions Atomiques pour Émargements (Détail)

### Catégorie: EMARGEMENTS

| Code Permission | Description | Scope |
|----------------|-------------|-------|
| `emargements.create.own` | Créer ses propres émargements | own |
| `emargements.create.all` | Créer des émargements (admin) | all |
| `emargements.view.own` | Voir ses propres émargements | own |
| `emargements.view.all` | Voir tous les émargements | all |
| `emargements.edit.own` | Modifier ses émargements non signés | own |
| `emargements.edit.all` | Modifier tous les émargements | all |
| `emargements.delete.own` | Supprimer ses émargements brouillons | own |
| `emargements.delete.all` | Supprimer des émargements (admin) | all |
| `emargements.submit.own` | Soumettre ses émargements | own |
| `emargements.sign.own` | Signer ses propres émargements | own |
| `emargements.sign.all` | Signer des émargements (client) | all |
| `emargements.approve` | Approuver un émargement | organization |
| `emargements.reject` | Rejeter un émargement | organization |
| `emargements.comment.own` | Commenter ses émargements | own |
| `emargements.comment` | Commenter des émargements | organization |
| `emargements.consolidate` | Consolider les émargements | organization |
| `emargements.consolidate.view` | Voir consolidation | organization |
| `emargements.consolidate.export` | Exporter consolidation | organization |
| `emargements.export` | Exporter des émargements | organization |
| `emargements.generate_report` | Générer rapport émargements | organization |
| `emargements.statistics` | Voir statistiques émargements | organization |
| `emargements.statistics.view` | Voir stats consolidation | organization |
| `emargements.reports.view` | Voir rapports émargements | organization |
| `emargements.unlock` | Débloquer émargement signé | organization |
| `emargements.archive` | Archiver émargements traités | organization |

### Catégorie: SIGNATURES

| Code Permission | Description | Scope |
|----------------|-------------|-------|
| `signatures.view.own` | Voir ses propres signatures | own |
| `signatures.view.all` | Voir toutes les signatures | all |
| `signatures.create` | Créer une demande de signature | organization |
| `signatures.request` | Demander une signature | organization |
| `signatures.cancel` | Annuler une demande de signature | organization |
| `signatures.verify` | Vérifier authenticité signature | organization |
| `signatures.invalidate` | Invalider une signature | organization |
| `signatures.history.view` | Voir historique signatures | organization |
| `signatures.audit` | Auditer les signatures | organization |

---

## 💡 Recommandations d'Implémentation

### Phase 1: Permissions Atomiques
```sql
-- Créer toutes les permissions atomiques en base
INSERT INTO iam_permissions (code, name, scope, resource, description) VALUES
  ('emargements.create.own', 'Créer émargements', 'own', 'emargements', '...'),
  ('emargements.submit.own', 'Soumettre émargements', 'own', 'emargements', '...'),
  -- ... etc
```

### Phase 2: Bundles en Configuration
```python
# /app/auth-microservice/awana_auth/core/bundles.py

BUNDLES = {
    "emargements.submit": [
        "emargements.create.own",
        "emargements.submit.own",
        "emargements.view.own",
        "emargements.edit.own",
        "emargements.draft.own"
    ],
    "consolidation.read": [
        "emargements.consolidate.view",
        "emargements.consolidate.export",
        "emargements.reports.view",
        "emargements.statistics.view",
        "signatures.verify",
        "signatures.history.view"
    ],
    # ... etc
}
```

### Phase 3: Assignment aux Profils
```python
# Profil Intérimaire
PROFILE_INTERIMAIRE = {
    "bundles": [
        "auth.basic",
        "missions.read",
        "applications.submit",
        "emargements.submit",
        "emargements.validate_interim"
    ]
}

# Profil Paie
PROFILE_PAIE = {
    "bundles": [
        "auth.basic",
        "consolidation.read",  # ⭐ Accès consolidation
        "signatures.read"
    ]
}
```

---

## 📊 Statistiques

- **Total Bundles:** 37
- **Bundles Émargements/Signatures:** 8 (dont 1 nouveau ⭐)
- **Profils utilisant consolidation.read:** 4 (Commercial, HR Manager, Paie, Admin)
- **Permissions atomiques émargements:** 26
- **Permissions atomiques signatures:** 9

---

## 🔗 Documents Connexes

- [IAM_PROFILE_PERMISSIONS_MATRIX.md](IAM_PROFILE_PERMISSIONS_MATRIX.md) - Matrice des permissions par profil
- [BUNDLE_PERMISSIONS.md](BUNDLE_PERMISSIONS.md) - Concept des bundles
- [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md) - Documentation des workflows

---

*Dernière mise à jour: 26 Novembre 2025*  
*Version: 1.0*
