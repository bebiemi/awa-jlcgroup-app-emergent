# 📋 Upload Documents

## 🎯 Vue d'Ensemble

**Catégorie:** Documents  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow d'upload de documents permet aux utilisateurs de télécharger des fichiers (CV, contrats, etc.).
- **Storage** : Stockage local dans `/app/uploads/`
- **Types acceptés** : PDF, DOCX, images
- **Sécurité** : Validation du type MIME et taille max


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                           UPLOAD DOCUMENTS                           │
└──────────────────────────────────────────────────────────────────────┘

1. POST /api/documents/upload
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
2. GET /api/documents/{id}
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
3. DELETE /api/documents/{id}
   │
   ├─→ Description à compléter
   └─→ Retour données

```

---

## 📡 Endpoints

### POST /api/documents/upload

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

### GET /api/documents/{id}

**Description:** Description à compléter

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

### DELETE /api/documents/{id}

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

- `get_current_user()`
- `upload_document()`
- `download_document()`
- `get_application_documents()`
- `delete_document()`

### Points clés de la logique

1. Validation des données d'entrée
2. Vérification des permissions
3. Traitement métier
4. Persistance en base de données
5. Retour de la réponse


---

## 🔍 Collections MongoDB Impactées

### jlc_db.documents
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### jlc_db.uploads
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
curl -X POST "http://localhost:8001/api/documents/upload" \
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
| `/app/auth-microservice/document_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
