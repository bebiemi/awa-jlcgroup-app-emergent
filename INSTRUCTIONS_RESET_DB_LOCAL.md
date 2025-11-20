# 🚀 Instructions pour Réinitialiser votre Base de Données Locale

## ⚠️ Contexte

Votre environnement de développement local sur Mac rencontre une erreur 500 sur `GET /api/iam/permissions` à cause de données de permissions avec un format invalide (utilisant `:` au lieu de `.`) dans votre base MongoDB locale.

L'environnement de prévisualisation (Emergent) fonctionne correctement car il a déjà été nettoyé et migré.

## 🎯 Solution : Script de Réinitialisation

Un script complet a été créé pour résoudre ce problème en une seule commande.

### 📁 Emplacement du script

```
/app/scripts/reset_local_db_with_superadmin.py
/app/scripts/README_RESET_DB.md  (Documentation détaillée)
```

## 🔧 Étapes à Suivre sur VOTRE MAC

### 1️⃣ Assurez-vous que MongoDB est démarré

```bash
# Vérifier le statut de MongoDB
sudo systemctl status mongod

# Si MongoDB n'est pas démarré
sudo systemctl start mongod
```

### 2️⃣ Naviguez vers le dossier scripts

```bash
cd /chemin/vers/votre/projet/scripts
```

### 3️⃣ Exécutez le script de réinitialisation

**Option A : Sans supprimer les utilisateurs existants**
```bash
python3 reset_local_db_with_superadmin.py
```

**Option B : Avec suppression complète des utilisateurs (ATTENTION)**
```bash
python3 reset_local_db_with_superadmin.py --delete-users
```

Le script va vous demander de taper `OUI` pour confirmer la suppression.

### 4️⃣ Redémarrez votre backend local

```bash
# Si vous utilisez supervisor
sudo supervisorctl restart backend

# Ou si vous lancez directement avec uvicorn
# Ctrl+C puis relancer votre commande de démarrage
```

### 5️⃣ Testez que tout fonctionne

```bash
# Tentez de vous connecter avec le compte superAdmin
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"adminbe","password":"Awana2025!"}'

# Si vous obtenez un token, testez l'endpoint permissions
TOKEN="<votre_token>"
curl http://localhost:8001/api/iam/permissions \
  -H "Authorization: Bearer $TOKEN"
```

Si vous obtenez une liste de permissions sans erreur 500, c'est gagné ! ✅

## 🔑 Identifiants SuperAdmin

Après l'exécution du script, vous pouvez vous connecter avec :

- **Email** : `adminbe@awana-group.com`
- **Username** : `adminbe`  
- **Password** : `Awana2025!`

Ce compte a **tous les droits** (138 permissions).

## 📊 Ce que le script fait

1. ✅ **Nettoie** toutes les permissions invalides (format `:` ou `_`)
2. ✅ **Crée** 138 permissions modernes au format `resource.action.scope`
3. ✅ **Crée** un profil SuperAdmin avec toutes les permissions
4. ✅ **Crée/Réinitialise** le compte `admin` avec le profil SuperAdmin
5. ✅ **Crée** un index unique sur le champ `code` pour éviter les doublons
6. ✅ **Optionnel** : Supprime tous les utilisateurs de test

## 🔍 Résultat Attendu

Après l'exécution, vous devriez voir :

```
================================================================================
✅ RÉINITIALISATION TERMINÉE AVEC SUCCÈS!
================================================================================

🔑 Identifiants SuperAdmin:
   Email: adminbe@awana-group.com
   Username: adminbe
   Password: Awana2025!
```

Et les statistiques :
- **Permissions** : 138
- **Profils** : 1 (super_admin)
- **Utilisateurs** : 1+ (selon si vous avez supprimé ou non)

## 🆘 Problèmes Possibles

### Erreur : "MongoDB connection refused"
**Solution** : MongoDB n'est pas démarré
```bash
sudo systemctl start mongod
```

### Erreur : "Module 'motor' not found"
**Solution** : Installer les dépendances
```bash
pip install motor passlib[bcrypt]
```

### Erreur : "Permission denied"
**Solution** : Vous n'avez pas les droits sur la base MongoDB. Vérifiez la configuration de votre MongoDB local.

### Le script s'exécute mais l'erreur 500 persiste
**Solution** : 
1. Vérifiez que vous utilisez bien la même base de données (par défaut : `awana`)
2. Vérifiez votre variable d'environnement `MONGO_URL` dans `.env`
3. Redémarrez complètement votre backend

## 📞 Questions ?

Si vous rencontrez des problèmes :
1. Vérifiez que MongoDB est bien démarré
2. Vérifiez les logs du script pour voir à quelle étape il échoue
3. Vérifiez que votre backend pointe bien vers la bonne base MongoDB

## ⏭️ Prochaines Étapes

Une fois votre environnement local réparé et aligné avec l'environnement de prévisualisation :

1. ✅ **Confirmer** que l'erreur 500 est résolue
2. ⏭️ **Continuer** avec la migration IAM complète (audit et remplacement de toutes les anciennes constantes)
3. ⏭️ **Améliorer** l'UI de gestion des groupes
4. ⏭️ **Tester** l'ensemble du système IAM

---

**N'oubliez pas** : Ce script ne touche QUE votre environnement local. L'environnement de prévisualisation sur Emergent est déjà propre et fonctionnel ! 🎉
