#!/usr/bin/env python3
"""
Script pour ajouter un index unique sur le champ 'code' des permissions
et vérifier qu'il n'y a pas de permissions sans code valide
"""
import os
import sys
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

def main():
    # Connexion à MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client['auth_db']
    permissions_collection = db.permissions
    
    print("=" * 70)
    print("AJOUT D'INDEX UNIQUE SUR LE CHAMP 'code' DES PERMISSIONS")
    print("=" * 70)
    
    # 1. Vérifier les permissions sans code
    print("\n1️⃣ Vérification des permissions sans code...")
    perms_without_code = list(permissions_collection.find({
        '$or': [
            {'code': {'$exists': False}}, 
            {'code': None}, 
            {'code': ''}
        ]
    }))
    
    if perms_without_code:
        print(f"❌ ERREUR: {len(perms_without_code)} permissions sans code trouvées!")
        print("Ces permissions doivent être corrigées avant de créer l'index.")
        for p in perms_without_code[:5]:
            print(f"   - ID: {p.get('id', 'N/A')}")
        return 1
    
    print(f"✅ Aucune permission sans code (total: {permissions_collection.count_documents({})})")
    
    # 2. Vérifier les doublons
    print("\n2️⃣ Vérification des codes en doublon...")
    pipeline = [
        {'$group': {'_id': '$code', 'count': {'$sum': 1}, 'ids': {'$push': '$id'}}},
        {'$match': {'count': {'$gt': 1}}}
    ]
    duplicates = list(permissions_collection.aggregate(pipeline))
    
    if duplicates:
        print(f"❌ ERREUR: {len(duplicates)} codes en doublon trouvés!")
        for dup in duplicates[:5]:
            print(f"   - Code '{dup['_id']}' apparaît {dup['count']} fois")
            print(f"     IDs: {', '.join([id[:8] for id in dup['ids']])}")
        return 1
    
    print("✅ Aucun code en doublon")
    
    # 3. Lister les index existants
    print("\n3️⃣ Index existants sur la collection permissions:")
    existing_indexes = permissions_collection.list_indexes()
    for idx in existing_indexes:
        print(f"   - {idx['name']}: {idx.get('key', {})}")
    
    # 4. Créer l'index unique sur 'code'
    print("\n4️⃣ Création de l'index unique sur le champ 'code'...")
    try:
        index_name = permissions_collection.create_index(
            [("code", ASCENDING)],
            unique=True,
            name="code_unique_idx"
        )
        print(f"✅ Index créé avec succès: {index_name}")
    except DuplicateKeyError as e:
        print(f"❌ ERREUR: Impossible de créer l'index unique - {e}")
        return 1
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️  L'index existe déjà")
        else:
            print(f"❌ ERREUR: {e}")
            return 1
    
    # 5. Vérifier que l'index a été créé
    print("\n5️⃣ Vérification de l'index créé:")
    existing_indexes = list(permissions_collection.list_indexes())
    code_index_found = False
    for idx in existing_indexes:
        if 'code' in idx.get('key', {}):
            code_index_found = True
            print(f"   ✅ Index trouvé: {idx['name']}")
            print(f"      - Unique: {idx.get('unique', False)}")
            print(f"      - Key: {idx.get('key', {})}")
    
    if not code_index_found:
        print("   ❌ Index sur 'code' non trouvé!")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ SUCCÈS - Index unique sur 'code' configuré")
    print("=" * 70)
    print("\nLes permissions sans code ou avec code en doublon seront")
    print("automatiquement rejetées par MongoDB.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
