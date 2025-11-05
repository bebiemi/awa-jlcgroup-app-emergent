# 🚀 Guide de Déploiement - Vue d'Ensemble

## 📋 Introduction

Ce document fournit une vue d'ensemble complète du processus de déploiement de l'application JLC pour tous les environnements. Il sert de point d'entrée pour la documentation de déploiement.

---

## 🎯 Architecture de Déploiement

### Stack Technologique

- **Backend**: FastAPI + Python 3.11+
- **Frontend**: React 18 + TypeScript + Vite
- **Base de données**: MongoDB 7.0+
- **Reverse Proxy**: Nginx
- **Process Manager**: Supervisor (dev/staging) ou Docker (prod)
- **Configuration**: YAML hiérarchique + Secrets Manager

### Environnements

| Environnement | Utilisation | Configuration | Secrets |
|---------------|-------------|---------------|---------|
| **Local** | Développement individuel | `config/local.yaml` | `.env.encrypted` |
| **Dev** | Intégration continue | `config/dev.yaml` | `.env.encrypted` |
| **Staging** | Préproduction / Tests | `config/staging.yaml` | `.env.encrypted` |
| **Prod** | Production | `config/prod.yaml` | AWS Secrets Manager |

---

## 📚 Documentation de Déploiement

### Guides Détaillés

1. **[Guide de Configuration Centralisée](/app/docs/CONFIGURATION_SYSTEM_GUIDE.md)**
   - Principe du système de configuration
   - Utilisation de ConfigManager
   - Gestion des secrets
   - Ordre de priorité des configurations
   - 📖 **Lecture obligatoire avant déploiement**

2. **[Guide de Déploiement DEV](/app/docs/DEPLOYMENT_DEV_GUIDE.md)**
   - Environnement de développement/intégration
   - Configuration avec .env.encrypted
   - Déploiement Supervisor ou Docker Compose
   - Tests et validation
   - Monitoring et logs
   - 🎯 **Pour équipe de développement**

3. **[Guide de Déploiement PRODUCTION](/app/docs/DEPLOYMENT_PROD_GUIDE.md)**
   - Environnement de production
   - AWS Secrets Manager
   - Configuration Nginx avec SSL/TLS
   - Docker production
   - Monitoring avancé (CloudWatch)
   - Procédures de rollback
   - 🚨 **Critique - Lecture obligatoire pour ops**

4. **[Log de Migration Configuration - Phase 3](/app/docs/CONFIGURATION_PHASE3_COMPLETE.md)**
   - Historique de migration vers configuration centralisée
   - Tests automatisés
   - Métriques de migration
   - 📊 **Référence technique**

---

## 🔄 Workflow de Déploiement

### Flux de Développement

```
Développeur Local (local.yaml)
         ↓
    git push
         ↓
CI/CD Pipeline (dev.yaml)
         ↓
Environnement Dev
         ↓
Tests Automatisés ✅
         ↓
Environnement Staging (staging.yaml)
         ↓
Tests UAT ✅
         ↓
Environnement Production (prod.yaml)
```

### Processus de Déploiement par Environnement

#### 1. Local → Dev

```bash
# 1. Développement local
npm run dev          # Frontend
python main.py       # Backend

# 2. Tests locaux
pytest tests/
npm test

# 3. Commit et push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin feature/ma-feature

# 4. Merge vers main (après review)
# 5. CI/CD automatique déploie sur Dev
```

#### 2. Dev → Staging

```bash
# 1. Tag de version
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 2. CI/CD déploie automatiquement sur Staging
# 3. Tests UAT par l'équipe QA
```

#### 3. Staging → Production

```bash
# 1. Validation finale sur Staging
# 2. Fenêtre de maintenance annoncée
# 3. Backup production
mongodump --uri="${MONGO_URL}" --out=/backups/$(date +%Y%m%d)

# 4. Déploiement production
# Voir: DEPLOYMENT_PROD_GUIDE.md

# 5. Health checks post-déploiement
/app/scripts/health-check-prod.sh

# 6. Monitoring actif (30 minutes)
```

---

## 🔐 Gestion des Secrets

### Vue d'Ensemble

| Secret | Local | Dev | Staging | Production |
|--------|-------|-----|---------|------------|
| **Stockage** | `.env` local | `.env.encrypted` | `.env.encrypted` | AWS Secrets Manager |
| **Chiffrement** | ❌ | ✅ Fernet | ✅ Fernet | ✅ AWS KMS |
| **Versionné** | ❌ | ✅ | ✅ | ❌ (AWS) |
| **Rotation** | Manuel | Manuel | Manuel | Automatique (30j) |

### Secrets Requis

#### Minimaux (tous environnements)

```bash
MONGO_URL=mongodb://...
JWT_SECRET_KEY=your-secret-key-min-32-chars
```

#### Complets (production)

```bash
# Database
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/auth_db_prod

# JWT
JWT_SECRET_KEY=production-jwt-secret-64-chars-minimum-very-strong

# OAuth2 Google
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret
GOOGLE_REDIRECT_URI=https://jlc-platform.com/auth/google/callback

# Email (SendGrid)
SENDGRID_API_KEY=SG.your-sendgrid-api-key

# SMS (Twilio - optionnel)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token

# Cloud Storage (AWS S3)
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=eu-west-1
```

### Procédure de Rotation

**Dev/Staging:**

```bash
# 1. Éditer .env
vim /app/auth-microservice/.env.dev

# 2. Re-chiffrer
cd /app/auth-microservice
python scripts/encrypt_env.py encrypt .env.dev .env.dev.encrypted

# 3. Commit
git add .env.dev.encrypted
git commit -m "security: rotate dev secrets"
git push

# 4. Déployer
# Le CI/CD déchiffre automatiquement avec .env.key stocké en secret
```

**Production:**

```bash
# 1. Modifier dans AWS Secrets Manager
aws secretsmanager update-secret \
  --secret-id jlc-auth-prod \
  --secret-string file://new-secrets.json

# 2. Redémarrer l'application
docker-compose -f docker-compose.prod.yml restart auth-microservice

# 3. Vérifier
curl https://api.jlc-platform.com/health
```

---

## ✅ Checklist de Déploiement

### Pré-Déploiement

- [ ] Code testé localement (tests unitaires + intégration)
- [ ] Pull request review approuvée
- [ ] Documentation à jour
- [ ] Secrets configurés pour l'environnement cible
- [ ] Backup de la base de données (staging/prod)
- [ ] Fenêtre de maintenance annoncée (prod uniquement)
- [ ] Équipe disponible en cas de problème

### Déploiement

- [ ] Code déployé (git pull + build)
- [ ] Dépendances installées (pip + yarn)
- [ ] Migrations de base de données exécutées (si nécessaire)
- [ ] Configuration validée (`python scripts/test_config.py`)
- [ ] Services redémarrés
- [ ] Health checks passent

### Post-Déploiement

- [ ] Health endpoint répond (200 OK)
- [ ] Tests de fumée passent
- [ ] Logs vérifiés (pas d'erreur critique)
- [ ] Métriques normales (CPU, RAM, temps de réponse)
- [ ] Monitoring actif (30 minutes minimum)
- [ ] Équipe informée du succès

### En Cas de Problème

- [ ] Rollback exécuté immédiatement
- [ ] Incident documenté
- [ ] Root cause analysis planifiée
- [ ] Post-mortem créé

---

## 🛠️ Outils et Scripts

### Scripts de Déploiement

```bash
/app/auth-microservice/scripts/
├── encrypt_env.py           # Chiffrement des secrets
├── test_config.py           # Validation de la configuration
├── seed_mission_references.py    # Seed des données de référence
└── seed_additional_references.py # Seed des données additionnelles
```

### Commandes Essentielles

#### Configuration

```bash
# Générer une clé de chiffrement
python scripts/encrypt_env.py generate-key

# Chiffrer un fichier .env
python scripts/encrypt_env.py encrypt .env .env.encrypted

# Déchiffrer
python scripts/encrypt_env.py decrypt .env.encrypted .env

# Tester la configuration
python scripts/test_config.py
```

#### Services

```bash
# Supervisor (dev/staging)
sudo supervisorctl status
sudo supervisorctl restart jlc-backend-dev
sudo supervisorctl restart jlc-frontend-dev
sudo supervisorctl tail -f jlc-backend-dev

# Docker (prod)
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f auth-microservice
docker-compose -f docker-compose.prod.yml restart
```

#### Monitoring

```bash
# Health check
curl https://api.jlc-platform.com/health

# Logs backend
tail -f /var/log/supervisor/jlc-backend-*.log
docker-compose logs -f --tail=100 auth-microservice

# Logs frontend
tail -f /var/log/supervisor/jlc-frontend-*.log

# Monitoring MongoDB
mongosh $MONGO_URL
# > db.serverStatus()
# > db.stats()
```

---

## 🐛 Dépannage Rapide

### Service ne démarre pas

```bash
# 1. Vérifier les logs
sudo supervisorctl tail -f jlc-backend-dev stderr

# 2. Vérifier la configuration
python scripts/test_config.py

# 3. Vérifier MongoDB
mongosh $MONGO_URL
```

### Erreur "Secret manquant"

```bash
# 1. Vérifier que .env existe
ls -la /app/auth-microservice/.env

# 2. Vérifier les variables
cat /app/auth-microservice/.env | grep JWT_SECRET_KEY

# 3. Re-déchiffrer si nécessaire
python scripts/encrypt_env.py decrypt .env.encrypted .env
```

### Erreur de connexion MongoDB

```bash
# 1. Tester la connexion
mongosh $MONGO_URL

# 2. Vérifier les credentials
echo $MONGO_URL

# 3. Vérifier le network/firewall
ping mongodb-host
telnet mongodb-host 27017
```

### Configuration incorrecte

```bash
# 1. Vérifier l'environnement détecté
curl http://localhost:8000/health | jq .environment

# 2. Forcer l'environnement
export APP_ENV=dev
sudo supervisorctl restart jlc-backend-dev

# 3. Vérifier quelle config est chargée
python -c "
from awana_auth.core.config_manager import get_config
config = get_config()
print(f'Env: {config.env}')
print(f'Debug: {config.get(\"app.debug\")}')
"
```

---

## 📊 Monitoring et Métriques

### Endpoints de Santé

```bash
# Backend health
curl https://api.jlc-platform.com/health
# Response: {"status": "healthy", "service": "JLC Auth Service", "version": "1.0.0", "environment": "prod"}

# OAuth status
curl https://api.jlc-platform.com/api/auth/google/status
# Response: {"enabled": true, "configured": true}

# Admin stats (avec token)
curl https://api.jlc-platform.com/api/auth/admin/stats \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

### Métriques Clés

| Métrique | Seuil Normal | Alerte | Critique |
|----------|--------------|--------|----------|
| Temps de réponse API | < 200ms | > 500ms | > 1s |
| Taux d'erreur | < 1% | > 5% | > 10% |
| CPU | < 50% | > 70% | > 90% |
| RAM | < 60% | > 80% | > 95% |
| Connexions MongoDB | < 50 | > 80 | > 100 |

### Logs Importants

**Démarrage réussi:**
```
🚀 Starting AWANA Auth Microservice (env: prod)...
🔧 Chargement de la configuration pour l'environnement: prod
🔐 Secrets chargés depuis AWS Secrets Manager: jlc-auth-prod
✅ Connected to MongoDB: auth_db_prod
✅ Configuration chargée avec succès
✅ Validation de configuration réussie
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Erreurs à surveiller:**
```
❌ Variable de configuration requise manquante: database.url
❌ Erreur lors du chargement des secrets AWS
⚠️  Secret AWS non trouvé: jlc-auth-prod
❌ MongoDB connection failed
```

---

## 🔗 Références

### Documentation

- [Configuration System Guide](/app/docs/CONFIGURATION_SYSTEM_GUIDE.md) - Guide complet du système de configuration
- [Dev Deployment Guide](/app/docs/DEPLOYMENT_DEV_GUIDE.md) - Déploiement environnement dev
- [Prod Deployment Guide](/app/docs/DEPLOYMENT_PROD_GUIDE.md) - Déploiement production
- [Configuration Phase 3](/app/docs/CONFIGURATION_PHASE3_COMPLETE.md) - Log de migration

### Fichiers Clés

- `/app/auth-microservice/config/` - Fichiers de configuration YAML
- `/app/auth-microservice/awana_auth/core/config_manager.py` - Gestionnaire de configuration
- `/app/auth-microservice/scripts/` - Scripts utilitaires
- `/app/auth-microservice/.env.example` - Exemple de fichier .env

### Services Externes

- **MongoDB Atlas** - Base de données production
- **AWS Secrets Manager** - Gestion des secrets production
- **AWS S3** - Stockage documents/uploads
- **SendGrid** - Service email
- **Google OAuth** - Authentification sociale

---

## 📞 Support

### Contacts

- **Équipe DevOps**: devops@jlc-platform.com
- **Support technique**: support-tech@jlc-platform.com
- **Urgences production**: +241-XX-XX-XX-XX (24/7)

### Ressources

- **Runbook**: [À créer] - Procédures d'intervention
- **Postmortem**: [À créer] - Analyses d'incidents
- **Status Page**: [À configurer] - État des services

---

## ✅ Prochaines Étapes

### Court Terme

1. [ ] Tester déploiement sur environnement dev
2. [ ] Créer .env.encrypted pour staging
3. [ ] Configurer AWS Secrets Manager pour prod
4. [ ] Mettre en place le CI/CD pipeline

### Moyen Terme

1. [ ] Créer scripts d'automatisation de déploiement
2. [ ] Mettre en place monitoring CloudWatch/Datadog
3. [ ] Configurer les alertes
4. [ ] Créer un runbook d'incident

### Long Terme

1. [ ] Infrastructure as Code (Terraform)
2. [ ] Blue-Green Deployment
3. [ ] Canary Releases
4. [ ] Auto-scaling

---

**Date de création**: 5 Novembre 2025  
**Version**: 1.0  
**Dernière mise à jour**: 5 Novembre 2025

---

**Ce document est maintenu par l'équipe DevOps. Pour toute suggestion ou correction, ouvrir une issue ou contacter devops@jlc-platform.com**
