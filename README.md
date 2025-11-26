# JLC Group Platform

**Version actuelle** : 1.0.0-stable ✅  
**Status** : Production Ready  
**Date de release** : 15 Novembre 2025

Application de gestion d'intérim pour JLC Group.

## Structure

```
jlc-monorepo/
├── auth-microservice/     # Service d'authentification (existant)
├── apps/
│   ├── api/              # Backend FastAPI
│   └── web/              # Frontend React
├── packages/            # Packages partagés
├── docker/              # Docker Compose
└── docs/                # Documentation
```

## Démarrage rapide

### Backend API

```bash
cd apps/api
pip install -r requirements.txt
python -m uvicorn server:app --reload --port 8001
```

### Frontend Web

```bash
cd apps/web
pnpm install
pnpm dev
```

### Auth Microservice

```bash
cd auth-microservice
pip install -r requirements.txt
python main.py
```

## Stack Technique

### Backend
- **Framework**: FastAPI 0.115+
- **Database**: MongoDB (Motor driver)
- **Auth**: JWT via auth-microservice
- **Architecture**: Clean Architecture (Domain/Application/Infrastructure/Presentation)

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build**: Vite
- **State**: Redux Toolkit + RTK Query
- **UI**: TailwindCSS + shadcn/ui
- **Router**: React Router v6

## Fonctionnalités

- ✅ Authentification multi-rles (Admin, Agence, Entreprise, Intérimaire)
- ✅ OAuth2 Google via EntraID
- ✅ Gestion de profils étendus par rle
- ✅ Validation des comptes (Entreprise & Intérimaire)
- ✅ Tableau de bord Admin avec KPIs
- ✅ Tableau de bord Intérimaire avec complétude profil
- ✅ Système de notifications (in-app + email)
- ✅ Upload d'avatars
- ✅ Audit trail

## Documentation

### Architecture & Développement

Voir `/docs` pour plus d'informations:
- Architecture
- Flow d'authentification
- Schéma de base de données
- API endpoints
- Configuration dynamique

### 🔍 Audit & Qualité du Code

- **[📑 Index Audit](/docs/AUDIT_INDEX.md)** - Point d'entrée pour l'audit des valeurs en dur
- **[📊 Résumé Exécutif](/docs/AUDIT_EXECUTIVE_SUMMARY.md)** - Vue d'ensemble de l'audit (886 valeurs en dur identifiées)
- **[🎯 Plan d'Action](/docs/AUDIT_ACTION_PLAN.md)** - Plan de correction en 4 phases
- **[🔍 Rapport Complet](/docs/AUDIT_VALEURS_EN_DUR.md)** - Détails des 886 occurrences
- **[🛠️ Script d'Audit](/scripts/audit_hardcoded_values.py)** - Outil automatisé de détection

#### Exécution locale rapide

```bash
python scripts/audit_hardcoded_values.py \
  --root-dir . \
  --markdown-output audit_reports/AUDIT_VALEURS_EN_DUR.md \
  --stats-output audit_reports/stats.json \
  --max-occurrences 2040
```

Voir le [guide dédié](/docs/AUDIT_VALEURS_EN_DUR_GUIDE.md) pour plus de détails et l'intégration CI.

### Déploiement

- **[📋 Deployment Overview](/docs/DEPLOYMENT_OVERVIEW.md)** - Vue d'ensemble complète du déploiement
- **[🚀 Quick Reference](/docs/DEPLOYMENT_QUICK_REFERENCE.md)** - Commandes essentielles et référence rapide
- **[💻 Dev Guide](/docs/DEPLOYMENT_DEV_GUIDE.md)** - Guide de déploiement environnement dev
- **[🏭 Production Guide](/docs/DEPLOYMENT_PROD_GUIDE.md)** - Guide de déploiement production
- **[⚙️ Configuration System](/docs/CONFIGURATION_SYSTEM_GUIDE.md)** - Système de configuration centralisé
- **[🕐 Configuration Versioning](/docs/CONFIGURATION_VERSIONING_GUIDE.md)** - Système de versioning et rollback de configuration
- **[✅ Checklist Template](/docs/DEPLOYMENT_CHECKLIST_TEMPLATE.md)** - Template de checklist de déploiement

## Licence

Propriétaire - JLC Group / Awana Group
