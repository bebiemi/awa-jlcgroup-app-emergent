================================================================================
LISTE COMPLÈTE DES ENDPOINTS - APPLICATION JLC
================================================================================

🔐 AUTH MICROSERVICE (Port 8000 - /api)
--------------------------------------------------------------------------------

📁 Auth & Users
   POST /api/auth/local/register
   POST /api/auth/local/login
   POST /api/auth/local/login/complete
   POST /api/auth/logout
   GET /api/auth/me
   GET /api/auth/users
   GET /api/auth/users/{user_id}
   PATCH /api/auth/users/{user_id}
   PATCH /api/auth/users/{user_id}/status
   DELETE /api/auth/users/{user_id}
   POST /api/auth/password-reset/request
   POST /api/auth/password-reset/confirm

📁 Google OAuth
   GET /api/auth/google/login
   GET /api/auth/google/callback
   GET /api/auth/google/status

📁 MFA
   GET /api/auth/mfa/status
   POST /api/auth/mfa/setup/totp
   POST /api/auth/mfa/setup/totp/verify
   POST /api/auth/mfa/setup/email
   POST /api/auth/mfa/backup-codes/regenerate
   DELETE /api/auth/mfa/method/{method}

📁 Roles
   GET /api/auth/roles
   POST /api/auth/roles
   GET /api/auth/roles/{role_id}
   PUT /api/auth/roles/{role_id}
   DELETE /api/auth/roles/{role_id}

📁 Security
   POST /api/auth/security/users
   GET /api/auth/admin/stats
   POST /api/auth/admin/users/{user_id}/mfa/reset

📁 Profiles
   GET /api/profiles/me
   PUT /api/profiles/me
   GET /api/profiles/{profile_id}

📁 Locations
   GET /api/locations
   POST /api/locations
   GET /api/locations/{location_id}
   PUT /api/locations/{location_id}
   DELETE /api/locations/{location_id}

📁 Validations
   GET /api/validations
   GET /api/validations/me
   POST /api/validations
   PATCH /api/validations/{validation_id}

📁 Missions
   GET /api/missions
   POST /api/missions
   GET /api/missions/{mission_id}
   PUT /api/missions/{mission_id}
   DELETE /api/missions/{mission_id}
   POST /api/missions/{mission_id}/apply
   GET /api/missions/{mission_id}/applications
   GET /api/missions/my-applications

📁 Documents
   POST /api/documents/upload
   GET /api/documents/{document_id}
   DELETE /api/documents/{document_id}

📁 Configuration
   GET /api/auth/config
   GET /api/auth/references
   GET /api/auth/references/{category}
   POST /api/auth/references
   PUT /api/auth/references/{reference_id}
   DELETE /api/auth/references/{reference_id}

📁 Versions
   GET /api/versions
   POST /api/versions/snapshot
   POST /api/versions/rollback
   GET /api/versions/compare/{version_id_from}/{version_id_to}

📁 Feature Flags
   GET /api/feature-flags
   POST /api/feature-flags
   GET /api/feature-flags/{flag_id}
   PUT /api/feature-flags/{flag_id}
   DELETE /api/feature-flags/{flag_id}
   POST /api/feature-flags/export
   POST /api/feature-flags/import

📁 Email
   GET /api/emails/status
   GET /api/emails/config
   POST /api/emails/test
   POST /api/emails/test-rollback-notification
   GET /api/emails/settings
   PUT /api/emails/settings
   POST /api/emails/settings/test
   DELETE /api/emails/settings
   GET /api/emails/history
   GET /api/emails/history/stats
   DELETE /api/emails/history
   GET /api/emails/templates
   POST /api/emails/templates
   GET /api/emails/templates/{template_id}
   PUT /api/emails/templates/{template_id}
   DELETE /api/emails/templates/{template_id}
   POST /api/emails/templates/{template_id}/preview
   POST /api/emails/templates/init-defaults

📁 Role Visibility
   GET /api/roles/visibility
   PUT /api/roles/{role_id}/visibility

================================================================================
🚀 BACKEND API (Port 8001 - /api)
--------------------------------------------------------------------------------

📁 Admin Stats
   GET /api/admin/stats

📁 Notifications
   GET /api/notifications
   POST /api/notifications/mark-read/{notification_id}
   POST /api/notifications/mark-all-read

📁 Profile (Backend)
   GET /api/profile
   PUT /api/profile

📁 Validation (Backend)
   GET /api/validations/pending
   POST /api/validations/{validation_id}/approve
   POST /api/validations/{validation_id}/reject

================================================================================
TOTAL: 98 endpoints
================================================================================
