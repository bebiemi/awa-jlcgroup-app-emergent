# 🎯 Plan d'Action - Correction des Valeurs en Dur

**Date**: 5 Novembre 2025  
**Scope**: Correction des 886 valeurs en dur identifiées

---

## 📊 Vue d'Ensemble

```
Total: 886 valeurs en dur
├── 🔴 CRITIQUE (504) → Phase 1 (0-3 jours)
├── 🟠 HAUTE (90) → Phase 2 (4-10 jours)
├── 🟡 MOYENNE (107) → Phase 3 (11-24 jours)
└── 🟢 BASSE (185) → Phase 4 (25-35 jours)
```

---

## 🔴 PHASE 1: CRITIQUE (Jours 1-3)

### Objectif: Sécurité & Workflow Métier
**504 occurrences à corriger**

---

### 1.1 Backend - Authentification & Rôles

#### 📄 `awana_auth_routes.py` (110 occurrences)

**Problème**: Rôles et statuts utilisateur hardcodés partout

**Actions**:
```python
# ❌ À remplacer:
if "admin" in user_roles:
if new_status not in ["active", "pending", "suspended", "deleted"]:
user["status"] = "pending"

# ✅ Par:
admin_role = config.get("security.roles.admin")
valid_statuses = config.get("security.user_statuses.all")
pending_status = config.get("security.user_statuses.pending")

if admin_role in user_roles:
if new_status not in valid_statuses:
user["status"] = pending_status
```

**Configuration à créer**:
```yaml
# config/base.yaml
security:
  roles:
    admin: "admin"
    super_admin: "super_admin"
    company: "company"
    interim: "interim"
    agency: "agency"
    commercial: "commercial"
    validator: "validator"
    
  user_statuses:
    active: "active"
    pending: "pending"
    suspended: "suspended"
    deleted: "deleted"
    blocked: "blocked"
    all:
      - "active"
      - "pending"
      - "suspended"
      - "deleted"
```

**Estimation**: 4-6 heures  
**Priorité**: 🔴 Critique

---

#### 📄 `mission_routes.py` (61 occurrences)

**Problème**: Rôles et permissions hardcodés dans toutes les routes

**Actions**:
```python
# ❌ À remplacer:
if not any(role in user_roles for role in ["admin", "super_admin", "company", "commercial"]):
if "interim" in user_roles:
can_publish = "admin" in user_roles or "super_admin" in user_roles

# ✅ Par:
allowed_roles = config.get("workflows.mission.permissions.create")
interim_role = config.get("security.roles.interim")
can_publish_roles = config.get("workflows.mission.permissions.publish")

if not any(role in user_roles for role in allowed_roles):
if interim_role in user_roles:
can_publish = any(role in user_roles for role in can_publish_roles)
```

**Configuration à créer**:
```yaml
# config/base.yaml
workflows:
  mission:
    permissions:
      create:
        - "admin"
        - "super_admin"
        - "company"
        - "commercial"
      publish:
        - "admin"
        - "super_admin"
        - "commercial"
      view_all:
        - "admin"
        - "super_admin"
      edit:
        - "admin"
        - "super_admin"
        - "commercial"
```

**Estimation**: 3-5 heures  
**Priorité**: 🔴 Critique

---

#### 📄 `validation_routes.py` (32 occurrences)

**Problème**: Types de validation et statuts hardcodés

**Actions**:
```python
# ❌ À remplacer:
if validation["status"] != "pending":
if validation_type == "interim":
validator_roles = ["admin", "super_admin", "commercial"]

# ✅ Par:
pending_status = config.get("workflows.validation.statuses.pending")
interim_type = config.get("workflows.validation.types.interim")
validator_roles = config.get("workflows.validation.permissions.validator_roles")

if validation["status"] != pending_status:
if validation_type == interim_type:
if not any(role in user_roles for role in validator_roles):
```

**Configuration à créer**:
```yaml
# config/base.yaml
workflows:
  validation:
    statuses:
      pending: "pending"
      approved: "approved"
      rejected: "rejected"
    types:
      interim: "interim"
      company: "company"
      collaborator: "collaborator"
    permissions:
      validator_roles:
        - "admin"
        - "super_admin"
        - "commercial"
```

**Estimation**: 2-3 heures  
**Priorité**: 🔴 Critique

---

#### 📄 `profile_routes.py` (42 occurrences)

**Problème**: Types de profil hardcodés

**Actions**:
```python
# ❌ À remplacer:
if profile_type == "interim":
if "interim" in current_user.roles:
elif profile_type == "company":

# ✅ Par:
interim_type = config.get("profiles.types.interim")
company_type = config.get("profiles.types.company")
interim_role = config.get("security.roles.interim")

if profile_type == interim_type:
if interim_role in current_user.roles:
elif profile_type == company_type:
```

**Configuration à créer**:
```yaml
# config/base.yaml
profiles:
  types:
    interim: "interim"
    company: "company"
    agency: "agency"
```

**Estimation**: 2-3 heures  
**Priorité**: 🔴 Critique

---

### 1.2 Frontend - Routes & Permissions

#### 📄 `App.tsx` (70 occurrences)

**Problème**: Rôles hardcodés dans toutes les routes protégées

**Actions**:
```typescript
// ❌ À remplacer:
if (user.roles.includes('admin')) return '/admin'
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>

// ✅ Par:
// Option 1: Charger depuis API
const roles = useAppConfig('roles')
if (user.roles.includes(roles.admin)) return '/admin'
<ProtectedRoute requiredRoles={[roles.admin, roles.super_admin]}>

// Option 2: Constantes depuis backend
import { ROLES } from '@/constants/roles'
if (user.roles.includes(ROLES.ADMIN)) return '/admin'
```

**Configuration backend à exposer**:
```python
# Créer un endpoint GET /api/config/roles
@router.get("/config/roles")
async def get_roles_config():
    return {
        "admin": config.get("security.roles.admin"),
        "super_admin": config.get("security.roles.super_admin"),
        # ...
    }
```

**Estimation**: 3-4 heures  
**Priorité**: 🔴 Critique

---

#### 📄 `ValidationsPage.tsx` (76 occurrences)

**Problème**: Types de validation et statuts hardcodés

**Actions**:
```typescript
// ❌ À remplacer:
if (validation.status === 'pending')
if (type === 'interim')

// ✅ Par:
const { statuses, types } = useValidationConfig()
if (validation.status === statuses.pending)
if (type === types.interim)
```

**Hook à créer**:
```typescript
// hooks/useValidationConfig.ts
export const useValidationConfig = () => {
  const { data } = useGetValidationConfigQuery()
  return data || DEFAULT_CONFIG
}
```

**Estimation**: 3-4 heures  
**Priorité**: 🔴 Critique

---

### 🎯 Résumé Phase 1

| Fichier | Occurrences | Estimation | Dev |
|---------|-------------|------------|-----|
| awana_auth_routes.py | 110 | 4-6h | Senior |
| mission_routes.py | 61 | 3-5h | Senior |
| validation_routes.py | 32 | 2-3h | Mid |
| profile_routes.py | 42 | 2-3h | Mid |
| App.tsx | 70 | 3-4h | Mid |
| ValidationsPage.tsx | 76 | 3-4h | Mid |
| **TOTAL Phase 1** | **~400** | **17-25h** | **2-3 devs** |

**Livrable**: 
- ✅ Configuration YAML complète
- ✅ ConfigManager utilisé partout
- ✅ API configuration exposée pour frontend
- ✅ Tests passés
- ✅ Documentation

---

## 🟠 PHASE 2: HAUTE (Jours 4-10)

### Objectif: Gestion Utilisateurs & Missions
**90 occurrences à corriger**

#### Fichiers concernés:
- `google_auth_routes.py` (47) - OAuth & statuts
- `security_routes.py` (16) - Sécurité
- `mfa_routes.py` (19) - MFA
- Autres fichiers backend (8)

**Détails complets**: Voir section Phase 2 ci-dessous

---

## 🟡 PHASE 3: MOYENNE (Jours 11-24)

### Objectif: Flexibilité Métier
**107 occurrences à corriger**

#### Fichiers concernés:
- Types de contrat (79)
- Types de document (11)
- Délais configurables (17)

---

## 🟢 PHASE 4: BASSE (Jours 25-35)

### Objectif: Messages & Limites
**185 occurrences à corriger**

#### Fichiers concernés:
- Messages d'erreur (169)
- Limites numériques (16)

---

## 📋 Checklist Quotidienne

### Développeur

Pour chaque valeur corrigée:
- [ ] Valeur ajoutée dans configuration YAML
- [ ] Code modifié pour utiliser `config.get()`
- [ ] Tests unitaires mis à jour
- [ ] Tests locaux passés
- [ ] Commit avec message descriptif
- [ ] Code review demandée

### Tech Lead / Reviewer

Pour chaque PR:
- [ ] Configuration YAML validée
- [ ] Pas de régression introduite
- [ ] Tests automatisés passés
- [ ] Documentation mise à jour
- [ ] Merge approuvé

---

## 🔧 Outils & Ressources

### Scripts Utiles

```bash
# Vérifier la progression
python scripts/audit_hardcoded_values.py

# Tester la configuration
python scripts/test_config.py

# Rechercher une valeur spécifique
grep -r "admin" --include="*.py" auth-microservice/
```

### Documentation

- [ConfigManager Guide](/app/docs/CONFIGURATION_SYSTEM_GUIDE.md)
- [Rapport Audit Complet](/app/docs/AUDIT_VALEURS_EN_DUR.md)
- [Executive Summary](/app/docs/AUDIT_EXECUTIVE_SUMMARY.md)

---

## 📞 Support

**Questions techniques**: tech-lead@jlc.com  
**Validation métier**: product-owner@jlc.com  
**Bloqueurs**: devops@jlc.com

---

## 📈 Suivi de Progression

### Tableau de Bord

| Phase | Total | Corrigé | Restant | % Complete | Status |
|-------|-------|---------|---------|------------|--------|
| 🔴 Phase 1 | 504 | 0 | 504 | 0% | 🔴 À faire |
| 🟠 Phase 2 | 90 | 0 | 90 | 0% | ⏸️ En attente |
| 🟡 Phase 3 | 107 | 0 | 107 | 0% | ⏸️ En attente |
| 🟢 Phase 4 | 185 | 0 | 185 | 0% | ⏸️ En attente |
| **TOTAL** | **886** | **0** | **886** | **0%** | 🔴 **En cours** |

**Mise à jour**: Quotidienne  
**Responsable**: Tech Lead

---

## 🎯 Critères de Succès

### Phase 1 (Critique)
- ✅ 0 rôle hardcodé dans le code
- ✅ 0 statut de validation hardcodé
- ✅ Configuration YAML complète et validée
- ✅ Tests de régression passés à 100%
- ✅ Déploiement sur dev réussi

### Projet Complet
- ✅ 0 valeur en dur dans tout le codebase
- ✅ 100% des valeurs dans configuration
- ✅ Script d'audit retourne 0 occurrences
- ✅ Documentation complète
- ✅ Formation équipe effectuée

---

**Ce plan doit être démarré IMMÉDIATEMENT. La Phase 1 est CRITIQUE pour la sécurité et la flexibilité du système.**

---

**Date de création**: 2025-11-05  
**Dernière mise à jour**: 2025-11-05  
**Prochaine révision**: Quotidienne
