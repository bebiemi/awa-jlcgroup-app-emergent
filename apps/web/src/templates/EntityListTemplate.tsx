/**
 * Template Générique pour Listes d'Entités
 * Réutilisable pour : Users, Entreprises, Validations, Missions, etc.
 * 
 * Configuration complète via props - Zéro valeur en dur
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import Breadcrumb from '@/components/Breadcrumb'
import Layout from '@/components/Layout'

// Types
export interface EntityColumn {
  key: string
  label: string
  render?: (value: any, entity: any) => React.ReactNode
  sortable?: boolean
  width?: string
}

export interface EntityFilter {
  key: string
  label: string
  type: 'select' | 'search' | 'date' | 'multiselect'
  options?: Array<{ value: string; label: string }>
  placeholder?: string
}

export interface EntityAction {
  key: string
  label: string
  icon?: any
  onClick: (entity: any) => void
  variant?: 'primary' | 'secondary' | 'danger'
  show?: (entity: any) => boolean
  permission?: string
}

export interface EntityListConfig {
  // Identité
  entityName: string // "Utilisateur", "Entreprise", etc.
  entityNamePlural: string // "Utilisateurs", "Entreprises"
  
  // UI
  title: string
  subtitle?: string
  icon?: any
  
  // Colonnes
  columns: EntityColumn[]
  
  // Filtres
  filters?: EntityFilter[]
  
  // Actions
  actions: {
    create?: {
      label: string
      onClick: () => void
      permission?: string
    }
    row: EntityAction[]
    bulk?: EntityAction[]
  }
  
  // Data
  data: any[]
  isLoading: boolean
  error?: any
  
  // Pagination
  pagination?: {
    currentPage: number
    totalPages: number
    onPageChange: (page: number) => void
  }
  
  // Recherche
  onSearch?: (query: string) => void
  searchPlaceholder?: string
  
  // Messages vides
  emptyState?: {
    message: string
    action?: {
      label: string
      onClick: () => void
    }
  }
}

interface EntityListTemplateProps {
  config: EntityListConfig
  permissions: Record<string, boolean>
}

export default function EntityListTemplate({ config, permissions }: EntityListTemplateProps) {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({})
  const [selectedEntities, setSelectedEntities] = useState<string[]>([])

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    if (config.onSearch) {
      config.onSearch(query)
    }
  }

  const handleFilterChange = (filterKey: string, value: any) => {
    const newFilters = { ...activeFilters, [filterKey]: value }
    setActiveFilters(newFilters)
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedEntities(config.data.map((e: any) => e.id))
    } else {
      setSelectedEntities([])
    }
  }

  const handleSelectEntity = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedEntities([...selectedEntities, id])
    } else {
      setSelectedEntities(selectedEntities.filter((eid) => eid !== id))
    }
  }

  // Filtrer les actions visibles selon permissions
  const visibleRowActions = config.actions.row.filter((action) => {
    if (action.permission && !permissions[action.permission]) {
      return false
    }
    return true
  })

  const canCreate = !config.actions.create?.permission || permissions[config.actions.create.permission]

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 p-6">
        {/* Breadcrumb */}
        <Breadcrumb className="mb-4" />

        <div className="max-w-7xl mx-auto">
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {config.icon && <config.icon className="h-10 w-10 text-jlc-purple-600" />}
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{config.title}</h1>
                  {config.subtitle && (
                    <p className="text-gray-600 mt-1">{config.subtitle}</p>
                  )}
                </div>
              </div>
              
              {config.actions.create && canCreate && (
                <button
                  onClick={config.actions.create.onClick}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all"
                >
                  <PlusIcon className="h-5 w-5" />
                  {config.actions.create.label}
                </button>
              )}
            </div>

            {/* Filtres et recherche */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex flex-col md:flex-row gap-4">
                {/* Recherche */}
                {config.onSearch && (
                  <div className="flex-1">
                    <div className="relative">
                      <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="text"
                        placeholder={config.searchPlaceholder || 'Rechercher...'}
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                )}

                {/* Filtres dynamiques */}
                {config.filters?.map((filter) => (
                  <div key={filter.key} className="md:w-64">
                    {filter.type === 'select' && (
                      <div className="relative">
                        <FunnelIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <select
                          value={activeFilters[filter.key] || ''}
                          onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent appearance-none bg-white"
                        >
                          <option value="">{filter.label}</option>
                          {filter.options?.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Table */}
            {config.isLoading ? (
              <div className="flex items-center justify-center py-12 bg-white rounded-lg shadow-sm">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
              </div>
            ) : config.data.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <div className="max-w-md mx-auto">
                  {config.icon && <config.icon className="h-16 w-16 text-gray-300 mx-auto mb-4" />}
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {config.emptyState?.message || `Aucun ${config.entityName.toLowerCase()}`}
                  </h3>
                  {config.emptyState?.action && canCreate && (
                    <button
                      onClick={config.emptyState.action.onClick}
                      className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
                    >
                      <PlusIcon className="h-5 w-5" />
                      {config.emptyState.action.label}
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {config.actions.bulk && config.actions.bulk.length > 0 && (
                        <th className="px-6 py-3 text-left">
                          <input
                            type="checkbox"
                            checked={selectedEntities.length === config.data.length}
                            onChange={(e) => handleSelectAll(e.target.checked)}
                            className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500"
                          />
                        </th>
                      )}
                      
                      {config.columns.map((column) => (
                        <th
                          key={column.key}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          style={{ width: column.width }}
                        >
                          {column.label}
                        </th>
                      ))}
                      
                      {visibleRowActions.length > 0 && (
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {config.data.map((entity: any) => (
                      <tr key={entity.id} className="hover:bg-gray-50 transition-colors">
                        {config.actions.bulk && config.actions.bulk.length > 0 && (
                          <td className="px-6 py-4">
                            <input
                              type="checkbox"
                              checked={selectedEntities.includes(entity.id)}
                              onChange={(e) => handleSelectEntity(entity.id, e.target.checked)}
                              className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500"
                            />
                          </td>
                        )}
                        
                        {config.columns.map((column) => (
                          <td key={column.key} className="px-6 py-4 text-sm text-gray-900">
                            {column.render
                              ? column.render(entity[column.key], entity)
                              : entity[column.key]}
                          </td>
                        ))}
                        
                        {visibleRowActions.length > 0 && (
                          <td className="px-6 py-4 text-right text-sm font-medium">
                            <div className="flex items-center justify-end gap-2">
                              {visibleRowActions.map((action) => {
                                if (action.show && !action.show(entity)) {
                                  return null
                                }
                                
                                const ActionIcon = action.icon || EyeIcon
                                const variantClasses = {
                                  primary: 'text-jlc-purple-600 hover:text-jlc-purple-900',
                                  secondary: 'text-gray-600 hover:text-gray-900',
                                  danger: 'text-red-600 hover:text-red-900',
                                }
                                
                                return (
                                  <button
                                    key={action.key}
                                    onClick={() => action.onClick(entity)}
                                    className={`p-1 rounded ${variantClasses[action.variant || 'secondary']}`}
                                    title={action.label}
                                  >
                                    <ActionIcon className="h-5 w-5" />
                                  </button>
                                )
                              })}
                            </div>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Pagination */}
                {config.pagination && config.pagination.totalPages > 1 && (
                  <div className="px-6 py-4 flex items-center justify-between border-t border-gray-200">
                    <div className="text-sm text-gray-700">
                      Page {config.pagination.currentPage} sur {config.pagination.totalPages}
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => config.pagination!.onPageChange(config.pagination!.currentPage - 1)}
                        disabled={config.pagination.currentPage === 1}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Précédent
                      </button>
                      <button
                        onClick={() => config.pagination!.onPageChange(config.pagination!.currentPage + 1)}
                        disabled={config.pagination.currentPage === config.pagination.totalPages}
                        className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Suivant
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
