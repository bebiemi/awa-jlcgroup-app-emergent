# Guide Complet - Système de Feature Flags

**Date:** 5 Novembre 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready

## Vue d'ensemble

Le système de Feature Flags permet aux Super-Admins de contrôler l'activation/désactivation progressive de fonctionnalités de l'application sans déploiement.

## Architecture

### Types de Feature Flags

| Type | Description | Exemple Use Case |
|------|-------------|------------------|
| **GLOBAL** | S'applique à tous les utilisateurs | Nouvelle UI dashboard |
| **ROLE** | S'applique à un rôle spécifique | Export CSV pour admins |
| **USER** | S'applique à un utilisateur précis | Beta testing pour un user |
| **ENV** | S'applique à un environnement | Feature en staging uniquement |

### Ordre de priorité

Lorsqu'un flag est évalué, l'ordre de priorité est :
```
USER (plus spécifique)
  ↓
ROLE
  ↓
ENV
  ↓
GLOBAL (fallback)
```

**Exemple:** Si un flag GLOBAL est désactivé, mais un flag USER est activé pour un utilisateur, ce dernier verra la fonctionnalité.

## Accès à l'interface

### Prérequis
- Rôle: **Super-Admin** (ou Admin pour consultation)
- URL: `http://localhost:3000/admin/feature-flags`

### Login Super-Admin
```
Email: admin@awanagroup.com
Password: awana2025
```

## Utilisation de l'interface

### 1. Vue d'ensemble

L'interface affiche 4 statistiques clés :
- **Total** : Nombre total de flags
- **Actifs** : Flags actuellement activés
- **Inactifs** : Flags désactivés
- **En rollout** : Flags avec rollout partiel (0% < x < 100%)

### 2. Filtres

**Afficher inactifs :**
- ☑️ Coché : Affiche tous les flags (actifs + inactifs)
- ☐ Décoché : Affiche uniquement les flags actifs

**Type :**
- Filtre dropdown : GLOBAL, ROLE, USER, ENV
- "Tous les types" : Pas de filtre

### 3. Créer un Feature Flag

**Étapes :**
1. Cliquer sur **"Nouveau Flag"** (en haut à droite)
2. Remplir le formulaire :
   ```
   Clé*            : feature.mission.bulk_assign
   Type*           : GLOBAL
   Cible           : (vide si GLOBAL, sinon obligatoire)
   Description     : Permet l'assignation groupée de missions
   ☑ Activé       : (cocher pour activer immédiatement)
   ```
3. Cliquer **"Créer"**

**Règles de validation :**
- Clé : min 3 caractères, format `feature.module.nom` recommandé
- Clé : unique dans tout le système
- Clé : non modifiable après création
- Cible : obligatoire si type ≠ GLOBAL

### 4. Modifier un Feature Flag

**Étapes :**
1. Cliquer sur l'icône ✏️ **Modifier** sur la ligne du flag
2. Modifier les champs (sauf la clé)
3. Cliquer **"Mettre à jour"**

**Champs modifiables :**
- Description
- Activation (via toggle ou modal)
- Cible (si type permet)

### 5. Toggle Rapide

Pour activer/désactiver rapidement un flag :
- Cliquer sur le **switch** dans la colonne "Statut"
- Le flag est immédiatement activé/désactivé
- Notification toast confirmant l'action

### 6. Rollout Progressif

Le rollout permet d'activer un flag pour un pourcentage d'utilisateurs.

**Étapes :**
1. Cliquer sur l'icône 📊 dans la colonne "Rollout"
2. Ajuster le slider (0% à 100%, pas de 5%)
3. Cliquer **"Appliquer"**

**Comment ça fonctionne :**
- Hash MD5 de `flag_key:user_id` → pourcentage entre 0 et 99
- Si `user_percentage < rollout_percentage` → flag activé
- Distribution uniforme et **consistante** (même user = même résultat)

**Exemple :**
```
Rollout 50% :
- user_abc (hash=23) → ACTIVÉ (23 < 50)
- user_def (hash=67) → DÉSACTIVÉ (67 >= 50)
```

### 7. Supprimer un Feature Flag

**⚠️ Action irréversible**

**Étapes :**
1. Cliquer sur l'icône 🗑️ **Supprimer**
2. Confirmer la suppression
3. Le flag est supprimé de la base de données

**Audit :** L'événement de suppression est enregistré dans `audit_events`.

## Exemples d'utilisation

### Scénario 1 : Nouvelle fonctionnalité en beta

**Objectif :** Activer "Assignation groupée de missions" pour 10% des utilisateurs.

```
1. Créer le flag :
   - Clé: feature.mission.bulk_assign
   - Type: GLOBAL
   - Activé: ✓
   - Description: Assignation groupée de missions

2. Appliquer rollout :
   - Rollout: 10%

3. Monitorer les retours

4. Augmenter progressivement :
   - 10% → 25% → 50% → 100%
```

### Scénario 2 : Fonctionnalité pour un rôle

**Objectif :** Export CSV réservé aux admins.

```
1. Créer le flag :
   - Clé: feature.export.csv
   - Type: ROLE
   - Cible: admin
   - Activé: ✓
   - Description: Export CSV pour les admins

2. Le flag est automatiquement activé pour tous les users avec role=admin
```

### Scénario 3 : Beta testing pour un utilisateur

**Objectif :** Tester le nouveau dashboard avec un utilisateur spécifique.

```
1. Créer le flag :
   - Clé: feature.dashboard.v2
   - Type: USER
   - Cible: <user_id>
   - Activé: ✓
   - Description: Dashboard V2 - Beta testing

2. Seul cet utilisateur voit la nouvelle interface
```

### Scénario 4 : Feature en staging uniquement

**Objectif :** Activer une feature en environnement de staging.

```
1. Créer le flag :
   - Clé: feature.payment.crypto
   - Type: ENV
   - Cible: staging
   - Activé: ✓
   - Description: Paiements crypto (staging uniquement)

2. La feature n'est visible qu'en staging
```

## Intégration dans le code

### Backend (FastAPI)

```python
from awana_auth.services.feature_flag_service import FeatureFlagService
from awana_auth.core.feature_flag_models import FeatureFlagContext

# Dans une route
@router.get("/missions/bulk-assign")
async def bulk_assign_missions(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Vérifier le feature flag
    service = FeatureFlagService(db)
    context = FeatureFlagContext(
        user_id=current_user.id,
        roles=current_user.roles,
        environment="production"
    )
    
    if not await service.is_enabled("feature.mission.bulk_assign", context):
        raise HTTPException(
            status_code=403,
            detail="Feature non disponible"
        )
    
    # Continuer si feature activée
    return {"message": "Bulk assign enabled"}
```

### Frontend (React)

```typescript
import { useCheckFeatureFlagQuery } from '@/features/admin/api/featureFlagApi'

function MissionPage() {
  const { data: bulkAssignFlag } = useCheckFeatureFlagQuery('feature.mission.bulk_assign')
  
  return (
    <div>
      {bulkAssignFlag?.enabled && (
        <button onClick={handleBulkAssign}>
          Assigner en groupe
        </button>
      )}
    </div>
  )
}
```

## API Reference

### Endpoints

#### 1. Vérifier un flag
```http
GET /api/feature-flags/check/{flag_key}
Authorization: Bearer {token}

Response:
{
  "flag_key": "feature.mission.bulk_assign",
  "enabled": true,
  "user_id": "user_uuid",
  "roles": ["admin"]
}
```

#### 2. Lister les flags
```http
GET /api/feature-flags?include_inactive=true&type_filter=GLOBAL
Authorization: Bearer {token}

Response:
{
  "flags": [...],
  "total": 4,
  "can_create": true
}
```

#### 3. Créer un flag
```http
POST /api/feature-flags
Authorization: Bearer {token}
Content-Type: application/json

{
  "key": "feature.new.feature",
  "type": "GLOBAL",
  "value": false,
  "metadata": {
    "description": "Nouvelle fonctionnalité",
    "rollout_percentage": 0,
    "tags": ["beta"]
  }
}
```

#### 4. Mettre à jour un flag
```http
PATCH /api/feature-flags/{flag_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "value": true,
  "metadata": {
    "rollout_percentage": 50
  }
}
```

#### 5. Appliquer un rollout
```http
POST /api/feature-flags/{flag_id}/rollout
Authorization: Bearer {token}
Content-Type: application/json

{
  "rollout_percentage": 75,
  "description": "Augmentation à 75%"
}
```

#### 6. Supprimer un flag
```http
DELETE /api/feature-flags/{flag_id}
Authorization: Bearer {token}
```

#### 7. Historique d'un flag
```http
GET /api/feature-flags/{flag_id}/history?limit=50
Authorization: Bearer {token}
```

#### 8. Tous les audits
```http
GET /api/feature-flags/audit/all?limit=50&target_type=feature_flag
Authorization: Bearer {token}
```

## Système d'audit

Toutes les opérations sont enregistrées dans la collection `audit_events`.

### Structure d'un événement

```javascript
{
  id: "uuid",
  actor_id: "admin_uuid",
  actor_name: "Admin User",
  action: "feature_flag.updated",
  target_type: "feature_flag",
  target_id: "flag_uuid",
  payload: {
    flag_key: "feature.mission.bulk_assign",
    old_value: false,
    new_value: true
  },
  created_at: "2025-11-05T12:00:00Z"
}
```

### Types d'actions

- `feature_flag.created` - Flag créé
- `feature_flag.updated` - Flag modifié
- `feature_flag.deleted` - Flag supprimé
- `feature_flag.rollout` - Rollout appliqué

## Cache

Le système utilise un cache mémoire avec TTL de 5 minutes.

**Invalidation automatique :**
- Création de flag
- Modification de flag
- Suppression de flag
- Application de rollout

**Pour production (Redis) :**
```python
# Dans feature_flag_service.py
# Remplacer le cache mémoire par Redis
import redis
self.cache = redis.Redis(host='localhost', port=6379)
```

## Bonnes pratiques

### Nommage des clés

✅ **Bon:**
```
feature.mission.bulk_assign
feature.dashboard.v2
feature.export.csv
feature.notifications.realtime
```

❌ **Mauvais:**
```
newFeature
feature_1
test
bulk
```

**Format recommandé:** `feature.{module}.{nom_fonctionnalité}`

### Descriptions

✅ **Bon:**
```
"Permet l'assignation groupée de missions aux intérimaires"
"Nouveau dashboard avec analytics temps réel et visualisations avancées"
```

❌ **Mauvais:**
```
"Nouvelle feature"
"Test"
"Feature mission"
```

### Tags

Utiliser des tags pour catégoriser :
```javascript
tags: ["ui", "beta", "mission", "productivity"]
```

### Rollout progressif

**Stratégie recommandée :**
```
0% (disabled) → 10% → 25% → 50% → 75% → 100%
```

**Attendre entre chaque étape :**
- Phase 1 (10%) : 1-2 jours
- Phase 2 (25%) : 1-2 jours
- Phase 3 (50%) : 2-3 jours
- Phase 4 (75%) : 2-3 jours
- Phase 5 (100%) : Déploiement complet

### Gestion des erreurs

**Toujours avoir un fallback :**
```typescript
const { data, error } = useCheckFeatureFlagQuery('feature.new.ui')

if (error || !data) {
  // Fallback : comportement par défaut (désactivé)
  return <OldUI />
}

if (data.enabled) {
  return <NewUI />
}

return <OldUI />
```

## Dépannage

### Erreur 401 (Non autorisé)

**Cause:** Token JWT invalide ou expiré

**Solution:**
1. Se déconnecter et se reconnecter
2. Vérifier que le compte a le rôle super_admin
3. Vérifier les logs backend

### Flag non visible dans la liste

**Cause:** Flag désactivé et filtre "Afficher inactifs" décoché

**Solution:** Cocher la case "Afficher inactifs"

### Rollout ne fonctionne pas

**Cause:** Flag désactivé (value=false)

**Solution:** 
1. Activer le flag (toggle ou modal)
2. Puis appliquer le rollout

### Cache non invalidé

**Cause:** Cache TTL de 5 minutes

**Solution:** 
- Attendre 5 minutes
- Ou redémarrer auth-microservice

### MongoDB ObjectId error

**Cause:** Champ `_id` MongoDB dans la réponse

**Solution:** Le service exclut déjà `_id` via projection `{'_id': 0}`

## Sécurité

### Permissions

| Action | Admin | Super-Admin |
|--------|-------|-------------|
| Voir les flags | ✓ | ✓ |
| Créer flag | ✗ | ✓ |
| Modifier flag | ✗ | ✓ |
| Supprimer flag | ✗ | ✓ |
| Rollout | ✗ | ✓ |

### Filtrage

- **Admin** : Voit uniquement GLOBAL et ROLE
- **Super-Admin** : Voit tous les types (GLOBAL, ROLE, USER, ENV)

### Audit

- Toutes les actions sont enregistrées
- Impossible de supprimer les logs d'audit
- Accès aux audits : Admin et Super-Admin

## Maintenance

### Créer un super-admin

```bash
cd /app/auth-microservice
python scripts/create_super_admin.py
```

### Voir les flags en base

```javascript
db.feature_flags.find().pretty()
```

### Compter les flags actifs

```javascript
db.feature_flags.countDocuments({ value: true })
```

### Nettoyer les flags de test

```javascript
db.feature_flags.deleteMany({
  key: { $regex: /^feature\.test\./ }
})
```

### Voir les audits récents

```javascript
db.audit_events.find()
  .sort({ created_at: -1 })
  .limit(10)
  .pretty()
```

## Migration vers production

### Prérequis

1. **Redis installé** (pour cache)
2. **MongoDB** avec index créés
3. **Compte super-admin** existant

### Étapes

1. Migrer la base de données :
```bash
python scripts/migrate_feature_flags.py
```

2. Configurer Redis (optionnel, pour prod) :
```python
# Dans feature_flag_service.py
import redis
self.cache = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)
```

3. Créer un super-admin :
```bash
python scripts/create_super_admin.py
```

4. Redémarrer les services :
```bash
sudo supervisorctl restart all
```

5. Tester l'interface :
```
http://localhost:3000/admin/feature-flags
```

## Support

Pour toute question ou problème :
1. Consulter cette documentation
2. Vérifier les logs : `/var/log/supervisor/auth-microservice.*.log`
3. Vérifier MongoDB : `db.feature_flags.find()`
4. Vérifier les audits : `db.audit_events.find()`

---

**Développeur:** AI Engineer  
**Date:** 5 Novembre 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
