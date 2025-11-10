"""
Initialize default allowed email domains
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from awana_auth.services.email_domain_service import EmailDomainService


async def initialize_email_domains():
    """Initialize default email domains"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/jlc_interim')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database()
    
    print("🚀 Initializing Email Domains...")
    
    service = EmailDomainService(db)
    await service.initialize_default_domains()
    
    print("✅ Email domains initialized successfully!")
    
    # Display domains
    domains = await service.list_domains(active_only=True)
    print("\n📧 Active Email Domains:")
    for domain in domains:
        print(f"  - {domain['domain']} ({domain.get('country_code', 'N/A')})")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_email_domains())
