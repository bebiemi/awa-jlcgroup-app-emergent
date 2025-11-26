import React from 'react';
import { useGetTemplatesQuery, useInitDefaultTemplatesMutation } from '../api/emailTemplatesApi';
import { usePermissions } from '@/hooks/usePermission';

export const EmailTemplatesPage: React.FC = () => {
  const { data, isLoading } = useGetTemplatesQuery({});
  const [initDefaults, { isLoading: isInitializing }] = useInitDefaultTemplatesMutation();
  const { permissions } = usePermissions(['emails.manage_templates', 'emails.read_config'])
  const canRead = permissions['emails.read_config'] || permissions['emails.manage_templates']
  const canManage = permissions['emails.manage_templates']

  const handleInitDefaults = async () => {
    if (!canManage) return
    try {
      await initDefaults().unwrap();
      alert('Templates par défaut créés avec succès !');
    } catch (err: any) {
      alert(`Erreur: ${err.data?.detail || 'Erreur inconnue'}`);
    }
  };

  if (!canRead) return null;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Templates Email</h1>
          <p className="text-gray-600 mt-2">Gérer les templates d'email personnalisables</p>
        </div>
        {canManage && (
          <button
            onClick={handleInitDefaults}
            disabled={isInitializing}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {isInitializing ? 'Initialisation...' : 'Initialiser Templates'}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.templates.map((template) => (
          <div key={template.id} className="bg-white shadow rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                <p className="text-sm text-gray-600">{template.type}</p>
              </div>
              {template.is_system && (
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                  Système
                </span>
              )}
            </div>

            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700">Sujet:</p>
              <p className="text-sm text-gray-600">{template.subject}</p>
            </div>

            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700">Variables:</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {template.variables.map((v) => (
                  <span key={v} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                    {v}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className={`text-sm ${template.is_active ? 'text-green-600' : 'text-gray-500'}`}>
                {template.is_active ? 'Actif' : 'Inactif'}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(template.updated_at).toLocaleDateString('fr-FR')}
              </span>
            </div>
          </div>
        ))}
      </div>

      {(!data || data.templates.length === 0) && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <p className="text-yellow-700">
            Aucun template trouvé. Cliquez sur "Initialiser Templates" pour créer les templates par défaut.
          </p>
        </div>
      )}
    </div>
  );
};
