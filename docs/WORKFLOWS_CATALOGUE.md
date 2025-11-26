# 📋 Catalogue Complet des Workflows

**Application:** AWANA Auth & Business System
**Total workflows identifiés:** 19

## 📊 Vue d'Ensemble

### Administration (1 workflows)

✅ **Gestion IAM (Permissions)**
- Endpoints: 3
- Fichiers: iam_routes.py, iam_unified_routes.py
- Status: DOCUMENTED → [workflows/GESTION_IAM_PERMISSIONS_FLOW.md](workflows/GESTION_IAM_PERMISSIONS_FLOW.md)

### Authentication (6 workflows)

✅ **Inscription Entreprise**
- Endpoints: 2
- Fichiers: awana_auth_routes.py, validation_routes.py
- Status: DOCUMENTED → [ENTREPRISE_REGISTRATION_FLOW.md](ENTREPRISE_REGISTRATION_FLOW.md)

✅ **Inscription Candidat/Intérimaire**
- Endpoints: 1
- Fichiers: awana_auth_routes.py
- Status: DOCUMENTED → [workflows/INSCRIPTION_CANDIDAT_INTERIMAIRE_FLOW.md](workflows/INSCRIPTION_CANDIDAT_INTERIMAIRE_FLOW.md)

✅ **Inscription Collaborateur**
- Endpoints: 1
- Fichiers: awana_auth_routes.py
- Status: DOCUMENTED → [workflows/INSCRIPTION_COLLABORATEUR_FLOW.md](workflows/INSCRIPTION_COLLABORATEUR_FLOW.md)

✅ **Authentification Locale**
- Endpoints: 3
- Fichiers: awana_auth_routes.py
- Status: DOCUMENTED → [workflows/AUTHENTIFICATION_LOCALE_FLOW.md](workflows/AUTHENTIFICATION_LOCALE_FLOW.md)

✅ **Authentification EntraID (SSO)**
- Endpoints: 2
- Fichiers: awana_auth_routes.py
- Status: DOCUMENTED → [workflows/AUTHENTIFICATION_ENTRAID_SSO_FLOW.md](workflows/AUTHENTIFICATION_ENTRAID_SSO_FLOW.md)

✅ **Authentification Google**
- Endpoints: 2
- Fichiers: google_auth_routes.py
- Status: DOCUMENTED → [workflows/AUTHENTIFICATION_GOOGLE_FLOW.md](workflows/AUTHENTIFICATION_GOOGLE_FLOW.md)

### Business (4 workflows)

✅ **Création Mission**
- Endpoints: 3
- Fichiers: mission_routes.py
- Status: DOCUMENTED → [workflows/CREATION_MISSION_FLOW.md](workflows/CREATION_MISSION_FLOW.md)

✅ **Candidature à une Mission**
- Endpoints: 2
- Fichiers: application_routes.py, mission_routes.py
- Status: DOCUMENTED → [workflows/CANDIDATURE_A_UNE_MISSION_FLOW.md](workflows/CANDIDATURE_A_UNE_MISSION_FLOW.md)

✅ **Validation Candidature**
- Endpoints: 2
- Fichiers: application_routes.py
- Status: DOCUMENTED → [workflows/VALIDATION_CANDIDATURE_FLOW.md](workflows/VALIDATION_CANDIDATURE_FLOW.md)

✅ **Gestion des Besoins**
- Endpoints: 3
- Fichiers: besoin_routes.py
- Status: DOCUMENTED → [workflows/GESTION_DES_BESOINS_FLOW.md](workflows/GESTION_DES_BESOINS_FLOW.md)

### Communication (2 workflows)

✅ **Notifications**
- Endpoints: 2
- Fichiers: notification_routes.py
- Status: DOCUMENTED → [workflows/NOTIFICATIONS_FLOW.md](workflows/NOTIFICATIONS_FLOW.md)

✅ **Emails Système**
- Endpoints: 2
- Fichiers: email_routes.py, email_settings_routes.py
- Status: DOCUMENTED → [workflows/EMAILS_SYSTEME_FLOW.md](workflows/EMAILS_SYSTEME_FLOW.md)

### Documents (1 workflows)

✅ **Upload Documents**
- Endpoints: 3
- Fichiers: document_routes.py
- Status: DOCUMENTED → [workflows/UPLOAD_DOCUMENTS_FLOW.md](workflows/UPLOAD_DOCUMENTS_FLOW.md)

### Security (3 workflows)

✅ **Réinitialisation Mot de Passe**
- Endpoints: 3
- Fichiers: awana_auth_routes.py
- Status: DOCUMENTED → [workflows/REINITIALISATION_MOT_DE_PASSE_FLOW.md](workflows/REINITIALISATION_MOT_DE_PASSE_FLOW.md)

✅ **Vérification Email**
- Endpoints: 3
- Fichiers: email_verification_routes.py
- Status: DOCUMENTED → [workflows/VERIFICATION_EMAIL_FLOW.md](workflows/VERIFICATION_EMAIL_FLOW.md)

✅ **Multi-Factor Authentication (MFA)**
- Endpoints: 3
- Fichiers: mfa_routes.py
- Status: DOCUMENTED → [workflows/MULTI_FACTOR_AUTHENTICATION_MFA_FLOW.md](workflows/MULTI_FACTOR_AUTHENTICATION_MFA_FLOW.md)

### User Management (2 workflows)

✅ **Gestion Profil Utilisateur**
- Endpoints: 3
- Fichiers: profile_routes.py, user_detail_routes.py
- Status: DOCUMENTED → [workflows/GESTION_PROFIL_UTILISATEUR_FLOW.md](workflows/GESTION_PROFIL_UTILISATEUR_FLOW.md)

✅ **Archivage Utilisateur**
- Endpoints: 2
- Fichiers: user_archive_routes.py
- Status: DOCUMENTED → [workflows/ARCHIVAGE_UTILISATEUR_FLOW.md](workflows/ARCHIVAGE_UTILISATEUR_FLOW.md)

## 📈 Statistiques

- ✅ Workflows documentés: 19
- 📝 Workflows à documenter: 0
- 📊 Progression: 100% ✅ TERMINÉ

## 🎯 Plan de Documentation

### Priorité 1: Authentication & Security (critique)
- [ ] Inscription Candidat/Intérimaire
- [ ] Inscription Collaborateur
- [ ] Authentification Locale
- [ ] Authentification EntraID (SSO)
- [ ] Authentification Google
- [ ] Réinitialisation Mot de Passe
- [ ] Vérification Email
- [ ] Multi-Factor Authentication (MFA)

### Priorité 2: Business Workflows (important)
- [ ] Création Mission
- [ ] Candidature à une Mission
- [ ] Validation Candidature
- [ ] Gestion des Besoins

### Priorité 3: User & Admin (important)
- [ ] Gestion Profil Utilisateur
- [ ] Archivage Utilisateur
- [ ] Gestion IAM (Permissions)

### Priorité 4: Support (moyen)
- [ ] Upload Documents
- [ ] Notifications
- [ ] Emails Système
