"""
Initialize/Update Complete Reference Data
Ensures all reference categories are properly populated with default values
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from uuid import uuid4

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


# Define all reference data according to application needs
REFERENCE_DATA = {
    "roles": [
        {"code": "admin", "label_fr": "Administrateur", "label_en": "Administrator", "order": 1},
        {"code": "commercial", "label_fr": "Commercial", "label_en": "Sales", "order": 2},
        {"code": "interim", "label_fr": "Intérimaire", "label_en": "Temporary Worker", "order": 3},
        {"code": "company", "label_fr": "Entreprise", "label_en": "Company", "order": 4},
        {"code": "agency", "label_fr": "Agence", "label_en": "Agency", "order": 5},
        {"code": "candidat", "label_fr": "Candidat", "label_en": "Applicant", "order": 6},
    ],
    
    "user_statuses": [
        {"code": "active", "label_fr": "Actif", "label_en": "Active", "order": 1},
        {"code": "pending", "label_fr": "En attente", "label_en": "Pending", "order": 2},
        {"code": "suspended", "label_fr": "Suspendu", "label_en": "Suspended", "order": 3},
        {"code": "archived", "label_fr": "Archivé", "label_en": "Archived", "order": 4},
    ],
    
    "mission_statuses": [
        {"code": "draft", "label_fr": "Brouillon", "label_en": "Draft", "order": 1},
        {"code": "published", "label_fr": "Publiée", "label_en": "Published", "order": 2},
        {"code": "in_progress", "label_fr": "En cours", "label_en": "In Progress", "order": 3},
        {"code": "completed", "label_fr": "Terminée", "label_en": "Completed", "order": 4},
        {"code": "cancelled", "label_fr": "Annulée", "label_en": "Cancelled", "order": 5},
        {"code": "closed", "label_fr": "Clôturée", "label_en": "Closed", "order": 6},
    ],
    
    "application_statuses": [
        {"code": "submitted", "label_fr": "Soumise", "label_en": "Submitted", "order": 1},
        {"code": "under_review", "label_fr": "En examen", "label_en": "Under Review", "order": 2},
        {"code": "shortlisted", "label_fr": "Présélectionnée", "label_en": "Shortlisted", "order": 3},
        {"code": "interview", "label_fr": "Entretien", "label_en": "Interview", "order": 4},
        {"code": "accepted", "label_fr": "Acceptée", "label_en": "Accepted", "order": 5},
        {"code": "rejected", "label_fr": "Refusée", "label_en": "Rejected", "order": 6},
        {"code": "withdrawn", "label_fr": "Retirée", "label_en": "Withdrawn", "order": 7},
    ],
    
    "validation_types": [
        {"code": "profile", "label_fr": "Profil", "label_en": "Profile", "order": 1},
        {"code": "document", "label_fr": "Document", "label_en": "Document", "order": 2},
        {"code": "mission", "label_fr": "Mission", "label_en": "Mission", "order": 3},
        {"code": "timesheet", "label_fr": "Feuille de temps", "label_en": "Timesheet", "order": 4},
        {"code": "medical", "label_fr": "Visite médicale", "label_en": "Medical Check", "order": 5},
    ],
    
    "validation_statuses": [
        {"code": "pending", "label_fr": "En attente", "label_en": "Pending", "order": 1},
        {"code": "approved", "label_fr": "Approuvée", "label_en": "Approved", "order": 2},
        {"code": "rejected", "label_fr": "Rejetée", "label_en": "Rejected", "order": 3},
        {"code": "revision_required", "label_fr": "Révision requise", "label_en": "Revision Required", "order": 4},
    ],
    
    "contract_types": [
        {"code": "cdi", "label_fr": "CDI - Contrat à Durée Indéterminée", "label_en": "Permanent Contract", "order": 1},
        {"code": "cdd", "label_fr": "CDD - Contrat à Durée Déterminée", "label_en": "Fixed-term Contract", "order": 2},
        {"code": "interim", "label_fr": "Intérim", "label_en": "Temporary Work", "order": 3},
        {"code": "freelance", "label_fr": "Freelance", "label_en": "Freelance", "order": 4},
        {"code": "stage", "label_fr": "Stage", "label_en": "Internship", "order": 5},
        {"code": "alternance", "label_fr": "Alternance", "label_en": "Work-Study", "order": 6},
    ],
    
    "document_types": [
        {"code": "cv", "label_fr": "CV", "label_en": "Resume", "order": 1},
        {"code": "id_card", "label_fr": "Carte d'identité", "label_en": "ID Card", "order": 2},
        {"code": "passport", "label_fr": "Passeport", "label_en": "Passport", "order": 3},
        {"code": "diploma", "label_fr": "Diplôme", "label_en": "Diploma", "order": 4},
        {"code": "certificate", "label_fr": "Certificat", "label_en": "Certificate", "order": 5},
        {"code": "medical_certificate", "label_fr": "Certificat médical", "label_en": "Medical Certificate", "order": 6},
        {"code": "work_permit", "label_fr": "Permis de travail", "label_en": "Work Permit", "order": 7},
        {"code": "residence_permit", "label_fr": "Titre de séjour", "label_en": "Residence Permit", "order": 8},
        {"code": "social_security", "label_fr": "Carte de sécurité sociale", "label_en": "Social Security Card", "order": 9},
        {"code": "bank_details", "label_fr": "RIB", "label_en": "Bank Details", "order": 10},
        {"code": "other", "label_fr": "Autre", "label_en": "Other", "order": 99},
    ],
    
    "experience_levels": [
        {"code": "entry", "label_fr": "Débutant (0-2 ans)", "label_en": "Entry Level (0-2 years)", "order": 1},
        {"code": "junior", "label_fr": "Junior (2-5 ans)", "label_en": "Junior (2-5 years)", "order": 2},
        {"code": "intermediate", "label_fr": "Intermédiaire (5-8 ans)", "label_en": "Intermediate (5-8 years)", "order": 3},
        {"code": "senior", "label_fr": "Senior (8-12 ans)", "label_en": "Senior (8-12 years)", "order": 4},
        {"code": "expert", "label_fr": "Expert (12+ ans)", "label_en": "Expert (12+ years)", "order": 5},
    ],
    
    "education_levels": [
        {"code": "no_diploma", "label_fr": "Sans diplôme", "label_en": "No Diploma", "order": 1},
        {"code": "cap_bep", "label_fr": "CAP/BEP", "label_en": "Vocational Certificate", "order": 2},
        {"code": "bac", "label_fr": "Baccalauréat", "label_en": "High School Diploma", "order": 3},
        {"code": "bac_2", "label_fr": "Bac+2 (BTS/DUT)", "label_en": "2-year Degree", "order": 4},
        {"code": "bac_3", "label_fr": "Bac+3 (Licence)", "label_en": "Bachelor's Degree", "order": 5},
        {"code": "bac_5", "label_fr": "Bac+5 (Master)", "label_en": "Master's Degree", "order": 6},
        {"code": "bac_8", "label_fr": "Bac+8 (Doctorat)", "label_en": "Doctorate", "order": 7},
    ],
    
    "skill_categories": [
        {"code": "technical", "label_fr": "Compétences Techniques", "label_en": "Technical Skills", "order": 1},
        {"code": "soft_skills", "label_fr": "Compétences Comportementales", "label_en": "Soft Skills", "order": 2},
        {"code": "languages", "label_fr": "Langues", "label_en": "Languages", "order": 3},
        {"code": "tools", "label_fr": "Outils & Logiciels", "label_en": "Tools & Software", "order": 4},
        {"code": "certifications", "label_fr": "Certifications", "label_en": "Certifications", "order": 5},
    ],
    
    "work_schedules": [
        {"code": "full_time", "label_fr": "Temps plein", "label_en": "Full Time", "order": 1},
        {"code": "part_time", "label_fr": "Temps partiel", "label_en": "Part Time", "order": 2},
        {"code": "shift_work", "label_fr": "Travail posté", "label_en": "Shift Work", "order": 3},
        {"code": "night_shift", "label_fr": "Nuit", "label_en": "Night Shift", "order": 4},
        {"code": "weekend", "label_fr": "Weekend", "label_en": "Weekend", "order": 5},
        {"code": "flexible", "label_fr": "Horaires flexibles", "label_en": "Flexible Hours", "order": 6},
    ],
    
    "salary_ranges": [
        {"code": "less_20k", "label_fr": "Moins de 20K€", "label_en": "Less than 20K€", "order": 1},
        {"code": "20k_30k", "label_fr": "20K€ - 30K€", "label_en": "20K€ - 30K€", "order": 2},
        {"code": "30k_40k", "label_fr": "30K€ - 40K€", "label_en": "30K€ - 40K€", "order": 3},
        {"code": "40k_50k", "label_fr": "40K€ - 50K€", "label_en": "40K€ - 50K€", "order": 4},
        {"code": "50k_70k", "label_fr": "50K€ - 70K€", "label_en": "50K€ - 70K€", "order": 5},
        {"code": "70k_100k", "label_fr": "70K€ - 100K€", "label_en": "70K€ - 100K€", "order": 6},
        {"code": "more_100k", "label_fr": "Plus de 100K€", "label_en": "More than 100K€", "order": 7},
    ],
    
    "medical_aptitudes": [
        {"code": "fit", "label_fr": "Apte", "label_en": "Fit", "order": 1},
        {"code": "fit_with_restrictions", "label_fr": "Apte avec restrictions", "label_en": "Fit with Restrictions", "order": 2},
        {"code": "temporarily_unfit", "label_fr": "Inapte temporaire", "label_en": "Temporarily Unfit", "order": 3},
        {"code": "unfit", "label_fr": "Inapte", "label_en": "Unfit", "order": 4},
        {"code": "pending", "label_fr": "En attente de visite", "label_en": "Pending Visit", "order": 5},
    ],
    
    "countries": [
        {"code": "GA", "label_fr": "Gabon", "label_en": "Gabon", "order": 1},
        {"code": "FR", "label_fr": "France", "label_en": "France", "order": 2},
        {"code": "CM", "label_fr": "Cameroun", "label_en": "Cameroon", "order": 3},
        {"code": "CI", "label_fr": "Côte d'Ivoire", "label_en": "Ivory Coast", "order": 4},
        {"code": "SN", "label_fr": "Sénégal", "label_en": "Senegal", "order": 5},
        {"code": "CD", "label_fr": "RD Congo", "label_en": "DR Congo", "order": 6},
        {"code": "CG", "label_fr": "Congo", "label_en": "Congo", "order": 7},
        {"code": "BJ", "label_fr": "Bénin", "label_en": "Benin", "order": 8},
        {"code": "TG", "label_fr": "Togo", "label_en": "Togo", "order": 9},
        {"code": "MA", "label_fr": "Maroc", "label_en": "Morocco", "order": 10},
    ],
}


async def init_references():
    """Initialize or update all reference data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    collection = db.system_references
    
    now = datetime.now(timezone.utc)
    stats = {"created": 0, "updated": 0, "unchanged": 0}
    
    for category, items in REFERENCE_DATA.items():
        print(f"\n📋 Processing category: {category}")
        
        for item in items:
            code = item["code"]
            
            # Check if reference already exists
            existing = await collection.find_one({
                "category": category,
                "code": code
            })
            
            reference_doc = {
                "id": existing.get("id", str(uuid4())) if existing else str(uuid4()),
                "category": category,
                "code": code,
                "label_fr": item["label_fr"],
                "label_en": item.get("label_en", item["label_fr"]),
                "description": item.get("description", ""),
                "order": item["order"],
                "is_active": existing.get("is_active", True) if existing else True,
                "metadata": existing.get("metadata", {}) if existing else {},
                "created_at": existing.get("created_at", now) if existing else now,
                "updated_at": now,
            }
            
            if existing:
                # Check if update is needed
                needs_update = (
                    existing.get("label_fr") != reference_doc["label_fr"] or
                    existing.get("label_en") != reference_doc["label_en"] or
                    existing.get("order") != reference_doc["order"]
                )
                
                if needs_update:
                    await collection.update_one(
                        {"id": reference_doc["id"]},
                        {"$set": reference_doc}
                    )
                    print(f"  ✓ Updated: {code}")
                    stats["updated"] += 1
                else:
                    stats["unchanged"] += 1
            else:
                await collection.insert_one(reference_doc)
                print(f"  ✓ Created: {code} - {item['label_fr']}")
                stats["created"] += 1
    
    print(f"\n✅ Reference data initialization complete!")
    print(f"   - Created: {stats['created']} references")
    print(f"   - Updated: {stats['updated']} references")
    print(f"   - Unchanged: {stats['unchanged']} references")
    print(f"   - Total categories: {len(REFERENCE_DATA)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(init_references())
