/**
 * Composant de Détail des Permissions d'un Profil
 * Affiche les permissions directes vs celles venant des bundles
 */
import React, { useEffect, useState } from 'react';
import { ShieldCheckIcon, CubeIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface PermissionBreakdownProps {
  profileId: string;
}

interface EffectivePermissionsResponse {
  profile_id: string;
  profile_code: string;
  profile_name: string;
  direct_permission_count: number;
  bundle_permission_count: number;
  total_effective_permissions: number;
  permissions: Array<{
    id: string;
    code: string;
    name: string;
    description?: string;
    category: string;
    resource: string;
    action: string;
    scope?: string;
  }>;
  capability_bundle_ids: string[];
}

interface Bundle {
  id: string;
  code: string;
  name: string;
  description: string;
  permission_ids: string[];
}

const ProfilePermissionsBreakdown: React.FC<PermissionBreakdownProps> = ({ profileId }) => {
  const [data, setData] = useState<EffectivePermissionsResponse | null>(null);
  const [bundles, setBundles] = useState<Bundle[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'direct' | 'bundles'>('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Récupérer le token d'authentification
        const token = localStorage.getItem('access_token');
        
        // Déterminer le baseUrl
        const getBaseUrl = () => {
          if (typeof window === 'undefined') return '/api';
          
          const isHTTPS = window.location.protocol === 'https:';
          const hostname = window.location.hostname;
          const isEmergentPreview = hostname.includes('preview.emergentagent.com') || hostname.includes('emergent.host');
          
          if (isHTTPS && isEmergentPreview) {
            return `https://${hostname}/api`;
          }
          
          return '/api';
        };
        
        const baseUrl = getBaseUrl();
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };
        
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Récupérer les permissions effectives
        const effectiveRes = await fetch(
          `${baseUrl}/iam/profiles/${profileId}/effective-permissions`,
          { headers }
        );
        
        if (!effectiveRes.ok) {
          throw new Error('Erreur lors du chargement des permissions');
        }
        
        const effectiveData = await effectiveRes.json();
        setData(effectiveData);

        // Récupérer les détails des bundles
        if (effectiveData.capability_bundle_ids && effectiveData.capability_bundle_ids.length > 0) {
          const bundlesRes = await fetch(`${baseUrl}/iam/bundles`, { headers });
          
          if (bundlesRes.ok) {
            const bundlesData = await bundlesRes.json();
            const profileBundles = bundlesData.filter((b: Bundle) =>
              effectiveData.capability_bundle_ids.includes(b.id)
            );
            setBundles(profileBundles);
          }
        }
      } catch (error) {
        console.error('Erreur chargement permissions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [profileId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-8 text-gray-500">
        Impossible de charger les permissions
      </div>
    );
  }

  // Identifier quelles permissions viennent des bundles
  const bundlePermissionIds = new Set<string>();
  bundles.forEach(bundle => {
    bundle.permission_ids.forEach(permId => bundlePermissionIds.add(permId));
  });

  const directPermissions = data.permissions.filter(p => !bundlePermissionIds.has(p.id));
  const bundlePermissions = data.permissions.filter(p => bundlePermissionIds.has(p.id));

  const displayedPermissions = 
    activeTab === 'direct' ? directPermissions :
    activeTab === 'bundles' ? bundlePermissions :
    data.permissions;

  return (
    <div className="space-y-4">
      {/* Statistiques */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircleIcon className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Total</span>
          </div>
          <p className="text-2xl font-bold text-blue-900">
            {data.total_effective_permissions}
          </p>
          <p className="text-xs text-gray-600 mt-1">permissions effectives</p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheckIcon className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-700">Directes</span>
          </div>
          <p className="text-2xl font-bold text-green-900">
            {data.direct_permission_count}
          </p>
          <p className="text-xs text-gray-600 mt-1">assignées directement</p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CubeIcon className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">Via Bundles</span>
          </div>
          <p className="text-2xl font-bold text-purple-900">
            {data.bundle_permission_count}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            depuis {bundles.length} bundle(s)
          </p>
        </div>
      </div>

      {/* Bundles utilisés */}
      {bundles.length > 0 && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <CubeIcon className="h-5 w-5 text-purple-600" />
            Bundles de Capacités Utilisés
          </h4>
          <div className="space-y-2">
            {bundles.map((bundle) => (
              <div key={bundle.id} className="bg-white border border-purple-200 rounded p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">{bundle.name}</p>
                    <p className="text-xs text-gray-500 font-mono mb-1">{bundle.code}</p>
                    {bundle.description && (
                      <p className="text-xs text-gray-600 leading-relaxed">
                        {bundle.description}
                      </p>
                    )}
                  </div>
                  <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded font-medium">
                    {bundle.permission_ids.length} perms
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-4">
          <button
            onClick={() => setActiveTab('all')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'all'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Toutes ({data.total_effective_permissions})
          </button>
          <button
            onClick={() => setActiveTab('direct')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'direct'
                ? 'border-green-600 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Directes ({data.direct_permission_count})
          </button>
          <button
            onClick={() => setActiveTab('bundles')}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'bundles'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Via Bundles ({data.bundle_permission_count})
          </button>
        </nav>
      </div>

      {/* Liste des permissions */}
      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {displayedPermissions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune permission dans cette catégorie
          </div>
        ) : (
          displayedPermissions.map((perm) => {
            const isFromBundle = bundlePermissionIds.has(perm.id);
            return (
              <div
                key={perm.id}
                className={`p-3 border rounded-lg ${
                  isFromBundle
                    ? 'bg-purple-50 border-purple-200'
                    : 'bg-green-50 border-green-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {isFromBundle ? (
                      <CubeIcon className="h-4 w-4 text-purple-600" />
                    ) : (
                      <ShieldCheckIcon className="h-4 w-4 text-green-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm text-gray-900">
                        {perm.name}
                      </span>
                      <span className="px-2 py-0.5 text-xs rounded bg-white border border-gray-300 text-gray-700">
                        {perm.category}
                      </span>
                      {isFromBundle && (
                        <span className="px-2 py-0.5 text-xs rounded bg-purple-100 text-purple-700">
                          Bundle
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-600 font-mono mb-1">{perm.code}</p>
                    {perm.description && (
                      <p className="text-xs text-gray-500 leading-relaxed">
                        {perm.description}
                      </p>
                    )}
                    <div className="flex gap-2 mt-2 text-xs text-gray-400">
                      <span>Ressource: {perm.resource}</span>
                      <span>•</span>
                      <span>Action: {perm.action}</span>
                      {perm.scope && perm.scope !== 'global' && (
                        <>
                          <span>•</span>
                          <span>Scope: {perm.scope}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ProfilePermissionsBreakdown;
