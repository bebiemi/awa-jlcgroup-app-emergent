# 🚀 Roadmap V2 - JLC Group Platform

## Vue d'ensemble
Ce document liste les améliorations et nouvelles fonctionnalités prévues pour la version 2.0 de la plateforme JLC Group.

---

## 🗺️ 1. Gestion Hiérarchique des Localisations

### Contexte
Actuellement, le système gère uniquement les **pays** et les **villes**. Pour une meilleure granularité géographique et une gestion plus précise des missions et des utilisateurs, il est nécessaire d'ajouter des niveaux intermédiaires.

### Fonctionnalité demandée
**Hiérarchie géographique complète :**
```
Pays
  └─ Province/Région
       └─ District/Département
            └─ Ville
                 └─ Quartier/Arrondissement
```

### Cas d'usage
1. **Missions géolocalisées** : Publier une mission spécifique à un quartier de Libreville
2. **Recherche affinée** : Filtrer les intérimaires par quartier
3. **Statistiques précises** : Analyser la répartition des utilisateurs par district
4. **Tarification variable** : Adapter les tarifs selon les zones géographiques

### Spécifications techniques

#### 1.1 Schéma de données proposé

**Collection : `provinces`**
```javascript
{
  id: String,              // UUID
  country_id: String,      // Référence au pays
  name: String,            // Ex: "Estuaire", "Provence-Alpes-Côte d'Azur"
  code: String,            // Ex: "EST", "PACA"
  active: Boolean,
  display_order: Integer,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Collection : `districts`**
```javascript
{
  id: String,              // UUID
  province_id: String,     // Référence à la province
  name: String,            // Ex: "Libreville", "Marseille"
  code: String,            // Ex: "LBV", "MRS"
  active: Boolean,
  display_order: Integer,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Collection : `quartiers`**
```javascript
{
  id: String,              // UUID
  city_id: String,         // Référence à la ville
  district_id: String,     // Référence au district (optionnel)
  name: String,            // Ex: "Nombakélé", "Le Panier"
  code: String,            // Ex: "NOM", "PAR"
  postal_code: String,     // Code postal si applicable
  active: Boolean,
  metadata: {
    zone_type: String,     // "urbain", "rural", "industriel"
    accessibility: String, // "facile", "moyenne", "difficile"
  },
  display_order: Integer,
  created_at: DateTime,
  updated_at: DateTime
}
```

#### 1.2 Modifications des collections existantes

**Collection : `cities` (existante)**
```javascript
// Ajouter :
{
  ...existing_fields,
  district_id: String,     // Nouvelle référence au district
  province_id: String,     // Nouvelle référence à la province
}
```

**Collection : `users` (existante)**
```javascript
// Ajouter dans le profil :
{
  ...existing_fields,
  location: {
    country_id: String,
    province_id: String,   // Nouveau
    district_id: String,   // Nouveau
    city_id: String,
    quartier_id: String,   // Nouveau
    address: String,
  }
}
```

**Collection : `missions` (existante)**
```javascript
// Ajouter :
{
  ...existing_fields,
  location: {
    country_id: String,
    province_id: String,   // Nouveau
    district_id: String,   // Nouveau
    city_id: String,
    quartier_id: String,   // Nouveau
    address: String,
  }
}
```

#### 1.3 API Endpoints à créer

**Backend : `/app/auth-microservice/location_hierarchy_routes.py`**

```python
# Provinces
GET    /api/locations/provinces                    # Liste toutes les provinces
GET    /api/locations/provinces?country_id={id}    # Provinces d'un pays
POST   /api/locations/provinces                    # Créer province (admin)
PUT    /api/locations/provinces/{id}               # Modifier province (admin)
DELETE /api/locations/provinces/{id}               # Supprimer province (admin)

# Districts
GET    /api/locations/districts                    # Liste tous les districts
GET    /api/locations/districts?province_id={id}   # Districts d'une province
POST   /api/locations/districts                    # Créer district (admin)
PUT    /api/locations/districts/{id}               # Modifier district (admin)
DELETE /api/locations/districts/{id}               # Supprimer district (admin)

# Quartiers
GET    /api/locations/quartiers                    # Liste tous les quartiers
GET    /api/locations/quartiers?city_id={id}       # Quartiers d'une ville
GET    /api/locations/quartiers?district_id={id}   # Quartiers d'un district
POST   /api/locations/quartiers                    # Créer quartier (admin)
PUT    /api/locations/quartiers/{id}               # Modifier quartier (admin)
DELETE /api/locations/quartiers/{id}               # Supprimer quartier (admin)

# Hiérarchie complète
GET    /api/locations/hierarchy?country_id={id}    # Arbre complet : Pays > Provinces > Districts > Villes > Quartiers
```

#### 1.4 Frontend : Composants à créer

**Page Admin : Location Management**
- `/app/apps/web/src/features/admin/pages/LocationManagementPage.tsx`
- Gestion CRUD complète de la hiérarchie géographique
- Vue en arborescence (tree view)
- Import/Export CSV pour import massif de données

**Composant : Sélecteur hiérarchique**
- `/app/apps/web/src/components/LocationSelector.tsx`
- Sélecteurs en cascade : Pays → Province → District → Ville → Quartier
- Auto-filtrage selon le niveau parent sélectionné
- Recherche rapide par nom

**Composant : Carte interactive (optionnel)**
- Intégration Leaflet ou Google Maps
- Affichage des zones géographiques
- Clic sur la carte pour sélectionner une localisation

#### 1.5 Migration de données

**Script : `/app/auth-microservice/scripts/migrate_locations_v2.py`**
```python
# Migration en 3 étapes :
# 1. Créer les provinces pour les pays existants
# 2. Créer les districts pour les provinces
# 3. Associer les villes existantes aux districts
# 4. Créer des quartiers par défaut pour les villes principales
```

**Données de base à importer (Gabon) :**
- **Provinces** : Estuaire, Haut-Ogooué, Moyen-Ogooué, Ngounié, Nyanga, Ogooué-Ivindo, Ogooué-Lolo, Ogooué-Maritime, Woleu-Ntem
- **Villes principales** : Libreville (Estuaire), Port-Gentil (Ogooué-Maritime), Franceville (Haut-Ogooué), Oyem (Woleu-Ntem)
- **Quartiers Libreville** : Nombakélé, Glass, Mont-Bouët, Lalala, Akébé, Batterie IV, Nzeng-Ayong, Charbonnages, etc.

#### 1.6 Permissions IAM

**Nouvelles permissions à ajouter :**
```python
# /app/auth-microservice/awana_auth/core/iam_constants.py
class IAMPermissions:
    # ... existing ...
    
    # Location Management
    LOCATIONS_READ = "locations.read"
    LOCATIONS_CREATE = "locations.create"
    LOCATIONS_EDIT = "locations.edit"
    LOCATIONS_DELETE = "locations.delete"
    LOCATIONS_IMPORT = "locations.import"
```

**Profils ayant accès :**
- **Super Admin** : Toutes permissions
- **Admin** : Read, Create, Edit (pas Delete)
- **Commercial** : Read uniquement

---

## 📋 2. Autres fonctionnalités V2 (du backlog)

### 2.1 Clarification Rôles vs Profils
**Status** : Planifié  
**Priorité** : P4  
**Description** : Revoir la distinction entre `user.roles` (legacy) et `user.profiles` (IAM) pour une architecture plus cohérente.

### 2.2 Traductions i18n
**Status** : Planifié  
**Priorité** : P5  
**Description** : Support multilingue (Français, Anglais)

### 2.3 Tests automatisés frontend
**Status** : Planifié  
**Priorité** : P6  
**Description** : Mise en place de tests E2E avec Playwright

### 2.4 Module Missions - Finalisation
**Status** : En cours  
**Priorité** : P2  
**Description** : Finaliser édition, suppression, workflow complet des missions

### 2.5 Company Management Page - Finalisation
**Status** : En cours  
**Priorité** : P3  
**Description** : Finaliser le frontend de la page de gestion des entreprises

---

## 📊 Estimation de charge

| Fonctionnalité | Complexité | Estimation | Priorité |
|----------------|------------|------------|----------|
| **Hiérarchie Géographique** | Élevée | 3-5 jours | P1 (V2) |
| Schéma DB + Migrations | Moyenne | 1 jour | - |
| API Backend (CRUD) | Moyenne | 1-2 jours | - |
| Frontend Admin + Composants | Élevée | 1-2 jours | - |
| Import données (Gabon) | Faible | 0.5 jour | - |
| Tests + Documentation | Moyenne | 0.5 jour | - |
| **Rôles vs Profils** | Moyenne | 2-3 jours | P4 |
| **i18n** | Moyenne | 2-3 jours | P5 |
| **Tests E2E** | Élevée | 3-4 jours | P6 |

---

## 🎯 Prochaines étapes (Validation requise)

### Phase 1 : Spécifications détaillées
- [ ] Valider le schéma de données avec l'équipe
- [ ] Définir les données géographiques prioritaires (Gabon en premier ?)
- [ ] Valider le design UI/UX du sélecteur hiérarchique
- [ ] Décider : Import manuel ou intégration API externe (ex: GeoNames) ?

### Phase 2 : Développement
- [ ] Créer les collections DB et migrations
- [ ] Développer les API endpoints
- [ ] Créer les composants frontend
- [ ] Importer les données de base

### Phase 3 : Tests et déploiement
- [ ] Tests unitaires backend
- [ ] Tests E2E frontend
- [ ] Migration des données existantes
- [ ] Déploiement progressif

---

## 📝 Notes importantes

1. **Rétrocompatibilité** : Les villes existantes doivent continuer de fonctionner pendant la migration
2. **Performance** : Indexer les champs de référence (country_id, province_id, etc.)
3. **Données de référence** : Envisager une source de données géographiques externe (GeoNames, OpenStreetMap)
4. **UX** : Le sélecteur doit être simple et rapide, éviter trop de clics
5. **Mobile** : Penser à l'expérience mobile pour la sélection de localisation

---

## 🔗 Ressources utiles

- **GeoNames** : https://www.geonames.org/ (Base de données géographiques mondiale)
- **Gabon Provinces** : https://fr.wikipedia.org/wiki/Provinces_du_Gabon
- **React Select** : https://react-select.com/ (Pour le sélecteur en cascade)
- **Leaflet** : https://leafletjs.com/ (Pour la carte interactive)

---

**Version** : 1.0  
**Dernière mise à jour** : 15 Novembre 2025  
**Contact** : Équipe DevOps JLC Group  
**Status** : 📋 Planification V2
