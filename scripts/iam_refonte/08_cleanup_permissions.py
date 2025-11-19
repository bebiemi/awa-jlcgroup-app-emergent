"""
Script 8: Nettoyage des Permissions IAM
- Phase 1: Suppression des permissions non utilisées (9)
- Phase 2: Migration des permissions legacy vers format moderne (18)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
from datetime import datetime


# Mapping des permissions legacy vers format moderne
LEGACY_TO_MODERN_MAPPING = {
    # Utilisateurs
    "gestion_utilisateurs": {
        "code": "users.manage",
        "name": "Gérer les utilisateurs",
        "description": "Gérer tous les aspects des utilisateurs",
        "resource": "users",
        "action": "manage",
        "scope": "organization",
        "category": "users"
    },
    "voir_utilisateurs": {
        "code": "users.view",
        "name": "Voir les utilisateurs",
        "description": "Consulter la liste des utilisateurs",
        "resource": "users",
        "action": "view",
        "scope": "organization",
        "category": "users"
    },
    
    # Groupes
    "gestion_groupes": {
        "code": "groups.manage",
        "name": "Gérer les groupes",
        "description": "Gérer tous les aspects des groupes",
        "resource": "groups",
        "action": "manage",
        "scope": "organization",
        "category": "groups"
    },
    
    # Profils
    "gestion_profils": {
        "code": "profiles.manage",
        "name": "Gérer les profils",
        "description": "Gérer tous les aspects des profils",
        "resource": "profiles",
        "action": "manage",
        "scope": "organization",
        "category": "iam"
    },
    
    # Validations
    "voir_validations": {
        "code": "validations.view",
        "name": "Voir les validations",
        "description": "Consulter les demandes de validation",
        "resource": "validations",
        "action": "view",
        "scope": "organization",
        "category": "validations"
    },
    "approuver_validations": {
        "code": "validations.approve",
        "name": "Approuver les validations",
        "description": "Approuver les demandes de validation",
        "resource": "validations",
        "action": "approve",
        "scope": "organization",
        "category": "validations"
    },
    "rejeter_validations": {
        "code": "validations.reject",
        "name": "Rejeter les validations",
        "description": "Rejeter les demandes de validation",
        "resource": "validations",
        "action": "reject",
        "scope": "organization",
        "category": "validations"
    },
    
    # Intérimaires
    "voir_interimaires": {
        "code": "candidates.view",
        "name": "Voir les intérimaires",
        "description": "Consulter la liste des intérimaires",
        "resource": "candidates",
        "action": "view",
        "scope": "organization",
        "category": "users"
    },
    "modifier_interimaires": {
        "code": "candidates.update",
        "name": "Modifier les intérimaires",
        "description": "Modifier les profils des intérimaires",
        "resource": "candidates",
        "action": "update",
        "scope": "organization",
        "category": "users"
    },
    "supprimer_interimaires": {
        "code": "candidates.delete",
        "name": "Supprimer les intérimaires",
        "description": "Supprimer des profils d'intérimaires",
        "resource": "candidates",
        "action": "delete",
        "scope": "organization",
        "category": "users"
    },
    
    # Rapports
    "voir_rapports": {
        "code": "reports.view",
        "name": "Voir les rapports",
        "description": "Consulter les rapports",
        "resource": "reports",
        "action": "view",
        "scope": "organization",
        "category": "reports"
    },
    "exporter_rapports": {
        "code": "reports.export",
        "name": "Exporter les rapports",
        "description": "Exporter les rapports",
        "resource": "reports",
        "action": "export",
        "scope": "organization",
        "category": "reports"
    },
    
    # Dashboard
    "voir_dashboard": {
        "code": "dashboard.view",
        "name": "Voir le dashboard",
        "description": "Accéder au tableau de bord",
        "resource": "dashboard",
        "action": "view",
        "scope": "organization",
        "category": "dashboard"
    },
    "voir_statistiques": {
        "code": "statistics.view",
        "name": "Voir les statistiques",
        "description": "Consulter les statistiques",
        "resource": "statistics",
        "action": "view",
        "scope": "organization",
        "category": "dashboard"
    },
    
    # Missions
    "voir_missions": {
        "code": "missions.view",
        "name": "Voir les missions",
        "description": "Consulter les missions",
        "resource": "missions",
        "action": "view",
        "scope": "organization",
        "category": "missions"
    },
    "modifier_missions": {
        "code": "missions.update",
        "name": "Modifier les missions",
        "description": "Modifier les missions",
        "resource": "missions",
        "action": "update",
        "scope": "organization",
        "category": "missions"
    },
    "supprimer_missions": {
        "code": "missions.delete",
        "name": "Supprimer les missions",
        "description": "Supprimer des missions",
        "resource": "missions",
        "action": "delete",
        "scope": "organization",
        "category": "missions"
    },
    "creer_missions": {
        "code": "missions.create",
        "name": "Créer des missions",
        "description": "Créer de nouvelles missions",
        "resource": "missions",
        "action": "create",
        "scope": "organization",
        "category": "missions"
    }
}


async def phase_1_remove_unused():
    """Phase 1: Supprimer les 9 permissions non utilisées"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("🗑️  PHASE 1: SUPPRESSION DES PERMISSIONS NON UTILISÉES")
    print("=" * 80)
    
    # Permissions à supprimer (confirmées comme non utilisées)
    to_delete = [
        "applications.edit_all",
        "applications.reject",
        "applications.validate",
        "supprimer_entreprises",
        "voir_entreprises",
        "modifier_entreprises",
        "documents.read_own",
        "missions.reject",
        "missions.validate"
    ]
    
    print(f"\n📋 Permissions à supprimer: {len(to_delete)}")
    for code in to_delete:
        print(f"   • {code}")
    
    # Vérifier une dernière fois qu'elles ne sont pas utilisées
    profiles = await db.profiles.find({}, {"_id": 0, "code": 1, "permission_ids": 1}).to_list(1000)
    bundles = await db.capability_bundles.find({}, {"_id": 0, "code": 1, "permission_ids": 1}).to_list(1000)
    
    all_perms = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    perms_by_code = {p['code']: p for p in all_perms}
    
    # Créer un mapping ID -> code
    id_to_code = {p['id']: p['code'] for p in all_perms}
    
    # Vérifier l'utilisation
    used_ids = set()
    for profile in profiles:
        used_ids.update(profile.get('permission_ids', []))
    for bundle in bundles:
        used_ids.update(bundle.get('permission_ids', []))
    
    used_codes = {id_to_code.get(id) for id in used_ids if id in id_to_code}
    
    # Sécurité: ne supprimer que si vraiment non utilisé
    safe_to_delete = []
    for code in to_delete:
        if code not in used_codes:
            safe_to_delete.append(code)
        else:
            print(f"⚠️  ATTENTION: {code} est utilisée, on ne supprime PAS")
    
    print(f"\n✅ Permissions confirmées pour suppression: {len(safe_to_delete)}")
    
    # Supprimer
    deleted_count = 0
    for code in safe_to_delete:
        result = await db.permissions.delete_one({"code": code})
        if result.deleted_count > 0:
            deleted_count += 1
            print(f"   ✓ Supprimée: {code}")
    
    print(f"\n✅ Phase 1 terminée: {deleted_count} permissions supprimées")
    
    client.close()
    return deleted_count


async def phase_2_migrate_legacy():
    """Phase 2: Migrer les permissions legacy vers format moderne"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🔄 PHASE 2: MIGRATION LEGACY → MODERNE")
    print("=" * 80)
    
    # Charger toutes les permissions
    all_perms = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    perms_by_code = {p['code']: p for p in all_perms}
    
    # Charger profils et bundles
    profiles = await db.profiles.find({}, {"_id": 0}).to_list(1000)
    bundles = await db.capability_bundles.find({}, {"_id": 0}).to_list(1000)
    
    print(f"\n📊 Permissions legacy trouvées: {len(LEGACY_TO_MODERN_MAPPING)}")
    
    migration_report = {
        "migrated": [],
        "skipped": [],
        "errors": []
    }
    
    for legacy_code, modern_def in LEGACY_TO_MODERN_MAPPING.items():
        # Vérifier que la permission legacy existe
        if legacy_code not in perms_by_code:
            print(f"⏭️  Ignoré (n'existe pas): {legacy_code}")
            migration_report["skipped"].append({"code": legacy_code, "reason": "not_found"})
            continue
        
        legacy_perm = perms_by_code[legacy_code]
        legacy_id = legacy_perm['id']
        modern_code = modern_def['code']
        
        # Vérifier si la permission moderne existe déjà
        if modern_code in perms_by_code:
            print(f"⚠️  {legacy_code} → {modern_code} existe déjà, fusion nécessaire")
            modern_perm = perms_by_code[modern_code]
            modern_id = modern_perm['id']
            
            # Remplacer l'ancien ID par le nouveau dans tous les profils et bundles
            for profile in profiles:
                perm_ids = profile.get('permission_ids', [])
                if legacy_id in perm_ids:
                    perm_ids.remove(legacy_id)
                    if modern_id not in perm_ids:
                        perm_ids.append(modern_id)
                    await db.profiles.update_one(
                        {"code": profile['code']},
                        {"$set": {"permission_ids": perm_ids}}
                    )
                    print(f"   ✓ Profil '{profile['code']}' mis à jour")
            
            for bundle in bundles:
                perm_ids = bundle.get('permission_ids', [])
                if legacy_id in perm_ids:
                    perm_ids.remove(legacy_id)
                    if modern_id not in perm_ids:
                        perm_ids.append(modern_id)
                    await db.capability_bundles.update_one(
                        {"code": bundle['code']},
                        {"$set": {"permission_ids": perm_ids}}
                    )
                    print(f"   ✓ Bundle '{bundle['code']}' mis à jour")
            
            # Supprimer l'ancienne permission
            await db.permissions.delete_one({"code": legacy_code})
            print(f"   ✓ Permission legacy '{legacy_code}' supprimée")
            
            migration_report["migrated"].append({
                "from": legacy_code,
                "to": modern_code,
                "action": "merged"
            })
        
        else:
            # Créer la nouvelle permission moderne
            modern_perm = {
                "id": f"perm_{modern_code.replace('.', '_')}",
                **modern_def
            }
            await db.permissions.insert_one(modern_perm)
            print(f"✅ Créée: {modern_code}")
            
            # Remplacer l'ancien ID par le nouveau dans tous les profils et bundles
            modern_id = modern_perm['id']
            
            for profile in profiles:
                perm_ids = profile.get('permission_ids', [])
                if legacy_id in perm_ids:
                    perm_ids.remove(legacy_id)
                    perm_ids.append(modern_id)
                    await db.profiles.update_one(
                        {"code": profile['code']},
                        {"$set": {"permission_ids": perm_ids}}
                    )
                    print(f"   ✓ Profil '{profile['code']}' migré")
            
            for bundle in bundles:
                perm_ids = bundle.get('permission_ids', [])
                if legacy_id in perm_ids:
                    perm_ids.remove(legacy_id)
                    perm_ids.append(modern_id)
                    await db.capability_bundles.update_one(
                        {"code": bundle['code']},
                        {"$set": {"permission_ids": perm_ids}}
                    )
                    print(f"   ✓ Bundle '{bundle['code']}' migré")
            
            # Supprimer l'ancienne permission
            await db.permissions.delete_one({"code": legacy_code})
            print(f"   ✓ Permission legacy '{legacy_code}' supprimée")
            
            migration_report["migrated"].append({
                "from": legacy_code,
                "to": modern_code,
                "action": "created"
            })
    
    # Sauvegarder le rapport
    report_path = '/app/scripts/iam_refonte/migration_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(migration_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Phase 2 terminée:")
    print(f"   • Migrations réussies: {len(migration_report['migrated'])}")
    print(f"   • Ignorées: {len(migration_report['skipped'])}")
    print(f"   • Erreurs: {len(migration_report['errors'])}")
    print(f"\n📄 Rapport: {report_path}")
    
    client.close()
    return migration_report


async def verify_cleanup():
    """Vérifier que le nettoyage est correct"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION POST-NETTOYAGE")
    print("=" * 80)
    
    # Compter les permissions
    all_perms = await db.permissions.find({}, {"_id": 0}).to_list(10000)
    
    # Vérifier le format
    modern_count = 0
    legacy_count = 0
    
    for perm in all_perms:
        code = perm.get('code', '')
        has_resource = bool(perm.get('resource'))
        has_action = bool(perm.get('action'))
        
        if '.' in code and has_resource and has_action:
            modern_count += 1
        else:
            legacy_count += 1
            print(f"   ⚠️  Legacy restant: {code}")
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   • Total permissions: {len(all_perms)}")
    print(f"   • Format moderne: {modern_count}")
    print(f"   • Format legacy restant: {legacy_count}")
    
    # Vérifier l'intégrité des références
    profiles = await db.profiles.find({}, {"_id": 0}).to_list(1000)
    bundles = await db.capability_bundles.find({}, {"_id": 0}).to_list(1000)
    
    perm_ids = {p['id'] for p in all_perms}
    
    orphan_refs = []
    for profile in profiles:
        for perm_id in profile.get('permission_ids', []):
            if perm_id not in perm_ids:
                orphan_refs.append(f"Profil '{profile['code']}' → {perm_id}")
    
    for bundle in bundles:
        for perm_id in bundle.get('permission_ids', []):
            if perm_id not in perm_ids:
                orphan_refs.append(f"Bundle '{bundle['code']}' → {perm_id}")
    
    if orphan_refs:
        print(f"\n⚠️  RÉFÉRENCES ORPHELINES TROUVÉES: {len(orphan_refs)}")
        for ref in orphan_refs[:10]:
            print(f"   • {ref}")
    else:
        print(f"\n✅ Aucune référence orpheline trouvée")
    
    client.close()
    return {
        "total": len(all_perms),
        "modern": modern_count,
        "legacy": legacy_count,
        "orphan_refs": len(orphan_refs)
    }


async def main():
    print("🚀 DÉMARRAGE DU NETTOYAGE IAM COMPLET\n")
    
    try:
        # Phase 1: Supprimer les permissions non utilisées
        deleted = await phase_1_remove_unused()
        
        # Phase 2: Migrer les permissions legacy
        migration = await phase_2_migrate_legacy()
        
        # Vérification finale
        verification = await verify_cleanup()
        
        print("\n" + "=" * 80)
        print("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS")
        print("=" * 80)
        print(f"\n📊 RÉSUMÉ:")
        print(f"   • Permissions supprimées: {deleted}")
        print(f"   • Permissions migrées: {len(migration['migrated'])}")
        print(f"   • Total permissions restantes: {verification['total']}")
        print(f"   • Format moderne: {verification['modern']}")
        print(f"   • Format legacy restant: {verification['legacy']}")
        
        if verification['legacy'] > 0:
            print(f"\n⚠️  Il reste {verification['legacy']} permissions legacy")
            print(f"    Ces permissions nécessitent une migration manuelle")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
