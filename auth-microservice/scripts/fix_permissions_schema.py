"""
Fix permissions schema - Add missing resource/action fields
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


async def fix_permissions():
    """Fix permissions missing resource and action fields"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.auth_db
    permissions_collection = db.permissions
    
    # Find permissions without resource/action
    cursor = permissions_collection.find({
        "$or": [
            {"resource": {"$exists": False}},
            {"action": {"$exists": False}}
        ]
    })
    
    fixed_count = 0
    async for perm in cursor:
        code = perm.get("code", perm.get("name", "unknown"))
        print(f"Fixing permission: {code}")
        
        # Parse code to extract resource and action
        # Format: "resource.action" or "resource:action"
        if "." in code:
            parts = code.split(".", 1)
        elif ":" in code:
            parts = code.split(":", 1)
        else:
            # Single word - use as both resource and action
            parts = [code, "manage"]
        
        resource = parts[0] if len(parts) > 0 else "general"
        action = parts[1] if len(parts) > 1 else "manage"
        
        # Map action to valid enum values (lowercase)
        action_mapping = {
            "read": "read",
            "create": "create",
            "edit": "update",
            "update": "update",
            "delete": "delete",
            "manage": "manage",
            "configure": "configure",
            "read_own": "read_own",
            "read_all": "read",
            "read_config": "read_config",
            "read_history": "read_history",
            "manage_templates": "manage_templates",
            "dashboard": "dashboard",
        }
        
        action_value = action_mapping.get(action, "manage")
        
        # Update the permission
        update_data = {
            "resource": resource,
            "action": action_value
        }
        
        # Add scope if missing
        if "scope" not in perm:
            update_data["scope"] = "organization"
        
        result = await permissions_collection.update_one(
            {"id": perm["id"]},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            fixed_count += 1
            print(f"  ✓ Fixed: {code} -> resource={resource}, action={action_value}")
    
    print(f"\n✅ Fixed {fixed_count} permissions")
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_permissions())
