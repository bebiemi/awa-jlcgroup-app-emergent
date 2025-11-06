# 🔐 Guide de Création du Super Admin

## Méthode 1: Script Python Interactif (Recommandé)

### Installation Locale (sans Docker)

```bash
# 1. Aller dans le dossier auth-microservice
cd auth-microservice

# 2. Activer l'environnement virtuel (si nécessaire)
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances si nécessaire
pip install motor passlib python-dotenv bcrypt

# 4. Exécuter le script
python scripts/create_super_admin_fresh.py
```

### Avec Docker

```bash
# Option A: Via docker-compose
cd docker
docker-compose exec auth-microservice python scripts/create_super_admin_fresh.py

# Option B: Via docker run
docker run -it --rm \
  --network jlc-network \
  -e MONGO_URL=mongodb://mongodb:27017 \
  -e DATABASE_NAME=auth_db \
  jlc-auth-prod python scripts/create_super_admin_fresh.py
```

---

## Méthode 2: Script Bash Rapide

### Créer un script bash

```bash
# Créer le fichier
cat > create-admin.sh << 'EOF'
#!/bin/bash
cd auth-microservice
python scripts/create_super_admin_fresh.py
EOF

# Rendre exécutable
chmod +x create-admin.sh

# Exécuter
./create-admin.sh
```

---

## Méthode 3: Directement via MongoDB (Avancé)

### Étape 1: Générer le hash du mot de passe

```python
# Dans un terminal Python
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "VotreMotDePasse123!"
hashed = pwd_context.hash(password)
print(f"Hashed password: {hashed}")
user_id = str(uuid.uuid4())
print(f"User ID: {user_id}")
```

### Étape 2: Insérer dans MongoDB

```javascript
// Dans mongosh ou MongoDB Compass
use auth_db

db.users.insertOne({
  "id": "VOTRE_UUID_ICI",
  "username": "admin",
  "email": "admin@jlc.com",
  "full_name": "Super Admin",
  "hashed_password": "VOTRE_HASH_ICI",
  "roles": ["super_admin"],
  "is_active": true,
  "is_verified": true,
  "phone_number": null,
  "avatar_url": null,
  "metadata": {
    "created_via": "manual",
    "created_by": "system"
  },
  "created_at": new Date().toISOString(),
  "updated_at": new Date().toISOString()
})
```

---

## Méthode 4: Via l'API (Après premier admin créé)

### Prérequis: Avoir un token admin valide

```bash
# 1. Se connecter en tant qu'admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"VotreMotDePasse"}' \
  | jq -r '.access_token')

# 2. Créer un nouvel utilisateur avec rôle super_admin
curl -X POST http://localhost:8000/api/auth/security/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "superadmin2",
    "email": "admin2@jlc.com",
    "full_name": "Super Admin 2",
    "password": "SecurePassword123!",
    "roles": ["super_admin"]
  }'
```

---

## Vérification

### Vérifier que le super admin existe

```bash
# Méthode 1: Via le script Python
cd auth-microservice
python scripts/create_super_admin_fresh.py
# Choisir l'option 2 pour lister

# Méthode 2: Via MongoDB
mongosh auth_db --eval "db.users.find({roles: 'super_admin'}).pretty()"

# Méthode 3: Via MongoDB Compass
# Ouvrir MongoDB Compass
# Se connecter à mongodb://localhost:27017
# Aller dans auth_db > users
# Filtrer: { "roles": "super_admin" }
```

### Test de connexion

```bash
# Via curl
curl -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "VotreMotDePasse"
  }'

# Via le frontend
# Ouvrir http://localhost:3000 (ou 5173)
# Entrer les identifiants
```

---

## Identifiants par Défaut (Développement)

⚠️ **ATTENTION**: Ces identifiants sont pour le développement UNIQUEMENT

```
Username: admin
Password: awana2025
Email: admin@jlc.com
```

🔒 **Pour la Production**:
- Utilisez des mots de passe forts (minimum 16 caractères)
- Activez l'authentification à deux facteurs si disponible
- Changez immédiatement les mots de passe par défaut
- Utilisez un gestionnaire de mots de passe

---

## Rôles et Permissions

### Hiérarchie des rôles

```
super_admin (Accès total)
  ├─ admin (Gestion utilisateurs)
  ├─ company (Gestion entreprise)
  ├─ agency (Gestion agence)
  ├─ collaborator (Collaborateur)
  └─ interim (Intérimaire)
```

### Permissions super_admin

- ✅ Gestion complète des utilisateurs
- ✅ Gestion des rôles et permissions
- ✅ Accès à toutes les fonctionnalités
- ✅ Configuration système
- ✅ Accès aux logs et audits
- ✅ Gestion des feature flags
- ✅ Gestion des configurations
- ✅ Backup et restauration

---

## Dépannage

### Erreur: "MongoDB connection refused"

```bash
# Vérifier que MongoDB tourne
sudo systemctl status mongodb
# ou avec Docker
docker-compose ps mongodb

# Démarrer MongoDB si nécessaire
sudo systemctl start mongodb
# ou
docker-compose up -d mongodb
```

### Erreur: "Database not found"

```bash
# La base de données sera créée automatiquement
# Vérifier la variable d'environnement
echo $MONGO_URL
echo $DATABASE_NAME

# Ou dans .env
cat auth-microservice/.env
```

### Erreur: "User already exists"

```bash
# Lister les utilisateurs existants
mongosh auth_db --eval "db.users.find({}, {username:1, email:1, roles:1}).pretty()"

# Supprimer un utilisateur si nécessaire
mongosh auth_db --eval "db.users.deleteOne({username: 'admin'})"

# Ou utiliser le script pour promouvoir l'utilisateur existant
python scripts/create_super_admin_fresh.py
# Choisir l'option d'ajout du rôle
```

### Mot de passe oublié

```bash
# Réinitialiser le mot de passe d'un utilisateur
python << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.auth_db
    
    new_password = "NouveauMotDePasse123!"
    hashed = pwd_context.hash(new_password)
    
    result = await db.users.update_one(
        {"username": "admin"},
        {"$set": {"hashed_password": hashed}}
    )
    
    print(f"Mot de passe réinitialisé: {result.modified_count} utilisateur(s)")
    client.close()

asyncio.run(reset_password())
EOF
```

---

## Sécurité

### Bonnes Pratiques

1. **Mots de passe forts**
   - Minimum 16 caractères
   - Majuscules, minuscules, chiffres, symboles
   - Utiliser un générateur de mots de passe

2. **Rotation des mots de passe**
   - Changer tous les 90 jours
   - Ne jamais réutiliser d'anciens mots de passe

3. **Limitation des super admins**
   - Créer le minimum nécessaire
   - Utiliser des rôles moins privilégiés quand possible

4. **Audit et logs**
   - Activer les logs d'authentification
   - Surveiller les connexions super admin

5. **Environnements séparés**
   - Super admins différents pour dev/staging/prod
   - Ne jamais utiliser les identifiants de dev en prod

---

## Support

En cas de problème:
1. Consulter la section Dépannage ci-dessus
2. Vérifier les logs: `tail -f auth-microservice/logs/app.log`
3. Consulter la documentation: `/docs`
4. Contacter l'équipe technique

---

**Version**: 1.0.0  
**Dernière mise à jour**: Novembre 2025
