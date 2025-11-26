# 📋 Réinitialisation Mot de Passe

## 🎯 Vue d'Ensemble

**Catégorie:** Security  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow de réinitialisation permet aux utilisateurs de changer leur mot de passe en cas d'oubli.
- **Token temporaire** : Génération d'un token unique avec expiration
- **Email** : Envoi du lien de réinitialisation par email
- **Sécurité** : Le token est valide 1 heure uniquement


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                    RÉINITIALISATION MOT DE PASSE                     │
└──────────────────────────────────────────────────────────────────────┘

1. POST /api/auth/forgot-password
   │
   ├─→ Create validation record for new user registration
   └─→ Retour données
   ↓
2. POST /api/auth/reset-password
   │
   ├─→ Create validation record for new user registration
   └─→ Retour données
   ↓
3. POST /api/users/{user_id}/password/admin-update
   │
   ├─→ Create validation record for new user registration
   └─→ Retour données

```

---

## 📡 Endpoints

### POST /api/auth/forgot-password

**Description:** Create validation record for new user registration

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

### POST /api/auth/reset-password

**Description:** Create validation record for new user registration

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

### POST /api/users/{user_id}/password/admin-update

**Description:** Create validation record for new user registration

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

- `create_validation_record()`
- `create_user_profile_if_not_exists()`
- `entraid_login()`
- `entraid_callback()`
- `entraid_token_login()`

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

### auth_db.password_reset_tokens
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### auth_db.email_verifications
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
curl -X POST "http://localhost:8001/api/auth/forgot-password" \
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
| `/app/auth-microservice/awana_auth_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
