# 🔧 Plan de Correction IAM - Analyse & Solutions

## 📊 Problèmes Identifiés

### ❌ Problème 1: Permissions affichées comme "0"
**Cause racine**: 
- Les nouveaux profils utilisent `capability_bundle_ids` pour stocker les bundles
- Le frontend affiche seulement `profile.permission_ids.length` 
- Les permissions des bundles ne sont PAS comptées
- Le type TypeScript `Profile` ne contient pas `capability_bundle_ids`

**Impact**: 
- 9 nouveaux profils (Restreint, Candidat Temp, etc.) affichent "0 permissions"
- Alors qu'ils ont des permissions via bundles

**Solution**:
1. Ajouter `capability_bundle_ids` au type `Profile` (frontend)
2. Créer un endpoint backend `/api/iam/profiles/{id}/effective-permissions` qui résout bundles → permissions
3. Modifier la page pour afficher le count effectif (direct + bundles)

---

### ❌ Problème 2: Modale d'édition inadéquate
**Causes**:
- Interface mono-colonne (pas de séparation disponibles/attribuées)
- Pas de descriptions visibles
- Pas de recherche/tri
- Possibilité de voir des doublons

**Solution**:
1. Créer un composant `DualColumnPermissionSelector`
2. Colonne gauche: permissions disponibles (filtrées, celles non attribuées)
3. Colonne droite: permissions attribuées
4. Ajouter recherche + tri (catégorie, ressource, action)
5. Afficher descriptions depuis `iam_permissions.description`

---

### ❌ Problème 3: Permissions supprimées réapparaissent (58 permissions)
**Hypothèses à vérifier**:
1. ✅ Pas de configuration IAM par défaut (vérifié - aucune)
2. ✅ Pas de seeds IAM (vérifié - aucun)
3. ⚠️  4 `iam_roles` legacy existent encore (possiblement source du problème)
4. 🔍 À vérifier: Cache frontend (RTK Query)
5. 🔍 À vérifier: Logique de sauvegarde backend

**Investigation nécessaire**:
1. Tester la sauvegarde d'un profil et vérifier MongoDB directement
2. Vérifier si les `iam_roles` legacy interfèrent
3. Analyser le code de `updateProfile` backend
4. Vérifier les tags de cache RTK Query

---

## 🎯 Plan d'Action

### Étape 1: Corriger le comptage des permissions (Problème 1)
- [ ] Modifier le type `Profile` pour inclure `capability_bundle_ids` et `effective_permission_count`
- [ ] Créer endpoint backend pour permissions effectives
- [ ] Modifier l'affichage frontend

### Étape 2: Améliorer la modale (Problème 2)
- [ ] Créer `DualColumnPermissionSelector.tsx`
- [ ] Implémenter recherche + tri
- [ ] Afficher descriptions complètes
- [ ] Gérer les bundles dans l'édition

### Étape 3: Corriger le bug de réinjection (Problème 3)
- [ ] Déboguer la sauvegarde
- [ ] Vérifier les iam_roles legacy
- [ ] Corriger le cache RTK Query si nécessaire
- [ ] Tester la persistance

---

## 🛠️ Contraintes Respectées

✅ Pas de régression
✅ Pas de valeurs en dur
✅ Utilisation de IAMService unifié
✅ Préservation de l'existant
✅ Code factorisé
