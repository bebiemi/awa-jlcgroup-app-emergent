# 🔐 Guide: Configuration Google OAuth pour JLC Group

## Étape 1: Accéder à Google Cloud Console

1. Ouvrez: https://console.cloud.google.com
2. Connectez-vous avec votre compte Google

---

## Étape 2: Créer ou Sélectionner un Projet

### Option A: Nouveau Projet
1. Cliquez sur le sélecteur de projet (en haut à gauche)
2. Cliquez sur **"NEW PROJECT"**
3. Nom du projet: `JLC Group Auth`
4. Cliquez sur **"CREATE"**

### Option B: Projet Existant
- Sélectionnez votre projet existant dans la liste

---

## Étape 3: Activer Google+ API

1. Menu hamburger (☰) → **APIs & Services** → **Library**
2. Recherchez: `Google+ API`
3. Cliquez sur **Google+ API**
4. Cliquez sur **"ENABLE"**

---

## Étape 4: Configurer l'Écran de Consentement OAuth

1. Menu: **APIs & Services** → **OAuth consent screen**
2. Sélectionnez: **External** (pour tester avec n'importe quel compte Google)
3. Cliquez sur **"CREATE"**

### Remplir le formulaire:

**App information:**
- App name: `JLC Group - Gestion Intérim`
- User support email: `votre-email@domain.com`
- App logo: (optionnel, vous pouvez uploader le logo JLC)

**App domain:**
- Application home page: `https://staffmanager-5.preview.emergentagent.com`
- Application privacy policy link: `https://staffmanager-5.preview.emergentagent.com/privacy`
- Application terms of service link: `https://staffmanager-5.preview.emergentagent.com/terms`

**Authorized domains:**
- Ajoutez: `emergentagent.com`

**Developer contact information:**
- Email: `votre-email@domain.com`

4. Cliquez sur **"SAVE AND CONTINUE"**

### Scopes (Étape 2):
1. Cliquez sur **"ADD OR REMOVE SCOPES"**
2. Sélectionnez:
   - ✅ `.../auth/userinfo.email`
   - ✅ `.../auth/userinfo.profile`
   - ✅ `openid`
3. Cliquez sur **"UPDATE"**
4. Cliquez sur **"SAVE AND CONTINUE"**

### Test users (Étape 3):
1. Cliquez sur **"ADD USERS"**
2. Ajoutez votre email pour tester
3. Cliquez sur **"SAVE AND CONTINUE"**

### Summary (Étape 4):
- Vérifiez les informations
- Cliquez sur **"BACK TO DASHBOARD"**

---

## Étape 5: Créer les Credentials OAuth 2.0

1. Menu: **APIs & Services** → **Credentials**
2. Cliquez sur **"+ CREATE CREDENTIALS"** (en haut)
3. Sélectionnez: **OAuth client ID**

### Configurer le Client ID:

**Application type:** `Web application`

**Name:** `JLC Group Web Client`

**Authorized JavaScript origins:**
```
https://staffmanager-5.preview.emergentagent.com
http://localhost:3000
```

**Authorized redirect URIs:**
```
https://staffmanager-5.preview.emergentagent.com/auth/google/callback
http://localhost:3000/auth/google/callback
```

4. Cliquez sur **"CREATE"**

---

## Étape 6: Copier les Credentials

Une popup s'affiche avec:
- ✅ **Client ID**: `123456789-xxxxx.apps.googleusercontent.com`
- ✅ **Client Secret**: `GOCSPX-xxxxxxxxxxxxx`

**⚠️ IMPORTANT**: 
- Copiez ces deux valeurs
- Conservez-les en sécurité
- Vous pouvez les retrouver dans la page Credentials

---

## Étape 7: Fournir les Credentials

Une fois que vous avez:
1. ✅ Client ID
2. ✅ Client Secret

**Fournissez-les moi dans ce format:**

```
Client ID: 123456789-xxxxx.apps.googleusercontent.com
Client Secret: GOCSPX-xxxxxxxxxxxxx
```

---

## 📸 Captures d'écran Utiles

### 1. Sélecteur de projet
Cherchez le nom de votre projet en haut à gauche, à côté de "Google Cloud"

### 2. OAuth consent screen
Devrait afficher "Publishing status: Testing"

### 3. Credentials
Devrait montrer votre "OAuth 2.0 Client IDs" créé

---

## ⏱️ Temps Estimé: 10-15 minutes

Si vous rencontrez des difficultés, je peux vous aider à chaque étape!

---

## 🔄 Mode Test vs Production

**Mode Test (actuel):**
- Limité aux "Test users" ajoutés
- Parfait pour développement
- Pas besoin de vérification Google

**Mode Production (plus tard):**
- Accessible à tous les utilisateurs
- Nécessite vérification par Google
- Process: OAuth consent screen → "PUBLISH APP"

Pour le moment, restez en mode **Test**!

---

## ✅ Checklist Finale

Avant de me fournir les credentials, vérifiez:
- [ ] OAuth consent screen configuré
- [ ] Scopes ajoutés (email, profile, openid)
- [ ] Test user ajouté (votre email)
- [ ] OAuth Client ID créé (type: Web application)
- [ ] Redirect URIs ajoutés
- [ ] Client ID copié
- [ ] Client Secret copié

---

**Une fois que vous avez les credentials, envoyez-les moi et je configure tout!** 🚀
