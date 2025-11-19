"""
Script pour créer les champs de formulaire d'entreprise par défaut
Ces champs seront utilisés à la fois pour l'inscription publique et la page de paramètres
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.auth_db

async def create_default_fields():
    """Créer les champs de formulaire par défaut pour les entreprises"""
    
    # Définir les champs de base
    default_fields = [
        # ===== CHAMPS OBLIGATOIRES POUR L'INSCRIPTION =====
        {
            "id": str(uuid.uuid4()),
            "field_key": "nom_commercial",
            "field_label": "Nom commercial",
            "field_type": "text",
            "category": "informations_generales",
            "order": 1,
            "placeholder": "Nom sous lequel l'entreprise est connue",
            "help_text": "Le nom commercial de votre entreprise",
            "validation": {
                "required": True,
                "min_length": 2,
                "max_length": 200,
                "custom_error_message": "Le nom commercial est requis (2-200 caractères)"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "raison_sociale",
            "field_label": "Raison sociale",
            "field_type": "text",
            "category": "informations_legales",
            "order": 2,
            "placeholder": "Raison sociale officielle",
            "help_text": "La raison sociale officielle de votre entreprise",
            "validation": {
                "required": True,
                "min_length": 2,
                "max_length": 200,
                "custom_error_message": "La raison sociale est requise (2-200 caractères)"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "nif",
            "field_label": "NIF (Numéro d'Identification Fiscale)",
            "field_type": "text",
            "category": "informations_legales",
            "order": 3,
            "placeholder": "Ex: 123456789A",
            "help_text": "Numéro d'identification fiscale (optionnel)",
            "validation": {
                "required": False,
                "min_length": 9,
                "max_length": 20,
                "pattern": "^[A-Z0-9]+$",
                "custom_error_message": "Format NIF invalide (lettres majuscules et chiffres uniquement)"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "siret",
            "field_label": "SIRET",
            "field_type": "text",
            "category": "informations_legales",
            "order": 4,
            "placeholder": "14 chiffres",
            "help_text": "Numéro SIRET à 14 chiffres (optionnel)",
            "validation": {
                "required": False,
                "min_length": 14,
                "max_length": 14,
                "pattern": "^[0-9]{14}$",
                "custom_error_message": "Le SIRET doit contenir exactement 14 chiffres"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "email",
            "field_label": "Email de l'entreprise",
            "field_type": "email",
            "category": "contact",
            "order": 5,
            "placeholder": "contact@entreprise.com",
            "help_text": "Adresse email principale de l'entreprise",
            "validation": {
                "required": True,
                "custom_error_message": "L'email de l'entreprise est requis"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "telephone",
            "field_label": "Téléphone",
            "field_type": "tel",
            "category": "contact",
            "order": 6,
            "placeholder": "+33 1 23 45 67 89",
            "help_text": "Numéro de téléphone principal",
            "validation": {
                "required": True,
                "custom_error_message": "Le téléphone est requis"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "representant_legal",
            "field_label": "Représentant légal",
            "field_type": "text",
            "category": "informations_legales",
            "order": 7,
            "placeholder": "Nom complet du représentant",
            "help_text": "Nom et prénom du représentant légal de l'entreprise",
            "validation": {
                "required": True,
                "min_length": 2,
                "max_length": 100,
                "custom_error_message": "Le représentant légal est requis (2-100 caractères)"
            },
            "visible_for_roles": ["admin", "company", "public"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        
        # ===== CHAMPS OPTIONNELS (POUR PAGE DE PARAMÈTRES) =====
        {
            "id": str(uuid.uuid4()),
            "field_key": "adresse",
            "field_label": "Adresse",
            "field_type": "textarea",
            "category": "localisation",
            "order": 10,
            "placeholder": "Numéro et nom de rue",
            "help_text": "Adresse complète du siège social",
            "validation": {
                "required": False,
                "max_length": 500
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "code_postal",
            "field_label": "Code postal",
            "field_type": "text",
            "category": "localisation",
            "order": 11,
            "placeholder": "75001",
            "help_text": "Code postal",
            "validation": {
                "required": False,
                "max_length": 10
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "ville",
            "field_label": "Ville",
            "field_type": "text",
            "category": "localisation",
            "order": 12,
            "placeholder": "Paris",
            "help_text": "Ville du siège social",
            "validation": {
                "required": False,
                "max_length": 100
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "pays",
            "field_label": "Pays",
            "field_type": "text",
            "category": "localisation",
            "order": 13,
            "placeholder": "France",
            "help_text": "Pays du siège social",
            "default_value": "France",
            "validation": {
                "required": False,
                "max_length": 100
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "secteur_activite",
            "field_label": "Secteur d'activité",
            "field_type": "text",
            "category": "informations_generales",
            "order": 20,
            "placeholder": "Ex: Informatique, BTP, Santé...",
            "help_text": "Domaine d'activité principal de l'entreprise",
            "validation": {
                "required": False,
                "max_length": 200
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "effectif",
            "field_label": "Effectif",
            "field_type": "select",
            "category": "informations_generales",
            "order": 21,
            "placeholder": "Choisir la taille de l'entreprise",
            "help_text": "Nombre d'employés",
            "options": [
                {"label": "1-10", "value": "1-10"},
                {"label": "11-50", "value": "11-50"},
                {"label": "51-200", "value": "51-200"},
                {"label": "201-500", "value": "201-500"},
                {"label": "500+", "value": "500+"}
            ],
            "validation": {
                "required": False
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "site_web",
            "field_label": "Site web",
            "field_type": "url",
            "category": "contact",
            "order": 22,
            "placeholder": "https://www.entreprise.com",
            "help_text": "URL du site web de l'entreprise",
            "validation": {
                "required": False,
                "max_length": 200
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "id": str(uuid.uuid4()),
            "field_key": "description",
            "field_label": "Description de l'entreprise",
            "field_type": "textarea",
            "category": "informations_generales",
            "order": 23,
            "placeholder": "Présentez votre entreprise...",
            "help_text": "Description détaillée de votre entreprise et de ses activités",
            "validation": {
                "required": False,
                "max_length": 2000
            },
            "visible_for_roles": ["admin", "company"],
            "editable_for_roles": ["admin", "company"],
            "is_active": True,
            "is_system": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "system"
        }
    ]
    
    # Vérifier si les champs existent déjà
    existing_count = await db.entreprise_form_fields.count_documents({})
    if existing_count > 0:
        print(f"⚠️  {existing_count} champs existent déjà. Suppression des champs existants...")
        await db.entreprise_form_fields.delete_many({})
    
    # Insérer les champs
    result = await db.entreprise_form_fields.insert_many(default_fields)
    print(f"✅ {len(result.inserted_ids)} champs de formulaire créés avec succès!")
    
    # Afficher les champs créés
    print("\n📋 Champs créés:")
    print("=" * 80)
    
    required_fields = [f for f in default_fields if f['validation']['required']]
    optional_fields = [f for f in default_fields if not f['validation']['required']]
    
    print(f"\n✅ CHAMPS OBLIGATOIRES (pour inscription) - {len(required_fields)} champs:")
    for field in required_fields:
        print(f"  • {field['field_label']} ({field['field_key']}) - {field['category']}")
    
    print(f"\n⚪ CHAMPS OPTIONNELS (page paramètres) - {len(optional_fields)} champs:")
    for field in optional_fields:
        print(f"  • {field['field_label']} ({field['field_key']}) - {field['category']}")
    
    print("\n📁 Catégories créées:")
    categories = set([f['category'] for f in default_fields])
    for cat in sorted(categories):
        count = len([f for f in default_fields if f['category'] == cat])
        print(f"  • {cat}: {count} champs")

async def main():
    try:
        await create_default_fields()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
