import { useState, useMemo } from 'react'
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'
import { Permission } from '../api/iamApi'

interface PermissionSelectorProps {
  permissions: Permission[]
  selectedPermissionIds: string[]
  onToggle: (permissionId: string) => void
  onToggleCategory: (category: string) => void
  disabled?: boolean
  maxHeight?: string
}

export default function PermissionSelector({
  permissions,
  selectedPermissionIds,
  onToggle,
  onToggleCategory,
  disabled = false,
  maxHeight = 'max-h-96',
}: PermissionSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedScope, setSelectedScope] = useState<string>('all')

  // Extraire les catégories et scopes uniques
  const categories = useMemo(() => {
    const uniqueCategories = new Set(permissions.map((p) => p.category))
    return ['all', ...Array.from(uniqueCategories)]
  }, [permissions])

  const scopes = useMemo(() => {
    const uniqueScopes = new Set(permissions.map((p) => p.scope))
    return ['all', ...Array.from(uniqueScopes)]
  }, [permissions])

  // Filtrer les permissions
  const filteredPermissions = useMemo(() => {
    return permissions.filter((perm) => {
      const matchesSearch =
        searchTerm === '' ||
        perm.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        perm.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (perm.description?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false)

      const matchesCategory = selectedCategory === 'all' || perm.category === selectedCategory
      const matchesScope = selectedScope === 'all' || perm.scope === selectedScope

      return matchesSearch && matchesCategory && matchesScope
    })
  }, [permissions, searchTerm, selectedCategory, selectedScope])

  // Grouper par catégorie
  const permissionsByCategory = useMemo(() => {
    return filteredPermissions.reduce((acc, perm) => {
      if (!acc[perm.category]) {
        acc[perm.category] = []
      }
      acc[perm.category].push(perm)
      return acc
    }, {} as Record<string, Permission[]>)
  }, [filteredPermissions])

  // Labels de catégories
  const categoryLabels: Record<string, string> = {
    all: 'Toutes les catégories',
    admin: 'Administration',
    user: 'Utilisateurs',
    mission: 'Missions',
    application: 'Candidatures',
    profile: 'Profils',
    document: 'Documents',
    rbac: 'Gestion IAM',
    system: 'Système',
    iam: 'IAM',
    auth: 'Authentification',
    email: 'Emails',
  }

  const scopeLabels: Record<string, string> = {
    all: 'Tous les scopes',
    _own: 'Propres ressources',
    _all: 'Toutes les ressources',
    _client: 'Client',
    _team: 'Équipe',
    global: 'Global',
  }

  return (
    <div className="space-y-4">
      {/* Barre de recherche */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Rechercher une permission..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            disabled={disabled}
          />
        </div>
      </div>

      {/* Filtres */}
      <div className="flex gap-3 items-center">
        <FunnelIcon className="h-5 w-5 text-gray-400" />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent text-sm"
          disabled={disabled}
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {categoryLabels[cat] || cat}
            </option>
          ))}
        </select>

        <select
          value={selectedScope}
          onChange={(e) => setSelectedScope(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent text-sm"
          disabled={disabled}
        >
          {scopes.map((scope) => (
            <option key={scope} value={scope}>
              {scopeLabels[scope] || scope}
            </option>
          ))}
        </select>
      </div>

      {/* Compteur */}
      <div className="text-sm text-gray-600">
        {selectedPermissionIds.length} permission(s) sélectionnée(s) sur {permissions.length}
        {filteredPermissions.length < permissions.length &&
          ` (${filteredPermissions.length} affichée(s))`}
      </div>

      {/* Liste des permissions groupées par catégorie */}
      <div className={`space-y-4 border border-gray-300 rounded-lg p-4 ${maxHeight} overflow-y-auto`}>
        {Object.keys(permissionsByCategory).length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            Aucune permission ne correspond aux critères de recherche
          </p>
        ) : (
          Object.entries(permissionsByCategory).map(([category, categoryPerms]) => {
            const categoryPermIds = categoryPerms.map((p) => p.id)
            const allSelected = categoryPermIds.every((id) => selectedPermissionIds.includes(id))
            const someSelected = categoryPermIds.some((id) => selectedPermissionIds.includes(id))

            return (
              <div key={category} className="border border-gray-200 rounded-lg p-4">
                {/* En-tête de catégorie avec case à cocher */}
                <label className="flex items-center cursor-pointer mb-3">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={(input) => {
                      if (input) input.indeterminate = someSelected && !allSelected
                    }}
                    onChange={() => onToggleCategory(category)}
                    disabled={disabled}
                    className="h-5 w-5 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded"
                  />
                  <span className="ml-3 text-sm font-semibold text-gray-900">
                    {categoryLabels[category] || category} ({categoryPerms.length})
                  </span>
                </label>

                {/* Liste des permissions de cette catégorie */}
                <div className="ml-8 space-y-2">
                  {categoryPerms.map((perm) => (
                    <label
                      key={perm.id}
                      className="flex items-start cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={selectedPermissionIds.includes(perm.id)}
                        onChange={() => onToggle(perm.id)}
                        disabled={disabled}
                        className="h-4 w-4 text-jlc-purple-600 focus:ring-jlc-purple-500 border-gray-300 rounded mt-0.5 flex-shrink-0"
                      />
                      <div className="ml-3 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium text-gray-700">{perm.name}</span>
                          <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                            {perm.code}
                          </span>
                          {perm.scope && perm.scope !== 'global' && (
                            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                              {scopeLabels[perm.scope] || perm.scope}
                            </span>
                          )}
                        </div>
                        {perm.description && (
                          <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                            {perm.description}
                          </p>
                        )}
                        <div className="flex gap-2 mt-1 text-xs text-gray-400">
                          <span>Resource: {perm.resource}</span>
                          <span>•</span>
                          <span>Action: {perm.action}</span>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
