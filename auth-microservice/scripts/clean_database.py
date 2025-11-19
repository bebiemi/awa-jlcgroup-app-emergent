#!/usr/bin/env python3
"""
Nettoyage complet de la base de données - Garder uniquement admin
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    print("=" * 80)
    print("🧹 NETTOYAGE COMPLET DE LA BASE DE DONNÉES")
    print("=" * 80)
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n⚠️  ATTENTION : Cette opération va supprimer toutes les données sauf l'admin !")
    
    # Compter avant suppression
    print("\n📊 État actuel de la base :")
    print(f"   Utilisateurs : {await db.users.count_documents({})}")
    print(f"   Entreprises : {await db.entreprises.count_documents({})}")
    print(f"   Missions : {await db.missions.count_documents({})}")
    print(f"   Besoins : {await db.besoins.count_documents({})}")
    print(f"   Candidatures : {await db.applications.count_documents({})}")
    
    # 1. Supprimer tous les utilisateurs SAUF admin
    print("\n1️⃣ Suppression des utilisateurs (sauf admin)...")
    result = await db.users.delete_many({"username": {"$ne": "admin"}})
    print(f"   ✅ {result.deleted_count} utilisateurs supprimés")
    
    # 2. Supprimer toutes les entreprises
    print("\n2️⃣ Suppression des entreprises...")
    result = await db.entreprises.delete_many({})
    print(f"   ✅ {result.deleted_count} entreprises supprimées")
    
    # 3. Supprimer toutes les missions
    print("\n3️⃣ Suppression des missions...")
    result = await db.missions.delete_many({})
    print(f"   ✅ {result.deleted_count} missions supprimées")
    
    # 4. Supprimer tous les besoins
    print("\n4️⃣ Suppression des besoins...")
    result = await db.besoins.delete_many({})
    print(f"   ✅ {result.deleted_count} besoins supprimés")
    
    # 5. Supprimer toutes les candidatures
    print("\n5️⃣ Suppression des candidatures...")
    result = await db.applications.delete_many({})
    print(f"   ✅ {result.deleted_count} candidatures supprimées")
    
    # 6. Supprimer les documents
    print("\n6️⃣ Suppression des documents...")
    result = await db.documents.delete_many({})
    print(f"   ✅ {result.deleted_count} documents supprimés")
    
    # État final
    print("\n" + "=" * 80)
    print("📊 État final de la base :")
    print(f"   Utilisateurs : {await db.users.count_documents({})} (admin uniquement)")
    print(f"   Entreprises : {await db.entreprises.count_documents({})}")
    print(f"   Missions : {await db.missions.count_documents({})}")
    print(f"   Besoins : {await db.besoins.count_documents({})}")
    print(f"   Candidatures : {await db.applications.count_documents({})}")
    print("=" * 80)
    print("\n✅ NETTOYAGE TERMINÉ - Base de données propre")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
