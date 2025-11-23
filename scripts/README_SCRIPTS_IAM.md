# 📚 Scripts d'Initialisation IAM

## ✅ Script Principal (Recommandé)

### `init_db_unified.py` - Script Unifié d'Initialisation

**Script principal et recommandé** pour l'initialisation complète de la base de données IAM.

**Ce qu'il fait:**
- ✅ Crée 182 permissions atomiques
- ✅ Crée 6 bundles de permissions
- ✅ Crée/Met à jour 7 profils système avec permissions appropriées
- ✅ Crée le compte super_admin
- ✅ Corrige automatiquement les problèmes de champs (password → password_hash)
- ✅ Active les comptes super_admin

**Usage:**
```bash
# Initialisation standard
python3 init_db_unified.py

# Avec suppression des utilisateurs de test
python3 init_db_unified.py --delete-users
```

**Profils créés:**
| Code | Nom | Permissions | Bundles |
|------|-----|-------------|---------|
| `super_admin` | Super Administrateur | 182 (toutes) | - |
| `admin` | Administrateur | 31 | users.manage, missions.full_access, config.manage, admin.access, entreprises.manage |
| `commercial` | Commercial | 15 | missions.full_access, entreprises.manage |
| `company_admin` | Admin Société | 5 | - |
| `interim_user` | Intérimaire/Candidat | 9 | - |
| `hr_manager` | Responsable RH | 6 | - |
| `read_only` | Lecture Seule | 4 | - |

---

## 📦 Scripts Alternatifs/Legacy

### `reset_db_with_permissions_and_bundles.py`

**Statut:** ⚠️ Remplacé par `init_db_unified.py`

Script précédent qui créait permissions + bundles mais ne mettait pas à jour les profils système.

**Migration:** Utilisez `init_db_unified.py` à la place.

---

### `reset_local_db_with_160_permissions.py`

**Statut:** ⚠️ Obsolète (Permissions incomplètes)

Ancien script créant seulement 160 permissions (maintenant 182) sans les bundles ni les profils système.

**Migration:** Utilisez `init_db_unified.py` à la place.

---

### `reset_local_db_with_superadmin.py`

**Statut:** ⚠️ Obsolète

Très ancien script - ne pas utiliser.

**Migration:** Utilisez `init_db_unified.py` à la place.

---

## 🛠 Scripts Utilitaires

### `fix_user_password_field.py`

**Utilité:** Correction des champs utilisateurs

**Quand l'utiliser:**
- Si des utilisateurs ont `password` au lieu de `password_hash`
- Si des comptes super_admin sont inactifs
- Si le champ `provider` manque

**Usage:**
```bash
python3 fix_user_password_field.py
```

**Note:** Cette correction est déjà incluse dans `init_db_unified.py`.

---

## 🔄 Workflow Recommandé

### Pour une Nouvelle Installation

```bash
# 1. Exécuter le script unifié
cd /app/scripts
python3 init_db_unified.py

# 2. Vérifier en base de données
mongosh auth_db --eval 'db.profiles.find({is_system_role: true}, {code: 1, name: 1, permissions: 1})'

# 3. Tester la connexion
curl -X POST http://localhost:8001/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Awana2025!"}'
```

### Pour Mise à Jour des Profils Existants

```bash
# Le script detect automatiquement les profils existants et les met à jour
python3 init_db_unified.py
```

### Pour Réinitialisation Complète (DEV seulement)

```bash
# ⚠️ Supprime tous les utilisateurs sauf admin
python3 init_db_unified.py --delete-users
```

---

## 📊 Comparaison des Scripts

| Fonctionnalité | init_db_unified.py | reset_db_with_permissions_and_bundles.py | reset_local_db_with_160_permissions.py |
|----------------|-------------------|------------------------------------------|---------------------------------------|
| Permissions atomiques | ✅ 182 | ✅ 182 | ⚠️ 160 |
| Bundles | ✅ 6 | ✅ 6 | ❌ |
| Profils système | ✅ 7 | ⚠️ 1 (super_admin) | ⚠️ 1 (super_admin) |
| Correction auto users | ✅ | ❌ | ❌ |
| Activation auto admin | ✅ | ❌ | ❌ |
| Bundles dans profils | ✅ | ❌ | ❌ |

---

## 🔍 Vérification Post-Installation

```bash
# Vérifier les permissions
mongosh auth_db --eval 'db.permissions.countDocuments({})'
# Attendu: 182

# Vérifier les bundles
mongosh auth_db --eval 'db.permission_bundles.countDocuments({})'
# Attendu: 6

# Vérifier les profils
mongosh auth_db --eval 'db.profiles.countDocuments({is_system_role: true})'
# Attendu: 7 ou plus

# Vérifier le compte admin
mongosh auth_db --eval 'db.users.findOne({username: "admin"}, {username: 1, status: 1, password_hash: 1})'
# Attendu: status = "active", password_hash existe
```

---

## 📝 Notes Importantes

1. **Toujours utiliser `init_db_unified.py`** pour les nouvelles installations
2. Les anciens scripts sont conservés pour référence mais ne doivent plus être utilisés
3. Le script unifié est **idempotent** : il peut être exécuté plusieurs fois sans problème
4. Les profils existants sont mis à jour, pas supprimés
5. Les utilisateurs existants sont préservés (sauf avec `--delete-users`)

---

## 🐛 Dépannage

### Erreur: "password_hash not found"
**Solution:** Exécutez `init_db_unified.py` ou `fix_user_password_field.py`

### Profils sans permissions
**Solution:** Exécutez `init_db_unified.py` pour mettre à jour les profils

### Connexion échoue avec 401
**Solution:** 
1. Vérifiez que le compte existe et est actif
2. Exécutez `init_db_unified.py` pour corriger

---

**Dernière mise à jour:** 23 Novembre 2025  
**Version du système:** 2.0 (Unified)
