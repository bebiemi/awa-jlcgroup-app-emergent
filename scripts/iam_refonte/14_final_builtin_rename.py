"""
Script 14: Renommage final des 24 dernières permissions builtin
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


# Mapping final pour les 24 permissions restantes
FINAL_RENAME_MAPPING = {
    # Missions
    "Missions Delete Own": "Supprimer ses missions",
    "Missions Manage All": "Gérer toutes les missions",
    "Missions View All": "Consulter toutes les missions",
    "Missions Edit All": "Modifier toutes les missions",
    
    # Applications
    "Applications Validate All": "Valider toutes les candidatures",
    "Applications View All": "Consulter toutes les candidatures",
    
    # Besoins
    "Besoins View All": "Consulter tous les besoins",
    "Besoins Edit All": "Modifier tous les besoins",
    
    # Entreprises
    "Entreprises Edit All": "Modifier toutes les entreprises",
    "Entreprises Archive": "Archiver les entreprises",
    "Entreprises Transfer Validate": "Valider les transferts d'entreprises",
    "Entreprises View All": "Consulter toutes les entreprises",
    
    # Dashboard
    "Dashboard Manage Own": "Gérer son tableau de bord",
    
    # Émargements
    "Emargements View All": "Consulter tous les émargements",
    
    # Payroll & Invoicing
    "Payroll Manage": "Gérer la paie",
    "Invoicing Manage": "Gérer la facturation",
    "Invoicing Create": "Créer des factures",
    "Invoicing Edit": "Modifier les factures",
    
    # Users
    "Users Manage": "Gérer les utilisateurs",
    "Users Edit": "Modifier les utilisateurs",
    
    # Reports
    "Reports View All": "Consulter tous les rapports",
    "Reports Export": "Exporter les rapports",
    
    # System
    "System Config": "Configuration système",
    "Admin Panel Access": "Accès au panneau d'administration",
}


async def final_rename():
    """Renommer les 24 dernières permissions builtin"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("📝 RENOMMAGE FINAL DES PERMISSIONS BUILTIN")
    print("=" * 80)
    
    # Récupérer toutes les permissions builtin encore en anglais
    english_indicators = ['View', 'Edit', 'Create', 'Delete', 'Manage', 'Own', 'All', 'Validate', 
                         'Archive', 'Transfer', 'Payroll', 'Invoicing', 'Users', 'Reports', 
                         'System', 'Config', 'Access', 'Panel', 'Admin']
    
    builtin_perms = await db.permissions.find(
        {"category": "builtin"}, 
        {"_id": 0}
    ).to_list(1000)
    
    english_perms = [p for p in builtin_perms 
                     if any(ind in p.get('name', '') for ind in english_indicators)]
    
    print(f"\n📊 Permissions en anglais trouvées: {len(english_perms)}")
    
    renamed_count = 0
    not_found = []
    
    for perm in english_perms:
        old_name = perm.get('name', '')
        code = perm.get('code', '')
        perm_id = perm.get('id')
        
        if old_name in FINAL_RENAME_MAPPING:
            new_name = FINAL_RENAME_MAPPING[old_name]
            
            result = await db.permissions.update_one(
                {"id": perm_id},
                {"$set": {"name": new_name}}
            )
            
            if result.modified_count > 0:
                renamed_count += 1
                print(f"✅ {code}")
                print(f"   {old_name} → {new_name}")
        else:
            not_found.append((code, old_name))
    
    print("\n" + "=" * 80)
    print("✅ RENOMMAGE FINAL TERMINÉ")
    print("=" * 80)
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Permissions renommées: {renamed_count}")
    print(f"   • Permissions non trouvées: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  PERMISSIONS NON MAPPÉES:")
        for code, name in not_found:
            print(f"   • {code:<50} → {name}")
    
    client.close()
    return renamed_count, not_found


async def generate_final_report():
    """Générer le rapport final complet"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("📊 RAPPORT FINAL COMPLET - PERMISSIONS BUILTIN")
    print("=" * 80)
    
    builtin_perms = await db.permissions.find(
        {"category": "builtin"}, 
        {"_id": 0, "code": 1, "name": 1}
    ).to_list(1000)
    
    # Détecter les permissions encore en anglais
    english_indicators = ['View', 'Edit', 'Create', 'Delete', 'Manage', 'Own', 'All', 
                         'Validate', 'Archive', 'Transfer', 'Read', 'Write', 'Update']
    
    still_english = []
    for perm in builtin_perms:
        name = perm.get('name', '')
        if any(ind in name for ind in english_indicators):
            still_english.append(perm)
    
    french_count = len(builtin_perms) - len(still_english)
    
    print(f"\n📈 STATISTIQUES FINALES:")
    print(f"   • Total permissions builtin: {len(builtin_perms)}")
    print(f"   • Permissions en français: {french_count} ({100*french_count/len(builtin_perms):.1f}%)")
    print(f"   • Permissions encore en anglais: {len(still_english)} ({100*len(still_english)/len(builtin_perms):.1f}%)")
    
    if still_english:
        print(f"\n⚠️  PERMISSIONS ENCORE EN ANGLAIS:")
        for perm in still_english[:10]:
            print(f"   • {perm['code']:<50} → {perm['name']}")
        if len(still_english) > 10:
            print(f"   ... et {len(still_english) - 10} autres")
    else:
        print(f"\n✅ TOUTES LES PERMISSIONS BUILTIN SONT EN FRANÇAIS!")
    
    print(f"\n📋 ÉCHANTILLON DE PERMISSIONS RENOMMÉES (15 premières):")
    for perm in builtin_perms[:15]:
        print(f"   • {perm['code']:<50} → {perm['name']}")
    
    client.close()
    
    return {
        "total": len(builtin_perms),
        "french": french_count,
        "english": len(still_english)
    }


async def main():
    print("🚀 RENOMMAGE FINAL DES PERMISSIONS BUILTIN\n")
    
    renamed, not_found = await final_rename()
    stats = await generate_final_report()
    
    print("\n" + "=" * 80)
    print("✅ PROCESSUS DE RENOMMAGE BUILTIN TERMINÉ")
    print("=" * 80)
    print(f"\n🎯 RÉSULTAT GLOBAL:")
    print(f"   • Total sessions de renommage: 3")
    print(f"   • Total permissions builtin: {stats['total']}")
    print(f"   • Permissions en français: {stats['french']} ({100*stats['french']/stats['total']:.1f}%)")
    print(f"   • Permissions encore en anglais: {stats['english']}")
    
    if stats['english'] == 0:
        print(f"\n🎉 SUCCÈS COMPLET: 100% des permissions builtin sont en français!")
    else:
        print(f"\n⚠️  {stats['english']} permission(s) nécessite(nt) encore un renommage manuel")
    
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
