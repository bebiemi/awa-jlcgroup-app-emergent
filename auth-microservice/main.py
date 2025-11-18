"""AWANA Auth Microservice - Standalone Authentication Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from contextlib import asynccontextmanager

# Initialiser la configuration AVANT tout le reste
from awana_auth.core.config_manager import init_config, get_config

# Déterminer l'environnement
env = os.getenv("APP_ENV", "local")
config = init_config(env=env)

# Configuration du logging depuis la config
log_level = config.get("monitoring.logging.level", default="INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from awana_auth_routes import auth_router, users_router, roles_router
from google_auth_routes import google_router
from security_routes import security_router
from mfa_routes import mfa_router
from location_routes import location_router
from validation_routes import validation_router
from profile_routes import profile_router
from mission_routes import router as mission_router
from document_routes import router as document_router
from configuration_routes import router as configuration_router
from version_routes import router as version_router
from feature_flag_routes import router as feature_flag_router
from role_visibility_routes import router as role_visibility_router
from email_routes import router as email_router
from email_settings_routes import router as email_settings_router
from email_history_routes import router as email_history_router
from email_template_routes import router as email_template_router
from contract_routes import router as contract_router
from presence_routes import router as presence_router
from iam_routes import router as iam_router
from iam_role_assignment_routes import router as iam_role_assignment_router
from email_domain_routes import router as email_domain_router
from user_detail_routes import router as user_detail_router
from user_archive_routes import router as user_archive_router
from country_config_routes import router as country_config_router
from besoin_routes import router as besoin_router
from entreprise_routes import router as entreprise_router
from form_config_routes import router as form_config_router
from bulk_operations_routes import bulk_router
from notification_routes import router as notification_router
from app_config_routes import router as app_config_router
from email_verification_routes import router as email_verification_router
from admin_email_verification_routes import router as admin_email_verification_router
from system_references_routes import router as system_references_router
from retention_management_routes import router as retention_management_router
from retention_policies_routes import router as retention_policies_router
from iam_unified_routes import router as iam_unified_router
from professional_experiences_routes import router as professional_experiences_router
from support_routes import router as support_router
from rate_limit import limiter

client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    logger.info(f"🚀 Starting AWANA Auth Microservice (env: {env})...")
    
    # Récupérer la configuration DB depuis ConfigManager
    mongo_url = config.get_secret('MONGO_URL', required=True)
    db_name = config.get('database.name', required=True)
    pool_size = config.get('database.pool_size', default=10)
    
    logger.info(f"📊 Database config: {db_name}, pool_size={pool_size}")
    
    client = AsyncIOMotorClient(
        mongo_url,
        maxPoolSize=pool_size,
        minPoolSize=config.get('database.min_pool_size', default=5),
        socketTimeoutMS=config.get('database.socket_timeout_ms', default=30000),
        connectTimeoutMS=config.get('database.connect_timeout_ms', default=10000),
        serverSelectionTimeoutMS=config.get('database.server_selection_timeout_ms', default=5000)
    )
    db = client[db_name]
    logger.info(f"✅ Connected to MongoDB: {db_name}")
    
    from awana_auth.rbac.manager import RBACManager
    rbac_manager = RBACManager(db)
    await rbac_manager.initialize_default_roles()
    logger.info("✅ AWANA Auth initialized")
    
    # Initialiser le service email avec la base de données
    from awana_auth.services.email_service_v2 import init_email_service
    init_email_service(db)
    logger.info("✅ Email service initialized")
    
    # Initialiser les domaines email autorisés
    from awana_auth.services.email_domain_service import EmailDomainService
    email_domain_service = EmailDomainService(db)
    await email_domain_service.initialize_default_domains()
    logger.info("✅ Email domains initialized")
    
    # Initialiser les tâches de fond
    from background_jobs import setup_background_jobs
    scheduler = setup_background_jobs(db)
    logger.info("✅ Background jobs initialized")
    
    yield
    
    # Arrêter le scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("🛑 Background jobs stopped")
    
    if client:
        logger.info("🔌 Closing MongoDB connection...")
        client.close()

app = FastAPI(
    title=config.get("app.name", default="AWANA Auth Microservice"),
    description="Standalone Auth with JWT, OAuth2, RBAC",
    version=config.get("app.version", default="1.0.0"),
    debug=config.get("app.debug", default=False),
    lifespan=lifespan
)

# Configuration CORS depuis ConfigManager
cors_origins = config.get("security.cors.allow_origins", default=["http://localhost:3000"])
cors_methods = config.get("security.cors.allow_methods", default=["*"])
cors_headers = config.get("security.cors.allow_headers", default=["*"])
cors_credentials = config.get("security.cors.allow_credentials", default=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_credentials,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)

app.state.limiter = limiter
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(roles_router, prefix="/api")
app.include_router(google_router, prefix="/api")
app.include_router(security_router, prefix="/api")
app.include_router(mfa_router, prefix="/api")
app.include_router(location_router, prefix="/api")
app.include_router(validation_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(professional_experiences_router, prefix="/api")
app.include_router(mission_router)
app.include_router(document_router)
app.include_router(configuration_router, prefix="/api/auth")
app.include_router(version_router)
app.include_router(feature_flag_router)
app.include_router(role_visibility_router)
app.include_router(email_router)
app.include_router(email_settings_router)
app.include_router(email_history_router)
app.include_router(email_template_router)
app.include_router(contract_router)
app.include_router(presence_router)
app.include_router(iam_router)
app.include_router(iam_role_assignment_router)
app.include_router(email_domain_router)
app.include_router(support_router, prefix="/api")
app.include_router(user_detail_router, prefix="/api/iam/users", tags=["User Details"])
app.include_router(user_archive_router, prefix="/api/iam/users", tags=["User Archive"])
app.include_router(bulk_router, prefix="/api/admin/users", tags=["Bulk Operations"])
app.include_router(country_config_router, prefix="/api/config/countries", tags=["Country Configuration"])
app.include_router(besoin_router, prefix="/api/besoins", tags=["Besoins"])
app.include_router(entreprise_router, prefix="/api/entreprises", tags=["Entreprises"])
app.include_router(form_config_router, prefix="/api/config", tags=["Dynamic Configuration"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(app_config_router, prefix="/api", tags=["App Configuration"])
app.include_router(email_verification_router, tags=["Email Verification"])
app.include_router(admin_email_verification_router, tags=["Admin Email Verification"])
app.include_router(system_references_router)
app.include_router(retention_management_router)
app.include_router(retention_policies_router)
app.include_router(iam_unified_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": config.get("app.name"),
        "version": config.get("app.version"),
        "environment": env
    }

@app.get("/")
async def root():
    return {
        "service": config.get("app.name"),
        "version": config.get("app.version"),
        "environment": env,
        "docs": "/docs",
        "health": "/health"
    }
