# Guide des Règles Métier et Feature Flags - JLC Group

## Table des Matières
1. [Règles Métier](#règles-métier)
2. [Feature Flags](#feature-flags)
3. [Stratégie de Déploiement](#stratégie-de-déploiement)
4. [Utilisation dans le Code](#utilisation-dans-le-code)

---

## Règles Métier

### Vue d'ensemble
Les règles métier définissent la logique business automatisée de l'application. Elles permettent de standardiser les comportements et d'automatiser les processus récurrents.

### Accès
**URL:** `/admin/rules`  
**Permissions requises:** `rules.manage`

### Types de Règles (4 catégories)

#### 1. 🔍 Validation
Règles de contrôle et de validation des données.

**Règles actives:**
- ✅ **Validation Automatique des Profils Complets** (Priority: 10)
  - Auto-valider les profils avec 100% complétion + documents requis + email vérifié
  
- ✅ **Vérification Documents Expirés** (Priority: 5)
  - Alerter 30 jours avant expiration des documents importants
  
- ✅ **Validation Visite Médicale Obligatoire** (Priority: 100)
  - Bloquer l'attribution de missions sans visite médicale valide

#### 2. 🔔 Notification
Règles de notification automatique.

**Règles actives:**
- ✅ **Notification Nouvelle Candidature** (Priority: 20)
  - Notifier admin + commercial lors d'une nouvelle candidature
  
- ✅ **Notification Changement Statut Mission** (Priority: 15)
  - Notifier toutes les parties prenantes lors des changements de statut

**Règles désactivées:**
- ⚪ **Rappel Profil Incomplet**
  - Rappel automatique après 7 jours (à activer manuellement)

#### 3. 🔄 Workflow
Règles de gestion des processus métier.

**Règles actives:**
- ✅ **Workflow Candidature Standard** (Priority: 30)
  - Gérer automatiquement le cycle de vie d'une candidature
  
- ✅ **Workflow Onboarding Intérimaire** (Priority: 50)
  - Automatiser la transformation candidat → intérimaire

**Règles désactivées:**
- ⚪ **Archivage Automatique Missions Anciennes**
  - Archiver les missions terminées depuis +6 mois

#### 4. ⚙️ Automation
Règles d'automatisation avancée.

**Toutes désactivées (en développement):**
- ⚪ **Attribution Automatique Missions Urgentes** (Priority: 80)
  - Nécessite IA de matching
  
- ⚪ **Calcul Automatique Salaire** (Priority: 100)
  - À implémenter
  
- ⚪ **Génération Automatique Rapports Mensuels** (Priority: 10)
  - Rapports mensuels automatiques

### Structure d'une Règle

```javascript
{
  "id": "uuid",
  "name": "Nom de la règle",
  "description": "Description détaillée",
  "rule_type": "validation|notification|workflow|automation",
  "conditions": {
    // Conditions pour déclencher la règle
    "profile_completion": {"min": 100},
    "required_documents": ["cv", "id_card"]
  },
  "actions": {
    // Actions à exécuter
    "set_status": "validated",
    "send_notification": true
  },
  "priority": 10,  // Ordre d'exécution (plus élevé = prioritaire)
  "is_active": true
}
```

### API Endpoints

**Lister les règles:**
```bash
GET /api/config/rules?rule_type=validation&is_active=true
```

**Créer une règle:**
```bash
POST /api/config/rules
Authorization: Bearer {token}
{
  "name": "Nouvelle Règle",
  "rule_type": "validation",
  "conditions": {...},
  "actions": {...},
  "priority": 10,
  "is_active": true
}
```

### Réinitialiser les Règles

```bash
cd /app/auth-microservice
python scripts/init_business_rules.py
```

---

## Feature Flags

### Vue d'ensemble
Les feature flags permettent de contrôler l'activation des fonctionnalités sans déploiement. Toutes les nouvelles features sont **admin-only par défaut**.

### Accès
**URL:** `/admin/feature-flags`  
**Permissions requises:** `flags.manage`

### Stratégie par Défaut
🔒 **Toutes les nouvelles fonctionnalités sont désactivées ou limitées aux administrateurs** jusqu'à validation complète.

### Feature Flags Disponibles (21)

#### ✅ Features Actives (6)

| Flag | Nom | Rôles | Description |
|------|-----|-------|-------------|
| `feature.dashboard.unified` | Dashboard Unifié | Admin | Widgets personnalisables |
| `feature.profile.postulant` | Dashboard Postulant | Candidat, Postulant | Parcours guidé |
| `feature.entreprises.management` | Gestion Entreprises | Admin, Commercial | Édition inline |
| `feature.admin.audit_logs` | Logs d'Audit | Admin | Historique complet |
| `feature.admin.system_health` | Monitoring Système | Admin | Santé du système |
| `feature.admin.data_export` | Export Données | Admin | Export massif |

#### 🔴 Features en Développement (15)

##### Priorité Haute
- `feature.validation.email` - Validation Email Obligatoire (Admin)
- `feature.ai.matching` - Matching IA Missions (Admin)
- `feature.notifications.realtime` - Notifications Temps Réel (Admin)

##### Priorité Moyenne
- `feature.cv.auto_generate` - Génération CV Auto (Admin)
- `feature.chat.messaging` - Système de Chat (Admin)
- `feature.documents.advanced` - Gestion Documents (Admin)
- `feature.reports.advanced` - Rapports Avancés (Admin, Commercial)
- `feature.timesheet.validation` - Validation Feuilles de Temps (Admin, Commercial)

##### Fonctionnalités Futures
- `feature.pointage.electronic` - Pointage Électronique (Admin)
- `feature.signature.electronic` - Signature Électronique (Admin)
- `feature.gamification` - Gamification (Admin)
- `feature.geography.v2` - Gestion Géographique V2 (Admin)
- `feature.ai.recommendations` - Recommandations IA (Admin)
- `feature.mobile.app` - Application Mobile (Global)
- `feature.api.public` - API Publique (Global)

### Types de Feature Flags

#### 🌐 GLOBAL
Activé/désactivé pour tous les utilisateurs.
```javascript
{
  "type": "GLOBAL",
  "enabled": false,
  "target": null
}
```

#### 👥 ROLE
Activé uniquement pour certains rôles.
```javascript
{
  "type": "ROLE",
  "enabled": true,
  "target": ["admin", "commercial"]
}
```

### API Endpoints

**Vérifier un flag:**
```bash
GET /api/feature-flags/check/feature.ai.matching
Authorization: Bearer {token}

Response: {
  "flag_key": "feature.ai.matching",
  "enabled": false,
  "user_id": "...",
  "roles": ["admin"]
}
```

**Lister tous les flags:**
```bash
GET /api/feature-flags?include_inactive=true
Authorization: Bearer {token}
```

**Activer/Désactiver:**
```bash
PATCH /api/feature-flags/{flag_id}
Authorization: Bearer {token}
{
  "enabled": true,
  "target": ["admin", "commercial"]
}
```

### Réinitialiser les Feature Flags

```bash
cd /app/auth-microservice
python scripts/init_feature_flags.py
```

---

## Stratégie de Déploiement

### Phase 1: Admin Only (Défaut)
🔒 Nouvelle feature créée → Désactivée ou Admin uniquement
- Tests internes
- Validation fonctionnelle
- Correction des bugs

### Phase 2: Beta Testing
👥 Élargissement progressif
- Ajouter rôle `commercial`
- Tests avec utilisateurs de confiance
- Collecte de feedback

### Phase 3: Production Limitée
📊 Rollout progressif
- Activer pour 10% des utilisateurs
- Monitoring des performances
- Ajustements si nécessaire

### Phase 4: Production Complète
✅ Activation générale
- Disponible pour tous les rôles appropriés
- Documentation utilisateur finale
- Support actif

### Exemple de Rollout

```bash
# Phase 1: Admin only (par défaut à la création)
{
  "key": "feature.ai.matching",
  "enabled": false,
  "target": ["admin"]
}

# Phase 2: Ajout commercial pour beta
PATCH /api/feature-flags/feature_ai_matching
{
  "enabled": true,
  "target": ["admin", "commercial"]
}

# Phase 3: Activation pour intérimaires
PATCH /api/feature-flags/feature_ai_matching
{
  "target": ["admin", "commercial", "interim"]
}

# Phase 4: Production (si applicable à tous)
PATCH /api/feature-flags/feature_ai_matching
{
  "type": "GLOBAL",
  "enabled": true
}
```

---

## Utilisation dans le Code

### Backend (Python/FastAPI)

#### Vérifier un Feature Flag
```python
from awana_auth.services.feature_flag_service import FeatureFlagService
from awana_auth.core.feature_flag_models import FeatureFlagContext

async def my_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    service = FeatureFlagService(db)
    
    context = FeatureFlagContext(
        user_id=current_user.id,
        roles=current_user.roles,
        environment="production"
    )
    
    if await service.is_enabled("feature.ai.matching", context):
        # Feature activée
        return await ai_matching_logic()
    else:
        # Feature désactivée
        return {"message": "Feature not available"}
```

#### Protéger une Route Entière
```python
@router.get("/ai-matching")
async def ai_matching_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Vérifier le flag
    service = FeatureFlagService(db)
    context = FeatureFlagContext(
        user_id=current_user.id,
        roles=current_user.roles,
        environment="production"
    )
    
    if not await service.is_enabled("feature.ai.matching", context):
        raise HTTPException(
            status_code=403,
            detail="This feature is not available for your account"
        )
    
    # Suite de la logique...
```

### Frontend (React/TypeScript)

#### Utiliser le Hook useFeatureFlag
```typescript
import { useFeatureFlag, FeatureGate } from '@/hooks/useFeatureFlag'

function MyComponent() {
  const { isEnabled, isLoading } = useFeatureFlag('feature.ai.matching')
  
  if (isLoading) return <Spinner />
  
  if (!isEnabled) {
    return <div>Feature not available</div>
  }
  
  return <AIMatchingComponent />
}
```

#### Composant FeatureGate
```typescript
import { FeatureGate } from '@/hooks/useFeatureFlag'

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Affiche le composant uniquement si le flag est activé */}
      <FeatureGate flag="feature.ai.matching">
        <AIMatchingPanel />
      </FeatureGate>
      
      {/* Avec fallback */}
      <FeatureGate 
        flag="feature.chat.messaging"
        fallback={<ComingSoonBanner />}
      >
        <ChatWidget />
      </FeatureGate>
    </div>
  )
}
```

#### Vérifier Plusieurs Flags
```typescript
import { useFeatureFlags } from '@/hooks/useFeatureFlag'

function AdminPanel() {
  const flags = useFeatureFlags([
    'feature.ai.matching',
    'feature.reports.advanced',
    'feature.admin.data_export'
  ])
  
  return (
    <div>
      {flags['feature.ai.matching'] && <AIMatchingButton />}
      {flags['feature.reports.advanced'] && <ReportsButton />}
      {flags['feature.admin.data_export'] && <ExportButton />}
    </div>
  )
}
```

#### Cacher des Éléments de Menu
```typescript
import { useFeatureFlag } from '@/hooks/useFeatureFlag'

function Sidebar() {
  const aiMatching = useFeatureFlag('feature.ai.matching')
  const chat = useFeatureFlag('feature.chat.messaging')
  
  return (
    <nav>
      <MenuItem to="/dashboard">Dashboard</MenuItem>
      <MenuItem to="/missions">Missions</MenuItem>
      
      {aiMatching.isEnabled && (
        <MenuItem to="/ai-matching">AI Matching</MenuItem>
      )}
      
      {chat.isEnabled && (
        <MenuItem to="/messages">Messages</MenuItem>
      )}
    </nav>
  )
}
```

---

## Bonnes Pratiques

### ✅ À FAIRE

1. **Toujours commencer en Admin Only**
   - Nouvelle feature = Admin only par défaut
   - Tests internes avant ouverture

2. **Utiliser des Noms Clairs**
   - Format: `feature.{domain}.{action}`
   - Ex: `feature.ai.matching`, `feature.chat.messaging`

3. **Documenter les Métadonnées**
   ```javascript
   {
     "metadata": {
       "phase": "development",
       "requires": ["openai_key"],
       "version": "1.0"
     }
   }
   ```

4. **Rollout Progressif**
   - Admin → Beta users → 10% → 50% → 100%

5. **Nettoyer les Flags Obsolètes**
   - Supprimer les flags de features en production stable

### ❌ À ÉVITER

1. ❌ Activer directement en production sans tests
2. ❌ Oublier de documenter les dépendances
3. ❌ Laisser des flags inutilisés dans le code
4. ❌ Modifier le `target` sans planification
5. ❌ Déployer sans feature flag pour features majeures

---

## Monitoring & Audit

### Logs d'Audit
Toutes les modifications de feature flags et règles métier sont loggées :
- Qui a modifié
- Quand
- Quoi (ancien état → nouvel état)
- Pourquoi (si description fournie)

### Alertes Recommandées
- Flag activé pour la première fois
- Flag désactivé en urgence
- Règle métier échouée plusieurs fois
- Règle avec priority > 90 modifiée

---

## Support

**Documentation technique:**
- Feature Flags: `/app/auth-microservice/feature_flag_routes.py`
- Règles Métier: `/app/auth-microservice/configuration_routes.py`
- Frontend Hook: `/app/apps/web/src/hooks/useFeatureFlag.ts`

**Scripts de migration:**
- `/app/auth-microservice/scripts/init_business_rules.py`
- `/app/auth-microservice/scripts/init_feature_flags.py`

**Contact:**
- Email: support@jlcgroup.ga
- Slack: #platform-support
