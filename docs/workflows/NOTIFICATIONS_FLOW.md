# 📋 Notifications

## 🎯 Vue d'Ensemble

**Catégorie:** Communication  
**Status:** TO_DOCUMENT  
**Fichiers impliqués:** 1


Le workflow de notifications permet d'envoyer des messages in-app aux utilisateurs.
- **Types** : Info, Warning, Success, Error
- **Persistance** : Stockage en base pour historique
- **Marquage** : Possibilité de marquer comme lu


---

## 🔄 Flow Complet

```
┌──────────────────────────────────────────────────────────────────────┐
│                            NOTIFICATIONS                             │
└──────────────────────────────────────────────────────────────────────┘

1. GET /api/notifications
   │
   ├─→ Description à compléter
   └─→ Retour données
   ↓
2. POST /api/notifications/mark-read
   │
   ├─→ Description à compléter
   └─→ Retour données

```

---

## 📡 Endpoints

### GET /api/notifications

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

### POST /api/notifications/mark-read

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

### Fonctions principales identifiées

- `get_current_user_info()`
- `get_notifications()`
- `mark_notification_as_read()`
- `mark_all_notifications_as_read()`

### Points clés de la logique

1. Validation des données d'entrée
2. Vérification des permissions
3. Traitement métier
4. Persistance en base de données
5. Retour de la réponse


---

## 🔍 Collections MongoDB Impactées

### jlc_db.notifications
Collection utilisée pour le stockage des données.

**Champs principaux:**
- `id`: Identifiant unique (UUID)
- `created_at`: Date de création
- `updated_at`: Date de mise à jour

### jlc_db.emails
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
curl -X GET "http://localhost:8001/api/notifications" \
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
| `/app/auth-microservice/notification_routes.py` | Implémentation du workflow |


---

*Documentation générée le 26 November 2025*
