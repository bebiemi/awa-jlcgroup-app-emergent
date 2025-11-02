# JLC Monorepo

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

Voir `/docs` pour plus d'informations:
- Architecture
- Flow d'authentification
- Schéma de base de données
- API endpoints

## Licence

Propriétaire - JLC Group / Awana Group
