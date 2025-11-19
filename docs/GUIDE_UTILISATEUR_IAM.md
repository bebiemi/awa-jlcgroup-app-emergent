# 📘 Guide Utilisateur IAM - Documentation Complète

**Version :** 2.0  
**Date :** 19 Janvier 2025  
**Public :** Administrateurs, Gestionnaires, Utilisateurs

---

## 🎯 Qu'est-ce que l'IAM ?

**IAM (Identity and Access Management)** est le système qui gère qui peut faire quoi dans l'application.

**En bref :**
- **Qui** = Utilisateur
- **Quoi** = Permission
- **Comment** = Profil + Bundle

---

## 📚 Table des Matières

1. [Concepts de Base](#1-concepts-de-base)
2. [Pour les Utilisateurs](#2-pour-les-utilisateurs)
3. [Pour les Administrateurs](#3-pour-les-administrateurs)
4. [Gestion des Profils](#4-gestion-des-profils)
5. [Gestion des Permissions](#5-gestion-des-permissions)
6. [Gestion des Bundles](#6-gestion-des-bundles)
7. [Résolution de Problèmes](#7-résolution-de-problèmes)
8. [FAQ](#8-faq)

---

## 1. Concepts de Base

### 🧩 Les 4 Éléments Principaux

#### 1.1 Utilisateur

**C'est vous !** Chaque personne qui se connecte à l'application.

**Caractéristiques :**
- Nom d'utilisateur unique
- Email
- Mot de passe
- **Profils assignés** (définissent vos droits)

#### 1.2 Permission

**Une autorisation spécifique** pour faire une action.

**Format :** `resource.action.scope`

**Exemples :**
```
missions.create.own      → Créer SES propres missions
missions.view.all        → Voir TOUTES les missions
documents.upload.own     → Télécharger SES documents
users.manage             → Gérer les utilisateurs
```

**Les 3 scopes :**
- `.own` = Vos ressources uniquement
- `.all` = Toutes les ressources
- (aucun) = Permission générale

#### 1.3 Bundle (Paquet de Capacités)

**Un ensemble cohérent de permissions** pour une fonctionnalité.

**Exemple :** Bundle "Gestion Entreprise"
```
✓ entreprises.manage.own
✓ entreprises.edit.own
✓ entreprises.view.own
```

**Avantage :** Au lieu d'assigner 50 permissions une par une, on assigne 1 bundle qui contient ces 50 permissions.

#### 1.4 Profil

**Votre rôle dans l'application** (Entreprise, Commercial, Candidat, etc.)

**Un profil contient :**
- Permissions directes (optionnel)
- Bundles de capacités (recommandé)

**Exemple :** Profil "Entreprise"
```
Permissions directes: 0
Bundles: 5 bundles
  → company_manage_own (3 permissions)
  → besoins_manage_own (5 permissions)
  → emargements_validate (4 permissions)
  → profile_self_manage (4 permissions)
  → documents_self_manage (5 permissions)

Total effectif: 21 permissions
```

### 🔗 Comment ça s'assemble ?

```
Vous (Utilisateur)
  ↓
Profil(s) assigné(s)
  ↓
├─ Permissions directes → Droits immédiatement accordés
└─ Bundles
     ↓
     Permissions des bundles → Droits accordés
       
RÉSULTAT = Union de toutes les permissions
```

---

## 2. Pour les Utilisateurs

### 2.1 Voir Vos Permissions

**Étape 1 :** Cliquer sur votre profil en haut à droite

**Étape 2 :** Aller dans "Mon Profil"

**Étape 3 :** Section "Mes Permissions"

Vous verrez :
- ✅ Votre profil actuel (ex: "Entreprise")
- ✅ Liste de vos permissions
- ✅ Ce que vous pouvez faire

### 2.2 Demander des Permissions Supplémentaires

**Si vous avez besoin d'accès supplémentaires :**

1. Contacter votre administrateur
2. Expliquer ce dont vous avez besoin
3. L'admin peut :
   - Vous assigner un autre profil
   - Ajouter des permissions spécifiques

**❌ Vous ne pouvez PAS :**
- Modifier vos propres permissions
- Vous auto-assigner des profils

### 2.3 Comprendre les Messages d'Erreur

#### "Accès refusé" ou "403 Forbidden"

**Signification :** Vous n'avez pas la permission nécessaire

**Que faire :**
1. Noter quelle action vous tentiez
2. Contacter l'admin
3. Demander la permission manquante

**Exemple :**
```
Vous essayez de publier une mission
→ Erreur: "Permission refusée"
→ Besoin de: missions.publish
→ Demander à l'admin
```

#### "Non autorisé" avec scope `.own`

**Signification :** Vous avez la permission, mais pas pour CETTE ressource

**Exemple :**
```
Permission: missions.edit.own
→ Vous pouvez éditer VOS missions
→ Mais pas les missions des autres

Solution: Vérifier que c'est bien votre ressource
```

---

## 3. Pour les Administrateurs

### 3.1 Accéder à l'Interface Admin IAM

**Navigation :**
```
Menu principal
  → Administration
    → IAM (Gestion des Accès)
```

**Vous verrez 5 onglets :**
1. 📊 Vue d'ensemble - Statistiques
2. 👥 Profils - Gérer les rôles
3. 🔑 Permissions - Voir toutes les permissions
4. 📦 Bundles - Gérer les paquets
5. 🛡️ Audit - Vérifier l'intégrité

### 3.2 Vue d'Ensemble

**Indicateurs Clés :**

| Indicateur | Signification | Bon Signe |
|-----------|---------------|-----------|
| Total profils | Nombre de rôles | 10-30 profils |
| Permissions | Droits disponibles | 200-300 permissions |
| Bundles | Paquets réutilisables | 20-40 bundles |
| Profils vides | Sans permissions | ⚠️ 0 de préférence |

**Alertes à surveiller :**

🟢 **Vert** = Tout va bien
```
✓ Format moderne respecté
✓ Bonne utilisation des bundles
✓ Aucune référence orpheline
```

🟡 **Jaune** = Attention
```
⚠️ X profils vides
⚠️ Permissions non utilisées
```

🔴 **Rouge** = Action requise
```
❌ Références orphelines
❌ Doublons détectés
❌ Format legacy présent
```

### 3.3 Actions Courantes

#### Créer un Nouvel Utilisateur

**Étape 1 :** Utilisateurs → Nouveau

**Étape 2 :** Remplir les informations
- Nom d'utilisateur
- Email
- Mot de passe temporaire

**Étape 3 :** **IMPORTANT** - Assigner un profil
- ⚠️ Sans profil = accès restreint minimal
- ✅ Choisir le profil approprié

**Profils Courants :**
- **Entreprise** → Pour les clients entreprises
- **Commercial** → Pour l'équipe commerciale
- **Candidat** → Pour les intérimaires
- **Admin** → Pour les administrateurs

#### Modifier les Permissions d'un Utilisateur

**Option A : Changer de Profil**

C'est la méthode **recommandée**.

```
1. Trouver l'utilisateur
2. Modifier → Section "Profils"
3. Retirer ancien profil
4. Ajouter nouveau profil
5. Sauvegarder
```

**Option B : Créer un Profil sur Mesure**

Si aucun profil existant ne convient :

```
1. IAM → Profils → Nouveau
2. Nom du profil (ex: "Commercial Senior")
3. Sélectionner des bundles
4. Ajouter permissions spécifiques si besoin
5. Sauvegarder
6. Assigner ce profil à l'utilisateur
```

---

## 4. Gestion des Profils

### 4.1 Voir Tous les Profils

**Navigation :** IAM → Onglet "Profils"

**Informations affichées :**
- Nom du profil
- Code technique
- Nombre de permissions directes
- Nombre de bundles
- Total effectif de permissions

### 4.2 Créer un Nouveau Profil

**🎯 Bonnes Pratiques :**
- ✅ Utiliser des bundles (réutilisables)
- ✅ Nom descriptif (ex: "Gestionnaire Paie")
- ✅ Description claire
- ❌ Éviter trop de permissions directes

**Étape par Étape :**

1. **Nouveau Profil** → Cliquer sur "+ Nouveau profil"

2. **Informations Générales**
   ```
   Nom: Gestionnaire Paie
   Code: payroll_manager
   Description: Gestion complète de la paie
   Catégorie: business
   ```

3. **Sélectionner des Bundles** (Recommandé)
   ```
   ✓ payroll_manage (gestion paie)
   ✓ users_view (voir utilisateurs)
   ✓ reports_generate (générer rapports)
   ```

4. **Permissions Spécifiques** (Optionnel)
   ```
   Ajouter uniquement des permissions
   qui n'existent dans aucun bundle
   ```

5. **Sauvegarder**

### 4.3 Modifier un Profil Existant

**⚠️ ATTENTION :** Modifier un profil affecte **TOUS** les utilisateurs qui l'ont.

**Étapes Sécurisées :**

1. **Vérifier l'Impact**
   ```
   Profil → "X utilisateurs"
   → Liste des utilisateurs affectés
   ```

2. **Si Profil Protégé**
   ```
   ⚠️ Les profils système sont verrouillés
   → Créer un nouveau profil à la place
   ```

3. **Modifications Possibles**
   - ✅ Ajouter des bundles
   - ✅ Ajouter des permissions
   - ⚠️ Retirer des permissions (vérifier impact)

4. **Sauvegarder et Tester**
   ```
   → Se connecter avec un compte test
   → Vérifier que tout fonctionne
   ```

### 4.4 Supprimer un Profil

**⚠️ Conditions :**
- Le profil ne doit pas être protégé
- Aucun utilisateur ne doit l'avoir
- Aucun groupe ne doit le référencer

**Étapes :**
1. Retirer le profil de tous les utilisateurs
2. Retirer des groupes
3. Supprimer le profil

---

## 5. Gestion des Permissions

### 5.1 Comprendre la Liste des Permissions

**Navigation :** IAM → Onglet "Permissions"

**Colonnes :**

| Colonne | Description | Exemple |
|---------|-------------|---------|
| Code | Identifiant unique | `missions.create.own` |
| Nom | Description courte | "Créer ses missions" |
| Resource | Type de ressource | `missions` |
| Action | Type d'action | `create` |
| Scope | Portée | `own` / `all` |
| Catégorie | Regroupement | `missions` |

### 5.2 Rechercher une Permission

**Barre de Recherche :** En haut de la liste

**Recherche par :**
- Code (ex: `missions.create`)
- Nom (ex: "Créer")
- Resource (ex: `documents`)

**Filtres :**
- Par catégorie (missions, users, documents...)
- Par scope (.own, .all)
- Par resource

### 5.3 Créer une Nouvelle Permission

**⚠️ Réservé aux Super Admins**

**Bonnes Pratiques :**

1. **Vérifier qu'elle n'existe pas déjà**
   ```
   Rechercher dans la liste existante
   ```

2. **Respecter le Format**
   ```
   ✅ resource.action.scope
   ✅ documents.upload.own
   ❌ upload_documents (legacy)
   ```

3. **Formulaire de Création**
   ```
   Code: documents.approve
   Nom: Approuver les documents
   Description: Autoriser l'approbation des documents
   Resource: documents
   Action: approve
   Scope: (vide si général)
   Catégorie: documents
   ```

4. **Assigner à un Bundle ou Profil**
   ```
   Ne pas créer de permission orpheline
   → L'ajouter immédiatement à un bundle/profil
   ```

### 5.4 Permissions Sensibles

**⚠️ Permissions à Manipuler avec Précaution :**

| Permission | Risque | Qui Devrait l'Avoir |
|-----------|--------|---------------------|
| `users.delete` | 🔴 Élevé | Super Admin uniquement |
| `*.all` | 🔴 Élevé | Admins uniquement |
| `payments.manage` | 🟠 Moyen | Gestionnaires paie |
| `documents.delete.all` | 🟠 Moyen | Admins + Managers |

**Principe du Moindre Privilège :**
```
✅ Donner le minimum nécessaire
✅ Préférer .own à .all
✅ Réviser régulièrement
```

---

## 6. Gestion des Bundles

### 6.1 Qu'est-ce qu'un Bundle ?

**Un bundle = Un ensemble cohérent de permissions**

**Avantages :**
- ✅ Réutilisable sur plusieurs profils
- ✅ Plus facile à maintenir
- ✅ Cohérence garantie

**Exemple :** Bundle "Gestion Documents Personnels"
```
✓ documents.upload.own
✓ documents.view.own
✓ documents.delete.own
✓ documents.download.own
✓ documents.manage.own
```

### 6.2 Voir les Bundles Existants

**Navigation :** IAM → Onglet "Bundles"

**Informations :**
- Nom du bundle
- Code technique
- Description
- Nombre de permissions
- Catégorie

### 6.3 Créer un Nouveau Bundle

**Quand Créer un Bundle ?**
- ✅ Vous avez un ensemble de permissions qui vont toujours ensemble
- ✅ Ces permissions représentent une fonctionnalité
- ✅ Plusieurs profils en auront besoin

**Étapes :**

1. **Nouveau Bundle**
   ```
   IAM → Bundles → + Nouveau bundle
   ```

2. **Informations**
   ```
   Nom: Gestion Candidatures (Own)
   Code: applications_manage_own
   Description: Gérer ses propres candidatures
   Catégorie: applications
   ```

3. **Sélectionner les Permissions**
   ```
   ✓ applications.create.own
   ✓ applications.view.own
   ✓ applications.edit.own
   ✓ applications.withdraw.own
   ```

4. **Sauvegarder**

5. **Ajouter aux Profils**
   ```
   → Aller dans les profils concernés
   → Ajouter ce bundle
   ```

### 6.4 Modifier un Bundle

**Impact :** Affecte tous les profils qui utilisent ce bundle

**Modifications Possibles :**
- ✅ Ajouter des permissions
- ⚠️ Retirer des permissions (vérifier impact)
- ✅ Modifier la description

**Étapes Sécurisées :**
1. Noter quels profils utilisent ce bundle
2. Faire la modification
3. Tester avec chaque profil
4. Valider que rien n'est cassé

---

## 7. Résolution de Problèmes

### 7.1 Utilisateur ne Peut Pas Accéder à une Page

**Diagnostic :**

1. **Vérifier le profil de l'utilisateur**
   ```
   Utilisateurs → Rechercher → Section "Profils"
   ```

2. **Vérifier les permissions du profil**
   ```
   IAM → Profils → Trouver le profil
   → Voir les permissions
   ```

3. **Identifier la permission manquante**
   ```
   Page inaccessible = Quelle permission requise ?
   Ex: Page "Missions" = Besoin de missions.view
   ```

4. **Solutions :**
   - Option A : Ajouter la permission au profil
   - Option B : Changer le profil de l'utilisateur
   - Option C : Créer un nouveau profil sur mesure

### 7.2 Erreur "Permission Refusée"

**Message :** "Vous n'avez pas la permission pour effectuer cette action"

**Causes Possibles :**

| Cause | Solution |
|-------|----------|
| Permission manquante | Ajouter la permission |
| Mauvais profil | Changer le profil |
| Scope incorrect (.own vs .all) | Ajuster le scope |
| Bundle non chargé | Redémarrer le service backend |

**Debug :**
```bash
# Vérifier les permissions chargées
1. Se connecter en tant que l'utilisateur
2. Aller dans "Mon Profil"
3. Section "Mes Permissions"
4. Chercher la permission nécessaire
```

### 7.3 Profil Vide ou Sans Effet

**Symptôme :** Un profil existe mais n'a aucune permission

**Vérification :**
```
IAM → Profils → Trouver le profil

Permissions directes: 0
Bundles: 0

→ Profil vide !
```

**Solutions :**
1. **Ajouter des bundles** (recommandé)
2. **Ajouter des permissions directes**
3. **Ou supprimer le profil** si inutilisé

### 7.4 Bundles ne Sont Pas Chargés

**Symptôme :** Utilisateur devrait avoir X permissions mais n'en a que Y

**Cause :** Bug critique corrigé le 19 janvier 2025

**Vérification :**
```python
# Test backend
from awana_auth.services.iam_service import IAMService
iam = IAMService(db)
perms = await iam.get_user_permissions("user_id")
print(len(perms.all_permissions))
```

**Si le problème persiste :**
1. Redémarrer auth-microservice
2. Vérifier les logs
3. Contacter le support technique

---

## 8. FAQ

### Q1: Combien de profils un utilisateur peut-il avoir ?

**R:** Autant que nécessaire. Les permissions de tous les profils sont combinées (union).

**Exemple :**
```
Utilisateur avec 2 profils:
  - Profil A: 10 permissions
  - Profil B: 15 permissions
  
Total: 25 permissions (si pas de doublon)
```

---

### Q2: Quelle est la différence entre .own et .all ?

**R:**

| Scope | Signification | Exemple |
|-------|---------------|---------|
| `.own` | Vos ressources uniquement | Vous voyez VOS missions |
| `.all` | Toutes les ressources | Vous voyez TOUTES les missions |

**Usage :**
- Utilisateurs normaux → `.own`
- Managers → `.all`
- Admins → `.all`

---

### Q3: Puis-je créer mes propres permissions ?

**R:** Dépend de votre rôle :
- **Super Admin** : ✅ Oui
- **Admin** : ✅ Oui (avec restrictions)
- **Utilisateur** : ❌ Non

---

### Q4: Les bundles sont-ils obligatoires ?

**R:** Non, mais **fortement recommandés**.

**Sans bundles :**
- ❌ Dupliquer les permissions sur chaque profil
- ❌ Difficile à maintenir
- ❌ Risque d'incohérence

**Avec bundles :**
- ✅ Modifier une fois, appliqué partout
- ✅ Cohérence garantie
- ✅ Plus facile à comprendre

---

### Q5: Comment savoir si un profil est adapté ?

**R:** Checklist :

```
✓ Le nom du profil correspond au rôle métier
✓ Les permissions correspondent aux tâches quotidiennes
✓ Ni trop de permissions (sécurité)
✓ Ni trop peu (utilisabilité)
✓ Utilise des bundles quand possible
```

**Test :** Se connecter avec un compte test et essayer d'utiliser l'application normalement.

---

### Q6: Puis-je avoir des permissions temporaires ?

**R:** Pas encore implémenté, mais prévu pour une version future.

**Alternative actuelle :**
1. Admin crée un profil temporaire
2. Assigne le profil
3. Le retire manuellement après

---

### Q7: Comment voir l'historique des modifications IAM ?

**R:** Navigation : IAM → Audit → Historique

**Informations :**
- Qui a fait la modification
- Quand
- Quoi (profil, permission, bundle)
- Avant/Après

---

### Q8: Les permissions sont-elles appliquées immédiatement ?

**R:** 

**Backend :** Oui (immédiat)
**Frontend :** Nécessite un **rechargement de la page** ou **déconnexion/reconnexion**

**Meilleure pratique :**
```
1. Admin modifie le profil
2. Admin informe l'utilisateur
3. Utilisateur se déconnecte
4. Utilisateur se reconnecte
→ Nouvelles permissions actives
```

---

### Q9: Comment tester un profil avant de l'assigner ?

**R:**

1. **Créer un compte de test**
2. **Assigner le profil au compte test**
3. **Se connecter avec le compte test**
4. **Tester toutes les fonctionnalités**
5. **Ajuster si nécessaire**
6. **Une fois validé, assigner aux vrais utilisateurs**

---

### Q10: Que faire en cas de blocage total ?

**R:**

**Si plus aucun admin ne peut accéder :**

1. **Contacter le support technique**
2. **Un super admin peut être créé manuellement**
3. **Ne JAMAIS modifier directement la base de données** sans expertise

**Prévention :**
- Toujours avoir au moins 2 super admins
- Documenter les accès critiques
- Sauvegardes régulières

---

## 📞 Support

**Questions techniques :** support-technique@awana.com  
**Formation IAM :** formation@awana.com  
**Urgence :** Hotline 24/7

---

## 📝 Changelog

**Version 2.0 (19 Janvier 2025)**
- ✅ Ajout support bundles
- ✅ Correction chargement permissions
- ✅ Interface admin améliorée
- ✅ Documentation complète

**Version 1.0 (Décembre 2024)**
- Version initiale

---

**Dernière mise à jour :** 19 Janvier 2025  
**Contributeurs :** Équipe Platform Awana
