# 🔧 Configuration Dynamique - Partie 2
## Implémentation pour le Workflow Missions

---

## 📦 Phase 1 : Migration du Workflow Missions

### Données Actuellement Hardcodées

Dans le workflow missions, nous avons plusieurs données en dur :

**1. Statuts de Mission** (dans `/app/auth-microservice/awana_auth/core/mission_models.py`)
```python
# ❌ Actuellement hardcodé
class MissionStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

**2. Statuts de Candidature**
```python
# ❌ Actuellement hardcodé
class ApplicationStatus(str, Enum):
    PENDING = "pending"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    SELECTED = "selected"
    REJECTED = "rejected"
    MEDICAL_PENDING = "medical_pending"
    MEDICAL_APPROVED = "medical_approved"
    MEDICAL_REJECTED = "medical_rejected"
    CONTRACT_PENDING = "contract_pending"
    CONTRACT_SIGNED = "contract_signed"
```

**3. Types de Contrats**
```python
# ❌ Hardcodé dans le frontend
const CONTRACT_TYPES = ["CDI", "CDD", "Interim", "Stage"]
```

**4. Aptitudes Médicales**
```python
# ❌ Hardcodé
MEDICAL_APTITUDES = ["apte", "inapte", "apte_avec_reserves"]
```

---

## 🎯 Solution : Référentiels Dynamiques

### Étape 1 : Créer les Scripts de Migration

**Fichier** : `/app/auth-microservice/scripts/seed_mission_references.py`

```python
"""
Script de migration pour créer les référentiels du workflow missions
À exécuter UNE SEULE FOIS après le déploiement
"""
import asyncio
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def seed_mission_references():
    """Créer les référentiels pour le workflow missions"""
    
    # Connexion MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.awana_db
    
    print("🚀 Démarrage de la migration des référentiels missions...")
    
    # ==================== STATUTS DE MISSION ====================
    mission_statuses = [
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "draft",
            "label_fr": "Brouillon",
            "label_en": "Draft",
            "description": "Mission en cours de création, non publiée",
            "order": 1,
            "metadata": {
                "color": "#94A3B8",
                "icon": "document",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "published",
            "label_fr": "Publiée",
            "label_en": "Published",
            "description": "Mission visible et ouverte aux candidatures",
            "order": 2,
            "metadata": {
                "color": "#10B981",
                "icon": "globe",
                "is_visible_to_candidates": True,
                "can_receive_applications": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "in_progress",
            "label_fr": "En cours",
            "label_en": "In Progress",
            "description": "Mission démarrée avec un candidat",
            "order": 3,
            "metadata": {
                "color": "#3B82F6",
                "icon": "play",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "completed",
            "label_fr": "Terminée",
            "label_en": "Completed",
            "description": "Mission terminée avec succès",
            "order": 4,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "check-circle",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "mission_statuses",
            "code": "cancelled",
            "label_fr": "Annulée",
            "label_en": "Cancelled",
            "description": "Mission annulée",
            "order": 5,
            "metadata": {
                "color": "#EF4444",
                "icon": "x-circle",
                "is_visible_to_candidates": False,
                "can_receive_applications": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Supprimer les anciennes valeurs et insérer les nouvelles
    await db.system_references.delete_many({"category": "mission_statuses"})
    await db.system_references.insert_many(mission_statuses)
    print(f"✅ {len(mission_statuses)} statuts de mission créés")
    
    # ==================== STATUTS DE CANDIDATURE ====================
    application_statuses = [
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "pending",
            "label_fr": "En attente",
            "label_en": "Pending",
            "description": "Candidature soumise, en attente de traitement",
            "order": 1,
            "metadata": {
                "color": "#F59E0B",
                "icon": "clock",
                "next_possible_statuses": ["interview_scheduled", "rejected"],
                "requires_action_from": "company"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "interview_scheduled",
            "label_fr": "Entretien programmé",
            "label_en": "Interview Scheduled",
            "description": "Entretien planifié avec le candidat",
            "order": 2,
            "metadata": {
                "color": "#3B82F6",
                "icon": "calendar",
                "next_possible_statuses": ["interview_completed"],
                "requires_action_from": "company"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "interview_completed",
            "label_fr": "Entretien effectué",
            "label_en": "Interview Completed",
            "description": "Entretien réalisé, décision en attente",
            "order": 3,
            "metadata": {
                "color": "#6366F1",
                "icon": "check",
                "next_possible_statuses": ["selected", "rejected"],
                "requires_action_from": "company"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "selected",
            "label_fr": "Sélectionné",
            "label_en": "Selected",
            "description": "Candidat sélectionné par l'entreprise",
            "order": 4,
            "metadata": {
                "color": "#10B981",
                "icon": "user-check",
                "next_possible_statuses": ["medical_pending"],
                "requires_action_from": "agency"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "medical_pending",
            "label_fr": "Visite médicale en attente",
            "label_en": "Medical Pending",
            "description": "En attente de la visite médicale",
            "order": 5,
            "metadata": {
                "color": "#F59E0B",
                "icon": "document-medical",
                "next_possible_statuses": ["medical_approved", "medical_rejected"],
                "requires_action_from": "agency",
                "requires_document_upload": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "medical_approved",
            "label_fr": "Visite médicale validée",
            "label_en": "Medical Approved",
            "description": "Candidat déclaré apte médicalement",
            "order": 6,
            "metadata": {
                "color": "#10B981",
                "icon": "shield-check",
                "next_possible_statuses": ["contract_pending"],
                "requires_action_from": "agency"
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "medical_rejected",
            "label_fr": "Visite médicale refusée",
            "label_en": "Medical Rejected",
            "description": "Candidat déclaré inapte médicalement",
            "order": 7,
            "metadata": {
                "color": "#EF4444",
                "icon": "shield-x",
                "next_possible_statuses": [],
                "is_final_status": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "contract_pending",
            "label_fr": "Contrat en attente",
            "label_en": "Contract Pending",
            "description": "En attente de signature du contrat",
            "order": 8,
            "metadata": {
                "color": "#F59E0B",
                "icon": "document-text",
                "next_possible_statuses": ["contract_signed"],
                "requires_action_from": "agency",
                "requires_document_upload": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "contract_signed",
            "label_fr": "Contrat signé",
            "label_en": "Contract Signed",
            "description": "Contrat signé, processus terminé",
            "order": 9,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "document-check",
                "next_possible_statuses": [],
                "is_final_status": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "application_statuses",
            "code": "rejected",
            "label_fr": "Refusée",
            "label_en": "Rejected",
            "description": "Candidature rejetée",
            "order": 10,
            "metadata": {
                "color": "#EF4444",
                "icon": "x-circle",
                "next_possible_statuses": [],
                "is_final_status": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "application_statuses"})
    await db.system_references.insert_many(application_statuses)
    print(f"✅ {len(application_statuses)} statuts de candidature créés")
    
    # ==================== TYPES DE CONTRATS ====================
    contract_types = [
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "cdi",
            "label_fr": "CDI",
            "label_en": "Permanent Contract",
            "description": "Contrat à Durée Indéterminée",
            "order": 1,
            "metadata": {
                "color": "#10B981",
                "icon": "briefcase"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "cdd",
            "label_fr": "CDD",
            "label_en": "Fixed-term Contract",
            "description": "Contrat à Durée Déterminée",
            "order": 2,
            "metadata": {
                "color": "#3B82F6",
                "icon": "calendar"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "interim",
            "label_fr": "Intérim",
            "label_en": "Temporary Work",
            "description": "Mission d'intérim",
            "order": 3,
            "metadata": {
                "color": "#F59E0B",
                "icon": "clock"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "contract_types",
            "code": "stage",
            "label_fr": "Stage",
            "label_en": "Internship",
            "description": "Convention de stage",
            "order": 4,
            "metadata": {
                "color": "#8B5CF6",
                "icon": "academic-cap"
            },
            "is_active": True,
            "is_system": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "contract_types"})
    await db.system_references.insert_many(contract_types)
    print(f"✅ {len(contract_types)} types de contrats créés")
    
    # ==================== APTITUDES MÉDICALES ====================
    medical_aptitudes = [
        {
            "id": str(uuid.uuid4()),
            "category": "medical_aptitudes",
            "code": "apte",
            "label_fr": "Apte",
            "label_en": "Fit",
            "description": "Candidat apte au travail",
            "order": 1,
            "metadata": {
                "color": "#10B981",
                "icon": "check-circle",
                "allows_contract": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "medical_aptitudes",
            "code": "apte_avec_reserves",
            "label_fr": "Apte avec réserves",
            "label_en": "Fit with Restrictions",
            "description": "Apte avec restrictions spécifiques",
            "order": 2,
            "metadata": {
                "color": "#F59E0B",
                "icon": "exclamation-triangle",
                "allows_contract": True,
                "requires_note": True
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "category": "medical_aptitudes",
            "code": "inapte",
            "label_fr": "Inapte",
            "label_en": "Unfit",
            "description": "Candidat inapte au travail",
            "order": 3,
            "metadata": {
                "color": "#EF4444",
                "icon": "x-circle",
                "allows_contract": False
            },
            "is_active": True,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.system_references.delete_many({"category": "medical_aptitudes"})
    await db.system_references.insert_many(medical_aptitudes)
    print(f"✅ {len(medical_aptitudes)} aptitudes médicales créées")
    
    print("\n🎉 Migration terminée avec succès !")
    print(f"📊 Total: {len(mission_statuses) + len(application_statuses) + len(contract_types) + len(medical_aptitudes)} référentiels créés")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_mission_references())
```

---

## 🔄 Étape 2 : Adapter le Backend pour Utiliser les Référentiels

### Modifier les Routes Missions

**Fichier** : `/app/auth-microservice/mission_routes.py`

Ajouter des helpers pour valider les statuts :

```python
# Helpers pour validation dynamique des statuts
async def get_valid_statuses(db: AsyncIOMotorDatabase, category: str) -> List[str]:
    """Récupérer les codes de statuts valides depuis la BDD"""
    references = await db.system_references.find({
        "category": category,
        "is_active": True
    }).to_list(length=None)
    return [ref["code"] for ref in references]

async def validate_status(
    db: AsyncIOMotorDatabase, 
    category: str, 
    status: str
) -> bool:
    """Valider qu'un statut existe et est actif"""
    ref = await db.system_references.find_one({
        "category": category,
        "code": status,
        "is_active": True
    })
    return ref is not None

async def get_status_metadata(
    db: AsyncIOMotorDatabase,
    category: str,
    status: str
) -> Dict[str, Any]:
    """Récupérer les métadonnées d'un statut"""
    ref = await db.system_references.find_one({
        "category": category,
        "code": status
    })
    return ref.get("metadata", {}) if ref else {}

# Modifier l'endpoint de création de mission
@router.post("/missions")
async def create_mission(
    mission: CreateMissionRequest,
    current_user: dict = Depends(require_company_or_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Créer une nouvelle mission"""
    
    # Valider le statut de mission
    if not await validate_status(db, "mission_statuses", mission.status):
        valid_statuses = await get_valid_statuses(db, "mission_statuses")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide. Valeurs autorisées: {valid_statuses}"
        )
    
    # Valider le type de contrat
    if not await validate_status(db, "contract_types", mission.contract_type):
        valid_types = await get_valid_statuses(db, "contract_types")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de contrat invalide. Valeurs autorisées: {valid_types}"
        )
    
    # Créer la mission...
    new_mission = Mission(
        **mission.dict(),
        company_id=current_user["user_id"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    await db.missions.insert_one(new_mission.dict())
    return {"mission": new_mission.dict()}

# Modifier l'endpoint de mise à jour du statut de candidature
@router.patch("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status_update: dict,
    current_user: dict = Depends(require_auth),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Mettre à jour le statut d'une candidature"""
    
    new_status = status_update.get("status")
    
    # Valider le nouveau statut
    if not await validate_status(db, "application_statuses", new_status):
        valid_statuses = await get_valid_statuses(db, "application_statuses")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide. Valeurs autorisées: {valid_statuses}"
        )
    
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Candidature non trouvée")
    
    # Récupérer les métadonnées du statut actuel et nouveau
    current_metadata = await get_status_metadata(db, "application_statuses", application["status"])
    new_metadata = await get_status_metadata(db, "application_statuses", new_status)
    
    # Vérifier les transitions autorisées
    allowed_transitions = current_metadata.get("next_possible_statuses", [])
    if allowed_transitions and new_status not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transition non autorisée de '{application['status']}' vers '{new_status}'. Transitions possibles: {allowed_transitions}"
        )
    
    # Vérifier si un document est requis
    if new_metadata.get("requires_document_upload") and not status_update.get("document_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ce changement de statut nécessite l'upload d'un document"
        )
    
    # Mettre à jour le statut
    update_data = {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if status_update.get("document_id"):
        update_data["documents"] = application.get("documents", []) + [status_update["document_id"]]
    
    await db.applications.update_one(
        {"id": application_id},
        {"$set": update_data}
    )
    
    updated_application = await db.applications.find_one({"id": application_id})
    return {"application": updated_application}
```

---

## 🎨 Étape 3 : Adapter le Frontend

### 1. Hook pour Charger les Référentiels

**Fichier** : `/app/apps/web/src/hooks/useReferences.ts`

```typescript
import { useMemo } from 'react'
import { useGetReferencesQuery } from '@/features/admin/api/configurationApi'

export interface ReferenceOption {
  value: string
  label: string
  color?: string
  icon?: string
  metadata?: Record<string, any>
}

export function useReferences(category: string) {
  const { data, isLoading, error } = useGetReferencesQuery({
    category,
    is_active: true
  })

  const options: ReferenceOption[] = useMemo(() => {
    if (!data?.references) return []
    
    return data.references.map(ref => ({
      value: ref.code,
      label: ref.label_fr,
      color: ref.metadata?.color,
      icon: ref.metadata?.icon,
      metadata: ref.metadata
    }))
  }, [data])

  const getLabel = (code: string): string => {
    const ref = options.find(opt => opt.value === code)
    return ref?.label || code
  }

  const getMetadata = (code: string): Record<string, any> => {
    const ref = options.find(opt => opt.value === code)
    return ref?.metadata || {}
  }

  return {
    options,
    isLoading,
    error,
    getLabel,
    getMetadata
  }
}

// Hooks spécialisés pour les différentes catégories
export const useMissionStatuses = () => useReferences('mission_statuses')
export const useApplicationStatuses = () => useReferences('application_statuses')
export const useContractTypes = () => useReferences('contract_types')
export const useMedicalAptitudes = () => useReferences('medical_aptitudes')
```

### 2. Composant Select Dynamique

**Fichier** : `/app/apps/web/src/components/ReferenceSelect.tsx`

```typescript
import { useReferences } from '@/hooks/useReferences'

interface ReferenceSelectProps {
  category: string
  value: string
  onChange: (value: string) => void
  label?: string
  required?: boolean
  disabled?: boolean
}

export default function ReferenceSelect({
  category,
  value,
  onChange,
  label,
  required = false,
  disabled = false
}: ReferenceSelectProps) {
  const { options, isLoading } = useReferences(category)

  if (isLoading) {
    return <div className="animate-pulse h-10 bg-gray-200 rounded"></div>
  }

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
      >
        <option value="">Sélectionner...</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}
```

### 3. Badge de Statut Dynamique

**Fichier** : `/app/apps/web/src/components/StatusBadge.tsx`

```typescript
import { useReferences } from '@/hooks/useReferences'

interface StatusBadgeProps {
  category: string
  status: string
  showIcon?: boolean
}

export default function StatusBadge({
  category,
  status,
  showIcon = false
}: StatusBadgeProps) {
  const { getLabel, getMetadata } = useReferences(category)
  
  const label = getLabel(status)
  const metadata = getMetadata(status)
  const color = metadata.color || '#6B7280'

  return (
    <span
      className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: `${color}20`,
        color: color,
        border: `1px solid ${color}`
      }}
    >
      {showIcon && metadata.icon && (
        <span className="text-sm">{metadata.icon}</span>
      )}
      {label}
    </span>
  )
}
```

### 4. Mise à Jour des Pages Missions

**Exemple** : `/app/apps/web/src/features/missions/pages/CreateMissionPage.tsx`

```typescript
import ReferenceSelect from '@/components/ReferenceSelect'
import { useContractTypes, useMissionStatuses } from '@/hooks/useReferences'

export default function CreateMissionPage() {
  const [formData, setFormData] = useState({
    title: '',
    contract_type: '',
    status: 'draft',
    // ...autres champs
  })

  return (
    <form onSubmit={handleSubmit}>
      {/* Titre */}
      <div>
        <label>Titre de la mission *</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          required
        />
      </div>

      {/* Type de contrat - Sélection dynamique */}
      <ReferenceSelect
        category="contract_types"
        value={formData.contract_type}
        onChange={(value) => setFormData({ ...formData, contract_type: value })}
        label="Type de contrat"
        required
      />

      {/* Statut - Sélection dynamique */}
      <ReferenceSelect
        category="mission_statuses"
        value={formData.status}
        onChange={(value) => setFormData({ ...formData, status: value })}
        label="Statut"
        required
      />

      {/* ...autres champs */}
    </form>
  )
}
```

**Exemple** : `/app/apps/web/src/features/missions/pages/ApplicationsManagementPage.tsx`

```typescript
import StatusBadge from '@/components/StatusBadge'
import { useApplicationStatuses } from '@/hooks/useReferences'

export default function ApplicationsManagementPage() {
  const { data } = useGetApplicationsQuery()
  const { getMetadata } = useApplicationStatuses()

  const canTransitionTo = (currentStatus: string, newStatus: string) => {
    const metadata = getMetadata(currentStatus)
    const allowedTransitions = metadata.next_possible_statuses || []
    return allowedTransitions.includes(newStatus)
  }

  return (
    <div>
      {data?.applications.map((app) => (
        <div key={app.id}>
          {/* Badge de statut dynamique */}
          <StatusBadge
            category="application_statuses"
            status={app.status}
            showIcon
          />

          {/* Boutons de transition conditionnels */}
          <div className="flex gap-2">
            {canTransitionTo(app.status, 'interview_scheduled') && (
              <button onClick={() => updateStatus('interview_scheduled')}>
                Programmer entretien
              </button>
            )}
            {canTransitionTo(app.status, 'selected') && (
              <button onClick={() => updateStatus('selected')}>
                Sélectionner
              </button>
            )}
            {canTransitionTo(app.status, 'rejected') && (
              <button onClick={() => updateStatus('rejected')}>
                Refuser
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
```

---

## ⚙️ Étape 4 : Configuration dans main.py

**Fichier** : `/app/auth-microservice/main.py`

```python
from configuration_routes import router as config_router

# Ajouter les routes de configuration
app.include_router(config_router, prefix="/api/auth")
```

**Fichier** : `/app/apps/web/src/store/store.ts`

```typescript
import { configurationApi } from '@/features/admin/api/configurationApi'

export const store = configureStore({
  reducer: {
    // ... autres reducers
    [configurationApi.reducerPath]: configurationApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      // ... autres middlewares
      configurationApi.middleware
    ),
})
```

---

## 🚀 Étape 5 : Déploiement

### 1. Exécuter le Script de Migration

```bash
# Se placer dans le dossier auth-microservice
cd /app/auth-microservice

# Exécuter le script de seed
python scripts/seed_mission_references.py
```

### 2. Redémarrer les Services

```bash
sudo supervisorctl restart all
```

### 3. Vérifier les Données

```bash
# Connexion à MongoDB
mongosh

use awana_db

# Vérifier les référentiels créés
db.system_references.find({ category: "mission_statuses" }).pretty()
db.system_references.find({ category: "application_statuses" }).pretty()
db.system_references.find({ category: "contract_types" }).pretty()
db.system_references.find({ category: "medical_aptitudes" }).pretty()
```

---

## ✅ Checklist de Migration

### Backend
- [ ] Créer `reference_models.py` avec les modèles Pydantic
- [ ] Créer `configuration_routes.py` avec les endpoints CRUD
- [ ] Créer le script `seed_mission_references.py`
- [ ] Ajouter les helpers de validation dans `mission_routes.py`
- [ ] Mettre à jour les endpoints existants pour valider contre les référentiels
- [ ] Intégrer les routes dans `main.py`
- [ ] Exécuter le script de seed

### Frontend
- [ ] Créer `configurationApi.ts` pour RTK Query
- [ ] Créer le hook `useReferences.ts`
- [ ] Créer le composant `ReferenceSelect.tsx`
- [ ] Créer le composant `StatusBadge.tsx`
- [ ] Créer la page `ReferencesManagementPage.tsx`
- [ ] Mettre à jour `CreateMissionPage.tsx` pour utiliser les selects dynamiques
- [ ] Mettre à jour `ApplicationsManagementPage.tsx` pour les badges et transitions
- [ ] Ajouter les routes dans `App.tsx`
- [ ] Enregistrer l'API dans `store.ts`

### Tests
- [ ] Tester la création de référentiels via l'API
- [ ] Tester la création de mission avec type de contrat dynamique
- [ ] Tester les transitions de statut avec validation
- [ ] Tester l'interface admin de gestion des référentiels
- [ ] Tester que les selects se remplissent correctement
- [ ] Tester les badges de statut avec couleurs dynamiques

---

## 🎯 Prochaines Étapes (Autres Modules)

Après avoir terminé le workflow missions, appliquer la même logique pour :

1. **Rôles Utilisateurs**
   - Migrer les rôles hardcodés vers `system_references`
   - Lier permissions aux rôles via metadata

2. **Hiérarchie Locations**
   - Créer référentiels pour pays, régions, villes
   - Utiliser `parent_id` pour la hiérarchie

3. **Types de Documents**
   - Dynamiser les types de documents uploadables
   - Lier aux statuts (ex: "medical_pending" requiert "medical_certificate")

4. **Compétences**
   - Créer un référentiel de compétences
   - Permettre aux admins d'ajouter de nouvelles compétences

---

## 📝 Bonnes Pratiques

### 1. Marquage Système
- Utiliser `is_system: true` pour les référentiels critiques
- Empêcher la suppression/désactivation des éléments système

### 2. Validation des Transitions
- Définir `next_possible_statuses` dans metadata
- Valider côté backend ET frontend

### 3. Cache
- Mettre en cache les référentiels côté frontend (RTK Query le fait automatiquement)
- Invalider le cache après modifications

### 4. Migration Progressive
- Garder les anciennes valeurs en dur pendant la transition
- Tester chaque module individuellement
- Migrer les données existantes progressivement

### 5. Documentation
- Documenter chaque catégorie de référentiel
- Expliquer les metadata spécifiques
- Maintenir des exemples à jour

---

## 🐛 Gestion des Erreurs

### Erreur : "Statut invalide"
```python
# Backend retourne la liste des statuts valides
raise HTTPException(
    status_code=400,
    detail=f"Statut invalide. Valeurs autorisées: {valid_statuses}"
)
```

### Erreur : "Transition non autorisée"
```python
# Vérifier les transitions possibles
allowed = metadata.get("next_possible_statuses", [])
if new_status not in allowed:
    raise HTTPException(
        status_code=400,
        detail=f"Transition impossible de '{current}' vers '{new_status}'"
    )
```

### Erreur : "Document requis"
```python
# Certains changements de statut nécessitent un document
if metadata.get("requires_document_upload") and not document_id:
    raise HTTPException(
        status_code=400,
        detail="Ce changement de statut nécessite l'upload d'un document"
    )
```

---

## 🎉 Résultat Final

✅ **Plus aucune donnée en dur dans le code**
✅ **Interface admin pour gérer toutes les valeurs**
✅ **Validation automatique des statuts et transitions**
✅ **Évolutivité : Ajout de nouvelles valeurs sans modifier le code**
✅ **Workflow missions entièrement paramétrable**

L'application est maintenant **configurable, maintenable et évolutive** ! 🚀
