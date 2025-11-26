# 📚 Documentation AWANA - Guide de Navigation

Bienvenue dans la documentation complète du système AWANA Auth & Business System.

## 🗺️ Comment Naviguer dans cette Documentation

### 🎯 Par où commencer ?

#### 1️⃣ Pour une Vue d'Ensemble Rapide
**→ Commencez par:** [WORKFLOWS_VISUAL_SUMMARY.md](WORKFLOWS_VISUAL_SUMMARY.md)
- Architecture globale du système
- Parcours utilisateur par type (Candidat, Entreprise, Collaborateur, Admin)
- Diagrammes visuels
- Schéma des collections MongoDB

#### 2️⃣ Pour un Index Complet
**→ Consultez:** [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md)
- Liste exhaustive des 19 workflows
- Liens vers chaque documentation détaillée
- Workflows critiques mis en évidence
- Statistiques et métriques

#### 3️⃣ Pour un Aperçu par Catégorie
**→ Consultez:** [WORKFLOWS_CATALOGUE.md](WORKFLOWS_CATALOGUE.md)
- Organisation par catégorie (Authentication, Business, Security, etc.)
- Statut de documentation
- Progression globale

---

## 📂 Structure de la Documentation

```
/app/docs/
│
├── README.md (ce fichier)
│
├── 📊 VUES D'ENSEMBLE
│   ├── WORKFLOWS_INDEX.md           → Index complet avec liens
│   ├── WORKFLOWS_VISUAL_SUMMARY.md  → Synthèse visuelle et diagrammes
│   └── WORKFLOWS_CATALOGUE.md       → Catalogue organisé par catégorie
│
├── 📖 WORKFLOWS DÉTAILLÉS
│   ├── ENTREPRISE_REGISTRATION_FLOW.md  (Workflow complet existant)
│   └── workflows/
│       ├── INSCRIPTION_CANDIDAT_INTERIMAIRE_FLOW.md
│       ├── INSCRIPTION_COLLABORATEUR_FLOW.md
│       ├── AUTHENTIFICATION_LOCALE_FLOW.md
│       ├── AUTHENTIFICATION_ENTRAID_SSO_FLOW.md
│       ├── AUTHENTIFICATION_GOOGLE_FLOW.md
│       ├── CREATION_MISSION_FLOW.md
│       ├── CANDIDATURE_A_UNE_MISSION_FLOW.md
│       ├── VALIDATION_CANDIDATURE_FLOW.md
│       ├── GESTION_DES_BESOINS_FLOW.md
│       ├── UPLOAD_DOCUMENTS_FLOW.md
│       ├── GESTION_PROFIL_UTILISATEUR_FLOW.md
│       ├── ARCHIVAGE_UTILISATEUR_FLOW.md
│       ├── REINITIALISATION_MOT_DE_PASSE_FLOW.md
│       ├── VERIFICATION_EMAIL_FLOW.md
│       ├── MULTI_FACTOR_AUTHENTICATION_MFA_FLOW.md
│       ├── GESTION_IAM_PERMISSIONS_FLOW.md
│       ├── NOTIFICATIONS_FLOW.md
│       └── EMAILS_SYSTEME_FLOW.md
│
├── 🔐 SÉCURITÉ & IAM
│   ├── IAM_AUDIT_EXPERT_REPORT.md          → Audit complet du système IAM
│   ├── IAM_CORRECTIONS_IMMEDIATE.md        → Vulnérabilités identifiées
│   ├── IAM_STEP_BY_STEP_FIX.md            → Plan d'action détaillé
│   ├── IAM_PROFILE_PERMISSIONS_MATRIX.md  → Matrice des permissions
│   ├── IAM_PROFILES_SUMMARY.md            → Résumé des profils
│   ├── IAM_ENDPOINT_MATRIX.json           → Matrice endpoints/permissions
│   └── SECURITY_AUDIT_REPORT.md           → Rapport d'audit sécurité
│
└── 📋 RAPPORTS & PLANS
    ├── SECURITY_ACTION_PLAN.md            → Plan d'action sécurité
    └── IAM_EXECUTIVE_SUMMARY.md           → Résumé exécutif IAM
```

---

## 🎯 Guides par Cas d'Usage

### 👨‍💻 Je suis nouveau développeur sur le projet
**Ordre de lecture recommandé:**
1. [WORKFLOWS_VISUAL_SUMMARY.md](WORKFLOWS_VISUAL_SUMMARY.md) - Comprendre l'architecture
2. [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md) - Vue d'ensemble des workflows
3. [ENTREPRISE_REGISTRATION_FLOW.md](ENTREPRISE_REGISTRATION_FLOW.md) - Exemple de workflow complet
4. [IAM_PROFILE_PERMISSIONS_MATRIX.md](IAM_PROFILE_PERMISSIONS_MATRIX.md) - Système de permissions

### 🔍 Je dois débugger un problème d'authentification
**Consultez:**
1. [workflows/AUTHENTIFICATION_LOCALE_FLOW.md](workflows/AUTHENTIFICATION_LOCALE_FLOW.md)
2. Section "Checklist de Debug" dans [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md)
3. Credentials de test dans le handoff summary

### 🛡️ Je dois comprendre le système de permissions
**Consultez:**
1. [IAM_PROFILE_PERMISSIONS_MATRIX.md](IAM_PROFILE_PERMISSIONS_MATRIX.md)
2. [workflows/GESTION_IAM_PERMISSIONS_FLOW.md](workflows/GESTION_IAM_PERMISSIONS_FLOW.md)
3. [IAM_AUDIT_EXPERT_REPORT.md](IAM_AUDIT_EXPERT_REPORT.md)

### 🔒 Je dois corriger des failles de sécurité
**Consultez:**
1. [IAM_CORRECTIONS_IMMEDIATE.md](IAM_CORRECTIONS_IMMEDIATE.md) - Vulnérabilités critiques
2. [IAM_STEP_BY_STEP_FIX.md](IAM_STEP_BY_STEP_FIX.md) - Plan d'action détaillé
3. [SECURITY_ACTION_PLAN.md](SECURITY_ACTION_PLAN.md) - Stratégie globale

### 📊 Je dois comprendre un workflow spécifique
**Consultez:**
1. [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md) - Trouver le workflow
2. Cliquer sur le lien vers le document détaillé
3. Chaque document contient:
   - Vue d'ensemble
   - Flow complet
   - Endpoints avec exemples
   - Logique implémentée
   - Collections MongoDB
   - Tests

---

## 📖 Structure d'un Document de Workflow

Chaque workflow détaillé suit la même structure pour faciliter la navigation :

```markdown
# 📋 [Nom du Workflow]

## 🎯 Vue d'Ensemble
Description, objectifs, caractéristiques principales

## 🔄 Flow Complet
Diagramme ASCII du processus complet

## 📡 Endpoints
Détails de chaque API endpoint avec exemples

## 🔐 Logique Implémentée
Description du code et de la logique métier

## 🔍 Collections MongoDB Impactées
Schémas des collections utilisées

## ⚡ Points Clés
✅ Ce qui fonctionne bien
⚠️ Points d'attention

## 🧪 Tests
Exemples de tests avec curl

## 📚 Fichiers Clés
Tableau des fichiers sources
```

---

## 🔍 Recherche Rapide

### Par Type d'Utilisateur

| Type | Workflows Principaux |
|------|---------------------|
| **Candidat** | Inscription Candidat, Authentification, Candidature Mission |
| **Intérimaire** | Authentification, Candidature Mission, Gestion Profil |
| **Entreprise** | Inscription Entreprise, Création Mission, Validation Candidature |
| **Collaborateur** | Inscription Collaborateur, Gestion Besoins, Validation Candidature |
| **Admin** | Gestion IAM, Validation Inscriptions, Archivage Utilisateurs |

### Par Fonctionnalité

| Fonctionnalité | Document(s) |
|----------------|-------------|
| **Connexion** | Authentification Locale, EntraID SSO, Google OAuth |
| **Inscription** | Inscription Candidat, Collaborateur, Entreprise |
| **Sécurité** | Réinitialisation MDP, Vérification Email, MFA |
| **Missions** | Création Mission, Candidature, Validation |
| **Permissions** | Gestion IAM, Matrice Permissions |
| **Communication** | Notifications, Emails Système |
| **Documents** | Upload Documents |

---

## 🆘 En Cas de Problème

### Le workflow que je cherche n'est pas clair
→ Consultez [WORKFLOWS_VISUAL_SUMMARY.md](WORKFLOWS_VISUAL_SUMMARY.md) pour les diagrammes visuels

### Je ne comprends pas le système de permissions
→ Consultez [IAM_PROFILE_PERMISSIONS_MATRIX.md](IAM_PROFILE_PERMISSIONS_MATRIX.md)

### Je dois corriger un bug
→ Utilisez la "Checklist de Debug" dans [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md)

### Je dois ajouter une fonctionnalité
→ Identifiez le workflow concerné et consultez sa documentation détaillée

---

## 📝 Conventions et Standards

### Codes de Permission
Format: `resource.action.scope`
- **resource**: missions, users, entreprises, etc.
- **action**: read, create, update, delete, manage
- **scope**: own, all, group

**Exemples:**
- `missions.read.own` - Lire ses propres missions
- `applications.manage.all` - Gérer toutes les candidatures
- `users.create.group` - Créer des utilisateurs dans son groupe

### Statuts Utilisateur
- `active` - Utilisateur actif, accès complet
- `pending` - En attente de validation
- `suspended` - Compte suspendu temporairement
- `archived` - Compte archivé (soft delete)

### Collections MongoDB
- **auth_db**: Données d'authentification, permissions, sessions
- **jlc_db**: Données métier (entreprises, missions, candidatures)

### Format des Dates
- **Stockage:** ISO 8601 string (`2025-11-26T10:30:00Z`)
- **Génération:** `datetime.now(timezone.utc).isoformat()`
- **⚠️ Ne PAS utiliser:** `datetime.utcnow()` (deprecated)

---

## 🔄 Mise à Jour de la Documentation

Cette documentation a été générée le **26 Novembre 2025**.

### Quand mettre à jour ?
- Ajout d'un nouveau workflow
- Modification majeure d'un workflow existant
- Changement dans le système de permissions
- Découverte de bug ou vulnérabilité

### Comment mettre à jour ?
1. Modifier le document concerné dans `/app/docs/`
2. Mettre à jour l'index si nécessaire
3. Mettre à jour la date de dernière modification
4. Commit avec message descriptif

---

## 📊 Statistiques de la Documentation

- **Total workflows documentés:** 19 ✅
- **Documents créés:** 21
- **Catégories couvertes:** 7
- **Pages de documentation:** ~100 pages équivalent
- **Dernière mise à jour:** 26 Novembre 2025
- **Progression:** 100% 🎉

---

## 🎓 Ressources Additionnelles

### Fichiers de Configuration
- `/app/auth-microservice/iam_config.yml` - Configuration IAM
- `/app/backend/.env` - Variables d'environnement backend
- `/app/frontend/.env` - Variables d'environnement frontend

### Fichiers de Code Principaux
- `/app/auth-microservice/awana_auth_routes.py` - Routes d'authentification
- `/app/auth-microservice/iam_routes.py` - Routes IAM
- `/app/auth-microservice/awana_auth/session/jwt.py` - Gestion JWT
- `/app/auth-microservice/awana_auth/core/models.py` - Modèles de données

### Scripts Utiles
- `/app/scripts/analyze_all_workflows.py` - Analyse des workflows
- `/app/scripts/generate_all_workflow_docs.py` - Génération documentation
- `/app/scripts/audit_security_endpoints.py` - Audit sécurité
- `/app/scripts/generate_profile_matrix.py` - Génération matrice permissions

### Tests
- `/app/test_result.md` - Résultats des tests
- `/app/backend/tests/` - Tests unitaires backend

---

## 💡 Conseils de Navigation

1. **Utilisez Ctrl+F** dans votre éditeur pour rechercher rapidement
2. **Suivez les liens** entre documents pour une navigation fluide
3. **Consultez les diagrammes** dans WORKFLOWS_VISUAL_SUMMARY.md en premier
4. **Référez-vous à la matrice** des permissions pour comprendre les droits
5. **Lisez les "Points Clés"** de chaque workflow pour les informations essentielles

---

## 📬 Contact et Support

Pour toute question sur cette documentation :
- Consultez d'abord [WORKFLOWS_INDEX.md](WORKFLOWS_INDEX.md)
- Vérifiez les sections "En cas de bug" des workflows concernés
- Consultez les rapports d'audit pour les questions de sécurité

---

**Bonne navigation ! 🚀**

*Cette documentation est vivante et doit être maintenue à jour avec l'évolution du système.*
