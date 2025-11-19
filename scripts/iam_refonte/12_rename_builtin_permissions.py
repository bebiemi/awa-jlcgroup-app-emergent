"""
Script 12: Renommage des permissions builtin
Convertit les noms de format 'resource:action' vers des noms descriptifs en français
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


# Mapping des anciens noms vers les nouveaux (descriptifs en français)
BUILTIN_RENAME_MAPPING = {
    # Format ancien 'resource:action' → Format descriptif français
    "users:read": "Consulter les utilisateurs",
    "users:write": "Modifier les utilisateurs", 
    "users:delete": "Supprimer les utilisateurs",
    "roles:read": "Consulter les rôles",
    "roles:write": "Modifier les rôles",
    "roles:delete": "Supprimer les rôles",
    "content:read": "Consulter le contenu",
    "content:write": "Modifier le contenu",
    "content:delete": "Supprimer le contenu",
    "analytics:read": "Consulter les analyses",
    "audit:read": "Consulter les journaux d'audit",
    "*:*": "Accès super administrateur",
    
    # Permissions avec noms anglais → Français
    "Dashboard View Readonly": "Consulter le tableau de bord",
    "Profile View Own": "Consulter son profil",
    "Missions View Published": "Consulter les missions publiées",
    "Missions Search Public": "Rechercher des missions",
    "Profile Edit Own": "Modifier son profil",
    "Profile Manage Own": "Gérer son profil",
    "Security Edit Own": "Modifier sa sécurité",
    "Dashboard Customize Own": "Personnaliser son tableau de bord",
    "Documents Upload Own": "Télécharger ses documents",
    "Documents View Own": "Consulter ses documents",
    "Documents Delete Own": "Supprimer ses documents",
    "Documents Download Own": "Télécharger ses documents",
    "Documents Manage Own": "Gérer ses documents",
    "Missions Apply": "Postuler à des missions",
    "Applications Create Own": "Créer ses candidatures",
    "Applications View Own": "Consulter ses candidatures",
    "Applications Track Own": "Suivre ses candidatures",
    "Applications Withdraw Own": "Retirer ses candidatures",
    "Applications View Details": "Voir les détails de candidature",
    "Notifications View Own": "Consulter ses notifications",
    "Notifications Mark Read": "Marquer les notifications lues",
    "Notifications Manage Own": "Gérer ses notifications",
    "Profile Update Own": "Mettre à jour son profil",
    "Profile Update Personal": "Mettre à jour ses informations personnelles",
    "Profile Update Professional": "Mettre à jour ses informations professionnelles",
    "Documents View Personal": "Consulter ses documents personnels",
    "Applications Resubmit Own": "Resoumettre ses candidatures",
    "Contracts View Own": "Consulter ses contrats",
    "Contracts Sign Own": "Signer ses contrats",
    "Contracts Download Own": "Télécharger ses contrats",
    "Messages View Own": "Consulter ses messages",
    "Messages Send": "Envoyer des messages",
    "Messages Reply": "Répondre aux messages",
    "Messages Delete Own": "Supprimer ses messages",
}


async def rename_builtin_permissions():
    """Renommer les permissions builtin"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("📝 RENOMMAGE DES PERMISSIONS BUILTIN")
    print("=" * 80)
    
    # Récupérer toutes les permissions builtin
    builtin_perms = await db.permissions.find(
        {"category": "builtin"}, 
        {"_id": 0}
    ).to_list(1000)
    
    print(f"\n📊 Permissions builtin trouvées: {len(builtin_perms)}")
    
    renamed_count = 0
    unchanged_count = 0
    
    for perm in builtin_perms:
        old_name = perm.get('name', '')
        code = perm.get('code', '')
        perm_id = perm.get('id')
        
        # Vérifier si on a un nouveau nom pour cette permission
        if old_name in BUILTIN_RENAME_MAPPING:
            new_name = BUILTIN_RENAME_MAPPING[old_name]
            
            # Mettre à jour la permission
            result = await db.permissions.update_one(
                {"id": perm_id},
                {"$set": {"name": new_name}}
            )
            
            if result.modified_count > 0:
                renamed_count += 1
                print(f"✅ {code}")
                print(f"   Ancien: {old_name}")
                print(f"   Nouveau: {new_name}")
                print()
        else:
            unchanged_count += 1
    
    print("\n" + "=" * 80)
    print("✅ RENOMMAGE TERMINÉ")
    print("=" * 80)
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Permissions renommées: {renamed_count}")
    print(f"   • Permissions inchangées: {unchanged_count}")
    print(f"   • Total: {len(builtin_perms)}")
    
    # Afficher les permissions inchangées qui pourraient nécessiter un renommage
    print(f"\n📋 PERMISSIONS INCHANGÉES (pour vérification):")
    unchanged_perms = []
    for perm in builtin_perms:
        old_name = perm.get('name', '')
        code = perm.get('code', '')
        if old_name not in BUILTIN_RENAME_MAPPING:
            # Vérifier si c'est déjà en français
            if not any(word in old_name for word in ['Consulter', 'Modifier', 'Supprimer', 'Gérer', 'Créer', 'Envoyer']):
                unchanged_perms.append((code, old_name))
    
    for code, name in unchanged_perms[:15]:
        print(f"   • {code:<40} → {name}")
    
    if len(unchanged_perms) > 15:
        print(f"   ... et {len(unchanged_perms) - 15} autres")
    
    print(f"\n💡 Total permissions nécessitant potentiellement un renommage manuel: {len(unchanged_perms)}")
    
    client.close()
    
    return {
        "renamed": renamed_count,
        "unchanged": unchanged_count,
        "total": len(builtin_perms),
        "needs_manual_review": len(unchanged_perms)
    }


async def verify_rename():
    """Vérifier que le renommage a bien fonctionné"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION DU RENOMMAGE")
    print("=" * 80)
    
    # Vérifier qu'il n'y a plus de format 'resource:action'
    old_format_perms = await db.permissions.find(
        {
            "category": "builtin",
            "name": {"$regex": "^[a-z]+:[a-z]+$"}
        },
        {"_id": 0, "code": 1, "name": 1}
    ).to_list(100)
    
    if not old_format_perms:
        print(f"\n✅ Aucune permission au format 'resource:action' trouvée")
    else:
        print(f"\n⚠️  {len(old_format_perms)} permission(s) au format 'resource:action' restante(s):")
        for perm in old_format_perms:
            print(f"   • {perm['code']}: {perm['name']}")
    
    # Afficher quelques exemples de permissions renommées
    print(f"\n📋 EXEMPLES DE PERMISSIONS RENOMMÉES:")
    sample_perms = await db.permissions.find(
        {"category": "builtin"},
        {"_id": 0, "code": 1, "name": 1}
    ).limit(10).to_list(10)
    
    for perm in sample_perms:
        print(f"   • {perm['code']:<40} → {perm['name']}")
    
    client.close()


async def main():
    print("🚀 DÉMARRAGE DU RENOMMAGE DES PERMISSIONS BUILTIN\n")
    
    # Renommer les permissions
    result = await rename_builtin_permissions()
    
    # Vérifier le renommage
    await verify_rename()
    
    print("\n" + "=" * 80)
    if result['renamed'] > 0:
        print(f"✅ {result['renamed']} permissions builtin renommées avec succès")
    else:
        print("ℹ️  Aucune permission à renommer")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
