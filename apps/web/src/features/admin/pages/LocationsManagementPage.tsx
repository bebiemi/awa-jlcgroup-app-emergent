import { useState } from 'react'
import Layout from '@/components/Layout'
import {
  useGetLocationTreeQuery,
  useToggleLocationVisibilityMutation,
  useDeleteLocationMutation,
  type LocationTree,
  type LocationType,
} from '../api/locationsApi'
import {
  MapPinIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import CreateLocationModal from '../components/CreateLocationModal'
import EditLocationModal from '../components/EditLocationModal'
import DeleteLocationModal from '../components/DeleteLocationModal'

const locationTypeLabels: Record<LocationType, string> = {
  country: 'Pays',
  province: 'Province',
  city: 'Chef-lieu',
  district: 'Arrondissement',
  neighborhood: 'Quartier',
}

const locationTypeColors: Record<LocationType, string> = {
  country: 'bg-red-100 text-red-700',
  province: 'bg-orange-100 text-orange-700',
  city: 'bg-blue-100 text-blue-700',
  district: 'bg-green-100 text-green-700',
  neighborhood: 'bg-purple-100 text-purple-700',
}

export default function LocationsManagementPage() {
  const { data: tree, isLoading, refetch } = useGetLocationTreeQuery()
  const [toggleVisibility] = useToggleLocationVisibilityMutation()
  const [deleteLocation] = useDeleteLocationMutation()

  const [searchQuery, setSearchQuery] = useState('')
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<LocationTree | null>(null)
  const [createParent, setCreateParent] = useState<LocationTree | null>(null)

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  const handleToggleVisibility = async (location: LocationTree) => {
    try {
      await toggleVisibility({ id: location.id, is_visible: !location.is_visible }).unwrap()
      toast.success(`${location.name} ${location.is_visible ? 'masqué' : 'visible'}`)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors du changement de visibilité')
    }
  }

  const handleEdit = (location: LocationTree) => {
    setSelectedLocation(location)
    setShowEditModal(true)
  }

  const handleDelete = (location: LocationTree) => {
    setSelectedLocation(location)
    setShowDeleteModal(true)
  }

  const handleAddChild = (parent: LocationTree) => {
    setCreateParent(parent)
    setShowCreateModal(true)
  }

  const handleAddRoot = () => {
    setCreateParent(null)
    setShowCreateModal(true)
  }

  const filterTree = (nodes: LocationTree[], query: string): LocationTree[] => {
    if (!query) return nodes

    const filtered: LocationTree[] = []
    for (const node of nodes) {
      const matchesSearch = node.name.toLowerCase().includes(query.toLowerCase())
      const filteredChildren = filterTree(node.children, query)

      if (matchesSearch || filteredChildren.length > 0) {
        filtered.push({
          ...node,
          children: filteredChildren,
        })
        // Auto-expand nodes with matches
        if (filteredChildren.length > 0) {
          expandedNodes.add(node.id)
        }
      }
    }
    return filtered
  }

  const renderTree = (nodes: LocationTree[], level: number = 0) => {
    return nodes.map((node) => {
      const isExpanded = expandedNodes.has(node.id)
      const hasChildren = node.children.length > 0
      const indent = level * 24

      return (
        <div key={node.id} className="select-none">
          <div
            className={`flex items-center justify-between py-2 px-3 hover:bg-gray-50 rounded-lg transition ${
              !node.is_visible ? 'opacity-50' : ''
            }`}
            style={{ paddingLeft: `${indent + 12}px` }}
          >
            <div className="flex items-center space-x-3 flex-1">
              {hasChildren ? (
                <button onClick={() => toggleNode(node.id)} className="p-1 hover:bg-gray-200 rounded">
                  {isExpanded ? (
                    <ChevronDownIcon className="h-4 w-4 text-gray-600" />
                  ) : (
                    <ChevronRightIcon className="h-4 w-4 text-gray-600" />
                  )}
                </button>
              ) : (
                <div className="w-6" />
              )}

              <MapPinIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />

              <div className="flex items-center space-x-2 flex-1">
                <span className="font-medium text-gray-900">{node.name}</span>
                <span className={`text-xs px-2 py-1 rounded-full ${locationTypeColors[node.type]}`}>
                  {locationTypeLabels[node.type]}
                </span>
                {node.is_required && (
                  <span className="text-xs px-2 py-1 rounded-full bg-red-50 text-red-600">Obligatoire</span>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={() => handleAddChild(node)}
                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                title="Ajouter un enfant"
              >
                <PlusIcon className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleEdit(node)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                title="Modifier"
              >
                <PencilIcon className="h-4 w-4" />
              </button>
              <button
                onClick={() => handleToggleVisibility(node)}
                className={`p-2 rounded-lg transition ${
                  node.is_visible ? 'text-gray-600 hover:bg-gray-100' : 'text-orange-600 hover:bg-orange-50'
                }`}
                title={node.is_visible ? 'Masquer' : 'Afficher'}
              >
                {node.is_visible ? <EyeIcon className="h-4 w-4" /> : <EyeSlashIcon className="h-4 w-4" />}
              </button>
              <button
                onClick={() => handleDelete(node)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                title="Supprimer"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          {isExpanded && hasChildren && <div className="mt-1">{renderTree(node.children, level + 1)}</div>}
        </div>
      )
    })
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  const filteredTree = searchQuery ? filterTree(tree || [], searchQuery) : tree || []

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestion des Localisations</h1>
            <p className="text-gray-600 mt-2">Gérez la hiérarchie des pays, provinces, villes et quartiers</p>
          </div>
          <button
            onClick={handleAddRoot}
            className="bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition flex items-center space-x-2"
          >
            <PlusIcon className="h-5 w-5" />
            <span>Ajouter un Pays</span>
          </button>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher une localisation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Tree View */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            {filteredTree.length === 0 ? (
              <div className="text-center py-12">
                <MapPinIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {searchQuery ? 'Aucune localisation trouvée' : 'Aucune localisation. Commencez par ajouter un pays.'}
                </p>
              </div>
            ) : (
              <div className="space-y-1">{renderTree(filteredTree)}</div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <CreateLocationModal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          setCreateParent(null)
        }}
        parent={createParent}
      />

      {selectedLocation && (
        <>
          <EditLocationModal
            isOpen={showEditModal}
            onClose={() => {
              setShowEditModal(false)
              setSelectedLocation(null)
            }}
            location={selectedLocation}
          />

          <DeleteLocationModal
            isOpen={showDeleteModal}
            onClose={() => {
              setShowDeleteModal(false)
              setSelectedLocation(null)
            }}
            location={selectedLocation}
          />
        </>
      )}
    </Layout>
  )
}
