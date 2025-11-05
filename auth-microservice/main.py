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
from rate_limit import limiter

client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    logger.info("Starting AWANA Auth Microservice...")
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DATABASE_NAME', 'auth_db')]
    logger.info(f"Connected to MongoDB: {os.getenv('DATABASE_NAME')}")
    
    from awana_auth.rbac.manager import RBACManager
    rbac_manager = RBACManager(db)
    await rbac_manager.initialize_default_roles()
    logger.info("AWANA Auth initialized")
    
    yield
    
    if client:
        client.close()

app = FastAPI(
    title="AWANA Auth Microservice",
    description="Standalone Auth with JWT, OAuth2, RBAC",
    version="1.0.0",
    lifespan=lifespan
)

allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "awana-auth", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"service": "AWANA Auth", "docs": "/docs", "health": "/health"}
