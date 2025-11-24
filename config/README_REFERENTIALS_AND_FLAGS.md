# 📚 Référentiels et Feature Flags - Guide Complet

## Vue d'ensemble

Le système de configuration centralisé gère deux composants essentiels :
1. **Référentiels** : Listes de valeurs, énumérations, données de référence
2. **Feature Flags** : Activation/désactivation dynamique de fonctionnalités

**Principe :** Config-driven, tout est défini dans des fichiers YAML versionnés.

---

## 📋 Référentiels

### Fichier de Configuration

**Emplacement :** `/app/config/referentials_config.yaml`

### Référentiels Disponibles

| Référentiel | Items | Description |
|-------------|-------|-------------|
| `user_statuses` | 5 | Statuts utilisateurs (actif, inactif, etc.) |
| `mission_statuses` | 8 | Statuts missions (brouillon, publiée, etc.) |
| `contract_types` | 6 | Types de contrat (CDI, CDD, intérim, etc.) |
| `business_sectors` | 10 | Secteurs d'activité |
| `experience_levels` | 4 | Niveaux d'expérience |
| `education_levels` | 7 | Niveaux d'études |
| `document_types` | 6 | Types de documents |
| `countries` | 5 | Pays |
| `cities_gabon` | 6 | Villes du Gabon |
| `application_statuses` | 7 | Statuts de candidature |
| `languages` | 5 | Langues |
| `language_levels` | 5 | Niveaux de langue |

### Initialisation

```bash
# Initialiser tous les référentiels
python3 /app/scripts/init_referentials.py

# Avec nettoyage des obsolètes
python3 /app/scripts/init_referentials.py --clean

# Avec config personnalisée
python3 /app/scripts/init_referentials.py --config /path/to/custom.yaml
```

### Structure d'un Référentiel

```yaml
user_statuses:
  collection: "referentials"  # Collection MongoDB
  key: "user_statuses"        # Clé unique
  version: "1.0"              # Version
  items:
    - code: "active"          # Code unique
      label:
        fr: "Actif"           # Label français
        en: "Active"          # Label anglais
      color: "green"          # Couleur UI
      description: "..."      # Description
      order: 1                # Ordre d'affichage
```

### Utilisation

**Backend (Python):**
```python
from motor.motor_asyncio import AsyncIOMotorClient

async def get_referential(key: str):
    db = client.jlc_db
    ref = await db.referentials.find_one({"key": key})
    return ref["items"] if ref else []

# Exemple
statuses = await get_referential("user_statuses")
```

**Frontend (React):**
```typescript
import { useReferential } from '@/hooks/useReferential';

function MyComponent() {
  const { data: statuses, isLoading } = useReferential('user_statuses');
  
  return (
    <select>
      {statuses?.map(status => (
        <option key={status.code} value={status.code}>
          {status.label.fr}
        </option>
      ))}
    </select>
  );
}
```

**API REST:**
```bash
GET /api/referentials/user_statuses
```

### Ajouter un Référentiel

1. Éditer `/app/config/referentials_config.yaml`
2. Ajouter la nouvelle section :

```yaml
payment_methods:
  collection: "referentials"
  key: "payment_methods"
  version: "1.0"
  items:
    - code: "credit_card"
      label:
        fr: "Carte bancaire"
        en: "Credit Card"
      order: 1
```

3. Exécuter : `python3 init_referentials.py`

---

## 🚩 Feature Flags

### Fichier de Configuration

**Emplacement :** `/app/config/feature_flags_config.yaml`

### Feature Flags Disponibles

#### ✅ Activés

| Flag | Description | Rollout |
|------|-------------|---------|
| `badge_new_user` | Badge NOUVEAU sur profils | 100% |
| `realtime_notifications` | Notifications temps réel WebSocket | 100% |
| `dark_mode` | Mode sombre | 100% |
| `data_export` | Export de données | 100% |
| `bulk_import` | Import en masse | 100% |
| `email_notifications` | Notifications email | 100% |
| `custom_tags` | Tags personnalisés | 100% |
| `favorites_system` | Système de favoris | 100% |
| `internal_notes` | Notes internes | 100% |
| `audit_trail` | Historique d'audit | 100% |

#### ⏸️ Désactivés

| Flag | Description | Rollout |
|------|-------------|---------|
| `ai_matching` | Matching IA candidats/missions | 0% |
| `electronic_signature` | Signature électronique | 0% |
| `integrated_chat` | Chat intégré | 0% |
| `advanced_analytics` | Analytics avancé | 0% |
| `cv_auto_generation` | Génération auto CV | 0% |
| `mfa` | Authentification multi-facteurs | 0% |
| `public_api` | API publique | 0% |
| `ai_recommendations` | Recommandations IA (Beta) | 10% |
| `video_interviews` | Entretiens vidéo (Beta) | 5% |

### Initialisation

```bash
# Initialiser tous les flags
python3 /app/scripts/init_feature_flags.py

# Activer un flag
python3 /app/scripts/init_feature_flags.py --enable ai_matching

# Désactiver un flag
python3 /app/scripts/init_feature_flags.py --disable dark_mode
```

### Structure d'un Feature Flag

```yaml
ai_matching:
  enabled: false                    # Activé ou non
  key: "features.ai_matching"       # Clé unique
  name: "Matching IA"               # Nom affiché
  description: "Matching auto..."   # Description
  category: "matching"              # Catégorie
  config:                           # Configuration spécifique
    algorithm: "similarity_score"
    threshold: 0.75
  rollout:                          # Déploiement progressif
    percentage: 0                   # % d'utilisateurs
    enabled_for_roles: ["admin"]   # Rôles autorisés
  metadata:
    owner: "Tech Team"
    created_at: "2025-11-23"
    requires_external_service: true
```

### Utilisation

**Backend (Python):**
```python
async def is_feature_enabled(flag_key: str, user=None):
    db = client.jlc_db
    flag = await db.feature_flags.find_one({"flag_key": flag_key})
    
    if not flag or not flag.get("enabled"):
        return False
    
    # Vérifier le rollout
    rollout = flag.get("rollout", {})
    percentage = rollout.get("percentage", 100)
    
    # Vérifier les rôles si utilisateur fourni
    if user:
        enabled_roles = rollout.get("enabled_for_roles", ["*"])
        if "*" not in enabled_roles:
            user_roles = user.get("roles", [])
            if not any(role in enabled_roles for role in user_roles):
                return False
    
    # Vérifier le pourcentage de rollout
    if percentage < 100:
        # Implémentation du % de rollout
        pass
    
    return True

# Exemple
if await is_feature_enabled("ai_matching", user):
    # Logique du matching IA
    pass
```

**Frontend (React):**
```typescript
import { useFeatureFlag } from '@/hooks/useFeatureFlag';

function MyComponent() {
  const { enabled, config } = useFeatureFlag('ai_matching');
  
  if (!enabled) {
    return <LegacyComponent />;
  }
  
  return <NewAIMatchingComponent config={config} />;
}
```

**API REST:**
```bash
GET /api/features/flags/ai_matching
```

### Rollout Progressif

Le système supporte le déploiement progressif :

```yaml
my_feature:
  enabled: true
  rollout:
    percentage: 25           # Seulement 25% des utilisateurs
    enabled_for_roles:       # Uniquement ces rôles
      - "admin"
      - "beta_tester"
    beta_testers_only: true  # Réservé aux beta testers
```

### Catégories

Les feature flags sont organisés par catégorie :

- **profiles** : Fonctionnalités liées aux profils
- **matching** : Algorithmes de matching
- **notifications** : Systèmes de notification
- **documents** : Gestion documentaire
- **communication** : Chat, messaging
- **analytics** : Analyses et statistiques
- **ui** : Interface utilisateur
- **data** : Import/export de données
- **organization** : Outils d'organisation
- **collaboration** : Travail collaboratif
- **security** : Sécurité
- **integration** : Intégrations tierces
- **beta** : Fonctionnalités expérimentales

---

## 🔄 Workflow de Gestion

### Ajouter un Référentiel

1. Éditer `/app/config/referentials_config.yaml`
2. Ajouter la section
3. Exécuter `python3 init_referentials.py`
4. Vérifier en DB : `db.referentials.find({key: "..."})`

### Activer une Feature

1. Option 1 : Éditer `/app/config/feature_flags_config.yaml` et réinit
2. Option 2 : `python3 init_feature_flags.py --enable {flag_key}`

### Modifier un Référentiel

1. Éditer le fichier YAML
2. Incrémenter la version
3. Exécuter `python3 init_referentials.py`

---

## 📊 Vérification

### Référentiels

```bash
# Compter les référentiels
mongosh jlc_db --eval 'db.referentials.countDocuments({})'

# Lister les clés
mongosh jlc_db --eval 'db.referentials.find({}, {key: 1, version: 1})'

# Voir un référentiel
mongosh jlc_db --eval 'db.referentials.findOne({key: "user_statuses"})'
```

### Feature Flags

```bash
# Compter les flags
mongosh jlc_db --eval 'db.feature_flags.countDocuments({})'

# Lister les flags activés
mongosh jlc_db --eval 'db.feature_flags.find({enabled: true}, {name: 1, key: 1})'

# Voir un flag
mongosh jlc_db --eval 'db.feature_flags.findOne({flag_key: "ai_matching"})'
```

---

## 🎯 Bonnes Pratiques

### Référentiels

✅ **À FAIRE**
- Toujours définir `code` unique
- Fournir labels en FR et EN
- Incrémenter la version lors de modifications
- Ordonner logiquement avec `order`
- Ajouter des descriptions claires

❌ **À ÉVITER**
- Changer les codes existants (breaking change)
- Supprimer des items utilisés
- Oublier de mettre à jour la version

### Feature Flags

✅ **À FAIRE**
- Commencer avec `enabled: false` et `percentage: 0`
- Documenter les dépendances externes
- Indiquer les variables d'environnement requises
- Tester avec un petit pourcentage d'abord
- Historiser les changements

❌ **À ÉVITER**
- Activer directement à 100% en production
- Oublier de nettoyer les flags obsolètes
- Créer trop de flags (complexité)

---

## 📝 Checklist de Déploiement

### Nouveaux Référentiels

- [ ] Définir dans `referentials_config.yaml`
- [ ] Tester en dev
- [ ] Exécuter `init_referentials.py`
- [ ] Vérifier en DB
- [ ] Créer l'API endpoint si nécessaire
- [ ] Documenter l'usage
- [ ] Tester l'intégration frontend

### Nouvelles Features

- [ ] Définir dans `feature_flags_config.yaml`
- [ ] `enabled: false` initialement
- [ ] Définir le rollout progressif
- [ ] Implémenter la feature avec vérification du flag
- [ ] Tester avec le flag activé/désactivé
- [ ] Activer à 10%
- [ ] Monitorer les erreurs
- [ ] Augmenter progressivement à 100%
- [ ] Nettoyer le code après stabilisation

---

**Dernière mise à jour :** 23 Novembre 2025  
**Version :** 1.0
