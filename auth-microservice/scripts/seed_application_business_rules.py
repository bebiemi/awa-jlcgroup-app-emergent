"""
Seed Application Business Rules
Création des règles métiers pour la gestion des candidatures

Règles créées :
1. Éligibilité candidats/postulants/intérimaires
2. Restrictions pour intérimaires en contrat actif
3. CV obligatoire pour candidature
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def seed_application_rules():
    """Créer les règles métiers pour les candidatures"""
    
    # Connexion MongoDB
    mongo_url = config.get('database.mongo_url', default='mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("🌱 Création des règles métiers pour les candidatures...")
    print("=" * 60)
    
    # Règles à créer
    rules = [
        {
            "rule_id": "application_eligibility_roles",
            "name": "Éligibilité des rôles pour candidature",
            "category": "application",
            "rule_type": "eligibility",
            "description": "Définit les rôles autorisés à postuler aux missions",
            "is_active": True,
            "priority": 100,
            "conditions": {
                "allowed_roles": ["candidat", "postulant", "intérimaire"],
                "required_mission_status": ["published", "accepting_applications"]
            },
            "actions": {
                "on_success": "allow_application",
                "on_failure": "reject_with_message"
            },
            "error_messages": {
                "role_not_allowed": "Votre profil n'est pas autorisé à postuler aux missions",
                "mission_not_open": "Cette mission n'accepte plus de candidatures"
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["missions"]
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "rule_id": "application_interim_contract_restriction",
            "name": "Restriction candidature pour intérimaire en contrat",
            "category": "application",
            "rule_type": "contract_restriction",
            "description": "Intérimaire en contrat actif peut postuler seulement si fin de contrat ≤ 5 jours ET aucune prolongation prévue",
            "is_active": True,
            "priority": 90,
            "conditions": {
                "role": "intérimaire",
                "has_active_contract": True,
                "days_before_contract_end": 5,  # Nombre de jours avant fin de contrat pour autoriser candidature
                "check_extensions": True,  # Vérifier s'il y a des prolongations prévues
                "check_amendments": True   # Vérifier s'il y a des avenants en cours
            },
            "actions": {
                "on_success": "allow_application",
                "on_failure": "reject_with_contract_info"
            },
            "error_messages": {
                "contract_active": "Vous êtes actuellement en mission. Vous pourrez postuler à partir de {days_before} jours avant la fin de votre contrat.",
                "extension_pending": "Une prolongation de votre contrat est en cours. Vous ne pouvez pas postuler à d'autres missions.",
                "amendment_active": "Un avenant à votre contrat est actif. Veuillez contacter votre responsable."
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["missions"],
                "configurable_params": ["days_before_contract_end"]
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "rule_id": "application_cv_requirement",
            "name": "CV obligatoire pour candidature",
            "category": "application",
            "rule_type": "document_requirement",
            "description": "Un CV valide est requis pour soumettre une candidature",
            "is_active": True,
            "priority": 80,
            "conditions": {
                "required_document_type": "cv",
                "allow_upload_during_application": True,  # Permet l'upload pendant la candidature
                "max_file_size_mb": 5,
                "allowed_formats": ["pdf", "doc", "docx"]
            },
            "actions": {
                "on_success": "allow_application",
                "on_failure": "prompt_cv_upload"
            },
            "error_messages": {
                "cv_missing": "Veuillez uploader votre CV pour continuer",
                "cv_invalid_format": "Format de CV non supporté. Formats acceptés : PDF, DOC, DOCX",
                "cv_too_large": "Fichier trop volumineux. Taille maximale : 5MB"
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["missions"],
                "configurable_params": ["max_file_size_mb", "allowed_formats"]
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "rule_id": "application_duplicate_prevention",
            "name": "Prévention des candidatures dupliquées",
            "category": "application",
            "rule_type": "duplicate_check",
            "description": "Un utilisateur ne peut postuler qu'une seule fois à une mission donnée",
            "is_active": True,
            "priority": 95,
            "conditions": {
                "check_user_id": True,
                "check_mission_id": True,
                "allow_reapplication_after_rejection": True,  # Future: permettre re-candidature après rejet
                "reapplication_cooldown_days": 30
            },
            "actions": {
                "on_success": "allow_application",
                "on_failure": "reject_duplicate"
            },
            "error_messages": {
                "already_applied": "Vous avez déjà postulé à cette mission",
                "cooldown_active": "Vous pourrez postuler à nouveau dans {days} jours"
            },
            "metadata": {
                "created_by": "system",
                "can_be_overridden": False,
                "applies_to": ["missions"]
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    # Insérer ou mettre à jour les règles
    for rule in rules:
        existing = await db.business_rules.find_one({"rule_id": rule["rule_id"]})
        
        if existing:
            # Mettre à jour
            result = await db.business_rules.update_one(
                {"rule_id": rule["rule_id"]},
                {"$set": {**rule, "updated_at": datetime.utcnow().isoformat()}}
            )
            if result.modified_count > 0:
                print(f"✅ Règle mise à jour: {rule['rule_id']}")
            else:
                print(f"ℹ️  Règle inchangée: {rule['rule_id']}")
        else:
            # Créer
            await db.business_rules.insert_one(rule)
            print(f"✨ Règle créée: {rule['rule_id']}")
            print(f"   📝 {rule['description']}")
    
    print("\n" + "=" * 60)
    print("✅ Règles métiers créées avec succès!")
    
    # Afficher résumé
    total_rules = await db.business_rules.count_documents({"category": "application"})
    active_rules = await db.business_rules.count_documents({"category": "application", "is_active": True})
    print(f"\n📊 Résumé:")
    print(f"   Total règles application: {total_rules}")
    print(f"   Règles actives: {active_rules}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_application_rules())
