"""Seed data for JLC application"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from src.domain.entities.profile import (
    Profile, ProfileType, AgencyProfile, CompanyProfile, InterimProfile
)
from src.domain.entities.validation import (
    AccountValidation, ValidationStatus, ValidationType
)
from src.domain.entities.notification import (
    Notification, NotificationChannel, NotificationPriority
)
from datetime import datetime

load_dotenv()


async def seed_database():
    """Seed database with demo data"""
    print("🌱 Seeding database...")

    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DATABASE_NAME', 'jlc_db')]

    # Clear existing data
    print("Clearing existing data...")
    await db.profiles.delete_many({})
    await db.account_validations.delete_many({})
    await db.notifications.delete_many({})
    print("✅ Existing data cleared")

    # Note: Users are created by auth-microservice, we'll use fake user IDs
    # In real scenario, these would be actual user IDs from auth service

    # Seed Profiles
    print("\n📋 Seeding profiles...")

    profiles_data = [
        # Admin (no validation needed)
        Profile(
            id="profile-admin-001",
            user_id="user-admin-001",
            profile_type=ProfileType.ADMIN,
            first_name="Jean",
            last_name="Administrateur",
            phone="+33 1 23 45 67 89",
            avatar_url=None
        ),
        
        # Agency (validated)
        Profile(
            id="profile-agency-001",
            user_id="user-agency-001",
            profile_type=ProfileType.AGENCY,
            first_name="Marie",
            last_name="Dupont",
            phone="+33 1 98 76 54 32",
            avatar_url=None,
            agency_data=AgencyProfile(
                agency_name="Awana Recrutement",
                agency_code="AWN-001",
                address="123 Avenue des Champs-Élysées, 75008 Paris",
                description="Agence de recrutement spécialisée dans l'intérim"
            )
        ),
        
        # Company (validated)
        Profile(
            id="profile-company-001",
            user_id="user-company-001",
            profile_type=ProfileType.COMPANY,
            first_name="Pierre",
            last_name="Martin",
            phone="+33 1 55 66 77 88",
            avatar_url=None,
            company_data=CompanyProfile(
                company_name="Tech Solutions SARL",
                registration_number="12345678901234",  # SIRET
                address="45 Rue de la Innovation, 69001 Lyon",
                industry="Technologies de l'information",
                company_size="50-200 employés",
                website="https://techsolutions.fr"
            )
        ),
        
        # Company (pending validation)
        Profile(
            id="profile-company-002",
            user_id="user-company-002",
            profile_type=ProfileType.COMPANY,
            first_name="Sophie",
            last_name="Bernard",
            phone="+33 4 11 22 33 44",
            avatar_url=None,
            company_data=CompanyProfile(
                company_name="Build Pro Construction",
                registration_number="98765432109876",
                address="78 Boulevard du Bâtiment, 13001 Marseille",
                industry="Construction",
                company_size="10-50 employés"
            )
        ),
        
        # Interim (validated, profile complete)
        Profile(
            id="profile-interim-001",
            user_id="user-interim-001",
            profile_type=ProfileType.INTERIM,
            first_name="Thomas",
            last_name="Leroy",
            phone="+33 6 12 34 56 78",
            avatar_url=None,
            interim_data=InterimProfile(
                skills=["JavaScript", "React", "Node.js", "Python", "FastAPI"],
                experience_years=5,
                resume_url=None,
                availability="Disponible immédiatement",
                bio="Développeur full-stack passionné avec 5 ans d'expérience",
                certifications=["AWS Certified Developer", "Scrum Master"]
            )
        ),
        
        # Interim (pending validation, profile incomplete)
        Profile(
            id="profile-interim-002",
            user_id="user-interim-002",
            profile_type=ProfileType.INTERIM,
            first_name="Emma",
            last_name="Dubois",
            phone="+33 7 98 76 54 32",
            avatar_url=None,
            interim_data=InterimProfile(
                skills=["Comptabilité", "Excel", "SAP"],
                experience_years=3,
                availability="À partir du 1er mars",
                bio="Assistante comptable avec expérience en PME"
            )
        )
    ]

    for profile in profiles_data:
        profile_dict = profile.dict()
        profile_dict['created_at'] = profile.created_at.isoformat()
        profile_dict['updated_at'] = profile.updated_at.isoformat()
        await db.profiles.insert_one(profile_dict)
        print(f"  ✅ Created profile: {profile.first_name} {profile.last_name} ({profile.profile_type.value})")

    # Seed Validations
    print("\n✅ Seeding validations...")

    validations_data = [
        # Company pending
        AccountValidation(
            id="validation-001",
            user_id="user-company-002",
            user_email="sophie.bernard@buildpro.fr",
            user_name="Sophie Bernard",
            validation_type=ValidationType.COMPANY,
            status=ValidationStatus.PENDING
        ),
        
        # Interim pending
        AccountValidation(
            id="validation-002",
            user_id="user-interim-002",
            user_email="emma.dubois@email.fr",
            user_name="Emma Dubois",
            validation_type=ValidationType.INTERIM,
            status=ValidationStatus.PENDING
        ),
        
        # Company approved
        AccountValidation(
            id="validation-003",
            user_id="user-company-001",
            user_email="pierre.martin@techsolutions.fr",
            user_name="Pierre Martin",
            validation_type=ValidationType.COMPANY,
            status=ValidationStatus.APPROVED,
            comment="Dossier complet, société vérifiée",
            reviewed_by="user-admin-001",
            reviewed_by_email="admin@jlcgroup.com",
            reviewed_at=datetime.utcnow()
        ),
        
        # Interim approved
        AccountValidation(
            id="validation-004",
            user_id="user-interim-001",
            user_email="thomas.leroy@email.fr",
            user_name="Thomas Leroy",
            validation_type=ValidationType.INTERIM,
            status=ValidationStatus.APPROVED,
            comment="Profil excellent, CV complet",
            reviewed_by="user-admin-001",
            reviewed_by_email="admin@jlcgroup.com",
            reviewed_at=datetime.utcnow()
        )
    ]

    for validation in validations_data:
        validation_dict = validation.dict()
        validation_dict['created_at'] = validation.created_at.isoformat()
        validation_dict['updated_at'] = validation.updated_at.isoformat()
        if validation.reviewed_at:
            validation_dict['reviewed_at'] = validation.reviewed_at.isoformat()
        await db.account_validations.insert_one(validation_dict)
        print(f"  ✅ Created validation: {validation.user_name} ({validation.validation_type.value} - {validation.status.value})")

    # Seed Notifications
    print("\n🔔 Seeding notifications...")

    notifications_data = [
        # For interim user 1 (validated)
        Notification(
            user_id="user-interim-001",
            channel=NotificationChannel.INAPP,
            title="Bienvenue sur JLC Group! 🎉",
            body="Votre compte a été validé. Vous pouvez maintenant postuler aux missions.",
            priority=NotificationPriority.HIGH,
            action_url="/missions"
        ),
        Notification(
            user_id="user-interim-001",
            channel=NotificationChannel.INAPP,
            title="Complétez votre profil",
            body="Pensez à ajouter votre CV pour maximiser vos chances!",
            priority=NotificationPriority.NORMAL,
            action_url="/profile"
        ),
        Notification(
            user_id="user-interim-001",
            channel=NotificationChannel.INAPP,
            title="Nouvelle mission disponible",
            body="Une mission de développeur React vient d'être publiée près de chez vous!",
            priority=NotificationPriority.NORMAL,
            action_url="/missions/123",
            is_read=True
        ),
        
        # For interim user 2 (pending)
        Notification(
            user_id="user-interim-002",
            channel=NotificationChannel.INAPP,
            title="Demande en cours de traitement",
            body="Votre demande d'inscription est en cours de vérification par notre équipe.",
            priority=NotificationPriority.NORMAL
        ),
        Notification(
            user_id="user-interim-002",
            channel=NotificationChannel.INAPP,
            title="Complétez votre profil",
            body="Ajoutez votre CV et vos certifications pour accélérer la validation.",
            priority=NotificationPriority.HIGH,
            action_url="/profile"
        ),
        
        # For company user 1 (validated)
        Notification(
            user_id="user-company-001",
            channel=NotificationChannel.INAPP,
            title="Compte entreprise activé ✅",
            body="Vous pouvez maintenant publier vos offres de mission.",
            priority=NotificationPriority.HIGH,
            action_url="/missions/create"
        ),
        Notification(
            user_id="user-company-001",
            channel=NotificationChannel.INAPP,
            title="3 candidatures reçues",
            body="Vous avez reçu 3 nouvelles candidatures pour votre mission développeur.",
            priority=NotificationPriority.NORMAL,
            action_url="/candidatures",
            is_read=True
        ),
        
        # For company user 2 (pending)
        Notification(
            user_id="user-company-002",
            channel=NotificationChannel.INAPP,
            title="Documents requis",
            body="Veuillez fournir votre KBIS et attestation URSSAF pour validation.",
            priority=NotificationPriority.URGENT,
            action_url="/profile"
        ),
        
        # For admin
        Notification(
            user_id="user-admin-001",
            channel=NotificationChannel.INAPP,
            title="2 nouvelles demandes de validation",
            body="2 comptes en attente de validation (1 entreprise, 1 intérimaire).",
            priority=NotificationPriority.HIGH,
            action_url="/admin/validations"
        )
    ]

    for notification in notifications_data:
        notification_dict = notification.dict()
        notification_dict['created_at'] = notification.created_at.isoformat()
        if notification.read_at:
            notification_dict['read_at'] = notification.read_at.isoformat()
        await db.notifications.insert_one(notification_dict)
        print(f"  ✅ Created notification: {notification.title}")

    # Print summary
    print("\n" + "="*50)
    print("🎉 Database seeded successfully!")
    print("="*50)
    print("\n📊 Summary:")
    print(f"  • {len(profiles_data)} profiles created")
    print(f"  • {len(validations_data)} validations created")
    print(f"  • {len(notifications_data)} notifications created")
    print("\n👤 Test Users (IDs for reference):")
    print("  • Admin:      user-admin-001")
    print("  • Agency:     user-agency-001")
    print("  • Company 1:  user-company-001 (validated)")
    print("  • Company 2:  user-company-002 (pending)")
    print("  • Interim 1:  user-interim-001 (validated)")
    print("  • Interim 2:  user-interim-002 (pending)")
    print("\n⚠️  Note: You need to create corresponding users in auth-microservice")
    print("="*50)

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
