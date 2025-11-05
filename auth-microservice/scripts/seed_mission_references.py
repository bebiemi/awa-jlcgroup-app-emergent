"""
Script de migration pour créer les référentiels du workflow missions
À exécuter UNE SEULE FOIS après le déploiement
"""
import asyncio
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def seed_mission_references():
    """Créer les référentiels pour le workflow missions"""
    
    # Connexion MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.awana_db
    
    print("🚀 Démarrage de la migration des référentiels missions...")
    
    # ==================== STATUTS DE MISSION ====================
    mission_statuses = [
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "draft",
            "label_fr": "Brouillon",
            "label_en": "Draft",
            "description": "Mission en cours de création, non publiée",
            "order": 1,
            "metadata": {
                "color": "#94A3B8",
                "icon": "document",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "published",
            "label_fr": "Publiée",
            "label_en": "Published",
            "description": "Mission visible et ouverte aux candidatures",
            "order": 2,
            "metadata": {
                "color": "#10B981",
                "icon": "globe",
                "is_visible_to_candidates": True,
                "can_receive_applications": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "in_progress",
            "label_fr": "En cours",
            "label_en": "In Progress",
            "description": "Mission démarrée avec un candidat",
            "order": 3,
            "metadata": {
                "color": "#3B82F6",
                "icon": "play",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "completed",
            "label_fr": "Terminée",
            "label_en": "Completed",
            "description": "Mission terminée avec succès",
            "order": 4,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "check-circle",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "cancelled",
            "label_fr": "Annulée",
            "label_en": "Cancelled",
            "description": "Mission annulée",
            "order": 5,
            "metadata": {
                "color": "#EF4444",
                "icon": "x-circle",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Supprimer les anciennes valeurs et insérer les nouvelles
    await db.system_references.delete_many({"category": "mission_statuses"})
    await db.system_references.insert_many(mission_statuses)
    print(f"✅ {len(mission_statuses)} statuts de mission créés")
    
    # ==================== STATUTS DE CANDIDATURE ====================
    application_statuses = [
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "pending",
            "label_fr": "En attente",
            "label_en": "Pending",
            "description": "Candidature soumise, en attente de traitement",
            "order": 1,
            "metadata": {
                "color": "#F59E0B",
                "icon": "clock",
                "next_possible_statuses": ["interview_scheduled", "rejected"],
                "requires_action_from": "company"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "interview_scheduled",
            "label_fr": "Entretien programmé",
            "label_en": "Interview Scheduled",
            "description": "Entretien planifié avec le candidat",
            "order": 2,
            "metadata": {
                "color": "#3B82F6",
                "icon": "calendar",
                "next_possible_statuses": ["interview_completed"],
                "requires_action_from": "company"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "interview_completed",
            "label_fr": "Entretien effectué",
            "label_en": "Interview Completed",
            "description": "Entretien réalisé, décision en attente",
            "order": 3,
            "metadata": {
                "color": "#6366F1",
                "icon": "check",
                "next_possible_statuses": ["selected", "rejected"],
                "requires_action_from": "company"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "selected",
            "label_fr": "Sélectionné",
            "label_en": "Selected",
            "description": "Candidat sélectionné par l'entreprise",
            "order": 4,
            "metadata": {
                "color": "#10B981",
                "icon": "user-check",
                "next_possible_statuses": ["medical_pending"],
                "requires_action_from": "agency"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "medical_pending",
            "label_fr": "Visite médicale en attente",
            "label_en": "Medical Pending",
            "description": "En attente de la visite médicale",
            "order": 5,
            "metadata": {
                "color": "#F59E0B",
                "icon": "document-medical",
                "next_possible_statuses": ["medical_approved", "medical_rejected"],
                "requires_action_from": "agency",
                "requires_document_upload": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "medical_approved",
            "label_fr": "Visite médicale validée",
            "label_en": "Medical Approved",
            "description": "Candidat déclaré apte médicalement",
            "order": 6,
            "metadata": {
                "color": "#10B981",
                "icon": "shield-check",
                "next_possible_statuses": ["contract_pending"],
                "requires_action_from": "agency"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "medical_rejected",
            "label_fr": "Visite médicale refusée",
            "label_en": "Medical Rejected",
            "description": "Candidat déclaré inapte médicalement",
            "order": 7,
            "metadata": {
                "color": "#EF4444",
                "icon": "shield-x",
                "next_possible_statuses": [],
                "is_final_status": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "contract_pending",
            "label_fr": "Contrat en attente",
            "label_en": "Contract Pending",
            "description": "En attente de signature du contrat",
            "order": 8,
            "metadata": {
                "color": "#F59E0B",
                "icon": "document-text",
                "next_possible_statuses": ["contract_signed"],
                "requires_action_from": "agency",
                "requires_document_upload": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "contract_signed",
            "label_fr": "Contrat signé",
            "label_en": "Contract Signed",
            "description": "Contrat signé, processus terminé",
            "order": 9,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "document-check",
                "next_possible_statuses": [],
                "is_final_status": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "rejected",
            "label_fr": "Refusée",
            "label_en": "Rejected",
            "description": "Candidature rejetée",
            "order": 10,
            "metadata": {
                "color": "#EF4444",
                "icon": "x-circle",
                "next_possible_statuses": [],
                "is_final_status": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "application_statuses"})
    await db.system_references.insert_many(application_statuses)
    print(f"✅ {len(application_statuses)} statuts de candidature créés")
    
    # ==================== TYPES DE CONTRATS ====================
    contract_types = [
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "cdi",
            "label_fr": "CDI",
            "label_en": "Permanent Contract",
            "description": "Contrat à Durée Indéterminée",
            "order": 1,
            "metadata": {
                "color": "#10B981",
                "icon": "briefcase"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "cdd",
            "label_fr": "CDD",
            "label_en": "Fixed-term Contract",
            "description": "Contrat à Durée Déterminée",
            "order": 2,
            "metadata": {
                "color": "#3B82F6",
                "icon": "calendar"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "interim",
            "label_fr": "Intérim",
            "label_en": "Temporary Work",
            "description": "Mission d'intérim",
            "order": 3,
            "metadata": {
                "color": "#F59E0B",
                "icon": "clock"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "stage",
            "label_fr": "Stage",
            "label_en": "Internship",
            "description": "Convention de stage",
            "order": 4,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "academic-cap"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "contract_types"})
    await db.system_references.insert_many(contract_types)
    print(f"✅ {len(contract_types)} types de contrats créés")
    
    # ==================== APTITUDES MÉDICALES ====================
    medical_aptitudes = [
        {
            "id": str(uuid.uuid4()),
            "category": "medical_aptitudes",
            "code": "apte",
            "label_fr": "Apte",
            "label_en": "Fit",
            "description": "Candidat apte au travail",
            "order": 1,
            "metadata": {
                "color": "#10B981",
                "icon": "check-circle",
                "allows_contract": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "medical_aptitudes",
            "code": "apte_avec_reserves",
            "label_fr": "Apte avec réserves",
            "label_en": "Fit with Restrictions",
            "description": "Apte avec restrictions spécifiques",
            "order": 2,
            "metadata": {
                "color": "#F59E0B",
                "icon": "exclamation-triangle",
                "allows_contract": True,
                "requires_note": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "medical_aptitudes",
            "code": "inapte",
            "label_fr": "Inapte",
            "label_en": "Unfit",
            "description": "Candidat inapte au travail",
            "order": 3,
            "metadata": {
                "color": "#EF4444",
                "icon": "x-circle",
                "allows_contract": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "medical_aptitudes"})
    await db.system_references.insert_many(medical_aptitudes)
    print(f"✅ {len(medical_aptitudes)} aptitudes médicales créées")
    
    print("\n🎉 Migration terminée avec succès !")
    print(f"📊 Total: {len(mission_statuses) + len(application_statuses) + len(contract_types) + len(medical_aptitudes)} référentiels créés")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_mission_references())
