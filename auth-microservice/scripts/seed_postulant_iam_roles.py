"""
Script pour créer les rôles et permissions IAM pour postulants/candidats/intérimaires
Garantit la cohérence avec l'utilisation de requiredPermissions
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid


async def seed_iam_roles():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    now = datetime.now(timezone.utc)
    
    # Définition des permissions par domaine
    permissions_definitions = {
        # Missions
        "missions.browse": "Consulter les offres de missions disponibles",
        "missions.read": "Voir les détails d'une mission",
        
        # Candidatures
        "applications.create": "Postuler à une mission",
        "applications.read_own": "Consulter ses propres candidatures",
        "applications.update_own": "Modifier ses candidatures",
        "applications.delete_own": "Retirer une candidature",
        
        # Profil
        "profile.read": "Consulter son profil",
        "profile.update": "Modifier son profil",
        "profile.read_completion": "Voir le pourcentage de complétion",
        
        # Documents
        "documents.manage_own": "Gérer ses propres documents (upload, delete)",
        "documents.read_own": "Consulter ses documents",
        
        # Contrats (intérimaires)
        "contracts.read_own": "Consulter ses contrats",
        "contracts.sign": "Signer électroniquement un contrat",
        
        # Communications
        "messages.send": "Envoyer des messages à JLC",
        "messages.read_own": "Lire ses messages",
        "notifications.read_own": "Consulter ses notifications",
    }
    
    # Créer/mettre à jour les permissions
    print("📋 CRÉATION DES PERMISSIONS IAM")
    permissions_created = 0
    permissions_updated = 0
    
    for perm_code, perm_description in permissions_definitions.items():
        existing = await db.iam_permissions.find_one({"code": perm_code})
        
        perm_doc = {
            "code": perm_code,
            "label": perm_description,
            "description": perm_description,
            "category": perm_code.split('.')[0],  # missions, applications, profile, etc.
            "is_active": True,
            "updated_at": now
        }
        
        if existing:
            await db.iam_permissions.update_one(
                {"_id": existing["_id"]},
                {"$set": perm_doc}
            )
            permissions_updated += 1
        else:
            perm_doc["id"] = str(uuid.uuid4())
            perm_doc["created_at"] = now
            await db.iam_permissions.insert_one(perm_doc)
            permissions_created += 1
    
    print(f"   ✅ Permissions créées: {permissions_created}")
    print(f"   ✅ Permissions mises à jour: {permissions_updated}")
    
    # Définition des rôles avec leurs permissions
    roles_definitions = [
        {
            "code": "postulant",
            "label": "Postulant / Candidat",
            "description": "Personne en recherche de mission, sans contrat en cours. Même niveau que 'candidat'.",
            "permissions": [
                # Missions
                "missions.browse",
                "missions.read",
                # Candidatures
                "applications.create",
                "applications.read_own",
                "applications.update_own",
                "applications.delete_own",
                # Profil
                "profile.read",
                "profile.update",
                "profile.read_completion",
                # Documents
                "documents.manage_own",
                "documents.read_own",
                # Communications
                "messages.send",
                "messages.read_own",
                "notifications.read_own",
            ],
            "level": 10,
            "is_system": True,
        },
        {
            "code": "candidat",
            "label": "Candidat",
            "description": "Alias de 'postulant'. Personne en recherche de mission, sans contrat en cours.",
            "permissions": [
                # EXACTEMENT les mêmes permissions que postulant
                "missions.browse",
                "missions.read",
                "applications.create",
                "applications.read_own",
                "applications.update_own",
                "applications.delete_own",
                "profile.read",
                "profile.update",
                "profile.read_completion",
                "documents.manage_own",
                "documents.read_own",
                "messages.send",
                "messages.read_own",
                "notifications.read_own",
            ],
            "level": 10,
            "is_system": True,
        },
        {
            "code": "interimaire",
            "label": "Intérimaire",
            "description": "Personne avec un contrat en cours. Accès étendu pour gestion documents RGPD et contrats.",
            "permissions": [
                # Toutes les permissions de postulant/candidat
                "missions.browse",
                "missions.read",
                "applications.read_own",  # Peut voir historique mais ne peut pas créer si contrat actif
                "profile.read",
                "profile.update",
                "profile.read_completion",
                # Documents étendus (RGPD)
                "documents.manage_own",
                "documents.read_own",
                # Contrats (spécifique intérimaire)
                "contracts.read_own",
                "contracts.sign",
                # Communications
                "messages.send",
                "messages.read_own",
                "notifications.read_own",
            ],
            "level": 20,
            "is_system": True,
        },
    ]
    
    # Créer/mettre à jour les rôles
    print("\n👥 CRÉATION DES RÔLES IAM")
    roles_created = 0
    roles_updated = 0
    
    for role_data in roles_definitions:
        existing = await db.iam_roles.find_one({"code": role_data["code"]})
        
        role_doc = {
            "code": role_data["code"],
            "label": role_data["label"],
            "description": role_data["description"],
            "permissions": role_data["permissions"],
            "level": role_data["level"],
            "is_system": role_data["is_system"],
            "is_active": True,
            "updated_at": now
        }
        
        if existing:
            await db.iam_roles.update_one(
                {"_id": existing["_id"]},
                {"$set": role_doc}
            )
            roles_updated += 1
        else:
            role_doc["id"] = str(uuid.uuid4())
            role_doc["created_at"] = now
            await db.iam_roles.insert_one(role_doc)
            roles_created += 1
    
    print(f"   ✅ Rôles créés: {roles_created}")
    print(f"   ✅ Rôles mis à jour: {roles_updated}")
    
    # Affichage récapitulatif
    print("\n📊 RÉCAPITULATIF DES RÔLES ET PERMISSIONS")
    
    for role_def in roles_definitions:
        role = await db.iam_roles.find_one({"code": role_def["code"]}, {"_id": 0})
        if role:
            print(f"\n   🎭 {role['label']} ({role['code']})")
            print(f"      Description: {role['description']}")
            print(f"      Niveau: {role['level']}")
            print(f"      Permissions: {len(role['permissions'])}")
            
            # Regrouper par catégorie
            perms_by_category = {}
            for perm in role['permissions']:
                category = perm.split('.')[0]
                if category not in perms_by_category:
                    perms_by_category[category] = []
                perms_by_category[category].append(perm)
            
            for category, perms in sorted(perms_by_category.items()):
                print(f"         • {category}: {len(perms)} permissions")
    
    # Vérifier les utilisateurs existants et leurs rôles
    print("\n\n👤 VÉRIFICATION DES UTILISATEURS")
    
    for role_code in ["postulant", "candidat", "interimaire"]:
        user_count = await db.users.count_documents({"roles": role_code})
        print(f"   - {role_code}: {user_count} utilisateur(s)")
    
    print("\n✅ Initialisation IAM terminée avec succès")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_iam_roles())
