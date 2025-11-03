# 🔐 Configuration des Secrets - JLC Group Application

## ⚠️ IMPORTANT: Ne jamais commiter de secrets dans Git

Ce document explique comment configurer les secrets de l'application sans les exposer dans le code source.

---

## 📋 Secrets Requis

### 1. Google OAuth Credentials

Obtenez vos credentials depuis [Google Cloud Console](https://console.cloud.google.com/):

1. Créez un projet ou sélectionnez un projet existant
2. Activez l'API Google+ 
3. Créez des credentials OAuth 2.0
4. Configurez les URLs autorisées

**Variables à configurer dans `/app/auth-microservice/.env`:**

```env
GOOGLE_CLIENT_ID=VOTRE_CLIENT_ID_ICI.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=VOTRE_CLIENT_SECRET_ICI
GOOGLE_REDIRECT_URI=https://votre-domaine.com/auth/google/callback
```

### 2. MongoDB Connection

**Variables à configurer dans `/app/backend/.env`:**

```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=jlc_db
```

### 3. JWT Secret

Générez une clé secrète forte:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Variables à configurer dans `/app/auth-microservice/.env`:**

```env
JWT_SECRET_KEY=VOTRE_SECRET_KEY_GENERE_ICI
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🚀 Configuration Locale (Développement)

### Étape 1: Copier les fichiers d'exemple

```bash
# Backend
cp /app/backend/.env.example /app/backend/.env

# Auth Microservice
cp /app/auth-microservice/.env.example /app/auth-microservice/.env

# Frontend
cp /app/apps/web/.env.example /app/apps/web/.env
```

### Étape 2: Remplir les valeurs

Éditez chaque fichier `.env` et remplacez les valeurs de placeholder par vos vraies credentials.

### Étape 3: Vérifier que .gitignore fonctionne

```bash
git status
```

Les fichiers `.env` ne devraient **PAS** apparaître dans les fichiers à commiter.

---

## 🔒 Sécurité

### ✅ À FAIRE:
- ✅ Utiliser des fichiers `.env` pour les secrets
- ✅ Ajouter `.env` dans `.gitignore`
- ✅ Utiliser des variables d'environnement en production
- ✅ Générer des secrets forts et uniques
- ✅ Changer régulièrement les secrets sensibles

### ❌ NE JAMAIS FAIRE:
- ❌ Commiter des secrets dans Git
- ❌ Partager des credentials par email
- ❌ Utiliser les mêmes secrets en dev et prod
- ❌ Hardcoder des secrets dans le code source
- ❌ Partager des fichiers `.env` sur Slack/Discord

---

## 🌐 Déploiement en Production

Pour la production, configurez les variables d'environnement directement dans votre service de déploiement:

### Emergent Platform
Les variables sont déjà configurées automatiquement.

### Autres Plateformes (Heroku, Vercel, etc.)
Utilisez leur interface pour configurer les variables d'environnement.

---

## 📞 Besoin d'aide?

Si vous avez des questions sur la configuration des secrets, contactez l'équipe Awana Group:
- 🌐 https://awana-group.com
- 📧 support@awana-group.com

---

© 2025 Designé et conçu par [Awana Group](https://awana-group.com)
