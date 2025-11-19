/**
 * Modal de Visualisation Détaillée d'un Profil
 * Affiche toutes les informations y compris les permissions par source
 */
import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { Profile } from '../api/iamApi';
import ProfilePermissionsBreakdown from './ProfilePermissionsBreakdown';

interface ViewProfileDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  profile: Profile | null;
}

const ViewProfileDetailsModal: React.FC<ViewProfileDetailsModalProps> = ({
  isOpen,
  onClose,
  profile,
}) => {
  if (!isOpen || !profile) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {profile.name}
              </h2>
              <p className="text-sm text-gray-500 font-mono mt-1">{profile.code}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Body */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {/* Informations générales */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Informations Générales
              </h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                {profile.description && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Description:</span>
                    <p className="text-sm text-gray-600 mt-1">{profile.description}</p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Catégorie:</span>
                    <p className="text-sm text-gray-900 mt-1">
                      <span className="px-2 py-1 bg-white border border-gray-300 rounded">
                        {profile.category}
                      </span>
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700">Statut:</span>
                    <p className="text-sm text-gray-900 mt-1">
                      {profile.is_system_role && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs mr-2">
                          Système
                        </span>
                      )}
                      {profile.is_protected && (
                        <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
                          Protégé
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-700">Créé le:</span>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(profile.created_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700">Mis à jour le:</span>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(profile.updated_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Détail des permissions */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Détail des Permissions
              </h3>
              <ProfilePermissionsBreakdown profileId={profile.id} />
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewProfileDetailsModal;
