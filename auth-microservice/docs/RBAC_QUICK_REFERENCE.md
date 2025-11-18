# 🚀 RBAC Quick Reference - AWANA

Guide de référence rapide pour le système de permissions.

---

## 📊 Statistiques

- **114 permissions** réparties en 22 catégories
- **18 profils** métier
- **3 rôles** IAM
- **Format hybride** : UUID + Code string

---

## 🔑 Permissions essentielles par domaine

### 👔 Missions
```
missions.browse          # Voir les offres (PUBLIC)
missions.read            # Lire les détails d'une mission
missions.create          # Créer une mission (ADMIN/COMMERCIAL)
missions.manage          # Gérer toutes les missions (ADMIN)
missions.publish         # Publier une mission (ADMIN/COMMERCIAL)
```

### 📝 Candidatures
```
applications.create      # Postuler à une mission
applications.read_own    # Voir ses propres candidatures
applications.manage      # Gérer toutes les candidatures (ADMIN/RH)
applications.review      # Examiner les candidatures (COMMERCIAL/RH)
```

### 🏢 Besoins (Entreprises)
```
besoins.create          # Créer un besoin
besoins.read            # Consulter les besoins
besoins.edit            # Modifier un besoin
besoins.submit          # Soumettre à JLC
besoins.convert_to_mission  # Convertir en mission (JLC ONLY)
```

### 👥 Utilisateurs
```
users.read              # Voir les utilisateurs
users.edit              # Modifier des utilisateurs
users.manage            # Gérer tous les utilisateurs (ADMIN)
profile.manage_own      # Gérer son propre profil (TOUS)
```

### 🔐 Administration
```
admin.dashboard         # Accès au tableau de bord admin
validations.manage      # Gérer les validations
iam.profiles.manage     # Gérer les profils IAM
*.*                     # Toutes les permissions (SUPER ADMIN)
```

---

## 👥 Profils utilisateur

### 🔴 Super Admin
- **Permissions** : Toutes (114)
- **Accès** : Complet sur toute l'application
- **Code** : `super_admin`

### 🟢 Intérimaire
- **Permissions** : 4
- **Peut** : Voir offres, postuler, gérer son profil
- **Code** : `interim_user`
- **Permissions clés** :
  - `missions.browse`
  - `applications.create`
  - `applications.read_own`
  - `profile.manage_own`

### 🟠 Entreprise
- **Permissions** : 9
- **Peut** : Créer besoins, gérer profil entreprise
- **Code** : `company_admin`
- **Permissions clés** :
  - `besoins.create`
  - `besoins.submit`
  - `entreprises.read`
  - `entreprises.edit`

### 🟡 Postulant
- **Permissions** : 16+
- **Peut** : Voir offres, postuler, gérer documents
- **Code** : `profile_postulant` ou `role.postulant`
- **Phase** : Onboarding (avant validation)

### 🔵 Commercial
- **Permissions** : Gestion missions + entreprises
- **Code** : `gestionnaire_commercial`

### 🟣 RH
- **Permissions** : Gestion intérimaires + validations
- **Code** : `gestionnaire_rh`

---

## 💻 Code Snippets

### Backend - Vérifier une permission

```python
from awana_auth.services.iam_unified_service import IAMUnifiedService

# Dans un endpoint
service = IAMUnifiedService(db)
has_access = await service.user_has_permission(user_id, "missions.browse")

if not has_access:
    raise HTTPException(status_code=403, detail="Permission denied")
```

### Backend - Dependency pour protéger un endpoint

```python
from awana_auth.dependencies.permission_dependencies import require_permission

@router.get("/missions")
async def get_missions(
    current_user: User = Depends(require_permission("missions.browse")),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Endpoint protégé
    return missions
```

### Frontend - Hook de permission

```typescript
import { usePermission } from '@/hooks/usePermission'

function MissionsPage() {
  const { hasPermission, isLoading } = usePermission('missions.browse')
  
  if (isLoading) return <Loader />
  if (!hasPermission) return <Navigate to="/" />
  
  return <div>Contenu protégé</div>
}
```

### Frontend - Vérification multiple

```typescript
import { usePermissions } from '@/hooks/usePermission'

const { permissions } = usePermissions([
  'missions.browse',
  'applications.create',
  'profile.manage_own'
])

if (permissions['missions.browse']) {
  // Afficher le menu missions
}
```

### Frontend - Route protégée

```typescript
// App.tsx
<Route
  path="/offres"
  element={
    <ProtectedRoute requiredPermissions={['missions.browse']}>
      <OffresPage />
    </ProtectedRoute>
  }
/>
```

### Frontend - Affichage conditionnel

```typescript
import { usePermission } from '@/hooks/usePermission'

function MissionCard({ mission }) {
  const { hasPermission } = usePermission('applications.create')
  
  return (
    <div>
      <h2>{mission.title}</h2>
      {hasPermission && (
        <button onClick={handleApply}>Postuler</button>
      )}
    </div>
  )
}
```

---

## 🔄 API Endpoints

### Récupérer les permissions d'un utilisateur
```bash
GET /api/iam/unified/users/{userId}/permissions

Response:
{
  "user_id": "...",
  "permissions": [
    {
      "id": "bf77b8c2-...",
      "code": "missions.browse",
      "description": "Consulter les offres de mission",
      "category": "missions"
    }
  ],
  "permissions_count": 4,
  "sources": {
    "legacy_roles": ["candidat"],
    "iam_roles_count": 1,
    "profiles_count": 1
  }
}
```

### Vérifier une permission
```bash
POST /api/iam/check-permission
Content-Type: application/json

{
  "user_id": "user-uuid",
  "permission_code": "missions.browse"
}

Response:
{
  "has_permission": true,
  "permission_code": "missions.browse"
}
```

---

## 🐛 Debugging

### Vérifier les permissions d'un utilisateur dans MongoDB

```javascript
// Se connecter à MongoDB
mongosh auth_db

// Trouver l'utilisateur
db.users.findOne({username: "nina"}, {roles: 1, profile_ids: 1, group_ids: 1})

// Voir ses profils
db.profiles.find({id: {$in: ["profile_postulant"]}})

// Voir les permissions du profil
db.permissions.find({id: {$in: ["bf77b8c2-...", "missions.browse"]}})
```

### Vérifier via curl

```bash
# 1. Se connecter
TOKEN=$(curl -s -X POST "http://localhost:8001/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"nina","password":"azerty123456!!"}' \
  | jq -r '.access_token')

# 2. Récupérer l'user_id
USER_ID=$(curl -s -X POST "http://localhost:8001/api/auth/local/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"nina","password":"azerty123456!!"}' \
  | jq -r '.user.id')

# 3. Vérifier les permissions
curl -s "http://localhost:8001/api/iam/unified/users/$USER_ID/permissions" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Logs backend

```bash
# Voir les logs d'authentification
docker logs jlc-auth-dev --tail 100 | grep -i "permission\|iam"

# Logs en temps réel
docker logs jlc-auth-dev -f
```

---

## ⚠️ Points d'attention

### 1. Format mixte des permission_ids
Les profils peuvent contenir deux formats :
- UUID : `"bf77b8c2-aae4-4ffc-b000-f4cbb242824a"`
- Code : `"missions.browse"`

Le service `IAMUnifiedService` gère les deux automatiquement.

### 2. Cache frontend
Si les permissions ne se mettent pas à jour :
```javascript
// Vider le cache RTK Query
dispatch({ type: 'api/resetApiState' })

// Ou se déconnecter/reconnecter
```

### 3. Permissions vs Rôles
**✅ Utiliser** : Permissions IAM (`missions.browse`)  
**❌ Éviter** : Rôles legacy (`if user.roles.includes('candidat')`)

### 4. Scope des permissions
- `own` : Ressources propres uniquement
- `global` : Toutes les ressources
- `organization` : Dans l'organisation

---

## 📚 Ressources

- **Documentation complète** : `AWANA_RBAC_DOCUMENTATION.md`
- **Export JSON** : `awana_rbac_export.json`
- **README** : `README_RBAC.md`
- **Script de régénération** : `scripts/export_rbac.py`

---

**Dernière mise à jour** : 17 novembre 2025
