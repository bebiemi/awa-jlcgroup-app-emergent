# 🔄 Script de Réinitialisation de la Base de Données IAM

## 📋 Description

Ce script permet de réinitialiser complètement votre base de données locale IAM avec :
- ✅ Nettoyage de toutes les permissions invalides
- ✅ Création de toutes les permissions modernes (format `resource.action.scope`)
- ✅ Création du profil SuperAdmin avec tous les droits
- ✅ Création/Réinitialisation du compte superAdmin
- ✅ Option pour supprimer les utilisateurs de test

## 🚀 Utilisation

### Option 1 : Réinitialisation SANS suppression des utilisateurs

Cette option garde vos utilisateurs existants et ne fait que nettoyer/recréer les permissions et le superAdmin :

```bash
cd /app/scripts
python3 reset_local_db_with_superadmin.py
```

### Option 2 : Réinitialisation COMPLÈTE avec suppression des utilisateurs

Cette option supprime TOUS les utilisateurs (y compris les comptes de test) :

```bash
cd /app/scripts
python3 reset_local_db_with_superadmin.py --delete-users
```

⚠️ **ATTENTION** : Cette option supprime tous les utilisateurs ! Vous devrez taper `OUI` pour confirmer.

## 📝 Ce que fait le script

### 1. Nettoyage des permissions
- Supprime toutes les permissions existantes (y compris celles avec format invalide `:` ou `_`)

### 2. Création des permissions modernes
- Crée **toutes** les permissions IAM au format moderne
- Total : ~150+ permissions couvrant :
  - Missions (browse, read, create, edit, delete avec scopes .all/.own)
  - Besoins (view, create, edit, delete, submit, validate, convert)
  - Applications, Profils, Entreprises
  - Documents, Users, Config, Forms
  - IAM, RBAC, Validations
  - Emails, Security, Dashboard
  - Permission wildcard `*.*` pour SuperAdmin

### 3. Index unique
- Crée un index unique sur le champ `code` pour garantir l'intégrité

### 4. Profil SuperAdmin
- Code : `super_admin`
- Contient **toutes** les permissions créées
- Protégé et système (is_protected: true, is_system_role: true)
- Priorité maximale : 1000

### 5. Compte SuperAdmin
- **Email** : `admin@awana.fr`
- **Username** : `admin`
- **Password** : `Awana2025!`
- Profil : super_admin avec tous les droits

## ✅ Après l'exécution

Une fois le script exécuté avec succès, vous verrez :

```
================================================================================
✅ RÉINITIALISATION TERMINÉE AVEC SUCCÈS!
================================================================================

🔑 Identifiants SuperAdmin:
   Email: adminbe@awana-group.com
   Username: adminbe
   Password: Awana2025!
```

Vous pouvez maintenant :
1. Redémarrer votre backend : `sudo supervisorctl restart backend`
2. Vous connecter avec le compte superAdmin
3. L'erreur 500 sur `/api/iam/permissions` devrait être résolue

## 🔍 Vérification

Pour vérifier que tout fonctionne :

```bash
# Compter les permissions
mongo awana --eval "db.permissions.countDocuments({})"

# Vérifier le profil super_admin
mongo awana --eval "db.profiles.findOne({code: 'super_admin'})"

# Vérifier le compte admin
mongo awana --eval "db.users.findOne({username: 'admin'})"
```

## 🆘 En cas de problème

Si vous rencontrez des erreurs :

1. **Erreur de connexion MongoDB** : Vérifiez que MongoDB est bien démarré
   ```bash
   sudo systemctl status mongod
   ```

2. **Erreur de permissions** : Assurez-vous d'avoir les droits d'écriture sur la DB

3. **Import échoué** : Vérifiez que le chemin vers `auth-microservice` est correct

## 📦 Dépendances requises

Le script nécessite :
- `motor` (MongoDB async driver)
- `passlib[bcrypt]` (pour le hashing des mots de passe)

Normalement déjà installées dans votre environnement backend.
