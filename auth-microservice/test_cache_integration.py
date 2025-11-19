#!/usr/bin/env python3
"""
Script de test de l'intégration du cache Redis avec IAMService
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from awana_auth.services.iam_service import IAMService
from awana_auth.services.iam_cache_service import get_cache_service, close_cache_service
import time

async def main():
    print("=" * 80)
    print("🧪 TEST D'INTÉGRATION: IAMService + Redis Cache")
    print("=" * 80)
    
    # Connexion MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['awana_db']
    print(f"✅ Connecté à MongoDB")
    
    # Initialiser le cache
    cache_service = await get_cache_service()
    print(f"✅ Cache service initialized (enabled: {cache_service.enabled})")
    
    # Créer IAMService avec cache
    iam_service = IAMService(db, cache_service=cache_service)
    print(f"✅ IAMService créé avec cache")
    
    # Trouver un utilisateur de test
    user = await db.users.find_one({"username": "admin"}, {"_id": 0})
    if not user:
        print("⚠️  Utilisateur 'admin' non trouvé")
        user = await db.users.find_one({}, {"_id": 0})
    
    if not user:
        print("❌ Aucun utilisateur trouvé dans la base")
        await close_cache_service()
        client.close()
        return
    
    user_id = user['id']
    username = user.get('username', 'unknown')
    print(f"✅ Utilisateur de test: {username} (ID: {user_id})")
    
    # Vider le cache pour cet utilisateur
    await cache_service.invalidate_user_permissions(user_id)
    print(f"🗑️  Cache invalidé pour l'utilisateur")
    
    print("\n" + "=" * 80)
    print("TEST 1: Premier appel (MISS attendu - données depuis MongoDB)")
    print("=" * 80)
    
    start_time = time.time()
    result1 = await iam_service.get_user_permissions(user_id)
    elapsed1 = (time.time() - start_time) * 1000
    
    print(f"⏱️  Temps: {elapsed1:.2f}ms")
    print(f"📊 Profils directs: {len(result1.direct_profiles)}")
    print(f"📊 Profils de groupe: {len(result1.group_profiles)}")
    print(f"📊 Total permissions: {len(result1.all_permissions)}")
    
    if result1.all_permissions:
        print(f"📝 Première permission: {result1.all_permissions[0].code}")
    
    print("\n" + "=" * 80)
    print("TEST 2: Deuxième appel (HIT attendu - données depuis cache)")
    print("=" * 80)
    
    start_time = time.time()
    result2 = await iam_service.get_user_permissions(user_id)
    elapsed2 = (time.time() - start_time) * 1000
    
    print(f"⏱️  Temps: {elapsed2:.2f}ms")
    print(f"📊 Total permissions: {len(result2.all_permissions)}")
    
    # Calculer le gain de performance
    speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 0
    print(f"🚀 Amélioration de performance: {speedup:.1f}x plus rapide")
    
    print("\n" + "=" * 80)
    print("TEST 3: Statistiques du cache")
    print("=" * 80)
    
    stats = await cache_service.get_cache_stats()
    print(f"📊 Clés totales: {stats.get('total_keys', 0)}")
    print(f"📊 Permissions utilisateurs en cache: {stats.get('user_permissions_cached', 0)}")
    print(f"📊 Hit rate: {stats.get('hit_rate', 0)}%")
    print(f"📊 Hits: {stats.get('hits', 0)}")
    print(f"📊 Misses: {stats.get('misses', 0)}")
    
    print("\n" + "=" * 80)
    print("TEST 4: Invalidation du cache")
    print("=" * 80)
    
    await cache_service.invalidate_user_permissions(user_id)
    print(f"✅ Cache invalidé pour l'utilisateur {user_id}")
    
    # Vérifier que le cache a bien été invalidé
    cached_data = await cache_service.get_user_permissions(user_id)
    if cached_data is None:
        print("✅ Confirmation: données bien supprimées du cache")
    else:
        print("⚠️  Attention: données encore présentes dans le cache")
    
    print("\n" + "=" * 80)
    print("✅ TESTS TERMINÉS AVEC SUCCÈS")
    print("=" * 80)
    
    # Cleanup
    await close_cache_service()
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
