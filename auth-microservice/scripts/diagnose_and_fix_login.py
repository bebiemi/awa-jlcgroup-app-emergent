#!/usr/bin/env python3
"""
Diagnostic complet et correction automatique du problème de connexion
"""
import asyncio
import sys
import os
import json
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

async def diagnose_and_fix():
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        print(f"🔌 Connecting to MongoDB: {mongo_url}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client['auth_db']
        
        username = "adminbe"
        password = "Awana2025!"
        
        print(f"\n{'='*60}")
        print(f"🔍 DIAGNOSTIC - Recherche de l'utilisateur: {username}")
        print(f"{'='*60}\n")
        
        # Étape 1: Trouver l'utilisateur
        user_doc = await db.users.find_one({
            "$or": [
                {"username": username},
                {"email": username}
            ],
            "provider": "local"
        })
        
        if not user_doc:
            print("❌ ERREUR: Utilisateur non trouvé!")
            print("\n🔍 Tentative de recherche sans filtre provider:")
            user_doc = await db.users.find_one({
                "$or": [
                    {"username": username},
                    {"email": username}
                ]
            })
            
            if user_doc:
                print(f"✓ Utilisateur trouvé avec provider: {user_doc.get('provider')}")
                print(f"⚠️ PROBLÈME: Le provider est '{user_doc.get('provider')}' au lieu de 'local'")
                
                # Correction du provider
                print("\n🔧 Correction du provider...")
                await db.users.update_one(
                    {"_id": user_doc["_id"]},
                    {"$set": {"provider": "local"}}
                )
                print("✅ Provider corrigé en 'local'")
                
                # Recharger l'utilisateur
                user_doc = await db.users.find_one({"_id": user_doc["_id"]})
            else:
                print("❌ Utilisateur introuvable dans la base de données!")
                sys.exit(1)
        
        print(f"✅ Utilisateur trouvé: {user_doc.get('username')}")
        
        # Étape 2: Vérifier les champs critiques
        print(f"\n{'='*60}")
        print("📋 VÉRIFICATION DES CHAMPS")
        print(f"{'='*60}\n")
        
        issues_found = []
        fixes_applied = []
        
        # Vérifier provider
        if user_doc.get('provider') != 'local':
            issues_found.append(f"Provider incorrect: {user_doc.get('provider')}")
        
        # Vérifier status
        current_status = user_doc.get('status')
        print(f"Status actuel: {current_status}")
        if current_status != 'active':
            issues_found.append(f"Status n'est pas 'active': {current_status}")
            print(f"  ⚠️ PROBLÈME: Status devrait être 'active'")
            
            # Correction du status
            print("  🔧 Correction du status...")
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"status": "active"}}
            )
            fixes_applied.append("Status corrigé en 'active'")
            print("  ✅ Status corrigé")
        else:
            print("  ✅ Status OK")
        
        # Vérifier is_active
        is_active = user_doc.get('is_active')
        print(f"is_active: {is_active}")
        if not is_active:
            issues_found.append("is_active n'est pas True")
            print("  ⚠️ PROBLÈME: is_active devrait être True")
            
            # Correction
            print("  🔧 Correction de is_active...")
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"is_active": True}}
            )
            fixes_applied.append("is_active corrigé en True")
            print("  ✅ is_active corrigé")
        else:
            print("  ✅ is_active OK")
        
        # Vérifier is_verified
        is_verified = user_doc.get('is_verified')
        print(f"is_verified: {is_verified}")
        if not is_verified:
            issues_found.append("is_verified n'est pas True")
            print("  ⚠️ PROBLÈME: is_verified devrait être True")
            
            # Correction
            print("  🔧 Correction de is_verified...")
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"is_verified": True}}
            )
            fixes_applied.append("is_verified corrigé en True")
            print("  ✅ is_verified corrigé")
        else:
            print("  ✅ is_verified OK")
        
        # Étape 3: Vérifier le mot de passe
        print(f"\n{'='*60}")
        print("🔐 VÉRIFICATION DU MOT DE PASSE")
        print(f"{'='*60}\n")
        
        has_password_hash = 'password_hash' in user_doc
        has_hashed_password = 'hashed_password' in user_doc
        
        print(f"Champ 'password_hash' existe: {has_password_hash}")
        print(f"Champ 'hashed_password' existe: {has_hashed_password}")
        
        password_field = None
        if has_password_hash:
            password_field = 'password_hash'
            print(f"✅ Utilisation du champ 'password_hash'")
        elif has_hashed_password:
            password_field = 'hashed_password'
            print(f"⚠️ Le code API attend 'password_hash' mais trouve 'hashed_password'")
            issues_found.append("Nom de champ incorrect: 'hashed_password' au lieu de 'password_hash'")
            
            # Correction: renommer le champ
            print("  🔧 Renommage du champ...")
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {
                    "$rename": {"hashed_password": "password_hash"},
                    "$unset": {"hashed_password": ""}
                }
            )
            fixes_applied.append("Champ renommé de 'hashed_password' à 'password_hash'")
            print("  ✅ Champ renommé")
            password_field = 'password_hash'
            
            # Recharger l'utilisateur
            user_doc = await db.users.find_one({"_id": user_doc["_id"]})
        else:
            print("❌ ERREUR CRITIQUE: Aucun champ de mot de passe trouvé!")
            print("  🔧 Génération d'un nouveau hash...")
            
            # Générer un nouveau hash
            new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"password_hash": new_hash}}
            )
            fixes_applied.append("Nouveau hash de mot de passe généré")
            print("  ✅ Nouveau hash créé")
            
            # Recharger l'utilisateur
            user_doc = await db.users.find_one({"_id": user_doc["_id"]})
            password_field = 'password_hash'
        
        # Vérifier le mot de passe
        print(f"\n🧪 Test de vérification du mot de passe...")
        stored_hash = user_doc[password_field]
        print(f"Hash stocké (préfixe): {stored_hash[:10]}...")
        print(f"Longueur du hash: {len(stored_hash)}")
        
        try:
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                stored_hash.encode('utf-8')
            )
            
            if password_valid:
                print(f"✅ Mot de passe valide!")
            else:
                print(f"❌ Mot de passe INVALIDE!")
                issues_found.append("Le hash du mot de passe ne correspond pas")
                
                # Régénérer le hash
                print("  🔧 Régénération du hash...")
                new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                await db.users.update_one(
                    {"_id": user_doc["_id"]},
                    {"$set": {"password_hash": new_hash}}
                )
                fixes_applied.append("Hash de mot de passe régénéré")
                print("  ✅ Hash régénéré")
                
                # Recharger et revérifier
                user_doc = await db.users.find_one({"_id": user_doc["_id"]})
                stored_hash = user_doc['password_hash']
                password_valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    stored_hash.encode('utf-8')
                )
                print(f"  ✅ Vérification après correction: {password_valid}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la vérification: {e}")
            issues_found.append(f"Erreur de vérification: {str(e)}")
        
        # Recharger le document final
        user_doc = await db.users.find_one({"_id": user_doc["_id"]})
        
        # Résumé
        print(f"\n{'='*60}")
        print("📊 RÉSUMÉ")
        print(f"{'='*60}\n")
        
        if issues_found:
            print(f"⚠️ Problèmes détectés: {len(issues_found)}")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("✅ Aucun problème détecté")
        
        if fixes_applied:
            print(f"\n🔧 Corrections appliquées: {len(fixes_applied)}")
            for fix in fixes_applied:
                print(f"  - {fix}")
        
        print(f"\n{'='*60}")
        print("📄 DOCUMENT UTILISATEUR FINAL")
        print(f"{'='*60}\n")
        
        # Afficher le document sans _id
        user_display = {k: v for k, v in user_doc.items() if k != '_id'}
        print(json.dumps(user_display, indent=2, default=str))
        
        print(f"\n{'='*60}")
        print("🎯 CONCLUSION")
        print(f"{'='*60}\n")
        
        if not issues_found or fixes_applied:
            print("✅ La connexion devrait maintenant fonctionner!")
            print("\n📝 Prochaines étapes:")
            print("1. Testez la connexion avec curl:")
            print(f"   curl -X POST http://jlc-api:8001/auth-api/auth/local/login \\")
            print(f"     -H 'Content-Type: application/json' \\")
            print(f"     -d '{{\"username\": \"{username}\", \"password\": \"{password}\"}}'")
        else:
            print("⚠️ Des problèmes persistent. Vérifiez les logs de l'API.")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(diagnose_and_fix())
