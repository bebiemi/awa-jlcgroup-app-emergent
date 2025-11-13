# 🔧 Guide de Débogage - Connexion Docker Local

Ce guide vous aidera à résoudre le problème de connexion sur votre environnement Docker local.

## 🎯 Problème

La connexion échoue avec le message "Incorrect username or password" malgré des credentials valides.

**Credentials de test:**
- Username: `adminbe`
- Password: `Awana2025!`

## 📋 Scripts de Diagnostic

### 1. **Diagnostic Complet et Correction Automatique** (RECOMMANDÉ)

Ce script vérifie et corrige automatiquement tous les problèmes potentiels :

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/diagnose_and_fix_login.py
```

**Ce script vérifie et corrige :**
- ✅ Le champ `provider` (doit être `local`)
- ✅ Le champ `status` (doit être `active`)
- ✅ Le champ `is_active` (doit être `True`)
- ✅ Le champ `is_verified` (doit être `True`)
- ✅ Le nom du champ de mot de passe (`password_hash` vs `hashed_password`)
- ✅ La validité du hash du mot de passe
- ✅ Régénère le hash si nécessaire

### 2. **Test Détaillé Sans Modification**

Pour vérifier l'état actuel sans apporter de modifications :

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/test_login_detailed.py
```

### 3. **Vérification de Base**

Pour voir rapidement le document utilisateur :

```bash
docker exec jlc-auth-dev python /app/auth-microservice/scripts/check_adminbe_user.py
```

## 🔍 Analyse du Code

### Problème Identifié

En examinant `/app/auth-microservice/awana_auth_routes.py` (ligne 804), le code recherche spécifiquement `password_hash` :

```python
if user_doc and user_doc.get("password_hash"):
    # ...
    password_valid = bcrypt.checkpw(
        login_data.password.encode('utf-8'),
        user_doc["password_hash"].encode('utf-8')
    )
```

**Problèmes potentiels :**
1. ❌ Le champ pourrait s'appeler `hashed_password` au lieu de `password_hash`
2. ❌ Le `status` pourrait ne pas être `active`
3. ❌ Le hash du mot de passe pourrait être corrompu
4. ❌ Le `provider` pourrait ne pas être `local`

## 🧪 Test de Connexion API

Après avoir exécuté le script de correction, testez la connexion :

```bash
# Depuis votre machine locale (remplacez localhost par votre host si nécessaire)
curl -X POST http://localhost:8001/auth-api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adminbe",
    "password": "Awana2025!"
  }'
```

**Ou depuis le conteneur :**

```bash
docker exec jlc-auth-dev curl -X POST http://jlc-api:8001/auth-api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "adminbe",
    "password": "Awana2025!"
  }'
```

## 📊 Vérifier les Logs Backend

Si la connexion échoue toujours, vérifiez les logs :

```bash
# Logs en temps réel
docker logs -f jlc-auth-dev

# Dernières 100 lignes
docker logs --tail 100 jlc-auth-dev
```

## 🔧 Correction Manuelle (si scripts ne fonctionnent pas)

Si les scripts automatiques échouent, vous pouvez corriger manuellement via MongoDB :

```bash
docker exec -it jlc-mongo mongosh
```

```javascript
use auth_db

// Vérifier l'utilisateur
db.users.findOne({username: "adminbe"})

// Corriger les champs
db.users.updateOne(
  {username: "adminbe"},
  {
    $set: {
      provider: "local",
      status: "active",
      is_active: true,
      is_verified: true
    }
  }
)

// Si le champ s'appelle hashed_password, le renommer
db.users.updateOne(
  {username: "adminbe"},
  {
    $rename: {"hashed_password": "password_hash"}
  }
)
```

## 🎯 Checklist de Vérification

Avant de tester la connexion, assurez-vous que :

- [ ] Le conteneur `jlc-auth-dev` est démarré
- [ ] Le conteneur `jlc-mongo` est démarré
- [ ] Le script `diagnose_and_fix_login.py` a été exécuté
- [ ] Tous les problèmes détectés ont été corrigés
- [ ] Les logs backend ne montrent pas d'erreurs de démarrage

## 📝 Problèmes Connus

### 1. Nom de Champ Incorrect

**Symptôme :** Le champ s'appelle `hashed_password` au lieu de `password_hash`

**Solution :** Le script `diagnose_and_fix_login.py` renomme automatiquement le champ

### 2. Status Incorrect

**Symptôme :** Le status est `pending` au lieu de `active`

**Solution :** Le script corrige automatiquement le status

### 3. Hash Corrompu

**Symptôme :** Le hash ne correspond pas au mot de passe

**Solution :** Le script régénère un nouveau hash valide

## 🆘 Besoin d'Aide Supplémentaire ?

Si le problème persiste après avoir exécuté tous les scripts :

1. **Capturez les logs complets :**
   ```bash
   docker logs jlc-auth-dev > auth_debug.log 2>&1
   ```

2. **Vérifiez le document utilisateur final :**
   ```bash
   docker exec jlc-auth-dev python /app/auth-microservice/scripts/check_adminbe_user.py > user_doc.txt
   ```

3. **Testez depuis Python directement :**
   ```bash
   docker exec jlc-auth-dev python /app/auth-microservice/scripts/test_login_detailed.py > test_results.txt
   ```

4. Partagez ces fichiers pour un diagnostic plus approfondi.

## ✅ Succès Attendu

Après correction, vous devriez voir :

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "...",
    "username": "adminbe",
    "email": "...",
    "status": "active"
  }
}
```

## 🔄 Prochaines Étapes

Une fois la connexion fonctionnelle :

1. ✅ Vérifier que tous les workflows de l'application fonctionnent
2. ✅ Résoudre le problème "Mixed Content" sur la page de configuration des pays
3. ✅ Finaliser le module "Missions"
4. ✅ Compléter les fonctionnalités en attente

---

**Dernière mise à jour :** 2025-01-XX
**Créé par :** Agent E1 (Fork)
