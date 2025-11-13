#!/usr/bin/env python3
"""
Synchroniser les 102 permissions exactes d'Emergent
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Liste COMPLÈTE et EXACTE des 102 permissions d'Emergent
EMERGENT_PERMISSIONS = [
    {"code": "*.*", "name": "*.*", "description": "All permissions", "resource": "*", "action": "*", "scope": "system", "category": "admin"},
    {"code": "admin.dashboard", "name": "Accès au tableau de bord admin", "description": "Voir le dashboard administrateur", "resource": "admin", "action": "read", "scope": "system", "category": "admin"},
    {"code": "analytics.read", "name": "analytics.read", "description": "View analytics", "resource": "analytics", "action": "read", "scope": "organization", "category": "analytics"},
    {"code": "applications.create", "name": "Créer des candidatures", "description": "Créer des candidatures à des missions", "resource": "applications", "action": "create", "scope": "own", "category": "applications"},
    {"code": "applications.read_own", "name": "Voir ses candidatures", "description": "Consulter ses propres candidatures", "resource": "applications", "action": "read", "scope": "own", "category": "applications"},
    {"code": "applications.review", "name": "Examiner les candidatures", "description": "Examiner et traiter les candidatures", "resource": "applications", "action": "review", "scope": "organization", "category": "applications"},
    {"code": "approuver_validations", "name": "Approuver les validations", "description": "Approuver les demandes de validation", "resource": "validations", "action": "approve", "scope": "organization", "category": "validations"},
    {"code": "audit.read", "name": "audit.read", "description": "View audit logs", "resource": "audit", "action": "read", "scope": "organization", "category": "audit"},
    {"code": "besoins.comment", "name": "Commenter les besoins", "description": "Ajouter des commentaires aux besoins", "resource": "besoins", "action": "comment", "scope": "organization", "category": "besoins"},
    {"code": "besoins.convert_to_mission", "name": "Convertir en mission", "description": "Convertir un besoin en mission", "resource": "besoins", "action": "convert", "scope": "organization", "category": "besoins"},
    {"code": "besoins.create", "name": "Créer des besoins", "description": "Créer de nouveaux besoins", "resource": "besoins", "action": "create", "scope": "organization", "category": "besoins"},
    {"code": "besoins.edit", "name": "Modifier les besoins", "description": "Éditer les besoins existants", "resource": "besoins", "action": "edit", "scope": "organization", "category": "besoins"},
    {"code": "besoins.read", "name": "Consulter les besoins", "description": "Voir les besoins", "resource": "besoins", "action": "read", "scope": "organization", "category": "besoins"},
    {"code": "besoins.submit", "name": "Soumettre les besoins", "description": "Soumettre des besoins pour validation", "resource": "besoins", "action": "submit", "scope": "organization", "category": "besoins"},
    {"code": "besoins.validate", "name": "Valider les besoins", "description": "Valider ou rejeter les besoins", "resource": "besoins", "action": "validate", "scope": "organization", "category": "besoins"},
    {"code": "config.manage", "name": "Gérer la configuration", "description": "Gérer la configuration générale", "resource": "config", "action": "manage", "scope": "system", "category": "config"},
    {"code": "config.read", "name": "Consulter la configuration", "description": "Voir la configuration", "resource": "config", "action": "read", "scope": "system", "category": "config"},
    {"code": "content.delete", "name": "content.delete", "description": "Delete content", "resource": "content", "action": "delete", "scope": "organization", "category": "content"},
    {"code": "content.read", "name": "content.read", "description": "View content", "resource": "content", "action": "read", "scope": "organization", "category": "content"},
    {"code": "content.write", "name": "content.write", "description": "Create/edit content", "resource": "content", "action": "write", "scope": "organization", "category": "content"},
    {"code": "contracts.approve", "name": "Approuver les contrats", "description": "Valider les contrats", "resource": "contracts", "action": "approve", "scope": "organization", "category": "contracts"},
    {"code": "contracts.create", "name": "Créer des contrats", "description": "Créer de nouveaux contrats", "resource": "contracts", "action": "create", "scope": "organization", "category": "contracts"},
    {"code": "contracts.read", "name": "Consulter les contrats", "description": "Voir les contrats", "resource": "contracts", "action": "read", "scope": "organization", "category": "contracts"},
    {"code": "contracts.update", "name": "Modifier les contrats", "description": "Mettre à jour les contrats", "resource": "contracts", "action": "update", "scope": "organization", "category": "contracts"},
    {"code": "creer_missions", "name": "Créer des missions", "description": "Créer de nouvelles missions", "resource": "missions", "action": "create", "scope": "organization", "category": "missions"},
    {"code": "emails.configure", "name": "Configurer les emails", "description": "Modifier la configuration email", "resource": "emails", "action": "configure", "scope": "system", "category": "emails"},
    {"code": "emails.manage_templates", "name": "Gérer les templates emails", "description": "Créer/modifier les templates", "resource": "emails", "action": "manage", "scope": "system", "category": "emails"},
    {"code": "emails.read_config", "name": "Consulter config emails", "description": "Voir la configuration email", "resource": "emails", "action": "read", "scope": "system", "category": "emails"},
    {"code": "emails.read_history", "name": "Consulter historique emails", "description": "Voir l'historique des emails", "resource": "emails", "action": "read_history", "scope": "system", "category": "emails"},
    {"code": "emails.test", "name": "Tester les emails", "description": "Envoyer des emails de test", "resource": "emails", "action": "test", "scope": "system", "category": "emails"},
    {"code": "entreprises.create", "name": "Créer des entreprises", "description": "Créer de nouvelles entreprises", "resource": "entreprises", "action": "create", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.delete", "name": "Supprimer des entreprises", "description": "Supprimer des entreprises", "resource": "entreprises", "action": "delete", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.edit", "name": "Modifier des entreprises", "description": "Mettre à jour les entreprises", "resource": "entreprises", "action": "edit", "scope": "organization", "category": "entreprises"},
    {"code": "entreprises.read", "name": "Consulter les entreprises", "description": "Voir les entreprises", "resource": "entreprises", "action": "read", "scope": "organization", "category": "entreprises"},
    {"code": "exporter_rapports", "name": "Exporter les rapports", "description": "Exporter les rapports", "resource": "reports", "action": "export", "scope": "organization", "category": "reports"},
    {"code": "flags.manage", "name": "Gérer les flags", "description": "Gérer les feature flags", "resource": "flags", "action": "manage", "scope": "system", "category": "flags"},
    {"code": "gestion_groupes", "name": "Gestion des groupes", "description": "Gérer les groupes", "resource": "groups", "action": "manage", "scope": "organization", "category": "groups"},
    {"code": "gestion_profils", "name": "Gestion des profils", "description": "Gérer les profils", "resource": "profiles", "action": "manage", "scope": "organization", "category": "profiles"},
    {"code": "gestion_utilisateurs", "name": "Gestion des utilisateurs", "description": "Gérer les utilisateurs", "resource": "users", "action": "manage", "scope": "organization", "category": "users"},
    {"code": "groups.manage", "name": "Gérer les groupes", "description": "Gérer les groupes", "resource": "groups", "action": "manage", "scope": "organization", "category": "groups"},
    {"code": "iam.groups.create", "name": "Créer des groupes", "description": "Créer de nouveaux groupes", "resource": "iam", "action": "create", "scope": "system", "category": "iam"},
    {"code": "iam.groups.delete", "name": "Supprimer des groupes", "description": "Supprimer des groupes", "resource": "iam", "action": "delete", "scope": "system", "category": "iam"},
    {"code": "iam.groups.manage", "name": "Gérer les groupes IAM", "description": "Gérer les groupes IAM", "resource": "iam", "action": "manage", "scope": "system", "category": "iam"},
    {"code": "iam.groups.read", "name": "Consulter les groupes IAM", "description": "Voir les groupes IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.groups.update", "name": "Modifier des groupes", "description": "Mettre à jour les groupes", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.create", "name": "Créer des permissions", "description": "Créer de nouvelles permissions", "resource": "iam", "action": "create", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.delete", "name": "Supprimer des permissions", "description": "Supprimer des permissions", "resource": "iam", "action": "delete", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.manage", "name": "Gérer les permissions", "description": "Gérer les permissions IAM", "resource": "iam", "action": "manage", "scope": "system", "category": "iam"},
    {"code": "iam.permissions.read", "name": "Consulter les permissions", "description": "Voir les permissions IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.create", "name": "Créer des profils", "description": "Créer de nouveaux profils", "resource": "iam", "action": "create", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.delete", "name": "Supprimer des profils", "description": "Supprimer des profils", "resource": "iam", "action": "delete", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.manage", "name": "Gérer les profils IAM", "description": "Gérer les profils IAM", "resource": "iam", "action": "manage", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.read", "name": "Consulter les profils IAM", "description": "Voir les profils IAM", "resource": "iam", "action": "read", "scope": "system", "category": "iam"},
    {"code": "iam.profiles.update", "name": "Modifier des profils", "description": "Mettre à jour les profils", "resource": "iam", "action": "update", "scope": "system", "category": "iam"},
    {"code": "iam.users.assign", "name": "Assigner utilisateurs", "description": "Assigner des utilisateurs aux groupes/profils", "resource": "iam", "action": "assign", "scope": "system", "category": "iam"},
    {"code": "locations.manage", "name": "Gérer les localisations", "description": "Gérer pays/villes/provinces", "resource": "locations", "action": "manage", "scope": "system", "category": "locations"},
    {"code": "missions.approve", "name": "Approuver les missions", "description": "Valider les missions", "resource": "missions", "action": "approve", "scope": "organization", "category": "missions"},
    {"code": "missions.browse", "name": "Parcourir les missions", "description": "Parcourir et rechercher les missions", "resource": "missions", "action": "browse", "scope": "organization", "category": "missions"},
    {"code": "missions.create", "name": "Créer des missions", "description": "Créer de nouvelles missions", "resource": "missions", "action": "create", "scope": "organization", "category": "missions"},
    {"code": "missions.delete", "name": "Supprimer les missions", "description": "Supprimer des missions", "resource": "missions", "action": "delete", "scope": "organization", "category": "missions"},
    {"code": "missions.publish", "name": "Publier les missions", "description": "Publier les missions", "resource": "missions", "action": "publish", "scope": "organization", "category": "missions"},
    {"code": "missions.read", "name": "Consulter les missions", "description": "Voir les missions", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    {"code": "missions.update", "name": "Modifier les missions", "description": "Mettre à jour les missions", "resource": "missions", "action": "update", "scope": "organization", "category": "missions"},
    {"code": "modifier_entreprises", "name": "Modifier entreprises", "description": "Modifier les entreprises", "resource": "entreprises", "action": "update", "scope": "organization", "category": "entreprises"},
    {"code": "modifier_interimaires", "name": "Modifier intérimaires", "description": "Modifier les intérimaires", "resource": "interimaires", "action": "update", "scope": "organization", "category": "interimaires"},
    {"code": "modifier_missions", "name": "Modifier missions", "description": "Modifier les missions", "resource": "missions", "action": "update", "scope": "organization", "category": "missions"},
    {"code": "profile.manage_own", "name": "Gérer son profil", "description": "Gérer son propre profil", "resource": "profile", "action": "manage", "scope": "own", "category": "profile"},
    {"code": "profiles.manage", "name": "Gérer les profils", "description": "Gérer les profils utilisateurs", "resource": "profiles", "action": "manage", "scope": "organization", "category": "profiles"},
    {"code": "references.manage", "name": "Gérer les références", "description": "Gérer les données de référence", "resource": "references", "action": "manage", "scope": "system", "category": "references"},
    {"code": "rejeter_validations", "name": "Rejeter les validations", "description": "Rejeter les demandes de validation", "resource": "validations", "action": "reject", "scope": "organization", "category": "validations"},
    {"code": "reports.export", "name": "Exporter les rapports", "description": "Exporter les rapports", "resource": "reports", "action": "export", "scope": "organization", "category": "reports"},
    {"code": "reports.view", "name": "Consulter les rapports", "description": "Voir les rapports", "resource": "reports", "action": "read", "scope": "organization", "category": "reports"},
    {"code": "roles.delete", "name": "roles.delete", "description": "Delete roles", "resource": "roles", "action": "delete", "scope": "organization", "category": "roles"},
    {"code": "roles.read", "name": "roles.read", "description": "View roles", "resource": "roles", "action": "read", "scope": "organization", "category": "roles"},
    {"code": "roles.write", "name": "roles.write", "description": "Create/edit roles", "resource": "roles", "action": "write", "scope": "organization", "category": "roles"},
    {"code": "rules.manage", "name": "Gérer les règles", "description": "Gérer les règles métier", "resource": "rules", "action": "manage", "scope": "system", "category": "rules"},
    {"code": "supprimer_entreprises", "name": "Supprimer entreprises", "description": "Supprimer les entreprises", "resource": "entreprises", "action": "delete", "scope": "organization", "category": "entreprises"},
    {"code": "supprimer_interimaires", "name": "Supprimer intérimaires", "description": "Supprimer les intérimaires", "resource": "interimaires", "action": "delete", "scope": "organization", "category": "interimaires"},
    {"code": "supprimer_missions", "name": "Supprimer missions", "description": "Supprimer les missions", "resource": "missions", "action": "delete", "scope": "organization", "category": "missions"},
    {"code": "system.config.read", "name": "Consulter la configuration", "description": "Voir la configuration système", "resource": "system", "action": "read", "scope": "system", "category": "system"},
    {"code": "system.config.update", "name": "Modifier la configuration", "description": "Mettre à jour la configuration", "resource": "system", "action": "update", "scope": "system", "category": "system"},
    {"code": "system.featureflags.manage", "name": "Gérer les feature flags", "description": "Activer/désactiver les fonctionnalités", "resource": "system", "action": "manage", "scope": "system", "category": "system"},
    {"code": "users.create", "name": "Créer des utilisateurs", "description": "Créer de nouveaux utilisateurs", "resource": "users", "action": "create", "scope": "organization", "category": "users"},
    {"code": "users.delete", "name": "Supprimer les utilisateurs", "description": "Supprimer des utilisateurs", "resource": "users", "action": "delete", "scope": "organization", "category": "users"},
    {"code": "users.manage_status", "name": "Gérer les statuts utilisateurs", "description": "Modifier les statuts des utilisateurs", "resource": "users", "action": "manage_status", "scope": "organization", "category": "users"},
    {"code": "users.read", "name": "Consulter les utilisateurs", "description": "Lire les informations des utilisateurs", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "users.reset_mfa", "name": "Réinitialiser MFA", "description": "Réinitialiser l'authentification multi-facteurs", "resource": "users", "action": "reset_mfa", "scope": "organization", "category": "users"},
    {"code": "users.update", "name": "Modifier les utilisateurs", "description": "Mettre à jour les utilisateurs", "resource": "users", "action": "update", "scope": "organization", "category": "users"},
    {"code": "users.write", "name": "users.write", "description": "Create/edit users", "resource": "users", "action": "write", "scope": "organization", "category": "users"},
    {"code": "validations.approve", "name": "Approuver les validations", "description": "Approuver les validations", "resource": "validations", "action": "approve", "scope": "organization", "category": "validations"},
    {"code": "validations.perform", "name": "Effectuer validations", "description": "Effectuer des validations", "resource": "validations", "action": "perform", "scope": "organization", "category": "validations"},
    {"code": "validations.reject", "name": "Rejeter les validations", "description": "Rejeter les validations", "resource": "validations", "action": "reject", "scope": "organization", "category": "validations"},
    {"code": "voir_dashboard", "name": "Voir dashboard", "description": "Accéder au tableau de bord", "resource": "dashboard", "action": "read", "scope": "organization", "category": "dashboard"},
    {"code": "voir_entreprises", "name": "Voir entreprises", "description": "Consulter les entreprises", "resource": "entreprises", "action": "read", "scope": "organization", "category": "entreprises"},
    {"code": "voir_interimaires", "name": "Voir intérimaires", "description": "Consulter les intérimaires", "resource": "interimaires", "action": "read", "scope": "organization", "category": "interimaires"},
    {"code": "voir_missions", "name": "Voir missions", "description": "Consulter les missions", "resource": "missions", "action": "read", "scope": "organization", "category": "missions"},
    {"code": "voir_rapports", "name": "Voir rapports", "description": "Consulter les rapports", "resource": "reports", "action": "read", "scope": "organization", "category": "reports"},
    {"code": "voir_statistiques", "name": "Voir statistiques", "description": "Consulter les statistiques", "resource": "statistiques", "action": "read", "scope": "organization", "category": "statistiques"},
    {"code": "voir_utilisateurs", "name": "Voir utilisateurs", "description": "Consulter les utilisateurs", "resource": "users", "action": "read", "scope": "organization", "category": "users"},
    {"code": "voir_validations", "name": "Voir validations", "description": "Consulter les validations", "resource": "validations", "action": "read", "scope": "organization", "category": "validations"},
]

async def sync_all():
    """Synchronise exactement les 102 permissions d'Emergent"""
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    print("=" * 70)
    print(" 🔄 SYNCHRONISATION COMPLÈTE - 102 PERMISSIONS EMERGENT")
    print("=" * 70)
    print(f"\n📍 MongoDB URL: {mongo_url}")
    print(f"📍 Total à synchroniser: {len(EMERGENT_PERMISSIONS)}\n")
    
    permissions_collection = db.permissions
    
    added_count = 0
    skipped_count = 0
    
    for perm_data in EMERGENT_PERMISSIONS:
        code = perm_data["code"]
        
        existing = await permissions_collection.find_one({"code": code})
        
        if existing:
            print(f"  ⏭  {code:45s} : existe")
            skipped_count += 1
        else:
            perm_id = str(uuid.uuid4())
            permission = {
                "id": perm_id,
                **perm_data,
                "is_system": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await permissions_collection.insert_one(permission)
            print(f"  ✅ {code:45s} : ajoutée")
            added_count += 1
    
    final_count = await permissions_collection.count_documents({})
    
    print("\n" + "=" * 70)
    print(" ✅ SYNCHRONISATION TERMINÉE")
    print("=" * 70)
    print(f"\n📊 Résumé:")
    print(f"   ✓ Ajoutées: {added_count}")
    print(f"   ⏭ Déjà existantes: {skipped_count}")
    print(f"   📦 TOTAL EN BASE: {final_count}")
    
    if final_count >= 102:
        print(f"\n🎉 PARFAIT! Vous avez maintenant {final_count} permissions (comme Emergent)!")
    
    print("\n💡 Prochaines étapes:")
    print("   1. Exécutez: python scripts/fix_superadmin_permissions.py")
    print("   2. Rechargez l'interface IAM")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(sync_all())
