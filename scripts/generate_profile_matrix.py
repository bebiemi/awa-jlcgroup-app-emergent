#!/usr/bin/env python3
"""
Génère la matrice complète des permissions par profil
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
from collections import defaultdict

async def generate_profile_permissions_matrix():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    print("=" * 80)
    print("GÉNÉRATION DE LA MATRICE DES PERMISSIONS PAR PROFIL")
    print("=" * 80)
    print()
    
    # Charger toutes les permissions
    all_permissions = await db.permissions.find({}, {"_id": 0}).to_list(1000)
    perms_dict = {p['code']: p for p in all_permissions}
    print(f"✅ Loaded {len(perms_dict)} permissions")
    
    # Charger tous les bundles
    bundles = await db.permission_bundles.find({}, {"_id": 0}).to_list(100)
    bundles_dict = {b.get('code', b.get('id')): b for b in bundles if b.get('code') or b.get('id')}
    print(f"✅ Loaded {len(bundles_dict)} bundles")
    
    # Charger tous les profils
    profiles = await db.profiles.find({}, {"_id": 0}).sort("priority", -1).to_list(100)
    print(f"✅ Loaded {len(profiles)} profiles\n")
    
    # Générer le rapport Markdown
    report = []
    report.append("# 📋 Matrice des Permissions par Profil\n\n")
    report.append(f"**Total profils:** {len(profiles)}\n")
    report.append(f"**Total permissions disponibles:** {len(perms_dict)}\n\n")
    
    # Table des matières
    report.append("## 📑 Table des Matières\n\n")
    for i, profile in enumerate(profiles, 1):
        safe_code = profile.get('code', 'unknown').replace('.', '-').replace('_', '-')
        report.append(f"{i}. [{profile.get('name', 'Sans nom')} ({profile.get('code', 'N/A')})](#profil-{i}-{safe_code})\n")
    report.append("\n---\n\n")
    
    # Détail de chaque profil
    for i, profile in enumerate(profiles, 1):
        code = profile.get('code', 'unknown')
        name = profile.get('name', 'Sans nom')
        description = profile.get('description', 'Aucune description')
        
        safe_code = code.replace('.', '-').replace('_', '-')
        report.append(f"## Profil {i}: {name}\n\n")
        report.append(f"**Code:** `{code}`\n\n")
        report.append(f"**Description:** {description}\n\n")
        report.append(f"**Priorité:** {profile.get('priority', 'N/A')}\n\n")
        
        # Calculer les permissions
        direct_perms = set()
        bundle_perms = set()
        
        # Permissions directes
        perms_list = profile.get('permissions', [])
        if perms_list == "*":
            direct_perms = set(perms_dict.keys())
            report.append(f"**Permissions directes:** ⭐ TOUTES (Wildcard - {len(direct_perms)} permissions)\n\n")
        elif isinstance(perms_list, list) and perms_list:
            direct_perms = set(perms_list)
            report.append(f"**Permissions directes:** {len(direct_perms)}\n\n")
        else:
            report.append(f"**Permissions directes:** 0\n\n")
        
        # Permissions des bundles
        bundles_list = profile.get('bundles', []) or []
        if bundles_list:
            report.append(f"**Bundles assignés:** {len(bundles_list)}\n\n")
            report.append("### 📦 Détail des Bundles\n\n")
            
            for bundle_code in bundles_list:
                if bundle_code in bundles_dict:
                    bundle = bundles_dict[bundle_code]
                    bundle_name = bundle.get('name', bundle_code)
                    bundle_perms_list = bundle.get('permissions', [])
                    bundle_perms.update(bundle_perms_list)
                    
                    report.append(f"#### Bundle: {bundle_name}\n")
                    report.append(f"**Code:** `{bundle_code}`\n\n")
                    report.append(f"**Permissions:** {len(bundle_perms_list)}\n\n")
                    
                    # Grouper par catégorie
                    by_category = defaultdict(list)
                    for perm_code in bundle_perms_list:
                        if perm_code in perms_dict:
                            cat = perms_dict[perm_code].get('category', 'other')
                            by_category[cat].append(perm_code)
                    
                    for cat, codes in sorted(by_category.items()):
                        report.append(f"- **{cat}:** {', '.join([f'`{c}`' for c in sorted(codes)])}\n")
                    report.append("\n")
        
        # Total des permissions effectives
        total_perms = direct_perms | bundle_perms
        report.append(f"### ✅ Total Permissions Effectives: {len(total_perms)}\n\n")
        
        if total_perms:
            # Grouper les permissions par catégorie
            by_category = defaultdict(list)
            for perm_code in sorted(total_perms):
                if perm_code in perms_dict:
                    perm = perms_dict[perm_code]
                    cat = perm.get('category', 'other')
                    by_category[cat].append(perm)
            
            report.append("### 📊 Permissions par Catégorie\n\n")
            for cat, perms in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
                report.append(f"#### {cat.upper()} ({len(perms)} permissions)\n\n")
                report.append("| Code | Nom | Scope | Description |\n")
                report.append("|------|-----|-------|-------------|\n")
                
                for perm in perms[:30]:  # Limiter pour lisibilité
                    scope = perm.get('scope', 'N/A')
                    desc = (perm.get('description') or perm.get('name', ''))[:60]
                    report.append(f"| `{perm['code']}` | {perm.get('name', '')} | {scope} | {desc} |\n")
                
                if len(perms) > 30:
                    report.append(f"\n*... et {len(perms) - 30} autres permissions*\n")
                report.append("\n")
        
        report.append("---\n\n")
    
    # Matrice comparative
    report.append("## 📈 Matrice Comparative des Profils\n\n")
    report.append("| Profil | Code | Permissions Directes | Bundles | Total Effectif |\n")
    report.append("|--------|------|---------------------|---------|----------------|\n")
    
    for profile in profiles:
        perms_list = profile.get('permissions', [])
        direct_count = len(perms_dict) if perms_list == "*" else len(perms_list or [])
        bundles_list = profile.get('bundles', []) or []
        bundles_count = len(bundles_list)
        
        # Calculer total effectif
        direct_perms = set(perms_dict.keys()) if perms_list == "*" else set(perms_list or [])
        bundle_perms = set()
        for bundle_code in bundles_list:
            if bundle_code in bundles_dict:
                bundle_perms.update(bundles_dict[bundle_code].get('permissions', []))
        
        total = len(direct_perms | bundle_perms)
        
        report.append(f"| {profile.get('name', 'N/A')} | `{profile.get('code', 'N/A')}` | {direct_count} | {bundles_count} | **{total}** |\n")
    
    report.append("\n")
    
    # Sauvegarder
    report_path = '/app/docs/IAM_PROFILE_PERMISSIONS_MATRIX.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print(f"✅ Rapport Markdown généré: {report_path}")
    
    # Générer aussi un JSON
    json_data = []
    for profile in profiles:
        perms_list = profile.get('permissions', [])
        direct_perms = list(perms_dict.keys()) if perms_list == "*" else (perms_list or [])
        
        bundle_perms = []
        bundles_list = profile.get('bundles', []) or []
        for bundle_code in bundles_list:
            if bundle_code in bundles_dict:
                bundle_perms.extend(bundles_dict[bundle_code].get('permissions', []))
        
        json_data.append({
            'code': profile.get('code'),
            'name': profile.get('name'),
            'description': profile.get('description', ''),
            'priority': profile.get('priority'),
            'direct_permissions': direct_perms,
            'bundles': bundles_list,
            'bundle_permissions': list(set(bundle_perms)),
            'total_effective_permissions': list(set(direct_perms) | set(bundle_perms))
        })
    
    json_path = '/app/docs/IAM_PROFILE_PERMISSIONS_MATRIX.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✅ JSON généré: {json_path}")
    print(f"\n{'=' * 80}")
    print(f"✅ TERMINÉ - {len(profiles)} profils analysés")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    asyncio.run(generate_profile_permissions_matrix())
