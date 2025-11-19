# 📜 Audit Trail IAM - Guide Utilisateur

## Vue d'ensemble

Le système d'audit trail enregistre toutes les actions sensibles effectuées dans le système IAM pour assurer la traçabilité, la sécurité et la conformité réglementaire.

---

## Types d'Actions Auditées

### Profils
- `profile_created` - Création d'un nouveau profil
- `profile_updated` - Modification d'un profil existant
- `profile_deleted` - Suppression d'un profil
- `profile_assigned` - Attribution d'un profil à un utilisateur
- `profile_removed` - Retrait d'un profil d'un utilisateur

### Permissions
- `permission_created` - Création d'une nouvelle permission
- `permission_updated` - Modification d'une permission
- `permission_deleted` - Suppression d'une permission  
- `permission_checked` - Vérification de permission (haute fréquence)
- `permission_denied` - Tentative d'accès refusée

### Permissions Temporaires
- `temp_permission_granted` - Octroi d'une permission temporaire
- `temp_permission_revoked` - Révocation d'une permission temporaire
- `temp_permission_expired` - Expiration automatique

### Groupes
- `group_created` - Création d'un groupe
- `user_added_to_group` - Ajout d'un utilisateur à un groupe
- `user_removed_from_group` - Retrait d'un utilisateur d'un groupe

### Système
- `cache_invalidated` - Invalidation du cache IAM
- `iam_audit_performed` - Audit IAM effectué

---

## Niveaux de Sévérité

| Niveau | Description | Utilisation |
|--------|-------------|-------------|
| **INFO** | Information normale | Actions courantes, succès |
| **WARNING** | Avertissement | Actions inhabituelles nécessitant attention |
| **ERROR** | Erreur | Actions échouées |
| **CRITICAL** | Critique | Actions sensibles de sécurité |

---

## API Endpoints

### 1. Historique Utilisateur

**GET** `/api/iam-audit/user/{user_id}?limit=100&start_date=2025-11-01`

**Permissions :** Utilisateur peut voir son propre historique, Admin peut voir tous

**Response :**
```json
[
  {
    "id": "audit_entry_uuid",
    "timestamp": "2025-11-19T14:30:00Z",
    "action": "profile_updated",
    "severity": "info",
    "actor_id": "admin_uuid",
    "actor_type": "admin",
    "target_type": "profile",
    "target_id": "profile_uuid",
    "target_name": "Entreprise Profile",
    "details": {
      "fields_changed": ["permissions"],
      "permissions_added": 3
    },
    "result": "success"
  }
]
```

---

### 2. Actions Échouées (Monitoring)

**GET** `/api/iam-audit/failed-actions?hours_back=24&limit=50`

**Permissions requises :** Administrateur

Récupère toutes les actions qui ont échoué dans les X dernières heures.

**Utilisation :** Dashboard de monitoring, détection d'anomalies

---

### 3. Alertes de Sécurité

**GET** `/api/iam-audit/security-alerts?hours_back=24`

**Permissions requises :** Administrateur

Récupère les entrées CRITICAL et ERROR.

**Response :**
```json
[
  {
    "timestamp": "2025-11-19T12:00:00Z",
    "action": "permission_deleted",
    "severity": "critical",
    "actor_id": "admin_uuid",
    "target_name": "applications.approve",
    "details": {
      "affected_users": 15
    }
  }
]
```

---

### 4. Recherche Avancée

**POST** `/api/iam-audit/search`

**Permissions requises :** Administrateur

**Request Body :**
```json
{
  "action": "permission_denied",
  "actor_id": "user_uuid",
  "severity": "warning",
  "result": "failure",
  "start_date": "2025-11-01T00:00:00Z",
  "end_date": "2025-11-19T23:59:59Z",
  "search_text": "missions"
}
```

**Response :**
```json
{
  "total": 150,
  "limit": 100,
  "skip": 0,
  "results": [...]
}
```

---

### 5. Statistiques d'Audit

**GET** `/api/iam-audit/statistics?start_date=2025-11-01&end_date=2025-11-19`

**Permissions requises :** Administrateur

**Response :**
```json
{
  "period": {
    "start": "2025-11-01T00:00:00Z",
    "end": "2025-11-19T23:59:59Z"
  },
  "total_actions": 5432,
  "by_action": [
    {
      "action": "permission_checked",
      "count": 3210
    },
    {
      "action": "profile_updated",
      "count": 450
    }
  ],
  "by_severity": {
    "info": 4800,
    "warning": 500,
    "error": 100,
    "critical": 32
  },
  "by_result": {
    "success": 5000,
    "failure": 400,
    "denied": 32
  },
  "top_users": [
    {
      "user_id": "admin_1",
      "username": "admin",
      "count": 850
    }
  ]
}
```

---

### 6. Rapport de Conformité

**GET** `/api/iam-audit/compliance-report?start_date=2025-11-01&end_date=2025-11-30`

**Permissions requises :** Administrateur

Génère un rapport RGPD/SOC2/ISO 27001 compliant.

**Response :**
```json
{
  "report_period": {
    "start": "2025-11-01T00:00:00Z",
    "end": "2025-11-30T23:59:59Z"
  },
  "sensitive_actions": 45,
  "sensitive_details": [
    {
      "action": "permission_deleted",
      "actor": "admin_uuid",
      "target": "applications.approve",
      "timestamp": "2025-11-15T10:30:00Z"
    }
  ],
  "permissions_denied": 128,
  "security_alerts": 8,
  "compliance_status": "compliant"
}
```

---

### 7. Nettoyage RGPD

**POST** `/api/iam-audit/cleanup?days_to_keep=90`

**Permissions requises :** Administrateur

Supprime les entrées plus anciennes que X jours (minimum 30 jours).

**Note :** Les entrées CRITICAL sont **toujours conservées**.

---

## Cas d'Usage

### 1. Investigation de Sécurité

**Scénario :** Identifier toutes les tentatives d'accès refusées d'un utilisateur

```bash
curl -X POST http://api.example.com/api/iam-audit/search \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "actor_id": "suspicious_user_id",
    "action": "permission_denied",
    "start_date": "2025-11-01T00:00:00Z"
  }'
```

---

### 2. Dashboard de Monitoring

**Afficher les actions échouées en temps réel**

```javascript
// Frontend : Rafraîchir toutes les 30 secondes
const fetchFailedActions = async () => {
  const response = await fetch('/api/iam-audit/failed-actions?hours_back=1', {
    headers: { Authorization: `Bearer ${adminToken}` }
  });
  const failed = await response.json();
  updateDashboard(failed);
};

setInterval(fetchFailedActions, 30000);
```

---

### 3. Audit Mensuel

**Générer un rapport pour la direction**

```bash
# Statistiques du mois
curl -X GET "http://api.example.com/api/iam-audit/statistics?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer $ADMIN_TOKEN" > monthly_audit_stats.json

# Rapport de conformité
curl -X GET "http://api.example.com/api/iam-audit/compliance-report?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer $ADMIN_TOKEN" > monthly_compliance_report.json
```

---

### 4. Alerte Automatique

**Détecter les activités suspectes**

```python
import requests
from datetime import datetime, timedelta

def check_security_alerts():
    """Vérifier les alertes toutes les heures"""
    response = requests.get(
        "http://api.example.com/api/iam-audit/security-alerts?hours_back=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    alerts = response.json()
    
    if len(alerts) > 10:
        # Envoyer notification urgente
        send_alert_to_security_team(alerts)
    
    return alerts
```

---

## Conformité Réglementaire

### RGPD (Règlement Général sur la Protection des Données)

**Exigences satisfaites :**
- ✅ Traçabilité complète des accès aux données
- ✅ Rétention configurable des logs (minimum 30 jours)
- ✅ Droit à l'oubli (cleanup après période de rétention)
- ✅ Audit des actions sensibles

**Recommandation :** 90 jours de rétention minimum

---

### SOC 2 (Service Organization Control)

**Exigences satisfaites :**
- ✅ Logging de toutes les actions administratives
- ✅ Contrôles d'accès enregistrés
- ✅ Monitoring des échecs d'authentification
- ✅ Rapports d'audit automatisés

**Recommandation :** 365 jours de rétention

---

### ISO 27001

**Exigences satisfaites :**
- ✅ Gestion des événements de sécurité
- ✅ Traçabilité des changements de permissions
- ✅ Alertes sur actions critiques
- ✅ Rapports de conformité

**Recommandation :** 180 jours de rétention

---

## Bonnes Pratiques

### ✅ À FAIRE

1. **Configurer des alertes automatiques**
   - Actions échouées > 10/heure
   - Alertes critiques en temps réel
   
2. **Réviser régulièrement les statistiques**
   - Dashboard hebdomadaire pour l'équipe sécurité
   - Rapport mensuel pour la direction
   
3. **Implémenter un pipeline de notification**
   ```
   Audit Trail → Détection anomalie → Slack/Email → Équipe sécurité
   ```
   
4. **Archiver les rapports de conformité**
   - Conserver hors système pour audit externe
   - Format PDF + JSON

5. **Tester le système de cleanup**
   - Exécution mensuelle avec vérification

### ❌ À ÉVITER

1. **Ne jamais désactiver l'audit**
   - Même en développement (utiliser une base de test)
   
2. **Éviter les requêtes sans filtre de date**
   - Performance et volume de données
   
3. **Ne pas ignorer les alertes CRITICAL**
   - Nécessitent investigation immédiate
   
4. **Ne pas supprimer manuellement les entrées**
   - Utiliser uniquement l'endpoint de cleanup

---

## Performance

### Optimisations Intégrées

1. **Index MongoDB**
   ```javascript
   db.iam_audit_trail.createIndex({ "actor_id": 1, "timestamp": -1 })
   db.iam_audit_trail.createIndex({ "action": 1, "timestamp": -1 })
   db.iam_audit_trail.createIndex({ "severity": 1, "timestamp": -1 })
   ```

2. **Pagination automatique**
   - Limite par défaut : 100 entrées
   - Maximum : 500 entrées

3. **Agrégations optimisées**
   - Pipeline MongoDB pour statistiques
   - Cache des top users

### Recommandations

- **Production** : Nettoyer tous les 30 jours via cron
- **Archivage** : Exporter les anciens logs vers S3/stockage froid
- **Monitoring** : Surveiller la taille de la collection `iam_audit_trail`

---

## Support

Pour toute question ou problème :
- Documentation technique : `/app/auth-microservice/awana_auth/services/iam_audit_service.py`
- Tests unitaires : `/app/auth-microservice/tests/test_iam_audit.py`
- API complète : Swagger UI à `/docs`
