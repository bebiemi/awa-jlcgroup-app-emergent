"""
Country Configuration Routes
Manages countries, currencies, and cities for application configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

from awana_auth.core.dependencies import get_database
from awana_auth.dependencies.permission_dependencies import require_permission
from awana_auth.core.iam_constants import IAMPermissions

router = APIRouter()


# ==================== MODELS ====================

class Country(BaseModel):
    """Country configuration model"""
    id: str
    name: str
    iso_code: str  # ISO 3166-1 alpha-2 (ex: GA, FR)
    phone_prefix: str  # ex: +241, +33
    currency_code: str  # ex: XAF, EUR
    currency_symbol: str  # ex: FCFA, €
    active: bool = True
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CountryCreate(BaseModel):
    """Create country model"""
    name: str = Field(..., min_length=2, max_length=100)
    iso_code: str = Field(..., min_length=2, max_length=2)
    phone_prefix: str = Field(..., pattern=r'^\+\d+$')
    currency_code: str = Field(..., min_length=3, max_length=3)
    currency_symbol: str = Field(..., min_length=1, max_length=10)
    active: bool = True


class CountryUpdate(BaseModel):
    """Update country model"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_prefix: Optional[str] = Field(None, pattern=r'^\+\d+$')
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
    currency_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    active: Optional[bool] = None


class City(BaseModel):
    """City model"""
    id: str
    country_id: str
    name: str
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CityCreate(BaseModel):
    """Create city model"""
    name: str = Field(..., min_length=2, max_length=100)
    active: bool = True


# ==================== DEFAULT DATA ====================

DEFAULT_COUNTRIES = [
    {
        "name": "Gabon",
        "iso_code": "GA",
        "phone_prefix": "+241",
        "currency_code": "XAF",
        "currency_symbol": "FCFA",
        "active": True,
        "is_default": True
    },
    {
        "name": "France",
        "iso_code": "FR",
        "phone_prefix": "+33",
        "currency_code": "EUR",
        "currency_symbol": "€",
        "active": True,
        "is_default": False
    },
    {
        "name": "Cameroun",
        "iso_code": "CM",
        "phone_prefix": "+237",
        "currency_code": "XAF",
        "currency_symbol": "FCFA",
        "active": True,
        "is_default": False
    },
    {
        "name": "Congo",
        "iso_code": "CG",
        "phone_prefix": "+242",
        "currency_code": "XAF",
        "currency_symbol": "FCFA",
        "active": True,
        "is_default": False
    }
]


# ==================== COUNTRY ROUTES ====================

@router.get("", response_model=List[Country])
async def get_countries(
    active_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all countries (public endpoint)"""
    query = {}
    if active_only:
        query["active"] = True
    
    countries = await db.countries.find(query, {"_id": 0}).sort("name", 1).to_list(length=None)
    return [Country(**country) for country in countries]


@router.get("/{country_id}", response_model=Country)
async def get_country(
    country_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific country by ID"""
    country = await db.countries.find_one({"id": country_id}, {"_id": 0})
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    return Country(**country)


@router.post("/init-default")
async def init_default_countries(
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Initialize default countries if none exist"""
    # Check if countries already exist
    count = await db.countries.count_documents({})
    
    if count > 0:
        return {
            "message": "Countries already initialized",
            "count": count
        }
    
    # Insert default countries
    now = datetime.now(timezone.utc).isoformat()
    countries_to_insert = []
    
    for country_data in DEFAULT_COUNTRIES:
        country_id = str(uuid.uuid4())
        countries_to_insert.append({
            "id": country_id,
            **country_data,
            "created_at": now,
            "updated_at": now
        })
    
    await db.countries.insert_many(countries_to_insert)
    
    return {
        "message": f"Successfully initialized {len(countries_to_insert)} countries",
        "count": len(countries_to_insert)
    }


@router.post("", response_model=Country)
async def create_country(
    country: CountryCreate,
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new country (admin only)"""
    # Check if country with same ISO code already exists
    existing = await db.countries.find_one({"iso_code": country.iso_code.upper()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Country with ISO code {country.iso_code} already exists"
        )
    
    now = datetime.now(timezone.utc).isoformat()
    country_id = str(uuid.uuid4())
    
    country_doc = {
        "id": country_id,
        **country.dict(),
        "iso_code": country.iso_code.upper(),
        "is_default": False,
        "created_at": now,
        "updated_at": now
    }
    
    await db.countries.insert_one(country_doc)
    del country_doc["_id"] if "_id" in country_doc else None
    
    return Country(**country_doc)


@router.patch("/{country_id}", response_model=Country)
async def update_country(
    country_id: str,
    country_update: CountryUpdate,
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update country (admin only)"""
    # Check if country exists
    existing = await db.countries.find_one({"id": country_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    # Prepare update data
    update_data = {k: v for k, v in country_update.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.countries.update_one(
        {"id": country_id},
        {"$set": update_data}
    )
    
    updated = await db.countries.find_one({"id": country_id}, {"_id": 0})
    return Country(**updated)


@router.patch("/{country_id}/set-default")
async def set_default_country(
    country_id: str,
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Set a country as default (admin only)"""
    # Check if country exists
    country = await db.countries.find_one({"id": country_id})
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    # Remove default flag from all countries
    await db.countries.update_many(
        {},
        {"$set": {"is_default": False}}
    )
    
    # Set this country as default
    await db.countries.update_one(
        {"id": country_id},
        {"$set": {"is_default": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "message": f"Country {country['name']} set as default",
        "country_id": country_id
    }


@router.delete("/{country_id}")
async def delete_country(
    country_id: str,
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete country (admin only)"""
    # Check if country is default
    country = await db.countries.find_one({"id": country_id})
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    if country.get("is_default"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default country. Set another country as default first."
        )
    
    # Check if country has cities
    cities_count = await db.cities.count_documents({"country_id": country_id})
    if cities_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete country with {cities_count} cities. Delete cities first."
        )
    
    result = await db.countries.delete_one({"id": country_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    return {"message": "Country deleted successfully"}


# ==================== CITY ROUTES ====================

@router.get("/{country_id}/cities", response_model=List[City])
async def get_cities(
    country_id: str,
    search: Optional[str] = None,
    active_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get cities for a country"""
    query = {"country_id": country_id}
    
    if active_only:
        query["active"] = True
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    cities = await db.cities.find(query, {"_id": 0}).sort("name", 1).to_list(length=None)
    return [City(**city) for city in cities]


@router.post("/{country_id}/cities", response_model=City)
async def create_city(
    country_id: str,
    city: CityCreate,
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new city for a country (admin only)"""
    # Check if country exists
    country = await db.countries.find_one({"id": country_id})
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
    
    # Check if city already exists for this country
    existing = await db.cities.find_one({
        "country_id": country_id,
        "name": {"$regex": f"^{city.name}$", "$options": "i"}
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"City {city.name} already exists for this country"
        )
    
    now = datetime.now(timezone.utc).isoformat()
    city_id = str(uuid.uuid4())
    
    city_doc = {
        "id": city_id,
        "country_id": country_id,
        **city.dict(),
        "created_at": now,
        "updated_at": now
    }
    
    await db.cities.insert_one(city_doc)
    del city_doc["_id"] if "_id" in city_doc else None
    
    return City(**city_doc)


@router.delete("/cities/{city_id}")
async def delete_city(
    city_id: str,
    current_user: dict = Depends(require_permission(IAMPermissions.USERS_MANAGE)),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete city (admin only)"""
    result = await db.cities.delete_one({"id": city_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    return {"message": "City deleted successfully"}
