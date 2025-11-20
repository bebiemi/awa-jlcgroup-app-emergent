# 🔐 Guide de Correction du Mot de Passe adminbe

## ❌ Problème

Le script de réinitialisation a rencontré une erreur bcrypt lors du hachage du mot de passe, rendant le compte `adminbe` inaccessible avec l'erreur "incorrect username or password".

## ✅ Solution

Un script de correction spécifique a été créé pour corriger uniquement le mot de passe.

## 🚀 Exécution

### Option 1 : Depuis votre machine locale (Mac)

```bash
cd /chemin/vers/votre/projet/scripts
python3 fix_adminbe_password.py
```

### Option 2 : Depuis le conteneur Docker

```bash
docker-compose exec auth-microservice bash
cd /app/scripts
python3 fix_adminbe_password.py
exit
```

## ✨ Ce que fait le script

1. ✅ Trouve le compte `adminbe` dans la base `auth_db`
2. ✅ Hash le mot de passe `Awana2025!` avec bcrypt (méthode directe, plus fiable)
3. ✅ Met à jour le champ `hashed_password` du compte
4. ✅ Vérifie que le hash fonctionne correctement

## 📊 Résultat Attendu

```
================================================================================
✅ CORRECTION TERMINÉE AVEC SUCCÈS!
================================================================================

🔑 Vous pouvez maintenant vous connecter avec:
   Username: adminbe
   Password: Awana2025!
```

## 🧪 Test de Connexion

Après avoir exécuté le script, testez la connexion :

```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"adminbe","password":"Awana2025!"}'
```

Vous devriez recevoir un `access_token` ! ✅

## 🔍 Pourquoi ce problème ?

Le script original utilisait `passlib` avec `bcrypt`, mais il y avait un conflit de version entre `passlib` et le module `bcrypt` installé dans votre environnement.

Le script de correction utilise directement `bcrypt` (sans passer par passlib), ce qui évite ce problème de compatibilité.

## 🆘 En cas de problème

Si le script échoue :

1. **Vérifiez que bcrypt est installé** :
   ```bash
   pip install bcrypt
   ```

2. **Vérifiez que MongoDB tourne** :
   ```bash
   # Sur Mac
   sudo systemctl status mongod
   
   # Ou
   brew services list | grep mongodb
   ```

3. **Vérifiez la base de données** :
   - Le script utilise `auth_db` par défaut
   - Variable d'environnement : `DATABASE_NAME` dans `auth-microservice/.env`

---

**Après correction**, vous pourrez vous connecter normalement avec le compte adminbe ! 🎯
