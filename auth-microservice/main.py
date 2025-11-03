"""AWANA Auth Microservice - Standalone Authentication Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

load_dotenv()

from awana_auth_routes import auth_router, users_router, roles_router
from google_auth_routes import google_router
from security_routes import security_router
from mfa_routes import mfa_router
from location_routes import location_router
from validation_routes import validation_router
from rate_limit import limiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "awana-auth", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"service": "AWANA Auth", "docs": "/docs", "health": "/health"}
