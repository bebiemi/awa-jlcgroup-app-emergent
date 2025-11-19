# Règles de Validation des Permissions IAM

## Vue d'ensemble

Le système IAM impose des validations strictes sur les permissions pour garantir l'intégrité et la cohérence des données.

## Règles de Validation

### 1. Champ `code` (Obligatoire)

Le champ `code` est **obligatoire** et doit respecter un pattern spécifique.

#### Pattern Accepté
- **Format** : `resource.action` ou `resource.subresource.action`
- **Caractères autorisés** : 
  - Lettres minuscules (a-z)
  - Chiffres (0-9)
  - Underscore (_)
  - Point (.) comme séparateur
- **Exception** : `*.*` pour les permissions wildcard (super admin)

#### Exemples Valides
```
missions.create
users.read
iam.profiles.manage
system.config.update
admin.dashboard.access
*.*
```

#### Exemples Invalides
```
missions_create          ❌ (pas de point)
Missions.Create          ❌ (majuscules)
missions-create          ❌ (tiret non autorisé)
missions.create.        ❌ (point final)
missions..create         ❌ (double point)
missions create          ❌ (espace)
```

### 2. Champ `resource` (Obligatoire)

#### Règles
- **Obligatoire**
- **Longueur** : 1-50 caractères
- **Caractères autorisés** : a-z, 0-9, underscore (_)
- **Normalisation** : Converti automatiquement en minuscules

#### Exemples Valides
```
missions
users
iam
system_config
entreprises
*
```

#### Exemples Invalides
```
iam.profiles            ❌ (point non autorisé)
My-Resource             ❌ (tiret et majuscules)
```

### 3. Champ `action` (Obligatoire)

#### Règles
- **Obligatoire**
- **Longueur** : 1-50 caractères
- **Caractères autorisés** : a-z, 0-9, underscore (_)
- **Normalisation** : Converti automatiquement en minuscules

#### Exemples Valides
```
create
read
update
delete
manage
read_own
convert_to_mission
*
```

#### Exemples Invalides
```
read-write              ❌ (tiret non autorisé)
Create                  ❌ (majuscule)
```

### 4. Unicité du Code

#### Règle
- Le champ `code` doit être **unique** dans toute la base de données
- Un index unique MongoDB garantit cette contrainte
- Tentative de créer une permission avec un code existant → Erreur 400

#### Message d'Erreur
```json
{
  "detail": "Permission with code 'missions.create' already exists"
}
```

### 5. Autres Champs

#### `name` (Obligatoire)
- **Longueur** : 1-200 caractères
- **Description** : Nom d'affichage de la permission

#### `description` (Optionnel)
- Description détaillée de la permission

#### `scope` (Optionnel)
- **Valeur par défaut** : `"organization"`
- **Longueur** : 1-50 caractères
- Détermine le périmètre d'application de la permission

#### `category` (Optionnel)
- **Valeur par défaut** : `"general"`
- Utilisé pour regrouper les permissions dans l'interface

#### `is_system` (Optionnel)
- **Valeur par défaut** : `false`
- Les permissions système ne peuvent pas être supprimées

## Protection au Niveau Base de Données

### Index Unique
Un index unique a été créé sur le champ `code` :

```python
db.permissions.create_index(
    [("code", ASCENDING)],
    unique=True,
    name="code_unique_idx"
)
```

### Vérification de Cohérence
Toutes les permissions existantes ont été nettoyées et validées :
- ✅ 217+ permissions valides
- ✅ Aucune permission sans code
- ✅ Aucun code en doublon

## Exemples d'Utilisation

### Création d'une Permission Valide

```bash
curl -X POST "http://localhost:8000/api/iam/permissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "besoins.validate",
    "name": "Valider les besoins",
    "description": "Permet de valider les besoins soumis par les entreprises",
    "resource": "besoins",
    "action": "validate",
    "category": "besoins"
  }'
```

**Réponse (201 Created):**
```json
{
  "id": "a1b2c3d4-...",
  "code": "besoins.validate",
  "name": "Valider les besoins",
  "description": "Permet de valider les besoins soumis par les entreprises",
  "resource": "besoins",
  "action": "validate",
  "scope": "organization",
  "is_system": false,
  "category": "besoins",
  "created_at": "2025-11-19T22:00:00Z",
  "updated_at": "2025-11-19T22:00:00Z"
}
```

### Erreurs Courantes

#### 1. Code Invalide
```json
{
  "detail": [
    {
      "type": "value_error",
      "msg": "Value error, Code invalide 'Invalid-Code'. Format attendu: 'resource.action' ou 'resource.subresource.action'"
    }
  ]
}
```

#### 2. Code en Doublon
```json
{
  "detail": "Permission with code 'besoins.validate' already exists"
}
```

#### 3. Champs Obligatoires Manquants
```json
{
  "detail": [
    {
      "type": "missing",
      "msg": "Field required",
      "input": {...},
      "loc": ["body", "code"]
    }
  ]
}
```

## Script de Vérification

Un script est disponible pour vérifier l'intégrité des permissions :

```bash
python3 /app/scripts/add_permission_code_index.py
```

Ce script :
1. Vérifie qu'aucune permission n'a de code vide ou null
2. Vérifie qu'il n'y a pas de doublons
3. Liste les index existants
4. Crée l'index unique si nécessaire
5. Valide la création de l'index

## Maintenance

### Nettoyage Périodique

Pour supprimer les permissions invalides (si elles existent) :

```python
from pymongo import MongoClient
import os

mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['auth_db']

# Supprimer les permissions sans code valide
result = db.permissions.delete_many({
    '$or': [
        {'code': {'$exists': False}}, 
        {'code': None}, 
        {'code': ''}
    ]
})

print(f"Permissions supprimées: {result.deleted_count}")
```

## Notes Importantes

1. **Toutes les permissions doivent avoir un code** - Aucune exception
2. **Les codes sont normalisés en minuscules** - Pas besoin de gérer les majuscules
3. **L'index unique garantit l'intégrité** - MongoDB rejette automatiquement les doublons
4. **Les validations Pydantic sont appliquées avant l'insertion** - Les données invalides sont rejetées immédiatement
5. **Le pattern est strictement appliqué** - Facilite la recherche et le filtrage des permissions

## Changelog

### 2025-11-19
- ✅ Ajout des validateurs Pydantic pour le champ `code`
- ✅ Création de l'index unique sur le champ `code`
- ✅ Nettoyage de 12 permissions dupliquées sans code
- ✅ Mise à jour de toutes les permissions par défaut pour inclure le champ `code`
- ✅ Documentation complète des règles de validation
