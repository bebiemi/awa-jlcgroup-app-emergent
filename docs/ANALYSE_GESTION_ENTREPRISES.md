# Analyse Complète - Gestion des Entreprises

Date: 2025-01-18
Agent: E1 (Fork)

## 🎯 Objectif

Implémenter une gestion complète des entreprises avec :
1. Création depuis /admin/entreprises
2. Système d'invitation d'utilisateurs
3. Alignement avec l'onboarding public
4. Alignement du portail entreprise avec IAM

---

## 📊 État de l'Existant

### 1. Permissions IAM Entreprises

**✅ Permissions existantes (12) :**
- `entreprises.create` - Créer des entreprises (scope: global)
- `entreprises.read` - Consulter les entreprises (scope: own)
- `entreprises.edit` - Modifier les entreprises (scope: own)
- `entreprises.delete` - Supprimer des entreprises (scope: global)
- `entreprises.view_all` - Voir toutes les entreprises (scope: global)
- `entreprises.edit_all` - Modifier toutes les entreprises (scope: global)
- `entreprises.delete_all` - Supprimer des entreprises (scope: global)
- `entreprises.view_own` - Voir son propre profil entreprise (scope: own)
- `entreprises.edit_own` - Modifier son propre profil entreprise (scope: own)
- Permissions legacy (3) : voir_entreprises, modifier_entreprises, supprimer_entreprises

**❌ Permissions manquantes demandées :**
- `enterprise.create` (existe sous `entreprises.create`)
- `enterprise.manage` (n'existe pas - à créer ?)
- `enterprise.invite_user` (n'existe pas - à créer)

**Recommandation :** Utiliser `entreprises.*` (convention française existante) plutôt que `enterprise.*`

---

### 2. Backend - Routes Entreprises

**Fichier :** `/app/auth-microservice/entreprise_routes.py` (420 lignes)

**Endpoints existants :**
| Méthode | Route | Permission | Description |
|---------|-------|------------|-------------|
| GET | `/me` | Aucune (current_user) | Récupérer l'entreprise de l'utilisateur |
| GET | `/{entreprise_id}` | Aucune (current_user) | Récupérer une entreprise par ID |
| GET | `/` | Aucune (current_user) | Lister toutes les entreprises |
| POST | `/` | `entreprises.create` | ✅ Créer une entreprise |
| PATCH | `/me` | `entreprises.edit` | Modifier son entreprise |
| PATCH | `/{entreprise_id}` | `entreprises.edit_all` | Modifier une entreprise (admin) |
| DELETE | `/{entreprise_id}` | `entreprises.delete` | Supprimer une entreprise |

**✅ Points positifs :**
- Utilisation de `require_permission()` pour POST
- Modèles Pydantic bien définis
- Validation SIRET (14 chiffres)
- Gestion du statut (active, inactive, suspended)

**⚠️ Points à améliorer :**
- GET endpoints sans vérification de permissions IAM
- Pas de système d'invitation d'utilisateurs
- Pas de lien automatique entreprise → utilisateur créé
- Pas d'utilisation d'IAMService pour les permissions dynamiques
- Pas de référentiels dynamiques (secteur_activite, effectif en dur)

---

### 3. Frontend - Page Admin Entreprises

**Fichier :** `/app/apps/web/src/features/admin/pages/EntreprisesManagementPage.tsx`

**Fonctionnalités actuelles :**
- ✅ Liste de toutes les entreprises
- ✅ Recherche par nom/SIRET/email
- ✅ Statistiques (total, actives, résultats)
- ✅ Détails dépliables
- ✅ Modification inline
- ❌ **PAS de bouton "Créer une entreprise"**
- ❌ **PAS de système d'invitation**

**API utilisée :**
- `useListEntreprisesQuery()` - RTK Query
- `useUpdateEntrepriseMutation()` - RTK Query

---

### 4. Frontend - Registration Entreprise

**Fichier :** `/app/apps/web/src/features/auth/pages/RegisterPage.tsx`

**À analyser :**
- Processus de création de compte entreprise
- Champs du formulaire
- Validation
- Assignation de profils

---

### 5. Frontend - Portail Entreprise

**À identifier :**
- Pages de gestion côté entreprise
- Fonctionnalités disponibles
- Gestion des collaborateurs

---

## 🚧 Problèmes Identifiés

### 1. **Manque de fonctionnalité de création admin**
La page admin n'a pas de bouton/modal pour créer une entreprise

### 2. **Pas de système d'invitation**
Aucun mécanisme pour :
- Générer des tokens d'invitation
- Envoyer des emails d'invitation
- Lier automatiquement user → entreprise

### 3. **Permissions IAM incomplètes**
- Manque `entreprises.invite_user`
- Manque `entreprises.manage` (si nécessaire)
- GET endpoints sans vérification de permissions

### 4. **Pas de référentiels dynamiques**
- `secteur_activite` : valeurs en dur
- `effectif` : valeurs en dur (TPE, PME, ETI, GE)
- Devrait utiliser les référentiels administrables

### 5. **Duplication potentielle**
- Logique de création entreprise peut être dupliquée entre :
  - Admin creation
  - Public registration
  - Onboarding flow

---

## 📋 Plan d'Implémentation Proposé

### Phase 1 : Permissions IAM
1. Créer permission `entreprises.invite_user`
2. Créer permission `entreprises.manage` (si nécessaire)
3. Ajouter vérifications de permissions sur GET endpoints

### Phase 2 : Système d'Invitation
1. Backend :
   - Créer table `invitations` (token, email, entreprise_id, role, expiry)
   - Endpoint POST `/entreprises/{id}/invite` 
   - Endpoint GET `/invitations/{token}/validate`
   - Intégration service email
2. Frontend :
   - Modal d'invitation depuis admin
   - Page de création de compte via invitation

### Phase 3 : Création Admin
1. Backend : (déjà existant)
   - Endpoint POST `/entreprises` ✅
2. Frontend :
   - Bouton "Créer une entreprise"
   - Modal/Page de création
   - Formulaire avec référentiels dynamiques
   - Option d'inviter un utilisateur immédiatement

### Phase 4 : Référentiels Dynamiques
1. Créer référentiels :
   - `secteurs_activite`
   - `effectifs_entreprise`
2. Modifier les formulaires pour utiliser ces référentiels

### Phase 5 : Alignement Onboarding
1. Analyser RegisterPage.tsx
2. Harmoniser la logique de création
3. Éviter duplication de code

### Phase 6 : Alignement Portail Entreprise
1. Identifier les pages entreprise existantes
2. Vérifier l'utilisation d'IAMService
3. Harmoniser avec les permissions

---

## ⚠️ Risques & Contraintes

### Risques identifiés :
1. **Régression sur Emergent** : Modifier les routes existantes peut casser des flows
2. **Duplication** : Risque de dupliquer la logique entre admin et public
3. **Emails** : Service d'envoi d'emails doit être fonctionnel
4. **Tokens** : Système de tokens sécurisés nécessaire

### Contraintes :
- ✅ Respect strict du système IAM hybride
- ✅ Utilisation d'IAMService
- ✅ Pas de rôles IAM directs aux utilisateurs
- ✅ Référentiels dynamiques obligatoires
- ✅ Pas de valeurs en dur

---

## 🔍 Questions pour l'Utilisateur

Avant d'implémenter, clarifier :

1. **Permission `entreprises.manage` :** Est-elle vraiment nécessaire ou `entreprises.edit_all` suffit-elle ?

2. **Profil entreprise :** Quel profil métier donner au premier utilisateur créé via invitation ?
   - `entreprise_admin` ?
   - `company_admin` ?
   - Autre ?

3. **Invitation multiple :** Faut-il permettre d'inviter plusieurs utilisateurs en même temps lors de la création ?

4. **Email service :** Quel service utiliser pour l'envoi d'emails d'invitation ?

5. **Priorité :** Dans quel ordre implémenter ?
   - Option A : Phase 1 → 2 → 3 (invitation d'abord)
   - Option B : Phase 1 → 3 → 2 (création simple d'abord, invitation après)

---

## 📝 Prochaines Étapes

1. Valider ce document d'analyse avec l'utilisateur
2. Répondre aux questions
3. Définir l'ordre des phases
4. Commencer l'implémentation phase par phase
5. Tester après chaque phase

---

**Note :** Ce document sera mis à jour au fur et à mesure de l'implémentation.
