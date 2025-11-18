#!/usr/bin/env python3
"""
Script d'export du système RBAC AWANA
Génère des fichiers JSON complets des permissions, profils, rôles et groupes IAM
"""
import asyncio
import json
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

# Configuration MongoDB
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = 'auth_db'

# Chemins d'export
DOCS_DIR = Path(__file__).parent.parent / 'docs'
EXPORT_FILE = DOCS_DIR / 'awana_rbac_export.json'


async def export_rbac():
    """Export complet du système RBAC"""
    print("🔄 Connexion à MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("📊 Récupération des données RBAC...")
        
        # Récupérer toutes les collections
        permissions = await db.permissions.find({}, {'_id': 0}).to_list(length=None)
        profiles = await db.profiles.find({}, {'_id': 0}).to_list(length=None)
        iam_roles = await db.iam_roles.find({}, {'_id': 0}).to_list(length=None)
        iam_groups = await db.iam_groups.find({}, {'_id': 0}).to_list(length=None)
        
        # Trier les données
        permissions.sort(key=lambda x: x.get('code', ''))
        profiles.sort(key=lambda x: x.get('code', ''))
        iam_roles.sort(key=lambda x: x.get('code', ''))
        iam_groups.sort(key=lambda x: x.get('name', ''))
        
        print(f"  ✓ {len(permissions)} permissions")
        print(f"  ✓ {len(profiles)} profils")
        print(f"  ✓ {len(iam_roles)} rôles IAM")
        print(f"  ✓ {len(iam_groups)} groupes IAM")
        
        # Construire l'export
        rbac_export = {
            "metadata": {
                "application": "AWANA - Plateforme d'intérim au Gabon",
                "version": "1.0",
                "export_date": datetime.now().strftime("%Y-%m-%d"),
                "description": "Système RBAC complet - Permissions, Profils, Rôles IAM",
                "statistics": {
                    "total_permissions": len(permissions),
                    "total_profiles": len(profiles),
                    "total_iam_roles": len(iam_roles),
                    "total_iam_groups": len(iam_groups)
                }
            },
            "permissions": permissions,
            "profiles": profiles,
            "iam_roles": iam_roles,
            "iam_groups": iam_groups
        }
        
        # Créer le répertoire docs si nécessaire
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Écrire le fichier
        print(f"\n💾 Écriture de l'export dans {EXPORT_FILE}...")
        with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(rbac_export, f, indent=2, ensure_ascii=False)
        
        # Afficher les statistiques
        file_size = EXPORT_FILE.stat().st_size / 1024  # En KB
        print(f"✅ Export terminé avec succès!")
        print(f"   Fichier: {EXPORT_FILE}")
        print(f"   Taille: {file_size:.1f} KB")
        
        # Créer aussi un résumé par catégorie
        print("\n📊 Résumé par catégorie:")
        categories = {}
        for perm in permissions:
            cat = perm.get('category', 'uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            bar = '█' * (count // 3)
            print(f"  • {cat:20s} : {count:3d}  {bar}")
        
        # Créer un résumé des profils principaux
        print("\n👥 Profils principaux:")
        key_profiles = ['super_admin', 'interim_user', 'company_admin', 'profile_postulant']
        for profile in profiles:
            if profile.get('code') in key_profiles:
                perm_count = len(profile.get('permission_ids', []))
                print(f"  • {profile.get('name', profile.get('code')):30s} → {perm_count:3d} permissions")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        raise
    finally:
        client.close()


async def export_summary():
    """Export d'un résumé condensé"""
    print("\n🔄 Génération du résumé...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        permissions = await db.permissions.find({}, {'_id': 0, 'code': 1, 'description': 1, 'category': 1}).to_list(length=None)
        
        # Grouper par catégorie
        by_category = {}
        for perm in permissions:
            cat = perm.get('category', 'uncategorized')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                'code': perm.get('code'),
                'description': perm.get('description')
            })
        
        summary = {
            "metadata": {
                "export_date": datetime.now().strftime("%Y-%m-%d"),
                "total_permissions": len(permissions)
            },
            "permissions_by_category": by_category
        }
        
        summary_file = DOCS_DIR / 'awana_rbac_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Résumé créé: {summary_file}")
        
    finally:
        client.close()


def main():
    """Point d'entrée principal"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          AWANA - Export du système RBAC                      ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    # Lancer les exports
    asyncio.run(export_rbac())
    asyncio.run(export_summary())
    
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                  Export terminé avec succès ✅               ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n📁 Fichiers disponibles dans: {DOCS_DIR}/")
    print("   • awana_rbac_export.json")
    print("   • awana_rbac_summary.json")
    print("   • AWANA_RBAC_DOCUMENTATION.md")
    print("   • README_RBAC.md\n")


if __name__ == "__main__":
    main()
