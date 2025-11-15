"""
Initialize Feature Flags
Creates feature flags for all current and future features
All new features are admin-only by default
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from uuid import uuid4

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


# Define feature flags - All new features start as admin-only
FEATURE_FLAGS = [
    # ==================== EXISTING FEATURES ====================
    {
        "key": "feature.dashboard.unified",
        "name": "Dashboard Unifié",
        "description": "Nouveau dashboard avec widgets personnalisables",
        "type": "ROLE",
        "enabled": True,
        "target": ["admin"],  # Admin only initially
        "metadata": {"version": "1.0", "release_date": "2025-01-15"}
    },
    {
        "key": "feature.profile.postulant",
        "name": "Dashboard Postulant",
        "description": "Dashboard guidé pour les candidats en phase de complétion",
        "type": "ROLE",
        "enabled": True,
        "target": ["candidat", "postulant"],
        "metadata": {"version": "1.0", "phase": "production"}
    },
    {
        "key": "feature.entreprises.management",
        "name": "Gestion Entreprises",
        "description": "Page de gestion des entreprises avec édition inline",
        "type": "ROLE",
        "enabled": True,
        "target": ["admin", "commercial"],
        "metadata": {"version": "1.0"}
    },
    
    # ==================== UPCOMING FEATURES (Admin Only) ====================
    {
        "key": "feature.ai.matching",
        "name": "Matching IA Missions",
        "description": "Matching automatique intérimaires-missions via IA",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],  # Admin only for testing
        "metadata": {"requires": ["openai_key", "matching_algorithm"], "phase": "development"}
    },
    {
        "key": "feature.cv.auto_generate",
        "name": "Génération Automatique CV",
        "description": "Générer des CV au format PDF/PNG/JPG à partir du profil",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"formats": ["pdf", "png", "jpg"], "phase": "planning"}
    },
    {
        "key": "feature.chat.messaging",
        "name": "Système de Chat",
        "description": "Messagerie instantanée entre utilisateurs",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"requires": ["websocket_server"], "phase": "planning"}
    },
    {
        "key": "feature.notifications.realtime",
        "name": "Notifications Temps Réel",
        "description": "Notifications push en temps réel via WebSockets",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"requires": ["websocket_server"], "phase": "planning"}
    },
    {
        "key": "feature.pointage.electronic",
        "name": "Pointage Électronique",
        "description": "Système de pointage pour intérimaires (mobile + web)",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"requires": ["geolocation", "mobile_app"], "phase": "planning"}
    },
    {
        "key": "feature.signature.electronic",
        "name": "Signature Électronique",
        "description": "Signature de contrats et documents en ligne",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"requires": ["signature_provider"], "phase": "planning"}
    },
    {
        "key": "feature.gamification",
        "name": "Gamification Intérimaires",
        "description": "Système de points, badges et récompenses",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"phase": "planning"}
    },
    {
        "key": "feature.geography.v2",
        "name": "Gestion Géographique V2",
        "description": "Gestion provinces, districts et quartiers",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"phase": "planning"}
    },
    {
        "key": "feature.validation.email",
        "name": "Validation Email Obligatoire",
        "description": "Forcer la validation d'email pour les postulants",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"applies_to": ["candidat", "postulant"], "phase": "development"}
    },
    {
        "key": "feature.documents.advanced",
        "name": "Gestion Documents Avancée",
        "description": "Catégorisation, rappels d'expiration, OCR",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"phase": "planning"}
    },
    {
        "key": "feature.reports.advanced",
        "name": "Rapports Avancés",
        "description": "Rapports personnalisables avec exports multiples",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin", "commercial"],
        "metadata": {"formats": ["pdf", "excel", "csv"], "phase": "planning"}
    },
    {
        "key": "feature.timesheet.validation",
        "name": "Validation Feuilles de Temps",
        "description": "Workflow de validation des feuilles de temps",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin", "commercial"],
        "metadata": {"phase": "planning"}
    },
    
    # ==================== EXPERIMENTAL FEATURES ====================
    {
        "key": "feature.ai.recommendations",
        "name": "Recommandations IA",
        "description": "Suggestions intelligentes de missions pour intérimaires",
        "type": "ROLE",
        "enabled": False,
        "target": ["admin"],
        "metadata": {"experimental": True, "requires": ["ai_model"]}
    },
    {
        "key": "feature.mobile.app",
        "name": "Application Mobile",
        "description": "Activer les fonctionnalités mobile",
        "type": "GLOBAL",
        "enabled": False,
        "target": None,
        "metadata": {"platforms": ["ios", "android"], "phase": "planning"}
    },
    {
        "key": "feature.api.public",
        "name": "API Publique",
        "description": "Endpoints API publics pour intégrations externes",
        "type": "GLOBAL",
        "enabled": False,
        "target": None,
        "metadata": {"requires": ["api_keys_management"], "phase": "planning"}
    },
    
    # ==================== ADMIN TOOLS ====================
    {
        "key": "feature.admin.audit_logs",
        "name": "Logs d'Audit Détaillés",
        "description": "Historique complet des actions administratives",
        "type": "ROLE",
        "enabled": True,
        "target": ["admin"],
        "metadata": {"retention_days": 365}
    },
    {
        "key": "feature.admin.system_health",
        "name": "Monitoring Système",
        "description": "Tableau de bord de santé du système",
        "type": "ROLE",
        "enabled": True,
        "target": ["admin"],
        "metadata": {"metrics": ["cpu", "memory", "disk", "api_latency"]}
    },
    {
        "key": "feature.admin.data_export",
        "name": "Export Données Massif",
        "description": "Exporter toutes les données en masse",
        "type": "ROLE",
        "enabled": True,
        "target": ["admin"],
        "metadata": {"formats": ["json", "csv", "sql"]}
    },
]


async def init_feature_flags():
    """Initialize feature flags"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    collection = db.feature_flags
    
    now = datetime.now(timezone.utc)
    stats = {"created": 0, "updated": 0, "unchanged": 0}
    
    print("🚩 Initializing Feature Flags...\n")
    
    for flag_data in FEATURE_FLAGS:
        key = flag_data["key"]
        
        # Check if flag already exists
        existing = await collection.find_one({"key": key})
        
        flag_doc = {
            "id": existing.get("id", str(uuid4())) if existing else str(uuid4()),
            "key": flag_data["key"],
            "name": flag_data["name"],
            "description": flag_data["description"],
            "type": flag_data["type"],
            "enabled": existing.get("enabled", flag_data["enabled"]) if existing else flag_data["enabled"],
            "target": flag_data.get("target"),
            "metadata": flag_data.get("metadata", {}),
            "created_at": existing.get("created_at", now) if existing else now,
            "updated_at": now,
        }
        
        if existing:
            # Check if update is needed (only description and metadata)
            needs_update = (
                existing.get("description") != flag_doc["description"] or
                existing.get("name") != flag_doc["name"] or
                existing.get("metadata") != flag_doc["metadata"]
            )
            
            if needs_update:
                # Don't update enabled status or target if already set
                update_doc = {k: v for k, v in flag_doc.items() if k not in ["enabled", "target"]}
                await collection.update_one(
                    {"id": flag_doc["id"]},
                    {"$set": update_doc}
                )
                status_icon = "🔄"
                stats["updated"] += 1
            else:
                status_icon = "✓"
                stats["unchanged"] += 1
        else:
            await collection.insert_one(flag_doc)
            status_icon = "✅"
            stats["created"] += 1
        
        enabled_icon = "🟢" if flag_doc["enabled"] else "🔴"
        type_icon = "🌐" if flag_data["type"] == "GLOBAL" else "👥"
        target_str = f" [{', '.join(flag_data.get('target', []))}]" if flag_data.get('target') else ""
        
        print(f"{status_icon} {type_icon} {enabled_icon} {flag_data['name']}{target_str}")
    
    print(f"\n✅ Feature flags initialization complete!")
    print(f"   - Created: {stats['created']} flags")
    print(f"   - Updated: {stats['updated']} flags")
    print(f"   - Unchanged: {stats['unchanged']} flags")
    print(f"   - Total: {len(FEATURE_FLAGS)} flags")
    
    # Stats
    enabled_count = sum(1 for f in FEATURE_FLAGS if f["enabled"])
    admin_only_count = sum(1 for f in FEATURE_FLAGS if f.get("target") == ["admin"])
    
    print(f"\n📊 Statistics:")
    print(f"   - Enabled: {enabled_count}")
    print(f"   - Disabled: {len(FEATURE_FLAGS) - enabled_count}")
    print(f"   - Admin Only: {admin_only_count}")
    print(f"   - Global: {sum(1 for f in FEATURE_FLAGS if f['type'] == 'GLOBAL')}")
    print(f"   - Role-based: {sum(1 for f in FEATURE_FLAGS if f['type'] == 'ROLE')}")
    
    print(f"\n💡 Note: All new features are admin-only by default for safe rollout")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(init_feature_flags())
