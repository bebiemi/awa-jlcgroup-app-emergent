# AWANA - Système RBAC Complet

**Date d'export :** 17 novembre 2025  
**Version :** 1.0  
**Statistiques :** 114 permissions, 18 profils, 3 rôles IAM

---

## 📊 Vue d'ensemble du système

Le système RBAC d'AWANA utilise une architecture hybride :
- **Permissions** : Droits atomiques (ex: `missions.browse`, `users.read`)
- **Profils** : Regroupements de permissions par rôle métier
- **Rôles IAM** : Rôles granulaires pour contrôle d'accès avancé
- **Groupes IAM** : Regroupements d'utilisateurs (actuellement 0)

---

## 🔑 Catégories de permissions

### 1. **Missions** (missions.*)
- `missions.browse` - Consulter les offres de mission disponibles
- `missions.read` - Lire les détails d'une mission
- `missions.create` - Créer de nouvelles missions
- `missions.update` - Modifier les missions existantes
- `missions.delete` - Supprimer des missions
- `missions.approve` - Approuver des missions
- `missions.publish` - Publier des missions
- `missions.manage` - Gérer toutes les missions

### 2. **Applications/Candidatures** (applications.*)
- `applications.create` - Créer une candidature à une mission
- `applications.read_own` - Voir ses propres candidatures
- `applications.create_own` - Créer ses propres candidatures
- `applications.update_own` - Modifier ses candidatures
- `applications.read` - Voir toutes les candidatures
- `applications.manage` - Gérer toutes les candidatures

### 3. **Besoins** (besoins.*)
- `besoins.create` - Créer et gérer des besoins de recrutement
- `besoins.read` - Consulter les besoins
- `besoins.edit` - Modifier les besoins en brouillon
- `besoins.submit` - Soumettre les besoins à JLC
- `besoins.comment` - Ajouter des commentaires sur les besoins
- `besoins.convert_to_mission` - Convertir un besoin en mission (JLC seulement)

### 4. **Entreprises** (entreprises.*)
- `entreprises.read` - Consulter les informations des entreprises
- `entreprises.edit` - Modifier les informations des entreprises
- `voir_entreprises` - Consulter les profils entreprises
- `modifier_entreprises` - Modifier les profils entreprises
- `supprimer_entreprises` - Supprimer des profils entreprises

### 5. **Utilisateurs** (users.*)
- `users.read` - Voir les utilisateurs
- `users.write` - Créer/modifier des utilisateurs
- `users.delete` - Supprimer des utilisateurs
- `users.edit` - Modifier des utilisateurs
- `users.manage` - Gérer les utilisateurs

### 6. **Profil personnel** (profile.*)
- `profile.manage_own` - Modifier son propre profil

### 7. **Documents** (documents.*)
- `documents.read_own` - Voir ses propres documents
- `documents.upload_own` - Uploader ses documents
- `documents.delete_own` - Supprimer ses documents

### 8. **IAM** (iam.*)
- `iam.profiles.manage` - Gérer les profils IAM
- `iam.groups.manage` - Gérer les groupes IAM
- `iam.permissions.manage` - Gérer les permissions
- `iam.permissions.read` - Consulter les permissions IAM
- `iam.permissions.create` - Créer de nouvelles permissions IAM
- `iam.permissions.delete` - Supprimer des permissions IAM

### 9. **Admin** (admin.*)
- `admin.dashboard` - Accès au tableau de bord admin
- `validations.manage` - Gérer les validations
- `locations.manage` - Gérer les localisations
- `groups.manage` - Gérer les groupes

### 10. **Autres permissions métier**
- `config.manage` - Gérer la configuration
- `references.manage` - Gérer les référentiels
- `rules.manage` - Gérer les règles métier
- `flags.manage` - Gérer les feature flags
- `emails.configure`, `emails.read_history`, `emails.manage_templates`
- `notifications.read_own`, `notifications.manage_own`
- `dashboard.view_own`, `dashboard.customize`
- `matching.view_recommendations`

---

## 👥 Profils clés

### 1. **Super Admin** (`super_admin`)
- **Permissions** : Toutes (114 permissions)
- **Accès** : Complet sur toute l'application
- **Couleur** : Rouge (#DC2626)
- **Priorité** : 100 (la plus haute)

### 2. **Intérimaire** (`interim_user`)
- **Code** : `interim_user`
- **Permissions principales** :
  - `missions.browse` - Voir les offres
  - `applications.create` - Postuler
  - `applications.read_own` - Voir ses candidatures
  - `profile.manage_own` - Gérer son profil
- **Couleur** : Vert (#10B981)
- **Priorité** : 300

### 3. **Entreprise Admin** (`company_admin`)
- **Code** : `company_admin`
- **Permissions principales** :
  - `besoins.create` - Créer des besoins
  - `besoins.read` - Consulter les besoins
  - `besoins.edit` - Modifier les besoins
  - `besoins.submit` - Soumettre à JLC
  - `entreprises.read` - Consulter infos entreprise
  - `entreprises.edit` - Modifier infos entreprise
  - `missions.browse` - Voir les missions
  - `profile.manage_own` - Gérer son profil
- **Priorité** : 250

### 4. **Postulant** (`profile_postulant`, `role.postulant`)
- **Code** : `profile_postulant` ou `role.postulant`
- **Permissions principales** :
  - `missions.browse` - Voir les offres
  - `missions.read` - Lire les détails
  - `applications.create_own` - Créer ses candidatures
  - `applications.read_own` - Voir ses candidatures
  - `applications.update_own` - Modifier ses candidatures
  - `profile.manage_own` - Gérer son profil
  - `documents.*_own` - Gérer ses documents
  - `notifications.*_own` - Gérer ses notifications
  - `dashboard.view_own` - Voir son tableau de bord
  - `matching.view_recommendations` - Voir recommandations
- **Utilisation** : Phase d'onboarding avant validation

### 5. **Candidat** (`candidat`)
- Similaire au postulant avec focus sur les candidatures

### 6. **Commercial** (`gestionnaire_commercial`)
- **Permissions** : Gestion des missions, entreprises, validations
- **Priorité** : 200

### 7. **RH** (`gestionnaire_rh`)
- **Permissions** : Gestion des intérimaires, validations
- **Priorité** : 200

### 8. **Lecture Seule** (`lecture_seule`)
- **Permissions** : Consultation uniquement (aucune modification)

---

## 🔄 Rôles IAM

### 1. **candidat**
- **Permissions** : 
  - `missions.browse`
  - `applications.create`
  - `applications.read_own`
  - `profile.manage_own`

### 2. **commercial**
- **Permissions** : Gestion des missions et entreprises

### 3. **entreprise**
- **Permissions** : Gestion des besoins et profil entreprise

---

## 📋 Matrice de permissions par rôle utilisateur

| Permission | Super Admin | Entreprise | Intérimaire | Postulant | Commercial | RH |
|------------|-------------|------------|-------------|-----------|------------|-----|
| missions.browse | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| missions.create | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| missions.manage | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| besoins.create | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| applications.create | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| applications.manage | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| users.manage | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| validations.manage | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| entreprises.edit | ✅ | ✅ (own) | ❌ | ❌ | ✅ | ❌ |

---

## 🏗️ Architecture du système

```
User (utilisateur)
  ├─ roles: ["company", "candidat", etc.] (Legacy)
  ├─ profile_ids: ["profile_postulant", "company_admin"]
  └─ group_ids: ["group_123"] (actuellement vide)

Profile (profil métier)
  ├─ code: "interim_user"
  ├─ name: "Intérimaire"
  └─ permission_ids: ["bf77b8c2-...", "missions.browse"]

Permission
  ├─ id: "bf77b8c2-aae4-4ffc-b000-f4cbb242824a"
  ├─ code: "missions.browse"
  └─ description: "Consulter les offres de mission disponibles"
```

---

## 🔐 Logique de résolution des permissions

Le service `IAMUnifiedService` consolide les permissions depuis :

1. **Profils métier** (via `profile_ids`)
2. **Rôles IAM** (via `roles`)
3. **Groupes IAM** (via `group_ids`)

**Important :** Le système supporte deux formats de `permission_ids` :
- UUID : `"bf77b8c2-aae4-4ffc-b000-f4cbb242824a"`
- Code string : `"missions.browse"`

La résolution utilise un `$or` pour chercher par les deux champs.

---

## 📂 Fichiers d'export disponibles

Deux fichiers JSON ont été générés :

1. **`awana_rbac_export.json`** (2193 lignes)
   - Export complet avec toutes les permissions, profils, rôles
   - Format : JSON structuré avec métadonnées

2. **`awana_rbac_summary.json`**
   - Résumé par catégorie
   - Profils clés uniquement
   - Plus léger et digeste

---

## 🚀 Utilisation

### Vérifier les permissions d'un utilisateur
```bash
GET /api/iam/unified/users/{userId}/permissions
```

### Vérifier une permission spécifique
```bash
POST /api/iam/check-permission
{
  "user_id": "...",
  "permission_code": "missions.browse"
}
```

### Dans le frontend (React)
```typescript
import { usePermission } from '@/hooks/usePermission'

const { hasPermission } = usePermission('missions.browse')
```

---

**Fin de la documentation RBAC AWANA**
