"""
Script 13: Renommage des permissions builtin restantes (noms anglais → français)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


# Mapping complet pour toutes les permissions en anglais restantes
ADDITIONAL_RENAME_MAPPING = {
    # Applications
    "Applications Read Own": "Lire ses candidatures",
    "Applications Withdraw Own": "Retirer ses candidatures",
    "Applications View Details": "Voir les détails de candidature",
    "Applications Resubmit Own": "Resoumettre ses candidatures",
    
    # Entreprises
    "Entreprises Manage Own": "Gérer son entreprise",
    "Entreprises Edit Own": "Modifier son entreprise",
    "Entreprises View Own": "Consulter son entreprise",
    
    # Besoins
    "Besoins Create Own": "Créer ses besoins",
    "Besoins Edit Own": "Modifier ses besoins",
    "Besoins Submit Own": "Soumettre ses besoins",
    "Besoins Comment Own": "Commenter ses besoins",
    "Besoins View Own": "Consulter ses besoins",
    
    # Émargements
    "Emargements Validate": "Valider les émargements",
    "Emargements Reject": "Rejeter les émargements",
    "Emargements Annotate": "Annoter les émargements",
    "Emargements View Own": "Consulter ses émargements",
    
    # Missions
    "Missions Create Own": "Créer ses missions",
    "Missions Edit Own": "Modifier ses missions",
    "Missions Publish Own": "Publier ses missions",
    "Missions Archive Own": "Archiver ses missions",
    "Missions View Own": "Consulter ses missions",
    "Missions Manage Own": "Gérer ses missions",
    
    # Notifications
    "Notifications View Own": "Consulter ses notifications",
    "Notifications Mark Read": "Marquer les notifications lues",
    "Notifications Manage Own": "Gérer ses notifications",
    
    # Profile
    "Profile Update Own": "Mettre à jour son profil",
    "Profile Update Personal": "Mettre à jour ses informations personnelles",
    "Profile Update Professional": "Mettre à jour ses informations professionnelles",
    
    # Documents
    "Documents View Personal": "Consulter ses documents personnels",
    
    # Contracts
    "Contracts View Own": "Consulter ses contrats",
    "Contracts Sign Own": "Signer ses contrats",
    "Contracts Download Own": "Télécharger ses contrats",
    
    # Messages
    "Messages View Own": "Consulter ses messages",
    "Messages Send": "Envoyer des messages",
    "Messages Reply": "Répondre aux messages",
    "Messages Delete Own": "Supprimer ses messages",
    
    # Autres permissions spécifiques
    "Gérer Profils (Ancien)": "Gérer les profils",
    
    # Permissions avec patterns divers
    "Dashboard Stats View": "Consulter les statistiques du tableau de bord",
    "Reports Generate": "Générer des rapports",
    "Settings View": "Consulter les paramètres",
    "Settings Edit": "Modifier les paramètres",
    "Admin Access": "Accès administrateur",
}


async def rename_remaining_builtin():
    """Renommer toutes les permissions builtin restantes en anglais"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("=" * 80)
    print("📝 RENOMMAGE DES PERMISSIONS BUILTIN RESTANTES")
    print("=" * 80)
    
    # Récupérer toutes les permissions builtin
    builtin_perms = await db.permissions.find(
        {"category": "builtin"}, 
        {"_id": 0}
    ).to_list(1000)
    
    print(f"\n📊 Permissions builtin trouvées: {len(builtin_perms)}")
    
    # Identifier celles qui ne sont pas en français
    english_perms = []
    for perm in builtin_perms:
        name = perm.get('name', '')
        # Vérifier si c'est en anglais (contient des mots anglais courants)
        english_indicators = ['View', 'Edit', 'Create', 'Delete', 'Manage', 'Own', 'Read', 'Write', 
                             'Update', 'Submit', 'Comment', 'Validate', 'Reject', 'Annotate',
                             'Publish', 'Archive', 'Mark', 'Personal', 'Professional', 'Sign',
                             'Download', 'Send', 'Reply', 'Generate', 'Access', 'Stats', 'Settings']
        
        if any(indicator in name for indicator in english_indicators):
            english_perms.append(perm)
    
    print(f"📊 Permissions en anglais détectées: {len(english_perms)}")
    
    renamed_count = 0
    not_found_in_mapping = []
    
    for perm in english_perms:
        old_name = perm.get('name', '')
        code = perm.get('code', '')
        perm_id = perm.get('id')
        
        if old_name in ADDITIONAL_RENAME_MAPPING:
            new_name = ADDITIONAL_RENAME_MAPPING[old_name]
            
            # Mettre à jour
            result = await db.permissions.update_one(
                {"id": perm_id},
                {"$set": {"name": new_name}}
            )
            
            if result.modified_count > 0:
                renamed_count += 1
                print(f"✅ {code:<45} {old_name} → {new_name}")
        else:
            not_found_in_mapping.append((code, old_name))
    
    print("\n" + "=" * 80)
    print("✅ RENOMMAGE TERMINÉ")
    print("=" * 80)
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Permissions renommées: {renamed_count}")
    print(f"   • Permissions non trouvées dans le mapping: {len(not_found_in_mapping)}")
    
    if not_found_in_mapping:
        print(f"\n⚠️  PERMISSIONS NON MAPPÉES (nécessitent un renommage manuel):")
        for code, name in not_found_in_mapping[:20]:
            print(f"   • {code:<45} → {name}")
        
        if len(not_found_in_mapping) > 20:
            print(f"   ... et {len(not_found_in_mapping) - 20} autres")
        
        # Proposer des traductions
        print(f"\n💡 SUGGESTIONS DE TRADUCTION:")
        for code, name in not_found_in_mapping[:10]:
            # Traduction automatique simple
            suggestion = name
            replacements = {
                ' Own': ' propres',
                ' View': ' Consulter',
                ' Edit': ' Modifier',
                ' Create': ' Créer',
                ' Delete': ' Supprimer',
                ' Manage': ' Gérer',
                ' Read': ' Lire',
                ' Write': ' Écrire',
                ' Update': ' Mettre à jour',
                ' Submit': ' Soumettre',
                ' Validate': ' Valider',
                ' Reject': ' Rejeter',
                'Own ': 'ses ',
            }
            for eng, fr in replacements.items():
                suggestion = suggestion.replace(eng, fr)
            
            print(f"   '{name}': '{suggestion}',")
    
    client.close()
    return renamed_count


async def final_report():
    """Générer un rapport final sur l'état des permissions builtin"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    print("\n" + "=" * 80)
    print("📊 RAPPORT FINAL - PERMISSIONS BUILTIN")
    print("=" * 80)
    
    builtin_perms = await db.permissions.find(
        {"category": "builtin"}, 
        {"_id": 0, "code": 1, "name": 1}
    ).to_list(1000)
    
    # Compter celles qui sont potentiellement encore en anglais
    english_indicators = ['View', 'Edit', 'Create', 'Delete', 'Manage', 'Own', 'Read', 'Write']
    english_count = sum(1 for p in builtin_perms if any(ind in p.get('name', '') for ind in english_indicators))
    french_count = len(builtin_perms) - english_count
    
    print(f"\n📈 STATISTIQUES:")
    print(f"   • Total permissions builtin: {len(builtin_perms)}")
    print(f"   • Permissions en français: {french_count} ({100*french_count/len(builtin_perms):.1f}%)")
    print(f"   • Permissions potentiellement en anglais: {english_count} ({100*english_count/len(builtin_perms):.1f}%)")
    
    print(f"\n📋 EXEMPLES DE PERMISSIONS (10 premières):")
    for perm in builtin_perms[:10]:
        print(f"   • {perm['code']:<45} → {perm['name']}")
    
    client.close()


async def main():
    print("🚀 DÉMARRAGE DU RENOMMAGE DES PERMISSIONS BUILTIN RESTANTES\n")
    
    renamed = await rename_remaining_builtin()
    await final_report()
    
    print("\n" + "=" * 80)
    print(f"✅ {renamed} permissions builtin supplémentaires renommées")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
