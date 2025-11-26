# 🔎 Audit des valeurs en dur – État d'avancement (26/11/2025)

## Synthèse rapide
- L'audit initial recense **886 occurrences** à supprimer et reste la référence (voir `docs/AUDIT_INDEX.md`).
- Les statuts et types de validation utilisés par l'API d'authentification sont désormais **pilotés par la configuration** (`validation_routes.py`).
- La trajectoire reste inchangée : suppression des valeurs en dur, factorisation via la config, et préparation à l'usage mobile.

## Travaux déjà effectués
- **Centralisation des statuts/types de validation** : `auth-microservice/validation_routes.py` lit désormais les statuts (`pending`, `approved`, `rejected`) et types (`interim`, `company`, `collaborator`) via `cfg.get_validation_status` / `cfg.get_validation_type`, couvrant les statistiques, les flux d'approbation/rejet et les contrôles spécifiques aux entreprises.
- **Dé-hardcodage du flux candidat → intérimaire** : `auth-microservice/awana_auth_routes.py` s’appuie sur `IAMGroups`, `IAMProfiles`, `UserRoles` et `get_validation_type_for_role` pour éviter les chaînes `candidat`/`grp.*` codées en dur (création des validations, promotion interimaire, mise à jour des rôles).
- **Documentation de progression mise à jour** : `REFACTORING_PROGRESS.md` reflète 8 fichiers refactorés (~23% du périmètre) dont la refonte des validations et l'attribution de profils IAM.
- **Contrôles d'accès référentiels alignés IAM** : `auth-microservice/system_references_routes.py` n’utilise plus les rôles `admin`/`super_admin` en dur et s'appuie sur `cfg.get_admin_role` / `cfg.get_super_admin_role` pour sécuriser l'accès public aux référentiels.
- **Attribution de profils IAM sans valeurs en dur** : `auth-microservice/security_routes.py` mappe désormais les rôles issus de la configuration (`cfg`) vers les profils `IAMProfiles`, supprimant les chaînes inline `admin`/`super_admin`/`interim`/`company`/`commercial` lors de la création d'utilisateurs.

## Actions prioritaires restantes
1. **Externaliser les rôles/statuts auth** : déplacer les comparaisons en dur dans `apps/api/**/awana_auth_routes.py` vers la configuration (`config/base.yaml`).
2. **Centraliser les permissions mission** : consommer des listes de rôles configurées dans `apps/api/**/mission_routes.py` pour la création/publication/édition/lecture globale.
3. **Finaliser la paramétrisation des validations** : s'assurer que les statuts/types restants et les rôles validateurs sont tous lus depuis la config dans `apps/api/**/validation_routes.py`.
4. **Automatiser l'audit en CI** : exécuter `scripts/audit_hardcoded_values.py` sur chaque PR et échouer en cas de nouvelles occurrences.
5. **Préparer l'exposition mobile** : stabiliser un contrat API v1, ajouter pagination/filtrage systématiques, timeouts et rate limiting pour la résilience.

## Commandes utiles
```bash
# Rejouer l'audit local des valeurs en dur
python scripts/audit_hardcoded_values.py --markdown-output audit_reports/AUDIT_VALEURS_EN_DUR.md --stats-output audit_reports/stats.json
```

```bash
# Vérifier la progression IAM (constantes synchronisées)
python scripts/test_iam_constants_sync.py
```

## Points de suivi
- Mettre en place un dashboard CI pour publier les rapports d'audit générés.
- Tenir la documentation de configuration à jour après chaque externalisation.
