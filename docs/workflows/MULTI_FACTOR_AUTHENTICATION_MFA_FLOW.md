# 📋 Multi-Factor Authentication (MFA)

## 🎯 Vue d'Ensemble

**Catégorie:** Security  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow MFA ajoute une couche de sécurité supplémentaire avec authentification à deux facteurs.
- **TOTP** : Time-based One-Time Password (Google Authenticator, Authy)
- **Setup** : Génération QR code pour configuration initiale
- **Vérification** : Code requis à chaque connexion si MFA activé


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                  MULTI-FACTOR AUTHENTICATION (MFA)                   │
└──────────────────────────────────────────────────────────────────────┘

1. POST /api/auth/mfa/setup
   │
   ├─→ Audit logging for all MFA events
   └─→ Retour données
   ↓
2. POST /api/auth/mfa/verify
   │
   ├─→ Audit logging for all MFA events
   └─→ Retour données
   ↓
3. POST /api/auth/mfa/disable
   │
   ├─→ Audit logging for all MFA events
   └─→ Retour données

```

---

## 📡 Endpoints

### POST /api/auth/mfa/setup

**Description:** Audit logging for all MFA events

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

### POST /api/auth/mfa/verify

**Description:** Audit logging for all MFA events

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

### POST /api/auth/mfa/disable

**Description:** Audit logging for all MFA events

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

- `check_mfa_rate_limit()`
- `log_mfa_event()`
- `get_mfa_status()`
- `setup_totp()`
- `verify_totp_setup()`

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
curl -X POST "http://localhost:8001/api/auth/mfa/setup" \
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
| `/app/auth-microservice/mfa_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
