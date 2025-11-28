# 📚 Script d'Installation des Référentiels - Résumé

## ✅ Ce qui a été fait

**Script d'installation des référentiels amélioré** avec validation, simulation et gestion complète.

---

## 📄 Fichiers créés/modifiés

### 1. Script d'installation (amélioré)
**[scripts/init_referentials.py](scripts/init_referentials.py)** - Version 2.0

**Améliorations apportées:**
- ✅ Mode `--validate` : Validation complète de la config sans toucher à la base
- ✅ Mode `--dry-run` : Simulation sans modification (test avant application)
- ✅ Validation automatique des données (codes uniques, labels obligatoires)
- ✅ Meilleure gestion des erreurs avec messages détaillés
- ✅ Compteurs et statistiques améliorés
- ✅ Index MongoDB automatique sur `key` et `updated_at`

### 2. Configuration YAML enrichie
**[config/referentials_config.yaml](config/referentials_config.yaml)**

**Nouveaux référentiels ajoutés (6):**
- ⭐ `emargement_statuses` - 8 statuts (draft, submitted, signed, validated, consolidated, etc.)
- ⭐ `signature_types` - 4 types (interim_emargement, client_emargement, contract, document_legal)
- ⭐ `evaluation_types` - 5 types (phone_interview, face_to_face, technical_test, etc.)
- ⭐ `rating_levels` - 5 niveaux (1-5 étoiles avec couleurs et emojis)
- ⭐ `priority_levels` - 4 niveaux (low, medium, high, urgent)
- ⭐ `notification_types` - 7 types (info, success, warning, error, mission_new, etc.)

**Total:** 18 référentiels

### 3. Documentation complète
**[docs/REFERENTIELS_GUIDE.md](docs/REFERENTIELS_GUIDE.md)** - 15KB

---

## 🚀 Utilisation

### Validation seule (recommandé avant toute modification)
```bash
cd /app
python3 scripts/init_referentials.py --validate
```

**Sortie:**
```
✅ 18 référentiel(s) trouvé(s)
🔍 VALIDATION DE LA CONFIGURATION
📦 Validation de 'user_statuses'... ✅ 5 items trouvés
...
✅ Configuration valide!
```

### Mode simulation (test sans modifier)
```bash
python3 scripts/init_referentials.py --dry-run
```

**Sortie:**
```
MODE SIMULATION (DRY-RUN)
📦 emargement_statuses
   ✅ Créé (simulation)
...
✅ 6 référentiel(s) initialisé(s) avec succès!
```

### Installation réelle
```bash
python3 scripts/init_referentials.py
```

### Nettoyage (supprimer référentiels obsolètes)
```bash
python3 scripts/init_referentials.py --clean
```

### Options combinées
```bash
# Simulation + nettoyage
python3 scripts/init_referentials.py --dry-run --clean

# Config personnalisée
python3 scripts/init_referentials.py --config /path/to/custom.yaml
```

---

## 📊 Référentiels Disponibles (18 total)

### Utilisateurs & Profils
- `user_statuses` (5 items)
- `education_levels` (7 items)

### Missions & Candidatures
- `mission_statuses` (8 items)
- `application_statuses` (7 items)
- `contract_types` (6 items)

### Compétences & Expérience
- `experience_levels` (4 items)
- `business_sectors` (10 items)

### Documents
- `document_types` (6 items)

### Localisation
- `countries` (5 items)
- `cities_gabon` (6 items)

### Langues
- `languages` (5 items)
- `language_levels` (5 items)

### Émargements & Signatures ⭐ NOUVEAU
- `emargement_statuses` (8 items)
- `signature_types` (4 items)

### Recrutement & Évaluation ⭐ NOUVEAU
- `evaluation_types` (5 items)
- `rating_levels` (5 items)

### Système ⭐ NOUVEAU
- `priority_levels` (4 items)
- `notification_types` (7 items)

---

## 🎯 Référentiel Émargements - Détails

### `emargement_statuses`

```yaml
draft            → Brouillon (gray)
submitted_interim → Soumis par l'intérimaire (blue)
signed_interim   → Signé intérimaire (purple)
pending_client   → En attente client (yellow)
validated        → Validé (green)
rejected         → Rejeté (red)
consolidated     → Consolidé (green)
archived         → Archivé (gray)
```

**Workflow:**
```
draft → submitted_interim → signed_interim → pending_client → validated → consolidated → archived
```

---

## 📝 Format YAML

### Structure de Base

```yaml
nom_referentiel:
  collection: "referentials"      # Collection MongoDB
  key: "nom_referentiel"          # Clé unique
  version: "1.0"                  # Version
  items:
    - code: "code_unique"         # ✅ OBLIGATOIRE
      label:                      # ✅ OBLIGATOIRE
        fr: "Libellé français"    # ✅ OBLIGATOIRE
        en: "English label"
      description: "..."          # Optionnel
      color: "green"              # Optionnel (UI)
      icon: "🎯"                  # Optionnel (emoji)
      order: 1                    # Optionnel (tri)
```

### Exemple Complet

```yaml
emargement_statuses:
  collection: "referentials"
  key: "emargement_statuses"
  version: "1.0"
  items:
    - code: "validated"
      label:
        fr: "Validé"
        en: "Validated"
      color: "green"
      description: "Validé et signé par le client"
      order: 5
```

---

## 🔧 Ajouter un Nouveau Référentiel

### 1. Éditer la config YAML
```bash
nano /app/config/referentials_config.yaml
```

### 2. Ajouter votre référentiel
```yaml
mon_referentiel:
  collection: "referentials"
  key: "mon_referentiel"
  version: "1.0"
  items:
    - code: "value1"
      label:
        fr: "Valeur 1"
        en: "Value 1"
      order: 1
```

### 3. Valider
```bash
python3 scripts/init_referentials.py --validate
```

### 4. Tester (simulation)
```bash
python3 scripts/init_referentials.py --dry-run
```

### 5. Appliquer
```bash
python3 scripts/init_referentials.py
```

---

## 📡 Utilisation dans l'Application

### Backend API

```python
@app.get("/api/referentials/{key}")
async def get_referential(key: str, db = Depends(get_database)):
    ref = await db.referentials.find_one({"key": key}, {"_id": 0})
    if not ref:
        raise HTTPException(404, f"Référentiel '{key}' non trouvé")
    return ref
```

**Test:**
```bash
curl http://localhost:8001/api/referentials/emargement_statuses
```

### Frontend React

```typescript
// Hook personnalisé
const useReferential = (key: string) => {
  const [items, setItems] = useState([]);
  
  useEffect(() => {
    fetch(`${API_URL}/api/referentials/${key}`)
      .then(res => res.json())
      .then(data => setItems(data.items));
  }, [key]);
  
  return items;
};

// Usage
const EmargementForm = () => {
  const statuses = useReferential('emargement_statuses');
  
  return (
    <select>
      {statuses.map(s => (
        <option key={s.code} value={s.code}>
          {s.label.fr}
        </option>
      ))}
    </select>
  );
};
```

---

## ✅ Validation Automatique

Le script valide automatiquement:

- ✅ Champ `code` présent et unique
- ✅ Champ `label` présent avec au moins `fr`
- ✅ Pas de codes dupliqués dans un référentiel
- ✅ Structure YAML correcte

**Exemple d'erreur détectée:**
```
❌ 'emargement_statuses': codes dupliqués: {'draft'}
❌ Item 'validated': label doit contenir 'fr'
```

---

## 🔍 Requêtes MongoDB

### Lister tous les référentiels
```javascript
db.referentials.find({}, {key: 1, version: 1})
```

### Récupérer un référentiel
```javascript
db.referentials.findOne({key: "emargement_statuses"})
```

### Compter les items
```javascript
db.referentials.aggregate([
  {$match: {key: "emargement_statuses"}},
  {$project: {count: {$size: "$items"}}}
])
```

---

## 🎨 Bonnes Pratiques

### ✅ À FAIRE
1. Toujours valider avant d'appliquer
2. Utiliser dry-run pour tester
3. Versionner les modifications (`1.0` → `1.1`)
4. Codes en `snake_case`
5. Labels multilingues (fr + en minimum)

### ❌ À ÉVITER
1. Modifier directement MongoDB
2. Codes dupliqués
3. Oublier les traductions
4. Supprimer des items encore utilisés

---

## 📈 Statistiques

| Métrique | Valeur |
|----------|--------|
| **Total référentiels** | 18 |
| **Nouveaux référentiels** | 6 ⭐ |
| **Total items** | ~100 |
| **Langues supportées** | 2 (fr, en) |
| **Collections MongoDB** | 1 (referentials) |

---

## 🔄 Workflow Recommandé

```
1. Éditer /app/config/referentials_config.yaml
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
5. Vérifier via API
   curl http://localhost:8001/api/referentials/{key}
```

---

## 📚 Documentation Complète

👉 **[docs/REFERENTIELS_GUIDE.md](docs/REFERENTIELS_GUIDE.md)** - Guide détaillé (15KB)

**Contient:**
- Liste complète des 18 référentiels
- Format YAML détaillé
- Exemples d'utilisation API/Frontend
- Requêtes MongoDB
- Dépannage
- Bonnes pratiques

---

*Créé le: 26 Novembre 2025*  
*Version: 2.0*
