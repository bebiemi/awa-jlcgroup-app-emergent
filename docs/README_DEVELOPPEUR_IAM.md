# 🛠️ Guide Développeur IAM

**Version :** 2.0  
**Date :** 19 Janvier 2025  
**Public :** Développeurs, DevOps

---

## 📚 Documentation Disponible

### Pour Développeurs
- **Ce fichier** - Guide technique complet
- `/app/docs/FAQ_IAM_COMPLETE.md` - FAQ technique détaillée
- `/app/docs/AGENCY_COUNTRY_PROFILE_OPERATIONS.md` - Exploitation du profil agence multi-pays
- `/app/auth-microservice/tests/test_iam_service.py` - Tests unitaires

### Pour Utilisateurs
- `/app/docs/GUIDE_UTILISATEUR_IAM.md` - Documentation utilisateur complète

### Rapports d'Audit
- `/app/docs/IAM_COMPLETE_CLEANUP_REPORT.md` - Nettoyage P0
- `/app/docs/ANALYSE_PROFIL_ENTREPRISE.md` - Diagnostic entreprise
- `/app/docs/P1_CACHE_BUG_FIX.md` - Fix cache RTK Query

---

## 🏗️ Architecture IAM

### Structure des Composants

```
Backend (Python/FastAPI)
├── awana_auth/services/iam_service.py        # Service principal IAM
├── awana_auth/core/iam_models.py             # Modèles Pydantic
├── iam_routes.py                             # Endpoints API IAM
├── iam_bundles_routes.py                     # Endpoints bundles
└── tests/test_iam_service.py                 # Tests unitaires

Frontend (React/TypeScript)
├── features/iam/api/
│   ├── iamApi.ts                             # API client profils/permissions
│   └── bundlesApi.ts                         # API client bundles
├── features/iam/pages/
│   ├── ProfilesManagementPage.tsx            # Gestion profils
│   ├── IAMAdminDashboard.tsx                 # Dashboard admin (NEW)
│   └── ...
└── features/iam/components/                  # Composants UI

Database (MongoDB)
├── users                                     # Utilisateurs
├── profiles                                  # Profils IAM
├── capability_bundles                        # Bundles de capacités
├── permissions                               # Permissions
└── groups                                    # Groupes
```

---

## 🚀 Quick Start

### 1. Exécuter les Tests

```bash
# Méthode 1: Script automatique
cd /app/auth-microservice
./run_tests.sh

# Méthode 2: Pytest direct
cd /app/auth-microservice
pytest tests/test_iam_service.py -v

# Test spécifique
pytest tests/test_iam_service.py::test_get_user_permissions_with_bundles -v
```

### 2. Tester le Service IAM

```python
# Script Python pour tester manuellement
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

sys.path.append('/app/auth-microservice')
from awana_auth.services.iam_service import IAMService

async def test_iam():
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    iam = IAMService(db)
    
    # Test avec un utilisateur
    perms = await iam.get_user_permissions("user_id_here")
    print(f"Permissions: {len(perms.all_permissions)}")
    
    for perm in perms.all_permissions[:10]:
        print(f"  - {perm.code}")
    
    client.close()

asyncio.run(test_iam())
```

### 3. Accéder à l'Interface Admin

```
URL: http://localhost:3000/iam/admin
Route: /features/iam/pages/IAMAdminDashboard.tsx
```

---

## 🔧 Développement

### Ajouter une Nouvelle Permission

**Backend** (`permissions` collection):

```python
new_permission = {
    "id": f"perm_{uuid4()}",
    "code": "resource.action.scope",
    "name": "Nom de la Permission",
    "description": "Description détaillée",
    "resource": "resource",
    "action": "action",
    "scope": "own",  # ou "all" ou None
    "category": "category_name",
    "created_at": datetime.now(timezone.utc)
}

await db.permissions.insert_one(new_permission)
```

**Format Obligatoire :**
```
resource.action[.scope]

Exemples valides:
✅ missions.create.own
✅ users.manage.all
✅ documents.view

Invalides:
❌ create_mission (legacy)
❌ see_users (legacy)
```

### Créer un Nouveau Bundle

```python
new_bundle = {
    "id": f"bundle_{uuid4()}",
    "code": "feature_bundle_name",
    "name": "Nom du Bundle",
    "description": "Description du bundle",
    "category": "business",  # ou "system", "admin"
    "permission_ids": [
        "perm_id_1",
        "perm_id_2",
        "perm_id_3"
    ],
    "tags": ["feature", "business"],
    "is_system": False,
    "created_at": datetime.now(timezone.utc)
}

await db.capability_bundles.insert_one(new_bundle)
```

### Créer un Nouveau Profil

```python
new_profile = {
    "id": f"profile_{uuid4()}",
    "code": "business_profile_code",
    "name": "Nom du Profil",
    "description": "Description du profil métier",
    "category": "business",
    "permission_ids": [],  # Permissions directes (optionnel)
    "capability_bundle_ids": [  # Bundles (recommandé)
        "bundle_id_1",
        "bundle_id_2"
    ],
    "is_protected": False,  # True = ne peut pas être supprimé
    "is_system_role": False,
    "created_at": datetime.now(timezone.utc)
}

await db.profiles.insert_one(new_profile)
```

---

## 🧪 Tests

### Structure des Tests

```python
# tests/test_iam_service.py

@pytest.fixture
async def db():
    """Fixture DB de test"""
    # Setup
    yield db
    # Cleanup

@pytest.mark.asyncio
async def test_feature(iam_service, sample_data):
    """Test d'une fonctionnalité"""
    # Arrange
    # Act
    result = await iam_service.method()
    # Assert
    assert result == expected
```

### Tests Disponibles

| Test | Couverture |
|------|-----------|
| `test_iam_service_initialization` | Initialisation |
| `test_get_user_permissions_basic` | Chargement permissions |
| `test_get_user_permissions_with_bundles` | **Bundles chargés** ✅ |
| `test_user_has_permission_granted` | Vérification permissions |
| `test_super_admin_bypass` | Super admin bypass |
| `test_multiple_profiles_union` | Union profils |
| `test_performance_many_permissions` | Performance |
| Et 12+ autres tests... | Full coverage |

### Ajouter un Nouveau Test

```python
@pytest.mark.asyncio
async def test_ma_nouvelle_fonctionnalite(iam_service, db):
    """Test de ma nouvelle fonctionnalité"""
    # Préparer les données
    user = {
        "id": "test_user",
        "profile_ids": ["test_profile"]
    }
    await db.users.insert_one(user)
    
    # Exécuter le test
    result = await iam_service.nouvelle_methode(user["id"])
    
    # Vérifier
    assert result.success is True
    assert len(result.data) > 0
```

---

## 🔌 API Endpoints

### Profils

```
GET    /api/iam/profiles                    # Liste tous les profils
GET    /api/iam/profiles/{profile_id}       # Détails d'un profil
POST   /api/iam/profiles                    # Créer un profil
PUT    /api/iam/profiles/{profile_id}       # Modifier un profil
DELETE /api/iam/profiles/{profile_id}       # Supprimer un profil
```

### Permissions

```
GET    /api/iam/permissions                 # Liste toutes les permissions
GET    /api/iam/permissions/{perm_id}       # Détails d'une permission
POST   /api/iam/permissions                 # Créer une permission
PUT    /api/iam/permissions/{perm_id}       # Modifier une permission
DELETE /api/iam/permissions/{perm_id}       # Supprimer une permission
```

### Bundles

```
GET    /api/iam/bundles                     # Liste tous les bundles
GET    /api/iam/bundles/{bundle_id}         # Détails d'un bundle
POST   /api/iam/bundles                     # Créer un bundle
PUT    /api/iam/bundles/{bundle_id}         # Modifier un bundle
DELETE /api/iam/bundles/{bundle_id}         # Supprimer un bundle
```

### Utilisateurs

```
GET    /api/iam/users/{user_id}/permissions    # Permissions d'un utilisateur
POST   /api/iam/users/{user_id}/profiles       # Assigner profils
POST   /api/iam/users/{user_id}/groups         # Assigner groupes
```

---

## 🎨 Frontend

### Utiliser les Hooks IAM

```typescript
import { 
  useListProfilesQuery, 
  useListPermissionsQuery,
  useUpdateProfileMutation 
} from '@/features/iam/api/iamApi';

import { useBundlesQuery } from '@/features/iam/api/bundlesApi';

function MyComponent() {
  // Charger les données
  const { data: profiles, isLoading } = useListProfilesQuery();
  const { data: permissions } = useListPermissionsQuery();
  const { data: bundles } = useBundlesQuery();
  
  // Mutations
  const [updateProfile] = useUpdateProfileMutation();
  
  const handleUpdate = async (profileId, data) => {
    try {
      await updateProfile({ id: profileId, data }).unwrap();
      toast.success('Profil mis à jour');
    } catch (error) {
      toast.error('Erreur');
    }
  };
  
  return <div>...</div>;
}
```

### Vérifier les Permissions Utilisateur

```typescript
import { useAppSelector } from '@/store/hooks';

function ProtectedComponent() {
  const permissions = useAppSelector((state) => state.auth.permissions);
  
  const canEdit = permissions.includes('missions.edit.own');
  const canDelete = permissions.includes('missions.delete.all');
  
  return (
    <div>
      {canEdit && <EditButton />}
      {canDelete && <DeleteButton />}
    </div>
  );
}
```

### Composant Conditionnel

```typescript
import { usePermission } from '@/hooks/usePermission';

function ConditionalFeature() {
  const hasPermission = usePermission('missions.create');
  
  if (!hasPermission) {
    return <div>Accès refusé</div>;
  }
  
  return <CreateMissionForm />;
}
```

---

## 🐛 Debugging

### Logs Backend

```bash
# Logs IAM Service
tail -f /var/log/supervisor/auth-microservice.out.log | grep IAM

# Logs d'erreur
tail -f /var/log/supervisor/auth-microservice.err.log
```

### Debug Permissions Utilisateur

```python
# Script de debug
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

sys.path.append('/app/auth-microservice')
from awana_auth.services.iam_service import IAMService

async def debug_user_permissions(username):
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # Trouver l'utilisateur
    user = await db.users.find_one({"username": username})
    if not user:
        print(f"❌ Utilisateur {username} non trouvé")
        return
    
    print(f"✅ Utilisateur: {user['username']}")
    print(f"   Profile IDs: {user.get('profile_ids', [])}")
    print(f"   Group IDs: {user.get('group_ids', [])}")
    
    # Charger les permissions
    iam = IAMService(db)
    perms_response = await iam.get_user_permissions(user['id'])
    
    print(f"\n📋 Permissions totales: {len(perms_response.all_permissions)}")
    
    # Grouper par resource
    from collections import defaultdict
    by_resource = defaultdict(list)
    for perm in perms_response.all_permissions:
        by_resource[perm.resource].append(perm.code)
    
    print(f"\n📊 Par ressource:")
    for resource, codes in sorted(by_resource.items()):
        print(f"   {resource}: {len(codes)} permissions")
        for code in codes[:3]:
            print(f"      • {code}")
        if len(codes) > 3:
            print(f"      ... et {len(codes) - 3} autres")
    
    client.close()

# Usage
asyncio.run(debug_user_permissions("mbj"))
```

### Debug Cache Frontend

```typescript
// Dans Redux DevTools
// Inspecter l'état
state.auth.permissions  // Liste des permissions
state.iamApi.queries    // Cache des queries IAM
state.bundlesApi.queries // Cache des bundles

// Forcer le rechargement
dispatch(iamApi.util.invalidateTags(['Profiles']));
```

---

## 📊 Monitoring

### Métriques à Surveiller

```bash
# Nombre de permissions par utilisateur (moyenne)
db.users.aggregate([
  {$lookup: {from: "profiles", localField: "profile_ids", foreignField: "id", as: "profiles"}},
  {$project: {username: 1, perm_count: {$size: "$profiles.permission_ids"}}}
])

# Profils vides
db.profiles.find({
  permission_ids: {$size: 0},
  capability_bundle_ids: {$size: 0}
})

# Bundles non utilisés
db.capability_bundles.find({
  id: {$nin: [...profile_bundle_ids]}
})
```

### Audit Automatique

```bash
# Exécuter l'audit complet
cd /app/scripts/iam_refonte
python 07_audit_complete_permissions.py

# Test d'intégrité
python 10_test_iam_integrity.py
```

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Principe du Moindre Privilège**
   ```
   ✅ Donner seulement ce qui est nécessaire
   ✅ Préférer .own à .all
   ❌ Ne pas donner *.all à tout le monde
   ```

2. **Validation Backend**
   ```python
   # Toujours vérifier les permissions côté backend
   @router.post("/missions")
   async def create_mission(
       data: MissionCreate,
       user = Depends(get_current_user),
       iam = Depends(get_iam_service)
   ):
       # Vérifier la permission
       check = await iam.user_has_permission(
           user['id'], 
           'missions.create'
       )
       
       if not check.has_permission:
           raise HTTPException(403, check.reason)
       
       # Créer la mission
       ...
   ```

3. **Profils Protégés**
   ```python
   # Ne jamais modifier les profils système
   if profile.is_protected:
       raise HTTPException(403, "Cannot modify protected profile")
   ```

---

## 🚀 Déploiement

### Checklist Pré-Déploiement

```bash
# 1. Exécuter tous les tests
cd /app/auth-microservice
./run_tests.sh

# 2. Audit IAM
cd /app/scripts/iam_refonte
python 10_test_iam_integrity.py

# 3. Vérifier les logs
tail -50 /var/log/supervisor/auth-microservice.err.log

# 4. Backup base de données
mongodump --uri="$MONGO_URL" --out=/backup/$(date +%Y%m%d)

# 5. Redémarrer les services
sudo supervisorctl restart auth-microservice
sudo supervisorctl restart frontend
```

### Rollback

```bash
# En cas de problème
sudo supervisorctl stop auth-microservice

# Restaurer le backup
mongorestore --uri="$MONGO_URL" /backup/20250119

# Redémarrer
sudo supervisorctl start auth-microservice
```

---

## 📞 Support

**Questions Techniques :** dev-team@awana.com  
**Bugs :** GitHub Issues  
**Urgence :** Hotline DevOps 24/7

---

## 📝 Changelog

### Version 2.0 (19 Janvier 2025)

**Nouveautés :**
- ✅ Tests unitaires complets (18 tests)
- ✅ Interface admin IAM dashboard
- ✅ Documentation utilisateur complète
- ✅ Support bundles dans IAMService
- ✅ API bundles complète

**Corrections :**
- ✅ Bug chargement bundles
- ✅ Cache RTK Query
- ✅ Format permissions moderne
- ✅ Références orphelines

### Version 1.0 (Décembre 2024)
- Version initiale

---

**Dernière mise à jour :** 19 Janvier 2025  
**Mainteneur :** Équipe Platform
