# Système de Notifications Email JLC

## Vue d'ensemble

Le système de notifications email permet d'envoyer automatiquement des alertes aux administrateurs lors d'événements critiques tels que les rollbacks de configuration et les modifications de feature flags.

## Architecture

### Composants

1. **EmailService** (`/app/auth-microservice/awana_auth/services/email_service.py`)
   - Service singleton pour l'envoi d'emails
   - Support SMTP avec TLS/SSL
   - Templates HTML et texte
   - Gestion des erreurs gracieuse

2. **Email Routes** (`/app/auth-microservice/email_routes.py`)
   - API REST pour tester et gérer les notifications
   - Endpoints protégés (admin/super-admin uniquement)

3. **Intégration avec Version Routes** (`/app/auth-microservice/version_routes.py`)
   - Envoi automatique de notifications lors des rollbacks
   - Exécution en arrière-plan via FastAPI BackgroundTasks

## Configuration

### Variables d'environnement

Créer ou modifier le fichier `/app/auth-microservice/.env` avec les paramètres suivants :

```bash
# Activer les notifications (true/false)
EMAIL_NOTIFICATIONS_ENABLED=true

# Configuration SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
SMTP_USE_TLS=true

# Expéditeur
SMTP_FROM_EMAIL=noreply@jlc.com
SMTP_FROM_NAME=JLC Application

# Destinataires (séparés par virgule)
ADMIN_NOTIFICATION_EMAILS=admin@jlc.com,tech-lead@jlc.com
```

### Fournisseurs SMTP Recommandés

#### 1. Gmail (Développement/Test)
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App Password
SMTP_USE_TLS=true
```
**Note**: Nécessite un "App Password" (https://myaccount.google.com/apppasswords)

#### 2. SendGrid (Production)
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxx
SMTP_USE_TLS=true
```
**Note**: Gratuit jusqu'à 100 emails/jour (https://signup.sendgrid.com/)

#### 3. Mailtrap (Test)
```bash
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=votre-username
SMTP_PASSWORD=votre-password
SMTP_USE_TLS=true
```
**Note**: Parfait pour tester sans envoyer de vrais emails (https://mailtrap.io/)

#### 4. Office365/Outlook
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=votre-email@outlook.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_USE_TLS=true
```

## API Endpoints

### 1. Vérifier la configuration
```bash
GET /api/emails/config
```
**Authentification**: Super-admin uniquement

**Réponse**:
```json
{
  "enabled": true,
  "configured": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "noreply@jlc.com",
  "smtp_use_tls": true,
  "from_email": "noreply@jlc.com",
  "from_name": "JLC Application",
  "admin_emails": ["admin@jlc.com", "tech-lead@jlc.com"],
  "admin_count": 2
}
```

### 2. Vérifier le statut
```bash
GET /api/emails/status
```
**Authentification**: Admin ou super-admin

**Réponse**:
```json
{
  "enabled": true,
  "configured": true,
  "smtp_configured": true,
  "recipients_configured": true,
  "recipients_count": 2,
  "status": "operational"
}
```

### 3. Envoyer un email de test
```bash
POST /api/emails/test
```
**Authentification**: Super-admin uniquement

**Body**:
```json
{
  "to_emails": ["test@example.com"],
  "subject": "Email de test JLC",
  "message": "Ceci est un test"
}
```

**Réponse**:
```json
{
  "message": "Email de test envoyé avec succès",
  "sent_to": ["test@example.com"],
  "count": 1
}
```

### 4. Tester une notification de rollback
```bash
POST /api/emails/test-rollback-notification
```
**Authentification**: Super-admin uniquement

**Réponse**:
```json
{
  "message": "Notification de test envoyée",
  "sent_to": ["admin@jlc.com", "tech-lead@jlc.com"],
  "count": 2
}
```

## Utilisation

### 1. Notification automatique lors du rollback

Les notifications sont envoyées automatiquement lorsqu'un rollback de configuration est effectué via l'API `/api/versions/rollback`.

**Exemple d'email envoyé**:

```
Sujet: ⚠️ Configuration Rollback Effectué - v20251104.180000

Bonjour,

Un rollback de configuration a été effectué sur l'application JLC.

Détails du Rollback
═══════════════════
Version précédente: v20251105.120000
Version cible: v20251104.180000
Raison: Correction d'une erreur dans la configuration des rôles
Date: 05/11/2025 13:15:30 UTC
Effectué par: Jean Dupont

Résumé des Changements
═══════════════════════
• Références ajoutées: 5
• Références modifiées: 3
• Références supprimées: 2

Cette opération a été exécutée automatiquement et peut avoir un impact sur les utilisateurs.
```

### 2. Envoi programmatique d'emails

```python
from awana_auth.services.email_service import get_email_service

email_service = get_email_service()

# Notification de rollback
result = email_service.send_rollback_notification(
    actor_name="Jean Dupont",
    version_from="v20251105.120000",
    version_to="v20251104.180000",
    reason="Correction d'erreur",
    rollback_time=datetime.now(timezone.utc),
    changes_summary={
        "added": 5,
        "modified": 3,
        "removed": 2
    }
)

if result["success"]:
    print(f"Email envoyé à {result['sent_to']}")
else:
    print(f"Erreur: {result['message']}")
```

### 3. Envoi d'email personnalisé

```python
html_content = """
<html>
<body>
    <h2>Notification personnalisée</h2>
    <p>Contenu de votre email ici</p>
</body>
</html>
"""

text_content = "Version texte de votre email"

result = email_service.send_email(
    to_emails=["admin@jlc.com"],
    subject="Notification importante",
    html_content=html_content,
    text_content=text_content
)
```

## Tests

### Test via curl

```bash
# 1. Se connecter en tant que super-admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/local/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"awana2025"}' | jq -r .access_token)

# 2. Vérifier la configuration email
curl -X GET http://localhost:8000/api/emails/config \
  -H "Authorization: Bearer $TOKEN"

# 3. Vérifier le statut
curl -X GET http://localhost:8000/api/emails/status \
  -H "Authorization: Bearer $TOKEN"

# 4. Envoyer un email de test
curl -X POST http://localhost:8000/api/emails/test \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["test@example.com"],
    "subject": "Test JLC",
    "message": "Email de test"
  }'

# 5. Tester la notification de rollback
curl -X POST http://localhost:8000/api/emails/test-rollback-notification \
  -H "Authorization: Bearer $TOKEN"
```

### Test via l'interface

1. Se connecter en tant que super-admin
2. Aller dans la section "Configuration Versions"
3. Effectuer un rollback
4. Vérifier que l'email a été reçu aux adresses configurées

## Gestion des Erreurs

### Service non configuré
Si `EMAIL_NOTIFICATIONS_ENABLED=false` ou si les paramètres SMTP sont manquants :
- Les endpoints retournent un statut `503 Service Unavailable`
- Le rollback fonctionne normalement mais sans notification email
- Les logs indiquent : `"Email service not configured. Email not sent."`

### Erreur d'envoi SMTP
En cas d'erreur SMTP (identifiants invalides, serveur inaccessible, etc.) :
- L'erreur est loggée
- Le rollback continue normalement
- L'API retourne `email_notification: "failed"` dans la réponse

### Destinataires manquants
Si `ADMIN_NOTIFICATION_EMAILS` est vide :
- `is_configured()` retourne `false`
- Aucun email n'est envoyé
- Les logs indiquent : `"No recipients specified"`

## Sécurité

### Authentification
- Tous les endpoints nécessitent une authentification JWT
- Les endpoints de configuration et test nécessitent le rôle `super_admin`
- Le endpoint de statut nécessite le rôle `admin` ou `super_admin`

### Mots de passe
- Les mots de passe SMTP ne sont **jamais** exposés via l'API
- Le endpoint `/api/emails/config` exclut le champ `smtp_password`
- Les mots de passe sont stockés uniquement dans les variables d'environnement

### Rate Limiting
- Les endpoints email sont protégés par le rate limiter global
- Limite par défaut : 10 requêtes par minute par IP

## Logs

Les logs d'email sont disponibles dans les logs de l'auth-microservice :

```bash
# Consulter les logs
tail -f /var/log/supervisor/auth-microservice.err.log | grep email

# Exemples de logs
INFO:email_service:Email sent successfully to 2 recipients
ERROR:email_service:Failed to send email: Authentication failed
WARNING:email_service:Email service not configured. Email not sent.
```

## Monitoring

### Métriques à surveiller

1. **Taux de succès d'envoi**
   - Vérifier régulièrement les logs pour détecter les échecs
   
2. **Temps de réponse SMTP**
   - Les timeouts peuvent indiquer un problème avec le serveur SMTP

3. **Configuration**
   - Utiliser `GET /api/emails/status` pour un health check

### Alertes recommandées

- Alerte si `configured: false` en production
- Alerte si plus de 3 échecs d'envoi consécutifs
- Alerte si les emails ne sont pas reçus après un rollback

## Migration et Déploiement

### Checklist avant déploiement

1. ✅ Configurer les variables d'environnement SMTP
2. ✅ Ajouter les emails admin dans `ADMIN_NOTIFICATION_EMAILS`
3. ✅ Tester l'envoi avec `/api/emails/test`
4. ✅ Activer avec `EMAIL_NOTIFICATIONS_ENABLED=true`
5. ✅ Effectuer un rollback de test
6. ✅ Vérifier la réception des emails

### Rollback de la fonctionnalité

Si nécessaire, désactiver les notifications :
```bash
EMAIL_NOTIFICATIONS_ENABLED=false
```
Puis redémarrer le service :
```bash
sudo supervisorctl restart auth-microservice
```

## Développements Futurs

### Fonctionnalités à ajouter

1. **Templates personnalisables**
   - Permettre aux admins de personnaliser les templates d'email
   - Stockage des templates dans la base de données

2. **Notifications supplémentaires**
   - Feature flag désactivé en production
   - Création/suppression de rôle super-admin
   - Échecs d'authentification répétés

3. **Dashboard d'emails**
   - Historique des emails envoyés
   - Statistiques (taux de succès, temps d'envoi)
   - Gestion des destinataires via UI

4. **Multi-canal**
   - Support Slack, Discord, Teams
   - Webhooks personnalisés
   - SMS pour les alertes critiques

5. **Files d'attente**
   - Utiliser Celery pour les envois asynchrones
   - Retry automatique en cas d'échec
   - Priorisation des emails

## FAQ

### Q: Puis-je utiliser plusieurs serveurs SMTP ?
**R**: Actuellement non, mais vous pouvez configurer un seul serveur SMTP. Pour une solution multi-serveur, il faudrait étendre la classe `EmailService`.

### Q: Les emails sont-ils envoyés même si le rollback échoue ?
**R**: Non, les emails sont envoyés uniquement si le rollback réussit (status code 200).

### Q: Puis-je désactiver temporairement les notifications ?
**R**: Oui, définissez `EMAIL_NOTIFICATIONS_ENABLED=false` et redémarrez le service.

### Q: Comment ajouter/retirer des destinataires ?
**R**: Modifiez `ADMIN_NOTIFICATION_EMAILS` dans `.env` et redémarrez le service.

### Q: Les emails sont-ils en français ou anglais ?
**R**: Actuellement en français uniquement. L'internationalisation peut être ajoutée ultérieurement.

### Q: Que se passe-t-il si le serveur SMTP est temporairement indisponible ?
**R**: L'email échoue mais le rollback continue. L'erreur est loggée. Il n'y a pas de retry automatique actuellement.

## Support

Pour toute question ou problème :
1. Vérifier les logs : `tail -f /var/log/supervisor/auth-microservice.err.log`
2. Tester la configuration : `GET /api/emails/status`
3. Consulter cette documentation
4. Contacter l'équipe technique

## Changelog

### Version 1.0 (05/11/2025)
- ✅ Système d'envoi d'emails avec SMTP
- ✅ Notification automatique pour rollbacks
- ✅ API REST pour tests et gestion
- ✅ Support Gmail, SendGrid, Mailtrap, Office365
- ✅ Templates HTML et texte
- ✅ Gestion des erreurs gracieuse
- ✅ Protection par authentification et rôles
