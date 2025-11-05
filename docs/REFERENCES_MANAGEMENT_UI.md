# Interface de Gestion des Référentiels

**Date:** 5 Novembre 2025  
**Route:** `/admin/references`  
**Permissions:** Admin, Super Admin

## Vue d'ensemble

L'interface de gestion des référentiels permet aux administrateurs de créer, modifier et gérer toutes les valeurs de référence utilisées dans l'application JLC.

## Fonctionnalités

### 1. Sélection de catégorie

**16 catégories disponibles:**

| Catégorie | Icône | Description | Nombre |
|-----------|-------|-------------|--------|
| `roles` | 👥 | Rôles utilisateurs (admin, interim, etc.) | 7 |
| `user_statuses` | 👤 | Statuts utilisateurs (active, pending, etc.) | 1 |
| `mission_statuses` | 💼 | Statuts de mission | 7 |
| `application_statuses` | 📋 | Statuts de candidature | 14 |
| `validation_types` | ✓ | Types de validation | 3 |
| `validation_statuses` | ✅ | Statuts de validation | 3 |
| `contract_types` | 📝 | Types de contrats | 4 |
| `document_types` | 📄 | Types de documents | 7 |
| `experience_levels` | 📊 | Niveaux d'expérience | 5 |
| `education_levels` | 🎓 | Niveaux d'éducation | 5 |
| `skill_categories` | 🎯 | Catégories de compétences | 4 |
| `skills` | ⚡ | Compétences spécifiques | 5 |
| `work_schedules` | 🕐 | Types d'horaires | 4 |
| `salary_ranges` | 💰 | Fourchettes salariales | 5 |
| `countries` | 🌍 | Pays | 5 |
| `medical_aptitudes` | 🏥 | Aptitudes médicales | 3 |

**Total:** 82 références actives

### 2. Statistiques par catégorie

Pour chaque catégorie sélectionnée, 4 indicateurs sont affichés :

- **Total** - Nombre total de références dans la catégorie
- **Actifs** - Références actives (utilisables)
- **Inactifs** - Références désactivées
- **Système** - Références système (non supprimables)

### 3. Tableau de références

**Colonnes affichées:**

| Colonne | Description |
|---------|-------------|
| **Code** | Identifiant unique (code technique) + badge "Système" si applicable |
| **Label FR** | Libellé en français (affiché aux utilisateurs) |
| **Label EN** | Libellé en anglais (pour i18n) |
| **Description** | Description détaillée (tronquée, tooltip sur hover) |
| **Ordre** | Ordre d'affichage (badge circulaire) |
| **Métadonnées** | Affichage visuel des métadonnées (couleur, icône, etc.) |
| **Statut** | Badge Actif/Inactif |
| **Actions** | Boutons Modifier et Supprimer |

### 4. Affichage des métadonnées

Les métadonnées sont affichées visuellement selon leur type :

- **Couleur** (`color`) - Pastille colorée avec la couleur hex
- **Icône** (`icon`) - Badge violet avec emoji et nom de l'icône
- **Années** (`years`) - Badge vert avec icône calendrier
- **Heures** (`hours`) - Badge bleu avec icône horloge

**Exemple pour `experience_levels`:**
```
senior: 🎨 star | 📅 8-15 | Couleur: #F59E0B
```

### 5. Création de référence

**Formulaire de création:**

```
Code *              : [text] (unique, non modifiable après création)
Label FR *          : [text] (obligatoire)
Label EN            : [text] (optionnel, pour i18n)
Description         : [textarea] (optionnel, aide contextuelle)
Ordre d'affichage   : [number] (défaut: 0)
☑ Actif            : [checkbox] (défaut: coché)
```

**Validations:**
- Code requis et unique dans la catégorie
- Label FR requis
- Code non modifiable après création (disabled en mode édition)

### 6. Modification de référence

**Restrictions:**
- Le code ne peut pas être modifié
- Les références système peuvent être modifiées mais pas supprimées
- Tous les autres champs sont éditables

### 7. Suppression de référence

**Règles:**
- ✅ Les références non-système peuvent être supprimées
- ❌ Les références système ne peuvent PAS être supprimées
- ⚠️ Confirmation requise avant suppression

## Utilisation

### Accès à l'interface

1. Se connecter en tant qu'Admin ou Super Admin
2. Naviguer: **Paramètres** → **Référentiels**
3. URL: `/admin/references`

### Créer une nouvelle référence

1. Sélectionner la catégorie (ex: `skills`)
2. Cliquer sur **Nouveau** (bouton en haut à droite)
3. Remplir le formulaire:
   ```
   Code: devops
   Label FR: DevOps
   Label EN: DevOps
   Description: Compétences DevOps (CI/CD, Docker, Kubernetes)
   Ordre: 10
   ☑ Actif
   ```
4. Cliquer **Créer**
5. La nouvelle référence apparaît dans le tableau

### Modifier une référence

1. Trouver la référence dans le tableau
2. Cliquer sur l'icône **crayon** (Modifier)
3. Modifier les champs souhaités
4. Cliquer **Modifier**

### Désactiver une référence

Au lieu de supprimer, il est recommandé de désactiver :

1. Cliquer sur **Modifier**
2. Décocher **Actif**
3. Sauvegarder

**Avantage:** Les données existantes restent cohérentes

### Supprimer une référence

⚠️ **Attention:** Suppression définitive

1. Cliquer sur l'icône **poubelle** (Supprimer)
2. Confirmer la suppression
3. La référence est supprimée de la base de données

**Note:** Les références système ne peuvent pas être supprimées

## Exemples d'usage

### Ajouter un nouveau niveau d'expérience

**Cas:** Besoin d'un niveau "Lead" entre Senior et Expert

```
Catégorie: experience_levels
Code: lead
Label FR: Lead
Label EN: Lead
Description: 12-18 ans d'expérience avec responsabilités de lead technique
Ordre: 4.5
Métadonnées: {
  "color": "#DC2626",
  "icon": "trophy",
  "years": "12-18"
}
```

### Ajouter une nouvelle compétence

**Cas:** Ajouter "Docker" dans les compétences techniques

```
Catégorie: skills
Code: docker
Label FR: Docker
Label EN: Docker
Description: Containerisation avec Docker
Ordre: 20
```

### Ajouter un nouveau type de document

**Cas:** Besoin de "Attestation de travail"

```
Catégorie: document_types
Code: work_certificate
Label FR: Attestation de travail
Label EN: Work Certificate
Description: Attestation d'emploi délivrée par l'employeur
Ordre: 8
Métadonnées: {
  "color": "#10B981",
  "icon": "document-check"
}
```

### Gérer les fourchettes salariales

**Cas:** Ajuster les tranches salariales

```
Catégorie: salary_ranges

Modifier range_3:
Label FR: 1M - 1.5M FCFA
Metadata: { "min": 1000000, "max": 1500000 }

Ajouter range_6:
Code: range_6
Label FR: 5M - 10M FCFA
Ordre: 6
Metadata: { "min": 5000000, "max": 10000000 }
```

## Design Pattern

### Grid Layout pour catégories

```tsx
// Disposition en grille responsive
grid-cols-2 md:grid-cols-4 lg:grid-cols-8

// Effet de sélection
bg-jlc-purple-600 text-white shadow-lg scale-105
```

### Tableau amélioré

- **Hover effect** sur les lignes (`hover:bg-gray-50`)
- **Code en monospace** avec background gris
- **Badges** pour statuts et métadonnées
- **Icônes interactives** avec hover effects

### État vide (Empty State)

Si aucune référence n'existe :
- Grande icône 📭
- Message explicatif
- Bouton CTA "Créer le premier référentiel"

## API Backend

### Endpoints utilisés

```http
GET /api/auth/config/references?category={category}
# Liste les références d'une catégorie

POST /api/auth/config/references
# Crée une nouvelle référence
Body: {
  "category": "skills",
  "code": "docker",
  "label_fr": "Docker",
  "label_en": "Docker",
  "description": "...",
  "order": 20,
  "is_active": true,
  "metadata": {}
}

PATCH /api/auth/config/references/{id}
# Modifie une référence existante
Body: {
  "label_fr": "Docker (Containerisation)",
  "description": "...",
  "order": 21
}

DELETE /api/auth/config/references/{id}
# Supprime une référence (si non-système)
```

### RTK Query Hooks

```typescript
// Hook de lecture
const { data, isLoading } = useGetReferencesQuery({
  category: 'skills',
  is_active: undefined
})

// Hook de création
const [createReference] = useCreateReferenceMutation()
await createReference({
  category: 'skills',
  code: 'docker',
  ...
}).unwrap()

// Hook de mise à jour
const [updateReference] = useUpdateReferenceMutation()
await updateReference({
  id: 'ref_id',
  data: { label_fr: 'New label' }
}).unwrap()

// Hook de suppression
const [deleteReference] = useDeleteReferenceMutation()
await deleteReference(ref_id).unwrap()
```

## Intégration avec le système de versioning

### Traçabilité

Chaque modification de référence devrait idéalement créer un snapshot :

```bash
# Après modifications importantes
1. Aller dans Paramètres → Versions Config
2. Créer snapshot: "Ajout de 5 nouvelles compétences techniques"
```

### Rollback

En cas d'erreur, utiliser le système de versioning :

```bash
1. Identifier la version avant les modifications
2. Effectuer un rollback
3. Les références sont restaurées à l'état précédent
```

## Bonnes pratiques

### Codes (identifiants)

✅ **Bons codes:**
- `full_time` (snake_case)
- `bac_plus_2` (descriptif)
- `senior` (court et clair)

❌ **Mauvais codes:**
- `Full Time` (espaces)
- `BAC+2` (caractères spéciaux)
- `s` (trop court, non descriptif)

### Labels

✅ **Bons labels:**
- "Temps plein" (clair et concis)
- "Bac+2 (BTS/DUT)" (précis avec contexte)
- "Senior (8-15 ans)" (avec indication)

❌ **Mauvais labels:**
- "TP" (trop abrégé)
- "Temps plein de travail à 40 heures par semaine" (trop long)

### Ordre d'affichage

- Utiliser des multiples de 10: 10, 20, 30...
- Facilite l'insertion entre deux valeurs
- Ex: Insérer entre 20 et 30 → utiliser 25

### Métadonnées

**Structure recommandée:**

```json
{
  "color": "#3B82F6",     // Couleur hex pour UI
  "icon": "star",          // Nom d'icône Heroicons
  "years": "5-8",          // Pour experience_levels
  "hours": "35-40",        // Pour work_schedules
  "min": 1000000,          // Pour salary_ranges
  "max": 2000000           // Pour salary_ranges
}
```

### Gestion des statuts

**Préférer désactivation à suppression:**

❌ Supprimer une référence utilisée = données orphelines
✅ Désactiver = masquer sans casser les données

## Limitations actuelles

1. **Métadonnées limitées**
   - Format libre (JSON object)
   - Pas de validation de structure
   - Pas d'éditeur visuel pour métadonnées

2. **Pas de réorganisation par drag & drop**
   - Modification manuelle de l'ordre
   - Pas de réorganisation visuelle

3. **Pas d'import/export**
   - Pas d'import CSV/JSON
   - Pas d'export en masse

4. **Pas de recherche/filtre**
   - Navigation par catégorie uniquement
   - Pas de recherche globale

## Évolutions futures possibles

1. **Éditeur de métadonnées avancé**
   - Color picker pour `color`
   - Icon picker pour `icon`
   - Validations par type

2. **Drag & drop pour ordre**
   - Réorganisation visuelle
   - Sauvegarde automatique de l'ordre

3. **Import/Export**
   - Import CSV en masse
   - Export catégorie vers JSON/CSV
   - Template de fichier d'import

4. **Recherche et filtrage**
   - Recherche globale tous types
   - Filtres avancés (actif/inactif, système/custom)
   - Tri par colonne

5. **Audit trail intégré**
   - Historique des modifications
   - Qui a modifié quoi et quand
   - Comparaison avant/après

6. **Validation des contraintes**
   - Vérifier références utilisées avant suppression
   - Alertes si suppression impacte des données

## Dépannage

### Les références ne s'affichent pas

**Cause:** API non accessible ou catégorie vide

**Solution:**
1. Vérifier les logs backend
2. Tester l'API directement: `curl http://localhost:8000/api/auth/config/references?category=skills`
3. Vérifier MongoDB: `db.system_references.find({category: "skills"})`

### Erreur "Les référentiels système ne peuvent pas être supprimés"

**Cause:** Tentative de suppression d'une référence avec `is_system: true`

**Solution:** Les références système sont protégées. Utilisez la désactivation si nécessaire.

### La modification ne s'enregistre pas

**Cause:** Validation backend échouée ou conflit de code

**Solutions:**
1. Vérifier la console navigateur pour les erreurs
2. Vérifier que le code est unique dans la catégorie
3. Vérifier les champs obligatoires (code, label_fr)

### Erreur 500 lors de la création

**Cause:** Erreur serveur, souvent due à un code dupliqué

**Solution:**
1. Vérifier logs backend: `tail -f /var/log/supervisor/auth-microservice.err.log`
2. Utiliser un code unique
3. Vérifier la structure des métadonnées (JSON valide)

## Support

Pour toute question ou problème :
1. Consulter cette documentation
2. Vérifier les logs backend et frontend
3. Tester l'API directement avec curl
4. Utiliser le système de versioning pour rollback si nécessaire

---

**Développeur:** AI Engineer  
**Date:** 5 Novembre 2025  
**Status:** ✅ Interface complète et fonctionnelle
