# 🔒 Plan d'Action - Sécurisation des Endpoints

**Date:** 24 Novembre 2025  
**Problèmes détectés:** 235  
**Routes analysées:** 378  
**Taux de protection:** 63.8%

## 📊 Résumé Exécutif

L'audit de sécurité a révélé que **36.2% des routes ne sont pas protégées**. Parmi les problèmes identifiés :

- 🔴 **10 CRITIQUES** : Routes manipulant des données sensibles sans aucune protection
- 🟠 **157 HIGH** : Routes de modification sans permissions granulaires ou permissions inexistantes
- 🟡 **68 MEDIUM** : Routes potentiellement sensibles sans protection

## 🎯 Actions Prioritaires

### Phase 1 : CRITIQUE (Immédiat - J+0)

#### 1. Routes Admin Non Protégées
**Impact:** Accès admin sans contrôle  
**Fichiers:**
- `/app/apps/api/src/presentation/routes/admin_routes.py`
- `/app/apps/api/src/presentation/routes/validation_routes.py`

**Actions:**
```python
# admin_routes.py
@router.get("/admin")
-async def admin_dashboard(db: AsyncIOMotorDatabase = Depends(get_database)):
+async def admin_dashboard(
+    current_user: User = Depends(require_permission("admin.dashboard")),
+    db: AsyncIOMotorDatabase = Depends(get_database)
+):

@router.post("/admin/{validation_id}/approve")
-async def approve_validation(...):
+async def approve_validation(
+    current_user: User = Depends(require_permission("validations.manage")),
+    ...
+):

@router.post("/admin/{validation_id}/reject")
-async def reject_validation(...):
+async def reject_validation(
+    current_user: User = Depends(require_permission("validations.manage")),
+    ...
+):
```

#### 2. Routes Utilisateurs Critiques
**Impact:** Manipulation de comptes utilisateurs  
**Fichier:** `/app/auth-microservice/user_detail_routes.py`

**Actions:**
```python
# Ajouter protection sur toutes les routes profiles
@router.get("/{user_id}/profiles")
-async def get_user_profiles(...):
+async def get_user_profiles(
+    current_user: User = Depends(require_permission("profile.view.all")),
+    ...
+):

@router.post("/{user_id}/profiles")
-async def create_user_profile(...):
+async def create_user_profile(
+    current_user: User = Depends(require_permission("profile.create")),
+    ...
+):

@router.delete("/{user_id}/profiles/{profile_id}")
-async def delete_user_profile(...):
+async def delete_user_profile(
+    current_user: User = Depends(require_permission("profile.delete")),
+    ...
+):
```

#### 3. Routes d'Archive/Rétention
**Impact:** Suppression de données sensibles  
**Fichier:** `/app/auth-microservice/user_archive_routes.py`

**Actions:**
```python
@router.patch("/{user_id}/archive")
-async def archive_user(...):
+async def archive_user(
+    current_user: User = Depends(require_permission("users.archive")),
+    ...
+):
```

#### 4. Routes de Gestion des Mots de Passe Admin
**Impact:** Réinitialisation de mot de passe sans autorisation  
**Fichier:** `/app/auth-microservice/awana_auth_routes.py`

**Actions:**
```python
@router.post("/{user_id}/password/admin-update")
-async def admin_update_password(...):
+async def admin_update_password(
+    current_user: User = Depends(require_permission("users.reset_password")),
+    ...
+):
```

#### 5. Routes de Workflow Utilisateurs
**Impact:** Accès aux données de rétention  
**Fichier:** `/app/auth-microservice/retention_management_routes.py`

**Actions:**
```python
@router.get("/users/in-workflow")
-async def get_users_in_workflow(...):
+async def get_users_in_workflow(
+    current_user: User = Depends(require_permission("users.view.all")),
+    ...
+):
```

### Phase 2 : HIGH (Urgent - J+1 à J+3)

#### 6. Permissions Email Inexistantes
**Impact:** Protection inadéquate  
**Fichiers:** `/app/auth-microservice/email_settings_routes.py`, `email_routes.py`

**Actions:**
1. **Créer les permissions manquantes:**
```yaml
# Ajouter dans /app/config/iam_config.yaml
permissions:
  - code: "emails.read_config"
    name: "Lire configuration email"
    resource: "emails"
    action: "read_config"
    category: "emails"
    
  - code: "emails.configure"
    name: "Configurer emails"
    resource: "emails"
    action: "configure"
    category: "emails"
```

2. **Relancer l'init IAM:**
```bash
python3 /app/scripts/init_iam_from_config.py
```

3. **Utiliser les permissions:**
```python
@router.get("/settings")
-async def get_settings(current_user: User = Depends(require_permission("emails.read_config"))):
+# Permission créée, code OK
```

#### 7. Routes de Vérification Email Sans Protection
**Impact:** Spam / Abus  
**Fichier:** `/app/auth-microservice/email_verification_routes.py`

**Actions:**
```python
@router.post("/send")
-async def send_verification(...):
+async def send_verification(
+    current_user: User = Depends(get_current_user),  # Au minimum authentification
+    ...
+):
```

#### 8. Routes de Modification sans Permissions Granulaires
**Impact:** Contrôle d'accès insuffisant  
**Fichiers:** Multiples

**Pattern à appliquer:**
```python
# Routes avec auth_only → Ajouter permission spécifique
-current_user: User = Depends(get_current_user)
+current_user: User = Depends(require_permission("resource.action"))
```

### Phase 3 : MEDIUM (Important - J+4 à J+7)

#### 9. Routes GET Sans Protection
**Impact:** Fuite d'informations  
**Stratégie:**
- Identifier les routes GET exposant des données sensibles
- Ajouter au minimum `Depends(get_current_user)` pour authentification
- Ajouter permissions granulaires pour données critiques

#### 10. Standardisation des Permissions
**Impact:** Cohérence du modèle IAM  
**Actions:**
1. Auditer toutes les permissions utilisées mais non définies
2. Les créer dans `iam_config.yaml`
3. Les mapper aux profils appropriés

## 📋 Tableau de Tracking

| Priorité | Route | Fichier | Status | Assigné | ETA |
|----------|-------|---------|--------|---------|-----|
| 🔴 P1 | GET /admin | admin_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | POST /admin/{id}/approve | validation_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | POST /admin/{id}/reject | validation_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | GET /{user_id}/profiles | user_detail_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | POST /{user_id}/profiles | user_detail_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | DELETE /{user_id}/profiles/{id} | user_detail_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | POST /{user_id}/password/admin-update | awana_auth_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | PATCH /{user_id}/archive | user_archive_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | GET /users/in-workflow | retention_management_routes.py | ⏳ À faire | - | J+0 |
| 🔴 P1 | GET /users/{user_id}/audit | user_detail_routes.py | ⏳ À faire | - | J+0 |
| 🟠 P2 | GET /settings | email_settings_routes.py | ⏳ À faire | - | J+1 |
| 🟠 P2 | PUT /settings | email_settings_routes.py | ⏳ À faire | - | J+1 |
| 🟠 P2 | POST /send | email_verification_routes.py | ⏳ À faire | - | J+2 |

## 🛠️ Scripts d'Aide

### Script de Correction Automatique (Proposition)

```python
# /app/scripts/fix_critical_routes.py
"""
Applique automatiquement les corrections critiques
ATTENTION: Vérifier manuellement après exécution
"""

FIXES = {
    '/app/apps/api/src/presentation/routes/admin_routes.py': [
        {
            'line_pattern': r'async def admin_dashboard\(',
            'add_before': '    current_user: User = Depends(require_permission("admin.dashboard")),\n'
        }
    ],
    # ... autres fixes
}

def apply_fixes():
    for filepath, fixes in FIXES.items():
        # Appliquer les correctifs
        pass
```

### Script de Vérification

```bash
# Vérifier qu'une route est protégée
python3 /app/scripts/audit_security_endpoints.py --check-route "GET /admin"
```

## 📈 Métriques de Suivi

### Objectifs
- **J+0:** Réduction des CRITICAL à 0
- **J+3:** Réduction des HIGH à < 20
- **J+7:** Taux de protection > 90%
- **J+14:** Tous les MEDIUM résolus

### KPIs
```
Routes protégées: 241/378 (63.8%) → Objectif: 340/378 (90%)
Routes critiques: 10 → Objectif: 0
Routes HIGH: 157 → Objectif: < 20
```

## 🔍 Recommandations Générales

### 1. Politique de Sécurité par Défaut
**Principe:** Toute nouvelle route DOIT être protégée par défaut

```python
# Template pour nouvelles routes
@router.{method}("/{path}")
async def my_endpoint(
    current_user: User = Depends(require_permission("resource.action")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Description de la route
    
    Permission requise: resource.action
    """
    pass
```

### 2. Review Checklist
Avant de merger une PR avec nouvelles routes:
- [ ] Route protégée avec permission appropriée
- [ ] Permission existe dans IAM ou créée dans iam_config.yaml
- [ ] Permission assignée aux profils appropriés
- [ ] Tests de sécurité ajoutés
- [ ] Documentation mise à jour

### 3. Audit Régulier
- **Hebdomadaire:** Audit automatique via script
- **Mensuel:** Review manuelle des nouveaux endpoints
- **Trimestriel:** Audit complet avec pen-testing

## 📚 Ressources

- Documentation IAM: `/app/config/README_IAM_CONFIG.md`
- Liste des permissions: `GET /api/iam/permissions`
- Guide des bundles: `/app/docs/BUNDLE_PERMISSIONS.md`
- Rapport d'audit complet: `/app/docs/SECURITY_AUDIT_REPORT.md`

## ✅ Validation

Une fois les corrections appliquées:

```bash
# Re-lancer l'audit
python3 /app/scripts/audit_security_endpoints.py

# Tester avec un utilisateur non-admin
curl -H "Authorization: Bearer $TOKEN" https://.../api/admin
# Doit retourner 403 Forbidden

# Tester avec un admin
curl -H "Authorization: Bearer $ADMIN_TOKEN" https://.../api/admin
# Doit retourner 200 OK avec données
```

---

**Note:** Ce plan d'action doit être exécuté progressivement. Les corrections critiques (Phase 1) sont à appliquer immédiatement. Les phases suivantes peuvent être planifiées selon les ressources disponibles.
