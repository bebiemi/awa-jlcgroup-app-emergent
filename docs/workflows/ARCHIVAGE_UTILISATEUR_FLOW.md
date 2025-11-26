# 📋 Archivage Utilisateur

## 🎯 Vue d'Ensemble

**Catégorie:** User Management  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow d'archivage permet de désactiver temporairement un utilisateur sans supprimer ses données.
- **Soft delete** : L'utilisateur reste en base avec flag `is_archived`
- **Restauration** : Possibilité de réactiver un utilisateur archivé
- **Permissions** : Réservé aux admins


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                        ARCHIVAGE UTILISATEUR                         │
└──────────────────────────────────────────────────────────────────────┘

1. PATCH /api/users/{user_id}/archive
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
2. PATCH /api/users/{user_id}/restore
   │
   ├─→ Description à compléter
   └─→ Retour données

```

---

## 📡 Endpoints

### PATCH /api/users/{user_id}/archive

**Description:** Description à compléter

**Method:** `PATCH`

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

### PATCH /api/users/{user_id}/restore

**Description:** Description à compléter

**Method:** `PATCH`

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

- `get_retention_days()`
- `archive_user()`
- `restore_user()`
- `purge_expired_users()`
- `get_retention_config()`

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
curl -X PATCH "http://localhost:8001/api/users/{user_id}/archive" \
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
| `/app/auth-microservice/user_archive_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
