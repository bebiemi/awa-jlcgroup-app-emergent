"""
Initialize Business Rules
Creates essential business rules for the application
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from uuid import uuid4

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


# Define business rules according to application needs
BUSINESS_RULES = [
    # ==================== VALIDATION RULES ====================
    {
        "name": "Validation Automatique des Profils Complets",
        "description": "Auto-valider les profils lorsque tous les documents requis sont présents",
        "rule_type": "validation",
        "conditions": {
            "profile_completion": {"min": 100},
            "required_documents": ["cv", "id_card"],
            "email_verified": True
        },
        "actions": {
            "set_status": "validated",
            "send_notification": True,
            "notification_type": "profile_validated"
        },
        "priority": 10,
        "is_active": True
    },
    {
        "name": "Vérification Documents Expirés",
        "description": "Alerter lorsqu'un document est proche de l'expiration",
        "rule_type": "validation",
        "conditions": {
            "document_types": ["id_card", "passport", "work_permit", "medical_certificate"],
            "days_before_expiration": 30
        },
        "actions": {
            "send_notification": True,
            "notification_type": "document_expiring",
            "create_task": True
        },
        "priority": 5,
        "is_active": True
    },
    {
        "name": "Validation Visite Médicale Obligatoire",
        "description": "Bloquer l'attribution de missions sans visite médicale valide",
        "rule_type": "validation",
        "conditions": {
            "mission_assignment": True,
            "medical_certificate_required": True,
            "medical_status": ["pending", None]
        },
        "actions": {
            "block_action": True,
            "show_message": "Une visite médicale valide est requise avant attribution",
            "redirect_to": "/profile?tab=medical"
        },
        "priority": 100,
        "is_active": True
    },
    
    # ==================== NOTIFICATION RULES ====================
    {
        "name": "Notification Nouvelle Candidature",
        "description": "Notifier le commercial et l'admin lors d'une nouvelle candidature",
        "rule_type": "notification",
        "conditions": {
            "event": "application.created",
            "application_status": "submitted"
        },
        "actions": {
            "notify_roles": ["admin", "commercial"],
            "notification_type": "new_application",
            "email": True,
            "in_app": True
        },
        "priority": 20,
        "is_active": True
    },
    {
        "name": "Notification Changement Statut Mission",
        "description": "Notifier les parties prenantes lors du changement de statut d'une mission",
        "rule_type": "notification",
        "conditions": {
            "event": "mission.status_changed",
            "statuses": ["published", "in_progress", "completed", "cancelled"]
        },
        "actions": {
            "notify_applicants": True,
            "notify_company": True,
            "notify_assigned_interim": True,
            "notification_type": "mission_status_changed"
        },
        "priority": 15,
        "is_active": True
    },
    {
        "name": "Rappel Profil Incomplet",
        "description": "Rappeler aux candidats de compléter leur profil après 7 jours",
        "rule_type": "notification",
        "conditions": {
            "user_role": "candidat",
            "profile_completion": {"max": 70},
            "days_since_registration": 7
        },
        "actions": {
            "send_notification": True,
            "notification_type": "profile_incomplete_reminder",
            "email": True
        },
        "priority": 5,
        "is_active": False  # Désactivé par défaut, à activer manuellement
    },
    
    # ==================== WORKFLOW RULES ====================
    {
        "name": "Workflow Candidature Standard",
        "description": "Gérer le cycle de vie automatique d'une candidature",
        "rule_type": "workflow",
        "conditions": {
            "application_created": True
        },
        "actions": {
            "workflow_steps": [
                {"status": "submitted", "auto_advance_days": 2, "next": "under_review"},
                {"status": "under_review", "requires_action": True},
                {"status": "shortlisted", "notify_candidate": True},
                {"status": "interview", "create_calendar_event": True}
            ]
        },
        "priority": 30,
        "is_active": True
    },
    {
        "name": "Workflow Onboarding Intérimaire",
        "description": "Automatiser les étapes d'onboarding d'un nouvel intérimaire",
        "rule_type": "workflow",
        "conditions": {
            "user_role": "candidat",
            "application_status": "accepted"
        },
        "actions": {
            "upgrade_role": "interim",
            "create_tasks": [
                "medical_visit_booking",
                "contract_signing",
                "bank_details_collection"
            ],
            "send_welcome_email": True,
            "notification_type": "onboarding_started"
        },
        "priority": 50,
        "is_active": True
    },
    {
        "name": "Archivage Automatique Missions Anciennes",
        "description": "Archiver les missions terminées depuis plus de 6 mois",
        "rule_type": "workflow",
        "conditions": {
            "mission_status": "completed",
            "days_since_completion": 180
        },
        "actions": {
            "set_status": "archived",
            "move_to_archive": True,
            "notify_admin": False
        },
        "priority": 1,
        "is_active": False  # À activer après validation
    },
    
    # ==================== AUTOMATION RULES ====================
    {
        "name": "Attribution Automatique Missions Urgentes",
        "description": "Proposer automatiquement les missions urgentes aux intérimaires qualifiés",
        "rule_type": "automation",
        "conditions": {
            "mission_priority": "urgent",
            "mission_status": "published",
            "auto_match_enabled": True
        },
        "actions": {
            "match_skills": True,
            "match_location": True,
            "match_availability": True,
            "send_proposals": True,
            "max_proposals": 5
        },
        "priority": 80,
        "is_active": False  # Nécessite IA de matching
    },
    {
        "name": "Calcul Automatique Salaire",
        "description": "Calculer automatiquement le salaire en fonction des heures et taux",
        "rule_type": "automation",
        "conditions": {
            "timesheet_validated": True
        },
        "actions": {
            "calculate_salary": True,
            "apply_bonuses": True,
            "deduct_taxes": True,
            "generate_payslip": True
        },
        "priority": 100,
        "is_active": False  # À implémenter
    },
    {
        "name": "Génération Automatique Rapports Mensuels",
        "description": "Générer et envoyer les rapports d'activité mensuels",
        "rule_type": "automation",
        "conditions": {
            "schedule": "monthly",
            "day_of_month": 1,
            "hour": 8
        },
        "actions": {
            "generate_reports": ["missions", "applications", "users", "revenue"],
            "send_to_roles": ["admin", "commercial"],
            "format": "pdf"
        },
        "priority": 10,
        "is_active": False  # À activer après tests
    },
]


async def init_business_rules():
    """Initialize business rules"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    collection = db.business_rules
    
    now = datetime.now(timezone.utc)
    stats = {"created": 0, "updated": 0, "unchanged": 0}
    
    print("🔧 Initializing Business Rules...\n")
    
    for rule_data in BUSINESS_RULES:
        name = rule_data["name"]
        
        # Check if rule already exists
        existing = await collection.find_one({"name": name})
        
        rule_doc = {
            "id": existing.get("id", str(uuid4())) if existing else str(uuid4()),
            "name": rule_data["name"],
            "description": rule_data["description"],
            "rule_type": rule_data["rule_type"],
            "conditions": rule_data["conditions"],
            "actions": rule_data["actions"],
            "priority": rule_data["priority"],
            "is_active": existing.get("is_active", rule_data["is_active"]) if existing else rule_data["is_active"],
            "created_at": existing.get("created_at", now) if existing else now,
            "updated_at": now,
        }
        
        if existing:
            # Check if update is needed
            needs_update = (
                existing.get("description") != rule_doc["description"] or
                existing.get("conditions") != rule_doc["conditions"] or
                existing.get("actions") != rule_doc["actions"] or
                existing.get("priority") != rule_doc["priority"]
            )
            
            if needs_update:
                await collection.update_one(
                    {"id": rule_doc["id"]},
                    {"$set": rule_doc}
                )
                status_icon = "🔄"
                stats["updated"] += 1
            else:
                status_icon = "✓"
                stats["unchanged"] += 1
        else:
            await collection.insert_one(rule_doc)
            status_icon = "✅"
            stats["created"] += 1
        
        active_icon = "🟢" if rule_doc["is_active"] else "⚪"
        print(f"{status_icon} [{rule_data['rule_type']:12}] {active_icon} {name}")
    
    print(f"\n✅ Business rules initialization complete!")
    print(f"   - Created: {stats['created']} rules")
    print(f"   - Updated: {stats['updated']} rules")
    print(f"   - Unchanged: {stats['unchanged']} rules")
    print(f"   - Total: {len(BUSINESS_RULES)} rules")
    
    # Stats by type
    print(f"\n📊 By Type:")
    types_count = {}
    for rule in BUSINESS_RULES:
        rt = rule["rule_type"]
        types_count[rt] = types_count.get(rt, 0) + 1
    
    for rt, count in sorted(types_count.items()):
        print(f"   - {rt.capitalize()}: {count}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(init_business_rules())
