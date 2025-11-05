# Références Importantes Ajoutées

**Date:** 5 Novembre 2025  
**Version snapshot:** v20251105.090140  
**Total ajouté:** 39 références  
**Total final:** 82 références actives

## Résumé des ajouts

### 1. User Statuses (1 référence ajoutée)
Statuts utilisateurs complétés :
- ✅ `deleted` - Supprimé - Compte utilisateur supprimé

### 2. Validation Types (3 références ajoutées)
Types de validation pour le workflow de validation :
- ✅ `interim` - Validation Intérimaire - Validation du profil intérimaire
- ✅ `company` - Validation Entreprise - Validation du profil entreprise  
- ✅ `collaborator` - Validation Collaborateur - Validation du profil collaborateur

### 3. Validation Statuses (3 références ajoutées)
Statuts pour le workflow de validation :
- ✅ `pending` - En attente - Validation en attente de traitement
- ✅ `approved` - Approuvé - Validation approuvée
- ✅ `rejected` - Rejeté - Validation rejetée

### 4. Roles (1 référence ajoutée)
Nouveau rôle système :
- ✅ `validator` - Validateur - Rôle de validateur des profils

### 5. Document Types (2 références ajoutées)
Types de documents supplémentaires :
- ✅ `diploma` - Diplôme - Diplôme ou certification
- ✅ `identity_document` - Pièce d'identité - Document d'identité officiel

### 6. Mission Statuses (2 références ajoutées)
Statuts de missions supplémentaires :
- ✅ `closed` - Clôturée - Mission clôturée (recrutement terminé)
- ✅ `archived` - Archivée - Mission archivée

### 7. Application Statuses (4 références ajoutées)
Statuts de candidatures manquants :
- ✅ `submitted` - Soumise - Candidature soumise
- ✅ `review` - En révision - Candidature en cours de révision
- ✅ `interviewed` - Entretien passé - Candidat a passé l'entretien
- ✅ `withdrawn` - Retirée - Candidature retirée par le candidat

### 8. Skill Categories (4 références ajoutées) ⭐ NOUVEAU
Catégories de compétences pour la gestion des profils :
- ✅ `technical` - Compétences Techniques - Compétences techniques et professionnelles
- ✅ `soft_skills` - Compétences Comportementales - Compétences comportementales et relationnelles
- ✅ `languages` - Langues - Compétences linguistiques
- ✅ `certifications` - Certifications - Certifications professionnelles

### 9. Experience Levels (5 références ajoutées) ⭐ NOUVEAU
Niveaux d'expérience professionnelle :
- ✅ `entry` - Débutant - 0-2 ans d'expérience
- ✅ `junior` - Junior - 2-5 ans d'expérience
- ✅ `intermediate` - Intermédiaire - 5-8 ans d'expérience
- ✅ `senior` - Senior - 8-15 ans d'expérience
- ✅ `expert` - Expert - 15+ ans d'expérience

### 10. Education Levels (5 références ajoutées) ⭐ NOUVEAU
Niveaux d'éducation :
- ✅ `bac` - Baccalauréat - Niveau Baccalauréat
- ✅ `bac_plus_2` - Bac+2 (BTS/DUT) - Diplôme Bac+2
- ✅ `licence` - Licence (Bac+3) - Niveau Licence
- ✅ `master` - Master (Bac+5) - Niveau Master
- ✅ `doctorat` - Doctorat (Bac+8) - Niveau Doctorat

### 11. Work Schedules (4 références ajoutées) ⭐ NOUVEAU
Types d'horaires de travail :
- ✅ `full_time` - Temps plein - Travail à temps plein (35-40h)
- ✅ `part_time` - Temps partiel - Travail à temps partiel (<35h)
- ✅ `flexible` - Horaires flexibles - Horaires flexibles
- ✅ `shift_work` - Travail posté - Travail en équipes/postes

### 12. Salary Ranges (5 références ajoutées) ⭐ NOUVEAU
Fourchettes salariales en FCFA :
- ✅ `range_1` - < 500 000 FCFA - Moins de 500 000 FCFA
- ✅ `range_2` - 500k - 1M FCFA - Entre 500 000 et 1 000 000 FCFA
- ✅ `range_3` - 1M - 2M FCFA - Entre 1 et 2 millions FCFA
- ✅ `range_4` - 2M - 5M FCFA - Entre 2 et 5 millions FCFA
- ✅ `range_5` - > 5M FCFA - Plus de 5 millions FCFA

## État final des références

### Récapitulatif par catégorie

| Catégorie | Références actives | Nouvelles | Description |
|-----------|-------------------|-----------|-------------|
| `application_statuses` | 14 | +4 | Statuts des candidatures |
| `contract_types` | 4 | 0 | Types de contrats |
| `countries` | 5 | 0 | Pays |
| `document_types` | 7 | +2 | Types de documents |
| `education_levels` | 5 | +5 | ⭐ Niveaux d'éducation |
| `experience_levels` | 5 | +5 | ⭐ Niveaux d'expérience |
| `medical_aptitudes` | 3 | 0 | Aptitudes médicales |
| `mission_statuses` | 7 | +2 | Statuts des missions |
| `roles` | 7 | +1 | Rôles utilisateurs |
| `salary_ranges` | 5 | +5 | ⭐ Fourchettes salariales |
| `skill_categories` | 4 | +4 | ⭐ Catégories de compétences |
| `skills` | 5 | 0 | Compétences spécifiques |
| `user_statuses` | 1 | +1 | Statuts utilisateurs |
| `validation_statuses` | 3 | +3 | Statuts de validation |
| `validation_types` | 3 | +3 | Types de validation |
| `work_schedules` | 4 | +4 | ⭐ Types d'horaires |
| **TOTAL** | **82** | **+39** | |

⭐ = Nouvelle catégorie

## Utilisation des nouvelles références

### 1. Profils Intérimaires
Les nouvelles références permettent d'enrichir les profils intérimaires avec :
- **Niveau d'expérience** (`experience_levels`) - Pour matcher les missions appropriées
- **Niveau d'éducation** (`education_levels`) - Pour les prérequis de formation
- **Catégories de compétences** (`skill_categories`) - Pour organiser les compétences
- **Préférences horaires** (`work_schedules`) - Pour les préférences de travail
- **Attentes salariales** (`salary_ranges`) - Pour le matching salarial

### 2. Offres de Mission
Les missions peuvent maintenant spécifier :
- **Niveau d'expérience requis** - Via `experience_levels`
- **Niveau d'éducation minimal** - Via `education_levels`
- **Type d'horaires** - Via `work_schedules`
- **Fourchette salariale** - Via `salary_ranges`

### 3. Workflow de Validation
Le système de validation est maintenant complet avec :
- **Types de validation** - interim, company, collaborator
- **Statuts de validation** - pending, approved, rejected
- **Rôle validator** - Pour assigner des validateurs spécifiques

### 4. Gestion des Candidatures
Workflow de candidature enrichi :
- `submitted` → `review` → `interview_scheduled` → `interviewed` → `selected`
- Possibilité de `withdrawn` (retrait par candidat)

## Exemples d'utilisation

### Créer un profil intérimaire complet
```json
{
  "user_id": "uuid",
  "experience_level": "intermediate",
  "education_level": "licence",
  "skills": [
    {"category": "technical", "name": "Python", "level": "advanced"},
    {"category": "soft_skills", "name": "Communication", "level": "expert"},
    {"category": "languages", "name": "Français", "level": "native"}
  ],
  "work_schedule_preferences": ["full_time", "flexible"],
  "salary_expectation": "range_3"
}
```

### Créer une mission avec critères
```json
{
  "title": "Développeur Full Stack",
  "experience_level_required": "junior",
  "education_level_required": "licence",
  "work_schedule": "full_time",
  "salary_range": "range_2",
  "required_skills": [
    {"category": "technical", "name": "JavaScript"},
    {"category": "technical", "name": "React"}
  ]
}
```

### Workflow de validation
```javascript
// Créer une demande de validation
const validation = {
  type: "interim",  // validation_types
  status: "pending",  // validation_statuses
  user_id: "user_uuid",
  validator_id: null,
  assigned_at: null
}

// Assigner à un validateur (role: validator)
validation.validator_id = "validator_uuid"
validation.assigned_at = new Date()

// Approuver la validation
validation.status = "approved"
validation.validated_at = new Date()
```

## Migration des données existantes

### Recommandations

1. **Profils existants:**
   - Ajouter progressivement les nouveaux champs
   - Ne pas rendre obligatoires immédiatement
   - Permettre aux utilisateurs de compléter leur profil

2. **Missions existantes:**
   - Les missions sans `experience_level` sont ouvertes à tous
   - Mettre à jour progressivement lors des éditions

3. **Validations:**
   - Migrer les validations en cours vers le nouveau système
   - Script de migration si nécessaire

## API - Nouveaux endpoints suggérés

### Référentiels
```http
GET /api/references/experience_levels
GET /api/references/education_levels
GET /api/references/work_schedules
GET /api/references/salary_ranges
GET /api/references/skill_categories
```

### Filtrage missions
```http
GET /api/missions?experience_level=junior&work_schedule=full_time&salary_range=range_2
```

### Matching candidats
```http
POST /api/matching/candidates
{
  "mission_id": "uuid",
  "filters": {
    "experience_level": ["junior", "intermediate"],
    "education_level": ["licence", "master"],
    "work_schedule": ["full_time"]
  }
}
```

## Configuration Cache

Les nouvelles références sont automatiquement incluses dans le cache de références si activé (`cache.references.enabled: true` dans base.yaml).

## Snapshot de configuration

Un snapshot automatique a été créé lors de l'ajout :
- **Version:** v20251105.090140
- **Description:** Ajout 39 références importantes (validation, expérience, éducation, horaires, salaires)
- **Accessible via:** `/admin/versions`

Pour restaurer l'état précédent si nécessaire :
```bash
# Via l'interface admin
1. Aller dans Paramètres → Versions Config
2. Sélectionner la version précédente
3. Cliquer "Rollback"
```

## Maintenance

### Ajouter des valeurs à une catégorie existante
```python
await db.system_references.insert_one({
    "id": str(uuid.uuid4()),
    "category": "skill_categories",
    "code": "management",
    "label_fr": "Management",
    "label_en": "Management",
    "description": "Compétences de management",
    "order": 5,
    "metadata": {"color": "#EF4444", "icon": "user-group"},
    "is_active": True,
    "is_system": True,
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc),
})
```

### Désactiver une référence (soft delete)
```python
await db.system_references.update_one(
    {"category": "salary_ranges", "code": "range_1"},
    {"$set": {"is_active": False}}
)
```

## Prochaines étapes suggérées

1. ✅ Références importantes ajoutées
2. 📋 **Mettre à jour les modèles Pydantic** pour inclure les nouveaux champs
3. 📋 **Enrichir les formulaires frontend** avec les nouveaux sélecteurs
4. 📋 **Implémenter le matching intelligent** basé sur les critères
5. 📋 **Ajouter des filtres de recherche** dans les listes missions/candidats
6. 📋 **Créer des rapports/analytics** utilisant ces catégories

## Support

Pour toute question ou ajout de références supplémentaires :
1. Modifier le fichier `/app/auth-microservice/scripts/add_missing_references.py`
2. Exécuter le script : `python scripts/add_missing_references.py`
3. Créer un snapshot de configuration via l'interface admin

---

**Développeur:** AI Engineer  
**Date:** 5 Novembre 2025  
**Status:** ✅ Complété et documenté
