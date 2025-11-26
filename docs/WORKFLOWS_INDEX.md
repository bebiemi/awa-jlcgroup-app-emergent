# 📚 Index Complet des Workflows - AWANA Auth & Business System

**Date de génération:** 26 Novembre 2025  
**Total workflows documentés:** 19  
**Progression:** 100%

---

## 📖 Comment utiliser cette documentation

Chaque workflow est documenté dans un fichier dédié avec la structure suivante :
- 🎯 **Vue d'ensemble** : Description et objectifs
- 🔄 **Flow complet** : Diagramme du processus
- 📡 **Endpoints** : Détails des API
- 🔐 **Logique implémentée** : Architecture du code
- 🔍 **Collections MongoDB** : Schémas de données
- ⚡ **Points clés** : Forces et points d'attention
- 🧪 **Tests** : Exemples de validation

---

## 🗂️ Workflows par Catégorie

### 1️⃣ Authentication (6 workflows)

#### ✅ [Inscription Entreprise](ENTREPRISE_REGISTRATION_FLOW.md)
**Status:** DOCUMENTÉ COMPLET  
**Endpoints:** `POST /api/auth/local/register`, `POST /api/admin/{validation_id}/approve`  
**Résumé:** Workflow d'inscription des entreprises avec validation admin obligatoire. Les utilisateurs sont créés avec status PENDING, puis l'entreprise est créée après approbation.

#### 📄 [Inscription Candidat/Intérimaire](workflows/INSCRIPTION_CANDIDAT_INTERIMAIRE_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/local/register`  
**Résumé:** Inscription publique avec activation immédiate (status: ACTIVE). Assignment automatique au groupe `grp.candidat`.

#### 📄 [Inscription Collaborateur](workflows/INSCRIPTION_COLLABORATEUR_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/local/register`  
**Résumé:** Inscription des employés JLC Group détectée par domaine email (@jlcgroup.*). Nécessite validation admin.

#### 📄 [Authentification Locale](workflows/AUTHENTIFICATION_LOCALE_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/local/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`  
**Résumé:** Connexion par username/password avec génération JWT. Support MFA optionnel. **Endpoint critique** : les permissions IAM sont injectées dans le token ici.

#### 📄 [Authentification EntraID (SSO)](workflows/AUTHENTIFICATION_ENTRAID_SSO_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/entraid/login`, `POST /api/auth/entraid/callback`  
**Résumé:** Single Sign-On Microsoft Entra ID (Azure AD) avec OAuth 2.0 + PKCE. Auto-provisioning des comptes.

#### 📄 [Authentification Google](workflows/AUTHENTIFICATION_GOOGLE_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/google/login`, `POST /api/auth/google/callback`  
**Résumé:** Connexion via compte Google OAuth. Auto-création du compte avec récupération du profil Google.

---

### 2️⃣ Business (4 workflows)

#### 📄 [Création Mission](workflows/CREATION_MISSION_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/missions`, `PUT /api/missions/{id}`, `DELETE /api/missions/{id}`  
**Résumé:** Publication d'offres d'emploi temporaire par les entreprises. Statuts : draft, published, closed.

#### 📄 [Candidature à une Mission](workflows/CANDIDATURE_A_UNE_MISSION_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/applications`, `GET /api/missions/{id}/applications`  
**Résumé:** Postulation des candidats/intérimaires aux missions. Upload de CV et lettre de motivation.

#### 📄 [Validation Candidature](workflows/VALIDATION_CANDIDATURE_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/applications/{id}/approve`, `POST /api/applications/{id}/reject`  
**Résumé:** Approbation ou rejet des candidatures par les entreprises/RH. Notifications automatiques.

#### 📄 [Gestion des Besoins](workflows/GESTION_DES_BESOINS_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/besoins`, `PUT /api/besoins/{id}`, `POST /api/besoins/{id}/convert-to-mission`  
**Résumé:** Phase pré-mission pour définir les besoins RH. Conversion en missions publiables.

---

### 3️⃣ Security (3 workflows)

#### 📄 [Réinitialisation Mot de Passe](workflows/REINITIALISATION_MOT_DE_PASSE_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/forgot-password`, `POST /api/auth/reset-password`, `POST /api/users/{user_id}/password/admin-update`  
**Résumé:** Récupération de compte par email. Token temporaire valide 1 heure. Reset admin disponible.

#### 📄 [Vérification Email](workflows/VERIFICATION_EMAIL_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/email/send`, `POST /api/email/verify`, `POST /api/email/resend`  
**Résumé:** Confirmation d'adresse email lors de l'inscription. Token envoyé par email, renvoi possible.

#### 📄 [Multi-Factor Authentication (MFA)](workflows/MULTI_FACTOR_AUTHENTICATION_MFA_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/auth/mfa/setup`, `POST /api/auth/mfa/verify`, `POST /api/auth/mfa/disable`  
**Résumé:** Authentification à deux facteurs avec TOTP (Google Authenticator, Authy). QR code pour setup.

---

### 4️⃣ User Management (2 workflows)

#### 📄 [Gestion Profil Utilisateur](workflows/GESTION_PROFIL_UTILISATEUR_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `GET /api/profiles/me`, `PUT /api/profiles/me`, `POST /api/users/{user_id}/profiles`  
**Résumé:** Consultation et modification du profil. Synchronisation auth_db.users et jlc_db.collaborator_profiles.

#### 📄 [Archivage Utilisateur](workflows/ARCHIVAGE_UTILISATEUR_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `PATCH /api/users/{user_id}/archive`, `PATCH /api/users/{user_id}/restore`  
**Résumé:** Soft delete des utilisateurs. Flag `is_archived` sans suppression des données. Restauration possible.

---

### 5️⃣ Administration (1 workflow)

#### 📄 [Gestion IAM (Permissions)](workflows/GESTION_IAM_PERMISSIONS_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/iam/permissions`, `POST /api/iam/profiles`, `POST /api/iam/groups`  
**Résumé:** Gestion des permissions, profils et groupes IAM. **Système critique** pour le contrôle d'accès.

---

### 6️⃣ Communication (2 workflows)

#### 📄 [Notifications](workflows/NOTIFICATIONS_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `GET /api/notifications`, `POST /api/notifications/mark-read`  
**Résumé:** Messages in-app persistés en base. Types : Info, Warning, Success, Error. Marquage lecture.

#### 📄 [Emails Système](workflows/EMAILS_SYSTEME_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/email/send`, `GET /api/email/settings`  
**Résumé:** Envoi d'emails transactionnels avec templates. Configuration SMTP. Logs des envois.

---

### 7️⃣ Documents (1 workflow)

#### 📄 [Upload Documents](workflows/UPLOAD_DOCUMENTS_FLOW.md)
**Status:** DOCUMENTÉ  
**Endpoints:** `POST /api/documents/upload`, `GET /api/documents/{id}`, `DELETE /api/documents/{id}`  
**Résumé:** Upload de fichiers (CV, contrats). Stockage local `/app/uploads/`. Validation type MIME.

---

## 🔑 Workflows Critiques (P0)

Ces workflows sont au cœur du système et nécessitent une attention particulière :

### 🚨 Authentification Locale
- **Pourquoi critique ?** Injection des permissions IAM dans le JWT. Tout bug ici impact tous les utilisateurs.
- **Fichier clé:** `/app/auth-microservice/awana_auth_routes.py` (ligne 990-1137)
- **Dernière modification majeure:** Correction du bug de permissions (24 Nov 2025)

### 🚨 Inscription Entreprise
- **Pourquoi critique ?** Workflow complexe en 2 phases (user → validation → entreprise). Gère l'onboarding client.
- **Fichier clé:** `/app/auth-microservice/awana_auth_routes.py`, `/app/apps/api/src/presentation/routes/validation_routes.py`

### 🚨 Gestion IAM
- **Pourquoi critique ?** Définit les droits d'accès de toute l'application. Vulnérabilité = faille sécurité globale.
- **Fichiers clés:** `/app/auth-microservice/iam_routes.py`, `/app/auth-microservice/iam_unified_routes.py`
- **⚠️ ATTENTION:** Audit de sécurité en attente d'implémentation (voir `/app/docs/IAM_CORRECTIONS_IMMEDIATE.md`)

---

## 📊 Statistiques

| Catégorie | Workflows | Status |
|-----------|-----------|--------|
| Authentication | 6 | ✅ 100% documenté |
| Business | 4 | ✅ 100% documenté |
| Security | 3 | ✅ 100% documenté |
| User Management | 2 | ✅ 100% documenté |
| Administration | 1 | ✅ 100% documenté |
| Communication | 2 | ✅ 100% documenté |
| Documents | 1 | ✅ 100% documenté |
| **TOTAL** | **19** | **✅ 100%** |

---

## 🔄 Dépendances Entre Workflows

### Flux d'inscription complet
```
1. Inscription (Candidat/Collaborateur/Entreprise)
   ↓
2. Vérification Email (optionnel)
   ↓
3. Validation Admin (si PENDING)
   ↓
4. Authentification Locale
   ↓
5. Accès aux fonctionnalités métier
```

### Flux métier mission
```
1. Entreprise crée une Mission
   ↓
2. Candidat/Intérimaire soumet une Candidature
   ↓
3. Entreprise/RH fait la Validation Candidature
   ↓
4. Notifications envoyées
   ↓
5. Upload Documents (contrat)
```

### Flux IAM
```
1. Création Permission (IAM)
   ↓
2. Création Profil avec permissions (IAM)
   ↓
3. Création Groupe avec profils (IAM)
   ↓
4. Assignment utilisateur au groupe (inscription ou manuel)
   ↓
5. Permissions injectées dans JWT (authentification)
```

---

## 📝 Notes pour la Maintenance

### Conventions de Code
- **Permissions format:** `resource.action.scope` (ex: `missions.read.own`)
- **Status utilisateur:** `active`, `pending`, `suspended`, `archived`
- **Collections MongoDB:** Toujours exclure `_id` avec `{"_id": 0}`
- **Dates:** Utiliser `datetime.now(timezone.utc)` (pas `datetime.utcnow()`)

### Fichiers Centraux
- **Configuration IAM:** `/app/auth-microservice/iam_config.yml`
- **Modèles User:** `/app/auth-microservice/awana_auth/core/models.py`
- **JWT Manager:** `/app/auth-microservice/awana_auth/session/jwt.py`
- **Services IAM:** `/app/auth-microservice/awana_auth/services/iam_unified_service.py`

### Bases de Données
- **auth_db:** Authentification, permissions, sessions
- **jlc_db:** Business data (entreprises, missions, candidatures)

---

## 🚀 Prochaines Étapes

### Priority P0 (URGENT)
- [ ] **Implémenter les correctifs de sécurité IAM** (voir `/app/docs/IAM_CORRECTIONS_IMMEDIATE.md`)
  - Routes non protégées à sécuriser
  - Validation permissions à ajouter
  - Plan détaillé dans `/app/docs/IAM_STEP_BY_STEP_FIX.md`

### Priority P1
- [x] Documentation des workflows ✅ TERMINÉ

### Priority P2
- [ ] Améliorer les templates frontend (NeedListTemplate vs EntityListTemplate)
- [ ] Intégrer les icônes personnalisées
- [ ] Ajouter filtres et pagination côté serveur pour Entreprises

### Priority P3
- [ ] Tests E2E avec Playwright
- [ ] Performance optimization (caching, indexes)

### Priority P4
- [ ] Signature électronique

---

## 🆘 En cas de Bug

### Checklist de Debug
1. **Vérifier les permissions** : Le JWT contient-il les bonnes permissions ?
   ```bash
   echo $TOKEN | cut -d. -f2 | base64 -d | jq .
   ```

2. **Vérifier le statut utilisateur** : L'utilisateur est-il ACTIVE ?
   ```bash
   mongo auth_db --eval 'db.users.findOne({email: "user@example.com"})'
   ```

3. **Vérifier les groupes IAM** : L'utilisateur est-il dans le bon groupe ?
   ```bash
   mongo auth_db --eval 'db.iam_groups.find({user_ids: "user_id"})'
   ```

4. **Consulter les logs** :
   ```bash
   tail -f /var/log/supervisor/backend.err.log
   ```

### Problèmes Connus
- **Erreur "ObjectId not serializable"** : Toujours exclure `_id` dans les requêtes MongoDB
- **Permissions vides dans JWT** : Bug corrigé le 24/11/2025, vérifier que le fix est appliqué
- **Service non redémarré** : Après modif .env ou install package, restart supervisor

---

## 📞 Contacts & Ressources

- **Rapports d'audit sécurité:** `/app/docs/IAM_AUDIT_EXPERT_REPORT.md`
- **Matrice des permissions:** `/app/docs/IAM_PROFILE_PERMISSIONS_MATRIX.md`
- **Configuration IAM:** `/app/auth-microservice/iam_config.yml`
- **Test results:** `/app/test_result.md`

---

*Dernière mise à jour: 26 Novembre 2025*  
*Généré automatiquement par le système de documentation AWANA*
