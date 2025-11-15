# Configuration Schema V2 - Features Phase 2

## Collections MongoDB

### 1. `app_config` Collection

Configuration centralisée pour toutes les fonctionnalités configurables.

```json
{
  "_id": ObjectId,
  "key": "profiles.badge_new_user",
  "value": {
    "enabled": true,
    "expiration_days": 7,
    "expiration_mode": "first_view",  // "first_view" | "creation_date" | "both"
    "badge_text": {
      "fr": "NOUVEAU",
      "en": "NEW"
    }
  },
  "description": "Configuration du badge 'Nouveau profil'",
  "category": "profiles",
  "updated_at": ISODate,
  "updated_by": "admin_user_id"
}
```

```json
{
  "_id": ObjectId,
  "key": "documents.categories",
  "value": [
    {
      "id": "identity",
      "name": {"fr": "Pièce d'identité", "en": "Identity Document"},
      "required": true,
      "expirable": true,
      "retention_years": 5,
      "allowed_formats": ["pdf", "jpg", "png"],
      "max_size_mb": 5,
      "required_for_roles": ["interim", "company", "agency"]
    },
    {
      "id": "contract",
      "name": {"fr": "Contrat", "en": "Contract"},
      "required": false,
      "expirable": false,
      "retention_years": 10,
      "allowed_formats": ["pdf"],
      "max_size_mb": 10,
      "required_for_roles": ["interim"]
    },
    {
      "id": "payslip",
      "name": {"fr": "Fiche de paie", "en": "Payslip"},
      "required": false,
      "expirable": false,
      "retention_years": 5,
      "allowed_formats": ["pdf"],
      "max_size_mb": 5,
      "required_for_roles": ["interim"]
    },
    {
      "id": "medical",
      "name": {"fr": "Certificat médical", "en": "Medical Certificate"},
      "required": true,
      "expirable": true,
      "expiration_reminder_days": [30, 15, 7],
      "retention_years": 3,
      "allowed_formats": ["pdf"],
      "max_size_mb": 5,
      "required_for_roles": ["interim"]
    },
    {
      "id": "siret",
      "name": {"fr": "Extrait SIRET", "en": "SIRET Extract"},
      "required": true,
      "expirable": false,
      "retention_years": null,
      "allowed_formats": ["pdf"],
      "max_size_mb": 5,
      "required_for_roles": ["company"]
    }
  ],
  "description": "Catégories de documents configurables",
  "category": "documents",
  "updated_at": ISODate,
  "updated_by": "admin_user_id"
}
```

```json
{
  "_id": ObjectId,
  "key": "notifications.types",
  "value": {
    "document_expiring": {
      "enabled": true,
      "channels": ["email", "in_app"],
      "template": "document_expiring",
      "reminder_days": [30, 15, 7, 1]
    },
    "new_mission_match": {
      "enabled": true,
      "channels": ["email", "in_app", "push"],
      "template": "new_mission_match",
      "min_match_score": 70
    },
    "application_status_change": {
      "enabled": true,
      "channels": ["email", "in_app"],
      "template": "application_status_change"
    },
    "new_message": {
      "enabled": true,
      "channels": ["in_app", "push"],
      "template": "new_message"
    },
    "profile_validation": {
      "enabled": true,
      "channels": ["email", "in_app"],
      "template": "profile_validation"
    }
  },
  "description": "Types de notifications configurables",
  "category": "notifications",
  "updated_at": ISODate,
  "updated_by": "admin_user_id"
}
```

```json
{
  "_id": ObjectId,
  "key": "dashboard.widgets",
  "value": {
    "profile_completion": {
      "enabled": true,
      "priority": 1,
      "roles": ["interim", "company", "agency"]
    },
    "missing_documents": {
      "enabled": true,
      "priority": 2,
      "roles": ["interim", "company"]
    },
    "recent_notifications": {
      "enabled": true,
      "priority": 3,
      "max_items": 5,
      "roles": ["all"]
    },
    "active_applications": {
      "enabled": true,
      "priority": 4,
      "roles": ["interim"]
    },
    "recommended_missions": {
      "enabled": true,
      "priority": 5,
      "max_items": 5,
      "roles": ["interim", "postulant"]
    }
  },
  "description": "Widgets du dashboard configurables",
  "category": "dashboard",
  "updated_at": ISODate,
  "updated_by": "admin_user_id"
}
```

### 2. `users` Collection (Ajouts)

Extensions au schéma utilisateur existant :

```json
{
  // ... existing fields ...
  "first_profile_view_at": ISODate,  // Date de première consultation du profil
  "badge_visible": true,  // Badge "Nouveau" visible ou non
  "dashboard_preferences": {
    "widgets_order": ["profile_completion", "missing_documents", "notifications"],
    "collapsed_widgets": [],
    "theme": "light"
  }
}
```

### 3. `documents` Collection (Amélioration)

```json
{
  "_id": ObjectId,
  "user_id": "string",
  "category_id": "identity",  // Référence à app_config documents.categories
  "file_name": "carte_identite.pdf",
  "file_url": "s3://...",
  "file_size": 1024000,
  "file_type": "pdf",
  "expiration_date": ISODate,  // null si non expirable
  "reminder_sent": {
    "30_days": ISODate,
    "15_days": ISODate,
    "7_days": ISODate,
    "1_day": ISODate
  },
  "status": "valid",  // "valid" | "expiring_soon" | "expired" | "pending_review"
  "uploaded_at": ISODate,
  "uploaded_by": "user_id",
  "verified_at": ISODate,
  "verified_by": "admin_user_id",
  "metadata": {
    "original_filename": "Carte Identité Jean Dupont.pdf",
    "mime_type": "application/pdf",
    "scan_result": "clean",
    "ocr_data": {}  // Données OCR si applicable
  }
}
```

### 4. `notifications` Collection

```json
{
  "_id": ObjectId,
  "user_id": "string",
  "type": "document_expiring",  // Référence à app_config notifications.types
  "title": {
    "fr": "Document bientôt expiré",
    "en": "Document expiring soon"
  },
  "message": {
    "fr": "Votre carte d'identité expire dans 15 jours",
    "en": "Your identity card expires in 15 days"
  },
  "data": {
    "document_id": "doc_123",
    "days_remaining": 15,
    "action_url": "/profile?tab=documents"
  },
  "channels": ["email", "in_app"],
  "sent_via": {
    "email": {
      "sent_at": ISODate,
      "status": "delivered"
    },
    "in_app": {
      "sent_at": ISODate,
      "read_at": ISODate
    }
  },
  "priority": "high",  // "low" | "medium" | "high" | "urgent"
  "read": false,
  "created_at": ISODate,
  "expires_at": ISODate  // Auto-suppression après X jours
}
```

## API Endpoints à Créer/Améliorer

### Configuration Endpoints

```python
GET    /api/config/app?key=profiles.badge_new_user
GET    /api/config/app?category=documents
POST   /api/config/app                    # Admin only
PATCH  /api/config/app/{key}              # Admin only
DELETE /api/config/app/{key}              # Admin only
```

### Profile Endpoints (Amélioration)

```python
GET    /api/profiles/me                   # Ajouter badge_visible, first_profile_view_at
PATCH  /api/profiles/me/view              # Mark profile as viewed (update first_profile_view_at)
GET    /api/profiles/me/completion        # Détails de la complétion
```

### Documents Endpoints (Amélioration)

```python
GET    /api/documents/me                  # Tous mes documents
GET    /api/documents/me/missing          # Documents manquants requis
GET    /api/documents/me/expiring         # Documents expirant bientôt
POST   /api/documents/me                  # Upload document
PATCH  /api/documents/me/{id}             # Update document
DELETE /api/documents/me/{id}             # Delete document
GET    /api/documents/categories          # Liste catégories configurables
```

### Notifications Endpoints

```python
GET    /api/notifications/me              # Mes notifications
GET    /api/notifications/me/unread       # Non lues
PATCH  /api/notifications/me/{id}/read    # Marquer comme lu
PATCH  /api/notifications/me/read-all     # Tout marquer comme lu
DELETE /api/notifications/me/{id}         # Supprimer
GET    /api/notifications/settings        # Préférences notifications
PATCH  /api/notifications/settings        # Modifier préférences
```

### Dashboard Endpoints

```python
GET    /api/dashboard/me                  # Dashboard complet
GET    /api/dashboard/me/widgets          # Liste widgets configurés
PATCH  /api/dashboard/me/preferences      # Sauvegarder préférences
```

## Environment Variables (Ajouts)

```bash
# Documents
DOCUMENTS_STORAGE_PROVIDER=s3  # "s3" | "local" | "azure"
DOCUMENTS_S3_BUCKET=jlc-documents
DOCUMENTS_MAX_SIZE_MB=10
DOCUMENTS_RETENTION_CHECK_CRON="0 2 * * *"  # Daily at 2AM

# Notifications
NOTIFICATIONS_ENABLED=true
NOTIFICATIONS_EMAIL_ENABLED=true
NOTIFICATIONS_PUSH_ENABLED=false
NOTIFICATIONS_EXPIRY_DAYS=30

# Badge
BADGE_NEW_USER_DAYS=7
```

## IAM Permissions (Ajouts)

```python
# Documents
'documents.read_own'
'documents.upload_own'
'documents.delete_own'
'documents.read_all'      # Admin
'documents.verify'        # Admin
'documents.configure'     # Super Admin

# Notifications
'notifications.read_own'
'notifications.manage_own'
'notifications.send'      # System/Admin

# Dashboard
'dashboard.view_own'
'dashboard.customize'

# Config
'config.read'
'config.manage'           # Admin only
```

## Migration Script

```python
# /app/auth-microservice/scripts/init_config_v2.py

async def init_app_config():
    """Initialize app_config collection with default values"""
    configs = [
        {
            "key": "profiles.badge_new_user",
            "value": {...},
            "category": "profiles"
        },
        # ... autres configs
    ]
    
    for config in configs:
        await db.app_config.update_one(
            {"key": config["key"]},
            {"$set": config},
            upsert=True
        )
```

## Usage Examples

### Backend (FastAPI)

```python
from config_service import get_config

# Get badge configuration
badge_config = await get_config("profiles.badge_new_user")
expiration_days = badge_config["value"]["expiration_days"]

# Get document categories
doc_categories = await get_config("documents.categories")
for category in doc_categories["value"]:
    if category["required"] and user_role in category["required_for_roles"]:
        # Check if user has this document
        pass
```

### Frontend (React)

```typescript
// Hook to get configuration
const { data: badgeConfig } = useGetConfigQuery('profiles.badge_new_user')
const { data: docCategories } = useGetConfigQuery('documents.categories')

// Use in component
if (badgeConfig?.value?.enabled) {
  const expirationDays = badgeConfig.value.expiration_days
  // Show badge if within expiration period
}
```

---

**Version** : 2.0  
**Date** : 15 Novembre 2025  
**Status** : Schéma pour implémentation Phase 2
