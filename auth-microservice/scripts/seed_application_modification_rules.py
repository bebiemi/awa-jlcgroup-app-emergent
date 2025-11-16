"""
Seed Application Modification & Cancellation Rules
Règles métiers pour la gestion des modifications et annulations de candidatures

Règles créées :
1. Restrictions de modification (statuts autorisés)
2. Restrictions d'annulation (statuts autorisés)
3. Notification automatique lors annulation
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def seed_modification_rules():
    """Créer les règles métiers pour modifications et annulations"""
    
    # Connexion MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("🌱 Création des règles de modification/annulation...")
    print("=" * 60)
    
    rules = [
        {
            "rule_id": "application_modification_restriction",
            "name": "Restrictions de modification de candidature",
            "category": "application",
            "rule_type": "modification",
            "description": "Un candidat peut modifier sa candidature seulement si elle n'a pas encore été envoyée au client",
            "is_active": True,
            "priority": 85,
            "conditions": {
                "allowed_statuses": [
                    "pending",
                    "submitted", 
                    "under_review"
                ],
                "forbidden_statuses": [
                    "sent_to_client",
                    "interview_scheduled",
                    "interview_completed",
                    "selected_by_client",
                    "rejected_by_client",
                    "selected",
                    "rejected",
                    "cancelled"
                ],
                "modifiable_fields": [
                    "additional_info",
                    "cover_letter",
                    "expected_salary",
                    "availability_date",
                    "preferred_work_schedule"
                ],
                "non_modifiable_fields": [
                    "mission_id",
                    "user_id",
                    "status",
                    "created_at"
                ]
            },
            "actions": {
                "on_success": "allow_modification",
                "on_failure": "reject_with_status_info"
            },
            "error_messages": {
                "status_not_allowed": "Vous ne pouvez plus modifier cette candidature (statut: {status})",
                "already_sent": "Cette candidature a déjà été transmise au client et ne peut plus être modifiée",
                "field_not_modifiable": "Le champ '{field}' ne peut pas être modifié"
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["candidats", "postulants", "intérimaires"],
                "audit_log": True
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "rule_id": "application_cancellation_restriction",
            "name": "Restrictions d'annulation de candidature",
            "category": "application",
            "rule_type": "cancellation",
            "description": "Un candidat peut annuler sa candidature avant qu'elle soit envoyée au client ou qu'un entretien soit programmé",
            "is_active": True,
            "priority": 90,
            "conditions": {
                "allowed_statuses": [
                    "pending",
                    "submitted",
                    "under_review"
                ],
                "forbidden_statuses": [
                    "interview_scheduled",
                    "interview_completed",
                    "sent_to_client",
                    "selected_by_client",
                    "selected",
                    "rejected",
                    "cancelled"
                ],
                "require_reason": False,
                "notify_admin": True,
                "notify_commercial": True,
                "grace_period_hours": 0
            },
            "actions": {
                "on_success": "cancel_application",
                "on_failure": "reject_with_reason",
                "post_action": "send_notifications"
            },
            "error_messages": {
                "status_not_allowed": "Vous ne pouvez plus annuler cette candidature (statut: {status})",
                "interview_scheduled": "Un entretien est déjà programmé. Veuillez contacter votre conseiller JLC.",
                "already_sent": "Cette candidature a été transmise au client. Veuillez contacter votre conseiller JLC.",
                "already_cancelled": "Cette candidature a déjà été annulée",
                "already_completed": "Cette candidature a déjà été traitée et ne peut plus être annulée"
            },
            "notifications": {
                "admin_notification": {
                    "enabled": True,
                    "template": "application_cancelled_by_candidate",
                    "priority": "medium"
                },
                "commercial_notification": {
                    "enabled": True,
                    "template": "candidate_cancelled_application",
                    "priority": "high"
                }
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["candidats", "postulants", "intérimaires"],
                "audit_log": True,
                "soft_delete": True
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "rule_id": "application_deletion_restriction",
            "name": "Restrictions de suppression définitive",
            "category": "application",
            "rule_type": "deletion",
            "description": "La suppression définitive n'est autorisée que pour les candidatures jamais envoyées (draft)",
            "is_active": True,
            "priority": 95,
            "conditions": {
                "allowed_statuses": [
                    "pending"
                ],
                "time_limit_hours": 24,
                "require_confirmation": True
            },
            "actions": {
                "on_success": "hard_delete",
                "on_failure": "suggest_cancel"
            },
            "error_messages": {
                "status_not_allowed": "Suppression non autorisée. Vous pouvez annuler cette candidature.",
                "time_limit_exceeded": "Délai de suppression dépassé. Veuillez annuler la candidature."
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["candidats", "postulants", "intérimaires"],
                "audit_log": True
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    for rule in rules:
        existing = await db.business_rules.find_one({"rule_id": rule["rule_id"]})
        
        if existing:
            result = await db.business_rules.update_one(
                {"rule_id": rule["rule_id"]},
                {"$set": {**rule, "updated_at": datetime.utcnow().isoformat()}}
            )
            if result.modified_count > 0:
                print(f"✅ Règle mise à jour: {rule['rule_id']}")
            else:
                print(f"ℹ️  Règle inchangée: {rule['rule_id']}")
        else:
            await db.business_rules.insert_one(rule)
            print(f"✨ Règle créée: {rule['rule_id']}")
            print(f"   📝 {rule['description']}")
    
    print("\n" + "=" * 60)
    print("✅ Règles métiers de modification/annulation créées!")
    
    # Résumé
    total = await db.business_rules.count_documents({"category": "application"})
    active = await db.business_rules.count_documents({"category": "application", "is_active": True})
    print(f"\n📊 Résumé:")
    print(f"   Total règles application: {total}")
    print(f"   Règles actives: {active}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_modification_rules())
