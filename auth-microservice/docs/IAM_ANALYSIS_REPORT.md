# 📊 Rapport d'Analyse IAM - AWANA

**Date:** 17 novembre 2025  
**Objectif:** Analyse préalable pour normalisation et amélioration du système IAM

---

## 📈 État Actuel du Système

### Statistiques Globales
- **114 permissions** au total
- **18 profils** métier
- **3 rôles IAM** (postulant, candidat, intérimaire)
- **0 groupes IAM**

### Distribution des Permissions par Type d'Action
```
view/read    : 25 permissions (22%)
create       : 10 permissions (9%)
edit/update  : 9 permissions (8%)
delete       : 10 permissions (9%)
manage       : 15 permissions (13%)
validate     : 4 permissions (3%)
reject       : 1 permission (1%)
autres       : 40 permissions (35%)
```

### Distribution des Scopes
```
organization : 68 permissions (60%)
global       : 35 permissions (31%)
system       : 6 permissions (5%)
own          : 5 permissions (4%)
```

---

## 🔍 Analyse par Ressource

### 1. **Missions** (7 permissions)
**Permissions existantes:**
- `missions.browse` ✅
- `missions.read` ✅
- `missions.create` ✅
- `missions.update` ✅
- `missions.delete` ✅
- `missions.approve` ✅
- `missions.manage` ✅

**Gaps identifiés:**
- ❌ `missions.view_own` - Voir ses propres missions (entreprise)
- ❌ `missions.edit_own` - Modifier ses propres missions (entreprise)
- ⚠️ `missions.view_published` - Voir uniquement les missions publiées
- ⚠️ `missions.validate` - Valider une mission (commercial/admin)
- ⚠️ `missions.reject` - Rejeter une mission

**Recommandations:**
1. Ajouter `missions.view_own` pour entreprises
2. Ajouter `missions.edit_own` pour entreprises
3. Renommer `missions.browse` → `missions.view_published` (ou garder les deux)

---

### 2. **Applications/Candidatures** (5 permissions)
**Permissions existantes:**
- `applications.create` ✅ (scope: own)
- `applications.read_own` ✅
- `applications.update_own` ✅
- `applications.delete_own` ✅
- `applications.manage_own` ✅

**Gaps identifiés:**
- ❌ `applications.view_all` - Voir toutes les candidatures (admin/RH)
- ❌ `applications.edit_all` - Modifier toutes les candidatures (admin)
- ❌ `applications.validate` - Valider une candidature
- ❌ `applications.reject` - Rejeter une candidature

**Recommandations:**
1. Ajouter `applications.view_all` pour admin/RH/commercial
2. Ajouter `applications.validate` pour workflow
3. Ajouter `applications.reject` pour workflow

---

### 3. **Besoins** (7 permissions) ⚠️ RESSOURCE CLÉ
**Permissions existantes:**
- `besoins.create` ✅
- `besoins.read` ✅
- `besoins.edit` ✅
- `besoins.submit` ✅
- `besoins.comment` ✅
- `besoins.validate` ✅
- `besoins.convert_to_mission` ✅

**Gaps identifiés:**
- ❌ `besoins.view_own` - Voir ses propres besoins (entreprise)
- ❌ `besoins.view_all` - Voir tous les besoins (commercial)
- ❌ `besoins.edit_own` - Modifier ses propres besoins (entreprise)
- ❌ `besoins.edit_all` - Modifier tous les besoins (commercial)
- ❌ `besoins.delete_own` - Supprimer ses propres besoins
- ❌ `besoins.reject` - Rejeter un besoin

**Note importante:** La ressource "besoins" est bien nommée et cohérente avec le métier gabonais. Pas besoin de la renommer "mission_request".

**Recommandations:**
1. Ajouter scopes manquants (_own, _all)
2. Clarifier `besoins.read` → devrait être `besoins.view_all`
3. Clarifier `besoins.edit` → devrait être `besoins.edit_own` ou `besoins.edit_all`
4. Ajouter `besoins.reject`

---

### 4. **Entreprises** (4 permissions)
**Permissions existantes:**
- `entreprises.read` ✅ (scope: own - incohérent)
- `entreprises.edit` ✅ (scope: own - incohérent)
- `voir_entreprises` ⚠️ (legacy, à supprimer)
- `modifier_entreprises` ⚠️ (legacy, à supprimer)

**Gaps identifiés:**
- ❌ `entreprises.view_own` - Voir son propre profil entreprise
- ❌ `entreprises.view_all` - Voir toutes les entreprises (admin)
- ❌ `entreprises.edit_own` - Modifier son propre profil
- ❌ `entreprises.edit_all` - Modifier toutes les entreprises (admin)
- ❌ `entreprises.create` - Créer une entreprise
- ❌ `entreprises.delete` - Supprimer une entreprise

**Recommandations:**
1. **URGENT:** Nettoyer les doublons legacy
2. Renommer `entreprises.read` → `entreprises.view_own`
3. Renommer `entreprises.edit` → `entreprises.edit_own`
4. Ajouter `entreprises.view_all` pour admin
5. Ajouter `entreprises.edit_all` pour admin

---

### 5. **Documents** (3 permissions)
**Permissions existantes:**
- `documents.read_own` ✅
- `documents.manage_own` ✅
- `documents.upload_own` ✅

**Gaps identifiés:**
- ❌ `documents.view_own` (alias de read_own)
- ❌ `documents.view_all` - Voir tous les documents (admin/RH)
- ❌ `documents.edit_own` - Modifier ses documents
- ❌ `documents.delete_own` - Supprimer ses documents

**Recommandations:**
1. Ajouter `documents.view_all` pour admin/RH
2. Ajouter `documents.delete_own`
3. Considérer `documents.validate` pour validation RGPD

---

### 6. **Users** (9 permissions)
**Permissions existantes:**
- `users.read` ✅
- `users.write` ✅
- `users.delete` ✅
- `users.edit` ✅
- `users.manage` ✅
- `users.create` ✅
- `users.block` ✅
- `users.unblock` ✅
- `users.impersonate` ✅

**Gaps identifiés:**
- ❌ `users.view_own` - Voir son propre profil
- ❌ `users.view_all` - Voir tous les utilisateurs
- ❌ `users.edit_own` - Modifier son propre profil

**Recommandations:**
1. Ajouter `users.view_own` (différent de `profile.manage_own`)
2. Renommer `users.read` → `users.view_all`

---

## 🔐 Permissions Système

### Existantes (6 permissions)
```
✅ audit.read
✅ system.config.read
✅ system.config.update
✅ system.featureflags.manage
✅ config.manage
✅ config.read
```

### Manquantes
```
❌ system.rbac.manage         - Gérer les rôles/permissions IAM
❌ system.audit.view          - Consulter les logs d'audit complets
❌ system.impersonate         - Impersonner un utilisateur
❌ system.maintenance         - Mettre en maintenance
❌ system.logs.view           - Consulter les logs système
❌ system.apikeys.manage      - Gérer les clés API
❌ system.mfa.bypass          - Bypasser MFA (urgence)
```

---

## 👤 Rôle "Auditor" - Non Existant

**À créer:**
```json
{
  "code": "auditor",
  "label": "Auditeur",
  "description": "Lecture seule sur toutes les ressources pour audit et conformité",
  "permissions": [
    "missions.view_all",
    "applications.view_all",
    "besoins.view_all",
    "entreprises.view_all",
    "users.view_all",
    "documents.view_all",
    "contracts.view_all",
    "system.audit.view",
    "system.logs.view"
  ],
  "level": 50,
  "is_system": true
}
```

**Sécurité:**
- ✅ Aucune permission d'écriture
- ✅ Aucune permission de suppression
- ✅ Aucune permission de validation/rejet
- ✅ Lecture uniquement

---

## 📋 Plan de Normalisation Proposé

### Phase 1: Nettoyage (0 régression)
1. **Supprimer les doublons legacy**
   - `voir_entreprises` → remplacer par `entreprises.view_all`
   - `modifier_entreprises` → remplacer par `entreprises.edit_all`
   - `supprimer_entreprises` → remplacer par `entreprises.delete_all`

2. **Vérifier les références**
   - Chercher dans les profils qui utilise ces permissions legacy
   - Remplacer les références avant suppression
   - Tester avec les utilisateurs concernés

### Phase 2: Ajout des permissions manquantes
1. **Missions**
   - `missions.view_own`
   - `missions.edit_own`
   - `missions.delete_own`
   - `missions.validate`
   - `missions.reject`

2. **Applications**
   - `applications.view_all`
   - `applications.edit_all`
   - `applications.validate`
   - `applications.reject`

3. **Besoins**
   - `besoins.view_own`
   - `besoins.view_all`
   - `besoins.edit_own`
   - `besoins.edit_all`
   - `besoins.delete_own`
   - `besoins.reject`

4. **Entreprises**
   - `entreprises.view_own` (renommer `entreprises.read`)
   - `entreprises.view_all`
   - `entreprises.edit_own` (renommer `entreprises.edit`)
   - `entreprises.edit_all`
   - `entreprises.create`
   - `entreprises.delete`

5. **Documents**
   - `documents.view_all`
   - `documents.edit_own`
   - `documents.delete_own`
   - `documents.validate`

6. **Users**
   - `users.view_own`
   - `users.view_all` (renommer `users.read`)
   - `users.edit_own`

7. **Système**
   - `system.rbac.manage`
   - `system.audit.view`
   - `system.impersonate`
   - `system.maintenance`
   - `system.logs.view`
   - `system.apikeys.manage`
   - `system.mfa.bypass`

### Phase 3: Création du rôle Auditor
1. Créer le rôle `auditor` avec permissions read-only
2. Créer le profil `profile_auditor`
3. Tester avec un utilisateur de test

### Phase 4: Mise à jour des profils existants
1. Mettre à jour `company_admin` avec les nouvelles permissions
2. Mettre à jour `interim_user` si nécessaire
3. Mettre à jour `super_admin` avec les permissions système

---

## ⚠️ Points d'Attention

### Risques identifiés
1. **Régression sur Emergent** : Vérifier que les permissions système ne cassent pas l'intégration
2. **Doublons legacy** : Nécessite migration des références avant suppression
3. **Scopes incohérents** : Certaines permissions ont scope "own" mais le nom ne l'indique pas
4. **Permissions trop larges** : `*.manage` donne souvent trop de droits

### Actions de sécurité
1. ✅ Tester chaque nouveau rôle/permission sur un utilisateur de test
2. ✅ Ne jamais modifier directement en production
3. ✅ Faire un backup MongoDB avant modifications
4. ✅ Documenter chaque changement
5. ✅ Vérifier l'impact sur les workflows existants

---

## 📊 Matrice de Normalisation

| Ressource | Pattern Actuel | Pattern Cible | Action |
|-----------|---------------|---------------|---------|
| missions.browse | ✅ | missions.view_published | Garder les deux |
| missions.read | ✅ | missions.view_all | Ajouter view_all |
| besoins.read | ❌ | besoins.view_all | Renommer |
| besoins.edit | ❌ | besoins.edit_own | Renommer |
| entreprises.read | ❌ | entreprises.view_own | Renommer |
| entreprises.edit | ❌ | entreprises.edit_own | Renommer |
| users.read | ❌ | users.view_all | Renommer |

---

## 🎯 Recommandations Finales

### Priorité Haute (P0)
1. ✅ Nettoyer les doublons legacy (voir_entreprises, etc.)
2. ✅ Ajouter les permissions manquantes pour "besoins" (c'est la ressource métier clé)
3. ✅ Créer le rôle "auditor"

### Priorité Moyenne (P1)
1. ⚠️ Normaliser les scopes (_own, _all)
2. ⚠️ Ajouter les permissions système manquantes
3. ⚠️ Ajouter les permissions de validation/rejet

### Priorité Basse (P2)
1. 📋 Documenter le nouveau système
2. 📋 Créer des tests automatisés pour les permissions
3. 📋 Mettre en place un système de revue des permissions

---

**Prochaine étape:** Validation du plan avec l'utilisateur avant exécution.
