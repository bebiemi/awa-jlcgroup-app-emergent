# 🔍 Audit Complet - Navigation & Routes

**Date:** 21 Novembre 2025  
**Objectif:** Cartographie complète de toutes les routes pour le refactor navigation

---

## 📋 Méthodologie

Pour chaque route, nous documentons :
1. **URL** - Le chemin de la route
2. **Contexte** - Profil métier (entreprise, commercial, candidat, admin)
3. **Permissions attendues** - Selon `ProtectedRoute` dans App.tsx
4. **Permissions réelles** - Utilisées dans les composants
5. **Pattern IAM** - Nouveau (IAM unifié) vs Ancien (roles)
6. **Breadcrumb actuel** - État du fil d'Ariane
7. **Problèmes identifiés** - Bugs, incohérences

---

## 🏢 Routes ENTREPRISE

### Dashboard Entreprise
- **URL:** `/entreprise`
- **Composant:** `CompanyDashboard`
- **Permissions attendues:** `['besoins.create.all', 'besoins.create.own']`
- **Pattern IAM:** ⚠️ MIXTE (utilise permissions mais breadcrumb en dur)
- **Breadcrumb:** "Tableau de bord entreprise"
- **Problèmes:** 
  - Breadcrumb reste quand on navigue vers d'autres contextes
  - Permission `besoins.create.all` non assignée aux entreprises

### Mes Besoins (Liste)
- **URL:** `/entreprise/besoins`
- **Composant:** `BesoinsListPage`
- **Permissions attendues:** `['besoins.read', 'besoins.view.all', 'besoins.view.own']`
- **Pattern IAM:** ✅ NOUVEAU (IAM unifié)
- **Breadcrumb:** "Mes Besoins" → Devrait être "Demandes clientes" pour commercial
- **Problèmes:**
  - Titre en dur "Mes Besoins" → devrait être contextuel
  - Pas de distinction UI entre vue Entreprise et vue Commercial

### Créer un Besoin
- **URL:** `/entreprise/besoins/create`
- **Composant:** `CreateBesoinPage`
- **Permissions attendues:** `['besoins.create.all', 'besoins.create.own']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Tableau de bord entreprise > Mes Besoins > Créer"
- **Problèmes:**
  - Breadcrumb conserve "Tableau de bord entreprise" même si accès commercial

### Détail d'un Besoin
- **URL:** `/entreprise/besoins/:id`
- **Composant:** `BesoinDetailPage`
- **Permissions attendues:** `['besoins.read', 'besoins.view.all', 'besoins.view.own']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** Variable selon contexte
- **Problèmes:** Breadcrumb incohérent

### Éditer un Besoin
- **URL:** `/entreprise/besoins/:id/edit`
- **Composant:** `EditBesoinPage`
- **Permissions attendues:** `['besoins.edit.all', 'besoins.edit.own']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** Chaîne complète avec contexte parent
- **Problèmes:** Héritage du breadcrumb parent

### Candidatures Entreprise
- **URL:** `/entreprise/candidatures`
- **Composant:** `CompanyCandidaturesPage`
- **Permissions attendues:** `['applications.read', 'applications.view.all', 'applications.view.own']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Candidatures"
- **Problèmes:** Aucun

---

## 💼 Routes COMMERCIAL

### Dashboard Commercial
- **URL:** `/commercial`
- **Composant:** `CommercialDashboard`
- **Permissions attendues:** `['dashboard.commercial.access', 'missions.manage.all']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Tableau de bord commercial"
- **Problèmes:** 
  - Permission `missions.manage.all` pas assignée au commercial
  - Résolu en ajoutant `dashboard.commercial.access`

### Besoins Clients (même que /entreprise/besoins)
- **URL:** `/entreprise/besoins` (partagé)
- **Composant:** `BesoinsListPage`
- **Contexte commercial:** ✅ Accessible avec `besoins.view.all`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** Devrait afficher "Demandes clientes" pour commercial
- **Problèmes:**
  - Pas de route dédiée `/commercial/besoins`
  - Titre page en dur
  - Breadcrumb pas contextuel

---

## 🎯 Routes MISSIONS

### Liste des Missions
- **URL:** `/missions`
- **Composant:** `MissionsListPage`
- **Permissions attendues:** `['missions.read', 'missions.browse', 'missions.manage.all']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Missions"
- **Problèmes:** Permission OR - accepte n'importe laquelle des 3

### Détail d'une Mission
- **URL:** `/missions/:id`
- **Composant:** `MissionDetailPage`
- **Permissions attendues:** `['missions.read']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Missions > [Nom de la mission]"
- **Problèmes:** Aucun

### Éditer une Mission
- **URL:** `/missions/:id/edit`
- **Composant:** `EditMissionPage`
- **Permissions attendues:** `['missions.edit.all', 'missions.edit.own']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Missions > [Nom] > Éditer"
- **Problèmes:** Aucun

### Candidatures d'une Mission
- **URL:** `/missions/:id/candidatures`
- **Composant:** `ApplicationsManagementPage`
- **Permissions attendues:** `['applications.manage']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Missions > [Nom] > Candidatures"
- **Problèmes:** Aucun

---

## 👤 Routes CANDIDAT

### Dashboard Candidat
- **URL:** `/candidat` (ou `/interim` ?)
- **Composant:** Variable selon type
- **Permissions attendues:** `['dashboard.candidat.access']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Tableau de bord"
- **Problèmes:** Routes multiples pour le même contexte

### Mes Candidatures
- **URL:** `/mes-candidatures`
- **Composant:** `MesCandidaturesPage`
- **Permissions attendues:** `['applications.read.all', 'applications.read.own']`
- **Pattern IAM:** ✅ NOUVEAU (hook `useCandidateTrackingAccess`)
- **Breadcrumb:** "Mes candidatures"
- **Problèmes:** Aucun (refait récemment)

### Offres/Missions Browse
- **URL:** `/offres`
- **Composant:** `OffresPage`
- **Permissions attendues:** `['missions.browse']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Offres"
- **Problèmes:** Alias `/missions-interim` existe

---

## 🛡️ Routes ADMIN

### Dashboard Admin
- **URL:** `/admin`
- **Composant:** `AdminDashboard`
- **Permissions attendues:** `['admin.dashboard', 'admin.access']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration"
- **Problèmes:** Aucun

### Utilisateurs
- **URL:** `/admin/users`
- **Composant:** `UsersPage`
- **Permissions attendues:** `['users.read', 'users.manage']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration > Utilisateurs"
- **Problèmes:** Aucun

### Validations
- **URL:** `/admin/validations`
- **Composant:** `ValidationsPage`
- **Permissions attendues:** `['validations.manage', 'admin.access']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration > Validations"
- **Problèmes:** Aucun

### Entreprises
- **URL:** `/admin/entreprises`
- **Composant:** `EntreprisesPage`
- **Permissions attendues:** `['entreprises.read', 'entreprises.manage']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration > Entreprises"
- **Problèmes:** Aucun

### IAM - Profils
- **URL:** `/admin/iam/profiles`
- **Composant:** `IAMProfilesPage`
- **Permissions attendues:** `['iam.profiles.manage', 'iam.groups.manage']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration > IAM > Profils"
- **Problèmes:** Aucun

### IAM - Groupes
- **URL:** `/admin/iam/groups`
- **Composant:** `GroupsManagementPage`
- **Permissions attendues:** `['iam.groups.manage', 'iam.profiles.manage']`
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration > IAM > Groupes"
- **Problèmes:** Page incomplète (affichage membres à ajouter)

### Configuration
- **URLs multiples:** `/admin/references`, `/admin/countries`, `/admin/rules`, etc.
- **Pattern IAM:** ✅ NOUVEAU
- **Breadcrumb:** "Administration > Configuration > [Section]"
- **Problèmes:** Aucun

---

## 📊 Analyse des Patterns IAM

### ✅ Routes avec Pattern IAM Unifié (Nouveau)
**Total:** ~95% des routes

**Caractéristiques:**
- Utilise `ProtectedRoute` avec `requiredPermissions`
- Permissions au format `resource.action.scope`
- Vérifications via `useHasPermission` hook
- Pas de référence aux `roles`

**Exemples:**
```tsx
<ProtectedRoute requiredPermissions={['missions.read']}>
  <MissionDetailPage />
</ProtectedRoute>
```

### ⚠️ Routes avec Pattern Mixte
**Total:** ~5% des routes

**Problèmes:**
- Composants internes utilisent encore `user.roles`
- Breadcrumb codé en dur
- Conditions multiples (roles + permissions)

**À corriger:**
- Dashboard Entreprise
- Quelques pages admin legacy

### ❌ Routes avec Ancien Pattern (Roles)
**Total:** 0% (tous migrés)

---

## 🚨 Problèmes Identifiés - Synthèse

### 1. **Breadcrumb Incohérent** (CRITIQUE)
**Symptômes:**
- Conserve le contexte du dashboard précédent
- Ex: "Tableau de bord entreprise > Mes Besoins" alors qu'on est en contexte commercial

**Cause:**
- Pas de gestion centralisée du breadcrumb
- Chaque page gère son propre breadcrumb
- Pas de reset lors du changement de contexte

**Impact:** UX dégradée, confusion utilisateur

### 2. **Titres de Pages en Dur** (MAJEUR)
**Exemples:**
- "Mes Besoins" → devrait être "Demandes clientes" pour commercial
- Pas de contextualisation par profil

**Cause:**
- Labels codés en dur dans les composants
- Pas d'utilisation de i18n contextuel

**Impact:** Incohérence terminologique

### 3. **Routes Partagées Sans Différenciation** (MAJEUR)
**Exemples:**
- `/entreprise/besoins` utilisé par Entreprise ET Commercial
- Même composant, même UI, mais contexte différent

**Cause:**
- Pas de templates réutilisables
- Logique métier pas factorisée

**Impact:** Maintenance difficile, UX non optimale

### 4. **Permissions OR Trop Larges** (MINEUR)
**Exemples:**
- Route accepte `permission1` OU `permission2` OU `permission3`
- Difficulté à tracer qui a accès à quoi

**Cause:**
- Migration progressive IAM
- Backward compatibility

**Impact:** Sécurité moins précise

### 5. **Sidebar Non Centralisée** (MAJEUR)
**Symptômes:**
- Menu codé en dur par contexte
- Duplication de logique
- Ajout d'un menu = modification à 3-4 endroits

**Cause:**
- Pas de configuration centralisée de navigation

**Impact:** Maintenance coûteuse

---

## 🎯 Recommandations Phase 2

### Priorité 1 - Configuration Navigation Centralisée
Créer `/app/apps/web/src/config/navigation.config.ts` avec :
- Toutes les routes par contexte
- Labels via i18n
- Permissions requises
- Hiérarchie parent/enfant pour breadcrumb

### Priorité 2 - Hooks de Navigation
Créer:
- `useNavigationConfig()` - Accès à la config
- `useBreadcrumb(currentPath)` - Génération breadcrumb
- `useSidebarItems(context)` - Items sidebar filtrés IAM
- `useCurrentContext()` - Détection contexte utilisateur

### Priorité 3 - Templates Réutilisables
Créer:
- `NeedListTemplate` pour Besoins (Entreprise + Commercial)
- `ApplicationTrackingTemplate` pour Candidatures
- `DashboardTemplate` générique

### Priorité 4 - Layouts par Contexte
Créer:
- `EnterpriseLayout`
- `CommercialLayout`
- `CandidateLayout`
- `AdminLayout`

Tous utilisant les hooks centralisés.

---

## 📈 Métriques Cibles

**Avant refactor:**
- Routes avec breadcrumb cohérent: ~60%
- Routes utilisant config centralisée: 0%
- Composants réutilisables: ~30%
- Maintenance (temps ajout menu): 30min

**Après refactor:**
- Routes avec breadcrumb cohérent: 100%
- Routes utilisant config centralisée: 100%
- Composants réutilisables: 80%
- Maintenance (temps ajout menu): 5min

---

**Audit complété le:** 21 Novembre 2025, 01:35 UTC  
**Prochaine étape:** Phase 2 - Implémentation du noyau navigation
