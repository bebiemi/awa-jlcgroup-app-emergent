# 📚 Catégories de Référentiels Disponibles

## Vue d'ensemble

L'application JLC dispose actuellement de **9 catégories de référentiels** dynamiques, soit un total de **43 référentiels** configurables.

---

## 📋 Liste des Catégories

### 1. **mission_statuses** - Statuts de Mission
**Nombre**: 5 référentiels  
**Type**: Système (is_system: true)  
**Codes disponibles**:
- `draft` - Brouillon
- `published` - Publiée
- `in_progress` - En cours
- `completed` - Terminée
- `cancelled` - Annulée

**Métadonnées**:
- `color` - Couleur d'affichage
- `icon` - Icône associée
- `is_visible_to_candidates` - Visible pour les candidats
- `can_receive_applications` - Peut recevoir des candidatures

---

### 2. **application_statuses** - Statuts de Candidature
**Nombre**: 10 référentiels  
**Type**: Système (is_system: true)  
**Codes disponibles**:
- `pending` - En attente
- `interview_scheduled` - Entretien programmé
- `interview_completed` - Entretien effectué
- `selected` - Sélectionné
- `medical_pending` - Visite médicale en attente
- `medical_approved` - Visite médicale validée
- `medical_rejected` - Visite médicale refusée
- `contract_pending` - Contrat en attente
- `contract_signed` - Contrat signé
- `rejected` - Refusée

**Métadonnées importantes**:
- `color` - Couleur d'affichage
- `icon` - Icône associée
- `next_possible_statuses` - Liste des transitions autorisées
- `requires_action_from` - Qui doit agir (company, agency)
- `requires_document_upload` - Document requis
- `is_final_status` - Statut final (pas de transition)

---

### 3. **contract_types** - Types de Contrat
**Nombre**: 4 référentiels  
**Type**: Non-système (modifiable)  
**Codes disponibles**:
- `cdi` - CDI (Contrat à Durée Indéterminée)
- `cdd` - CDD (Contrat à Durée Déterminée)
- `interim` - Intérim
- `stage` - Stage

**Métadonnées**:
- `color` - Couleur d'affichage
- `icon` - Icône associée

---

### 4. **medical_aptitudes** - Aptitudes Médicales
**Nombre**: 3 référentiels  
**Type**: Système (is_system: true)  
**Codes disponibles**:
- `apte` - Apte
- `apte_avec_reserves` - Apte avec réserves
- `inapte` - Inapte

**Métadonnées importantes**:
- `color` - Couleur d'affichage
- `icon` - Icône associée
- `allows_contract` - Autorise la signature du contrat
- `requires_note` - Nécessite une note explicative

---

### 5. **roles** - Rôles Utilisateurs
**Nombre**: 6 référentiels  
**Type**: Système (is_system: true)  
**Codes disponibles**:
- `admin` - Administrateur
- `super_admin` - Super Administrateur
- `company` - Entreprise
- `agency` - Agence
- `commercial` - Commercial
- `interim` - Intérimaire

**Métadonnées**:
- `color` - Couleur d'affichage
- `icon` - Icône associée
- `permissions` - Liste des permissions

---

### 6. **skills** - Compétences
**Nombre**: 5 référentiels (extensible)  
**Type**: Non-système (modifiable)  
**Codes disponibles**:
- `python` - Python
- `javascript` - JavaScript
- `react` - React
- `communication` - Communication
- `leadership` - Leadership

**Métadonnées**:
- `color` - Couleur d'affichage
- `icon` - Icône associée
- `category_type` - Type (tech, soft)

---

### 7. **countries** - Pays
**Nombre**: 5 référentiels (extensible)  
**Type**: Non-système (modifiable)  
**Codes disponibles**:
- `GA` - Gabon
- `FR` - France
- `CI` - Côte d'Ivoire
- `SN` - Sénégal
- `CM` - Cameroun

**Métadonnées**:
- `dial_code` - Code téléphonique (+241)
- `flag` - Emoji drapeau (🇬🇦)
- `currency` - Devise (XAF, EUR)

---

### 8. **document_types** - Types de Documents
**Nombre**: 5 référentiels  
**Type**: Mixte (certains système, d'autres modifiables)  
**Codes disponibles**:
- `cv` - CV (système)
- `cover_letter` - Lettre de motivation
- `medical_certificate` - Certificat médical (système)
- `contract` - Contrat (système)
- `id_card` - Carte d'identité

**Métadonnées importantes**:
- `color` - Couleur d'affichage
- `icon` - Icône associée
- `required_for` - Requis pour quelle étape (application, medical_check, contract_signing)
- `max_size_mb` - Taille maximale (en MB)
- `allowed_formats` - Formats autorisés (pdf, doc, jpg, etc.)

---

### 9. **Futures Catégories** (À implémenter)

Catégories suggérées pour extension future :
- `regions` - Régions géographiques (avec parent_id vers countries)
- `cities` - Villes (avec parent_id vers regions)
- `job_categories` - Catégories d'emploi
- `experience_levels` - Niveaux d'expérience
- `education_levels` - Niveaux d'études
- `notification_types` - Types de notifications
- `statuses` - Statuts génériques (utilisateurs, entreprises, etc.)

---

## 🔧 Utilisation dans le Code

### Backend - Validation

```python
from awana_auth.core.cache import reference_cache, get_cache_key

# Valider un statut
if not await validate_status(db, "application_statuses", new_status):
    raise HTTPException(status_code=400, detail="Statut invalide")

# Récupérer les métadonnées
metadata = await get_status_metadata(db, "application_statuses", current_status)
allowed_transitions = metadata.get("next_possible_statuses", [])
```

### Frontend - Affichage

```typescript
// Hook pour charger les référentiels
import { useReferences } from '@/hooks/useReferences'

const { options, getLabel, getMetadata } = useReferences('contract_types')

// Composant Select dynamique
<ReferenceSelect
  category="contract_types"
  value={formData.contract_type}
  onChange={(value) => setFormData({ ...formData, contract_type: value })}
  label="Type de contrat"
  required
/>

// Badge de statut dynamique
<StatusBadge
  category="application_statuses"
  status={app.status}
  showIcon
/>
```

---

## 📊 Statistiques

**Total des référentiels**: 43  
**Catégories système**: 5 (mission_statuses, application_statuses, medical_aptitudes, roles, document_types)  
**Catégories modifiables**: 4 (contract_types, skills, countries, document_types)  
**Référentiels avec transitions**: 1 (application_statuses avec next_possible_statuses)  
**Référentiels avec validation conditionnelle**: 2 (application_statuses, medical_aptitudes)

---

## 🚀 Ajout d'une Nouvelle Catégorie

### Étape 1: Créer le script de seed

```python
# /app/auth-microservice/scripts/seed_my_category.py
await db.system_references.insert_many([
    {
        "id": str(uuid.uuid4()),
        "category": "my_category",
        "code": "value1",
        "label_fr": "Valeur 1",
        "label_en": "Value 1",
        "order": 1,
        "metadata": {},
        "is_active": True,
        "is_system": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
])
```

### Étape 2: Ajouter dans ReferencesManagementPage

```typescript
const categories = [
  // ... existantes
  { value: 'my_category', label: 'Ma Catégorie' },
]
```

### Étape 3: Créer un hook spécialisé (optionnel)

```typescript
export const useMyCategory = () => useReferences('my_category')
```

---

## 💡 Bonnes Pratiques

1. **Utilisez des codes en minuscules avec underscores** (`medical_approved`, pas `Medical-Approved`)
2. **Définissez toujours un order** pour contrôler l'affichage
3. **Utilisez is_system: true** pour les valeurs critiques
4. **Documentez les métadonnées** dans le script de seed
5. **Testez les transitions** avant de déployer
6. **Invalidez le cache** après modification

---

## 🔗 Fichiers Associés

- **Modèles**: `/app/auth-microservice/awana_auth/core/reference_models.py`
- **Routes API**: `/app/auth-microservice/configuration_routes.py`
- **Cache**: `/app/auth-microservice/awana_auth/core/cache.py`
- **Scripts seed**: `/app/auth-microservice/scripts/seed_*.py`
- **Frontend API**: `/app/apps/web/src/features/admin/api/configurationApi.ts`
- **Hooks**: `/app/apps/web/src/hooks/useReferences.ts`
- **Composants**: `/app/apps/web/src/components/ReferenceSelect.tsx`, `StatusBadge.tsx`
- **Page admin**: `/app/apps/web/src/features/admin/pages/ReferencesManagementPage.tsx`
