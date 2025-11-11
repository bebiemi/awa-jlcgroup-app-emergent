"""
Initialize Default Configurations
Creates default form schemas, workflows, and reference data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid


async def initialize_default_configs():
    """Initialize all default configurations"""
    
    # Get MongoDB connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "auth_db")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc)
    
    print("🔧 Initializing default configurations...")
    
    # ==================== FORM SCHEMA: BESOIN ====================
    
    print("📝 Creating form schema: besoin...")
    
    besoin_form = {
        "id": str(uuid.uuid4()),
        "form_type": "besoin",
        "version": "1.0",
        "fields": [
            {
                "key": "titre",
                "type": "text",
                "label": {"fr": "Titre du poste", "en": "Job Title"},
                "placeholder": {"fr": "Ex: Développeur Full Stack Senior", "en": "Ex: Senior Full Stack Developer"},
                "required": True,
                "validations": [
                    {"type": "required", "message": {"fr": "Le titre est obligatoire", "en": "Title is required"}},
                    {"type": "min_length", "value": 3, "message": {"fr": "Minimum 3 caractères", "en": "Minimum 3 characters"}},
                    {"type": "max_length", "value": 200, "message": {"fr": "Maximum 200 caractères", "en": "Maximum 200 characters"}}
                ],
                "order": 1,
                "group": "basic_info",
                "active": True
            },
            {
                "key": "description",
                "type": "textarea",
                "label": {"fr": "Description du besoin", "en": "Job Description"},
                "placeholder": {"fr": "Décrivez le poste et les missions", "en": "Describe the position and responsibilities"},
                "help_text": {"fr": "Soyez précis sur les attentes et le contexte", "en": "Be specific about expectations and context"},
                "required": True,
                "validations": [
                    {"type": "required", "message": {"fr": "La description est obligatoire", "en": "Description is required"}},
                    {"type": "min_length", "value": 10, "message": {"fr": "Minimum 10 caractères", "en": "Minimum 10 characters"}}
                ],
                "order": 2,
                "group": "basic_info",
                "active": True
            },
            {
                "key": "duree",
                "type": "select",
                "label": {"fr": "Durée du contrat", "en": "Contract Duration"},
                "required": True,
                "options": [
                    {
                        "value": "indeterminee",
                        "label": {"fr": "Indéterminée (CDI)", "en": "Indefinite (Permanent)"},
                        "active": True
                    },
                    {
                        "value": "periode_precise",
                        "label": {"fr": "Période précise (CDD)", "en": "Fixed Period (Temporary)"},
                        "active": True
                    }
                ],
                "order": 3,
                "group": "contract_info",
                "active": True
            },
            {
                "key": "date_debut_souhaitee",
                "type": "date",
                "label": {"fr": "Date de début souhaitée", "en": "Desired Start Date"},
                "required": False,
                "depends_on": "duree",
                "depends_condition": {"eq": "periode_precise"},
                "order": 4,
                "group": "contract_info",
                "active": True
            },
            {
                "key": "date_fin_souhaitee",
                "type": "date",
                "label": {"fr": "Date de fin souhaitée", "en": "Desired End Date"},
                "required": False,
                "depends_on": "duree",
                "depends_condition": {"eq": "periode_precise"},
                "order": 5,
                "group": "contract_info",
                "active": True
            },
            {
                "key": "type_poste",
                "type": "select",
                "label": {"fr": "Type de poste", "en": "Position Type"},
                "required": True,
                "options": [
                    {"value": "CDI", "label": {"fr": "CDI", "en": "Permanent"}, "active": True},
                    {"value": "CDD", "label": {"fr": "CDD", "en": "Fixed-term"}, "active": True},
                    {"value": "interim", "label": {"fr": "Intérim", "en": "Temporary"}, "active": True},
                    {"value": "stage", "label": {"fr": "Stage", "en": "Internship"}, "active": True},
                    {"value": "alternance", "label": {"fr": "Alternance", "en": "Work-study"}, "active": True},
                    {"value": "freelance", "label": {"fr": "Freelance", "en": "Freelance"}, "active": True}
                ],
                "order": 6,
                "group": "contract_info",
                "active": True
            },
            {
                "key": "competences_attendues",
                "type": "multi_select",
                "label": {"fr": "Compétences attendues", "en": "Required Skills"},
                "placeholder": {"fr": "Sélectionnez les compétences", "en": "Select skills"},
                "required": True,
                "options": [],  # Will be populated from reference data
                "order": 7,
                "group": "requirements",
                "active": True
            },
            {
                "key": "pieces_jointes",
                "type": "file",
                "label": {"fr": "Documents joints", "en": "Attachments"},
                "help_text": {"fr": "Fichiers PDF, Word, Excel acceptés", "en": "PDF, Word, Excel files accepted"},
                "required": False,
                "order": 8,
                "group": "documents",
                "active": True
            }
        ],
        "groups": [
            {"key": "basic_info", "label": {"fr": "Informations de base", "en": "Basic Information"}, "order": 1},
            {"key": "contract_info", "label": {"fr": "Informations contractuelles", "en": "Contract Information"}, "order": 2},
            {"key": "requirements", "label": {"fr": "Exigences", "en": "Requirements"}, "order": 3},
            {"key": "documents", "label": {"fr": "Documents", "en": "Documents"}, "order": 4}
        ],
        "metadata": {"description": "Form for creating hiring needs"},
        "created_at": now,
        "updated_at": now
    }
    
    existing_besoin = await db.form_schemas.find_one({"form_type": "besoin"})
    if not existing_besoin:
        await db.form_schemas.insert_one(besoin_form)
        print("✅ Besoin form schema created")
    else:
        print("ℹ️  Besoin form schema already exists")
    
    # ==================== WORKFLOW: BESOIN ====================
    
    print("🔄 Creating workflow: besoin...")
    
    besoin_workflow = {
        "id": str(uuid.uuid4()),
        "entity_type": "besoin",
        "version": "1.0",
        "initial_status": "brouillon",
        "statuses": [
            {
                "key": "brouillon",
                "label": {"fr": "Brouillon", "en": "Draft"},
                "description": {"fr": "Besoin en cours de création", "en": "Need being created"},
                "color": "#9CA3AF",
                "icon": "edit",
                "allowed_transitions": ["soumis"],
                "permissions_required": [],
                "notifications": [],
                "order": 1,
                "is_terminal": False,
                "active": True
            },
            {
                "key": "soumis",
                "label": {"fr": "Soumis à JLC", "en": "Submitted to JLC"},
                "description": {"fr": "En attente de validation JLC", "en": "Awaiting JLC validation"},
                "color": "#3B82F6",
                "icon": "send",
                "allowed_transitions": ["analyse", "brouillon"],
                "permissions_required": ["besoins.submit"],
                "notifications": ["jlc_team"],
                "order": 2,
                "is_terminal": False,
                "active": True
            },
            {
                "key": "analyse",
                "label": {"fr": "Analyse en cours", "en": "Under Analysis"},
                "description": {"fr": "JLC analyse le besoin", "en": "JLC analyzing the need"},
                "color": "#F59E0B",
                "icon": "search",
                "allowed_transitions": ["mission_creee", "soumis"],
                "permissions_required": ["besoins.validate"],
                "notifications": [],
                "order": 3,
                "is_terminal": False,
                "active": True
            },
            {
                "key": "mission_creee",
                "label": {"fr": "Mission créée", "en": "Mission Created"},
                "description": {"fr": "Mission(s) créée(s) à partir du besoin", "en": "Mission(s) created from need"},
                "color": "#8B5CF6",
                "icon": "check-circle",
                "allowed_transitions": ["publication"],
                "permissions_required": ["besoins.convert_to_mission"],
                "notifications": ["entreprise"],
                "order": 4,
                "is_terminal": False,
                "active": True
            },
            {
                "key": "publication",
                "label": {"fr": "En recherche de profils", "en": "Looking for Candidates"},
                "description": {"fr": "Mission publiée, recherche active", "en": "Mission published, active search"},
                "color": "#10B981",
                "icon": "users",
                "allowed_transitions": ["pourvu"],
                "permissions_required": ["missions.publish"],
                "notifications": [],
                "order": 5,
                "is_terminal": False,
                "active": True
            },
            {
                "key": "pourvu",
                "label": {"fr": "Clôturé", "en": "Closed"},
                "description": {"fr": "Besoin pourvu, contrat signé", "en": "Need filled, contract signed"},
                "color": "#059669",
                "icon": "check",
                "allowed_transitions": [],
                "permissions_required": [],
                "notifications": ["entreprise", "jlc_team"],
                "order": 6,
                "is_terminal": True,
                "active": True
            }
        ],
        "metadata": {"description": "Workflow for hiring needs"},
        "created_at": now,
        "updated_at": now
    }
    
    existing_workflow = await db.workflow_configs.find_one({"entity_type": "besoin"})
    if not existing_workflow:
        await db.workflow_configs.insert_one(besoin_workflow)
        print("✅ Besoin workflow created")
    else:
        print("ℹ️  Besoin workflow already exists")
    
    # ==================== REFERENCE DATA: TYPES DE POSTE ====================
    
    print("📚 Creating reference data: types_poste...")
    
    types_poste = {
        "id": str(uuid.uuid4()),
        "reference_type": "types_poste",
        "version": "1.0",
        "items": [
            {"key": "CDI", "label": {"fr": "CDI", "en": "Permanent Contract"}, "order": 1, "active": True, "metadata": {}},
            {"key": "CDD", "label": {"fr": "CDD", "en": "Fixed-term Contract"}, "order": 2, "active": True, "metadata": {}},
            {"key": "interim", "label": {"fr": "Intérim", "en": "Temporary Work"}, "order": 3, "active": True, "metadata": {}},
            {"key": "stage", "label": {"fr": "Stage", "en": "Internship"}, "order": 4, "active": True, "metadata": {}},
            {"key": "alternance", "label": {"fr": "Alternance", "en": "Work-study Program"}, "order": 5, "active": True, "metadata": {}},
            {"key": "freelance", "label": {"fr": "Freelance", "en": "Freelance"}, "order": 6, "active": True, "metadata": {}}
        ],
        "metadata": {"description": "Types of employment contracts"},
        "created_at": now,
        "updated_at": now
    }
    
    existing_types = await db.reference_data.find_one({"reference_type": "types_poste"})
    if not existing_types:
        await db.reference_data.insert_one(types_poste)
        print("✅ Types de poste reference data created")
    else:
        print("ℹ️  Types de poste already exists")
    
    # ==================== REFERENCE DATA: COMPETENCES ====================
    
    print("📚 Creating reference data: competences...")
    
    competences = {
        "id": str(uuid.uuid4()),
        "reference_type": "competences",
        "version": "1.0",
        "items": [
            # Tech skills
            {"key": "react", "label": {"fr": "React", "en": "React"}, "order": 1, "active": True, "metadata": {"category": "tech"}},
            {"key": "nodejs", "label": {"fr": "Node.js", "en": "Node.js"}, "order": 2, "active": True, "metadata": {"category": "tech"}},
            {"key": "python", "label": {"fr": "Python", "en": "Python"}, "order": 3, "active": True, "metadata": {"category": "tech"}},
            {"key": "java", "label": {"fr": "Java", "en": "Java"}, "order": 4, "active": True, "metadata": {"category": "tech"}},
            {"key": "mongodb", "label": {"fr": "MongoDB", "en": "MongoDB"}, "order": 5, "active": True, "metadata": {"category": "tech"}},
            {"key": "postgresql", "label": {"fr": "PostgreSQL", "en": "PostgreSQL"}, "order": 6, "active": True, "metadata": {"category": "tech"}},
            {"key": "docker", "label": {"fr": "Docker", "en": "Docker"}, "order": 7, "active": True, "metadata": {"category": "tech"}},
            {"key": "kubernetes", "label": {"fr": "Kubernetes", "en": "Kubernetes"}, "order": 8, "active": True, "metadata": {"category": "tech"}},
            # Business skills
            {"key": "gestion_projet", "label": {"fr": "Gestion de projet", "en": "Project Management"}, "order": 20, "active": True, "metadata": {"category": "business"}},
            {"key": "communication", "label": {"fr": "Communication", "en": "Communication"}, "order": 21, "active": True, "metadata": {"category": "business"}},
            {"key": "leadership", "label": {"fr": "Leadership", "en": "Leadership"}, "order": 22, "active": True, "metadata": {"category": "business"}},
            {"key": "marketing", "label": {"fr": "Marketing", "en": "Marketing"}, "order": 23, "active": True, "metadata": {"category": "business"}},
        ],
        "metadata": {"description": "Skills and competencies"},
        "created_at": now,
        "updated_at": now
    }
    
    existing_comp = await db.reference_data.find_one({"reference_type": "competences"})
    if not existing_comp:
        await db.reference_data.insert_one(competences)
        print("✅ Compétences reference data created")
    else:
        print("ℹ️  Compétences already exists")
    
    print("\n✅ All default configurations initialized successfully!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_default_configs())
