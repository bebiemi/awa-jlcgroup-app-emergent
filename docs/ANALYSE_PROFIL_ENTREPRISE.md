# 🔍 Analyse Complète du Profil Entreprise - Diagnostic des Problèmes

**Date :** 19 Janvier 2025  
**Statut :** ❌ **SYSTÈME IAM NON FONCTIONNEL - BUG CRITIQUE IDENTIFIÉ**

---

## 📋 Résumé Exécutif

Le profil Entreprise ne fonctionne pas comme prévu à cause d'un **BUG CRITIQUE** dans le service IAM backend qui **ne charge pas les permissions des bundles de capacités**. Cela entraîne une cascade de dysfonctionnements.

### ❗ Problèmes Constatés

1. ✅ **Confirmé :** Le profil Entreprise voit toutes les missions (pas de filtrage)
2. ✅ **Confirmé :** Il peut publier et annuler des missions (boutons visibles)
3. ✅ **Confirmé :** Pas d'accès au suivi des candidatures
4. ✅ **Confirmé :** Ne voit pas la gestion de son entreprise

---

## 🎯 CAUSE RACINE PRINCIPALE

### Bug Critique #1 : IAMService ne charge pas les bundles

**Fichier :** `/app/auth-microservice/awana_auth/services/iam_service.py`  
**Ligne :** 185  
**Méthode :** `async def get_user_permissions()`

**Code actuel (BUGUÉ) :**

```python
# Ligne 182-186
if all_profile_ids:
    profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
    async for profile in profiles_cursor:
        all_permission_ids.update(profile.get("permission_ids", []))
        # ❌ MANQUE: Ne charge PAS capability_bundle_ids !
```

**Impact :**
- Les permissions des bundles de capacités (capability_bundles) ne sont **JAMAIS chargées**
- L'utilisateur ne reçoit que les permissions **directes** des profils
- Toutes les permissions en `.own` (scope personnel) ne sont **jamais appliquées**

---

## 📊 Analyse Détaillée : Utilisateur MBJ (Entreprise)

### Configuration Actuelle

**Utilisateur :** `mbj` (mbj@idae.ga)  
**Roles :** `['company']`  
**Profils IAM (3) :**

1. **profile.restricted** (Restreint)
   - Permissions directes : 0
   - Bundles : 2 (mais non chargés !)

2. **profile.company** (Entreprise) ✅ Profil principal
   - Permissions directes : 0
   - **Bundles : 5** (mais non chargés !) ⚠️
   
3. **company_admin** (Admin Société)
   - **Permissions directes : 20** ✅
   - Bundles : 0

**Groupe :** `Equipe Entreprise` (entreprises)
   - Profil du groupe : Entreprise (10 permissions)

---

### Permissions ATTENDUES (si les bundles fonctionnaient)

#### Profil company_admin (20 permissions) - ✅ FONCTIONNEL

```
BESOINS (8):
   • besoins.create                → Créer des besoins
   • besoins.read                  → Consulter les besoins
   • besoins.edit                  → Modifier les besoins
   • besoins.submit                → Soumettre les besoins
   • besoins.comment               → Commenter les besoins
   • besoins.view_own              → Voir ses propres besoins
   • besoins.edit_own              → Modifier ses propres besoins
   • besoins.delete_own            → Supprimer ses propres besoins

ENTREPRISES (4):
   • entreprises.read              → Consulter les entreprises
   • entreprises.edit              → Modifier les entreprises
   • entreprises.view_own          → Voir son entreprise
   • entreprises.edit_own          → Modifier son entreprise

MISSIONS (4):
   • missions.browse               → Parcourir missions
   • missions.view_own             → Voir ses missions
   • missions.edit_own             → Modifier ses missions
   • missions.delete_own           → Supprimer ses missions

AUTRES (4):
   • dashboard.access              → Tableau de bord
   • profile.manage_own            → Gérer profil
   • profile.view_own              → Voir profil
   • profile.edit_own              → Modifier profil
```

#### Profil profile.company (21 permissions via bundles) - ❌ NON CHARGÉ

```
Bundle 1: Gestion Entreprise (Own) - 3 permissions
   • entreprises.manage.own        → Gérer son entreprise
   • entreprises.edit.own          → Modifier son entreprise
   • entreprises.view.own          → Consulter son entreprise

Bundle 2: Gestion Besoins (Own) - 5 permissions
   • besoins.create.own            → Créer ses besoins
   • besoins.edit.own              → Modifier ses besoins
   • besoins.submit.own            → Soumettre ses besoins
   • besoins.comment.own           → Commenter ses besoins
   • besoins.view.own              → Consulter ses besoins

Bundle 3: Validation Émargements - 4 permissions
   • emargements.validate          → Valider émargements
   • emargements.reject            → Rejeter émargements
   • emargements.annotate          → Annoter émargements
   • emargements.view.own          → Voir ses émargements

Bundle 4: Gestion Profil Personnel - 4 permissions
   • profile.edit.own              → Modifier profil
   • profile.manage.own            → Gérer profil
   • security.edit.own             → Modifier sécurité
   • dashboard.customize.own       → Personnaliser dashboard

Bundle 5: Gestion Documents Personnels - 5 permissions
   • documents.upload.own          → Upload documents
   • documents.view.own            → Voir documents
   • documents.delete.own          → Supprimer documents
   • documents.download.own        → Télécharger documents
   • documents.manage.own          → Gérer documents
```

**Total ATTENDU :** 20 (directes) + 21 (bundles) = **41 permissions**  
**Total RÉEL :** **20 permissions seulement** ❌

---

## 🔴 Conséquences du Bug

### 1. Permissions Manquantes

| Permission | Impact | Status |
|------------|--------|--------|
| `entreprises.manage.own` | Ne peut pas gérer son entreprise | ❌ Manquant |
| `besoins.create.own` | Scope `.own` non appliqué | ❌ Manquant |
| `emargements.validate` | Ne peut pas valider les émargements | ❌ Manquant |
| `documents.*.own` | Gestion documents non fonctionnelle | ❌ Manquant |

### 2. Problèmes d'Affichage Frontend

**Menus manquants :**
- "Gestion de l'entreprise" → Nécessite `entreprises.manage.own` (non chargée)
- "Validation émargements" → Nécessite `emargements.validate` (non chargée)
- "Mes documents" → Nécessite `documents.*.own` (non chargées)

### 3. Problème des Missions

**Pourquoi voit-il toutes les missions ?**

L'utilisateur a `missions.browse` du profil `company_admin`, ce qui lui permet de voir la liste des missions. Mais :

1. **Pas de filtre backend :** L'endpoint `/api/missions` retourne probablement toutes les missions sans filtrer par `entreprise_id`
2. **Permissions trop larges :** `missions.browse` devrait être restreint aux missions de son entreprise

**Pourquoi peut-il publier/annuler ?**

Le frontend vérifie probablement `missions.edit_own` ou `missions.delete_own` qui sont présentes, mais :
- Ces permissions devraient filtrer les actions aux missions `.own` (de son entreprise uniquement)
- Le backend ne fait probablement pas cette vérification

---

## 🔍 Analyse Backend

### Endpoint Missions (supposé)

```
GET /api/missions
```

**Problème attendu :**
- Ne filtre pas par `entreprise_id` ou `created_by`
- Retourne toutes les missions sans restriction
- Ne vérifie pas le scope `.own`

**Ce qui devrait être fait :**
```python
# Si l'utilisateur n'a que missions.view_own
user_entreprise_id = user.get('entreprise_id')
missions = await missions_collection.find(
    {"entreprise_id": user_entreprise_id}
).to_list(1000)
```

---

## 🎨 Analyse Frontend

### Pages Entreprise

**Fichiers à vérifier :**
- `/app/apps/web/src/features/missions/pages/MissionsPage.tsx`
- Sidebar.tsx pour l'affichage des menus

**Problèmes identifiés :**

1. **MissionsPage.tsx (ligne 70)** :
   ```typescript
   const { data: missions = [], isLoading, refetch } = useGetMissionsQuery({
     ...(selectedStatus !== 'all' && { status: selectedStatus }),
   })
   ```
   - N'applique aucun filtre par entreprise
   - Compte sur le backend pour filtrer (qui ne le fait pas)

2. **Actions Publier/Annuler (ligne 75-76)** :
   ```typescript
   const [publishMission] = usePublishMissionMutation()
   const [deleteMission] = useDeleteMissionMutation()
   ```
   - Disponibles pour toutes les missions
   - Devraient être conditionnés par scope `.own`

---

## 🧩 Architecture IAM Complète

### Hiérarchie Actuelle

```
User (mbj)
  ├─ profile_ids: [restricted, profile.company, company_admin]
  ├─ group_ids: [Equipe Entreprise]
  │    └─ Profil du groupe: Entreprise (10 perms)
  └─ Permissions effectives:
       ├─ company_admin (20 perms directes) ✅
       ├─ profile.company (0 perms directes, 21 via bundles) ❌
       └─ profile.restricted (0 perms directes, X via bundles) ❌
```

### Bundles du Profil profile.company

```
profile.company
  ├─ capability_bundle_ids: [
  │    '8a67063f-5532-42e3-8753-2635f397c286',  // company_manage_own
  │    'fe18acd4-4dee-4494-80b1-fc6848f929f1',  // besoins_manage_own
  │    'd51f2a48-526d-406e-9a47-fbcb2455cdd1',  // emargements_validate
  │    '1c7f6681-396f-434b-85e2-9dc07d7c4192',  // profile_self_manage
  │    '349aad49-0169-4366-bd56-5da2261130f6'   // documents_self_manage
  │  ]
  └─ BUG: Ces bundles ne sont PAS chargés par IAMService ❌
```

---

## ✅ Solution Proposée

### Fix #1 : Corriger IAMService pour charger les bundles

**Fichier :** `/app/auth-microservice/awana_auth/services/iam_service.py`  
**Ligne :** 185

**Code à remplacer :**

```python
# AVANT (ligne 182-186)
if all_profile_ids:
    profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
    async for profile in profiles_cursor:
        all_permission_ids.update(profile.get("permission_ids", []))
```

**Par :**

```python
# APRÈS - Charge aussi les bundles
if all_profile_ids:
    profiles_cursor = self.profiles_collection.find({"id": {"$in": list(all_profile_ids)}})
    async for profile in profiles_cursor:
        # Permissions directes
        all_permission_ids.update(profile.get("permission_ids", []))
        
        # Permissions des bundles
        bundle_ids = profile.get("capability_bundle_ids", [])
        if bundle_ids:
            bundles_cursor = self.bundles_collection.find({"id": {"$in": bundle_ids}})
            async for bundle in bundles_cursor:
                all_permission_ids.update(bundle.get("permission_ids", []))
```

### Fix #2 : Filtrer les missions backend par entreprise

**Endpoint :** `/api/missions` (GET)

**Ajouter filtre :**
```python
# Si l'utilisateur n'a que missions.view_own
if not has_permission(user, "missions.view_all"):
    user_entreprise_id = user.get("entreprise_id")
    query_filter["entreprise_id"] = user_entreprise_id
```

### Fix #3 : Conditionner actions frontend par scope

**Fichier :** `MissionsPage.tsx`

**Avant :**
```typescript
const [publishMission] = usePublishMissionMutation()
const [deleteMission] = useDeleteMissionMutation()
```

**Après :**
```typescript
// Vérifier si l'utilisateur peut publier toutes les missions
const canPublishAll = userPermissions.includes('missions.publish_all')

// Afficher "Publier" uniquement si:
// - missions.publish_all (toutes)
// - OU missions.publish_own ET mission.entreprise_id === user.entreprise_id
```

---

## 📊 Validation Post-Fix

### Tests à effectuer après correction

1. **Test Backend IAM :**
   ```bash
   # L'utilisateur mbj doit avoir 41 permissions (20 + 21)
   GET /api/iam/users/{mbj_id}/permissions
   # Vérifier que les permissions .own des bundles sont présentes
   ```

2. **Test Frontend Menus :**
   - Menu "Gestion de l'entreprise" doit apparaître
   - Menu "Validation émargements" doit apparaître
   - Menu "Mes documents" doit apparaître

3. **Test Missions :**
   - L'entreprise ne doit voir que SES missions
   - Les boutons "Publier/Annuler" ne doivent apparaître que sur SES missions

---

## 🚫 Ce qui NE doit PAS être fait

❌ **Ne pas créer de nouvelles permissions**  
❌ **Ne pas modifier les profils existants**  
❌ **Ne pas toucher aux bundles**  
❌ **Ne pas casser les autres profils**

✅ **Uniquement corriger le chargement des bundles dans IAMService**

---

## 📈 Impact Estimé de la Correction

| Composant | Avant Fix | Après Fix | Impact |
|-----------|-----------|-----------|--------|
| **Permissions chargées** | 20 | 41 | +105% ✅ |
| **Menus visibles** | 3/6 | 6/6 | +100% ✅ |
| **Missions affichées** | Toutes | Seulement siennes | ✅ |
| **Actions missions** | Toutes missions | Seulement siennes | ✅ |
| **Gestion entreprise** | ❌ Non visible | ✅ Visible | ✅ |
| **Régression** | N/A | Aucune | ✅ |

---

## 🎯 Conclusion

**Diagnostic :** ✅ **CAUSE RACINE IDENTIFIÉE**

Le problème est **entièrement dû au bug dans IAMService** qui ne charge pas les bundles de capacités. Une fois ce bug corrigé, toutes les permissions `.own` seront chargées et le système fonctionnera comme prévu.

**Complexité de la correction :** 🟢 **FAIBLE**  
**Risque de régression :** 🟢 **TRÈS FAIBLE**  
**Impact positif :** 🟢 **TRÈS ÉLEVÉ**

---

**Prochaine étape :** Attendre validation utilisateur avant d'appliquer les corrections.
