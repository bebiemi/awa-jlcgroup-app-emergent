# 📋 Résumé des Profils et Permissions

**Document simplifié pour référence rapide**

---

## 🎯 Profils Principaux

### 1. Super Administrateur (`super_admin`)
**Total permissions:** 182 (TOUTES)

**Rôle:** Accès complet à toutes les fonctionnalités du système

**Permissions clés:**
- ✅ Toutes les permissions IAM
- ✅ Toutes les permissions utilisateurs
- ✅ Toutes les permissions missions, besoins, entreprises
- ✅ Gestion complète des documents et applications
- ✅ Configuration et administration système

**Qui devrait avoir ce profil:** Administrateurs système uniquement

---

### 2. Administrateur (`admin`)
**Total permissions:** 31

**Rôle:** Administration opérationnelle sans accès système critique

**Permissions directes (31):**
- users.unblock
- admin.statistics
- users.reset_password
- config.feature_flags
- entreprises.grouping.manage
- *(et 26 autres)*

**Bundles (5):**
1. **users.manage** (8 permissions)
   - users.archive, block, create, delete
   - users.edit.all, restore, unblock, view.all

2. **missions.full_access** (9 permissions)
   - missions.archive, assign, cancel, create
   - missions.publish, read.all, reject, update, validate

3. **config.manage** (4 permissions)
   - config.email_templates, feature_flags
   - config.read, update

4. **admin.access** (4 permissions)
   - admin.audit_logs, dashboard, rbac, statistics

5. **entreprises.manage** (6 permissions)
   - entreprises.approve, create, delete
   - entreprises.edit.all, validate, view.all

**Qui devrait avoir ce profil:** Administrateurs fonctionnels, responsables d'équipe

---

### 3. Commercial (`commercial`)
**Total permissions:** 15

**Rôle:** Gestion des missions et entreprises clientes

**Bundles (2):**
1. **missions.full_access** (9 permissions)
   - Création, modification, validation de missions
   - Lecture de toutes les missions
   - Assignment et publication

2. **entreprises.manage** (6 permissions)
   - Gestion complète des entreprises clientes
   - Création, édition, validation
   - Vue sur toutes les entreprises

**Permissions effectives:**
- ✅ Créer et gérer des missions
- ✅ Assigner des intérimaires
- ✅ Gérer les entreprises clientes
- ✅ Valider/rejeter des missions
- ❌ Pas d'accès aux utilisateurs système
- ❌ Pas d'accès à la configuration

**Qui devrait avoir ce profil:** Équipe commerciale, chargés d'affaires

---

### 4. Responsable RH (`hr_manager`)
**Total permissions:** 8

**Rôle:** Gestion des ressources humaines et recrutement

**Permissions:**
- users.read.all (voir tous les utilisateurs)
- users.manage_status.all (gérer les statuts)
- missions.read.all (voir toutes les missions)
- applications.read.all (voir les candidatures)
- documents.view_cv.all (consulter les CV)
- documents.view_contracts.all (consulter les contrats)
- *(et 2 autres)*

**Qui devrait avoir ce profil:** RH, responsables recrutement

---

### 5. Admin Société (`company_admin`)
**Total permissions:** 5

**Rôle:** Administrateur d'une entreprise cliente

**Permissions:**
- entreprises.view.own (voir son entreprise)
- entreprises.edit.own (éditer son entreprise)
- applications.read.all (voir les candidatures)
- missions.read.own (voir ses missions)
- dashboard.view.own (son tableau de bord)

**Qui devrait avoir ce profil:** Responsables côté client

---

### 6. Intérimaire (`interim_user`)
**Total permissions:** 7

**Rôle:** Accès candidat/intérimaire

**Permissions:**
- applications.create.own (postuler)
- applications.read.own (voir ses candidatures)
- applications.edit.own (modifier ses candidatures)
- missions.read.own (voir ses missions)
- documents.upload_cv.own (téléverser CV)
- documents.view_cv.own (consulter son CV)
- profile.view.own (voir son profil)

**Qui devrait avoir ce profil:** Intérimaires, candidats

---

### 7. Candidat (`candidat`)
**Total permissions:** 6

**Rôle:** Accès candidat basique

**Permissions:**
- applications.create.own (postuler)
- applications.read.own (voir ses candidatures)
- missions.read.own (voir missions assignées)
- documents.upload_cv.own (téléverser CV)
- documents.view_cv.own (voir son CV)
- profile.view.own (voir son profil)

**Qui devrait avoir ce profil:** Candidats en cours de recrutement

---

### 8. Lecture Seule (`read_only`)
**Total permissions:** 4

**Rôle:** Accès consultation uniquement

**Permissions:**
- missions.read.all
- entreprises.read.all
- users.read.all
- dashboard.view.all

**Qui devrait avoir ce profil:** Auditeurs, consultants, stagiaires

---

### 9. Gestionnaire Commercial (`gestionnaire_commercial`)
**Total permissions:** 12

**Rôle:** Commercial avec focus sur les besoins

**Bundles:**
1. **missions.full_access** (9 permissions)
2. Permissions besoins (3)
   - besoins.read.all
   - besoins.create
   - besoins.edit.all

**Qui devrait avoir ce profil:** Commerciaux spécialisés besoins

---

## 📊 Tableau Comparatif

| Profil | Code | Permissions | Bundles | Cas d'Usage |
|--------|------|-------------|---------|-------------|
| Super Admin | `super_admin` | 182 | 0 | Administration système |
| Admin | `admin` | 31 | 5 | Administration opérationnelle |
| Commercial | `commercial` | 15 | 2 | Gestion missions/entreprises |
| RH Manager | `hr_manager` | 8 | 0 | Gestion RH |
| Admin Société | `company_admin` | 5 | 0 | Client admin |
| Intérimaire | `interim_user` | 7 | 0 | Intérimaire actif |
| Candidat | `candidat` | 6 | 0 | Candidat postulant |
| Lecture Seule | `read_only` | 4 | 0 | Consultation |

---

## 🔑 Catégories de Permissions Principales

### IAM (18 permissions)
Gestion des utilisateurs, profils, permissions, groupes
- Création/édition/suppression profils
- Assignment de permissions
- Gestion groupes IAM
- Audit IAM

### Missions (21 permissions)
Gestion du cycle de vie des missions
- Création/édition/suppression
- Assignment d'intérimaires
- Validation/rejet
- Publication

### Entreprises (16 permissions)
Gestion des entreprises clientes
- Création/édition/suppression
- Validation
- Regroupement d'entreprises

### Utilisateurs (19 permissions)
Gestion des comptes utilisateurs
- Création/édition/suppression
- Blocage/déblocage
- Réinitialisation MFA/password
- Gestion des statuts

### Besoins (21 permissions)
Gestion des besoins clients
- Création/édition/suppression
- Validation
- Conversion en mission

### Documents (15 permissions)
Gestion documentaire
- Upload/download
- CV et contrats
- Validation documents

### Applications (14 permissions)
Gestion des candidatures
- Postulation
- Suivi candidatures
- Validation/rejet

---

## 🎨 Recommandations d'Attribution

### Pour un nouvel utilisateur interne:
1. **Équipe tech/DevOps:** `admin` ou `super_admin`
2. **Commercial:** `commercial`
3. **RH:** `hr_manager`
4. **Support:** `read_only` (lecture seule)

### Pour un utilisateur externe:
1. **Client entreprise:** `company_admin`
2. **Candidat:** `candidat`
3. **Intérimaire actif:** `interim_user`

### Principes:
- ✅ Commencer avec le minimum de permissions
- ✅ Utiliser les bundles pour grouper les permissions cohérentes
- ✅ Éviter le profil `super_admin` sauf nécessité absolue
- ❌ Ne pas créer de profils custom sans documentation
- ❌ Ne pas hardcoder de permissions dans le code

---

## 📚 Documents Connexes

- **Matrice complète:** `/app/docs/IAM_PROFILE_PERMISSIONS_MATRIX.md`
- **Configuration IAM:** `/app/config/iam_config.yaml`
- **Guide des bundles:** `/app/docs/BUNDLE_PERMISSIONS.md`
- **Audit IAM:** `/app/docs/IAM_AUDIT_EXPERT_REPORT.md`

---

*Dernière mise à jour: 24 Novembre 2025*
