# 🔧 Guide Pas-à-Pas - Corrections IAM

Ce guide fournit les instructions exactes pour corriger les problèmes IAM identifiés.

---

## 🔴 PHASE 1: CORRECTIONS BLOQUANTES (30 min)

### Issue #1: POST /{user_id}/password/admin-update

**Fichier:** `/app/auth-microservice/user_detail_routes.py`  
**Ligne:** 516

**Code actuel:**
```python
@router.post("/{user_id}/password/admin-update")
async def admin_update_password(
    user_id: str,
    password_data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

**Correction à appliquer:**
```python
@router.post("/{user_id}/password/admin-update")
async def admin_update_password(
    user_id: str,
    password_data: dict,
    current_user: User = Depends(require_permission("users.reset_password", scope="all")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

**Explication:** Ajoute la vérification de permission `users.reset_password` avec scope `all` (seuls les admins peuvent réinitialiser les mots de passe).

---

### Issue #2: GET /admin

**Fichier:** `/app/apps/api/src/presentation/routes/validation_routes.py`  
**Ligne:** 66

**Code actuel:**
```python
@router.get("/admin")
async def admin_dashboard(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

**Correction à appliquer:**
```python
@router.get("/admin")
async def admin_dashboard(
    current_user: User = Depends(require_permission("admin.dashboard", scope="all")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

---

### Issue #3: POST /admin/{validation_id}/approve

**Fichier:** `/app/apps/api/src/presentation/routes/validation_routes.py`  
**Ligne:** 97

**Code actuel:**
```python
@router.post("/admin/{validation_id}/approve")
async def approve_validation(
    validation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

**Correction à appliquer:**
```python
@router.post("/admin/{validation_id}/approve")
async def approve_validation(
    validation_id: str,
    current_user: User = Depends(require_permission("validations.manage", scope="all")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

---

### Issue #4: POST /admin/{validation_id}/reject

**Fichier:** `/app/apps/api/src/presentation/routes/validation_routes.py`  
**Ligne:** 186

**Code actuel:**
```python
@router.post("/admin/{validation_id}/reject")
async def reject_validation(
    validation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

**Correction à appliquer:**
```python
@router.post("/admin/{validation_id}/reject")
async def reject_validation(
    validation_id: str,
    current_user: User = Depends(require_permission("validations.manage", scope="all")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

---

### ✅ Vérification Phase 1

```bash
# Redémarrer les services
sudo supervisorctl restart auth-microservice backend

# Tester que les endpoints sont protégés
TOKEN_USER=$(curl -s -X POST "http://localhost:8001/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"commercial1","password":"Azerty123456!!"}' | jq -r '.access_token')

# Doit retourner 403
curl -H "Authorization: Bearer $TOKEN_USER" http://localhost:8001/api/admin

# Tester avec admin
TOKEN_ADMIN=$(curl -s -X POST "http://localhost:8001/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Awana2025!"}' | jq -r '.access_token')

# Doit retourner 200
curl -H "Authorization: Bearer $TOKEN_ADMIN" http://localhost:8001/api/admin
```

---

## 🟠 PHASE 2: PERMISSIONS MANQUANTES (2-3h)

### Étape 1: Modifier le Config IAM

**Fichier:** `/app/config/iam_config.yaml`

Ajouter les permissions manquantes dans la section `permissions:`:

```yaml
permissions:
  # ... permissions existantes ...
  
  # Nouvelles permissions pour emails
  - code: "emails.read_config"
    name: "Lire configuration email"
    description: "Permet de consulter les paramètres d'email"
    resource: "emails"
    action: "read_config"
    scope: "all"
    category: "emails"
    is_system: false
    is_atomic: true
  
  - code: "emails.configure"
    name: "Configurer les emails"
    description: "Permet de modifier les paramètres d'email"
    resource: "emails"
    action: "configure"
    scope: "all"
    category: "emails"
    is_system: false
    is_atomic: true
  
  # Permissions pour email verification
  - code: "emails.send_verification"
    name: "Envoyer email de vérification"
    description: "Permet d'envoyer des emails de vérification"
    resource: "emails"
    action: "send_verification"
    scope: "own"
    category: "emails"
    is_system: false
    is_atomic: true
  
  - code: "emails.resend_verification"
    name: "Renvoyer email de vérification"
    description: "Permet de renvoyer des emails de vérification"
    resource: "emails"
    action: "resend_verification"
    scope: "own"
    category: "emails"
    is_system: false
    is_atomic: true
```

### Étape 2: Assigner aux Profils Appropriés

Dans la même fichier, ajouter ces permissions aux profils:

```yaml
profiles:
  - code: "admin"
    name: "Administrateur"
    permissions:
      # ... permissions existantes ...
      - "emails.read_config"
      - "emails.configure"
      - "emails.send_verification"
      - "emails.resend_verification"
  
  - code: "commercial"
    name: "Commercial"
    permissions:
      # ... permissions existantes ...
      - "emails.send_verification"
      - "emails.resend_verification"
```

### Étape 3: Réinitialiser IAM

```bash
cd /app
python3 scripts/init_iam_from_config.py
```

**Output attendu:**
```
✅ Permissions créées: 4
✅ Profils mis à jour: 2
✅ INITIALISATION TERMINÉE AVEC SUCCÈS!
```

### Étape 4: Redémarrer les Services

```bash
sudo supervisorctl restart auth-microservice backend
```

### ✅ Vérification Phase 2

```bash
# Vérifier que les permissions existent
curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  http://localhost:8001/api/iam/permissions | \
  jq '.[] | select(.code | contains("emails"))'

# Doit afficher les 4 nouvelles permissions

# Tester un endpoint qui utilisait ces permissions
curl -s -H "Authorization: Bearer $TOKEN_ADMIN" \
  http://localhost:8001/api/email/settings

# Ne doit plus retourner 500
```

---

## 🟡 PHASE 3: AUTH-ONLY ET SCOPES (1-2 jours)

### Pattern de Correction Auth-Only

**Avant:**
```python
@router.post("/send")
async def send_email(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

**Après:**
```python
@router.post("/send")
async def send_email(
    current_user: User = Depends(require_permission("emails.send", scope="own")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
```

### Pattern d'Ajout de Scope

**Avant:**
```python
current_user: User = Depends(require_permission("users.read"))
```

**Après:**
```python
# Si l'utilisateur peut voir ses propres données
current_user: User = Depends(require_permission("users.read", scope="own"))

# Si l'utilisateur peut voir toutes les données (admin)
current_user: User = Depends(require_permission("users.read", scope="all"))

# Si l'utilisateur peut voir les données de son entreprise
current_user: User = Depends(require_permission("users.read", scope="company"))
```

### Fichiers à Corriger (Top 10)

1. **email_verification_routes.py**
   - 3 routes à corriger (send, verify, resend)
   
2. **email_routes.py**
   - 5 routes à corriger
   
3. **notification_routes.py**
   - 7 routes à corriger
   
4. **document_routes.py**
   - 12 routes à corriger
   
5. **mission_routes.py**
   - 8 routes à corriger

*Liste complète disponible dans `IAM_CORRECTIONS_IMMEDIATE.md`*

---

## 🔄 PHASE 4: SUPPRESSION ROLE CHECKS (1 jour)

### Pattern de Correction

**Avant (MAUVAIS):**
```python
@router.get("/admin/stats")
async def admin_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Vérification hardcodée
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Logique métier
    stats = await get_stats(db)
    return stats
```

**Après (BON):**
```python
@router.get("/admin/stats")
async def admin_stats(
    current_user: User = Depends(require_permission("admin.stats", scope="all")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # La vérification est faite par le decorator
    # Pas besoin de check manuel
    
    # Logique métier
    stats = await get_stats(db)
    return stats
```

### Fichiers Concernés

1. awana_auth_routes.py (5 occurrences)
2. user_detail_routes.py (3 occurrences)
3. mission_routes.py (4 occurrences)
4. entreprise_routes.py (3 occurrences)
5. validation_routes.py (2 occurrences)

---

## 🧪 Tests de Non-Régression

Après chaque phase, exécuter:

```bash
# 1. Audit IAM
python3 /app/scripts/audit_iam_advanced.py

# 2. Tests manuels
bash /app/scripts/test_iam_endpoints.sh

# 3. Vérification logs
tail -n 100 /var/log/supervisor/*.err.log | grep -i "permission\|403\|500"
```

---

## 📊 Suivi de Progression

### Tableau de Bord

| Phase | Status | Issues Résolus | Temps Estimé | Temps Réel |
|-------|--------|----------------|--------------|------------|
| 1. Bloquants | ⏳ | 0/4 | 30 min | - |
| 2. Permissions | ⏳ | 0/49 | 2-3h | - |
| 3. Auth-Only | ⏳ | 0/55 | 1-2j | - |
| 4. Role Checks | ⏳ | 0/17 | 1j | - |

**Légende:**
- ⏳ À faire
- 🔄 En cours
- ✅ Terminé
- ❌ Bloqué

---

## 🆘 Troubleshooting

### Erreur: "Permission not found"

**Symptôme:** Erreur 500 après avoir ajouté une permission

**Solution:**
1. Vérifier que la permission est dans `iam_config.yaml`
2. Relancer `init_iam_from_config.py`
3. Vérifier dans MongoDB:
   ```bash
   python3 -c "
   import asyncio
   from motor.motor_asyncio import AsyncIOMotorClient
   async def check():
       client = AsyncIOMotorClient('mongodb://localhost:27017')
       perm = await client.auth_db.permissions.find_one({'code': 'emails.read_config'})
       print('Found' if perm else 'Not found')
   asyncio.run(check())
   "
   ```

### Erreur: "Module has no attribute 'require_permission'"

**Solution:**
Ajouter l'import en haut du fichier:
```python
from awana_auth.dependencies import require_permission
```

### Erreur: 403 même avec la bonne permission

**Solution:**
1. Vérifier que la permission est assignée au profil de l'utilisateur
2. Vérifier que l'utilisateur a le bon profil
3. Se reconnecter pour obtenir un nouveau JWT avec les permissions à jour

---

## ✅ Checklist Finale

Avant de considérer le travail terminé:

- [ ] Les 4 endpoints bloquants sont protégés
- [ ] Les 49 permissions manquantes sont créées
- [ ] Les 55 auth-only sont corrigés
- [ ] Les 17 role checks sont supprimés
- [ ] Les 149 scopes sont ajoutés
- [ ] Audit IAM retourne 0 BLOQUANT
- [ ] Audit IAM retourne < 20 IMPORTANT
- [ ] Tous les tests passent
- [ ] Documentation mise à jour
- [ ] Équipe formée aux bonnes pratiques

---

*Guide créé par Audit IAM Expert*  
*Dernière mise à jour: 24 Novembre 2025*
