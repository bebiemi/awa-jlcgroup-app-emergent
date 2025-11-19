/**
 * Sélecteur de permissions à deux colonnes
 * Colonne gauche: Permissions disponibles
 * Colonne droite: Permissions attribuées
 */
import React, { useState, useMemo } from 'react';
import { Permission } from '../api/iamApi';
import { MagnifyingGlassIcon, ArrowRightIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface DualColumnPermissionSelectorProps {
  allPermissions: Permission[];
  selectedPermissionIds: string[];
  onAdd: (permissionId: string) => void;
  onRemove: (permissionId: string) => void;
  disabled?: boolean;
}

type SortBy = 'name' | 'category' | 'resource' | 'action';

const DualColumnPermissionSelector: React.FC<DualColumnPermissionSelectorProps> = ({
  allPermissions,
  selectedPermissionIds,
  onAdd,
  onRemove,
  disabled = false,
}) => {
  const [searchLeft, setSearchLeft] = useState('');
  const [searchRight, setSearchRight] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('category');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  // Permissions disponibles (non sélectionnées)
  const availablePermissions = useMemo(() => {
    return allPermissions.filter(p => !selectedPermissionIds.includes(p.id));
  }, [allPermissions, selectedPermissionIds]);

  // Permissions attribuées
  const assignedPermissions = useMemo(() => {
    return allPermissions.filter(p => selectedPermissionIds.includes(p.id));
  }, [allPermissions, selectedPermissionIds]);

  // Fonction de tri
  const sortPermissions = (perms: Permission[]): Permission[] => {
    return [...perms].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'category':
          return a.category.localeCompare(b.category) || a.name.localeCompare(b.name);
        case 'resource':
          return a.resource.localeCompare(b.resource) || a.name.localeCompare(b.name);
        case 'action':
          return a.action.localeCompare(b.action) || a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });
  };

  // Filtrer permissions disponibles
  const filteredAvailable = useMemo(() => {
    let filtered = availablePermissions.filter(p => {
      const matchesSearch = 
        p.name.toLowerCase().includes(searchLeft.toLowerCase()) ||
        p.code.toLowerCase().includes(searchLeft.toLowerCase()) ||
        (p.description && p.description.toLowerCase().includes(searchLeft.toLowerCase()));
      
      const matchesCategory = filterCategory === 'all' || p.category === filterCategory;
      
      return matchesSearch && matchesCategory;
    });
    
    return sortPermissions(filtered);
  }, [availablePermissions, searchLeft, filterCategory, sortBy]);

  // Filtrer permissions attribuées
  const filteredAssigned = useMemo(() => {
    let filtered = assignedPermissions.filter(p =>
      p.name.toLowerCase().includes(searchRight.toLowerCase()) ||
      p.code.toLowerCase().includes(searchRight.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(searchRight.toLowerCase()))
    );
    
    return sortPermissions(filtered);
  }, [assignedPermissions, searchRight, sortBy]);

  // Catégories uniques
  const categories = useMemo(() => {
    const cats = new Set(allPermissions.map(p => p.category));
    return ['all', ...Array.from(cats)].filter(c => c !== 'all' || c === 'all');
  }, [allPermissions]);

  // Composant pour afficher une permission
  const PermissionCard: React.FC<{
    permission: Permission;
    onAction: () => void;
    actionIcon: React.ReactNode;
    actionLabel: string;
  }> = ({ permission, onAction, actionIcon, actionLabel }) => (
    <div className="group p-3 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-medium text-sm text-gray-900 truncate">
              {permission.name}
            </span>
            <span className="px-2 py-0.5 text-xs rounded border border-gray-300 text-gray-700 bg-white">
              {permission.category}
            </span>
          </div>
          
          <p className="text-xs text-gray-600 font-mono mb-1">
            {permission.code}
          </p>
          
          {permission.description && (
            <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
              {permission.description}
            </p>
          )}
          
          {!permission.description && (
            <p className="text-xs text-gray-400 italic">
              Description indisponible
            </p>
          )}
          
          <div className="flex gap-2 mt-2 text-xs text-gray-400">
            <span>Ressource: {permission.resource}</span>
            <span>•</span>
            <span>Action: {permission.action}</span>
            {permission.scope && permission.scope !== 'global' && (
              <>
                <span>•</span>
                <span>Scope: {permission.scope}</span>
              </>
            )}
          </div>
        </div>
        
        <button
          onClick={onAction}
          disabled={disabled}
          className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title={actionLabel}
        >
          {actionIcon}
        </button>
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex gap-2 items-center">
        <select 
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value as SortBy)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={disabled}
        >
          <option value="category">Trier par: Catégorie</option>
          <option value="name">Trier par: Nom</option>
          <option value="resource">Trier par: Ressource</option>
          <option value="action">Trier par: Action</option>
        </select>

        <select 
          value={filterCategory} 
          onChange={(e) => setFilterCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={disabled}
        >
          <option value="all">Toutes catégories</option>
          {categories.filter(c => c !== 'all').map(cat => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Two Columns */}
      <div className="grid grid-cols-2 gap-4">
        {/* Left Column: Available */}
        <div className="border-2 border-gray-200 rounded-lg p-4 bg-white">
          <div className="mb-3">
            <h3 className="font-semibold text-gray-900 mb-2">
              Permissions Disponibles
            </h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Rechercher..."
                value={searchLeft}
                onChange={(e) => setSearchLeft(e.target.value)}
                className="pl-10"
                disabled={disabled}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {filteredAvailable.length} permission(s)
            </p>
          </div>
          
          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
            {filteredAvailable.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">
                Aucune permission disponible
              </p>
            ) : (
              filteredAvailable.map((perm) => (
                <PermissionCard
                  key={perm.id}
                  permission={perm}
                  onAction={() => onAdd(perm.id)}
                  actionIcon={<ArrowRight className="h-4 w-4" />}
                  actionLabel="Ajouter"
                />
              ))
            )}
          </div>
        </div>

        {/* Right Column: Assigned */}
        <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
          <div className="mb-3">
            <h3 className="font-semibold text-gray-900 mb-2">
              Permissions Attribuées
            </h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Rechercher..."
                value={searchRight}
                onChange={(e) => setSearchRight(e.target.value)}
                className="pl-10 bg-white"
                disabled={disabled}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {filteredAssigned.length} permission(s)
            </p>
          </div>
          
          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
            {filteredAssigned.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">
                Aucune permission attribuée
              </p>
            ) : (
              filteredAssigned.map((perm) => (
                <PermissionCard
                  key={perm.id}
                  permission={perm}
                  onAction={() => onRemove(perm.id)}
                  actionIcon={<X className="h-4 w-4" />}
                  actionLabel="Retirer"
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DualColumnPermissionSelector;
