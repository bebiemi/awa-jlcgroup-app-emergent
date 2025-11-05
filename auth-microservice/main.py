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
    
    yield
    
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
app.include_router(mission_router)
app.include_router(document_router)
app.include_router(configuration_router, prefix="/api/auth")
app.include_router(version_router)
app.include_router(feature_flag_router)
app.include_router(role_visibility_router)

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
