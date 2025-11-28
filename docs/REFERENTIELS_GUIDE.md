# 📚 Guide des Référentiels - AWANA

**Version:** 2.0  
**Date:** 26 Novembre 2025

---

## 📋 Qu'est-ce qu'un Référentiel ?

Un **référentiel** est une **liste de valeurs prédéfinies** utilisée dans l'application (statuts, types, catégories, etc.).

**Avantages:**
- ✅ Données cohérentes dans toute l'application
- ✅ Facilite la traduction (multilingue)
- ✅ Modification centralisée sans toucher au code
- ✅ Stylisation uniforme (couleurs, icônes)

---

## 🗂️ Référentiels Disponibles

### 📊 Total: 18 référentiels

#### Utilisateurs & Profils (2)
- `user_statuses` - Statuts utilisateurs (active, pending, suspended, archived)
- `education_levels` - Niveaux d'études (BEP/CAP, Bac, Licence, Master, etc.)

#### Missions & Candidatures (3)
- `mission_statuses` - Statuts missions (draft, published, in_progress, completed)
- `application_statuses` - Statuts candidatures (submitted, shortlisted, accepted, rejected)
- `contract_types` - Types de contrat (CDI, CDD, intérim, freelance, stage)

#### Compétences & Expérience (2)
- `experience_levels` - Niveaux d'expérience (junior, intermediate, senior, expert)
- `business_sectors` - Secteurs d'activité (IT, construction, santé, finance, etc.)

#### Documents (1)
- `document_types` - Types de documents (CV, cover letter, ID card, diploma, contract, payslip)

#### Localisation (2)
- `countries` - Pays (Gabon, France, Cameroun, Côte d'Ivoire, Sénégal)
- `cities_gabon` - Villes du Gabon (Libreville, Port-Gentil, Franceville, etc.)

#### Langues (2)
- `languages` - Langues (français, anglais, espagnol, allemand, portugais)
- `language_levels` - Niveaux de langue (beginner, intermediate, advanced, fluent, native)

#### Émargements & Signatures ⭐ (2)
- `emargement_statuses` - Statuts émargements (draft, submitted, signed, validated, consolidated)
- `signature_types` - Types de signature (interim_emargement, client_emargement, contract)

#### Recrutement & Évaluation ⭐ (2)
- `evaluation_types` - Types d'évaluation (phone_interview, face_to_face, technical_test)
- `rating_levels` - Niveaux de notation (1-5 étoiles)

#### Système (2)
- `priority_levels` - Niveaux de priorité (low, medium, high, urgent)
- `notification_types` - Types de notification (info, success, warning, error, mission_new)

---

## 📁 Structure des Fichiers

```
/app/
├── config/
│   └── referentials_config.yaml    ← Configuration des référentiels
│
├── scripts/
│   └── init_referentials.py        ← Script d'installation
│
└── docs/
    └── REFERENTIELS_GUIDE.md       ← Ce document
```

---

## 🚀 Installation des Référentiels

### 1. Validation de la Configuration

**Avant toute modification, toujours valider:**

```bash
cd /app
python3 scripts/init_referentials.py --validate
```

**Sortie:**
```
🔍 VALIDATION DE LA CONFIGURATION
================================================================================

📦 Validation de 'user_statuses'...
   ✅ 5 items trouvés

📦 Validation de 'mission_statuses'...
   ✅ 8 items trouvés

...

✅ Configuration valide!
```

### 2. Mode Simulation (Dry-Run)

**Tester sans modifier la base:**

```bash
python3 scripts/init_referentials.py --dry-run
```

**Sortie:**
```
🔄 INITIALISATION DES RÉFÉRENTIELS (jlc_db)
   MODE SIMULATION (DRY-RUN)
================================================================================

📦 user_statuses
   Collection: referentials
   Version: 1.0
   Items: 5
   ✅ Créé (simulation)

📊 RÉSUMÉ
Créés: 18
Mis à jour: 0
```

### 3. Installation Réelle

**Appliquer les modifications:**

```bash
python3 scripts/init_referentials.py
```

**Sortie:**
```
🔄 INITIALISATION DES RÉFÉRENTIELS (jlc_db)
   MODE PRODUCTION
================================================================================

📦 user_statuses
   ✅ Créé

📦 mission_statuses
   ✅ Mis à jour

...

✅ 10 référentiel(s) initialisé(s) avec succès!
```

### 4. Nettoyer les Référentiels Obsolètes

**Supprimer les référentiels qui ne sont plus dans la config:**

```bash
python3 scripts/init_referentials.py --clean
```

### 5. Options Combinées

```bash
# Simulation avec nettoyage
python3 scripts/init_referentials.py --dry-run --clean

# Config personnalisée
python3 scripts/init_referentials.py --config /path/to/custom.yaml

# Validation seule
python3 scripts/init_referentials.py --validate
```

---

## 📝 Format YAML d'un Référentiel

### Structure de Base

```yaml
nom_du_referentiel:
  collection: "referentials"       # Collection MongoDB
  key: "nom_du_referentiel"        # Clé unique
  version: "1.0"                   # Version (optionnel)
  items:
    - code: "code_unique"          # ✅ OBLIGATOIRE
      label:                       # ✅ OBLIGATOIRE
        fr: "Libellé français"     # ✅ OBLIGATOIRE
        en: "English label"        # Recommandé
      description: "Description"   # Optionnel
      color: "green"               # Optionnel (pour UI)
      icon: "🎯"                   # Optionnel (emoji ou classe CSS)
      order: 1                     # Optionnel (ordre d'affichage)
```

### Exemple Complet

```yaml
# Statuts de mission
mission_statuses:
  collection: "referentials"
  key: "mission_statuses"
  version: "1.0"
  items:
    - code: "draft"
      label:
        fr: "Brouillon"
        en: "Draft"
      color: "gray"
      description: "Mission en cours de création"
      order: 1
      
    - code: "published"
      label:
        fr: "Publiée"
        en: "Published"
      color: "green"
      description: "Mission publiée et visible"
      order: 2
```

---

## 🔧 Ajouter un Nouveau Référentiel

### Étape 1: Éditer le fichier YAML

```bash
nano /app/config/referentials_config.yaml
```

### Étape 2: Ajouter votre référentiel

```yaml
# À la fin du fichier
mon_nouveau_referentiel:
  collection: "referentials"
  key: "mon_nouveau_referentiel"
  version: "1.0"
  items:
    - code: "valeur1"
      label:
        fr: "Valeur 1"
        en: "Value 1"
      order: 1
      
    - code: "valeur2"
      label:
        fr: "Valeur 2"
        en: "Value 2"
      order: 2
```

### Étape 3: Valider

```bash
python3 scripts/init_referentials.py --validate
```

### Étape 4: Appliquer

```bash
python3 scripts/init_referentials.py
```

---

## 📡 Utilisation dans l'API

### Backend (FastAPI)

```python
from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_referential(db: AsyncIOMotorDatabase, key: str):
    """Récupérer un référentiel"""
    ref = await db.referentials.find_one({"key": key}, {"_id": 0})
    return ref

# Usage
ref = await get_referential(db, "mission_statuses")
items = ref["items"]
```

### Endpoint API

```python
@app.get("/api/referentials/{key}")
async def get_referential_endpoint(
    key: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Récupérer un référentiel par sa clé"""
    ref = await db.referentials.find_one({"key": key}, {"_id": 0})
    
    if not ref:
        raise HTTPException(status_code=404, detail=f"Référentiel '{key}' non trouvé")
    
    return ref
```

### Frontend (React)

```typescript
// Hook personnalisé
const useReferential = (key: string) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch(`${API_URL}/api/referentials/${key}`)
      .then(res => res.json())
      .then(data => {
        setItems(data.items);
        setLoading(false);
      });
  }, [key]);
  
  return { items, loading };
};

// Usage dans un composant
const MissionForm = () => {
  const { items: statuses } = useReferential('mission_statuses');
  
  return (
    <select>
      {statuses.map(status => (
        <option key={status.code} value={status.code}>
          {status.label.fr}
        </option>
      ))}
    </select>
  );
};
```

---

## 🔍 Requêtes MongoDB Utiles

### Lister tous les référentiels

```javascript
db.referentials.find({}, {key: 1, version: 1, "items": {$size: "$items"}})
```

### Récupérer un référentiel

```javascript
db.referentials.findOne({key: "mission_statuses"})
```

### Compter les items d'un référentiel

```javascript
db.referentials.aggregate([
  {$match: {key: "mission_statuses"}},
  {$project: {count: {$size: "$items"}}}
])
```

### Chercher dans les labels

```javascript
db.referentials.find({
  "items.label.fr": {$regex: "publié", $options: "i"}
})
```

---

## 🎨 Bonnes Pratiques

### ✅ À FAIRE

1. **Toujours valider avant d'appliquer**
   ```bash
   python3 scripts/init_referentials.py --validate
   ```

2. **Utiliser le dry-run pour tester**
   ```bash
   python3 scripts/init_referentials.py --dry-run
   ```

3. **Versionner les modifications**
   - Incrémenter la version quand vous modifiez un référentiel
   - `version: "1.0"` → `version: "1.1"`

4. **Codes en snake_case**
   - ✅ `in_progress`
   - ❌ `inProgress` ou `InProgress`

5. **Labels multilingues**
   - Toujours fournir au minimum `fr` et `en`

6. **Ordre logique**
   - Utiliser le champ `order` pour contrôler l'affichage

### ❌ À ÉVITER

1. **Modifier directement la base MongoDB**
   - ❌ Toujours passer par le script d'installation

2. **Codes dupliqués**
   - ❌ Deux items avec le même `code` dans un référentiel

3. **Labels non traduits**
   - ❌ Oublier de mettre `fr` et `en`

4. **Supprimer des items utilisés**
   - ⚠️ Vérifier d'abord que le code n'est plus utilisé dans l'application

---

## 🔄 Workflow de Modification

```
1. Éditer referentials_config.yaml
   ↓
2. Valider
   python3 scripts/init_referentials.py --validate
   ↓
3. Tester en simulation
   python3 scripts/init_referentials.py --dry-run
   ↓
4. Appliquer
   python3 scripts/init_referentials.py
   ↓
5. Vérifier
   curl http://localhost:8001/api/referentials/{key}
```

---

## 🐛 Dépannage

### Erreur: "Fichier de configuration non trouvé"

```bash
# Vérifier l'emplacement
ls -la /app/config/referentials_config.yaml

# Utiliser un chemin absolu
python3 scripts/init_referentials.py --config /app/config/referentials_config.yaml
```

### Erreur: "Codes dupliqués"

```
❌ 'mission_statuses': codes dupliqués: {'draft'}
```

**Solution:** Vérifiez que chaque `code` est unique dans le référentiel

### Erreur: "Label doit contenir 'fr'"

```
❌ Item 'draft': label doit contenir 'fr'
```

**Solution:** Ajoutez le label français
```yaml
label:
  fr: "Brouillon"  # ← Ajouter ceci
  en: "Draft"
```

### Index déjà existant

```
ℹ️ Index déjà existants
```

**C'est normal** - Les index ne sont créés qu'une fois

---

## 📊 Statistiques Actuelles

```bash
# Compter tous les référentiels
python3 -c "
import yaml
with open('/app/config/referentials_config.yaml') as f:
    config = yaml.safe_load(f)
    refs = [k for k in config.keys() if not k.startswith('_')]
    print(f'{len(refs)} référentiels configurés')
"
```

**Sortie actuelle:** `18 référentiels configurés`

---

## 📚 Documents Connexes

- Configuration: `/app/config/referentials_config.yaml`
- Script: `/app/scripts/init_referentials.py`
- Bundles: [BUNDLES_MATRIX_COMPLETE.md](BUNDLES_MATRIX_COMPLETE.md)

---

*Dernière mise à jour: 26 Novembre 2025*
