# 📚 Guide Complet - Configuration Dynamique JLC

## Table des Matières

1. [Introduction](#introduction)
2. [Référentiels (System References)](#référentiels-system-references)
3. [Règles Métier (Business Rules)](#règles-métier-business-rules)
4. [Feature Flags](#feature-flags)
5. [Cas d'Usage Concrets](#cas-dusage-concrets)
6. [Workflows Complets](#workflows-complets)

---

## Introduction

L'application JLC utilise un système de configuration dynamique à trois niveaux :

| Système | Objectif | Portée |
|---------|----------|--------|
| **Référentiels** | Données de référence (listes, types) | Application entière |
| **Règles Métier** | Logique métier configurable | Processus spécifiques |
| **Feature Flags** | Activation/désactivation de fonctionnalités | Par environnement/rôle/utilisateur |

**Avantages :**
- ✅ Modifications sans redéploiement
- ✅ Configuration par environnement
- ✅ A/B testing facile
- ✅ Rollback instantané
- ✅ Audit complet

---

## Référentiels (System References)

### 📖 Concept

Les référentiels sont des **listes de valeurs prédéfinies** utilisées dans toute l'application (types de contrats, statuts, secteurs d'activité, etc.).

### 🗄️ Structure MongoDB

```javascript
// Collection: system_references
{
  "_id": ObjectId("..."),
  "id": "uuid",
  "category": "contract_types",  // Catégorie du référentiel
  "code": "cdi",                  // Code unique
  "label_fr": "CDI",              // Libellé français
  "label_en": "Permanent Contract", // Libellé anglais
  "description": "Contrat à durée indéterminée",
  "is_active": true,
  "order": 1,                     // Ordre d'affichage
  "metadata": {                   // Données supplémentaires
    "icon": "briefcase",
    "color": "#4CAF50"
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 📋 Catégories Principales

#### 1. Types de Contrats (`contract_types`)

```javascript
[
  {
    "category": "contract_types",
    "code": "cdi",
    "label_fr": "CDI",
    "label_en": "Permanent Contract",
    "is_active": true,
    "order": 1,
    "metadata": {
      "duration": "indefinite",
      "trial_period_days": 90
    }
  },
  {
    "category": "contract_types",
    "code": "cdd",
    "label_fr": "CDD",
    "label_en": "Fixed-term Contract",
    "is_active": true,
    "order": 2,
    "metadata": {
      "duration": "fixed",
      "max_duration_months": 18
    }
  },
  {
    "category": "contract_types",
    "code": "interim",
    "label_fr": "Intérim",
    "label_en": "Temporary Work",
    "is_active": true,
    "order": 3,
    "metadata": {
      "duration": "mission_based",
      "renewable": true
    }
  }
]
```

#### 2. Statuts Utilisateur (`user_statuses`)

```javascript
[
  {
    "category": "user_statuses",
    "code": "active",
    "label_fr": "Actif",
    "label_en": "Active",
    "metadata": {
      "color": "#4CAF50",
      "icon": "check-circle"
    }
  },
  {
    "category": "user_statuses",
    "code": "inactive",
    "label_fr": "Inactif",
    "label_en": "Inactive",
    "metadata": {
      "color": "#9E9E9E",
      "icon": "x-circle"
    }
  },
  {
    "category": "user_statuses",
    "code": "suspended",
    "label_fr": "Suspendu",
    "label_en": "Suspended",
    "metadata": {
      "color": "#FF9800",
      "icon": "pause-circle"
    }
  }
]
```

#### 3. Secteurs d'Activité (`sectors`)

```javascript
[
  {
    "category": "sectors",
    "code": "it",
    "label_fr": "Informatique & Tech",
    "label_en": "IT & Technology",
    "description": "Développement, infrastructure, cybersécurité",
    "metadata": {
      "icon": "code",
      "color": "#2196F3"
    }
  },
  {
    "category": "sectors",
    "code": "finance",
    "label_fr": "Finance & Banque",
    "label_en": "Finance & Banking",
    "metadata": {
      "icon": "currency-dollar",
      "color": "#4CAF50"
    }
  },
  {
    "category": "sectors",
    "code": "healthcare",
    "label_fr": "Santé",
    "label_en": "Healthcare",
    "metadata": {
      "icon": "heart",
      "color": "#F44336"
    }
  }
]
```

#### 4. Compétences (`skills`)

```javascript
[
  {
    "category": "skills",
    "code": "javascript",
    "label_fr": "JavaScript",
    "label_en": "JavaScript",
    "metadata": {
      "type": "technical",
      "level": ["junior", "intermediate", "senior"]
    }
  },
  {
    "category": "skills",
    "code": "communication",
    "label_fr": "Communication",
    "label_en": "Communication",
    "metadata": {
      "type": "soft_skill"
    }
  }
]
```

### 🔧 API - Gestion des Référentiels

#### Récupérer tous les référentiels

```bash
GET /api/references
```

**Réponse :**
```json
{
  "references": [
    {
      "id": "uuid",
      "category": "contract_types",
      "code": "cdi",
      "label_fr": "CDI",
      "label_en": "Permanent Contract",
      "is_active": true
    }
  ]
}
```

#### Récupérer par catégorie

```bash
GET /api/references?category=contract_types
```

#### Créer un référentiel

```bash
POST /api/references
Content-Type: application/json

{
  "category": "skills",
  "code": "python",
  "label_fr": "Python",
  "label_en": "Python",
  "description": "Langage de programmation Python",
  "metadata": {
    "type": "technical",
    "icon": "code"
  }
}
```

#### Mettre à jour

```bash
PUT /api/references/{id}
Content-Type: application/json

{
  "label_fr": "Python - Développement",
  "is_active": true
}
```

### 💻 Utilisation Frontend

#### Hook personnalisé

```typescript
// hooks/useReferences.ts
import { useGetReferencesQuery } from '@/features/admin/api/referencesApi'

export const useReferences = (category?: string) => {
  const { data, isLoading, error } = useGetReferencesQuery(
    category ? { category } : undefined
  )
  
  return {
    references: data?.references || [],
    isLoading,
    error
  }
}
```

#### Utilisation dans un composant

```typescript
// components/ContractTypeSelect.tsx
import { useReferences } from '@/hooks/useReferences'

export const ContractTypeSelect = () => {
  const { references: contractTypes, isLoading } = useReferences('contract_types')
  
  if (isLoading) return <Spinner />
  
  return (
    <select>
      {contractTypes
        .filter(ct => ct.is_active)
        .sort((a, b) => a.order - b.order)
        .map(type => (
          <option key={type.code} value={type.code}>
            {type.label_fr}
          </option>
        ))}
    </select>
  )
}
```

---

## Règles Métier (Business Rules)

### 📖 Concept

Les règles métier définissent la **logique de l'application** de manière configurable (validations, calculs, workflows).

### 🗄️ Structure MongoDB

```javascript
// Collection: business_rules
{
  "_id": ObjectId("..."),
  "id": "uuid",
  "name": "interim_application_rules",
  "description": "Règles de candidature pour intérimaires",
  "category": "interim_management",
  "is_active": true,
  "priority": 100,
  "conditions": {                    // Conditions d'application
    "roles": ["interim"],
    "environment": ["production", "staging"]
  },
  "rules": {                         // Les règles elles-mêmes
    "j_minus_5_rule": {
      "enabled": true,
      "days_before_end": 5,
      "description": "Autoriser candidature 5 jours avant fin mission"
    },
    "j_minus_14_alert": {
      "enabled": true,
      "days_before_end": 14,
      "alert_type": "warning",
      "description": "Alerte 14 jours avant fin mission"
    },
    "max_simultaneous_applications": {
      "enabled": true,
      "max_count": 3,
      "description": "Maximum 3 candidatures simultanées"
    }
  },
  "metadata": {
    "owner": "system",
    "tags": ["interim", "application", "mission"]
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 📋 Exemples de Règles Métier

#### 1. Règles de Candidature Intérim

```javascript
{
  "name": "interim_application_rules",
  "category": "interim_management",
  "rules": {
    "can_apply_before_mission_end": {
      "enabled": true,
      "days_offset": 5,
      "description": "Autoriser candidature J-5 avant fin mission"
    },
    "require_profile_completion": {
      "enabled": true,
      "min_completion_percentage": 80,
      "description": "Profil doit être complété à 80% minimum"
    },
    "require_cv": {
      "enabled": true,
      "description": "CV obligatoire pour postuler"
    },
    "max_applications_per_day": {
      "enabled": true,
      "max_count": 5,
      "description": "Maximum 5 candidatures par jour"
    },
    "blackout_period": {
      "enabled": false,
      "hours": 24,
      "description": "Période d'attente entre 2 candidatures pour la même entreprise"
    }
  }
}
```

#### 2. Règles de Validation de Mission

```javascript
{
  "name": "mission_validation_rules",
  "category": "mission_management",
  "rules": {
    "min_mission_duration": {
      "enabled": true,
      "days": 1,
      "description": "Durée minimum d'une mission"
    },
    "max_mission_duration": {
      "enabled": true,
      "days": 365,
      "description": "Durée maximum sans renouvellement"
    },
    "require_validation_steps": {
      "enabled": true,
      "steps": ["manager_approval", "hr_validation", "legal_check"],
      "description": "Étapes de validation obligatoires"
    },
    "budget_validation": {
      "enabled": true,
      "require_approval_above": 50000,
      "currency": "XAF",
      "description": "Validation budgétaire au-dessus de 50,000 XAF"
    }
  }
}
```

#### 3. Règles de Calcul de Rémunération

```javascript
{
  "name": "compensation_calculation_rules",
  "category": "payroll",
  "rules": {
    "overtime_rate": {
      "enabled": true,
      "multiplier": 1.5,
      "applies_after_hours": 40,
      "description": "Heures supplémentaires à 150%"
    },
    "night_shift_bonus": {
      "enabled": true,
      "percentage": 20,
      "start_hour": "22:00",
      "end_hour": "06:00",
      "description": "Prime de nuit 20%"
    },
    "weekend_bonus": {
      "enabled": true,
      "percentage": 50,
      "description": "Prime weekend 50%"
    },
    "seniority_bonus": {
      "enabled": true,
      "tiers": [
        {"years": 2, "percentage": 5},
        {"years": 5, "percentage": 10},
        {"years": 10, "percentage": 15}
      ]
    }
  }
}
```

#### 4. Règles de Workflow de Validation

```javascript
{
  "name": "validation_workflow_rules",
  "category": "workflow",
  "rules": {
    "application_workflow": {
      "enabled": true,
      "steps": [
        {
          "step": "application_submitted",
          "auto_transition": false,
          "notification": ["applicant", "recruiter"]
        },
        {
          "step": "application_reviewed",
          "requires_approval": true,
          "approvers": ["recruiter"],
          "sla_hours": 48
        },
        {
          "step": "interview_scheduled",
          "requires_approval": false,
          "notification": ["applicant", "interviewer"]
        },
        {
          "step": "contract_proposed",
          "requires_approval": true,
          "approvers": ["hr_manager"],
          "sla_hours": 24
        },
        {
          "step": "contract_signed",
          "final": true,
          "notification": ["all"]
        }
      ]
    }
  }
}
```

### 🔧 API - Gestion des Règles Métier

#### Récupérer toutes les règles

```bash
GET /api/business-rules
```

#### Récupérer une règle spécifique

```bash
GET /api/business-rules/interim_application_rules
```

#### Créer une règle

```bash
POST /api/business-rules
Content-Type: application/json

{
  "name": "custom_validation_rule",
  "description": "Règle de validation personnalisée",
  "category": "validation",
  "rules": {
    "custom_check": {
      "enabled": true,
      "threshold": 100
    }
  }
}
```

#### Mettre à jour une règle

```bash
PUT /api/business-rules/interim_application_rules
Content-Type: application/json

{
  "rules": {
    "can_apply_before_mission_end": {
      "enabled": true,
      "days_offset": 7  // Changé de 5 à 7 jours
    }
  }
}
```

#### Activer/Désactiver une règle

```bash
PATCH /api/business-rules/interim_application_rules/toggle
Content-Type: application/json

{
  "is_active": false
}
```

### 💻 Utilisation Backend

```python
# Exemple: Vérifier si un intérimaire peut postuler
from awana_auth.services.business_rules_service import BusinessRulesService

async def can_user_apply_to_mission(user_id: str, mission_id: str, db):
    # Récupérer les règles
    rules_service = BusinessRulesService(db)
    rules = await rules_service.get_rules("interim_application_rules")
    
    if not rules or not rules.get("is_active"):
        # Pas de règles = autorisation par défaut
        return True, None
    
    # Vérifier la complétude du profil
    if rules["rules"]["require_profile_completion"]["enabled"]:
        profile = await db.interim_profiles.find_one({"user_id": user_id})
        min_completion = rules["rules"]["require_profile_completion"]["min_completion_percentage"]
        
        if profile["profile_completion_percentage"] < min_completion:
            return False, f"Profil doit être complété à {min_completion}% minimum"
    
    # Vérifier si CV présent
    if rules["rules"]["require_cv"]["enabled"]:
        if not profile.get("cv_document_id"):
            return False, "CV obligatoire pour postuler"
    
    # Vérifier le nombre de candidatures
    if rules["rules"]["max_applications_per_day"]["enabled"]:
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        applications_today = await db.mission_applications.count_documents({
            "interim_id": user_id,
            "created_at": {"$gte": today_start.isoformat()}
        })
        
        max_count = rules["rules"]["max_applications_per_day"]["max_count"]
        if applications_today >= max_count:
            return False, f"Maximum {max_count} candidatures par jour atteint"
    
    return True, None
```

### 💻 Utilisation Frontend

```typescript
// hooks/useBusinessRules.ts
import { useGetBusinessRulesQuery } from '@/features/admin/api/businessRulesApi'

export const useBusinessRules = (ruleName: string) => {
  const { data, isLoading } = useGetBusinessRulesQuery(ruleName)
  
  const isRuleEnabled = (ruleKey: string): boolean => {
    if (!data?.rules) return false
    return data.rules[ruleKey]?.enabled === true
  }
  
  const getRuleValue = (ruleKey: string, valueKey: string): any => {
    if (!data?.rules) return null
    return data.rules[ruleKey]?.[valueKey]
  }
  
  return {
    rules: data,
    isLoading,
    isRuleEnabled,
    getRuleValue
  }
}

// Utilisation dans un composant
const ApplicationButton = ({ missionId }) => {
  const { isRuleEnabled, getRuleValue } = useBusinessRules('interim_application_rules')
  const { profile } = useProfile()
  
  const canApply = useMemo(() => {
    if (isRuleEnabled('require_profile_completion')) {
      const minCompletion = getRuleValue('require_profile_completion', 'min_completion_percentage')
      if (profile.completion < minCompletion) {
        return { allowed: false, reason: `Profil à compléter (${minCompletion}% requis)` }
      }
    }
    
    if (isRuleEnabled('require_cv') && !profile.cv_document_id) {
      return { allowed: false, reason: 'CV obligatoire' }
    }
    
    return { allowed: true }
  }, [profile, isRuleEnabled, getRuleValue])
  
  return (
    <button disabled={!canApply.allowed}>
      {canApply.allowed ? 'Postuler' : canApply.reason}
    </button>
  )
}
```

---

## Feature Flags

### 📖 Concept

Les feature flags permettent d'**activer/désactiver des fonctionnalités** sans redéploiement, avec un ciblage granulaire.

### 🎯 Niveaux de Ciblage

| Niveau | Description | Priorité |
|--------|-------------|----------|
| **GLOBAL** | Pour toute l'application | 1 (plus bas) |
| **ENVIRONMENT** | Par environnement (dev, staging, prod) | 2 |
| **ROLE** | Par rôle utilisateur | 3 |
| **USER** | Par utilisateur spécifique | 4 (plus haut) |

### 🗄️ Structure MongoDB

```javascript
// Collection: feature_flags
{
  "_id": ObjectId("..."),
  "id": "uuid",
  "name": "interim_auto_matching",
  "description": "Matching automatique intérimaire-mission par IA",
  "category": "interim_features",
  "flag_type": "ROLE",  // GLOBAL, ENVIRONMENT, ROLE, USER
  "is_enabled": true,
  "target": {
    "roles": ["interim", "agency"],
    "environments": ["staging", "production"],
    "user_ids": []
  },
  "config": {             // Configuration supplémentaire
    "matching_threshold": 0.75,
    "max_suggestions": 5,
    "auto_apply": false
  },
  "rollout_percentage": 100,  // Pour A/B testing
  "valid_from": "2025-01-01T00:00:00Z",
  "valid_until": null,
  "metadata": {
    "owner": "product_team",
    "jira_ticket": "JLC-1234",
    "requires_restart": false
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 📋 Exemples de Feature Flags

#### 1. Feature Flags Globaux

```javascript
// Nouvelle fonctionnalité pour tous
{
  "name": "email_notifications",
  "description": "Système de notifications par email",
  "flag_type": "GLOBAL",
  "is_enabled": true,
  "config": {
    "batch_size": 100,
    "retry_attempts": 3
  }
}

// Maintenance mode
{
  "name": "maintenance_mode",
  "description": "Mode maintenance de l'application",
  "flag_type": "GLOBAL",
  "is_enabled": false,
  "config": {
    "message": "Maintenance en cours, retour prévu à 14h"
  }
}
```

#### 2. Feature Flags par Environnement

```javascript
{
  "name": "debug_toolbar",
  "description": "Barre d'outils de débogage",
  "flag_type": "ENVIRONMENT",
  "is_enabled": true,
  "target": {
    "environments": ["local", "development", "staging"]
  }
}

{
  "name": "payment_sandbox",
  "description": "Utiliser le mode sandbox pour les paiements",
  "flag_type": "ENVIRONMENT",
  "is_enabled": true,
  "target": {
    "environments": ["local", "development"]
  },
  "config": {
    "sandbox_api_key": "sk_test_..."
  }
}
```

#### 3. Feature Flags par Rôle

```javascript
{
  "name": "advanced_analytics",
  "description": "Tableaux de bord analytiques avancés",
  "flag_type": "ROLE",
  "is_enabled": true,
  "target": {
    "roles": ["admin", "super_admin", "company"]
  }
}

{
  "name": "bulk_import",
  "description": "Import en masse de données",
  "flag_type": "ROLE",
  "is_enabled": true,
  "target": {
    "roles": ["admin", "super_admin"]
  },
  "config": {
    "max_file_size_mb": 10,
    "allowed_formats": ["csv", "xlsx"]
  }
}
```

#### 4. Feature Flags par Utilisateur

```javascript
{
  "name": "beta_features",
  "description": "Accès aux fonctionnalités beta",
  "flag_type": "USER",
  "is_enabled": true,
  "target": {
    "user_ids": [
      "user-uuid-1",
      "user-uuid-2"
    ]
  }
}
```

#### 5. Feature Flags avec Rollout Progressif

```javascript
{
  "name": "new_dashboard_ui",
  "description": "Nouveau design du tableau de bord",
  "flag_type": "ROLE",
  "is_enabled": true,
  "target": {
    "roles": ["interim"]
  },
  "rollout_percentage": 25,  // 25% des utilisateurs ciblés
  "config": {
    "theme": "modern",
    "animations_enabled": true
  }
}
```

### 🔧 API - Gestion des Feature Flags

#### Récupérer tous les feature flags

```bash
GET /api/feature-flags
```

#### Récupérer les flags actifs pour l'utilisateur courant

```bash
GET /api/feature-flags/active
Authorization: Bearer {token}
```

**Réponse :**
```json
{
  "feature_flags": {
    "email_notifications": true,
    "advanced_analytics": true,
    "new_dashboard_ui": false
  }
}
```

#### Créer un feature flag

```bash
POST /api/feature-flags
Content-Type: application/json

{
  "name": "ai_assistant",
  "description": "Assistant IA pour aide contextuelle",
  "flag_type": "ROLE",
  "is_enabled": true,
  "target": {
    "roles": ["all"]
  },
  "config": {
    "model": "gpt-4",
    "max_tokens": 500
  }
}
```

#### Activer/Désactiver un flag

```bash
PATCH /api/feature-flags/ai_assistant/toggle
Content-Type: application/json

{
  "is_enabled": true
}
```

#### Mettre à jour le rollout

```bash
PATCH /api/feature-flags/new_dashboard_ui/rollout
Content-Type: application/json

{
  "rollout_percentage": 50
}
```

### 💻 Utilisation Backend

```python
# services/feature_flag_service.py
from awana_auth.services.feature_flag_service import FeatureFlagService

async def check_feature_access(
    feature_name: str,
    user: User,
    db: AsyncIOMotorDatabase
) -> tuple[bool, dict]:
    """
    Vérifier si une feature est accessible pour l'utilisateur
    Returns: (is_enabled, config)
    """
    flag_service = FeatureFlagService(db)
    
    # Vérifier si le flag existe et est actif
    is_enabled = await flag_service.is_feature_enabled(
        feature_name=feature_name,
        user_id=user.id,
        user_roles=user.roles,
        environment=os.getenv("ENVIRONMENT", "local")
    )
    
    # Récupérer la configuration
    config = await flag_service.get_feature_config(feature_name)
    
    return is_enabled, config

# Utilisation dans une route
@app.get("/api/missions/ai-suggestions")
async def get_ai_mission_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Vérifier si la feature est activée
    is_enabled, config = await check_feature_access(
        "interim_auto_matching",
        current_user,
        db
    )
    
    if not is_enabled:
        raise HTTPException(
            status_code=403,
            detail="Feature not available"
        )
    
    # Utiliser la configuration
    threshold = config.get("matching_threshold", 0.75)
    max_suggestions = config.get("max_suggestions", 5)
    
    # Logique de matching IA...
    suggestions = await get_ai_suggestions(
        user_id=current_user.id,
        threshold=threshold,
        max_count=max_suggestions
    )
    
    return {"suggestions": suggestions}
```

### 💻 Utilisation Frontend

#### Hook personnalisé

```typescript
// hooks/useFeatureFlag.ts
import { useGetActiveFeatureFlagsQuery } from '@/features/admin/api/featureFlagApi'

export const useFeatureFlag = (flagName: string) => {
  const { data, isLoading } = useGetActiveFeatureFlagsQuery()
  
  const isEnabled = data?.feature_flags?.[flagName] === true
  const config = data?.configs?.[flagName] || {}
  
  return {
    isEnabled,
    config,
    isLoading
  }
}
```

#### Composant de protection

```typescript
// components/FeatureGate.tsx
import { useFeatureFlag } from '@/hooks/useFeatureFlag'

interface FeatureGateProps {
  feature: string
  fallback?: React.ReactNode
  children: React.ReactNode
}

export const FeatureGate = ({ feature, fallback, children }: FeatureGateProps) => {
  const { isEnabled, isLoading } = useFeatureFlag(feature)
  
  if (isLoading) return null
  if (!isEnabled) return fallback || null
  
  return <>{children}</>
}

// Utilisation
<FeatureGate 
  feature="advanced_analytics"
  fallback={<BasicAnalytics />}
>
  <AdvancedAnalytics />
</FeatureGate>
```

#### Utilisation dans un composant

```typescript
const Dashboard = () => {
  const { isEnabled: showAIAssistant, config: aiConfig } = useFeatureFlag('ai_assistant')
  const { isEnabled: showNewUI } = useFeatureFlag('new_dashboard_ui')
  
  return (
    <div className={showNewUI ? 'modern-layout' : 'classic-layout'}>
      <h1>Tableau de Bord</h1>
      
      {showAIAssistant && (
        <AIAssistant 
          model={aiConfig.model}
          maxTokens={aiConfig.max_tokens}
        />
      )}
      
      <FeatureGate feature="advanced_analytics">
        <AdvancedCharts />
      </FeatureGate>
    </div>
  )
}
```

---

## Cas d'Usage Concrets

### 🎯 Cas 1: Lancement Progressif d'une Nouvelle Feature

**Contexte:** Vous avez développé un nouveau système de matching IA pour les intérimaires.

**Objectif:** Lancer progressivement pour limiter les risques.

**Étape 1: Créer le feature flag**

```bash
POST /api/feature-flags
{
  "name": "ai_matching_v2",
  "description": "Nouveau système de matching IA",
  "flag_type": "ROLE",
  "is_enabled": true,
  "target": {
    "roles": ["interim"]
  },
  "rollout_percentage": 10,  // Commencer à 10%
  "config": {
    "algorithm": "collaborative_filtering",
    "min_confidence": 0.8
  }
}
```

**Étape 2: Monitorer les métriques**

Après 1 semaine, si tout va bien:

```bash
PATCH /api/feature-flags/ai_matching_v2/rollout
{
  "rollout_percentage": 25
}
```

**Étape 3: Rollout complet**

```bash
PATCH /api/feature-flags/ai_matching_v2/rollout
{
  "rollout_percentage": 100
}
```

**Étape 4: Promotion en feature standard**

```bash
PATCH /api/feature-flags/ai_matching_v2/toggle
{
  "flag_type": "GLOBAL",
  "is_enabled": true
}
```

### 🎯 Cas 2: Gestion d'une Règle Métier Saisonnière

**Contexte:** Pendant la période de vacances, vous voulez assouplir les règles de candidature.

**Solution:**

```javascript
// Créer une règle avec dates de validité
{
  "name": "summer_application_rules",
  "category": "interim_management",
  "is_active": true,
  "valid_from": "2025-06-01T00:00:00Z",
  "valid_until": "2025-08-31T23:59:59Z",
  "rules": {
    "max_applications_per_day": {
      "enabled": true,
      "max_count": 10  // Augmenté de 5 à 10
    },
    "require_profile_completion": {
      "enabled": true,
      "min_completion_percentage": 60  // Réduit de 80 à 60
    }
  }
}
```

**Backend:**

```python
async def get_applicable_rules(category: str, db):
    now = datetime.now(timezone.utc)
    
    rules = await db.business_rules.find({
        "category": category,
        "is_active": True,
        "$or": [
            {"valid_until": None},
            {"valid_until": {"$gte": now.isoformat()}}
        ],
        "valid_from": {"$lte": now.isoformat()}
    }).sort("priority", -1).to_list(None)
    
    # Retourner la règle avec la plus haute priorité
    return rules[0] if rules else None
```

### 🎯 Cas 3: A/B Testing d'une Feature UI

**Contexte:** Tester 2 versions d'un dashboard.

**Feature Flag A (50% des utilisateurs):**

```javascript
{
  "name": "dashboard_variant_a",
  "flag_type": "ROLE",
  "target": {"roles": ["interim"]},
  "rollout_percentage": 50,
  "config": {
    "variant": "A",
    "layout": "grid",
    "show_charts": true
  }
}
```

**Feature Flag B (50% restants):**

```javascript
{
  "name": "dashboard_variant_b",
  "flag_type": "ROLE",
  "target": {"roles": ["interim"]},
  "rollout_percentage": 50,
  "config": {
    "variant": "B",
    "layout": "list",
    "show_tables": true
  }
}
```

**Frontend:**

```typescript
const Dashboard = () => {
  const { isEnabled: variantA, config: configA } = useFeatureFlag('dashboard_variant_a')
  const { isEnabled: variantB, config: configB } = useFeatureFlag('dashboard_variant_b')
  
  // Analytics tracking
  useEffect(() => {
    const variant = variantA ? 'A' : variantB ? 'B' : 'default'
    analytics.track('dashboard_variant_viewed', { variant })
  }, [variantA, variantB])
  
  if (variantA) {
    return <DashboardGridLayout config={configA} />
  }
  
  if (variantB) {
    return <DashboardListLayout config={configB} />
  }
  
  return <DefaultDashboard />
}
```

### 🎯 Cas 4: Configuration Multi-Environnement

**Contexte:** Comportements différents par environnement.

**Feature Flags:**

```javascript
// Development - debugging activé
{
  "name": "api_debug_mode",
  "flag_type": "ENVIRONMENT",
  "target": {"environments": ["local", "development"]},
  "is_enabled": true,
  "config": {
    "log_level": "DEBUG",
    "show_sql": true,
    "response_time_logging": true
  }
}

// Staging - données de test
{
  "name": "use_test_data",
  "flag_type": "ENVIRONMENT",
  "target": {"environments": ["staging"]},
  "is_enabled": true,
  "config": {
    "test_payment_gateway": true,
    "mock_external_apis": true
  }
}

// Production - features stables uniquement
{
  "name": "experimental_features",
  "flag_type": "ENVIRONMENT",
  "target": {"environments": ["production"]},
  "is_enabled": false
}
```

---

## Workflows Complets

### 🔄 Workflow 1: Ajout d'un Nouveau Secteur d'Activité

**Étape 1: Créer le référentiel**

```bash
POST /api/references
{
  "category": "sectors",
  "code": "logistics",
  "label_fr": "Logistique & Transport",
  "label_en": "Logistics & Transportation",
  "description": "Secteur logistique et transport",
  "metadata": {
    "icon": "truck",
    "color": "#FF9800"
  }
}
```

**Étape 2: Créer les compétences associées**

```bash
POST /api/references
{
  "category": "skills",
  "code": "forklift_license",
  "label_fr": "Permis Chariot Élévateur",
  "label_en": "Forklift License",
  "metadata": {
    "sector": "logistics",
    "type": "certification"
  }
}
```

**Étape 3: Le secteur apparaît automatiquement**

Le frontend récupère les références et affiche le nouveau secteur dans tous les formulaires concernés sans modification de code.

### 🔄 Workflow 2: Modification d'une Règle Métier

**Contexte:** Changer le délai de candidature de J-5 à J-7.

**Étape 1: Interface Admin**

```typescript
// Dans l'interface admin
const updateRule = async () => {
  await updateBusinessRule({
    name: 'interim_application_rules',
    rules: {
      can_apply_before_mission_end: {
        enabled: true,
        days_offset: 7  // Changé de 5 à 7
      }
    }
  })
}
```

**Étape 2: Vérification côté backend**

Le backend utilise automatiquement la nouvelle valeur:

```python
rules = await get_business_rules("interim_application_rules")
days_offset = rules["rules"]["can_apply_before_mission_end"]["days_offset"]
# days_offset = 7 maintenant

can_apply = (mission_end_date - now).days <= days_offset
```

**Étape 3: Impact immédiat**

Tous les intérimaires peuvent maintenant postuler 7 jours avant la fin de leur mission au lieu de 5.

### 🔄 Workflow 3: Rollback d'une Feature Problématique

**Contexte:** Une nouvelle feature cause des bugs en production.

**Action immédiate:**

```bash
PATCH /api/feature-flags/problematic_feature/toggle
{
  "is_enabled": false
}
```

**Résultat:** La feature est désactivée instantanément pour tous les utilisateurs, sans redéploiement.

---

## Bonnes Pratiques

### ✅ Référentiels

1. **Nommage cohérent:** Utilisez des codes snake_case
2. **Traductions:** Toujours fournir label_fr et label_en
3. **Métadonnées:** Utilisez metadata pour des infos supplémentaires
4. **Order:** Définissez l'ordre d'affichage
5. **is_active:** Permettez la désactivation sans suppression

### ✅ Règles Métier

1. **Granularité:** Une règle par concept métier
2. **Documentation:** Description claire de chaque règle
3. **Versioning:** Utilisez valid_from/valid_until pour les règles temporaires
4. **Priority:** Définissez les priorités pour résoudre les conflits
5. **Testing:** Testez toujours avec is_active=false d'abord

### ✅ Feature Flags

1. **Nommage descriptif:** `feature_what_it_does`
2. **Rollout progressif:** Commencez à 10%, puis 25%, 50%, 100%
3. **Monitoring:** Suivez les métriques pour chaque variant
4. **Cleanup:** Supprimez les flags devenus permanents
5. **Documentation:** Documentez l'objectif et la durée prévue

---

## Conclusion

Le système de configuration dynamique de JLC permet une **agilité maximale** :

✅ **Référentiels** : Données de référence centralisées et multilingues
✅ **Règles Métier** : Logique métier configurable sans code
✅ **Feature Flags** : Activation/désactivation granulaire de features

**Avantages clés:**
- 🚀 Déploiement rapide de changements
- 🔄 Rollback instantané
- 🎯 Ciblage précis (rôle, environnement, utilisateur)
- 📊 A/B testing facile
- 🔍 Audit complet des changements

---

**Version:** 1.0.0  
**Dernière mise à jour:** Novembre 2025
