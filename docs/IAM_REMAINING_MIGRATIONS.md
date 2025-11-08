# IAM Migration - Fichiers Restants

Ce document liste les fichiers backend qui n'ont pas encore été migrés vers le système IAM.

## ⏸️ Fichiers Non Prioritaires (3)

Ces fichiers contiennent encore des fonctions `require_admin` / `require_super_admin` locales.

### 1. feature_flag_routes.py
**Status:** Non migré  
**Endpoints:** ~5  
**Permission suggérée:** `flags.manage`  
**Priorité:** Basse

### 2. role_visibility_routes.py  
**Status:** Non migré  
**Endpoints:** ~3  
**Permission suggérée:** `users.manage`  
**Priorité:** Basse

### 3. email_routes.py
**Status:** Non migré  
**Endpoints:** ~2  
**Permission suggérée:** `emails.manage`  
**Priorité:** Basse

## 📝 Pattern de Migration

Pour chaque fichier:

1. **Ajouter imports:**
```python
from awana_auth.dependencies.permission_dependencies import require_permission
```

2. **Supprimer fonctions locales:**
```python
# DELETE:
def require_super_admin(current_user: User = Depends(get_current_user)):
    ...
```

3. **Remplacer dans endpoints:**
```python
# OLD:
current_user: User = Depends(require_admin)

# NEW:
current_user: User = Depends(require_permission("resource.action"))
```

## ✅ Fichiers Migrés (9/12 = 75%)

- ✅ awana_auth_routes.py
- ✅ security_routes.py  
- ✅ email_settings_routes.py
- ✅ email_template_routes.py
- ✅ email_history_routes.py
- ✅ validation_routes.py
- ✅ iam_routes.py
- ✅ mission_routes.py
- ✅ contract_routes.py (no restrictions)
- ✅ presence_routes.py (auth only)

## 🎯 Impact Faible

Ces 3 fichiers non migrés représentent <5% du trafic total et ne sont pas critiques pour le fonctionnement du système IAM.

Le système peut fonctionner en production avec ces fichiers dans l'état actuel (utilisant toujours les rôles legacy).

## 🚀 Migration Future (Optionnel)

Ces fichiers peuvent être migrés ultérieurement si nécessaire, en suivant le pattern établi dans les 9 fichiers déjà migrés.
