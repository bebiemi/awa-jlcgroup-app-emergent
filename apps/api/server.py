"""JLC API Main Server"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
from pathlib import Path

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database client
client = None
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global client, db
    logger.info("Starting JLC API...")

    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv('DATABASE_NAME', 'jlc_db')
    db = client[db_name]
    app.state.db = db
    logger.info(f"Connected to MongoDB: {db_name}")

    # Ensure indexes
    await db.profiles.create_index("user_id", unique=True)
    await db.account_validations.create_index("user_id")
    await db.account_validations.create_index("status")
    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("is_read", 1)])
    await db.audit_trail.create_index("entity_id")
    await db.audit_trail.create_index("user_id")
    logger.info("Database indexes created")

    # Create upload directory
    upload_dir = Path(os.getenv('UPLOAD_DIR', '/app/uploads'))
    upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory ready: {upload_dir}")

    yield

    # Cleanup
    if client:
        client.close()
        logger.info("MongoDB connection closed")


app = FastAPI(
    title="JLC API",
    description="JLC Group Interim Management API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
upload_dir = Path(os.getenv('UPLOAD_DIR', '/app/uploads'))
if upload_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# Import and include routers
from src.presentation.routes import profile_routes, validation_routes, notification_routes, admin_routes, iam_proxy_routes, config_proxy_routes, security_proxy_routes, auth_api_proxy_routes, auth_proxy_routes, besoins_proxy_routes, entreprises_proxy_routes, auth_endpoints_proxy, email_verification_proxy_routes, auth_admin_users_proxy, admin_users_proxy, documents_proxy_routes

# ⚠️ IMPORTANT: Proxy routes MUST be mounted BEFORE local routes to avoid conflicts
# Proxy Admin Users routes (most specific - must be first)
app.include_router(admin_users_proxy.router, prefix="/api/admin/users", tags=["Admin Users Proxy"])
# Proxy Auth Admin Users routes (must be before general auth routes for specificity)
app.include_router(auth_admin_users_proxy.router, prefix="/api/auth/admin/users", tags=["Auth Admin Users Proxy"])
# Proxy Auth routes to auth-microservice
app.include_router(auth_proxy_routes.router, prefix="/api/auth", tags=["Auth Proxy"])
# Proxy Users and Profiles routes to auth-microservice (includes /profiles/me)
app.include_router(auth_endpoints_proxy.router, prefix="/api", tags=["Auth Endpoints Proxy"])

# Local backend routes (mounted after proxies to avoid conflicts)
# DISABLED: profile_routes conflicts with auth_endpoints_proxy which handles ALL /profiles/* routes
# app.include_router(profile_routes.router, prefix="/api")
app.include_router(validation_routes.router, prefix="/api")
app.include_router(notification_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")
# Proxy IAM routes to auth-microservice
app.include_router(iam_proxy_routes.router, prefix="/api/iam", tags=["IAM Proxy"])
# Proxy Config routes to auth-microservice
app.include_router(config_proxy_routes.router, prefix="/api/config", tags=["Config Proxy"])
# Proxy Security routes to auth-microservice
app.include_router(security_proxy_routes.router, prefix="/api", tags=["Security Proxy"])
# Proxy /auth-api to auth-microservice /api (for frontend compatibility)
app.include_router(auth_api_proxy_routes.router, prefix="/auth-api", tags=["Auth API Proxy"])
# Proxy /api/besoins to auth-microservice
app.include_router(besoins_proxy_routes.router, prefix="/api/besoins", tags=["Besoins Proxy"])
# Proxy /api/entreprises to auth-microservice
app.include_router(entreprises_proxy_routes.router, prefix="/api/entreprises", tags=["Entreprises Proxy"])
# Proxy /api/email-verification to auth-microservice
app.include_router(email_verification_proxy_routes.router, prefix="/api/email-verification", tags=["Email Verification Proxy"])
# Proxy /api/documents and /api/support to auth-microservice
app.include_router(documents_proxy_routes.router, prefix="/api", tags=["Documents & Support Proxy"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "jlc-api",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def api_health():
    """Health check endpoint under /api path (for production routing)"""
    return {
        "status": "healthy",
        "service": "jlc-api",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "JLC API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
