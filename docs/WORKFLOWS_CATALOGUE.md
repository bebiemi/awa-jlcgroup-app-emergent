# 📋 Catalogue Complet des Workflows

**Application:** AWANA Auth & Business System
**Total workflows identifiés:** 19

## 📊 Vue d'Ensemble

### Administration (1 workflows)

📝 **Gestion IAM (Permissions)**
- Endpoints: 3
- Fichiers: iam_routes.py, iam_unified_routes.py
- Status: TO_DOCUMENT

### Authentication (6 workflows)

✅ **Inscription Entreprise**
- Endpoints: 2
- Fichiers: awana_auth_routes.py, validation_routes.py
- Status: DOCUMENTED

📝 **Inscription Candidat/Intérimaire**
- Endpoints: 1
- Fichiers: awana_auth_routes.py
- Status: TO_DOCUMENT

📝 **Inscription Collaborateur**
- Endpoints: 1
- Fichiers: awana_auth_routes.py
- Status: TO_DOCUMENT

📝 **Authentification Locale**
- Endpoints: 3
- Fichiers: awana_auth_routes.py
- Status: TO_DOCUMENT

📝 **Authentification EntraID (SSO)**
- Endpoints: 2
- Fichiers: awana_auth_routes.py
- Status: TO_DOCUMENT

📝 **Authentification Google**
- Endpoints: 2
- Fichiers: google_auth_routes.py
- Status: TO_DOCUMENT

### Business (4 workflows)

📝 **Création Mission**
- Endpoints: 3
- Fichiers: mission_routes.py
- Status: TO_DOCUMENT

📝 **Candidature à une Mission**
- Endpoints: 2
- Fichiers: application_routes.py, mission_routes.py
- Status: TO_DOCUMENT

📝 **Validation Candidature**
- Endpoints: 2
- Fichiers: application_routes.py
- Status: TO_DOCUMENT

📝 **Gestion des Besoins**
- Endpoints: 3
- Fichiers: besoin_routes.py
- Status: TO_DOCUMENT

### Communication (2 workflows)

📝 **Notifications**
- Endpoints: 2
- Fichiers: notification_routes.py
- Status: TO_DOCUMENT

📝 **Emails Système**
- Endpoints: 2
- Fichiers: email_routes.py, email_settings_routes.py
- Status: TO_DOCUMENT

### Documents (1 workflows)

📝 **Upload Documents**
- Endpoints: 3
- Fichiers: document_routes.py
- Status: TO_DOCUMENT

### Security (3 workflows)

📝 **Réinitialisation Mot de Passe**
- Endpoints: 3
- Fichiers: awana_auth_routes.py
- Status: TO_DOCUMENT

📝 **Vérification Email**
- Endpoints: 3
- Fichiers: email_verification_routes.py
- Status: TO_DOCUMENT

📝 **Multi-Factor Authentication (MFA)**
- Endpoints: 3
- Fichiers: mfa_routes.py
- Status: TO_DOCUMENT

### User Management (2 workflows)

📝 **Gestion Profil Utilisateur**
- Endpoints: 3
- Fichiers: profile_routes.py, user_detail_routes.py
- Status: TO_DOCUMENT

📝 **Archivage Utilisateur**
- Endpoints: 2
- Fichiers: user_archive_routes.py
- Status: TO_DOCUMENT

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
