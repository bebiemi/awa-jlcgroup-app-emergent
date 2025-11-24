# 🚨 ACTIONS IMMÉDIATES - Corrections IAM Obligatoires

**PRIORITÉ: CRITIQUE**

Ces corrections doivent être appliquées IMMÉDIATEMENT pour éliminer les bugs de permissions.

## 📝 Corrections par Fichier

### email_settings_routes.py

#### GET /settings
**Ligne:** ?

**Action:**
```python
Créer permission dans iam_config.yaml et relancer init_iam_from_config.py
```

**Impact si non corrigé:** MAINTENANCE - Duplication et incohérence

---

#### GET /settings
**Ligne:** ?

**Action:**
```python
Ajouter dans /app/config/iam_config.yaml:
  - code: emails.read_config
    name: '...'
```

**Impact si non corrigé:** BUG - Erreur 500 possible

---

#### PUT /settings
**Ligne:** ?

**Action:**
```python
Créer permission dans iam_config.yaml et relancer init_iam_from_config.py
```

**Impact si non corrigé:** MAINTENANCE - Duplication et incohérence

---

#### PUT /settings
**Ligne:** ?

**Action:**
```python
Ajouter dans /app/config/iam_config.yaml:
  - code: emails.configure
    name: '...'
```

**Impact si non corrigé:** BUG - Erreur 500 possible

---

#### DELETE /settings
**Ligne:** ?

**Action:**
```python
Créer permission dans iam_config.yaml et relancer init_iam_from_config.py
```

**Impact si non corrigé:** MAINTENANCE - Duplication et incohérence

---

#### DELETE /settings
**Ligne:** ?

**Action:**
```python
Ajouter dans /app/config/iam_config.yaml:
  - code: emails.configure
    name: '...'
```

**Impact si non corrigé:** BUG - Erreur 500 possible

---

### email_verification_routes.py

#### POST /send
**Ligne:** ?

**Action:**
```python
Remplacer get_current_user par require_permission('send.create')
```

**Impact si non corrigé:** SECURITE - Controle acces insuffisant

---

#### POST /resend
**Ligne:** ?

**Action:**
```python
Remplacer get_current_user par require_permission('resend.create')
```

**Impact si non corrigé:** SECURITE - Controle acces insuffisant

---

### mission_routes.py

#### POST /{mission_id}/publish
**Ligne:** ?

**Action:**
```python
Remplacer get_current_user par require_permission('{mission_id}.create')
```

**Impact si non corrigé:** SECURITE - Controle acces insuffisant

---

#### POST /{mission_id}/apply
**Ligne:** ?

**Action:**
```python
Remplacer get_current_user par require_permission('{mission_id}.create')
```

**Impact si non corrigé:** SECURITE - Controle acces insuffisant

---

### user_detail_routes.py

#### POST /{user_id}/password/admin-update
**Ligne:** 516

**Action:**
```python
Ajouter: Depends(require_permission('users.create', scope='organization'))
```

**Impact si non corrigé:** SECURITE - Acces non autorise possible

---

### validation_routes.py

#### GET /admin
**Ligne:** 66

**Action:**
```python
Ajouter: Depends(require_permission('admin.read', scope='all'))
```

**Impact si non corrigé:** SECURITE - Acces non autorise possible

---

#### POST /admin/{validation_id}/approve
**Ligne:** 97

**Action:**
```python
Ajouter: Depends(require_permission('admin.create', scope='all'))
```

**Impact si non corrigé:** SECURITE - Acces non autorise possible

---

#### POST /admin/{validation_id}/reject
**Ligne:** 186

**Action:**
```python
Ajouter: Depends(require_permission('admin.create', scope='all'))
```

**Impact si non corrigé:** SECURITE - Acces non autorise possible

---

## 🛠️ Commandes à Exécuter

Après avoir appliqué les corrections:

```bash
# 1. Relancer l'init IAM pour créer les permissions manquantes
python3 /app/scripts/init_iam_from_config.py

# 2. Redémarrer les services
sudo supervisorctl restart auth-microservice backend

# 3. Re-lancer l'audit pour vérifier
python3 /app/scripts/audit_iam_advanced.py
```
