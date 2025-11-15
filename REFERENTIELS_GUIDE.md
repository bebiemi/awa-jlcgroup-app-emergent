# Guide des Référentiels - JLC Group

## Vue d'ensemble

Les référentiels sont des données de configuration qui permettent de standardiser les valeurs utilisées dans l'application. Ils sont entièrement gérables via l'interface d'administration.

## Accès

**URL:** `/admin/references`

**Permissions requises:** `config.manage` ou `admin.dashboard`

## Catégories disponibles

### 1. 👥 Rôles Utilisateurs (`roles`)
Définit les différents rôles système :
- `admin` - Administrateur
- `commercial` - Commercial
- `interim` - Intérimaire
- `company` - Entreprise
- `agency` - Agence
- `candidat` - Candidat

### 2. 👤 Statuts Utilisateurs (`user_statuses`)
États du cycle de vie d'un utilisateur :
- `active` - Actif
- `pending` - En attente
- `suspended` - Suspendu
- `archived` - Archivé

### 3. 💼 Statuts de Mission (`mission_statuses`)
États d'avancement d'une mission :
- `draft` - Brouillon
- `published` - Publiée
- `in_progress` - En cours
- `completed` - Terminée
- `cancelled` - Annulée
- `closed` - Clôturée

### 4. 📋 Statuts de Candidature (`application_statuses`)
Progression d'une candidature :
- `submitted` - Soumise
- `under_review` - En examen
- `shortlisted` - Présélectionnée
- `interview` - Entretien
- `accepted` - Acceptée
- `rejected` - Refusée
- `withdrawn` - Retirée

### 5. ✓ Types de Validation (`validation_types`)
Différents types de validation :
- `profile` - Profil
- `document` - Document
- `mission` - Mission
- `timesheet` - Feuille de temps
- `medical` - Visite médicale

### 6. ✅ Statuts de Validation (`validation_statuses`)
États d'une validation :
- `pending` - En attente
- `approved` - Approuvée
- `rejected` - Rejetée
- `revision_required` - Révision requise

### 7. 📝 Types de Contrat (`contract_types`)
Formes de contrat de travail :
- `cdi` - CDI - Contrat à Durée Indéterminée
- `cdd` - CDD - Contrat à Durée Déterminée
- `interim` - Intérim
- `freelance` - Freelance
- `stage` - Stage
- `alternance` - Alternance

### 8. 📄 Types de Documents (`document_types`)
Documents requis ou acceptés :
- `cv` - CV
- `id_card` - Carte d'identité
- `passport` - Passeport
- `diploma` - Diplôme
- `certificate` - Certificat
- `medical_certificate` - Certificat médical
- `work_permit` - Permis de travail
- `residence_permit` - Titre de séjour
- `social_security` - Carte de sécurité sociale
- `bank_details` - RIB
- `other` - Autre

### 9. 📊 Niveaux d'Expérience (`experience_levels`)
Classifications d'expérience professionnelle :
- `entry` - Débutant (0-2 ans)
- `junior` - Junior (2-5 ans)
- `intermediate` - Intermédiaire (5-8 ans)
- `senior` - Senior (8-12 ans)
- `expert` - Expert (12+ ans)

### 10. 🎓 Niveaux d'Éducation (`education_levels`)
Diplômes et formations :
- `no_diploma` - Sans diplôme
- `cap_bep` - CAP/BEP
- `bac` - Baccalauréat
- `bac_2` - Bac+2 (BTS/DUT)
- `bac_3` - Bac+3 (Licence)
- `bac_5` - Bac+5 (Master)
- `bac_8` - Bac+8 (Doctorat)

### 11. 🎯 Catégories de Compétences (`skill_categories`)
Regroupements de compétences :
- `technical` - Compétences Techniques
- `soft_skills` - Compétences Comportementales
- `languages` - Langues
- `tools` - Outils & Logiciels
- `certifications` - Certifications

### 12. 🕐 Types d'Horaires (`work_schedules`)
Modalités de travail :
- `full_time` - Temps plein
- `part_time` - Temps partiel
- `shift_work` - Travail posté
- `night_shift` - Nuit
- `weekend` - Weekend
- `flexible` - Horaires flexibles

### 13. 💰 Fourchettes Salariales (`salary_ranges`)
Tranches de rémunération annuelle :
- `less_20k` - Moins de 20K€
- `20k_30k` - 20K€ - 30K€
- `30k_40k` - 30K€ - 40K€
- `40k_50k` - 40K€ - 50K€
- `50k_70k` - 50K€ - 70K€
- `70k_100k` - 70K€ - 100K€
- `more_100k` - Plus de 100K€

### 14. 🏥 Aptitudes Médicales (`medical_aptitudes`)
Résultats de visite médicale :
- `fit` - Apte
- `fit_with_restrictions` - Apte avec restrictions
- `temporarily_unfit` - Inapte temporaire
- `unfit` - Inapte
- `pending` - En attente de visite

### 15. 🌍 Pays (`countries`)
Pays principaux d'opération :
- `GA` - Gabon
- `FR` - France
- `CM` - Cameroun
- `CI` - Côte d'Ivoire
- `SN` - Sénégal
- `CD` - RD Congo
- `CG` - Congo
- `BJ` - Bénin
- `TG` - Togo
- `MA` - Maroc

## Gestion des Référentiels

### Ajouter une nouvelle référence

1. Accéder à `/admin/references`
2. Sélectionner la catégorie souhaitée
3. Cliquer sur "Nouveau"
4. Remplir les champs :
   - **Code** : Identifiant unique (ex: `full_time_remote`)
   - **Label FR** : Libellé en français
   - **Label EN** : Libellé en anglais (optionnel)
   - **Description** : Description détaillée (optionnel)
   - **Ordre** : Position d'affichage (numérique)
   - **Actif** : Coché si la référence doit être visible
5. Enregistrer

### Modifier une référence existante

1. Trouver la référence dans la liste
2. Cliquer sur l'icône "Éditer" (crayon)
3. Modifier les champs nécessaires
4. Enregistrer

### Désactiver une référence

Au lieu de supprimer une référence utilisée, il est recommandé de la désactiver :
1. Éditer la référence
2. Décocher "Actif"
3. Enregistrer

Les références désactivées ne sont plus proposées dans les formulaires mais restent visibles sur les données historiques.

## Structure Technique

### Collection MongoDB
**Collection:** `system_references`

**Structure d'un document:**
```javascript
{
  "id": "uuid-v4",
  "category": "contract_types",
  "code": "cdi",
  "label_fr": "CDI - Contrat à Durée Indéterminée",
  "label_en": "Permanent Contract",
  "description": "",
  "order": 1,
  "is_active": true,
  "metadata": {},
  "created_at": ISODate("2025-01-15T10:00:00Z"),
  "updated_at": ISODate("2025-01-15T10:00:00Z")
}
```

### API Endpoints

**Lister les références:**
```
GET /api/config/references?category=contract_types
```

**Créer une référence:**
```
POST /api/config/references
Body: {
  "category": "contract_types",
  "code": "new_type",
  "label_fr": "Nouveau Type",
  "label_en": "New Type",
  "order": 10,
  "is_active": true
}
```

**Mettre à jour:**
```
PATCH /api/config/references/{id}
```

**Supprimer:**
```
DELETE /api/config/references/{id}
```

## Script de Migration

Pour réinitialiser ou mettre à jour tous les référentiels :

```bash
cd /app/auth-microservice
python scripts/init_complete_references.py
```

Ce script :
- ✅ Crée les références manquantes
- ✅ Met à jour les labels si modifiés
- ✅ Préserve les références existantes
- ✅ N'écrase pas les statuts `is_active`
- ✅ Conserve les métadonnées personnalisées

## Bonnes Pratiques

1. **Codes uniques** : Utilisez des codes descriptifs en anglais (ex: `full_time`, `part_time`)
2. **Ordre logique** : Numérotez de 1 à N pour contrôler l'affichage
3. **Désactivation vs Suppression** : Désactivez plutôt que supprimer pour l'historique
4. **Bilingue** : Remplissez toujours FR et EN pour l'internationalisation
5. **Descriptions** : Ajoutez des descriptions pour clarifier l'usage
6. **Métadonnées** : Utilisez le champ `metadata` pour des données supplémentaires JSON

## Dépendances

Les référentiels sont utilisés par :
- Formulaires de création de missions
- Profils utilisateurs
- Filtres de recherche
- Validations système
- Rapports et statistiques

## Support

Pour toute question sur les référentiels :
- Email : support@jlcgroup.ga
- Documentation technique : `/app/auth-microservice/form_config_routes.py`
