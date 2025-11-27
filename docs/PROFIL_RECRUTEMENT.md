# 👔 Profil Recrutement - Documentation Complète

**Date:** 26 Novembre 2025  
**Version:** 1.0

---

## 📋 Vue d'Ensemble

Le profil **Recrutement** est un profil spécialisé pour les équipes de recrutement qui doivent :
- Consulter les profils des candidats et intérimaires
- Évaluer et noter les candidats
- Attribuer les candidats aux missions
- Accéder aux CV et documents de candidature

---

## 🎯 Objectif du Profil

Le recrutement est une fonction transverse qui nécessite :
1. **Accès étendu aux candidats** : Voir tous les profils, compétences, disponibilités
2. **Capacité d'évaluation** : Noter, commenter, créer des feedbacks
3. **Attribution aux missions** : Matcher candidats et missions
4. **Accès documents** : Consulter CV, lettres de motivation

**Ce profil N'A PAS** :
- ❌ Droits de modification des utilisateurs (réservé aux Admin/HR)
- ❌ Création de missions (réservé aux Entreprises/Commercial)
- ❌ Validation finale des candidatures (réservé aux Entreprises/HR)
- ❌ Accès aux émargements et paie

---

## 📦 Bundles Assignés

### Bundle Principal: `recruitment.manage` ⭐
**Description:** Bundle complet pour le recrutement incluant toutes les permissions nécessaires

**Permissions incluses (35 permissions):**

#### 👥 Consultation Utilisateurs (8 permissions)
```javascript
[
  "users.view.all",           // Voir la liste de tous les utilisateurs
  "users.read.all",           // Lire les détails de tous les utilisateurs
  "users.profiles.view",      // Consulter les profils complets
  "users.skills.view",        // Voir les compétences
  "users.experience.view",    // Voir les expériences professionnelles
  "users.availability.view",  // Voir les disponibilités
  "users.search",             // Rechercher des candidats
  "users.filter"              // Filtrer par critères
]
```

#### ⭐ Évaluation Candidats (9 permissions)
```javascript
[
  "users.rate",               // Noter un candidat (ex: 1-5 étoiles)
  "users.rating.view",        // Voir les notes attribuées
  "users.comment.create",     // Créer un commentaire sur un candidat
  "users.comment.view",       // Voir les commentaires
  "users.feedback.create",    // Créer un feedback détaillé
  "users.feedback.view",      // Voir les feedbacks
  "users.notes.create",       // Créer des notes internes
  "users.notes.view",         // Voir toutes les notes
  "users.notes.edit.own"      // Modifier ses propres notes
]
```

#### 🎯 Attribution Missions (7 permissions)
```javascript
[
  "missions.view.all",        // Voir toutes les missions
  "missions.read.all",        // Lire détails missions
  "missions.assign",          // Attribuer une mission
  "missions.users.assign",    // Assigner un user à une mission
  "missions.users.unassign",  // Retirer un user d'une mission
  "missions.matching.view",   // Voir le matching candidat-mission
  "applications.assign_candidate"  // Assigner directement un candidat
]
```

#### 📄 Accès Documents (3 permissions)
```javascript
[
  "documents.cv.view",               // Voir les CV
  "documents.cv.download",           // Télécharger les CV
  "documents.motivation_letter.view" // Voir lettres de motivation
]
```

#### 📝 Candidatures (3 permissions)
```javascript
[
  "applications.view.all",    // Voir toutes les candidatures
  "applications.read.all",    // Lire détails candidatures
  "applications.comment"      // Commenter une candidature
]
```

### Bundles Complémentaires

- **`auth.basic`** : Authentification et gestion de profil personnel
- **`missions.read`** : Consultation missions (inclus dans recruitment.manage)
- **`applications.review`** : Révision candidatures
- **`documents.recruitment_access`** : Accès étendu documents
- **`notifications.user`** : Notifications personnelles
- **`analytics.view`** : Tableaux de bord et statistiques

---

## 🔐 Permissions Détaillées par Fonctionnalité

### 1. Consultation des Candidats

#### Liste des candidats
```http
GET /api/users?role=candidat,interimaire
Authorization: Bearer <token avec users.view.all>
```

**Réponse:**
```json
{
  "users": [
    {
      "id": "user_123",
      "full_name": "Jean Dupont",
      "email": "jean@example.com",
      "role": "candidat",
      "status": "active",
      "skills": ["Python", "React", "Node.js"],
      "availability": "immediate",
      "rating": 4.5,
      "applications_count": 3
    }
  ]
}
```

#### Recherche avancée
```http
POST /api/users/search
Authorization: Bearer <token avec users.search>

{
  "skills": ["Python", "React"],
  "availability": "immediate",
  "min_rating": 4.0,
  "location": "Paris"
}
```

---

### 2. Évaluation des Candidats

#### Noter un candidat
```http
POST /api/users/{user_id}/rate
Authorization: Bearer <token avec users.rate>

{
  "rating": 4.5,
  "comment": "Excellent profil technique, très motivé"
}
```

#### Créer un feedback
```http
POST /api/users/{user_id}/feedback
Authorization: Bearer <token avec users.feedback.create>

{
  "type": "interview",
  "date": "2025-11-26",
  "notes": "Entretien positif. Points forts: communication, autonomie. À développer: anglais technique.",
  "recommendation": "À recontacter pour missions React"
}
```

#### Ajouter une note interne
```http
POST /api/users/{user_id}/notes
Authorization: Bearer <token avec users.notes.create>

{
  "title": "Note entretien téléphonique",
  "content": "Disponible à partir du 1er décembre. Préfère missions longues (3+ mois).",
  "tags": ["disponibilité", "préférences"],
  "private": true
}
```

#### Voir toutes les évaluations d'un candidat
```http
GET /api/users/{user_id}/evaluations
Authorization: Bearer <token avec users.rating.view>
```

**Réponse:**
```json
{
  "user_id": "user_123",
  "average_rating": 4.3,
  "ratings": [
    {
      "rating": 4.5,
      "by": "recruiter_1",
      "date": "2025-11-20",
      "comment": "Excellent profil"
    }
  ],
  "feedbacks": [...],
  "notes": [...]
}
```

---

### 3. Attribution aux Missions

#### Voir le matching candidat-mission
```http
GET /api/missions/{mission_id}/matching
Authorization: Bearer <token avec missions.matching.view>
```

**Réponse:**
```json
{
  "mission_id": "mission_456",
  "candidates": [
    {
      "user_id": "user_123",
      "match_score": 92,
      "matching_skills": ["Python", "React"],
      "missing_skills": ["Docker"],
      "availability": "immediate",
      "rating": 4.5,
      "recommendation": "excellent"
    },
    {
      "user_id": "user_789",
      "match_score": 85,
      ...
    }
  ]
}
```

#### Assigner un candidat à une mission
```http
POST /api/missions/{mission_id}/assign
Authorization: Bearer <token avec missions.users.assign>

{
  "user_id": "user_123",
  "start_date": "2025-12-01",
  "note": "Profil parfait pour cette mission React"
}
```

#### Retirer un candidat d'une mission
```http
DELETE /api/missions/{mission_id}/users/{user_id}
Authorization: Bearer <token avec missions.users.unassign>

{
  "reason": "Candidat a décliné l'offre"
}
```

---

### 4. Accès aux Documents

#### Voir le CV d'un candidat
```http
GET /api/documents/cv/{user_id}
Authorization: Bearer <token avec documents.cv.view>
```

#### Télécharger un CV
```http
GET /api/documents/cv/{user_id}/download
Authorization: Bearer <token avec documents.cv.download>
```

**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="cv_jean_dupont.pdf"
```

#### Voir lettre de motivation
```http
GET /api/documents/motivation-letter/{application_id}
Authorization: Bearer <token avec documents.motivation_letter.view>
```

---

### 5. Gestion des Candidatures

#### Voir toutes les candidatures
```http
GET /api/applications?status=submitted
Authorization: Bearer <token avec applications.view.all>
```

#### Commenter une candidature
```http
POST /api/applications/{application_id}/comments
Authorization: Bearer <token avec applications.comment>

{
  "comment": "Profil intéressant, à convoquer pour entretien",
  "internal": true
}
```

---

## 🚫 Limitations du Profil

Le profil Recrutement **N'A PAS** accès à :

❌ **Gestion utilisateurs**
- Création/modification/suppression de comptes
- Changement de statut (actif/suspendu)
- Réinitialisation de mots de passe

❌ **Validation finale**
- Approbation/rejet final des candidatures (réservé aux Entreprises/HR)
- Signature de contrats

❌ **Création de missions**
- Seuls Commercial, HR Manager, Entreprises peuvent créer

❌ **Données RH sensibles**
- Émargements, paie, contrats de travail
- Données salariales

❌ **Administration système**
- Gestion IAM, configuration, logs

---

## 📊 Workflow Type

```
┌─────────────────────────────────────────────────────────┐
│            WORKFLOW RECRUTEMENT COMPLET                  │
└─────────────────────────────────────────────────────────┘

1️⃣ RÉCEPTION CANDIDATURE
   GET /api/applications
   ↓
   
2️⃣ CONSULTATION PROFIL
   GET /api/users/{user_id}
   GET /api/documents/cv/{user_id}
   ↓
   
3️⃣ ÉVALUATION
   POST /api/users/{user_id}/rate
   POST /api/users/{user_id}/feedback
   ↓
   
4️⃣ RECHERCHE MISSION
   GET /api/missions
   GET /api/missions/{mission_id}/matching
   ↓
   
5️⃣ ATTRIBUTION
   POST /api/missions/{mission_id}/assign
   ↓
   
6️⃣ SUIVI
   POST /api/applications/{id}/comments
   GET /api/analytics (statistiques)
```

---

## 🎯 Cas d'Usage Concrets

### Cas 1: Rechercher un candidat pour une mission React

```python
# 1. Rechercher candidats avec compétences React
candidates = search_users(
    skills=["React", "JavaScript"],
    availability="immediate",
    min_rating=4.0
)

# 2. Voir le matching avec la mission
for candidate in candidates:
    match = get_mission_matching(mission_id, candidate.id)
    print(f"{candidate.name}: {match.score}%")

# 3. Consulter les évaluations
best_candidate = candidates[0]
evaluations = get_user_evaluations(best_candidate.id)

# 4. Attribuer à la mission
assign_to_mission(mission_id, best_candidate.id)
```

### Cas 2: Évaluer un candidat après entretien

```python
# 1. Noter le candidat
rate_user(
    user_id="user_123",
    rating=4.5,
    comment="Très bon niveau technique"
)

# 2. Ajouter un feedback détaillé
create_feedback(
    user_id="user_123",
    type="interview",
    notes="""
    Points forts:
    - Excellente maîtrise React/TypeScript
    - Bonne communication
    - Autonome
    
    Points d'amélioration:
    - Anglais technique à renforcer
    
    Recommandation: À privilégier pour missions React
    """
)

# 3. Ajouter une note interne
create_note(
    user_id="user_123",
    title="Disponibilité",
    content="Disponible à partir du 1er décembre",
    private=True
)
```

### Cas 3: Dashboard recrutement

```python
# Statistiques du jour
stats = get_recruitment_stats()

print(f"Nouvelles candidatures: {stats.new_applications}")
print(f"Candidats notés aujourd'hui: {stats.rated_today}")
print(f"Missions avec candidats assignés: {stats.missions_filled}")
print(f"Taux de matching moyen: {stats.avg_match_score}%")
```

---

## 📈 Métriques Clés

Le profil Recrutement peut suivre :

- **Candidatures traitées** par jour/semaine/mois
- **Taux de matching moyen** candidat-mission
- **Délai moyen d'attribution** (candidature → assignation)
- **Nombre de candidats évalués**
- **Taux de conversion** (candidature → mission)

---

## 🔗 API Endpoints Principaux

| Endpoint | Permission | Description |
|----------|-----------|-------------|
| `GET /api/users` | users.view.all | Liste candidats |
| `POST /api/users/search` | users.search | Recherche avancée |
| `GET /api/users/{id}` | users.read.all | Détail candidat |
| `POST /api/users/{id}/rate` | users.rate | Noter candidat |
| `POST /api/users/{id}/feedback` | users.feedback.create | Ajouter feedback |
| `POST /api/users/{id}/notes` | users.notes.create | Ajouter note |
| `GET /api/missions` | missions.view.all | Liste missions |
| `GET /api/missions/{id}/matching` | missions.matching.view | Matching |
| `POST /api/missions/{id}/assign` | missions.users.assign | Attribuer |
| `GET /api/documents/cv/{id}` | documents.cv.view | Voir CV |
| `GET /api/applications` | applications.view.all | Liste candidatures |

---

## 💡 Bonnes Pratiques

### ✅ À FAIRE
- Documenter chaque évaluation avec des feedbacks détaillés
- Utiliser le système de notes pour garder une trace des échanges
- Consulter le matching avant d'attribuer une mission
- Mettre à jour régulièrement les évaluations après chaque interaction

### ❌ À ÉVITER
- Ne pas noter sans justification/commentaire
- Ne pas attribuer sans vérifier disponibilité réelle
- Ne pas modifier les données utilisateur directement (utiliser les notes)
- Ne pas partager les évaluations internes avec les candidats

---

## 🔒 Sécurité

### Données Sensibles
Le profil Recrutement a accès à des données sensibles :
- CV et informations personnelles
- Notes d'évaluation internes
- Historique professionnel

**Obligations:**
- Respecter le RGPD
- Ne pas partager d'évaluations internes
- Supprimer les notes obsolètes
- Utiliser le flag `private: true` pour notes confidentielles

---

## 📚 Documents Connexes

- [BUNDLES_MATRIX_COMPLETE.md](BUNDLES_MATRIX_COMPLETE.md) - Matrice complète des bundles
- [IAM_PROFILE_PERMISSIONS_MATRIX.md](IAM_PROFILE_PERMISSIONS_MATRIX.md) - Matrice permissions
- [permission_bundles.py](../auth-microservice/awana_auth/core/permission_bundles.py) - Configuration

---

*Dernière mise à jour: 26 Novembre 2025*  
*Version: 1.0*
