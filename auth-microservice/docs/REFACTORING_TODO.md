# Refactoring TODO

## État Actuel vs. Objectif

### Structure Actuelle
```
/app/auth-microservice/
├── awana_auth/
│   ├── core/
│   │   ├── models.py
│   │   └── profile_models.py
│   └── services/
│       ├── application_eligibility_service.py
│       └── ...
├── mission_routes.py          ❌ À la racine
├── profile_routes.py          ❌ À la racine
├── professional_experiences_routes.py  ❌ À la racine
└── main.py
```

### Structure Cible (Recommandée)
```
/app/auth-microservice/
├── awana_auth/
│   ├── core/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── profile.py
│   │   │   └── documents.py
│   │   └── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── profile_routes.py
│   │   ├── mission_routes.py
│   │   └── document_routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   └── application_eligibility_service.py
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_application_eligibility.py
│       └── test_document_upload.py
└── main.py
```

---

## Tâches de Refactoring

### 🔴 Priorité Haute

#### 1. Organiser les Routes
**Statut**: ❌ À faire  
**Effort**: Moyen (2-3h)

**Actions**:
- [ ] Créer `/app/auth-microservice/awana_auth/routes/`
- [ ] Déplacer `mission_routes.py` → `routes/mission_routes.py`
- [ ] Déplacer `profile_routes.py` → `routes/profile_routes.py`
- [ ] Déplacer `professional_experiences_routes.py` → `routes/experience_routes.py`
- [ ] Créer `routes/__init__.py` avec exports
- [ ] Mettre à jour les imports dans `main.py`

**Tests nécessaires**: Vérifier que tous les endpoints fonctionnent après déplacement

---

#### 2. Séparer les Modèles
**Statut**: ⚠️  Partiellement fait  
**Effort**: Faible (1h)

**Actions**:
- [ ] Créer `/app/auth-microservice/awana_auth/core/models/`
- [ ] Séparer `models.py` en :
  - `user.py` (User, UserCreate, etc.)
  - `auth.py` (Token, LoginRequest, etc.)
- [ ] Séparer `profile_models.py` en :
  - `profile.py` (Profile bases)
  - `interim_profile.py` (InterimProfile, CandidatProfile)
  - `documents.py` (DocumentUploadResponse, etc.)
- [ ] Créer `models/__init__.py` avec exports

---

#### 3. Tests Unitaires Complets
**Statut**: 🟡 En cours  
**Effort**: Élevé (4-6h)

**Actions**:
- [x] Tests ApplicationEligibilityService
- [x] Tests Document Upload
- [ ] Tests Mission Application Endpoint
- [ ] Tests Profile Endpoints
- [ ] Tests Experience CRUD
- [ ] Configuration pytest avec fixtures partagées
- [ ] Tests d'intégration E2E

**Couverture cible**: >80%

---

### 🟡 Priorité Moyenne

#### 4. Factoriser les Services
**Statut**: ❌ À faire  
**Effort**: Moyen (2h)

**Actions**:
- [ ] Créer `ProfileService` pour logique métier profil
- [ ] Créer `DocumentService` pour gestion documents
- [ ] Créer `MissionService` pour logique missions
- [ ] Extraire logique répétée des routes vers services

**Bénéfices**: Meilleure séparation des responsabilités, code plus testable

---

#### 5. Configuration Centralisée
**Statut**: ⚠️  Config dispersée  
**Effort**: Faible (1h)

**Actions**:
- [ ] Créer `/app/auth-microservice/awana_auth/core/config.py`
- [ ] Centraliser toutes les configs :
  - Upload (MAX_FILE_SIZE, ALLOWED_MIME_TYPES)
  - Business rules (CACHE_TTL)
  - Database (MONGO_URL)
- [ ] Utiliser Pydantic Settings
- [ ] Variables d'environnement documentées

---

#### 6. Validation Pydantic Renforcée
**Statut**: ⚠️  Validation partielle  
**Effort**: Faible (1h)

**Actions**:
- [ ] Ajouter validators sur tous les modèles
- [ ] Validation email avec regex
- [ ] Validation téléphone international
- [ ] Validation dates (end_date > start_date)
- [ ] Messages d'erreur clairs et traduits

---

### 🟢 Priorité Basse

#### 7. Documentation API (OpenAPI)
**Statut**: ⚠️  Documentation de base  
**Effort**: Moyen (2h)

**Actions**:
- [ ] Enrichir docstrings des endpoints
- [ ] Ajouter exemples de requêtes/réponses
- [ ] Ajouter descriptions détaillées
- [ ] Swagger UI amélioré avec sections
- [ ] Exemples de codes d'erreur

---

#### 8. Logging Structuré
**Statut**: ❌ Logging basique  
**Effort**: Faible (1h)

**Actions**:
- [ ] Configurer structlog ou python-json-logger
- [ ] Logs JSON avec context (user_id, request_id)
- [ ] Niveaux de log cohérents
- [ ] Rotation des logs configurée

---

#### 9. Monitoring & Métriques
**Statut**: ❌ Pas de monitoring  
**Effort**: Élevé (4h)

**Actions**:
- [ ] Prometheus metrics
- [ ] Métriques métier (candidatures/jour, taux de succès)
- [ ] Health check endpoint détaillé
- [ ] Dashboard Grafana (si infrastructure)

---

## Plan de Migration (Sans Régression)

### Phase 1: Préparation (1 jour)
1. Créer les nouveaux répertoires (`routes/`, `models/`, `tests/`)
2. Copier (pas déplacer) les fichiers vers nouvelle structure
3. Mettre à jour les imports dans les copies
4. Tests unitaires passent sur nouvelle structure

### Phase 2: Tests Parallèles (1 jour)
1. Exécuter ancienne et nouvelle structure en parallèle
2. Comparer les résultats
3. Fixer les différences

### Phase 3: Bascule (0.5 jour)
1. Mettre à jour `main.py` pour utiliser nouvelle structure
2. Supprimer anciens fichiers
3. Tests E2E complets
4. Rollback si problème

### Phase 4: Nettoyage (0.5 jour)
1. Supprimer code dupliqué
2. Mise à jour documentation
3. Annonce aux équipes

---

## Commandes Utiles

### Exécuter les Tests
```bash
# Tous les tests
pytest /app/auth-microservice/tests/ -v

# Tests spécifiques
pytest /app/auth-microservice/tests/test_application_eligibility.py -v

# Avec couverture
pytest /app/auth-microservice/tests/ --cov=awana_auth --cov-report=html
```

### Vérifier la Structure
```bash
tree /app/auth-microservice/awana_auth -L 2
```

### Linting
```bash
# Python
ruff check /app/auth-microservice/awana_auth/

# Avec auto-fix
ruff check /app/auth-microservice/awana_auth/ --fix
```

---

## Métriques de Succès

- [ ] 0 régression sur endpoints existants
- [ ] Couverture de tests > 80%
- [ ] Tous les linters passent
- [ ] Documentation à jour
- [ ] Temps de réponse API identique ou meilleur
- [ ] Zéro valeur en dur (config dynamique)

---

## Prochaines Étapes Recommandées

1. **Immédiat**: Créer tests unitaires manquants
2. **Court terme (1 semaine)**: Organiser routes et modèles
3. **Moyen terme (2-4 semaines)**: Services + Config centralisée
4. **Long terme (1-2 mois)**: Monitoring + Documentation complète

---

## Contacts & Ressources

- **Lead Dev**: À définir
- **Documentation**: `/app/auth-microservice/docs/`
- **Tests**: `/app/auth-microservice/tests/`
- **CI/CD**: À configurer
