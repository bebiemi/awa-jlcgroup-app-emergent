# Guide du Système de Versioning de Configuration

## Vue d'ensemble

Le système de versioning de configuration permet de créer des snapshots de la configuration de l'application, de suivre l'historique des changements, et de faire des rollbacks vers des versions antérieures.

## Architecture

### Backend

**Fichiers principaux:**
- `/auth-microservice/version_routes.py` - Routes API pour le versioning
- `/auth-microservice/awana_auth/core/version_models.py` - Modèles Pydantic
- Collection MongoDB: `configuration_history`

**Endpoints API:**

#### 1. Lister les versions
```http
GET /api/versions/list?limit=50&skip=0
```

**Réponse:**
```json
{
  "versions": [
    {
      "id": "uuid",
      "version": "v20251105.041023",
      "description": "Description du snapshot",
      "created_at": "2025-11-05T04:10:23.279000",
      "created_by_name": "Admin",
      "snapshot_type": "manual",
      "tags": ["tag1", "tag2"]
    }
  ],
  "total": 1,
  "limit": 50,
  "skip": 0
}
```

#### 2. Créer un snapshot
```http
POST /api/versions/snapshot?description=Description&tags[]=tag1
Authorization: Bearer {token}
```

**Permissions:** Admin/Super Admin requis

**Réponse:**
```json
{
  "message": "Snapshot créé avec succès",
  "snapshot": {
    "id": "uuid",
    "version": "v20251105.041023",
    "description": "Description du snapshot"
  }
}
```

**Contenu du snapshot:**
- Toutes les références actives (roles, statuses, etc.)
- Configuration YAML pertinente
- Métadonnées (créateur, date, environnement)

#### 3. Détails d'une version
```http
GET /api/versions/{version_id}
```

**Réponse:** Retourne le snapshot complet avec toutes les données de configuration

#### 4. Rollback vers une version
```http
POST /api/versions/rollback
Authorization: Bearer {token}
Content-Type: application/json

{
  "version_id": "uuid",
  "reason": "Raison du rollback"
}
```

**Permissions:** Admin/Super Admin requis

**Comportement:**
1. Crée automatiquement un snapshot de la config actuelle (avec tags `["auto", "pre-rollback"]`)
2. Désactive toutes les références actuelles
3. Restaure les références de la version cible
4. Enregistre l'opération de rollback dans l'historique

#### 5. Comparer deux versions
```http
GET /api/versions/compare/{version_id_from}/{version_id_to}
```

**Réponse:**
```json
{
  "version_from": "v20251105.041023",
  "version_to": "v20251105.041530",
  "added": ["roles.new_role"],
  "removed": ["roles.old_role"],
  "modified": ["roles.admin"],
  "changes": {
    "roles.admin": {
      "from": {...},
      "to": {...}
    }
  }
}
```

### Frontend

**Fichiers principaux:**
- `/apps/web/src/features/admin/pages/ConfigurationVersionsPage.tsx`
- Route: `/admin/versions`
- Lien sidebar: "Versions Config" (section Paramètres)

**Fonctionnalités UI:**

#### 1. Vue d'ensemble
- Affichage du nombre total de versions
- Nombre de snapshots manuels
- Nombre de rollbacks effectués

#### 2. Historique des versions
- Liste chronologique des versions (plus récent en premier)
- Affichage des informations:
  - Version (format: v{YYYYMMDD}.{HHMMSS})
  - Type (manual, rollback, auto)
  - Description
  - Créateur
  - Date et heure
  - Tags

#### 3. Créer un snapshot
- Modal avec champ de description (obligatoire)
- Sauvegarde la configuration actuelle
- Notifications toast pour succès/erreur

#### 4. Rollback
- Modal de confirmation avec avertissement
- Champ raison obligatoire
- Création automatique d'un snapshot de backup
- Notifications toast pour succès/erreur

## Format de version

Les versions utilisent un format timestamp pour assurer l'unicité et la chronologie:

```
v{YYYY}{MM}{DD}.{HH}{MM}{SS}

Exemple: v20251105.041023
```

## Types de snapshot

### 1. Manual
- Créé manuellement par un administrateur
- Badge vert dans l'UI
- Utilisé pour marquer des changements importants

### 2. Auto (pre-rollback)
- Créé automatiquement avant chaque rollback
- Tags: `["auto", "pre-rollback"]`
- Permet d'annuler un rollback si nécessaire

### 3. Rollback
- Enregistre l'opération de rollback effectuée
- Badge bleu dans l'UI
- Contient la version cible et la raison

## Données sauvegardées dans un snapshot

### 1. Références (system_references)
Catégories sauvegardées:
- `roles` - Rôles utilisateurs
- `user_statuses` - Statuts utilisateurs
- `mission_statuses` - Statuts des missions
- `application_statuses` - Statuts des candidatures
- `validation_statuses` - Statuts de validation
- `validation_types` - Types de validation
- `contract_types` - Types de contrats

Pour chaque référence:
```json
{
  "code": "admin",
  "label_fr": "Administrateur",
  "label_en": "Administrator",
  "order": 1
}
```

### 2. Configuration YAML
Sections pertinentes du fichier de configuration:
- `security.roles`
- `security.user_statuses`

### 3. Métadonnées
- `id` - UUID unique
- `version` - Numéro de version timestamp
- `description` - Description du snapshot
- `created_at` - Date/heure de création
- `created_by` - ID de l'utilisateur créateur
- `created_by_name` - Nom affiché du créateur
- `snapshot_type` - Type (manual, auto, rollback)
- `environment` - Environnement (local, dev, staging, production)
- `tags` - Liste de tags

## Utilisation recommandée

### Quand créer un snapshot manuel

1. **Avant des changements majeurs:**
   - Ajout/suppression de rôles
   - Modification des workflows
   - Changements des règles métier

2. **Jalons importants:**
   - Fin d'une phase de développement
   - Avant un déploiement en production
   - Après validation d'une configuration

3. **Documentation:**
   - Utiliser des descriptions claires
   - Ajouter des tags pertinents
   - Mentionner les tickets/tâches liés

### Quand faire un rollback

1. **Problèmes détectés:**
   - Bug lié à un changement de configuration
   - Comportement inattendu de l'application
   - Erreurs de validation

2. **Tests échoués:**
   - Après modification des règles
   - Suite à l'ajout de nouveaux rôles
   - Problèmes d'intégration

3. **Retour en arrière:**
   - Annuler une modification non souhaitée
   - Restaurer une configuration stable connue

## Bonnes pratiques

### Descriptions de snapshot
```
✅ Bon: "Ajout du rôle 'supervisor' pour la gestion d'équipe - Ticket #123"
❌ Mauvais: "Modification config"

✅ Bon: "Configuration initiale v1.0 - Production 05/11/2025"
❌ Mauvais: "Test"
```

### Tags suggérés
- `production` - Snapshots de production
- `staging` - Snapshots de staging
- `pre-deployment` - Avant déploiement
- `rollback` - Opération de rollback
- `auto` - Snapshot automatique
- `major-change` - Changement majeur
- `roles` - Modification des rôles
- `workflow` - Modification workflow

### Raisons de rollback
```
✅ Bon: "Bug critique: Les intérimaires ne peuvent plus postuler - Rollback vers v20251105.120000"
❌ Mauvais: "Ça marche pas"

✅ Bon: "Tests de validation échoués après ajout rôle supervisor - Restauration config stable"
❌ Mauvais: "Problème"
```

## Sécurité et permissions

### Permissions requises
- **Lister les versions:** Aucune (public)
- **Voir détails version:** Aucune (public)
- **Créer snapshot:** Admin ou Super Admin
- **Rollback:** Admin ou Super Admin
- **Comparer versions:** Aucune (public)

### Audit
Toutes les opérations sont enregistrées:
- Qui a créé le snapshot
- Quand il a été créé
- Description et raison
- Opérations de rollback

## Limitations actuelles

1. **Portée des snapshots:**
   - Actuellement: Références (system_references) + config YAML
   - Non inclus: Données utilisateurs, missions, candidatures

2. **Rollback:**
   - Restaure uniquement les références
   - Ne restaure pas les données métier

3. **Comparaison:**
   - Compare uniquement les références
   - Pas de visualisation diff détaillée dans l'UI

## Évolutions futures possibles

1. **Snapshot complet:**
   - Inclure les règles métier (business_rules)
   - Sauvegarder les configurations de workflow
   - Export/Import de snapshots

2. **UI améliorée:**
   - Visualisation diff côte à côte
   - Prévisualisation avant rollback
   - Filtres et recherche avancée

3. **Automatisation:**
   - Snapshots automatiques périodiques
   - Snapshots avant chaque déploiement
   - Notifications par email

4. **Gestion avancée:**
   - Archivage de versions anciennes
   - Nettoyage automatique
   - Export vers Git

## Dépannage

### Le snapshot ne contient aucune référence
**Cause:** Aucune référence active dans la base de données  
**Solution:** Vérifier que des références existent dans la collection `system_references`

### Erreur 403 lors de la création de snapshot
**Cause:** Permissions insuffisantes  
**Solution:** Se connecter avec un compte Admin ou Super Admin

### Le rollback ne restaure pas tout
**Cause:** Le rollback ne restaure que les références  
**Solution:** Utiliser les scripts de migration pour les autres données

### Les versions n'apparaissent pas dans l'UI
**Cause:** Variable d'environnement incorrecte  
**Solution:** Vérifier que `VITE_AUTH_SERVICE_URL` pointe vers le bon service

## Tests

### Test backend (CLI)
```bash
# Obtenir un token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"awana2025"}' | jq -r '.access_token')

# Lister les versions
curl -s "http://localhost:8000/api/versions/list" | jq '.'

# Créer un snapshot
curl -s -X POST "http://localhost:8000/api/versions/snapshot?description=Test" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Test frontend
1. Se connecter avec un compte admin
2. Naviguer vers "Paramètres" → "Versions Config"
3. Vérifier l'affichage de la liste
4. Tester la création d'un snapshot
5. Tester le rollback (sur environnement de test)

## Support

Pour toute question ou problème:
1. Consulter les logs: `/var/log/supervisor/auth-microservice.*.log`
2. Vérifier la collection MongoDB: `configuration_history`
3. Examiner les requêtes réseau dans les DevTools du navigateur
