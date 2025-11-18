# 📚 Documentation RBAC - AWANA

Ce répertoire contient l'export complet du système RBAC (Role-Based Access Control) de l'application AWANA.

## 📁 Fichiers disponibles

### 1. `awana_rbac_export.json` (69 KB)
**Export JSON complet du système RBAC**

Structure :
```json
{
  "metadata": {
    "application": "AWANA - Plateforme d'intérim au Gabon",
    "version": "1.0",
    "export_date": "2025-11-17",
    "statistics": {
      "total_permissions": 114,
      "total_profiles": 18,
      "total_iam_roles": 3,
      "total_iam_groups": 0
    }
  },
  "permissions": [...],  // 114 permissions
  "profiles": [...],     // 18 profils métier
  "iam_roles": [...],    // 3 rôles IAM
  "iam_groups": [...]    // 0 groupes IAM
}
```

**Utilisation :**
```bash
# Lire le fichier
cat docs/awana_rbac_export.json | jq '.permissions[] | select(.code | contains("missions"))'

# Compter les permissions par catégorie
cat docs/awana_rbac_export.json | jq '.permissions | group_by(.category) | map({category: .[0].category, count: length})'

# Lister les permissions d'un profil
cat docs/awana_rbac_export.json | jq '.profiles[] | select(.code == "interim_user")'
```

### 2. `AWANA_RBAC_DOCUMENTATION.md` (8.7 KB)
**Documentation complète et lisible du système RBAC**

Contenu :
- 📊 Vue d'ensemble du système
- 🔑 Liste complète des permissions par catégorie
- 👥 Description des profils clés
- 📋 Matrice de permissions par rôle
- 🏗️ Architecture du système
- 🔐 Logique de résolution des permissions
- 🚀 Guide d'utilisation (API + Frontend)

**À lire en priorité pour comprendre le système.**

---

## 🔄 Mettre à jour les exports

Si le système RBAC évolue (nouvelles permissions, profils, etc.), régénérez les exports :

### Depuis la ligne de commande

```bash
# Se connecter au container
docker exec -it jlc-auth-dev bash

# Lancer le script de génération
cd /app/auth-microservice
python3 scripts/export_rbac.py
```

### Depuis MongoDB directement

```bash
# Export des permissions
mongosh auth_db --quiet --eval "JSON.stringify(db.permissions.find({}, {_id:0}).toArray())" > permissions.json

# Export des profils
mongosh auth_db --quiet --eval "JSON.stringify(db.profiles.find({}, {_id:0}).toArray())" > profiles.json

# Export des rôles IAM
mongosh auth_db --quiet --eval "JSON.stringify(db.iam_roles.find({}, {_id:0}).toArray())" > iam_roles.json
```

---

## 📊 Statistiques actuelles

| Élément | Quantité | Description |
|---------|----------|-------------|
| **Permissions** | 114 | Droits atomiques (ex: `missions.browse`) |
| **Profils** | 18 | Regroupements métier de permissions |
| **Rôles IAM** | 3 | Rôles granulaires (candidat, commercial, entreprise) |
| **Groupes IAM** | 0 | Regroupements d'utilisateurs (non utilisé) |

### Répartition des permissions par catégorie

```
legacy          : 34 permissions (30%)
iam             : 15 permissions (13%)
missions        : 7 permissions (6%)
besoins         : 7 permissions (6%)
users           : 6 permissions (5%)
applications    : 5 permissions (4%)
autres          : 40 permissions (36%)
```

---

## 🔑 Permissions critiques

### Pour les Intérimaires / Candidats
- `missions.browse` - Voir les offres de missions
- `applications.create` - Postuler à une mission
- `applications.read_own` - Voir ses candidatures
- `profile.manage_own` - Gérer son profil

### Pour les Entreprises
- `besoins.create` - Créer un besoin de recrutement
- `besoins.submit` - Soumettre à JLC
- `entreprises.read` - Consulter infos entreprise
- `entreprises.edit` - Modifier infos entreprise

### Pour les Admins
- `admin.dashboard` - Accès tableau de bord admin
- `users.manage` - Gérer les utilisateurs
- `validations.manage` - Gérer les validations
- `*.*` - Toutes les permissions (super admin)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Utilisateur)                   │
├─────────────────────────────────────────────────────────┤
│ • roles: ["company", "candidat"]                        │
│ • profile_ids: ["profile_postulant", "company_admin"]  │
│ • group_ids: [] (vide actuellement)                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                Profile (Profil métier)                  │
├─────────────────────────────────────────────────────────┤
│ • code: "interim_user"                                  │
│ • name: "Intérimaire"                                   │
│ • permission_ids: ["bf77b8c2-...", "missions.browse"]  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Permission                              │
├─────────────────────────────────────────────────────────┤
│ • id: "bf77b8c2-aae4-4ffc-b000-f4cbb242824a"           │
│ • code: "missions.browse"                               │
│ • description: "Consulter les offres de mission"       │
└─────────────────────────────────────────────────────────┘
```

### Service de résolution

Le service `IAMUnifiedService` consolide les permissions depuis :

1. **Profils métier** (via `profile_ids`)
2. **Rôles IAM** (via `roles`)  
3. **Groupes IAM** (via `group_ids`)

**Note importante :** Le système supporte deux formats dans `permission_ids` :
- UUID : `"bf77b8c2-aae4-4ffc-b000-f4cbb242824a"`
- Code string : `"missions.browse"`

La résolution utilise un opérateur `$or` pour chercher par les deux champs.

---

## 🚀 Utilisation dans l'application

### Backend (Python/FastAPI)

```python
from awana_auth.services.iam_unified_service import IAMUnifiedService

# Vérifier les permissions d'un utilisateur
service = IAMUnifiedService(db)
permissions = await service.get_user_all_permissions(user_id)

# Vérifier une permission spécifique
has_access = await service.user_has_permission(user_id, "missions.browse")
```

### Frontend (React/TypeScript)

```typescript
import { usePermission } from '@/hooks/usePermission'

// Dans un composant
function MissionsPage() {
  const { hasPermission, isLoading } = usePermission('missions.browse')
  
  if (!hasPermission) {
    return <Navigate to="/" />
  }
  
  return <div>Liste des missions...</div>
}
```

### Protéger une route

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

### API REST

```bash
# Récupérer les permissions d'un utilisateur
GET /api/iam/unified/users/{userId}/permissions

# Vérifier une permission
POST /api/iam/check-permission
{
  "user_id": "...",
  "permission_code": "missions.browse"
}
```

---

## 📝 Notes de développement

### Ajouter une nouvelle permission

1. Insérer dans MongoDB :
```javascript
db.permissions.insertOne({
  "id": "uuid-generated",
  "code": "ma_nouvelle_permission",
  "description": "Description claire",
  "category": "missions",
  "is_system": true,
  "created_at": new Date(),
  "updated_at": new Date()
})
```

2. Ajouter au profil approprié :
```javascript
db.profiles.updateOne(
  { code: "interim_user" },
  { $push: { permission_ids: "ma_nouvelle_permission" } }
)
```

3. Utiliser dans le frontend :
```typescript
const { hasPermission } = usePermission('ma_nouvelle_permission')
```

### Créer un nouveau profil

```javascript
db.profiles.insertOne({
  "id": "profile_custom",
  "code": "custom_user",
  "name": "Utilisateur Custom",
  "description": "Description du profil",
  "permission_ids": [
    "missions.browse",
    "applications.create",
    "profile.manage_own"
  ],
  "is_system": false,
  "is_active": true,
  "priority": 300,
  "category": "user",
  "created_at": new Date(),
  "updated_at": new Date()
})
```

---

## 🔒 Sécurité

**Bonnes pratiques :**

1. ✅ Toujours utiliser les permissions IAM (pas les rôles legacy)
2. ✅ Principe du moindre privilège (donner le minimum nécessaire)
3. ✅ Vérifier les permissions côté backend ET frontend
4. ✅ Utiliser des scopes (`own`, `global`, `organization`)
5. ✅ Auditer les changements de permissions

**À éviter :**

1. ❌ Hardcoder des vérifications de rôles (`if user.role == "admin"`)
2. ❌ Se fier uniquement au frontend pour la sécurité
3. ❌ Créer des permissions trop larges (`*.*`)
4. ❌ Mélanger rôles legacy et permissions IAM

---

## 📞 Support

Pour toute question sur le système RBAC :
- 📧 Consulter la documentation principale : `AWANA_RBAC_DOCUMENTATION.md`
- 🔍 Inspecter les exports JSON pour les détails techniques
- 🛠️ Utiliser les hooks frontend et services backend fournis

---

**Dernière mise à jour :** 17 novembre 2025  
**Version :** 1.0
