# 🔧 Configuration Dynamique - Guide Complet

## 📋 Vue d'ensemble

Ce guide transforme votre application JLC d'une configuration **statique** (données en dur) vers une configuration **dynamique** (base de données paramétrable).

### Avantages

- ✅ **Aucune modification de code** pour changer des valeurs
- ✅ **Interface admin** pour tout configurer
- ✅ **Multi-tenant** ready (configurations par organisation)
- ✅ **Historique** des modifications
- ✅ **Évolutif** : Ajouter facilement de nouveaux référentiels
- ✅ **Cache** pour les performances

---

## 🎯 Données à Dynamiser

### Actuellement en Dur (À Migrer)

| Catégorie | Exemples | Localisation Actuelle |
|-----------|----------|----------------------|
| **Rôles** | admin, interim, company | Code Python/TypeScript |
| **Statuts** | active, pending, suspended | Hardcodé |
| **Types contrats** | CDI, CDD, intérim | Frontend/Backend |
| **Pays** | Gabon, France, etc. | PhoneInput.tsx |
| **Compétences** | React, Python, etc. | Aucun référentiel |
| **Documents** | CV, contrat, certificat | Hardcodé |
| **Permissions** | create_user, edit_mission | Code |

---

## 🏗️ Architecture Proposée

### 1. Table Générique : `system_references`

Stocke tous les référentiels de manière générique.

**Structure** :
```python
{
    "id": "uuid",
    "category": "roles",  # Catégorie du référentiel
    "code": "interim",    # Code unique
    "label_fr": "Intérimaire",
    "label_en": "Temp Worker",
    "description": "Utilisateur intérimaire",
    "parent_id": null,    # Pour hiérarchies (pays > régions > villes)
    "order": 1,           # Ordre d'affichage
    "metadata": {         # Données supplémentaires spécifiques
        "color": "#3B82F6",
        "icon": "user",
        "permissions": ["view_jobs", "apply"]
    },
    "is_active": true,
    "is_system": false,   # true = ne peut pas être supprimé
    "created_at": "2025-01-20T10:00:00Z",
    "updated_at": "2025-01-20T10:00:00Z"
}
```

### 2. Table : `application_settings`

Paramètres globaux de l'application.

**Structure** :
```python
{
    "id": "uuid",
    "key": "max_upload_size",
    "value": "10485760",  # 10MB
    "type": "integer",    # string, integer, boolean, json
    "category": "uploads",
    "label": "Taille max upload (bytes)",
    "description": "Taille maximale des fichiers uploadés",
    "is_public": false,   # Accessible côté frontend ?
    "created_at": "2025-01-20T10:00:00Z",
    "updated_at": "2025-01-20T10:00:00Z"
}
```

### 3. Table : `business_rules`

Règles métier paramétrables.

**Structure** :
```python
{
    "id": "uuid",
    "name": "auto_validate_email_domains",
    "description": "Domaines email validés automatiquement",
    "rule_type": "validation",
    "conditions": {
        "domains": ["gmail.com", "awana-group.com"]
    },
    "actions": {
        "set_status": "active",
        "skip_validation": true
    },
    "priority": 10,
    "is_active": true,
    "created_at": "2025-01-20T10:00:00Z"
}
```

---

## 💾 Modèles de Données Backend

### Fichier : `/app/auth-microservice/awana_auth/core/reference_models.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ReferenceCategory(str, Enum):
    """Catégories de référentiels"""
    ROLES = "roles"
    STATUSES = "statuses"
    CONTRACT_TYPES = "contract_types"
    COUNTRIES = "countries"
    REGIONS = "regions"
    CITIES = "cities"
    SKILLS = "skills"
    DOCUMENT_TYPES = "document_types"
    PERMISSIONS = "permissions"
    MISSION_STATUSES = "mission_statuses"
    APPLICATION_STATUSES = "application_statuses"

class SystemReference(BaseModel):
    """Modèle pour les référentiels système"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    code: str  # Identifiant unique dans la catégorie
    label_fr: str
    label_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None  # Pour hiérarchies
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_system: bool = False  # Ne peut pas être modifié/supprimé si True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "roles",
                "code": "interim",
                "label_fr": "Intérimaire",
                "label_en": "Temporary Worker",
                "description": "Utilisateur cherchant des missions intérim",
                "metadata": {
                    "color": "#3B82F6",
                    "icon": "user",
                    "permissions": ["view_jobs", "apply"]
                },
                "is_active": True,
                "is_system": False
            }
        }

class ApplicationSetting(BaseModel):
    """Paramètres applicatifs"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str  # Clé unique
    value: str  # Valeur stockée en string
    type: str = "string"  # string, integer, boolean, json, array
    category: str = "general"
    label: str
    description: Optional[str] = None
    is_public: bool = False  # Accessible côté frontend
    validation_rules: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_typed_value(self) -> Any:
        """Retourne la valeur avec le bon type"""
        if self.type == "integer":
            return int(self.value)
        elif self.type == "boolean":
            return self.value.lower() in ['true', '1', 'yes']
        elif self.type == "json":
            import json
            return json.loads(self.value)
        elif self.type == "array":
            import json
            return json.loads(self.value)
        return self.value

class BusinessRule(BaseModel):
    """Règles métier"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    rule_type: str  # validation, notification, workflow, automation
    conditions: Dict[str, Any]  # Conditions pour déclencher la règle
    actions: Dict[str, Any]  # Actions à exécuter
    priority: int = 0  # Ordre d'exécution
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Requêtes API
class CreateReferenceRequest(BaseModel):
    category: str
    code: str
    label_fr: str
    label_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class UpdateReferenceRequest(BaseModel):
    label_fr: Optional[str] = None
    label_en: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class CreateSettingRequest(BaseModel):
    key: str
    value: str
    type: str = "string"
    category: str = "general"
    label: str
    description: Optional[str] = None
    is_public: bool = False
```

---

## 🔌 Routes API Backend

### Fichier : `/app/auth-microservice/configuration_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from awana_auth.core.dependencies import get_database, require_admin
from awana_auth.core.reference_models import *
import uuid
from datetime import datetime

router = APIRouter(prefix="/config", tags=["Configuration"])

# ==================== RÉFÉRENTIELS ====================

@router.get("/references")
async def get_references(
    category: Optional[str] = None,
    parent_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les référentiels
    Public (utilisé côté frontend)
    """
    query = {}
    if category:
        query["category"] = category
    if parent_id:
        query["parent_id"] = parent_id
    if is_active is not None:
        query["is_active"] = is_active
    
    references = await db.system_references.find(query).sort("order", 1).to_list(length=None)
    return {"references": references}

@router.post("/references", dependencies=[Depends(require_admin)])
async def create_reference(
    ref: CreateReferenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un nouveau référentiel (Admin uniquement)
    """
    # Vérifier unicité code dans la catégorie
    existing = await db.system_references.find_one({
        "category": ref.category,
        "code": ref.code
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le code '{ref.code}' existe déjà dans la catégorie '{ref.category}'"
        )
    
    reference = SystemReference(
        **ref.dict(),
        id=str(uuid.uuid4())
    )
    
    await db.system_references.insert_one(reference.dict())
    return {"reference": reference.dict()}

@router.patch("/references/{ref_id}", dependencies=[Depends(require_admin)])
async def update_reference(
    ref_id: str,
    update: UpdateReferenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un référentiel (Admin uniquement)
    """
    ref = await db.system_references.find_one({"id": ref_id})
    if not ref:
        raise HTTPException(status_code=404, detail="Référentiel non trouvé")
    
    if ref.get("is_system") and not update.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les référentiels système ne peuvent pas être désactivés"
        )
    
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.system_references.update_one(
        {"id": ref_id},
        {"$set": update_data}
    )
    
    updated_ref = await db.system_references.find_one({"id": ref_id})
    return {"reference": updated_ref}

@router.delete("/references/{ref_id}", dependencies=[Depends(require_admin)])
async def delete_reference(
    ref_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Supprimer un référentiel (Admin uniquement)
    Impossible pour les référentiels système
    """
    ref = await db.system_references.find_one({"id": ref_id})
    if not ref:
        raise HTTPException(status_code=404, detail="Référentiel non trouvé")
    
    if ref.get("is_system"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les référentiels système ne peuvent pas être supprimés"
        )
    
    # Vérifier qu'il n'est pas utilisé (exemple pour les rôles)
    if ref["category"] == "roles":
        users_count = await db.users.count_documents({"roles": ref["code"]})
        if users_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ce rôle est utilisé par {users_count} utilisateur(s)"
            )
    
    await db.system_references.delete_one({"id": ref_id})
    return {"message": "Référentiel supprimé"}

# ==================== PARAMÈTRES ====================

@router.get("/settings")
async def get_settings(
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les paramètres
    Si is_public=True, accessible sans authentification
    """
    query = {}
    if category:
        query["category"] = category
    if is_public is not None:
        query["is_public"] = is_public
    
    settings = await db.application_settings.find(query).to_list(length=None)
    
    # Convertir les valeurs en types appropriés
    for setting in settings:
        setting_obj = ApplicationSetting(**setting)
        setting["typed_value"] = setting_obj.get_typed_value()
    
    return {"settings": settings}

@router.post("/settings", dependencies=[Depends(require_admin)])
async def create_setting(
    setting: CreateSettingRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer un paramètre (Admin uniquement)
    """
    existing = await db.application_settings.find_one({"key": setting.key})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le paramètre '{setting.key}' existe déjà"
        )
    
    app_setting = ApplicationSetting(**setting.dict(), id=str(uuid.uuid4()))
    await db.application_settings.insert_one(app_setting.dict())
    
    return {"setting": app_setting.dict()}

@router.patch("/settings/{key}", dependencies=[Depends(require_admin)])
async def update_setting(
    key: str,
    value: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mettre à jour un paramètre (Admin uniquement)
    """
    setting = await db.application_settings.find_one({"key": key})
    if not setting:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    
    await db.application_settings.update_one(
        {"key": key},
        {"$set": {"value": value, "updated_at": datetime.utcnow()}}
    )
    
    updated = await db.application_settings.find_one({"key": key})
    return {"setting": updated}

# ==================== RÈGLES MÉTIER ====================

@router.get("/rules", dependencies=[Depends(require_admin)])
async def get_business_rules(
    rule_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Récupérer les règles métier (Admin uniquement)
    """
    query = {}
    if rule_type:
        query["rule_type"] = rule_type
    if is_active is not None:
        query["is_active"] = is_active
    
    rules = await db.business_rules.find(query).sort("priority", 1).to_list(length=None)
    return {"rules": rules}

@router.post("/rules", dependencies=[Depends(require_admin)])
async def create_business_rule(
    rule: BusinessRule,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Créer une règle métier (Admin uniquement)
    """
    rule.id = str(uuid.uuid4())
    await db.business_rules.insert_one(rule.dict())
    return {"rule": rule.dict()}

# ==================== CACHE ====================

@router.post("/cache/clear", dependencies=[Depends(require_admin)])
async def clear_cache():
    """
    Vider le cache des configurations
    À appeler après modification des référentiels
    """
    # Implémenter la logique de cache (Redis, mémoire, etc.)
    return {"message": "Cache vidé"}
```

---

## 🎨 Interface Admin Frontend

### 1. API Slice RTK Query

**Fichier** : `/app/apps/web/src/features/admin/api/configurationApi.ts`

```typescript
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface SystemReference {
  id: string
  category: string
  code: string
  label_fr: string
  label_en?: string
  description?: string
  parent_id?: string
  order: number
  metadata: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface ApplicationSetting {
  id: string
  key: string
  value: string
  type: 'string' | 'integer' | 'boolean' | 'json' | 'array'
  category: string
  label: string
  description?: string
  is_public: boolean
  typed_value?: any
}

export const configurationApi = createApi({
  reducerPath: 'configurationApi',
  baseQuery: fetchBaseQuery({
    baseUrl: '/auth-api/auth/config',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token')
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['References', 'Settings'],
  endpoints: (builder) => ({
    // RÉFÉRENTIELS
    getReferences: builder.query<{ references: SystemReference[] }, {
      category?: string
      parent_id?: string
      is_active?: boolean
    }>({
      query: (params) => ({
        url: '/references',
        params,
      }),
      providesTags: ['References'],
    }),
    
    createReference: builder.mutation<{ reference: SystemReference }, Partial<SystemReference>>({
      query: (data) => ({
        url: '/references',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['References'],
    }),
    
    updateReference: builder.mutation<{ reference: SystemReference }, {
      id: string
      data: Partial<SystemReference>
    }>({
      query: ({ id, data }) => ({
        url: `/references/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['References'],
    }),
    
    deleteReference: builder.mutation<void, string>({
      query: (id) => ({
        url: `/references/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['References'],
    }),
    
    // PARAMÈTRES
    getSettings: builder.query<{ settings: ApplicationSetting[] }, {
      category?: string
      is_public?: boolean
    }>({
      query: (params) => ({
        url: '/settings',
        params,
      }),
      providesTags: ['Settings'],
    }),
    
    updateSetting: builder.mutation<{ setting: ApplicationSetting }, {
      key: string
      value: string
    }>({
      query: ({ key, value }) => ({
        url: `/settings/${key}`,
        method: 'PATCH',
        body: { value },
      }),
      invalidatesTags: ['Settings'],
    }),
  }),
})

export const {
  useGetReferencesQuery,
  useCreateReferenceMutation,
  useUpdateReferenceMutation,
  useDeleteReferenceMutation,
  useGetSettingsQuery,
  useUpdateSettingMutation,
} = configurationApi
```

### 2. Page de Gestion des Référentiels

**Fichier** : `/app/apps/web/src/features/admin/pages/ReferencesManagementPage.tsx`

```typescript
import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Modal from '@/components/Modal'
import {
  useGetReferencesQuery,
  useCreateReferenceMutation,
  useUpdateReferenceMutation,
  useDeleteReferenceMutation,
} from '../api/configurationApi'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'

const categories = [
  { value: 'roles', label: 'Rôles Utilisateurs' },
  { value: 'statuses', label: 'Statuts' },
  { value: 'contract_types', label: 'Types de Contrat' },
  { value: 'countries', label: 'Pays' },
  { value: 'skills', label: 'Compétences' },
  { value: 'document_types', label: 'Types de Documents' },
  { value: 'mission_statuses', label: 'Statuts de Mission' },
  { value: 'application_statuses', label: 'Statuts de Candidature' },
]

export default function ReferencesManagementPage() {
  const [selectedCategory, setSelectedCategory] = useState('roles')
  const [showModal, setShowModal] = useState(false)
  const [editingRef, setEditingRef] = useState<any>(null)
  
  const { data, isLoading } = useGetReferencesQuery({
    category: selectedCategory,
    is_active: undefined,
  })
  
  const [createReference] = useCreateReferenceMutation()
  const [updateReference] = useUpdateReferenceMutation()
  const [deleteReference] = useDeleteReferenceMutation()
  
  const [formData, setFormData] = useState({
    code: '',
    label_fr: '',
    label_en: '',
    description: '',
    order: 0,
    is_active: true,
    metadata: {},
  })
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      if (editingRef) {
        await updateReference({
          id: editingRef.id,
          data: formData,
        }).unwrap()
      } else {
        await createReference({
          category: selectedCategory,
          ...formData,
        }).unwrap()
      }
      
      setShowModal(false)
      resetForm()
    } catch (error) {
      console.error('Erreur:', error)
    }
  }
  
  const resetForm = () => {
    setFormData({
      code: '',
      label_fr: '',
      label_en: '',
      description: '',
      order: 0,
      is_active: true,
      metadata: {},
    })
    setEditingRef(null)
  }
  
  const handleEdit = (ref: any) => {
    setEditingRef(ref)
    setFormData({
      code: ref.code,
      label_fr: ref.label_fr,
      label_en: ref.label_en || '',
      description: ref.description || '',
      order: ref.order,
      is_active: ref.is_active,
      metadata: ref.metadata || {},
    })
    setShowModal(true)
  }
  
  const handleDelete = async (id: string) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce référentiel ?')) {
      try {
        await deleteReference(id).unwrap()
      } catch (error) {
        console.error('Erreur:', error)
      }
    }
  }
  
  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Gestion des Référentiels
            </h1>
            <p className="text-gray-600">
              Gérez les valeurs configurables de l'application
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
          >
            <PlusIcon className="h-5 w-5" />
            Nouveau
          </button>
        </div>
        
        {/* Sélecteur de catégorie */}
        <Card>
          <div className="flex gap-2 flex-wrap">
            {categories.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setSelectedCategory(cat.value)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedCategory === cat.value
                    ? 'bg-jlc-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </Card>
        
        {/* Liste des référentiels */}
        <Card>
          {isLoading ? (
            <p>Chargement...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Label FR
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Label EN
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Ordre
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Système
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data?.references.map((ref) => (
                    <tr key={ref.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {ref.code}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {ref.label_fr}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {ref.label_en || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {ref.order}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          ref.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {ref.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {ref.is_system && (
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                            Système
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEdit(ref)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          {!ref.is_system && (
                            <button
                              onClick={() => handleDelete(ref.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <TrashIcon className="h-5 w-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
      
      {/* Modal Création/Édition */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          resetForm()
        }}
        title={editingRef ? 'Modifier le référentiel' : 'Nouveau référentiel'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Code *
            </label>
            <input
              type="text"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
              disabled={!!editingRef}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Label FR *
            </label>
            <input
              type="text"
              value={formData.label_fr}
              onChange={(e) => setFormData({ ...formData, label_fr: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Label EN
            </label>
            <input
              type="text"
              value={formData.label_en}
              onChange={(e) => setFormData({ ...formData, label_en: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
              rows={3}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Ordre
            </label>
            <input
              type="number"
              value={formData.order}
              onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 text-jlc-purple-600 rounded"
            />
            <label className="ml-2 block text-sm text-gray-900">
              Actif
            </label>
          </div>
          
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => {
                setShowModal(false)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
            >
              {editingRef ? 'Modifier' : 'Créer'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  )
}
```

---

**(Suite dans le prochain message - le fichier est trop long)**
