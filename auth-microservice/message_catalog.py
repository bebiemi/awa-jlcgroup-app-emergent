"""Centralized reusable API messages to avoid hardcoded literals in routes.

This lightweight catalog keeps user-facing strings in one place so they can be
internationalized or sourced from configuration later without editing each
route. The keys are grouped by domain (MFA, invitation, validation, location)
and intentionally kept small and descriptive.
"""

from typing import Final


MFA_MESSAGES: Final = {
    "rate_limit": "Trop de tentatives. Veuillez réessayer dans 15 minutes.",
    "totp_pending_missing": "Aucune configuration TOTP en attente",
    "totp_expired": "Configuration expirée. Veuillez recommencer.",
    "invalid_code": "Code invalide",
    "totp_success": "TOTP activé avec succès. Conservez vos codes de secours en lieu sûr.",
    "email_success": "Email OTP activé. Un code a été envoyé à {email}",
    "sms_sent": "Un code de vérification a été envoyé au {phone_number}",
    "sms_invalid": "Code invalide ou expiré",
    "phone_missing": "Numéro de téléphone non trouvé",
    "sms_success": "SMS OTP activé avec succès",
}


INVITATION_MESSAGES: Final = {
    "company_not_found": "Entreprise non trouvée",
    "user_exists": "Un utilisateur avec cet email existe déjà",
    "invitation_pending": "Une invitation est déjà en attente pour cet email",
}


VALIDATION_MESSAGES: Final = {
    "not_found": "Validation not found",
    "already_processed": "Validation already processed",
    "validator_missing": "Validator not found",
    "validator_role_missing": "User does not have validator role ({roles})",
}


LOCATION_MESSAGES: Final = {
    "not_found": "Location not found",
    "parent_not_found": "Parent location not found",
    "duplicate": "Location with name '{name}' already exists at this level",
    "children_block_delete": "Cannot delete location with {children} children. Delete children first.",
}
