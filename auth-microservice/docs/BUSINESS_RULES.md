# Règles Métier - Système de Candidature

## Vue d'ensemble

Ce document décrit les règles métier dynamiques configurées dans la collection `business_rules` de MongoDB.
Ces règles régissent le processus de candidature aux missions.

---

## Architecture

### Localisation
- **Base de données**: `auth_db`
- **Collection**: `business_rules`
- **Service**: `ApplicationEligibilityService` (`/awana_auth/services/application_eligibility_service.py`)
- **Catégorie**: `application`

### Structure d'une Règle

```python
{
  "rule_id": str,           # Identifiant unique
  "category": str,          # Catégorie (ex: "application")
  "is_active": bool,        # Règle active/inactive
  "priority": int,          # Priorité d'exécution (100 = haute)
  "conditions": dict,       # Conditions de la règle
  "error_messages": dict,   # Messages d'erreur contextuels
  "description": str        # Description de la règle
}
```

---

## Règles Actives

### 1. Éligibilité par Rôle
**Rule ID**: `application_eligibility_roles`  
**Priorité**: 100 (Haute)

**Objectif**: Définir quels rôles peuvent postuler et à quels types de missions.

**Conditions**:
```json
{
  "allowed_roles": ["candidat", "postulant", "intérimaire", "interim"],
  "required_mission_status": ["open", "published"]
}
```

**Messages d'erreur**:
- `role_not_allowed`: "Rôle non autorisé à postuler"
- `mission_not_open`: "Mission non ouverte aux candidatures"

**Logique**:
1. Vérifie que l'utilisateur a au moins un rôle autorisé
2. Vérifie que la mission est dans un statut permettant les candidatures
3. Bloque si conditions non remplies

---

### 2. Restriction Contrat Intérimaire
**Rule ID**: `application_interim_contract_restriction`  
**Priorité**: 90 (Haute)

**Objectif**: Empêcher un intérimaire en mission de postuler à une nouvelle mission, sauf conditions spécifiques.

**Conditions**:
```json
{
  "days_before_contract_end": 5,
  "check_extensions": true,
  "check_amendments": true
}
```

**Messages d'erreur**:
- `contract_active`: "Vous êtes en mission. Vous pourrez postuler à partir de {days_before} jours avant la fin."
- `extension_pending`: "Une prolongation de contrat est en cours"
- `amendment_active`: "Un avenant est actif sur votre contrat"

**Logique**:
1. Cherche un contrat actif pour l'intérimaire
2. Si contrat trouvé, calcule jours restants
3. Bloque si > `days_before_contract_end` jours restants
4. Si ≤ 5 jours, vérifie extensions/avenants
5. Bloque si extension pending ou avenant actif
6. Autorise sinon

**Configuration Modifiable**:
- `days_before_contract_end`: Nombre de jours avant fin de contrat (défaut: 5)
- `check_extensions`: Vérifier les prolongations (défaut: true)
- `check_amendments`: Vérifier les avenants (défaut: true)

---

### 3. Exigence CV
**Rule ID**: `application_cv_requirement`  
**Priorité**: 80

**Objectif**: Définir si un CV est requis pour postuler.

**Conditions**:
```json
{
  "cv_required": true,
  "allow_upload": true
}
```

**Messages d'erreur**:
- `cv_missing`: "Un CV est requis pour postuler"

**Logique**:
1. Vérifie si l'utilisateur a un CV dans son profil
2. Retourne metadata `cv_required` et `allow_upload`
3. Le frontend gère l'upload si manquant

**Note**: Cette règle retourne des métadonnées mais ne bloque pas directement.
Le frontend utilise ces infos pour afficher InlineDocumentUpload.

---

### 4. Prévention Candidature Dupliquée
**Rule ID**: `application_duplicate_prevention`  
**Priorité**: 70

**Objectif**: Empêcher qu'un utilisateur postule plusieurs fois à la même mission.

**Messages d'erreur**:
- `already_applied`: "Vous avez déjà postulé à cette mission"

**Logique**:
1. Cherche une candidature existante (user_id + mission_id)
2. Bloque si trouvée
3. Retourne `existing_application_id` en metadata

---

### 5. Restriction Modification Candidature
**Rule ID**: `application_modification_restriction`  
**Priorité**: 60

**Objectif**: Définir quand une candidature peut être modifiée.

**Conditions**:
```json
{
  "allowed_statuses": ["submitted", "under_review"]
}
```

**Messages d'erreur**:
- `status_not_modifiable`: "Vous ne pouvez plus modifier cette candidature"

---

### 6. Restriction Annulation Candidature
**Rule ID**: `application_cancellation_restriction`  
**Priorité**: 50

**Objectif**: Définir quand une candidature peut être annulée.

**Conditions**:
```json
{
  "blocked_statuses": ["hired", "withdrawn", "contract_signed"]
}
```

**Messages d'erreur**:
- `cannot_cancel`: "Vous ne pouvez plus annuler cette candidature"

---

### 7. Restriction Suppression Candidature
**Rule ID**: `application_deletion_restriction`  
**Priorité**: 40

**Objectif**: Empêcher la suppression de candidatures (préférer annulation).

**Messages d'erreur**:
- `cannot_delete`: "La suppression n'est pas autorisée. Veuillez annuler la candidature."

---

## Modification des Règles

### Via Script

```bash
cd /app/auth-microservice
python3 scripts/seed_application_business_rules.py
```

### Via MongoDB

```javascript
db.business_rules.updateOne(
  { rule_id: "application_interim_contract_restriction" },
  { $set: { "conditions.days_before_contract_end": 7 } }
)
```

### Via API (Admin)

```bash
curl -X PATCH "http://localhost:8000/api/system-references/business-rules/{rule_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conditions": {"days_before_contract_end": 7}}'
```

---

## Ordre d'Exécution

Les règles sont exécutées par **priorité décroissante** (100 → 0):

1. **100**: Éligibilité par rôle → Bloque si rôle non autorisé
2. **90**: Restriction contrat intérimaire → Bloque si contrat actif
3. **80**: Exigence CV → Retourne metadata
4. **70**: Prévention dupliquée → Bloque si déjà postulé
5. **60-40**: Règles de modification/annulation

Si une règle bloque (`is_eligible = False`), l'exécution s'arrête et l'erreur est retournée.

---

## Tests

### Tests Unitaires

```bash
cd /app/auth-microservice
pytest tests/test_application_eligibility.py -v
```

### Tests Manuels

```bash
# Vérifier les règles actives
curl -X GET "http://localhost:8000/api/system-references/business-rules?category=application" \
  -H "Authorization: Bearer $TOKEN"

# Tester éligibilité (backend direct)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"nina","password":"azerty123456!!"}' | jq -r '.access_token')

curl -X POST "http://localhost:8000/api/missions/{mission_id}/apply" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cv_document_id":"xxx","additional_info":"Test"}'
```

---

## Exemples de Scénarios

### Scénario 1: Candidat avec CV postule
- ✅ Rôle autorisé (candidat)
- ✅ Mission ouverte
- ✅ Pas de candidature existante
- ✅ CV présent
- **Résultat**: Candidature acceptée

### Scénario 2: Intérimaire en mission (8 jours restants)
- ✅ Rôle autorisé (intérimaire)
- ✅ Mission ouverte
- ❌ Contrat actif avec 8 jours > 5 jours
- **Résultat**: Bloqué - "Vous pourrez postuler à partir de 5 jours avant la fin"

### Scénario 3: Intérimaire en mission (3 jours restants)
- ✅ Rôle autorisé (intérimaire)
- ✅ Mission ouverte
- ✅ Contrat actif mais ≤ 5 jours restants
- ✅ Pas d'extension/avenant
- **Résultat**: Candidature autorisée

---

## Maintenance

### Ajout d'une Nouvelle Règle

1. Définir la structure dans un script de seed
2. Ajouter la logique dans `ApplicationEligibilityService`
3. Tester avec tests unitaires
4. Documenter ici
5. Déployer

### Désactivation d'une Règle

```javascript
db.business_rules.updateOne(
  { rule_id: "application_cv_requirement" },
  { $set: { is_active: false } }
)
```

**Note**: Le cache du service sera rafraîchi après 5 minutes (TTL).

---

## Références

- Service: `/app/auth-microservice/awana_auth/services/application_eligibility_service.py`
- Scripts: `/app/auth-microservice/scripts/seed_application_business_rules.py`
- Tests: `/app/auth-microservice/tests/test_application_eligibility.py`
- Frontend: `/app/apps/web/src/features/missions/components/MissionDetailModal.tsx`
