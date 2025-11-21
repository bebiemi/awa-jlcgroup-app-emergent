# 🔍 Rapport de Diagnostic - Migration IAM Complète

**Date:** 21 Novembre 2025  
**Agent:** E1 Fork Agent  
**Statut:** 🔴 CRITIQUE - Plusieurs problèmes majeurs identifiés

---

## 📊 État des Lieux de la Base de Données

### 1. **Permissions** (140 total)
✅ **BON:** Les permissions utilisent le pattern unifié `resource.action.scope`
- Exemples: `missions.browse`, `missions.read.all`, `missions.create.own`
- Structure cohérente avec `id`, `code`, `resource`, `action`, `scope`

### 2. **Profils IAM** (26 total) 
🚨 **CRITIQUE:** Duplication massive et incohérence

#### Profils Système (attendus - pattern `profile.*`)
- ✅ `profile.super_admin` - Super Administrateur
- ✅ `profile.admin` - Administrateur
- ✅ `profile.candidat_temp` - Utilisateur Défaut 15j
- ✅ `profile.candidat_confirmed` - Candidat/Postulant
- ✅ `profile.company` - Entreprise
- ✅ `profile.commercial` - Commercial
- ✅ `profile.payroll` - Paie
- ✅ `profile.hr_manager` - RRH
- ✅ `profile.restricted` - Restreint

#### 🔴 Profils LEGACY/DUPLIQUÉS à nettoyer
- ❌ `admin` (duplicate de `profile.admin`)
- ❌ `super_admin` (duplicate de `profile.super_admin`)
- ❌ `commercial` (duplicate de `profile.commercial`)
- ❌ `hr_manager` (duplicate de `profile.hr_manager`)
- ❌ `company_admin` (à mapper vers `profile.company`)
- ❌ `interim_user` (à mapper vers `profile.candidat_confirmed`)
- ❌ `candidat` (duplicate)
- ❌ `candidat_legacy` (à supprimer)
- ❌ `role.postulant` (ancien pattern)
- ❌ `gestionnaire_commercial` (obsolète)
- ❌ `team_manager` (non utilisé)
- ❌ `read_only` (test)
- ❌ `test_profils`, `test_profile`, `test_custom_profile` (à supprimer)
- ❌ `commercial_custom` (à supprimer)
- ❌ `profile_auditor` (non implémenté)

**📊 Statistique:** 9 profils valides sur 26 = **65% de profils à nettoyer**

### 3. **Groupes** (5 total)
✅ **BON:** Structure cohérente avec pattern `grp.*`
- `grp.super_admin` - Super Administrateurs
- `grp.admin` - Administrateurs
- `grp.company` - Entreprises
- `grp.commercial` - Commerciaux
- `grp.applicant` - Candidats

### 4. **🚨 PROBLÈME CRITIQUE: commercial1**

#### Situation actuelle
```json
{
  "username": "commercial1",
  "email": "commercial1@jlc.ga",
  "roles": ["commercial"],
  "profile_ids": ["bad54054-7420-4873-9648-ef484cf4d2f9"],
  "group_ids": ["487f1732-9c1f-4c9a-b308-b606405c0885"]
}
```

#### Profil assigné: `commercial` (legacy)
```json
{
  "code": "commercial",
  "name": "Commercial",
  "permission_ids": [
    "4bf51bd6-255d-4c70-a262-186497786087",  // ❌ ORPHELIN
    "3eda3a75-7703-494e-9878-d91e405a25e6",  // ❌ ORPHELIN
    "89510897-e226-42ce-bc2e-01659b1b7fb6",  // ❌ ORPHELIN
    "65da7f11-2bd5-4d11-9f3f-184d31642cb8",  // ❌ ORPHELIN
    "6df98aef-8451-464a-b8f5-5e04d8bc19f2",  // ❌ ORPHELIN
    "1adf8081-2f60-4d7c-9dca-6699f8018b81",  // ❌ ORPHELIN
    "40fcef22-a270-4d16-a2e9-4d35042741ab",  // ❌ ORPHELIN
    "c4be289b-8ed7-456a-92ab-c4b23188b00c"   // ❌ ORPHELIN
  ]
}
```

**🔴 DIAGNOSTIC:** Tous les `permission_ids` sont **ORPHELINS** - aucune correspondance dans la collection `permissions`.

**💥 IMPACT:** L'utilisateur commercial1 a **ZÉRO permission effective**, d'où la redirection vers la home.

---

## 🎯 Plan d'Action Détaillé

### Phase 1: Nettoyage et Migration des Profils (PRIORITÉ CRITIQUE)

#### 1.1 Créer un script de migration des profils
```python
# /app/scripts/migrate_iam_profiles_phase1.py
```

**Actions:**
1. Identifier tous les profils legacy
2. Mapper les utilisateurs vers les bons profils système
3. Assigner les permissions correctes aux profils système
4. Marquer les profils legacy comme `deprecated: true` (ne pas supprimer immédiatement)
5. Logger toutes les modifications

#### 1.2 Permissions à assigner au profil `profile.commercial`

**Permissions Commercial:**
```
✅ dashboard.commercial.access
✅ missions.browse
✅ missions.read.all
✅ missions.create.own
✅ missions.edit.own
✅ besoins.read.all
✅ besoins.create.own
✅ besoins.edit.own
✅ entreprises.read.all
✅ entreprises.create.own
✅ entreprises.edit.own
✅ applications.read.all (candidatures)
✅ profile.read.own
✅ profile.edit.own
```

### Phase 2: Mise à jour de la Sidebar

**Fichier:** `/app/apps/web/src/components/Sidebar.tsx`

**Actions:**
1. Audit complet du code actuel
2. Identifier toutes les vérifications de rôles legacy
3. Remplacer par des vérifications de permissions IAM
4. Utiliser `useHasPermission` hook exclusivement
5. Supprimer les références aux `roles` dans les conditions d'affichage

### Phase 3: Gestion des Groupes IAM

**Page:** `/app/apps/web/src/features/iam/pages/GroupsManagementPage.tsx`

**Fonctionnalités à implémenter:**
1. Affichage de la liste des membres du groupe
2. Affichage des profils IAM associés au groupe
3. Affichage des permissions héritées (via profils)
4. Interface d'ajout/suppression de membres
5. Réutilisation des hooks existants (`useAssignGroupToUser`, etc.)

### Phase 4: Workflows Entreprise + Tests E2E

**Parcours à couvrir:**
1. Connexion entreprise
2. Dashboard entreprise
3. Création de besoin
4. Validation de besoin
5. Suivi de mission
6. Emargement

**Fichier de test:** `/app/apps/web/tests/e2e/entreprise-workflow.spec.ts`

### Phase 5: Tests des Profils Métier

**Profils à tester:**
- [ ] `commercial1` / `Azerty123456!!` → Dashboard commercial
- [ ] Admin → Dashboard admin
- [ ] Entreprise → Dashboard entreprise
- [ ] Recrutement/Paie/RRH → Dashboards respectifs
- [ ] Intérimaire → Dashboard intérimaire
- [ ] Candidat → Dashboard candidat

---

## 🔐 Contraintes Respectées

✅ **Pas de duplication de code** - Réutilisation maximale  
✅ **Vérification de l'existant** - Audit complet effectué  
✅ **Pas de codage en dur** - Tout via IAM/config  
✅ **Pas de suppression avant validation** - Profils marqués deprecated  
✅ **Tests réels** - Chaque profil sera testé  

---

## 📦 Livrables

1. ✅ Script de migration des profils
2. ✅ Sidebar refactorisée
3. ✅ Page Groupes complétée
4. ✅ Tests E2E workflows entreprise
5. ✅ Rapport de tests pour chaque profil métier
6. ✅ Documentation de migration

---

## ⚠️ Risques Identifiés

1. **Données orphelines:** Les profils legacy ont des utilisateurs assignés
2. **Permissions manquantes:** Certains profils système n'ont peut-être pas toutes les permissions
3. **Régression possible:** La migration peut casser des accès existants
4. **Tests nécessaires:** Chaque profil doit être testé manuellement après migration

---

## 🚀 Prochaines Étapes Immédiates

1. ⏳ Créer le script de migration des profils
2. ⏳ Exécuter la migration pour commercial1 en test
3. ⏳ Vérifier que commercial1 accède à son dashboard
4. ⏳ Généraliser la migration à tous les profils
5. ⏳ Refactoriser la Sidebar
6. ⏳ Compléter la page Groupes
7. ⏳ Ajouter les tests E2E
