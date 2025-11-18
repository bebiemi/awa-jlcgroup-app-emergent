import { useState } from 'react'
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import {
  useGetProfileRolesQuery,
  useListIAMRolesQuery,
  useAssignRolesToProfileMutation,
  useRemoveRoleFromProfileMutation
} from '@/features/iam/api/iamApi'

interface ProfileIAMRolesSectionProps {
  profileId: string
  profileName: string
}

export default function ProfileIAMRolesSection({ profileId, profileName }: ProfileIAMRolesSectionProps) {
  const { data: profileRolesData, isLoading: loadingProfileRoles } = useGetProfileRolesQuery(profileId)
  const { data: allIAMRoles = [], isLoading: loadingAllRoles } = useListIAMRolesQuery()
  
  const [assignRoles] = useAssignRolesToProfileMutation()
  const [removeRole] = useRemoveRoleFromProfileMutation()
  
  const [selectedRoleId, setSelectedRoleId] = useState('')

  const profileRoles = profileRolesData?.iam_roles || []

  const handleAssignRole = async () => {
    if (!selectedRoleId) {
      toast.error('Veuillez sélectionner un rôle IAM')
      return
    }
    
    try {
      await assignRoles({ 
        profileId, 
        role_ids: [selectedRoleId] 
      }).unwrap()
      
      toast.success('Rôle IAM assigné au profil avec succès')
      setSelectedRoleId('')
    } catch (error: any) {
      const errorMsg = error?.data?.detail || error?.data?.message || 'Erreur lors de l\'assignation du rôle'
      toast.error(errorMsg)
      console.error('Error assigning role:', error)
    }
  }

  const handleRemoveRole = async (roleId: string, roleName: string) => {
    if (!confirm(`Êtes-vous sûr de vouloir retirer le rôle "${roleName}" de ce profil ?`)) {
      return
    }
    
    try {
      await removeRole({ profileId, roleId }).unwrap()
      toast.success('Rôle IAM retiré du profil avec succès')
    } catch (error: any) {
      const errorMsg = error?.data?.detail || error?.data?.message || 'Erreur lors du retrait du rôle'
      toast.error(errorMsg)
      console.error('Error removing role:', error)
    }
  }

  // Filtrer les rôles déjà assignés
  const availableRoles = allIAMRoles.filter(
    (role: any) => !profileRoles.some((pr: any) => pr.id === role.id)
  )

  if (loadingAllRoles) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Rôles IAM Techniques</h3>
          <p className="text-sm text-gray-500 mt-1">
            Rôles IAM assignés au profil <span className="font-medium">{profileName}</span>
          </p>
        </div>
        
        <div className="flex gap-2">
          <select
            value={selectedRoleId}
            onChange={(e) => setSelectedRoleId(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
            disabled={availableRoles.length === 0}
          >
            <option value="">Sélectionner un rôle IAM</option>
            {availableRoles.map((role: any) => (
              <option key={role.id} value={role.id}>
                {role.label || role.code} ({role.profile_count || 0} profil{role.profile_count > 1 ? 's' : ''})
              </option>
            ))}
          </select>
          
          <button
            onClick={handleAssignRole}
            disabled={!selectedRoleId || availableRoles.length === 0}
            className="px-4 py-2 bg-jlc-purple-600 text-white rounded-md hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            Ajouter
          </button>
        </div>
      </div>
      
      {loadingProfileRoles ? (
        <div className="animate-pulse space-y-2">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      ) : profileRoles.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-500 text-sm">Aucun rôle IAM assigné à ce profil</p>
          <p className="text-xs text-gray-400 mt-1">
            Les rôles IAM sont des permissions techniques avancées
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {profileRoles.map((role: any) => (
            <div 
              key={role.id} 
              className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-white border border-purple-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-900">{role.label || role.code}</p>
                  <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded">
                    IAM Role
                  </span>
                </div>
                
                {role.description && (
                  <p className="text-sm text-gray-600 mt-1">{role.description}</p>
                )}
                
                {role.permissions && role.permissions.length > 0 && (
                  <p className="text-xs text-gray-500 mt-2">
                    {role.permissions.length} permission(s) incluse(s)
                  </p>
                )}
              </div>
              
              <button
                onClick={() => handleRemoveRole(role.id, role.label || role.code)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
                title="Retirer ce rôle"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}
      
      {profileRoles.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-blue-800">
            <strong>Note:</strong> Les utilisateurs avec ce profil hériteront automatiquement 
            des permissions de ces rôles IAM (modèle hybride).
          </p>
        </div>
      )}
    </div>
  )
}
