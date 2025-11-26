#!/usr/bin/env python3
"""
Synchroniser toutes les permissions depuis Emergent
Ce script ajoute les permissions manquantes sans supprimer les existantes
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Liste COMPLÈTE des permissions (extraites du code source + Emergent)
ALL_PERMISSIONS = [
    # ============ USERS PERMISSIONS ============
    {"code": "users:read", "name": "users:read", "description": "View users", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "users:write", "name": "users:write", "description": "Create/edit users", "resource": "users", "action": "write", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "users.delete", "description": "Delete users", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    {"code": "users.read", "name": "Consulter les utilisateurs", "description": "Lire les informations des utilisateurs", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "users.create", "name": "Créer des utilisateurs", "description": "Créer de nouveaux utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.update", "name": "Modifier les utilisateurs", "description": "Mettre à jour les utilisateurs", "resource": "users", "action": "update", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "Supprimer les utilisateurs", "description": "Supprimer des utilisateurs", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    {"code": "users.manage", "name": "Gérer les utilisateurs", "description": "Gestion complète des utilisateurs", "resource": "users", "action": "manage", "scope": "organization", "category": "users"},
    {"code": "users.edit", "name": "Éditer les utilisateurs", "description": "Éditer les profils utilisateurs", "resource": "users", "action": "edit", "scope": "organization", "category": "users"},
    {"code": "users.manage_status", "name": "Gérer les statuts utilisateurs", "description": "Modifier les statuts des utilisateurs", "resource": "users", "action": "manage_status", "scope": "organization", "category": "users"},
    {"code": "users.reset_mfa", "name": "Réinitialiser MFA", "description": "Réinitialiser l'authentification multi-facteurs", "resource": "users", "action": "reset_mfa", "scope": "organization", "category": "users"},
    
    # ============ ROLES PERMISSIONS ============
    {"code": "roles:read", "name": "roles:read", "description": "View roles", "resource": "roles", "action": "read", "scope": "organization", "category": "roles"},
    {"code": "roles:write", "name": "roles:write", "description": "Create/edit roles", "resource": "roles", "action": "write", "scope": "organization", "category": "roles"},
    {"code": "roles:delete", "name": "roles:delete", "description": "Delete roles", "resource": "roles", "action": "delete", "scope": "organization", "category": "roles"},
    
    # ============ CONTENT PERMISSIONS ============
    {"code": "content:read", "name": "content:read", "description": "View content", "resource": "content", "action": "read", "scope": "organization", "category": "content"},
    {"code": "content:write", "name": "content:write", "description": "Create/edit content", "resource": "content", "action": "write", "scope": "organization", "category": "content"},
    {"code": "content:delete", "name": "content:delete", "description": "Delete content", "resource": "content", "action": "delete", "scope": "organization", "category": "content"},
    
    # ============ ANALYTICS & AUDIT ============
    {"code": "analytics:read", "name": "analytics:read", "description": "View analytics", "resource": "analytics", "action": "read", "scope": "organization", "category": "analytics"},
    {"code": "audit:read", "name": "audit:read", "description": "View audit logs", "resource": "audit", "action": "read", "scope": "organization", "category": "audit"},
    
    # ============ MISSIONS PERMISSIONS ============
    {"code": "missions.read", "name": "Consulter les missions", "description": "Voir les missions", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    {"code": "missions.create", "name": "Créer des missions", "description": "Créer de nouvelles missions", "resource": "missions", "action": "create", "scope": "organization", "category": "missions"},
    {"code": "missions.update", "name": "Modifier les missions", "description": "Mettre à jour les missions", "resource": "missions", "action": "update", "scope": "organization", "category": "missions"},
    {"code": "missions.delete", "name": "Supprimer les missions", "description": "Supprimer des missions", "resource": "missions", "action": "delete", "scope": "organization", "category": "missions"},
    {"code": "missions.approve", "name": "Approuver les missions", "description": "Valider les missions", "resource": "missions", "action": "approve", "scope": "organization", "category": "missions"},
    {"code": "missions.manage", "name": "Gérer les missions", "description": "Gestion complète des missions", "resource": "missions", "action": "manage", "scope": "organization", "category": "missions"},
    
    # ============ CONTRACTS PERMISSIONS ============
    {"code": "contracts.read", "name": "Consulter les contrats", "description": "Voir les contrats", "resource": "contracts", "action": "read", "scope": "organization", "category": "contracts"},
    {"code": "contracts.create", "name": "Créer des contrats", "description": "Créer de nouveaux contrats", "resource": "contracts", "action": "create", "scope": "organization", "category": "contracts"},
    {"code": "contracts.update", "name": "Modifier les contrats", "description": "Mettre à jour les contrats", "resource": "contracts", "action": "update", "scope": "organization", "category": "contracts"},
    {"code": "contracts.approve", "name": "Approuver les contrats", "description": "Valider les contrats", "resource": "contracts", "action": "approve", "scope": "organization", "category": "contracts"},
    
    # ============ IAM PERMISSIONS ============
    {"code": "iam.permissions.read", "name": "Consulter les permissions", "description": "Voir les permissions IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.manage", "name": "Gérer les permissions", "description": "Gérer les permissions IAM", "resource": "iam", "action": "manage", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.create", "name": "Créer des permissions", "description": "Créer de nouvelles permissions", "resource": "iam", "action": "create", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.delete", "name": "Supprimer des permissions", "description": "Supprimer des permissions", "resource": "iam", "action": "delete", "scope": "system", "category": "iam"},
    
    {"code": "iam.profiles.read", "name": "Consulter les profils IAM", "description": "Voir les profils IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.manage", "name": "Gérer les profils IAM", "description": "Gérer les profils IAM", "resource": "iam", "action": "manage", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.create", "name": "Créer des profils", "description": "Créer de nouveaux profils", "resource": "iam", "action": "create", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.update", "name": "Modifier des profils", "description": "Mettre à jour les profils", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.delete", "name": "Supprimer des profils", "description": "Supprimer des profils", "resource": "iam", "action": "delete", "scope": "system", "category": "iam"},
    
    {"code": "iam.groups.read", "name": "Consulter les groupes IAM", "description": "Voir les groupes IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.groups.manage", "name": "Gérer les groupes IAM", "description": "Gérer les groupes IAM", "resource": "iam", "action": "manage", "scope": "system", "category": "iam"},
    {"code": "iam.groups.create", "name": "Créer des groupes", "description": "Créer de nouveaux groupes", "resource": "iam", "action": "create", "scope": "system", "category": "iam"},
    {"code": "iam.groups.update", "name": "Modifier des groupes", "description": "Mettre à jour les groupes", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.groups.delete", "name": "Supprimer des groupes", "description": "Supprimer des groupes", "resource": "iam", "action": "delete", "scope": "system", "category": "iam"},
    
    {"code": "iam.users.assign", "name": "Assigner utilisateurs", "description": "Assigner des utilisateurs aux groupes/profils", "resource": "iam", "action": "assign", "scope": "system", "category": "iam"},
    
    # ============ ADMIN PERMISSIONS ============
    {"code": "admin.dashboard", "name": "Accès au tableau de bord admin", "description": "Voir le dashboard administrateur", "resource": "admin", "action": "read", "scope": "system", "category": "admin"},
    {"code": "admin.settings", "name": "Gérer les paramètres", "description": "Modifier les paramètres système", "resource": "admin", "action": "update", "scope": "system", "category": "admin"},
    
    # ============ SYSTEM PERMISSIONS ============
    {"code": "system.config.read", "name": "Consulter la configuration", "description": "Voir la configuration système", "resource": "system", "action": "read", "scope": "system", "category": "system"},
    {"code": "system.config.update", "name": "Modifier la configuration", "description": "Mettre à jour la configuration", "resource": "system", "action": "update", "scope": "system", "category": "system"},
    {"code": "system.featureflags.manage", "name": "Gérer les feature flags", "description": "Activer/désactiver les fonctionnalités", "resource": "system", "action": "manage", "scope": "system", "category": "system"},
    
    # ============ REPORTS PERMISSIONS ============
    {"code": "reports.view", "name": "Consulter les rapports", "description": "Voir les rapports", "resource": "reports", "action": "read", "scope": "organization", "category": "reports"},
    {"code": "reports.export", "name": "Exporter les rapports", "description": "Exporter les rapports", "resource": "reports", "action": "export", "scope": "organization", "category": "reports"},
    
    # ============ PROFILES PERMISSIONS ============
    {"code": "profiles.read", "name": "Consulter les profils utilisateurs", "description": "Voir les profils", "resource": "profiles", "action": "read", "scope": "organization", "category": "profiles"},
    {"code": "profiles.update", "name": "Modifier les profils utilisateurs", "description": "Mettre à jour les profils", "resource": "profiles", "action": "update", "scope": "organization", "category": "profiles"},
    
    # ============ EMAILS PERMISSIONS ============
    {"code": "emails.read_config", "name": "Consulter config emails", "description": "Voir la configuration email", "resource": "emails", "action": "read", "scope": "system", "category": "emails"},
    {"code": "emails.configure", "name": "Configurer les emails", "description": "Modifier la configuration email", "resource": "emails", "action": "configure", "scope": "system", "category": "emails"},
    {"code": "emails.test", "name": "Tester les emails", "description": "Envoyer des emails de test", "resource": "emails", "action": "test", "scope": "system", "category": "emails"},
    {"code": "emails.manage_templates", "name": "Gérer les templates emails", "description": "Créer/modifier les templates", "resource": "emails", "action": "manage", "scope": "system", "category": "emails"},
    {"code": "emails.read_history", "name": "Consulter historique emails", "description": "Voir l'historique des emails", "resource": "emails", "action": "read_history", "scope": "system", "category": "emails"},
    
    # ============ VALIDATIONS PERMISSIONS ============
    {"code": "validations.manage", "name": "Gérer les validations", "description": "Gérer les validations utilisateurs", "resource": "validations", "action": "manage", "scope": "system", "category": "validations"},
    
    # ============ LOCATIONS PERMISSIONS ============
    {"code": "locations.manage", "name": "Gérer les localisations", "description": "Gérer pays/villes/provinces", "resource": "locations", "action": "manage", "scope": "system", "category": "locations"},
    
    # ============ REFERENCES PERMISSIONS ============
    {"code": "references.manage", "name": "Gérer les références", "description": "Gérer les données de référence", "resource": "references", "action": "manage", "scope": "system", "category": "references"},
    
    # ============ CONFIG PERMISSIONS ============
    {"code": "config.manage", "name": "Gérer la configuration", "description": "Gérer la configuration générale", "resource": "config", "action": "manage", "scope": "system", "category": "config"},
    
    # ============ FLAGS PERMISSIONS ============
    {"code": "flags.manage", "name": "Gérer les flags", "description": "Gérer les feature flags", "resource": "flags", "action": "manage", "scope": "system", "category": "flags"},
    
    # ============ RULES PERMISSIONS ============
    {"code": "rules.manage", "name": "Gérer les règles", "description": "Gérer les règles métier", "resource": "rules", "action": "manage", "scope": "system", "category": "rules"},
    
    # ============ ENTREPRISES PERMISSIONS ============
    {"code": "entreprises.read", "name": "Consulter les entreprises", "description": "Voir les entreprises", "resource": "entreprises", "action": "read", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.create", "name": "Créer des entreprises", "description": "Créer de nouvelles entreprises", "resource": "entreprises", "action": "create", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.edit", "name": "Modifier des entreprises", "description": "Mettre à jour les entreprises", "resource": "entreprises", "action": "edit", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.delete", "name": "Supprimer des entreprises", "description": "Supprimer des entreprises", "resource": "entreprises", "action": "delete", "scope": "organization", "category": "entreprises"},
    
    # ============ SUPER ADMIN PERMISSION ============
    {"code": "*:*", "name": "*:*", "description": "All permissions", "resource": "*", "action": "*", "scope": "system", "category": "admin"},
]

async def sync_permissions():
    """Synchronise les permissions avec celles d'Emergent"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    print("=" * 70)
    print(" 🔄 SYNCHRONISATION DES PERMISSIONS DEPUIS EMERGENT")
    print("=" * 70)
    print(f"\n📍 MongoDB URL: {mongo_url}")
    print(f"📍 Database: auth_db")
    print(f"📍 Total permissions à vérifier: {len(ALL_PERMISSIONS)}\n")
    
    permissions_collection = db.permissions
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    print("=" * 70)
    print(" 📋 TRAITEMENT DES PERMISSIONS")
    print("=" * 70 + "\n")
    
    for perm_data in ALL_PERMISSIONS:
        code = perm_data["code"]
        
        # Vérifier si la permission existe déjà (par code)
        existing = await permissions_collection.find_one({"code": code})
        
        if existing:
            # Permission existe déjà
            print(f"  ⏭  {code:40s} : existe déjà")
            skipped_count += 1
            
            # Optionnel: mettre à jour les champs (sauf id)
            # await permissions_collection.update_one(
            #     {"code": code},
            #     {"$set": perm_data}
            # )
            # updated_count += 1
            
        else:
            # Ajouter la nouvelle permission
            perm_id = str(uuid.uuid4())
            permission = {
                "id": perm_id,
                **perm_data,
                "is_system": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await permissions_collection.insert_one(permission)
            print(f"  ✅ {code:40s} : ajoutée")
            added_count += 1
    
    # Vérifier le total final
    final_count = await permissions_collection.count_documents({})
    
    print("\n" + "=" * 70)
    print(" ✅ SYNCHRONISATION TERMINÉE")
    print("=" * 70)
    print(f"\n📊 Résumé:")
    print(f"   ✓ Permissions ajoutées: {added_count}")
    print(f"   ✓ Permissions mises à jour: {updated_count}")
    print(f"   ⏭ Permissions déjà existantes: {skipped_count}")
    print(f"   📦 Total en base: {final_count}")
    
    if final_count >= 102:
        print(f"\n🎉 Vous avez maintenant {final_count} permissions (comme Emergent)!")
    else:
        print(f"\n⚠️ Il reste {102 - final_count} permissions manquantes")
    
    print("\n💡 Prochaines étapes:")
    print("   1. Redémarrez le backend si nécessaire")
    print("   2. Rechargez l'interface IAM")
    print("   3. Les permissions devraient maintenant s'afficher")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(sync_permissions())
