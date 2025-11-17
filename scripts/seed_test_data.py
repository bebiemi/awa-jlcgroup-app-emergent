"""
Script de génération de données de test pour l'application Awana
Crée des entreprises, besoins, missions, profils et candidatures
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configuration MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

# Données de test
COMPANIES = [
    {
        "name": "Gabon Télécom SA",
        "siret": "GA001234567890",
        "nif": "NIF_GAB_001",
        "sector": "Télécommunications",
        "size": "Grande entreprise",
        "description": "Leader des télécommunications au Gabon",
        "address": "Boulevard Triomphal, Libreville",
        "needs_count": 5
    },
    {
        "name": "Banque Internationale du Gabon",
        "siret": "GA002345678901",
        "nif": "NIF_GAB_002",
        "sector": "Banque & Finance",
        "size": "Grande entreprise",
        "description": "Institution bancaire de référence",
        "address": "Avenue du Colonel Parant, Libreville",
        "needs_count": 4
    },
    {
        "name": "Société Gabonaise de Raffinage (SOGARA)",
        "siret": "GA003456789012",
        "nif": "NIF_GAB_003",
        "sector": "Pétrole & Gaz",
        "size": "Grande entreprise",
        "description": "Raffinage et distribution de produits pétroliers",
        "address": "Port-Gentil",
        "needs_count": 4
    }
]

BESOINS = [
    # Gabon Télécom (5 besoins)
    {
        "company_index": 0,
        "title": "Technicien Réseau Fibre Optique",
        "description": "Installation et maintenance réseau fibre optique FTTH",
        "job_type": "Télécommunications",
        "positions": 3,
        "required_skills": ["Fibre optique", "Réseau télécom", "FTTH", "Test de câblage"],
        "experience_required": "2-5 ans",
        "education_level": "Bac+2",
        "salary_range": "450 000 - 650 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "high"
    },
    {
        "company_index": 0,
        "title": "Développeur Full Stack",
        "description": "Développement applications web et mobile pour services clients",
        "job_type": "Informatique",
        "positions": 2,
        "required_skills": ["React", "Node.js", "MongoDB", "API REST", "Mobile"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+5",
        "salary_range": "800 000 - 1 200 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "medium"
    },
    {
        "company_index": 0,
        "title": "Chargé de Clientèle",
        "description": "Gestion portefeuille clients entreprises",
        "job_type": "Commercial",
        "positions": 4,
        "required_skills": ["Relation client", "Vente B2B", "Négociation", "CRM"],
        "experience_required": "2-5 ans",
        "education_level": "Bac+3",
        "salary_range": "400 000 - 600 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "medium"
    },
    {
        "company_index": 0,
        "title": "Ingénieur Sécurité Réseau",
        "description": "Sécurisation infrastructure réseau et cybersécurité",
        "job_type": "Informatique",
        "positions": 1,
        "required_skills": ["Cybersécurité", "Firewall", "VPN", "Intrusion detection", "Linux"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+5",
        "salary_range": "900 000 - 1 400 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "high"
    },
    {
        "company_index": 0,
        "title": "Technicien Support Informatique",
        "description": "Support technique niveau 1 et 2 pour clients entreprises",
        "job_type": "Informatique",
        "positions": 5,
        "required_skills": ["Support IT", "Windows", "Résolution problèmes", "Service client"],
        "experience_required": "0-2 ans",
        "education_level": "Bac+2",
        "salary_range": "350 000 - 450 000 FCFA",
        "contract_type": "CDD",
        "work_schedule": "Temps plein",
        "urgency": "medium"
    },
    
    # Banque Internationale du Gabon (4 besoins)
    {
        "company_index": 1,
        "title": "Chargé d'Affaires PME",
        "description": "Gestion et développement portefeuille clientèle PME",
        "job_type": "Banque & Finance",
        "positions": 2,
        "required_skills": ["Analyse financière", "Crédit", "Relation client", "Risque bancaire"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+5",
        "salary_range": "700 000 - 1 000 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "high"
    },
    {
        "company_index": 1,
        "title": "Conseiller Clientèle Agence",
        "description": "Accueil et conseil clients particuliers en agence",
        "job_type": "Banque & Finance",
        "positions": 6,
        "required_skills": ["Relation client", "Produits bancaires", "Vente", "Gestion de caisse"],
        "experience_required": "0-2 ans",
        "education_level": "Bac+2",
        "salary_range": "350 000 - 500 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "medium"
    },
    {
        "company_index": 1,
        "title": "Analyste Risques Crédit",
        "description": "Analyse et évaluation risques crédit entreprises",
        "job_type": "Banque & Finance",
        "positions": 2,
        "required_skills": ["Analyse financière", "Modélisation risque", "Excel avancé", "Réglementation bancaire"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+5",
        "salary_range": "800 000 - 1 200 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "high"
    },
    {
        "company_index": 1,
        "title": "Auditeur Interne",
        "description": "Audit des processus et contrôle interne",
        "job_type": "Audit & Contrôle",
        "positions": 1,
        "required_skills": ["Audit", "Contrôle interne", "Comptabilité", "Réglementation"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+5",
        "salary_range": "900 000 - 1 300 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "medium"
    },
    
    # SOGARA (4 besoins)
    {
        "company_index": 2,
        "title": "Ingénieur Process Raffinage",
        "description": "Supervision et optimisation processus de raffinage",
        "job_type": "Pétrole & Gaz",
        "positions": 2,
        "required_skills": ["Raffinage", "Procédés chimiques", "HSSE", "Instrumentation"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+5",
        "salary_range": "1 200 000 - 1 800 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "high"
    },
    {
        "company_index": 2,
        "title": "Technicien Maintenance Industrielle",
        "description": "Maintenance préventive et curative équipements industriels",
        "job_type": "Maintenance",
        "positions": 8,
        "required_skills": ["Maintenance industrielle", "Mécanique", "Électricité", "Hydraulique"],
        "experience_required": "2-5 ans",
        "education_level": "Bac+2",
        "salary_range": "500 000 - 700 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "3x8",
        "urgency": "high"
    },
    {
        "company_index": 2,
        "title": "Responsable HSE",
        "description": "Pilotage politique santé, sécurité et environnement",
        "job_type": "HSE",
        "positions": 1,
        "required_skills": ["HSE", "Réglementation ICPE", "Management QSE", "Audit sécurité"],
        "experience_required": "10+ ans",
        "education_level": "Bac+5",
        "salary_range": "1 500 000 - 2 000 000 FCFA",
        "contract_type": "CDI",
        "work_schedule": "Temps plein",
        "urgency": "high"
    },
    {
        "company_index": 2,
        "title": "Opérateur de Production",
        "description": "Conduite et surveillance unités de production",
        "job_type": "Production",
        "positions": 12,
        "required_skills": ["Conduite process", "Lecture instrumentation", "Procédures sécurité"],
        "experience_required": "0-2 ans",
        "education_level": "Bac",
        "salary_range": "400 000 - 550 000 FCFA",
        "contract_type": "CDD",
        "work_schedule": "3x8",
        "urgency": "medium"
    }
]

MISSIONS_JLC = [
    {
        "title": "Agent de Sécurité Centre Commercial",
        "description": "Surveillance et sécurisation du centre commercial Mbolo",
        "job_type": "Sécurité",
        "location": "Libreville",
        "positions": 4,
        "required_skills": ["Surveillance", "Rondes de sécurité", "Gestion conflits", "Secourisme"],
        "experience_required": "0-2 ans",
        "education_level": "Bac",
        "salary_range": "250 000 - 350 000 FCFA",
        "start_date_days": 10,
        "duration_months": 6
    },
    {
        "title": "Caissier Supermarché",
        "description": "Encaissement et service client en grande distribution",
        "job_type": "Commerce",
        "location": "Libreville",
        "positions": 6,
        "required_skills": ["Caisse", "Service client", "Gestion espèces", "Merchandising"],
        "experience_required": "0-2 ans",
        "education_level": "Bac",
        "salary_range": "200 000 - 300 000 FCFA",
        "start_date_days": 5,
        "duration_months": 3
    },
    {
        "title": "Manutentionnaire Entrepôt",
        "description": "Manutention et gestion stocks entrepôt logistique",
        "job_type": "Logistique",
        "location": "Port-Gentil",
        "positions": 8,
        "required_skills": ["Manutention", "Gestion stocks", "Chariot élévateur", "Préparation commandes"],
        "experience_required": "0-2 ans",
        "education_level": "CAP/BEP",
        "salary_range": "250 000 - 350 000 FCFA",
        "start_date_days": 15,
        "duration_months": 4
    },
    {
        "title": "Réceptionniste Hôtel 4 étoiles",
        "description": "Accueil clientèle internationale, réservations et conciergerie",
        "job_type": "Hôtellerie",
        "location": "Libreville",
        "positions": 3,
        "required_skills": ["Accueil", "Anglais", "Réservation", "Service client"],
        "experience_required": "2-5 ans",
        "education_level": "Bac+2",
        "salary_range": "350 000 - 500 000 FCFA",
        "start_date_days": 20,
        "duration_months": 12
    },
    {
        "title": "Serveur Restaurant Gastronomique",
        "description": "Service en salle restaurant haut de gamme",
        "job_type": "Restauration",
        "location": "Libreville",
        "positions": 5,
        "required_skills": ["Service en salle", "Œnologie", "Anglais", "Vente additionnelle"],
        "experience_required": "2-5 ans",
        "education_level": "CAP/BEP",
        "salary_range": "300 000 - 450 000 FCFA",
        "start_date_days": 12,
        "duration_months": 6
    },
    {
        "title": "Agent d'Entretien Bureaux",
        "description": "Nettoyage et entretien locaux professionnels",
        "job_type": "Services",
        "location": "Libreville",
        "positions": 10,
        "required_skills": ["Nettoyage professionnel", "Utilisation matériel", "Hygiène"],
        "experience_required": "0-2 ans",
        "education_level": "Primaire",
        "salary_range": "150 000 - 250 000 FCFA",
        "start_date_days": 3,
        "duration_months": 12
    },
    {
        "title": "Chauffeur Poids Lourd",
        "description": "Transport marchandises longue distance",
        "job_type": "Transport",
        "location": "Libreville - Port-Gentil",
        "positions": 4,
        "required_skills": ["Permis EC", "Conduite poids lourd", "Mécanique de base", "Sécurité routière"],
        "experience_required": "5-10 ans",
        "education_level": "CAP/BEP",
        "salary_range": "450 000 - 650 000 FCFA",
        "start_date_days": 7,
        "duration_months": 12
    },
    {
        "title": "Électricien Bâtiment",
        "description": "Installation et maintenance électrique bâtiments",
        "job_type": "BTP",
        "location": "Libreville",
        "positions": 5,
        "required_skills": ["Installation électrique", "Normes NF C 15-100", "Dépannage", "Lecture plans"],
        "experience_required": "2-5 ans",
        "education_level": "CAP/BEP",
        "salary_range": "400 000 - 600 000 FCFA",
        "start_date_days": 10,
        "duration_months": 6
    },
    {
        "title": "Plombier Sanitaire",
        "description": "Installation et réparation plomberie/sanitaire",
        "job_type": "BTP",
        "location": "Libreville",
        "positions": 3,
        "required_skills": ["Plomberie", "Sanitaire", "Soudure", "Lecture plans"],
        "experience_required": "2-5 ans",
        "education_level": "CAP/BEP",
        "salary_range": "400 000 - 600 000 FCFA",
        "start_date_days": 14,
        "duration_months": 6
    },
    {
        "title": "Secrétaire Administrative",
        "description": "Gestion administrative et accueil téléphonique",
        "job_type": "Administration",
        "location": "Libreville",
        "positions": 2,
        "required_skills": ["Bureautique", "Gestion administrative", "Accueil téléphonique", "Organisation"],
        "experience_required": "2-5 ans",
        "education_level": "Bac+2",
        "salary_range": "300 000 - 450 000 FCFA",
        "start_date_days": 8,
        "duration_months": 12
    },
    {
        "title": "Comptable Junior",
        "description": "Saisie comptable et déclarations fiscales",
        "job_type": "Comptabilité",
        "location": "Libreville",
        "positions": 2,
        "required_skills": ["Comptabilité générale", "Fiscalité", "Sage", "Déclarations"],
        "experience_required": "0-2 ans",
        "education_level": "Bac+2",
        "salary_range": "350 000 - 500 000 FCFA",
        "start_date_days": 20,
        "duration_months": 12
    },
    {
        "title": "Assistant Commercial",
        "description": "Support équipe commerciale et suivi clients",
        "job_type": "Commercial",
        "location": "Libreville",
        "positions": 3,
        "required_skills": ["Support commercial", "CRM", "Devis/Factures", "Suivi clients"],
        "experience_required": "0-2 ans",
        "education_level": "Bac+2",
        "salary_range": "300 000 - 450 000 FCFA",
        "start_date_days": 15,
        "duration_months": 6
    },
    {
        "title": "Agent Call Center",
        "description": "Réception appels et renseignements clients",
        "job_type": "Service Client",
        "location": "Libreville",
        "positions": 8,
        "required_skills": ["Téléphone", "Écoute active", "CRM", "Gestion réclamations"],
        "experience_required": "0-2 ans",
        "education_level": "Bac",
        "salary_range": "250 000 - 350 000 FCFA",
        "start_date_days": 5,
        "duration_months": 12
    },
    {
        "title": "Développeur Web Junior",
        "description": "Développement sites web et applications",
        "job_type": "Informatique",
        "location": "Libreville",
        "positions": 2,
        "required_skills": ["HTML/CSS", "JavaScript", "PHP", "WordPress"],
        "experience_required": "0-2 ans",
        "education_level": "Bac+2",
        "salary_range": "400 000 - 600 000 FCFA",
        "start_date_days": 30,
        "duration_months": 12
    },
    {
        "title": "Infirmier Médecine du Travail",
        "description": "Suivi santé salariés et visites médicales",
        "job_type": "Santé",
        "location": "Port-Gentil",
        "positions": 2,
        "required_skills": ["Soins infirmiers", "Médecine du travail", "Premiers secours", "Suivi médical"],
        "experience_required": "5-10 ans",
        "education_level": "Bac+3",
        "salary_range": "500 000 - 700 000 FCFA",
        "start_date_days": 25,
        "duration_months": 12
    }
]

CANDIDATS_PROFILES = [
    {
        "username": "marie_tech",
        "email": "marie.tchoumba@email.ga",
        "full_name": "Marie TCHOUMBA",
        "password": "Password123!",
        "phone": "+241 06 12 34 56",
        "profile": {
            "skills": [
                {"name": "Fibre optique", "level": "expert", "years": 5},
                {"name": "Réseau télécom", "level": "expert", "years": 6},
                {"name": "FTTH", "level": "avancé", "years": 4},
                {"name": "Test de câblage", "level": "expert", "years": 5}
            ],
            "sectors": ["Télécommunications", "Informatique"],
            "years_of_experience": 6,
            "education_level": "Bac+3",
            "certifications": ["FTTH Certified", "Cisco CCNA"],
            "languages": ["Français", "Anglais"]
        }
    },
    {
        "username": "jean_dev",
        "email": "jean.mbadinga@email.ga",
        "full_name": "Jean-Pierre MBADINGA",
        "password": "Password123!",
        "phone": "+241 06 23 45 67",
        "profile": {
            "skills": [
                {"name": "React", "level": "expert", "years": 7},
                {"name": "Node.js", "level": "expert", "years": 8},
                {"name": "MongoDB", "level": "avancé", "years": 6},
                {"name": "API REST", "level": "expert", "years": 8},
                {"name": "Mobile", "level": "intermédiaire", "years": 3}
            ],
            "sectors": ["Informatique", "Télécommunications"],
            "years_of_experience": 8,
            "education_level": "Bac+5",
            "certifications": ["AWS Certified", "React Native Certified"],
            "languages": ["Français", "Anglais", "Espagnol"]
        }
    },
    {
        "username": "sarah_bank",
        "email": "sarah.ondo@email.ga",
        "full_name": "Sarah ONDO OBIANG",
        "password": "Password123!",
        "phone": "+241 06 34 56 78",
        "profile": {
            "skills": [
                {"name": "Analyse financière", "level": "expert", "years": 7},
                {"name": "Crédit", "level": "expert", "years": 7},
                {"name": "Relation client", "level": "avancé", "years": 8},
                {"name": "Risque bancaire", "level": "expert", "years": 6}
            ],
            "sectors": ["Banque & Finance"],
            "years_of_experience": 8,
            "education_level": "Bac+5",
            "certifications": ["CFA Level 2", "Analyste Crédit Certifié"],
            "languages": ["Français", "Anglais"]
        }
    },
    {
        "username": "paul_oil",
        "email": "paul.moussavou@email.ga",
        "full_name": "Paul MOUSSAVOU",
        "password": "Password123!",
        "phone": "+241 06 45 67 89",
        "profile": {
            "skills": [
                {"name": "Raffinage", "level": "expert", "years": 10},
                {"name": "Procédés chimiques", "level": "expert", "years": 12},
                {"name": "HSSE", "level": "expert", "years": 10},
                {"name": "Instrumentation", "level": "avancé", "years": 8}
            ],
            "sectors": ["Pétrole & Gaz"],
            "years_of_experience": 12,
            "education_level": "Bac+5",
            "certifications": ["Ingénieur Process", "HSE Manager"],
            "languages": ["Français", "Anglais"]
        }
    },
    {
        "username": "alice_maint",
        "email": "alice.nzamba@email.ga",
        "full_name": "Alice NZAMBA",
        "password": "Password123!",
        "phone": "+241 06 56 78 90",
        "profile": {
            "skills": [
                {"name": "Maintenance industrielle", "level": "avancé", "years": 4},
                {"name": "Mécanique", "level": "avancé", "years": 5},
                {"name": "Électricité", "level": "intermédiaire", "years": 3},
                {"name": "Hydraulique", "level": "intermédiaire", "years": 3}
            ],
            "sectors": ["Maintenance", "Production"],
            "years_of_experience": 5,
            "education_level": "Bac+2",
            "certifications": ["Technicien Maintenance"],
            "languages": ["Français"]
        }
    },
    {
        "username": "robert_sec",
        "email": "robert.nguema@email.ga",
        "full_name": "Robert NGUEMA",
        "password": "Password123!",
        "phone": "+241 06 67 89 01",
        "profile": {
            "skills": [
                {"name": "Surveillance", "level": "avancé", "years": 3},
                {"name": "Rondes de sécurité", "level": "avancé", "years": 3},
                {"name": "Gestion conflits", "level": "intermédiaire", "years": 2},
                {"name": "Secourisme", "level": "avancé", "years": 3}
            ],
            "sectors": ["Sécurité"],
            "years_of_experience": 3,
            "education_level": "Bac",
            "certifications": ["Agent de Sécurité", "SST"],
            "languages": ["Français"]
        }
    },
    {
        "username": "grace_hotel",
        "email": "grace.bounda@email.ga",
        "full_name": "Grace BOUNDA",
        "password": "Password123!",
        "phone": "+241 06 78 90 12",
        "profile": {
            "skills": [
                {"name": "Accueil", "level": "expert", "years": 5},
                {"name": "Anglais", "level": "expert", "years": 6},
                {"name": "Réservation", "level": "avancé", "years": 4},
                {"name": "Service client", "level": "expert", "years": 5}
            ],
            "sectors": ["Hôtellerie", "Tourisme"],
            "years_of_experience": 5,
            "education_level": "Bac+2",
            "certifications": ["BTS Hôtellerie"],
            "languages": ["Français", "Anglais", "Portugais"]
        }
    },
    {
        "username": "daniel_elec",
        "email": "daniel.owono@email.ga",
        "full_name": "Daniel OWONO",
        "password": "Password123!",
        "phone": "+241 06 89 01 23",
        "profile": {
            "skills": [
                {"name": "Installation électrique", "level": "avancé", "years": 4},
                {"name": "Normes NF C 15-100", "level": "avancé", "years": 4},
                {"name": "Dépannage", "level": "avancé", "years": 4},
                {"name": "Lecture plans", "level": "intermédiaire", "years": 3}
            ],
            "sectors": ["BTP", "Électricité"],
            "years_of_experience": 4,
            "education_level": "CAP/BEP",
            "certifications": ["CAP Électricien"],
            "languages": ["Français"]
        }
    },
    {
        "username": "emma_compta",
        "email": "emma.mengue@email.ga",
        "full_name": "Emma MENGUE",
        "password": "Password123!",
        "phone": "+241 06 90 12 34",
        "profile": {
            "skills": [
                {"name": "Comptabilité générale", "level": "intermédiaire", "years": 2},
                {"name": "Fiscalité", "level": "débutant", "years": 1},
                {"name": "Sage", "level": "intermédiaire", "years": 2},
                {"name": "Déclarations", "level": "débutant", "years": 1}
            ],
            "sectors": ["Comptabilité", "Administration"],
            "years_of_experience": 2,
            "education_level": "Bac+2",
            "certifications": ["BTS Comptabilité"],
            "languages": ["Français"]
        }
    },
    {
        "username": "thomas_driver",
        "email": "thomas.ibinga@email.ga",
        "full_name": "Thomas IBINGA",
        "password": "Password123!",
        "phone": "+241 06 01 23 45",
        "profile": {
            "skills": [
                {"name": "Permis EC", "level": "expert", "years": 8},
                {"name": "Conduite poids lourd", "level": "expert", "years": 8},
                {"name": "Mécanique de base", "level": "avancé", "years": 6},
                {"name": "Sécurité routière", "level": "expert", "years": 8}
            ],
            "sectors": ["Transport", "Logistique"],
            "years_of_experience": 8,
            "education_level": "CAP/BEP",
            "certifications": ["Permis EC", "FIMO/FCO"],
            "languages": ["Français"]
        }
    }
]


async def create_seed_data():
    """Fonction principale de création des données"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    
    print("🚀 Début de la création des données de test...")
    
    try:
        # 1. Créer les utilisateurs entreprises et leurs profils
        print("\n1️⃣ Création des entreprises...")
        company_users = []
        
        for i, company_data in enumerate(COMPANIES):
            user_id = str(uuid4())
            username = f"company_{i+1}"
            
            # Créer l'utilisateur entreprise
            user = {
                "id": user_id,
                "username": username,
                "email": f"{username}@{company_data['name'].lower().replace(' ', '')}.ga",
                "full_name": company_data['name'],
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaISpJ8xKWO",  # Password123!
                "roles": ["company"],
                "status": "active",
                "is_collaborator": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            await db.users.insert_one(user)
            
            # Créer le profil entreprise
            company_profile = {
                "user_id": user_id,
                "company_name": company_data['name'],
                "siret": company_data['siret'],
                "nif": company_data['nif'],
                "sector": company_data['sector'],
                "company_size": company_data['size'],
                "description": company_data['description'],
                "address": company_data['address'],
                "phone": f"+241 01 {10+i:02d} {20+i:02d} {30+i:02d}",
                "website": f"https://www.{company_data['name'].lower().replace(' ', '')}.ga",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.company_profiles.insert_one(company_profile)
            company_users.append({"user_id": user_id, "company_name": company_data['name']})
            
            print(f"   ✅ Entreprise créée: {company_data['name']} ({username})")
        
        # 2. Créer les besoins
        print("\n2️⃣ Création des besoins entreprises...")
        for besoin_data in BESOINS:
            company = company_users[besoin_data['company_index']]
            
            besoin = {
                "id": str(uuid4()),
                "company_id": company['user_id'],
                "company_name": company['company_name'],
                "title": besoin_data['title'],
                "description": besoin_data['description'],
                "job_type": besoin_data['job_type'],
                "positions": besoin_data['positions'],
                "required_skills": besoin_data['required_skills'],
                "experience_required": besoin_data['experience_required'],
                "education_level": besoin_data['education_level'],
                "salary_range": besoin_data['salary_range'],
                "contract_type": besoin_data['contract_type'],
                "work_schedule": besoin_data['work_schedule'],
                "status": "open",
                "urgency": besoin_data['urgency'],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.company_needs.insert_one(besoin)
            print(f"   ✅ Besoin créé: {besoin_data['title']} - {company['company_name']}")
        
        print(f"\n   📊 Total besoins créés: {len(BESOINS)}")
        
        # 3. Créer les missions JLC
        print("\n3️⃣ Création des missions JLC...")
        for mission_data in MISSIONS_JLC:
            start_date = datetime.now(timezone.utc) + timedelta(days=mission_data['start_date_days'])
            end_date = start_date + timedelta(days=mission_data['duration_months'] * 30)
            
            mission = {
                "id": str(uuid4()),
                "title": mission_data['title'],
                "description": mission_data['description'],
                "job_type": mission_data['job_type'],
                "location": mission_data['location'],
                "positions_available": mission_data['positions'],
                "required_skills": mission_data['required_skills'],
                "experience_required": mission_data['experience_required'],
                "education_level": mission_data['education_level'],
                "salary_range": mission_data['salary_range'],
                "start_date": start_date,
                "end_date": end_date,
                "status": "published",
                "created_by": "admin",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            await db.missions.insert_one(mission)
            print(f"   ✅ Mission créée: {mission_data['title']}")
        
        print(f"\n   📊 Total missions créées: {len(MISSIONS_JLC)}")
        
        # 4. Créer les profils candidats
        print("\n4️⃣ Création des profils candidats...")
        for candidat_data in CANDIDATS_PROFILES:
            user_id = str(uuid4())
            
            # Créer l'utilisateur
            user = {
                "id": user_id,
                "username": candidat_data['username'],
                "email": candidat_data['email'],
                "full_name": candidat_data['full_name'],
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaISpJ8xKWO",  # Password123!
                "roles": ["candidat", "intérimaire"],
                "status": "active",
                "is_collaborator": False,
                "phone": candidat_data['phone'],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            await db.users.insert_one(user)
            
            # Créer le profil intérimaire
            profile = candidat_data['profile']
            interim_profile = {
                "user_id": user_id,
                "skills": profile['skills'],
                "sectors": profile['sectors'],
                "years_of_experience": profile['years_of_experience'],
                "education_level": profile['education_level'],
                "certifications": profile['certifications'],
                "languages": profile['languages'],
                "availability": "immediate",
                "preferred_locations": ["Libreville", "Port-Gentil"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.interim_profiles.insert_one(interim_profile)
            print(f"   ✅ Candidat créé: {candidat_data['full_name']} ({candidat_data['username']})")
        
        print(f"\n   📊 Total candidats créés: {len(CANDIDATS_PROFILES)}")
        
        # 5. Créer quelques candidatures pour tester la timeline
        print("\n5️⃣ Création de candidatures de test...")
        missions = await db.missions.find({}, {"_id": 0}).to_list(length=None)
        users = await db.users.find({"roles": {"$in": ["candidat", "intérimaire"]}}, {"_id": 0}).to_list(length=None)
        
        # Créer 3-5 candidatures par utilisateur
        application_count = 0
        for user in users[:5]:  # Seulement les 5 premiers pour commencer
            user_missions = missions[:3]  # 3 premières missions
            
            for mission in user_missions:
                app_id = str(uuid4())
                created_at = datetime.now(timezone.utc) - timedelta(days=15)
                
                application = {
                    "id": app_id,
                    "user_id": user['id'],
                    "mission_id": mission['id'],
                    "mission_title": mission['title'],
                    "status": "under_review",  # Statut varié
                    "additional_info": "Très motivé(e) pour cette mission",
                    "created_at": created_at,
                    "updated_at": datetime.now(timezone.utc)
                }
                
                await db.applications.insert_one(application)
                application_count += 1
        
        print(f"   📊 Total candidatures créées: {application_count}")
        
        print("\n✨ Données de test créées avec succès!")
        print("\n📋 RÉCAPITULATIF:")
        print(f"   - Entreprises: {len(COMPANIES)}")
        print(f"   - Besoins: {len(BESOINS)}")
        print(f"   - Missions JLC: {len(MISSIONS_JLC)}")
        print(f"   - Candidats: {len(CANDIDATS_PROFILES)}")
        print(f"   - Candidatures: {application_count}")
        
        print("\n🔑 CREDENTIALS DE TEST:")
        print("\n   Entreprises:")
        for i in range(len(COMPANIES)):
            print(f"      - company_{i+1} / Password123!")
        
        print("\n   Candidats:")
        for candidat in CANDIDATS_PROFILES:
            print(f"      - {candidat['username']} / Password123!")
        
        print("\n✅ Vous pouvez maintenant tester le matching et la timeline!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des données: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(create_seed_data())
