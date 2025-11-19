# 🔐 Permissions Temporaires - Guide Utilisateur

## Vue d'ensemble

Le système de permissions temporaires permet d'accorder des accès limités dans le temps à des utilisateurs sans modifier leurs profils permanents.

## Cas d'usage

### 1. **Accès Projet Temporaire**
Un développeur externe a besoin d'accéder aux missions pendant la durée d'un projet (30 jours).

### 2. **Remplacement d'un Collègue**
Un employé remplace temporairement un responsable RH absent et a besoin de ses permissions pendant 2 semaines.

### 3. **Urgence Opérationnelle**
Un problème critique nécessite d'accorder temporairement des permissions élevées à un technicien (24 heures).

### 4. **Test de Nouvelles Fonctionnalités**
Accorder temporairement des permissions à des utilisateurs pilotes pour tester de nouvelles fonctionnalités (7 jours).

---

## API Endpoints

### 1. Accorder une Permission Temporaire

**POST** `/api/temporary-permissions`

**Permissions requises :** Administrateur

**Request Body :**
```json
{
  "user_id": "user_uuid",
  "permission_code": "missions.delete.own",
  "duration_hours": 24,
  "reason": "Urgence - résolution incident production"
}
```

**Response :**
```json
{
  "id": "temp_perm_uuid",
  "user_id": "user_uuid",
  "permission_code": "missions.delete.own",
  "permission_id": "perm_uuid",
  "granted_by": "admin_uuid",
  "granted_at": "2025-11-19T10:00:00Z",
  "expires_at": "2025-11-20T10:00:00Z",
  "reason": "Urgence - résolution incident production",
  "is_active": true
}
```

---

### 2. Consulter les Permissions Actives

**GET** `/api/temporary-permissions/active/{user_id}`

**Permissions :** Utilisateur peut voir ses propres permissions, Admin peut voir toutes

**Response :**
```json
[
  {
    "id": "temp_perm_uuid",
    "permission_code": "missions.delete.own",
    "expires_at": "2025-11-20T10:00:00Z",
    "reason": "Urgence production"
  }
]
```

---

### 3. Prolonger une Permission

**POST** `/api/temporary-permissions/{temp_perm_id}/extend`

**Permissions requises :** Administrateur

**Request Body :**
```json
{
  "additional_hours": 12
}
```

**Response :** Permission mise à jour avec nouvelle date d'expiration

---

### 4. Révoquer une Permission

**POST** `/api/temporary-permissions/{temp_perm_id}/revoke`

**Permissions requises :** Administrateur

**Request Body :**
```json
{
  "reason": "Incident résolu, accès n'est plus nécessaire"
}
```

---

### 5. Alertes d'Expiration

**GET** `/api/temporary-permissions/expiring-soon?hours_threshold=24`

**Permissions requises :** Administrateur

Récupère les permissions qui expirent dans les X heures (utile pour notifications).

---

### 6. Statistiques

**GET** `/api/temporary-permissions/statistics`

**Permissions requises :** Administrateur

**Response :**
```json
{
  "total": 150,
  "active": 42,
  "expired": 95,
  "revoked": 13,
  "top_permissions": [
    {
      "permission": "missions.delete.own",
      "count": 35
    },
    {
      "permission": "applications.approve",
      "count": 28
    }
  ]
}
```

---

### 7. Nettoyage Automatique

**POST** `/api/temporary-permissions/cleanup`

**Permissions requises :** Administrateur

Désactive toutes les permissions expirées. Peut être appelé par une tâche cron.

---

## Workflow Complet

### Scénario : Remplacement RH

```bash
# 1. Admin accorde la permission temporaire
curl -X POST http://api.example.com/api/temporary-permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "marie_dev",
    "permission_code": "applications.approve",
    "duration_hours": 336,
    "reason": "Remplacement Sophie RH - 2 semaines"
  }'

# 2. Marie peut maintenant utiliser la permission pendant 14 jours

# 3. Si besoin, prolonger
curl -X POST http://api.example.com/api/temporary-permissions/{id}/extend \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"additional_hours": 168}'

# 4. Ou révoquer anticipativement
curl -X POST http://api.example.com/api/temporary-permissions/{id}/revoke \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"reason": "Sophie est revenue plus tôt"}'
```

---

## Bonnes Pratiques

### ✅ À FAIRE

1. **Toujours spécifier une raison claire**
   - Facilite l'audit et la compréhension ultérieure
   
2. **Utiliser la durée minimale nécessaire**
   - Privilégier des périodes courtes (24-48h) sauf besoin spécifique
   
3. **Monitorer les expirations proches**
   - Configurer des notifications pour les permissions qui expirent bientôt
   
4. **Révoquer dès que possible**
   - Ne pas attendre l'expiration si l'accès n'est plus nécessaire

5. **Nettoyer régulièrement**
   - Exécuter le cleanup automatique quotidiennement via cron

### ❌ À ÉVITER

1. **Permissions temporaires trop longues**
   - Si > 30 jours, considérer une modification de profil permanent
   
2. **Octroi sans raison**
   - Toujours documenter le contexte pour l'audit
   
3. **Oublier de révoquer**
   - Risque de sécurité si l'accès reste actif inutilement

---

## Sécurité & Conformité

### Audit Trail

Toutes les actions sur les permissions temporaires sont enregistrées :
- Octroi (qui, quand, pourquoi)
- Prolongation
- Révocation
- Expiration automatique

### RGPD

- Les permissions expirées sont automatiquement désactivées
- L'historique est conservé pour conformité (90 jours par défaut)
- Possibilité de nettoyer l'historique selon politique de rétention

### Notifications Recommandées

1. **24h avant expiration** : Notifier l'utilisateur et l'admin
2. **À l'expiration** : Confirmer la désactivation
3. **En cas de révocation** : Notifier l'utilisateur concerné

---

## Intégration avec IAMService

Les permissions temporaires sont automatiquement prises en compte par `IAMService.user_has_permission()` :

```python
# Le système vérifie automatiquement :
# 1. Permissions permanentes du profil
# 2. Permissions temporaires actives
result = await iam_service.user_has_permission(
    user_id="user_123",
    permission_code="missions.delete.own"
)

if result.has_permission:
    # Permission OK (permanente OU temporaire)
    ...
```

---

## Support

Pour toute question ou problème :
- Documentation technique : `/app/auth-microservice/awana_auth/services/temporary_permissions_service.py`
- Tests unitaires : `/app/auth-microservice/tests/test_temporary_permissions.py`
- API complète : Swagger UI à `/docs`
