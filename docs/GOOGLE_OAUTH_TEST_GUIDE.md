# 🎉 Google OAuth JLC Group - Guide de Test

## ✅ Configuration Terminée!

**Client ID**: `166774342464-b9tt2eh4hd7viva770r759b0f7fha67h.apps.googleusercontent.com`  
**Client Secret**: `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` ✅  
**Status**: 🟢 **ACTIF ET FONCTIONNEL**

---

## 🧪 Test du Flow Google OAuth

### Étape 1: Accéder à la Page de Login

**URL**: https://jlc-user-portal.preview.emergentagent.com/login

✅ Vous devriez voir:
- Logo JLC GROUP ⭐
- Formulaire de connexion classique
- **Bouton "Se connecter avec Google"** avec logo Google

---

### Étape 2: Cliquer sur "Se connecter avec Google"

**Action**: Cliquer sur le bouton Google

**Ce qui se passe**:
1. ⏳ Le bouton affiche "Redirection..."
2. 🔄 Appel à l'API: `POST /auth-api/auth/google/login`
3. 🌐 Redirection vers Google OAuth consent screen

---

### Étape 3: Écran de Consentement Google

**Ce que vous voyez**:
```
JLC Group - Gestion Intérim
wants to access your Google Account

This will allow JLC Group - Gestion Intérim to:
✓ See your personal info, including any personal info you've made publicly available
✓ See your primary Google Account email address

[Cancel] [Continue]
```

**Action**: Cliquer sur **"Continue"**

⚠️ **Note**: Si vous n'avez pas ajouté votre email comme "Test user" dans Google Cloud Console:
- Vous verrez un message d'erreur
- Solution: Retourner à Google Cloud Console → OAuth consent screen → Test users → Ajouter votre email

---

### Étape 4: Sélection du Compte Google

**Ce que vous voyez**:
- Liste de vos comptes Google
- "Choose an account to continue to JLC Group - Gestion Intérim"

**Action**: Sélectionnez le compte avec lequel vous voulez vous connecter

---

### Étape 5: Callback et Redirection

**Ce qui se passe automatiquement**:
1. Google redirige vers: `https://jlc-user-portal.preview.emergentagent.com/auth/google/callback?code=...&state=...`
2. ⏳ Page de chargement: "Connexion en cours..."
3. 🔄 Appel à l'API: `POST /auth-api/auth/google/callback`
4. 🎉 Création/mise à jour du compte utilisateur
5. 🔑 Génération des JWT tokens
6. ➡️ Redirection automatique vers le dashboard

---

### Étape 6: Premier Login - Création de Compte

**Si c'est votre premier login avec ce compte Google**:

✅ **Compte créé automatiquement** avec:
```json
{
  "username": "votre-email-prefix",
  "email": "votre-email@gmail.com",
  "full_name": "Votre Nom Complet",
  "provider": "google",
  "status": "pending",
  "roles": ["interim"],
  "picture": "https://lh3.googleusercontent.com/...",
  "is_verified": true
}
```

**Vous serez redirigé vers**: `/interimaire` (Dashboard Intérimaire)

**Ce que vous verrez**:
- 🟡 Bannière: "Validation en cours"
- Message: "Votre compte est en cours de vérification par notre équipe"
- Complétude du profil: 0% (profil vide)
- Checklist pour compléter le profil

---

### Étape 7: Logins Suivants

**Si vous vous reconnectez avec le même compte Google**:

✅ **Compte reconnu** et mis à jour:
- Email/nom mis à jour si changés sur Google
- Rôles/permissions conservés
- Status conservé (pending/active)

**Redirection**: Dashboard selon votre rôle actuel

---

## 🎯 Scénarios de Test Recommandés

### Test 1: Premier Login Google (Nouveau Utilisateur)

1. **Se connecter avec un nouveau compte Google**
2. ✅ Vérifier que le compte est créé
3. ✅ Vérifier que le rôle "interim" est assigné
4. ✅ Vérifier que le status est "pending"
5. ✅ Vérifier la redirection vers `/interimaire`
6. ✅ Vérifier la bannière "Validation en cours"

### Test 2: Login Admin Approuve le Compte

1. **Se déconnecter**
2. **Se connecter avec admin/awana2025**
3. **Aller dans**: Admin → Validations
4. **Trouver**: Le compte Google créé (status: pending)
5. **Action**: Approuver le compte avec un commentaire
6. ✅ Vérifier la notification envoyée

### Test 3: Re-login Google Après Validation

1. **Se déconnecter**
2. **Se reconnecter avec le même compte Google**
3. ✅ Vérifier que le status est maintenant "active"
4. ✅ Vérifier que la bannière "Compte approuvé" s'affiche

### Test 4: Compléter le Profil

1. **Aller dans**: Mon Profil
2. **Remplir**: Compétences, expérience, bio, etc.
3. **Upload**: Photo de profil (ou utiliser celle de Google)
4. **Sauvegarder**
5. ✅ Vérifier que la complétude augmente

### Test 5: Erreurs et Edge Cases

**Test 5.1: Annuler le consentement Google**
- Action: Cliquer "Cancel" sur l'écran Google
- Résultat attendu: Retour à la page login avec message d'erreur

**Test 5.2: State CSRF invalide**
- (Test automatique déjà géré)
- Résultat: Erreur "Invalid or expired state parameter"

**Test 5.3: Code expiré**
- Attendre 10 minutes après la redirection
- Résultat: Erreur "Authorization code expired"

---

## 📊 Vérifications Backend

### Dans MongoDB (Collection `users`)

```javascript
db.users.find({ provider: "google" })
```

**Résultat attendu**:
```json
{
  "_id": ObjectId("..."),
  "id": "generated-uuid",
  "username": "john.doe",
  "email": "john.doe@gmail.com",
  "full_name": "John Doe",
  "provider": "google",
  "provider_user_id": "123456789012345678901",
  "password_hash": null,
  "is_verified": true,
  "status": "pending",
  "roles": [],
  "created_at": ISODate("..."),
  "updated_at": ISODate("..."),
  "last_login_at": ISODate("...")
}
```

### Dans MongoDB (Collection `audit_trail`)

```javascript
db.audit_trail.find({ action: "LOGIN_SUCCESS", "details.provider": "google" })
```

**Résultat attendu**:
```json
{
  "action": "LOGIN_SUCCESS",
  "user_id": "user-id",
  "resource_type": "auth",
  "ip_address": "xxx.xxx.xxx.xxx",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "provider": "google",
    "method": "oauth",
    "session_id": "session-uuid"
  },
  "created_at": ISODate("...")
}
```

---

## 🔍 Logs à Surveiller

### Auth Microservice (`/tmp/auth.log`)

```bash
tail -f /tmp/auth.log
```

**Messages attendus**:
```
INFO:awana_auth.providers.google:Google OAuth login initiated from IP: xxx.xxx.xxx.xxx
INFO:awana_auth.providers.google:New Google user registered: john.doe@gmail.com
INFO:awana_auth.audit.logger:Audit log created: LOGIN_SUCCESS for user xxx
```

### Backend JLC API

```bash
tail -f /var/log/supervisor/backend.out.log
```

**Messages attendus**:
```
INFO:     POST /api/profiles/me
INFO:     GET /api/notifications
```

---

## ⚙️ Configuration Actuelle

### Variables d'Environnement (`.env`)

```env
GOOGLE_CLIENT_ID=166774342464-b9tt2eh4hd7viva770r759b0f7fha67h.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://jlc-user-portal.preview.emergentagent.com/auth/google/callback
```

### Google Cloud Console - Configuration Actuelle

**Redirect URIs autorisés**:
```
https://jlc-user-portal.preview.emergentagent.com/auth/google/callback
http://localhost:3000/auth/google/callback
```

**Scopes demandés**:
- `openid`
- `email`
- `profile`

**Mode**: Testing (limité aux Test users)

---

## 🚨 Troubleshooting

### Problème 1: "Google OAuth is not configured"

**Cause**: Variables d'environnement non chargées

**Solution**:
```bash
cd /app/auth-microservice
cat .env | grep GOOGLE
# Vérifier que les valeurs sont présentes

# Redémarrer le service
pkill -9 -f "uvicorn main:app"
cd /app/auth-microservice
nohup /root/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/auth.log 2>&1 &
```

### Problème 2: "Access blocked: This app's request is invalid"

**Cause**: Redirect URI non autorisé dans Google Cloud Console

**Solution**:
1. Google Cloud Console → Credentials
2. Éditer OAuth 2.0 Client ID
3. Vérifier les Authorized redirect URIs
4. Ajouter l'URI manquant

### Problème 3: "Invalid or expired state parameter"

**Cause**: State token expiré (>10 minutes) ou déjà utilisé

**Solution**: Recommencer le flow depuis le début

### Problème 4: "Failed to fetch"

**Cause**: Backend non accessible

**Solution**:
```bash
sudo supervisorctl status
# Vérifier que backend et frontend sont RUNNING

# Redémarrer si nécessaire
sudo supervisorctl restart backend frontend
```

---

## 📈 Métriques de Succès

### KPIs à Surveiller

1. **Taux de conversion OAuth**:
   - Clicks "Se connecter avec Google" vs logins réussis
   - Target: >90%

2. **Temps moyen du flow**:
   - De "Click Google" à "Dashboard"
   - Target: <30 secondes

3. **Erreurs OAuth**:
   - Annulations utilisateur
   - Erreurs techniques
   - Target: <5%

---

## 🎯 Checklist de Validation Finale

Avant de considérer Google OAuth comme "production-ready":

- [ ] Test avec au moins 3 comptes Google différents
- [ ] Vérifier que les nouveaux users sont bien créés
- [ ] Vérifier que les logins répétés fonctionnent
- [ ] Tester l'annulation du consentement Google
- [ ] Vérifier les logs d'audit
- [ ] Vérifier les notifications envoyées
- [ ] Tester le flow de validation admin
- [ ] Vérifier la complétude du profil
- [ ] Tester sur mobile (responsive)
- [ ] Vérifier les performances (<2s pour callback)

---

## 🚀 Prochaines Étapes (Optionnel)

### Passage en Production

1. **Google Cloud Console**:
   - OAuth consent screen → Publish App
   - Remplir le formulaire de vérification
   - Attendre l'approbation Google (quelques jours)

2. **Domaine de Production**:
   - Ajouter les redirect URIs de production
   - Mettre à jour GOOGLE_REDIRECT_URI

3. **Monitoring**:
   - Ajouter Sentry pour tracking erreurs OAuth
   - Dashboard analytics pour métriques OAuth

---

**🎉 STATUS**: Google OAuth est maintenant **PLEINEMENT FONCTIONNEL** sur le preview!

**Test immédiatement**: https://jlc-user-portal.preview.emergentagent.com/login
