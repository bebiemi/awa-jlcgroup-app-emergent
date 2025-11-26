# 📋 Validation Candidature

## 🎯 Vue d'Ensemble

**Catégorie:** Business  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow de validation permet aux entreprises et collaborateurs d'approuver ou rejeter les candidatures.
- **Permissions** : Réservé aux entreprises et collaborateurs RH
- **Actions** : Approve ou Reject avec commentaire
- **Notifications** : Email automatique au candidat


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                        VALIDATION CANDIDATURE                        │
└──────────────────────────────────────────────────────────────────────┘

1. POST /api/applications/{id}/approve
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
2. POST /api/applications/{id}/reject
   │
   ├─→ Description à compléter
   └─→ Retour données

```

---

## 📡 Endpoints

### POST /api/applications/{id}/approve

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

### POST /api/applications/{id}/reject

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



---

## 🔐 Logique Implémentée

Logique à documenter

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
curl -X POST "http://localhost:8001/api/applications/{id}/approve" \
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
| `/app/auth-microservice/application_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
