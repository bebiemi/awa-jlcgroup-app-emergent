"""
Initialize Phase 2 Configuration
Script to initialize app_config collection with default values
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from awana_auth.services.config_service import init_default_configs
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main initialization function"""
    # Get MongoDB URL from environment
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client.auth_db
    
    try:
        logger.info("🚀 Starting Phase 2 configuration initialization...")
        
        # Initialize default configs
        initialized = await init_default_configs(db)
        
        logger.info(f"✅ Initialized {initialized} configurations")
        logger.info("✅ Phase 2 configuration initialization complete!")
        
        # Display initialized configs
        configs = await db.app_config.find({}, {"_id": 0, "key": 1, "category": 1}).to_list(length=100)
        logger.info("\n📋 Available configurations:")
        for config in configs:
            logger.info(f"  - {config['key']} ({config['category']})")
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
