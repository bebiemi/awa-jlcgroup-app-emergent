# 🚀 Démarrage Rapide - Application JLC

## 📋 Situation Actuelle

Vous avez créé le super utilisateur `adminbe` mais l'interface IAM retourne une erreur 500 car les collections MongoDB ne sont pas encore initialisées.

## ⚡ Solution en 2 Commandes

### 1️⃣ Initialiser la base de données complète

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/complete_database_initialization.py
```

**Ce script crée :**
- ✅ 30+ permissions système
- ✅ 5 profils utilisateurs (super_admin, admin, company, interim, candidat)
- ✅ 12+ permissions IAM
- ✅ 4 profils IAM
- ✅ 4 groupes IAM
- ✅ 14 références système
- ✅ 12 collections MongoDB

**Durée :** ~10 secondes

### 2️⃣ Vérifier que tout fonctionne

```bash
# Test de connexion
curl -X POST http://localhost:8001/auth-api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adminbe",
    "password": "Awana2025!"
  }'
```

**Résultat attendu :** Un token JWT

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "...",
    "username": "adminbe",
    "email": "adminbe@awana-group.com",
    "roles": ["super_admin"]
  }
}
```

## 🎯 Accès à l'Application

1. **Frontend :** http://localhost:3000
2. **Backend API :** http://localhost:8001/auth-api
3. **Interface IAM :** http://localhost:3000/admin/iam (après connexion)

**Credentials :**
- Username: `adminbe`
- Password: `Awana2025!`

## 📊 Vérifier l'État de la Base de Données

```bash
# Se connecter à MongoDB
docker exec -it jlc-mongo mongosh

# Dans mongosh
use auth_db
show collections

# Vérifier les documents
db.permissions.countDocuments()
db.iam_permissions.countDocuments()
db.iam_profiles.countDocuments()
db.iam_groups.countDocuments()
```

## 🔧 Si Problèmes Persistent

### Erreur de connexion "Incorrect username or password"

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/diagnose_and_fix_login.py
```

### Erreur 500 sur IAM malgré l'initialisation

```bash
# Vérifier les logs
docker logs jlc-auth-dev --tail 50

# Redémarrer le backend
docker restart jlc-auth-dev
```

### Backend ne démarre pas

```bash
# Vérifier la connexion MongoDB
docker exec jlc-auth-dev python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
async def test():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    info = await client.server_info()
    print('✅ MongoDB connected:', info['version'])
asyncio.run(test())
"
```

## 📚 Documentation Complète

- **Guide complet :** `/app/DOCS_INITIALIZATION_ET_DEBUG.md`
- **Scripts de diagnostic :** `/app/auth-microservice/scripts/README_DOCKER_DEBUG.md`
- **Code source :** `/app/auth-microservice/`

## 🆘 Checklist de Vérification

- [ ] MongoDB démarré : `docker ps | grep mongo`
- [ ] Backend démarré : `docker ps | grep auth`
- [ ] Initialisation exécutée : Script `complete_database_initialization.py`
- [ ] Collections créées : `show collections` dans mongosh
- [ ] Connexion testée : curl avec credentials
- [ ] Interface IAM accessible : http://localhost:3000/admin/iam

## 🎉 Prochaines Étapes

Une fois l'initialisation terminée :

1. ✅ Connectez-vous à l'interface web
2. ✅ Vérifiez l'accès à la page IAM
3. ✅ Créez vos premiers utilisateurs/groupes
4. ✅ Configurez les permissions selon vos besoins

---

**Besoin d'aide ?** Consultez `/app/DOCS_INITIALIZATION_ET_DEBUG.md` pour un guide détaillé.
