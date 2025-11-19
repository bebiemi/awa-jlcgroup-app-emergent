"""
Script de migration : Ajouter les champs représentant légal aux validations existantes
Phase 1 : Détection + Badge
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.auth_db


async def migrate_validations():
    """Ajouter les nouveaux champs aux validations existantes"""
    
    print("🔄 Migration des validations - Ajout champs représentant légal...")
    
    # Récupérer toutes les validations de type "company"
    validations = await db.validations.find({"validation_type": "company"}).to_list(None)
    
    print(f"📊 {len(validations)} validations de type 'company' trouvées")
    
    updated_count = 0
    
    for validation in validations:
        # Récupérer l'utilisateur associé
        user = await db.users.find_one({"id": validation["user_id"]}, {"_id": 0})
        
        if not user:
            print(f"⚠️  User {validation['user_id']} non trouvé pour validation {validation['id']}")
            continue
        
        # Extraire les infos du représentant légal depuis les données dynamiques
        # Vérifier si l'utilisateur a un company_data avec representant_legal
        company_data = user.get("company_data", {})
        representant_legal = company_data.get("representant_legal", "")
        
        # Si pas trouvé, utiliser le full_name de l'utilisateur
        if not representant_legal:
            representant_legal = user.get("full_name", "")
        
        # Email du représentant = email de l'utilisateur
        representant_email = user.get("email", "")
        
        # Mettre à jour la validation
        update_data = {
            "representant_legal_nom": representant_legal,
            "representant_legal_email": representant_email,
            "has_existing_representant": False,
            "existing_representant_user_id": None,
            "existing_representant_entreprises": [],
            "contact_confirmation": False,
            "rattachement_status": None,
            "rattachement_to_entreprise_id": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.validations.update_one(
            {"id": validation["id"]},
            {"$set": update_data}
        )
        
        updated_count += 1
        print(f"  ✅ Validation {validation['id']}: {representant_legal} <{representant_email}>")
    
    print(f"\n✅ Migration terminée : {updated_count} validations mises à jour")


async def add_entreprise_fields():
    """Ajouter les champs de liaison aux entreprises existantes"""
    
    print("\n🔄 Migration des entreprises - Ajout champs de liaison...")
    
    entreprises = await db.entreprises.find({}).to_list(None)
    
    print(f"📊 {len(entreprises)} entreprises trouvées")
    
    updated_count = 0
    
    for entreprise in entreprises:
        update_data = {
            "representant_legal_nom": entreprise.get("legal_representative", ""),
            "representant_legal_email": entreprise.get("email", ""),
            "user_id": entreprise.get("created_by", None),
            "linked_entreprises": [],
            "grouping_status": "independent",
            "grouping_parent_id": None,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.entreprises.update_one(
            {"id": entreprise["id"]},
            {"$set": update_data}
        )
        
        updated_count += 1
    
    print(f"✅ {updated_count} entreprises mises à jour")


async def create_grouping_requests_collection():
    """Créer la collection pour les demandes de regroupement"""
    
    print("\n🔄 Création de la collection entreprise_grouping_requests...")
    
    # Vérifier si la collection existe
    collections = await db.list_collection_names()
    
    if "entreprise_grouping_requests" in collections:
        print("⚠️  Collection 'entreprise_grouping_requests' existe déjà")
    else:
        # Créer la collection avec un index
        await db.create_collection("entreprise_grouping_requests")
        
        # Créer des index
        await db.entreprise_grouping_requests.create_index([("entreprise_1_id", 1)])
        await db.entreprise_grouping_requests.create_index([("entreprise_2_id", 1)])
        await db.entreprise_grouping_requests.create_index([("status", 1)])
        
        print("✅ Collection 'entreprise_grouping_requests' créée avec index")


async def main():
    try:
        print("=" * 80)
        print("🚀 MIGRATION PHASE 1 : DÉTECTION + BADGE")
        print("=" * 80)
        
        await migrate_validations()
        await add_entreprise_fields()
        await create_grouping_requests_collection()
        
        print("\n" + "=" * 80)
        print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 80)
        
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
