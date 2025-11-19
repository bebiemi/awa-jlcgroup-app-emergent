#!/usr/bin/env python3
"""
Création de jeux de données de test pour tous les profils
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import bcrypt

async def main():
    print("=" * 80)
    print("🎲 CRÉATION DES JEUX DE DONNÉES DE TEST")
    print("=" * 80)
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['auth_db']
    
    # ============================================================================
    # 1. ENTREPRISES
    # ============================================================================
    print("\n1️⃣ Création des entreprises...")
    
    entreprises = [
        {
            "id": str(uuid4()),
            "nom": "TechCorp Gabon",
            "email": "contact@techcorp.ga",
            "telephone": "+24101234567",
            "secteur": "Technologies",
            "description": "Entreprise de développement logiciel",
            "adresse": "Libreville, Gabon",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid4()),
            "nom": "Construction Plus",
            "email": "info@constructionplus.ga",
            "telephone": "+24101234568",
            "secteur": "BTP",
            "description": "Entreprise de construction et génie civil",
            "adresse": "Port-Gentil, Gabon",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid4()),
            "nom": "Santé Services",
            "email": "contact@santeservices.ga",
            "telephone": "+24101234569",
            "secteur": "Santé",
            "description": "Services médicaux et paramédicaux",
            "adresse": "Libreville, Gabon",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "cdbb75b3-bfbc-4530-92d0-0498cbd4191d",  # Entreprise de mbj existante
            "nom": "IDAE Consulting",
            "email": "contact@idae.ga",
            "telephone": "+24101234570",
            "secteur": "Conseil",
            "description": "Cabinet de conseil en management",
            "adresse": "Libreville, Gabon",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for ent in entreprises:
        existing = await db.entreprises.find_one({"id": ent["id"]})
        if not existing:
            await db.entreprises.insert_one(ent)
            print(f"   ✅ Créé: {ent['nom']}")
        else:
            # Mise à jour pour compléter les infos
            await db.entreprises.update_one(
                {"id": ent["id"]},
                {"$set": {k: v for k, v in ent.items() if k != "id"}}
            )
            print(f"   ℹ️  Mis à jour: {ent['nom']}")
    
    # ============================================================================
    # 2. UTILISATEURS PAR PROFIL
    # ============================================================================
    print("\n2️⃣ Création des utilisateurs par profil...")
    
    # Récupérer les profils
    profiles = {}
    for code in ["profile.company", "commercial", "applicant", "admin", "super_admin"]:
        profile = await db.profiles.find_one({"code": code}, {"_id": 0})
        if profile:
            profiles[code] = profile
    
    # Hash du mot de passe par défaut
    default_password = "Test123!!"
    password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Helper pour créer un user complet
    def create_user_dict(username, email, full_name, company_id=None, profile_codes=None, roles=None):
        profile_ids = []
        if profile_codes:
            for code in profile_codes:
                if profiles.get(code):
                    profile_ids.append(profiles[code]["id"])
        
        return {
            "id": str(uuid4()),
            "username": username,
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "company_id": company_id,
            "entreprise_id": company_id,
            "profile_ids": profile_ids,
            "group_ids": [],
            "roles": roles or [],
            "status": "active",
            "is_verified": True,
            "provider": "local",
            "provider_user_id": None,
            "mfa_enabled": False,
            "mfa_required": False,
            "mfa_methods": [],
            "metadata": {},
            "profile_history": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    utilisateurs = [
        # 2.1 Entreprises (1 par entreprise)
        create_user_dict("techcorp_admin", "admin@techcorp.ga", "Admin TechCorp", 
                        entreprises[0]["id"], ["profile.company"], ["company"]),
        create_user_dict("construction_admin", "admin@constructionplus.ga", "Admin Construction Plus",
                        entreprises[1]["id"], ["profile.company"], ["company"]),
        create_user_dict("sante_admin", "admin@santeservices.ga", "Admin Santé Services",
                        entreprises[2]["id"], ["profile.company"], ["company"]),
        
        # 2.2 Commerciaux
        create_user_dict("commercial1", "commercial1@jlc.ga", "Jean Commercial",
                        None, ["commercial"], ["commercial"]),
        create_user_dict("commercial2", "commercial2@jlc.ga", "Marie Commerciale",
                        None, ["commercial"], ["commercial"]),
        
        # 2.3 Candidats
        create_user_dict("candidat1", "candidat1@gmail.com", "Pierre Candidat",
                        None, ["applicant"], ["applicant"]),
        create_user_dict("candidat2", "candidat2@gmail.com", "Sophie Candidate",
                        None, ["applicant"], ["applicant"]),
        create_user_dict("candidat3", "candidat3@gmail.com", "Ahmed Candidat",
                        None, ["applicant"], ["applicant"]),
    ]
    
    created_users = {}
    for user in utilisateurs:
        existing = await db.users.find_one({"username": user["username"]})
        if not existing:
            await db.users.insert_one(user)
            created_users[user["username"]] = user["id"]
            print(f"   ✅ Créé: {user['username']} ({user['full_name']}) - {user.get('roles', [])[0] if user.get('roles') else 'N/A'}")
        else:
            created_users[user["username"]] = existing["id"]
            print(f"   ℹ️  Existe: {user['username']}")
    
    # ============================================================================
    # 3. MISSIONS
    # ============================================================================
    print("\n3️⃣ Création des missions...")
    
    missions = [
        # Missions TechCorp
        {
            "id": str(uuid4()),
            "title": "Développeur Full Stack",
            "description": "Développement d'applications web avec React et FastAPI",
            "company_id": entreprises[0]["id"],
            "contract_type": "CDI",
            "location": "Libreville",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "salary_min": 800000,
            "salary_max": 1200000,
            "status": "published",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "techcorp_admin"][0],
            "applications_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "title": "DevOps Engineer",
            "description": "Gestion infrastructure cloud et CI/CD",
            "company_id": entreprises[0]["id"],
            "contract_type": "CDI",
            "location": "Libreville",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=45)).isoformat(),
            "salary_min": 1000000,
            "salary_max": 1500000,
            "status": "published",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "techcorp_admin"][0],
            "applications_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc)
        },
        
        # Missions Construction Plus
        {
            "id": str(uuid4()),
            "title": "Chef de Chantier",
            "description": "Supervision des travaux de construction",
            "company_id": entreprises[1]["id"],
            "contract_type": "CDD",
            "location": "Port-Gentil",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
            "salary_min": 700000,
            "salary_max": 900000,
            "status": "published",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "construction_admin"][0],
            "applications_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "title": "Ingénieur Génie Civil",
            "description": "Études techniques et suivi de chantier",
            "company_id": entreprises[1]["id"],
            "contract_type": "CDI",
            "location": "Port-Gentil",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
            "salary_min": 1200000,
            "salary_max": 1600000,
            "status": "published",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "construction_admin"][0],
            "applications_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc)
        },
        
        # Missions Santé Services
        {
            "id": str(uuid4()),
            "title": "Infirmier(ère) Diplômé(e)",
            "description": "Soins aux patients en milieu hospitalier",
            "company_id": entreprises[2]["id"],
            "contract_type": "CDI",
            "location": "Libreville",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=20)).isoformat(),
            "salary_min": 500000,
            "salary_max": 700000,
            "status": "published",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "sante_admin"][0],
            "applications_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc)
        },
        
        # Mission IDAE (créée par admin)
        {
            "id": str(uuid4()),
            "title": "Consultant en Stratégie",
            "description": "Accompagnement stratégique des entreprises",
            "company_id": entreprises[3]["id"],  # IDAE
            "contract_type": "CDI",
            "location": "Libreville",
            "start_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "salary_min": 1500000,
            "salary_max": 2000000,
            "status": "published",
            "created_by": (await db.users.find_one({"username": "admin"}))["id"],
            "applications_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "published_at": datetime.now(timezone.utc)
        },
    ]
    
    created_missions = []
    for mission in missions:
        existing = await db.missions.find_one({"title": mission["title"], "company_id": mission["company_id"]})
        if not existing:
            await db.missions.insert_one(mission)
            created_missions.append(mission)
            print(f"   ✅ Créé: {mission['title']} - {[e for e in entreprises if e['id'] == mission['company_id']][0]['nom']}")
        else:
            created_missions.append(existing)
            print(f"   ℹ️  Existe: {mission['title']}")
    
    # ============================================================================
    # 4. BESOINS
    # ============================================================================
    print("\n4️⃣ Création des besoins...")
    
    besoins = [
        {
            "id": str(uuid4()),
            "entreprise_id": entreprises[0]["id"],
            "entreprise_name": entreprises[0]["nom"],
            "titre": "Développeurs Python",
            "description": "Recrutement de 3 développeurs Python pour projet 6 mois",
            "nombre_postes": 3,
            "duree": "periode_precise",
            "duree_mois": 6,
            "type_poste": "CDD",
            "competences_attendues": ["Python", "FastAPI", "MongoDB"],
            "status": "soumis",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "techcorp_admin"][0],
            "created_by_name": "Admin TechCorp",
            "responsable_besoin_id": [u["id"] for u in utilisateurs if u["username"] == "techcorp_admin"][0],
            "status_history": [],
            "mission_ids": [],
            "pieces_jointes": [],
            "custom_fields": {},
            "comments_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid4()),
            "entreprise_id": entreprises[1]["id"],
            "entreprise_name": entreprises[1]["nom"],
            "titre": "Maçons Qualifiés",
            "description": "Recherche de 5 maçons pour chantier 12 mois",
            "nombre_postes": 5,
            "duree": "periode_precise",
            "duree_mois": 12,
            "type_poste": "CDD",
            "competences_attendues": ["Maçonnerie", "Lecture de plans"],
            "status": "soumis",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "construction_admin"][0],
            "created_by_name": "Admin Construction Plus",
            "responsable_besoin_id": [u["id"] for u in utilisateurs if u["username"] == "construction_admin"][0],
            "status_history": [],
            "mission_ids": [],
            "pieces_jointes": [],
            "custom_fields": {},
            "comments_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid4()),
            "entreprise_id": entreprises[2]["id"],
            "entreprise_name": entreprises[2]["nom"],
            "titre": "Aide-Soignant(e)s",
            "description": "Recrutement de 2 aide-soignants en CDI",
            "nombre_postes": 2,
            "duree": "indeterminee",
            "type_poste": "CDI",
            "competences_attendues": ["Soins de base", "Hygiène"],
            "status": "soumis",
            "created_by": [u["id"] for u in utilisateurs if u["username"] == "sante_admin"][0],
            "created_by_name": "Admin Santé Services",
            "responsable_besoin_id": [u["id"] for u in utilisateurs if u["username"] == "sante_admin"][0],
            "status_history": [],
            "mission_ids": [],
            "pieces_jointes": [],
            "custom_fields": {},
            "comments_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid4()),
            "entreprise_id": entreprises[3]["id"],  # IDAE
            "entreprise_name": entreprises[3]["nom"],
            "titre": "Consultant Junior",
            "description": "Recrutement d'un consultant junior en management",
            "nombre_postes": 1,
            "duree": "indeterminee",
            "type_poste": "CDI",
            "competences_attendues": ["Conseil", "Analyse"],
            "status": "analyse",
            "created_by": (await db.users.find_one({"username": "mbj"}))["id"],
            "created_by_name": "MBJ",
            "responsable_besoin_id": (await db.users.find_one({"username": "mbj"}))["id"],
            "status_history": [],
            "mission_ids": [],
            "pieces_jointes": [],
            "custom_fields": {},
            "comments_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
    ]
    
    for besoin in besoins:
        existing = await db.besoins.find_one({"titre": besoin["titre"], "entreprise_id": besoin["entreprise_id"]})
        if not existing:
            await db.besoins.insert_one(besoin)
            print(f"   ✅ Créé: {besoin['titre']} - {besoin['entreprise_name']}")
        else:
            print(f"   ℹ️  Existe: {besoin['titre']}")
    
    # ============================================================================
    # 5. CANDIDATURES
    # ============================================================================
    print("\n5️⃣ Création des candidatures...")
    
    # Récupérer les IDs des candidats
    candidat_ids = [created_users.get(f"candidat{i}") for i in range(1, 4)]
    
    candidatures = [
        # Candidatures pour TechCorp
        {
            "id": str(uuid4()),
            "mission_id": created_missions[0]["id"],  # Développeur Full Stack
            "candidate_id": candidat_ids[0],
            "status": "pending",
            "cover_letter": "Je suis très intéressé par ce poste de développeur...",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid4()),
            "mission_id": created_missions[0]["id"],  # Développeur Full Stack
            "candidate_id": candidat_ids[1],
            "status": "shortlisted",
            "cover_letter": "Avec 3 ans d'expérience en React et Python...",
            "created_at": datetime.now(timezone.utc) - timedelta(days=2),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Candidatures pour Construction Plus
        {
            "id": str(uuid4()),
            "mission_id": created_missions[2]["id"],  # Chef de Chantier
            "candidate_id": candidat_ids[2],
            "status": "pending",
            "cover_letter": "Fort de 5 ans d'expérience en gestion de chantier...",
            "created_at": datetime.now(timezone.utc) - timedelta(days=1),
            "updated_at": datetime.now(timezone.utc)
        },
        
        # Candidature pour Santé Services
        {
            "id": str(uuid4()),
            "mission_id": created_missions[4]["id"],  # Infirmier
            "candidate_id": candidat_ids[0],
            "status": "pending",
            "cover_letter": "Diplômée d'État avec 2 ans d'expérience...",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
    ]
    
    for candidature in candidatures:
        existing = await db.applications.find_one({
            "mission_id": candidature["mission_id"],
            "candidate_id": candidature["candidate_id"]
        })
        if not existing:
            await db.applications.insert_one(candidature)
            mission = [m for m in created_missions if m["id"] == candidature["mission_id"]][0]
            print(f"   ✅ Créé: Candidature pour '{mission['title']}'")
        else:
            print(f"   ℹ️  Existe: Candidature déjà présente")
    
    # ============================================================================
    # RÉSUMÉ
    # ============================================================================
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES DONNÉES CRÉÉES")
    print("=" * 80)
    
    total_entreprises = await db.entreprises.count_documents({})
    total_users = await db.users.count_documents({})
    total_missions = await db.missions.count_documents({})
    total_besoins = await db.besoins.count_documents({})
    total_candidatures = await db.applications.count_documents({})
    
    print(f"\n✅ Entreprises : {total_entreprises}")
    print(f"✅ Utilisateurs : {total_users}")
    print(f"✅ Missions : {total_missions}")
    print(f"✅ Besoins : {total_besoins}")
    print(f"✅ Candidatures : {total_candidatures}")
    
    print("\n" + "=" * 80)
    print("🔑 COMPTES DE TEST CRÉÉS")
    print("=" * 80)
    print(f"\nMot de passe pour tous : {default_password}")
    print("\n📋 Profil ENTREPRISE :")
    print("   - techcorp_admin / TechCorp Gabon")
    print("   - construction_admin / Construction Plus")
    print("   - sante_admin / Santé Services")
    print("   - mbj / IDAE Consulting (existant)")
    
    print("\n📋 Profil COMMERCIAL :")
    print("   - commercial1 (Jean Commercial)")
    print("   - commercial2 (Marie Commerciale)")
    
    print("\n📋 Profil CANDIDAT :")
    print("   - candidat1 (Pierre Candidat)")
    print("   - candidat2 (Sophie Candidate)")
    print("   - candidat3 (Ahmed Candidat)")
    
    print("\n📋 Profil ADMIN (existants) :")
    print("   - admin / Awana2025!")
    print("   - nina (Candidat) / azerty123456!!")
    
    print("\n" + "=" * 80)
    print("✅ CRÉATION TERMINÉE")
    print("=" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
