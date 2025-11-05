"""
Script de migration pour créer les référentiels supplémentaires
Rôles, Compétences, Pays, Types de documents
"""
import asyncio
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def seed_additional_references():
    """Créer les référentiels supplémentaires"""
    
    # Connexion MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DATABASE_NAME', 'auth_db')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🚀 Démarrage de la migration des référentiels supplémentaires...")
    
    # ==================== RÔLES ====================
    roles = [
        {
            "id": str(uuid.uuid4()),
            "category": "roles",
            "code": "admin",
            "label_fr": "Administrateur",
            "label_en": "Administrator",
            "description": "Administrateur système avec tous les droits",
            "order": 1,
            "metadata": {
                "color": "#DC2626",
                "icon": "shield-check",
                "permissions": ["all"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "roles",
            "code": "super_admin",
            "label_fr": "Super Administrateur",
            "label_en": "Super Administrator",
            "description": "Super administrateur avec droits étendus",
            "order": 2,
            "metadata": {
                "color": "#991B1B",
                "icon": "shield-exclamation",
                "permissions": ["all"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "roles",
            "code": "company",
            "label_fr": "Entreprise",
            "label_en": "Company",
            "description": "Entreprise cliente cherchant des ressources",
            "order": 3,
            "metadata": {
                "color": "#2563EB",
                "icon": "building-office",
                "permissions": ["create_mission", "view_applications", "select_candidates"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "roles",
            "code": "agency",
            "label_fr": "Agence",
            "label_en": "Agency",
            "description": "Agence d'intérim gérant les candidats",
            "order": 4,
            "metadata": {
                "color": "#7C3AED",
                "icon": "building",
                "permissions": ["manage_candidates", "manage_applications", "upload_documents"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "roles",
            "code": "commercial",
            "label_fr": "Commercial",
            "label_en": "Sales",
            "description": "Commercial gérant les missions",
            "order": 5,
            "metadata": {
                "color": "#059669",
                "icon": "briefcase",
                "permissions": ["create_mission", "manage_missions", "view_applications"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "roles",
            "code": "interim",
            "label_fr": "Intérimaire",
            "label_en": "Temporary Worker",
            "description": "Candidat cherchant des missions",
            "order": 6,
            "metadata": {
                "color": "#0891B2",
                "icon": "user",
                "permissions": ["view_missions", "apply_mission", "view_my_applications"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "roles"})
    await db.system_references.insert_many(roles)
    print(f"✅ {len(roles)} rôles créés")
    
    # ==================== COMPÉTENCES ====================
    skills = [
        {
            "id": str(uuid.uuid4()),
            "category": "skills",
            "code": "python",
            "label_fr": "Python",
            "label_en": "Python",
            "description": "Langage de programmation Python",
            "order": 1,
            "metadata": {
                "color": "#3776AB",
                "icon": "code",
                "category_type": "tech"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "skills",
            "code": "javascript",
            "label_fr": "JavaScript",
            "label_en": "JavaScript",
            "description": "Langage de programmation JavaScript",
            "order": 2,
            "metadata": {
                "color": "#F7DF1E",
                "icon": "code",
                "category_type": "tech"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "skills",
            "code": "react",
            "label_fr": "React",
            "label_en": "React",
            "description": "Bibliothèque JavaScript React",
            "order": 3,
            "metadata": {
                "color": "#61DAFB",
                "icon": "code",
                "category_type": "tech"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "skills",
            "code": "communication",
            "label_fr": "Communication",
            "label_en": "Communication",
            "description": "Compétences en communication",
            "order": 10,
            "metadata": {
                "color": "#10B981",
                "icon": "chat-bubble",
                "category_type": "soft"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "skills",
            "code": "leadership",
            "label_fr": "Leadership",
            "label_en": "Leadership",
            "description": "Compétences en leadership",
            "order": 11,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "star",
                "category_type": "soft"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "skills"})
    await db.system_references.insert_many(skills)
    print(f"✅ {len(skills)} compétences créées")
    
    # ==================== PAYS ====================
    countries = [
        {
            "id": str(uuid.uuid4()),
            "category": "countries",
            "code": "GA",
            "label_fr": "Gabon",
            "label_en": "Gabon",
            "description": "République Gabonaise",
            "order": 1,
            "metadata": {
                "dial_code": "+241",
                "flag": "🇬🇦",
                "currency": "XAF"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "countries",
            "code": "FR",
            "label_fr": "France",
            "label_en": "France",
            "description": "République Française",
            "order": 2,
            "metadata": {
                "dial_code": "+33",
                "flag": "🇫🇷",
                "currency": "EUR"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "countries",
            "code": "CI",
            "label_fr": "Côte d'Ivoire",
            "label_en": "Ivory Coast",
            "description": "République de Côte d'Ivoire",
            "order": 3,
            "metadata": {
                "dial_code": "+225",
                "flag": "🇨🇮",
                "currency": "XOF"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "countries",
            "code": "SN",
            "label_fr": "Sénégal",
            "label_en": "Senegal",
            "description": "République du Sénégal",
            "order": 4,
            "metadata": {
                "dial_code": "+221",
                "flag": "🇸🇳",
                "currency": "XOF"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "countries",
            "code": "CM",
            "label_fr": "Cameroun",
            "label_en": "Cameroon",
            "description": "République du Cameroun",
            "order": 5,
            "metadata": {
                "dial_code": "+237",
                "flag": "🇨🇲",
                "currency": "XAF"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "countries"})
    await db.system_references.insert_many(countries)
    print(f"✅ {len(countries)} pays créés")
    
    # ==================== TYPES DE DOCUMENTS ====================
    document_types = [
        {
            "id": str(uuid.uuid4()),
            "category": "document_types",
            "code": "cv",
            "label_fr": "CV",
            "label_en": "Resume",
            "description": "Curriculum Vitae",
            "order": 1,
            "metadata": {
                "color": "#3B82F6",
                "icon": "document-text",
                "required_for": ["application"],
                "max_size_mb": 5,
                "allowed_formats": ["pdf", "doc", "docx"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "document_types",
            "code": "cover_letter",
            "label_fr": "Lettre de motivation",
            "label_en": "Cover Letter",
            "description": "Lettre de motivation",
            "order": 2,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "document",
                "required_for": ["application"],
                "max_size_mb": 5,
                "allowed_formats": ["pdf", "doc", "docx"]
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "document_types",
            "code": "medical_certificate",
            "label_fr": "Certificat médical",
            "label_en": "Medical Certificate",
            "description": "Certificat de visite médicale",
            "order": 3,
            "metadata": {
                "color": "#10B981",
                "icon": "document-check",
                "required_for": ["medical_check"],
                "max_size_mb": 10,
                "allowed_formats": ["pdf", "jpg", "png"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "document_types",
            "code": "contract",
            "label_fr": "Contrat",
            "label_en": "Contract",
            "description": "Contrat de travail signé",
            "order": 4,
            "metadata": {
                "color": "#F59E0B",
                "icon": "document-duplicate",
                "required_for": ["contract_signing"],
                "max_size_mb": 10,
                "allowed_formats": ["pdf"]
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "document_types",
            "code": "id_card",
            "label_fr": "Carte d'identité",
            "label_en": "ID Card",
            "description": "Carte d'identité nationale",
            "order": 5,
            "metadata": {
                "color": "#EF4444",
                "icon": "identification",
                "required_for": ["onboarding"],
                "max_size_mb": 5,
                "allowed_formats": ["pdf", "jpg", "png"]
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "document_types"})
    await db.system_references.insert_many(document_types)
    print(f"✅ {len(document_types)} types de documents créés")
    
    print("\n🎉 Migration terminée avec succès !")
    print(f"📊 Total: {len(roles) + len(skills) + len(countries) + len(document_types)} référentiels créés")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_additional_references())
