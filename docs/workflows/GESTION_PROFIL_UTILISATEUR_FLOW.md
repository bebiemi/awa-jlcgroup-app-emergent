# 📋 Gestion Profil Utilisateur

## 🎯 Vue d'Ensemble

**Catégorie:** User Management  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 2


Le workflow de gestion du profil permet aux utilisateurs de consulter et modifier leurs informations personnelles.
- **Profil unifié** : Informations auth + profil métier
- **Permissions** : Chaque utilisateur peut modifier son propre profil
- **Synchronisation** : Mise à jour dans auth_db.users et jlc_db.collaborator_profiles


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                      GESTION PROFIL UTILISATEUR                      │
└──────────────────────────────────────────────────────────────────────┘

1. GET /api/profiles/me
   │
   ├─→ Log user activity
   └─→ Retour données
   ↓
2. PUT /api/profiles/me
   │
   ├─→ Log user activity
   └─→ Retour données
   ↓
3. POST /api/users/{user_id}/profiles
   │
   ├─→ Log user activity
   └─→ Retour données

```

---

## 📡 Endpoints

### GET /api/profiles/me

**Description:** Log user activity

**Method:** `GET`

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

### PUT /api/profiles/me

**Description:** Log user activity

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

### POST /api/users/{user_id}/profiles

**Description:** Log user activity

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



---

## 🔐 Logique Implémentée

### Fonctions principales identifiées

- `get_my_profile()`
- `update_my_profile()`
- `upload_document()`
- `get_my_documents()`
- `delete_document()`

### Points clés de la logique

1. Validation des données d'entrée
2. Vérification des permissions
3. Traitement métier
4. Persistance en base de données
5. Retour de la réponse


---

## 🔍 Collections MongoDB Impactées

### auth_db.users
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### jlc_db.collaborator_profiles
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
curl -X GET "http://localhost:8001/api/profiles/me" \
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
| `/app/auth-microservice/profile_routes.py` | Implémentation du workflow |
| `/app/auth-microservice/user_detail_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
