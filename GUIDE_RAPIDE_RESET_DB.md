# 🚀 Guide Rapide - Réinitialisation DB Locale

## 📦 Informations Critiques

### Bases de Données
- **`auth_db`** : Authentification et IAM ← **C'est celle-ci qui est réinitialisée**
- **`jlc_db`** : Application principale (données métier)

### Identifiants SuperAdmin
- **Email** : `adminbe@awana-group.com`
- **Username** : `adminbe`
- **Password** : `Awana2025!`

## ⚡ Commande Rapide

```bash
cd /chemin/vers/votre/projet/scripts
python3 reset_local_db_with_superadmin.py
```

## ✅ Ce qui sera fait

1. ✨ Nettoyage de toutes les permissions invalides (format `:` ou `_`)
2. ✨ Création de 138 permissions modernes (format `resource.action.scope`)
3. ✨ Création du profil `super_admin` avec toutes les permissions
4. ✨ Création/Réinitialisation du compte `adminbe` avec tous les droits

## 🔍 Vérification Rapide

Après exécution, testez votre connexion :

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"adminbe","password":"Awana2025!"}'
```

Si vous obtenez un `access_token`, c'est parfait ! ✅

## 📚 Documentation Complète

Pour plus de détails, consultez :
- `/app/scripts/README_RESET_DB.md` - Documentation technique
- `/app/INSTRUCTIONS_RESET_DB_LOCAL.md` - Instructions complètes

## ⚠️ Options Avancées

### Supprimer TOUS les utilisateurs
```bash
python3 reset_local_db_with_superadmin.py --delete-users
```
⚠️ Cette commande supprime tous les comptes utilisateurs (vous devrez confirmer en tapant `OUI`)

---

**Après l'exécution**, n'oubliez pas de redémarrer votre backend local ! 🔄
