# 📋 Authentification Google

## 🎯 Vue d'Ensemble

**Catégorie:** Authentication  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow Google OAuth permet la connexion via compte Google.
- **OAuth 2.0** : Protocole standard Google
- **Auto-provisioning** : Création automatique du compte utilisateur
- **Récupération profil** : Email, nom, photo depuis Google


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                       AUTHENTIFICATION GOOGLE                        │
└──────────────────────────────────────────────────────────────────────┘

1. POST /api/auth/google/login
   │
   ├─→ Save OAuth state in MongoDB with TTL
   └─→ Retour données
   ↓
2. POST /api/auth/google/callback
   │
   ├─→ Save OAuth state in MongoDB with TTL
   └─→ Retour données

```

---

## 📡 Endpoints

### POST /api/auth/google/login

**Description:** Save OAuth state in MongoDB with TTL

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

### POST /api/auth/google/callback

**Description:** Save OAuth state in MongoDB with TTL

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

- `save_state()`
- `get_and_delete_state()`
- `create_user_profile()`
- `google_login()`
- `google_callback()`

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

### auth_db.sessions
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### auth_db.iam_groups
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
curl -X POST "http://localhost:8001/api/auth/google/login" \
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
| `/app/auth-microservice/google_auth_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
