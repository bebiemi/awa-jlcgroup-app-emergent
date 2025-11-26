# 🧪 Tests locaux rapides

## API (FastAPI) – tests unitaires/async
1. Installer les dépendances API uniquement pour éviter les conflits de version Redis :
   ```bash
   pip install -r requirements-dev.txt
   ```
   *Le fichier pointe vers `apps/api/requirements.txt` sans tirer les dépendances de l'auth microservice (Redis 7.x) qui s'opposent à Redis 5.x côté API.*

2. Lancer les tests ciblés :
   ```bash
   pytest apps/api/tests/test_validation_repository.py
   pytest apps/api/tests/test_dependencies.py
   ```

3. Lancer la vérification d'alignement IAM :
   ```bash
   python scripts/test_iam_constants_sync.py
   ```

## Auth microservice
Si vous devez tester le microservice d'authentification, installez ses dépendances séparément pour éviter le conflit Redis :
```bash
pip install -r auth-microservice/requirements.txt
```
