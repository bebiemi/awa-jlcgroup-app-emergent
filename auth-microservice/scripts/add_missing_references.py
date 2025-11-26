"""
Script pour ajouter les références importantes manquantes
"""
import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

from awana_auth.utils.config_helpers import ConfigHelper as cfg

# Charger les variables d'environnement
load_dotenv()

# Connexion MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/auth_db')

# Références à ajouter (celles qui manquent par rapport à base.yaml)
USER_STATUS_DELETED = cfg.get_deleted_status() or "deleted"

VALIDATION_TYPES = {
    "interim": cfg.get_validation_type("interim") or "interim",
    "company": cfg.get_validation_type("company") or "company",
    "collaborator": cfg.get_validation_type("collaborator") or "collaborator",
}

VALIDATION_STATUSES = {
    "pending": cfg.get_validation_status("pending") or "pending",
    "approved": cfg.get_validation_status("approved") or "approved",
    "rejected": cfg.get_validation_status("rejected") or "rejected",
}

VALIDATOR_ROLE = cfg.get_validator_role() or "validator"

MISSION_STATUSES = {
    "closed": cfg.get_mission_status("closed") or "closed",
    "archived": cfg.get_mission_status("archived") or "archived",
}

APPLICATION_STATUSES = {
    "submitted": cfg.get_application_status("submitted") or "submitted",
    "review": cfg.get_application_status("review") or "review",
    "interviewed": cfg.get_application_status("interviewed") or "interviewed",
    "withdrawn": cfg.get_application_status("withdrawn") or "withdrawn",
}

MISSING_REFERENCES = {
    # User Statuses - ajouter deleted qui manque
    "user_statuses": [
        {
            "code": USER_STATUS_DELETED,
            "label_fr": "Supprimé",
            "label_en": "Deleted",
            "description": "Compte utilisateur supprimé",
            "order": 5,
            "metadata": {"color": "#6B7280", "icon": "trash"}
        },
    ],
    
    # Validation Types - ajouter types manquants
    "validation_types": [
        {
            "code": VALIDATION_TYPES["interim"],
            "label_fr": "Validation Intérimaire",
            "label_en": "Interim Validation",
            "description": "Validation du profil intérimaire",
            "order": 1,
            "metadata": {"color": "#3B82F6", "icon": "user"}
        },
        {
            "code": VALIDATION_TYPES["company"],
            "label_fr": "Validation Entreprise",
            "label_en": "Company Validation",
            "description": "Validation du profil entreprise",
            "order": 2,
            "metadata": {"color": "#8B5CF6", "icon": "building"}
        },
        {
            "code": VALIDATION_TYPES["collaborator"],
            "label_fr": "Validation Collaborateur",
            "label_en": "Collaborator Validation",
            "description": "Validation du profil collaborateur",
            "order": 3,
            "metadata": {"color": "#10B981", "icon": "users"}
        },
    ],
    
    # Validation Statuses
    "validation_statuses": [
        {
            "code": VALIDATION_STATUSES["pending"],
            "label_fr": "En attente",
            "label_en": "Pending",
            "description": "Validation en attente de traitement",
            "order": 1,
            "metadata": {"color": "#F59E0B", "icon": "clock"}
        },
        {
            "code": VALIDATION_STATUSES["approved"],
            "label_fr": "Approuvé",
            "label_en": "Approved",
            "description": "Validation approuvée",
            "order": 2,
            "metadata": {"color": "#10B981", "icon": "check-circle"}
        },
        {
            "code": VALIDATION_STATUSES["rejected"],
            "label_fr": "Rejeté",
            "label_en": "Rejected",
            "description": "Validation rejetée",
            "order": 3,
            "metadata": {"color": "#EF4444", "icon": "x-circle"}
        },
    ],
    
    # Ajouter validator role
    "roles": [
        {
            "code": VALIDATOR_ROLE,
            "label_fr": "Validateur",
            "label_en": "Validator",
            "description": "Rôle de validateur des profils",
            "order": 7,
            "metadata": {"color": "#14B8A6", "icon": "check-badge"}
        },
    ],
    
    # Document types supplémentaires
    "document_types": [
        {
            "code": "diploma",
            "label_fr": "Diplôme",
            "label_en": "Diploma",
            "description": "Diplôme ou certification",
            "order": 6,
            "metadata": {"color": "#8B5CF6", "icon": "academic-cap"}
        },
        {
            "code": "identity_document",
            "label_fr": "Pièce d'identité",
            "label_en": "Identity Document",
            "description": "Document d'identité officiel",
            "order": 7,
            "metadata": {"color": "#F59E0B", "icon": "identification"}
        },
    ],
    
    # Mission statuses supplémentaires
    "mission_statuses": [
        {
            "code": MISSION_STATUSES["closed"],
            "label_fr": "Clôturée",
            "label_en": "Closed",
            "description": "Mission clôturée (recrutement terminé)",
            "order": 6,
            "metadata": {"color": "#6B7280", "icon": "lock-closed"}
        },
        {
            "code": MISSION_STATUSES["archived"],
            "label_fr": "Archivée",
            "label_en": "Archived",
            "description": "Mission archivée",
            "order": 7,
            "metadata": {"color": "#9CA3AF", "icon": "archive-box"}
        },
    ],
    
    # Application statuses manquants
    "application_statuses": [
        {
            "code": APPLICATION_STATUSES["submitted"],
            "label_fr": "Soumise",
            "label_en": "Submitted",
            "description": "Candidature soumise",
            "order": 1,
            "metadata": {"color": "#3B82F6", "icon": "paper-airplane"}
        },
        {
            "code": APPLICATION_STATUSES["review"],
            "label_fr": "En révision",
            "label_en": "Under Review",
            "description": "Candidature en cours de révision",
            "order": 2,
            "metadata": {"color": "#F59E0B", "icon": "eye"}
        },
        {
            "code": APPLICATION_STATUSES["interviewed"],
            "label_fr": "Entretien passé",
            "label_en": "Interviewed",
            "description": "Candidat a passé l'entretien",
            "order": 4,
            "metadata": {"color": "#8B5CF6", "icon": "chat-bubble-left-right"}
        },
        {
            "code": APPLICATION_STATUSES["withdrawn"],
            "label_fr": "Retirée",
            "label_en": "Withdrawn",
            "description": "Candidature retirée par le candidat",
            "order": 11,
            "metadata": {"color": "#6B7280", "icon": "arrow-uturn-left"}
        },
    ],
    
    # Skill categories
    "skill_categories": [
        {
            "code": "technical",
            "label_fr": "Compétences Techniques",
            "label_en": "Technical Skills",
            "description": "Compétences techniques et professionnelles",
            "order": 1,
            "metadata": {"color": "#3B82F6", "icon": "code-bracket"}
        },
        {
            "code": "soft_skills",
            "label_fr": "Compétences Comportementales",
            "label_en": "Soft Skills",
            "description": "Compétences comportementales et relationnelles",
            "order": 2,
            "metadata": {"color": "#10B981", "icon": "heart"}
        },
        {
            "code": "languages",
            "label_fr": "Langues",
            "label_en": "Languages",
            "description": "Compétences linguistiques",
            "order": 3,
            "metadata": {"color": "#8B5CF6", "icon": "language"}
        },
        {
            "code": "certifications",
            "label_fr": "Certifications",
            "label_en": "Certifications",
            "description": "Certifications professionnelles",
            "order": 4,
            "metadata": {"color": "#F59E0B", "icon": "academic-cap"}
        },
    ],
    
    # Experience levels
    "experience_levels": [
        {
            "code": "entry",
            "label_fr": "Débutant",
            "label_en": "Entry Level",
            "description": "0-2 ans d'expérience",
            "order": 1,
            "metadata": {"color": "#10B981", "icon": "arrow-trending-up", "years": "0-2"}
        },
        {
            "code": "junior",
            "label_fr": "Junior",
            "label_en": "Junior",
            "description": "2-5 ans d'expérience",
            "order": 2,
            "metadata": {"color": "#3B82F6", "icon": "arrow-trending-up", "years": "2-5"}
        },
        {
            "code": "intermediate",
            "label_fr": "Intermédiaire",
            "label_en": "Intermediate",
            "description": "5-8 ans d'expérience",
            "order": 3,
            "metadata": {"color": "#8B5CF6", "icon": "arrow-trending-up", "years": "5-8"}
        },
        {
            "code": "senior",
            "label_fr": "Senior",
            "label_en": "Senior",
            "description": "8-15 ans d'expérience",
            "order": 4,
            "metadata": {"color": "#F59E0B", "icon": "star", "years": "8-15"}
        },
        {
            "code": "expert",
            "label_fr": "Expert",
            "label_en": "Expert",
            "description": "15+ ans d'expérience",
            "order": 5,
            "metadata": {"color": "#EF4444", "icon": "fire", "years": "15+"}
        },
    ],
    
    # Education levels
    "education_levels": [
        {
            "code": "bac",
            "label_fr": "Baccalauréat",
            "label_en": "High School Diploma",
            "description": "Niveau Baccalauréat",
            "order": 1,
            "metadata": {"color": "#10B981", "icon": "academic-cap"}
        },
        {
            "code": "bac_plus_2",
            "label_fr": "Bac+2 (BTS/DUT)",
            "label_en": "2-Year Degree",
            "description": "Diplôme Bac+2",
            "order": 2,
            "metadata": {"color": "#3B82F6", "icon": "academic-cap"}
        },
        {
            "code": "licence",
            "label_fr": "Licence (Bac+3)",
            "label_en": "Bachelor's Degree",
            "description": "Niveau Licence",
            "order": 3,
            "metadata": {"color": "#8B5CF6", "icon": "academic-cap"}
        },
        {
            "code": "master",
            "label_fr": "Master (Bac+5)",
            "label_en": "Master's Degree",
            "description": "Niveau Master",
            "order": 4,
            "metadata": {"color": "#F59E0B", "icon": "academic-cap"}
        },
        {
            "code": "doctorat",
            "label_fr": "Doctorat (Bac+8)",
            "label_en": "PhD",
            "description": "Niveau Doctorat",
            "order": 5,
            "metadata": {"color": "#EF4444", "icon": "academic-cap"}
        },
    ],
    
    # Work schedule types
    "work_schedules": [
        {
            "code": "full_time",
            "label_fr": "Temps plein",
            "label_en": "Full Time",
            "description": "Travail à temps plein",
            "order": 1,
            "metadata": {"color": "#3B82F6", "icon": "clock", "hours": "35-40"}
        },
        {
            "code": "part_time",
            "label_fr": "Temps partiel",
            "label_en": "Part Time",
            "description": "Travail à temps partiel",
            "order": 2,
            "metadata": {"color": "#10B981", "icon": "clock", "hours": "<35"}
        },
        {
            "code": "flexible",
            "label_fr": "Horaires flexibles",
            "label_en": "Flexible Hours",
            "description": "Horaires flexibles",
            "order": 3,
            "metadata": {"color": "#8B5CF6", "icon": "adjustments-horizontal"}
        },
        {
            "code": "shift_work",
            "label_fr": "Travail posté",
            "label_en": "Shift Work",
            "description": "Travail en équipes/postes",
            "order": 4,
            "metadata": {"color": "#F59E0B", "icon": "arrow-path"}
        },
    ],
    
    # Salary ranges
    "salary_ranges": [
        {
            "code": "range_1",
            "label_fr": "< 500 000 FCFA",
            "label_en": "< 500k XAF",
            "description": "Moins de 500 000 FCFA",
            "order": 1,
            "metadata": {"color": "#10B981", "min": 0, "max": 500000}
        },
        {
            "code": "range_2",
            "label_fr": "500k - 1M FCFA",
            "label_en": "500k - 1M XAF",
            "description": "Entre 500 000 et 1 000 000 FCFA",
            "order": 2,
            "metadata": {"color": "#3B82F6", "min": 500000, "max": 1000000}
        },
        {
            "code": "range_3",
            "label_fr": "1M - 2M FCFA",
            "label_en": "1M - 2M XAF",
            "description": "Entre 1 et 2 millions FCFA",
            "order": 3,
            "metadata": {"color": "#8B5CF6", "min": 1000000, "max": 2000000}
        },
        {
            "code": "range_4",
            "label_fr": "2M - 5M FCFA",
            "label_en": "2M - 5M XAF",
            "description": "Entre 2 et 5 millions FCFA",
            "order": 4,
            "metadata": {"color": "#F59E0B", "min": 2000000, "max": 5000000}
        },
        {
            "code": "range_5",
            "label_fr": "> 5M FCFA",
            "label_en": "> 5M XAF",
            "description": "Plus de 5 millions FCFA",
            "order": 5,
            "metadata": {"color": "#EF4444", "min": 5000000, "max": None}
        },
    ],
}


async def add_missing_references():
    """Ajouter les références manquantes"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🔄 Connexion à MongoDB...")
    print(f"📊 Base de données: auth_db")
    print(f"📦 Collection: system_references\n")
    
    stats = {
        "added": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    for category, references in MISSING_REFERENCES.items():
        print(f"\n📁 Catégorie: {category}")
        print(f"   Références à ajouter: {len(references)}")
        
        for ref in references:
            try:
                # Vérifier si la référence existe déjà
                existing = await db.system_references.find_one({
                    "category": category,
                    "code": ref["code"]
                })
                
                if existing:
                    print(f"   ⏭️  {ref['code']} - Déjà existe (skipped)")
                    stats["skipped"] += 1
                    continue
                
                # Créer la nouvelle référence
                new_ref = {
                    "id": str(uuid.uuid4()),
                    "category": category,
                    "code": ref["code"],
                    "label_fr": ref["label_fr"],
                    "label_en": ref.get("label_en", ref["label_fr"]),
                    "description": ref.get("description", ""),
                    "order": ref.get("order", 0),
                    "metadata": ref.get("metadata", {}),
                    "is_active": True,
                    "is_system": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                
                await db.system_references.insert_one(new_ref)
                print(f"   ✅ {ref['code']} - Ajouté ({ref['label_fr']})")
                stats["added"] += 1
                
            except Exception as e:
                print(f"   ❌ {ref['code']} - Erreur: {str(e)}")
                stats["errors"] += 1
    
    # Statistiques finales
    print("\n" + "="*60)
    print("📊 STATISTIQUES FINALES")
    print("="*60)
    print(f"✅ Références ajoutées: {stats['added']}")
    print(f"⏭️  Références déjà existantes: {stats['skipped']}")
    print(f"❌ Erreurs: {stats['errors']}")
    print(f"📦 Total traité: {stats['added'] + stats['skipped'] + stats['errors']}")
    
    # Compter les références par catégorie
    print("\n" + "="*60)
    print("📈 RÉFÉRENCES PAR CATÉGORIE (après ajout)")
    print("="*60)
    
    categories = await db.system_references.distinct("category")
    total = 0
    for cat in sorted(categories):
        count = await db.system_references.count_documents({
            "category": cat,
            "is_active": True
        })
        total += count
        print(f"{cat:25} : {count:3} références actives")
    
    print(f"{'─'*60}")
    print(f"{'TOTAL':25} : {total:3} références actives")
    
    client.close()


if __name__ == "__main__":
    print("🚀 Ajout des références importantes manquantes\n")
    asyncio.run(add_missing_references())
    print("\n✅ Script terminé avec succès!")
