# 🏗️ Refonte Architecture IAM - Documentation Technique

## 📊 État Actuel de l'Architecture (Audit)

### Collections MongoDB
- **profiles**: 16 profils (16 actifs)
- **permissions**: 169 permissions (toutes catégories confondues)
- **iam_groups**: 0 groupes (non utilisé actuellement)
- **users**: 109 utilisateurs (43 sans profils IAM)

### Profils Existants
```
✅ Profils Système:
  - gestionnaire_commercial (0 perms)

✅ Profils Admin:
  - super_admin (117 perms)
  - admin (46 perms)

✅ Profils Métier:
  - hr_manager (6 perms)
  - commercial (6 perms)
  - company_admin (20 perms)
  - team_manager (3 perms)
  - entreprise (17 perms)
  - commercial_custom (22 perms)

✅ Profils Utilisateurs:
  - interim_user (11 perms)
  - applicant (8 perms)
  - role.postulant (20 perms)

✅ Profils Spéciaux:
  - read_only (7 perms)
  - profile_auditor (9 perms)

✅ Profils Test:
  - test_profils (4 perms)
  - test_profile (0 perms)
```

### Distribution des Utilisateurs par Rôle
- interim: 32 utilisateurs
- company: 26 utilisateurs
- candidat: 26 utilisateurs
- intérimaire: 10 utilisateurs
- collaborateur: 6 utilisateurs
- super_admin: 5 utilisateurs
- admin: 3 utilisateurs
- commercial: 1 utilisateur

### ⚠️ Problèmes Identifiés
1. **43 utilisateurs sans profils IAM** → Migration nécessaire
2. **171 permissions orphelines** → Nettoyage nécessaire
3. **Duplication de profils** (applicant vs role.postulant)
4. **Pas de système d'expiration temporelle**
5. **Pas de bundles de capacités réutilisables**
6. **Aucun profil "Restreint" par défaut**

---

## 🎯 Nouvelle Architecture IAM

### 1. Collections MongoDB

#### Collection `profiles` (Profils Métier - UI Visible)
```javascript
{
  "id": "uuid",
  "code": "string",              // Ex: "candidat_confirmed"
  "name": "string",              // Ex: "Candidat Confirmé"
  "description": "string",       // Obligatoire
  "category": "string",          // business|admin|system
  "is_system": boolean,          // Profils système non modifiables
  "is_visible": boolean,         // Visible dans l'UI
  "capability_bundle_ids": [],   // Référence aux bundles
  "permission_ids": [],          // Permissions directes (legacy)
  "parent_profile_id": "uuid",   // Héritage (ex: candidat_15j hérite de restreint)
  "metadata": {
    "priority": number,          // Ordre d'affichage
    "icon": "string",
    "color": "string"
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

#### Collection `capability_bundles` (Bundles de Capacités - Technique)
```javascript
{
  "id": "uuid",
  "code": "string",              // Ex: "missions_manage_own"
  "name": "string",              // Ex: "Gestion Missions (Own)"
  "description": "string",       // Obligatoire
  "category": "string",          // missions|documents|profile|admin|security
  "permission_ids": [],          // Permissions atomiques incluses
  "is_system": boolean,
  "tags": [],                    // Pour recherche/filtrage
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

#### Collection `permissions` (Permissions Atomiques)
```javascript
{
  "id": "uuid",
  "code": "string",              // Format: resource.action.scope
  "name": "string",              // Ex: "Voir Missions Publiées"
  "description": "string",       // Obligatoire
  "resource": "string",          // Ex: "missions"
  "action": "string",            // Ex: "view"
  "scope": "string",             // Ex: "published" | "own" | "all"
  "category": "string",          // Pour regroupement
  "tags": [],
  "is_system": boolean,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

#### Collection `users` (Modifications)
```javascript
{
  // Champs existants...
  "profile_ids": [],             // Profils assignés
  "temporary_profiles": [        // Profils temporaires avec expiration
    {
      "profile_id": "uuid",
      "assigned_at": "ISO8601",
      "expires_at": "ISO8601",
      "reason": "string"
    }
  ],
  "first_login_at": "ISO8601",   // Pour calcul expiration 15j
  "profile_history": [           // Historique des changements
    {
      "profile_id": "uuid",
      "action": "assigned|removed|expired",
      "timestamp": "ISO8601",
      "reason": "string"
    }
  ]
}
```

---

## 🧩 Nouveaux Profils Métier

### 1. Profil "Restreint" (profile.restricted)
**Objectif**: Profil de sécurité minimum (Zero Trust)

**Permissions**:
```
✅ dashboard.view.readonly
✅ missions.view.published
✅ missions.search.public
✅ profile.view.own
✅ security.view.own
```

**Bundles**:
- `readonly_access` (lecture seule générale)
- `public_missions_view` (missions publiques)

**Caractéristiques**:
- Assigné automatiquement à tous les utilisateurs
- Non supprimable
- Système (is_system: true)
- Priorité: 1 (plus haute)

---

### 2. Profil "Utilisateur Défaut 15j" (profile.candidat_temp)
**Objectif**: Profil temporaire pour nouveaux candidats

**Hérite de**: `profile.restricted`

**Permissions additionnelles**:
```
✅ profile.edit.own
✅ security.edit.own (MFA, passkey)
✅ dashboard.customize.own
✅ missions.apply (sauf collaborateurs)
✅ applications.view.own
✅ applications.track.own
✅ documents.upload.own
✅ documents.manage.own
```

**Bundles**:
- Hérite de `readonly_access`
- `profile_self_manage`
- `documents_self_manage`
- `missions_apply`
- `applications_track_own`

**Expiration**:
- Durée: 15 jours glissants
- Base: `first_login_at`
- Action expiration: Downgrade vers `profile.restricted`
- Notification: J-3, J-1

**Caractéristiques**:
- Assigné automatiquement à la création
- Temporaire
- Système (is_system: true)

---

### 3. Profil "Candidat/Postulant" (profile.candidat_confirmed)
**Objectif**: Profil permanent après validation

**Hérite de**: `profile.candidat_temp`

**Permissions identiques** à Candidat 15j mais:
- ✅ Pas d'expiration
- ✅ Accès futurs: formations, IA matching, scoring

**Bundles**:
- Tous ceux de `candidat_temp`
- `advanced_matching` (futur)
- `training_access` (futur)

**Activation**:
- Validation email/téléphone
- Ou validation manuelle admin

---

### 4. Profil "Entreprise" (profile.company)
**Objectif**: Gestionnaire d'entreprise

**Permissions**:
```
✅ entreprises.manage.own
✅ besoins.create.own
✅ besoins.edit.own (draft seulement)
✅ besoins.submit.own
✅ besoins.comment.own
✅ emargements.validate
✅ emargements.annotate
✅ missions.view.own
✅ dashboard.manage.own
```

**Bundles**:
- `company_manage_own`
- `besoins_manage_own`
- `emargements_validate`
- `dashboard_company`

**Sous-rôles IAM**:
- `company_admin` (créer/éditer entreprise)
- `company_manager` (gérer équipes)
- `company_supervisor` (valider émargements)

**Contraintes**:
- ❌ Ne peut pas modifier besoin soumis à JLC
- ❌ Ne peut pas publier missions directement

---

### 5. Profil "Commercial" (profile.commercial)
**Objectif**: Gestionnaire commercial avec scope own/all

**Permissions (granulaires)**:
```
✅ Missions:
  - missions.manage.own
  - missions.manage.all
  - missions.pause
  - missions.publish
  - missions.assign_users

✅ Candidatures:
  - applications.review.all
  - applications.validate.all
  - applications.prescreen

✅ Besoins:
  - besoins.view.all
  - besoins.edit.all
  - besoins.approve
  - besoins.reject

✅ Entreprises:
  - entreprises.create
  - entreprises.edit.all
  - entreprises.archive
  - entreprises.transfer.validate

✅ Autres:
  - cvtech.search
  - dashboard.manage.own
```

**Bundles**:
- `missions_manage_own`
- `missions_manage_all`
- `applications_review`
- `besoins_manage_all`
- `entreprises_manage_all`
- `commercial_tools`

---

### 6. Profil "Paie" (profile.payroll)
**Objectif**: Gestionnaire paie et facturation

**Permissions**:
```
✅ missions.view.all (in_progress)
✅ entreprises.view.all (limited fields)
✅ emargements.view.all
✅ emargements.adjust
✅ invoicing.manage
✅ payroll.calculate
✅ missions.timeline.view
✅ dashboard.payroll
```

**Bundles**:
- `missions_view_active`
- `emargements_manage`
- `payroll_manage`
- `invoicing_manage`

**Restrictions**:
- Accès limité aux données entreprises
- Pas de modification missions

---

### 7. Profil "RRH" (profile.hr_manager)
**Objectif**: Responsable Ressources Humaines

**Permissions**:
```
✅ users.manage
✅ recruitment.validate
✅ medical_visits.trigger
✅ medical_visits.validate
✅ candidat_to_interim.approve
✅ recruitment.participate
✅ applications.view.all
✅ missions.view.open
✅ team_managers.assign
✅ dashboard.hr
```

**Bundles**:
- `users_manage`
- `recruitment_process`
- `medical_compliance`
- `candidat_progression`
- `hr_reporting`

---

## 🔐 Capability Bundles (Exemples)

### Bundle: `readonly_access`
```javascript
{
  "code": "readonly_access",
  "name": "Accès Lecture Seule",
  "permissions": [
    "dashboard.view.readonly",
    "profile.view.own"
  ]
}
```

### Bundle: `missions_manage_own`
```javascript
{
  "code": "missions_manage_own",
  "name": "Gestion Missions (Own)",
  "permissions": [
    "missions.create.own",
    "missions.edit.own",
    "missions.delete.own",
    "missions.view.own"
  ]
}
```

### Bundle: `documents_self_manage`
```javascript
{
  "code": "documents_self_manage",
  "name": "Gestion Documents Personnels",
  "permissions": [
    "documents.upload.own",
    "documents.view.own",
    "documents.delete.own",
    "documents.download.own"
  ]
}
```

---

## 🔄 Plan de Migration

### Phase 1: Préparation (Jour 1)
1. ✅ Audit complet de l'existant
2. ✅ Backup de toutes les collections IAM
3. ✅ Création des nouveaux modèles Pydantic
4. ✅ Création collection `capability_bundles`

### Phase 2: Création des Bundles (Jour 1)
1. Créer tous les capability bundles
2. Mapper permissions existantes vers bundles
3. Tester cohérence des bundles

### Phase 3: Création des Nouveaux Profils (Jour 2)
1. Créer profil `restricted`
2. Créer profil `candidat_temp`
3. Créer profil `candidat_confirmed`
4. Créer profils métier (entreprise, commercial, paie, rrh)
5. Lier bundles aux profils

### Phase 4: Migration Utilisateurs (Jour 2-3)
1. Identifier mapping rôles → profils
2. Assigner profils sans perte de droits
3. Assigner `restricted` à tous
4. Gérer utilisateurs sans profils
5. Historiser les changements

### Phase 5: Système d'Expiration (Jour 3)
1. Implémenter job de vérification expiration
2. Système de notification (J-3, J-1)
3. Downgrade automatique
4. Logs d'audit

### Phase 6: UI Admin (Jour 4)
1. Page gestion bundles
2. Page profils enrichie
3. Filtres et recherche
4. Visualisation hiérarchies
5. Gestion expirations

### Phase 7: Tests & Documentation (Jour 5)
1. Tests unitaires
2. Tests d'intégration
3. Tests non-régression
4. Documentation API
5. Guide utilisateur

---

## 📋 Mapping Migration Utilisateurs

### Rôles Actuels → Nouveaux Profils
```
interim (32 users) → profile.interim_user + profile.restricted
company (26 users) → profile.company + profile.restricted
candidat (26 users) → profile.candidat_confirmed + profile.restricted
intérimaire (10 users) → profile.interim_user + profile.restricted
collaborateur (6 users) → profile.collaborateur + profile.restricted
super_admin (5 users) → profile.super_admin + profile.restricted
admin (3 users) → profile.admin + profile.restricted
commercial (1 user) → profile.commercial + profile.restricted

Sans rôle (43 users):
  - status=pending → profile.candidat_temp + profile.restricted
  - status=active → profile.candidat_confirmed + profile.restricted
  - status=suspended → profile.restricted uniquement
```

### Règles de Migration
1. **Tous les utilisateurs reçoivent `profile.restricted`**
2. **Préserver tous les droits existants**
3. **Nouveaux candidats**: `candidat_temp` (15j) + `restricted`
4. **Candidats validés**: `candidat_confirmed` + `restricted`
5. **Utilisateurs suspendus**: `restricted` uniquement

---

## 🔧 Services et APIs

### IAMService (Unifié)
```python
class IAMService:
    async def get_user_effective_permissions(user_id: str) -> List[Permission]
    async def check_permission(user_id: str, permission: str) -> bool
    async def assign_profile(user_id: str, profile_id: str, temporary: bool = False)
    async def remove_profile(user_id: str, profile_id: str)
    async def check_expirations() -> List[ExpirationEvent]
    async def downgrade_expired_profiles()
    async def get_profile_hierarchy(profile_id: str) -> ProfileHierarchy
    async def resolve_bundles(profile_id: str) -> List[Permission]
```

### API Endpoints (Nouveaux)
```
POST   /api/iam/bundles                   # Créer bundle
GET    /api/iam/bundles                   # Lister bundles
GET    /api/iam/bundles/{id}              # Détails bundle
PUT    /api/iam/bundles/{id}              # Modifier bundle
DELETE /api/iam/bundles/{id}              # Supprimer bundle

GET    /api/iam/profiles/{id}/hierarchy   # Hiérarchie profil
GET    /api/iam/profiles/{id}/effective   # Permissions effectives

POST   /api/iam/users/{id}/profiles/temporary  # Assigner profil temporaire
GET    /api/iam/users/{id}/expirations         # Voir expirations
POST   /api/iam/expirations/check              # Forcer check expirations
```

---

## ⚠️ Contraintes de Non-Régression

### Tests Obligatoires Avant Déploiement
1. ✅ Tous les utilisateurs existants conservent leurs permissions
2. ✅ Aucun endpoint protégé ne devient inaccessible
3. ✅ Admin/SuperAdmin gardent accès complet
4. ✅ Commerciaux conservent leurs accès missions
5. ✅ Entreprises conservent gestion besoins
6. ✅ Candidats peuvent toujours postuler

### Rollback Plan
1. Backup MongoDB avant migration
2. Script de rollback disponible
3. Logs détaillés de toutes modifications
4. Possibilité de restaurer ancienne structure

---

## 📊 Métriques de Succès

### KPIs
- ✅ 0 régression fonctionnelle
- ✅ 100% des utilisateurs migrés
- ✅ 0 perte de permissions
- ✅ Temps réponse API < 200ms
- ✅ Documentation complète
- ✅ Tests coverage > 80%

---

## 🚀 Prochaines Étapes

1. ✅ **Phase 1 terminée** - Audit et architecture
2. 🔄 **Phase 2 en cours** - Implémentation des modèles et bundles
3. ⏳ Phase 3 - Création des profils
4. ⏳ Phase 4 - Migration utilisateurs
5. ⏳ Phase 5 - Système d'expiration
6. ⏳ Phase 6 - Interface admin
7. ⏳ Phase 7 - Tests et documentation

---

**Date de création**: 2025-01-19
**Version**: 1.0
**Auteur**: E1 Fork Agent
