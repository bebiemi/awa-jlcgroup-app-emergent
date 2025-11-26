# 📋 Création Mission

## 🎯 Vue d'Ensemble

**Catégorie:** Business  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow de création de mission permet aux entreprises de publier des offres d'emploi temporaire.
- **Permissions** : Réservé aux utilisateurs avec rôle `company` ou `collaborateur`
- **Validation** : Vérification des champs obligatoires (titre, description, dates)
- **Statut** : Les missions sont créées avec statut `draft` ou `published`


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                           CRÉATION MISSION                           │
└──────────────────────────────────────────────────────────────────────┘

1. POST /api/missions
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
2. PUT /api/missions/{id}
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
3. DELETE /api/missions/{id}
   │
   ├─→ Description à compléter
   └─→ Retour données

```

---

## 📡 Endpoints

### POST /api/missions

**Description:** Description à compléter

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <token>"
}
```

**Exemple de réponse:**
```json
{
  "message": "success"
}
```

---

### PUT /api/missions/{id}

**Description:** Description à compléter

**Method:** `PUT`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <token>"
}
```

**Exemple de réponse:**
```json
{
  "message": "success"
}
```

---

### DELETE /api/missions/{id}

**Description:** Description à compléter

**Method:** `DELETE`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <token>"
}
```

**Exemple de réponse:**
```json
{
  "message": "success"
}
```

---



---

## 🔐 Logique Implémentée

### Fonctions principales identifiées

- `validate_status()`
- `get_status_metadata()`
- `get_valid_statuses()`
- `check_application_restrictions()`
- `get_current_user()`

### Points clés de la logique

1. Validation des données d'entrée
2. Vérification des permissions
3. Traitement métier
4. Persistance en base de données
5. Retour de la réponse


---

## 🔍 Collections MongoDB Impactées

### jlc_db.missions
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### jlc_db.applications
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### jlc_db.besoins
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour



---

## ⚡ Points Clés

### ✅ Ce qui fonctionne bien


1. **Architecture claire** : Séparation des responsabilités
2. **Sécurité** : Validation des permissions à chaque étape
3. **Traçabilité** : Audit logs pour toutes les actions
4. **Robustesse** : Gestion des erreurs et cas limites


### ⚠️ Points d'attention


1. **Performance** : Attention aux requêtes N+1 sur gros volumes
2. **Validation** : Toujours vérifier les données côté serveur
3. **Permissions** : Double-check des droits d'accès


---

## 🧪 Tests

### Test 1: Endpoint principal

```bash
curl -X POST "http://localhost:8001/api/missions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

**Vérifications:**
- Status code 200
- Réponse JSON valide
- Données cohérentes



---

## 📚 Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `/app/auth-microservice/mission_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
