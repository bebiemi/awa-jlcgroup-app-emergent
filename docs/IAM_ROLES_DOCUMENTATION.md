# 📚 Documentation des Rôles IAM

## Vue d'ensemble

Ce document liste tous les **rôles IAM** (Profils) du système JLC Group avec leurs descriptions, permissions et cas d'usage.

---

## 🎯 Architecture IAM

Le système utilise un **modèle hybride** :

```
Utilisateur → Profil(s) / Groupe(s) → Rôle(s) IAM → Permissions
```

- **Utilisateur** : Personne utilisant le système
- **Profil** : Rôle métier (ex: Intérimaire, Commercial)
- **Groupe** : Organisation (ex: Équipe RH, Département Commercial)
- **Rôle IAM** : Ensemble de permissions techniques
- **Permission** : Droit granulaire (ex: `mission.view_all`, `user.edit_own`)

---

## 📋 Classification des Rôles

### 1. Rôles Administrateurs

#### 🔐 Super Administrateur (`super_admin`)
- **Code** : `super_admin`
- **Catégorie** : `admin`
- **Description** : Accès complet au système, gestion de tous les utilisateurs et configurations
- **Permissions** : Toutes les permissions du système
- **Utilisation** : 
  - Configuration initiale du système
  - Gestion des autres administrateurs
  - Accès aux fonctionnalités critiques
- **Protégé** : ✅ Oui (système)

#### 🛡️ Administrateur (`admin`)
- **Code** : `admin`
- **Catégorie** : `admin`
- **Description** : Administrateur général du système avec accès étendu
- **Permissions principales** :
  - Gestion des utilisateurs (`users.*`)
  - Gestion des missions (`missions.*`)
  - Accès aux rapports et statistiques
  - Configuration des références système
- **Utilisation** :
  - Gestion quotidienne du système
  - Support utilisateur
  - Validation des candidatures
- **Protégé** : ✅ Oui (système)

#### 🔍 Auditeur (`profile_auditor`)
- **Code** : `profile_auditor`
- **Catégorie** : `admin`
- **Description** : Accès en lecture seule pour audit et conformité
- **Permissions principales** :
  - Lecture de tous les utilisateurs
  - Lecture de toutes les missions
  - Accès aux logs d'audit
  - Consultation des statistiques
- **Utilisation** :
  - Audit de conformité
  - Vérification des processus
  - Génération de rapports
- **Protégé** : ✅ Oui

---

### 2. Rôles Métier

#### 👤 Postulant / Candidat (`applicant`)
- **Code** : `applicant`
- **Catégorie** : `user`
- **Description** : Profil de base pour les candidats recherchant des missions
- **Permissions principales** :
  - `profile.view_own` : Voir son propre profil
  - `profile.edit_own` : Modifier son propre profil
  - `dashboard.access` : Accéder au tableau de bord
  - `missions.view_published` : Voir les missions publiées
  - `applications.create_own` : Postuler à des missions
  - `applications.view_own` : Voir ses candidatures
  - `documents.upload_own` : Uploader des documents (CV, etc.)
- **Utilisation** :
  - Inscription initiale
  - Recherche de missions
  - Candidature
- **Protégé** : ❌ Non

#### 💼 Intérimaire (`interim_user`)
- **Code** : `interim_user`
- **Catégorie** : `user`
- **Description** : Profil pour intérimaires actifs avec contrats
- **Permissions principales** :
  - Toutes les permissions de `applicant`
  - `contracts.view_own` : Voir ses contrats
  - `timesheets.submit` : Soumettre des feuilles de temps
  - `missions.view_assigned` : Voir les missions assignées
- **Utilisation** :
  - Intérimaires en mission
  - Gestion des contrats actifs
  - Suivi des heures
- **Protégé** : ❌ Non

#### 🏢 Admin Société (`company_admin`)
- **Code** : `company_admin`
- **Catégorie** : `user`
- **Description** : Administrateur d'une entreprise cliente
- **Permissions principales** :
  - `missions.create_company` : Créer des missions pour son entreprise
  - `missions.edit_company` : Modifier les missions de son entreprise
  - `missions.view_company` : Voir toutes les missions de son entreprise
  - `applications.view_company` : Voir les candidatures à ses missions
  - `applications.review` : Évaluer les candidatures
  - `contracts.create_company` : Créer des contrats
- **Utilisation** :
  - Entreprises clientes
  - Création et gestion de besoins
  - Sélection de candidats
- **Protégé** : ❌ Non

#### 🎯 Commercial (`commercial`)
- **Code** : `commercial`
- **Catégorie** : `user`
- **Description** : Commercial JLC Group gérant les relations entreprises
- **Permissions principales** :
  - `companies.view_all` : Voir toutes les entreprises
  - `companies.edit_assigned` : Modifier ses entreprises assignées
  - `missions.view_all` : Voir toutes les missions
  - `applications.view_all` : Voir toutes les candidatures
  - `contracts.create` : Créer des contrats
  - `reports.commercial` : Accès aux rapports commerciaux
- **Utilisation** :
  - Gestion du portefeuille clients
  - Suivi des missions
  - Statistiques commerciales
- **Protégé** : ❌ Non

#### 👥 Responsable RH (`hr_manager`)
- **Code** : `hr_manager`
- **Catégorie** : `user`
- **Description** : Gestionnaire des ressources humaines
- **Permissions principales** :
  - `users.view_all` : Voir tous les utilisateurs
  - `users.edit_team` : Modifier les utilisateurs de son équipe
  - `applications.review` : Évaluer les candidatures
  - `contracts.manage` : Gérer les contrats
  - `documents.verify` : Vérifier les documents
  - `reports.hr` : Accès aux rapports RH
- **Utilisation** :
  - Gestion des intérimaires
  - Validation des documents
  - Suivi des contrats
- **Protégé** : ❌ Non

#### 🎖️ Responsable d'Équipe (`team_manager`)
- **Code** : `team_manager`
- **Catégorie** : `user`
- **Description** : Manager d'une équipe interne
- **Permissions principales** :
  - `users.view_team` : Voir les utilisateurs de son équipe
  - `missions.assign_team` : Assigner des missions à son équipe
  - `reports.team` : Voir les rapports de son équipe
  - `performance.view_team` : Voir les performances de son équipe
- **Utilisation** :
  - Gestion d'équipe
  - Suivi de performance
  - Coordination des missions
- **Protégé** : ❌ Non

---

### 3. Rôles Spéciaux

#### 👁️ Lecture Seule (`read_only`)
- **Code** : `read_only`
- **Catégorie** : `user`
- **Description** : Accès en lecture uniquement
- **Permissions principales** :
  - `profile.view_own` : Voir son propre profil
  - `dashboard.access` : Accéder au tableau de bord
  - `missions.view_published` : Voir les missions publiées (lecture seule)
  - `users.view_basic` : Voir les informations de base des utilisateurs
- **Utilisation** :
  - Consultants externes
  - Observateurs
  - Comptes de démonstration
- **Protégé** : ❌ Non

---

## 🔑 Permissions par Défaut

Tous les utilisateurs reçoivent automatiquement ces permissions minimales :

| Permission | Description |
|------------|-------------|
| `profile.view_own` | Consulter son propre profil |
| `profile.edit_own` | Modifier son propre profil |
| `dashboard.access` | Accéder à son tableau de bord |

---

## 📊 Matrice des Permissions

### Gestion des Utilisateurs

| Rôle | view_own | edit_own | view_all | edit_all | create | delete |
|------|----------|----------|----------|----------|--------|--------|
| Super Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| HR Manager | ✅ | ✅ | ✅ | ⚠️ Équipe | ❌ | ❌ |
| Commercial | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Postulant | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

### Gestion des Missions

| Rôle | view_published | view_all | create | edit_own | edit_all | assign |
|------|----------------|----------|--------|----------|----------|--------|
| Super Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Company Admin | ✅ | ⚠️ Société | ✅ | ✅ | ❌ | ❌ |
| Commercial | ✅ | ✅ | ✅ | ⚠️ Assigné | ❌ | ✅ |
| Postulant | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Lecture Seule | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🛠️ Bonnes Pratiques

### Attribution des Rôles

1. **Principe du moindre privilège** : Attribuez le rôle avec le minimum de permissions nécessaires
2. **Utiliser les groupes** : Organisez les utilisateurs en groupes plutôt que d'attribuer des rôles individuellement
3. **Rôles temporaires** : Pour les accès temporaires, utilisez les groupes avec date d'expiration
4. **Audit régulier** : Vérifiez régulièrement les permissions des utilisateurs

### Création de Nouveaux Rôles

1. **Définir le besoin** : Identifier précisément les permissions requises
2. **Code descriptif** : Utiliser un code clair (ex: `marketing_manager`)
3. **Catégorie appropriée** : Choisir entre `admin`, `user`, `custom`
4. **Documentation** : Documenter le rôle et son utilisation
5. **Testing** : Tester avec un utilisateur test avant déploiement

---

## 🔄 Migration et Évolution

### Historique des Changements

- **v2.0** (2025-01-XX) : Migration vers le système IAM hybride
  - Suppression des profils legacy (`admin_complet`, `lecture_seule`, `gestionnaire_rh`)
  - Ajout des permissions par défaut (`profile.view_own`, `profile.edit_own`, `dashboard.access`)
  - Normalisation des codes de profils

- **v1.0** (2024-XX-XX) : Système initial avec permissions directes

### Profils Dépréciés

Les profils suivants ont été supprimés lors de la migration v2.0 :

| Code | Nom | Raison |
|------|-----|--------|
| `admin_complet` | Admin Complet | Fusionné avec `admin` |
| `lecture_seule` (legacy) | Lecture Seule | Remplacé par `read_only` |
| `gestionnaire_rh` | Gestionnaire RH | Remplacé par `hr_manager` |

---

## 📞 Support

Pour toute question concernant les rôles IAM :

- Documentation technique : `/app/docs/`
- Scripts de gestion : `/app/scripts/`
- Contact : admin@jlcgroup.com

---

**Dernière mise à jour** : $(date '+%Y-%m-%d')
**Version** : 2.0
