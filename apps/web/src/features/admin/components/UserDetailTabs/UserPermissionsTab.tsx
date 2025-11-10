import { useState } from 'react'
import { UserDetail, useGetUserGroupsQuery, useGetUserProfilesQuery, useAssignGroupMutation, useRemoveGroupMutation, useAssignProfileMutation, useRemoveProfileMutation } from '../../api/userDetailsApi'
import { useListGroupsQuery, useListProfilesQuery } from '@/features/iam/api/iamApi'
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { BADGE_VARIANTS } from '@/constants/ui'

interface UserPermissionsTabProps {
  userId: string
  userDetail: UserDetail
}

export default function UserPermissionsTab({ userId, userDetail }: UserPermissionsTabProps) {
  const { data: userGroups = [], isLoading: loadingGroups } = useGetUserGroupsQuery(userId)
  const { data: userProfiles = [], isLoading: loadingProfiles } = useGetUserProfilesQuery(userId)
  const { data: allGroupsData } = useListGroupsQuery({})
  const { data: allProfilesData } = useListProfilesQuery({})
  
  const allGroups = Array.isArray(allGroupsData) ? allGroupsData : []
  const allProfiles = Array.isArray(allProfilesData) ? allProfilesData : []
  
  const [assignGroup] = useAssignGroupMutation()
  const [removeGroup] = useRemoveGroupMutation()
  const [assignProfile] = useAssignProfileMutation()
  const [removeProfile] = useRemoveProfileMutation()
  
  const [selectedGroup, setSelectedGroup] = useState('')
  const [selectedProfile, setSelectedProfile] = useState('')

  const handleAssignGroup = async () => {
    if (!selectedGroup) return
    
    try {
      await assignGroup({ userId, data: { group_id: selectedGroup } }).unwrap()
      toast.success('Groupe assigné avec succès')
      setSelectedGroup('')
    } catch (error: any) {
      toast.error(error?.data?.message || 'Erreur lors de l\'assignation')
    }
  }

  const handleRemoveGroup = async (groupId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir retirer ce groupe ?')) return
    
    try {
      await removeGroup({ userId, groupId }).unwrap()
      toast.success('Groupe retiré avec succès')
    } catch (error: any) {
      toast.error(error?.data?.message || 'Erreur lors du retrait')
    }
  }

  const handleAssignProfile = async () => {
    if (!selectedProfile) return
    
    try {
      await assignProfile({ userId, data: { profile_id: selectedProfile } }).unwrap()
      toast.success('Profil assigné avec succès')
      setSelectedProfile('')
    } catch (error: any) {
      toast.error(error?.data?.message || 'Erreur lors de l\'assignation')
    }
  }

  const handleRemoveProfile = async (profileId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir retirer ce profil ?')) return
    
    try {
      await removeProfile({ userId, profileId }).unwrap()
      toast.success('Profil retiré avec succès')
    } catch (error: any) {
      toast.error(error?.data?.message || 'Erreur lors du retrait')
    }
  }

  const availableGroups = Array.isArray(allGroups) 
    ? allGroups.filter(g => !userGroups.some(ug => ug.id === g.id))
    : []
  
  const availableProfiles = Array.isArray(allProfiles)
    ? allProfiles.filter(p => !userProfiles.some(up => up.id === p.id))
    : []

  return (
    <div className="space-y-6">
      {/* Groupes IAM */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Groupes IAM</h3>
          <div className="flex gap-2">
            <select
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              disabled={availableGroups.length === 0}
            >
              <option value="">Sélectionner un groupe</option>
              {availableGroups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleAssignGroup}
              disabled={!selectedGroup}
              className="px-4 py-2 bg-jlc-purple-600 text-white rounded-md hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <PlusIcon className="h-4 w-4" />
              Ajouter
            </button>
          </div>
        </div>
        
        {loadingGroups ? (
          <div className="animate-pulse space-y-2">
            <div className="h-12 bg-gray-200 rounded"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
          </div>
        ) : userGroups.length === 0 ? (
          <p className="text-gray-500 text-sm">Aucun groupe assigné</p>
        ) : (
          <div className="space-y-2">
            {userGroups.map((group) => (
              <div key={group.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <p className="font-medium text-gray-900">{group.name}</p>
                  <p className="text-xs text-gray-500">{group.code}</p>
                  {group.description && (
                    <p className="text-xs text-gray-500 mt-1">{group.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleRemoveGroup(group.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                  title="Retirer"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Profils IAM */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Profils IAM</h3>
          <div className="flex gap-2">
            <select
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              disabled={availableProfiles.length === 0}
            >
              <option value="">Sélectionner un profil</option>
              {availableProfiles.map((profile) => (
                <option key={profile.id} value={profile.id}>
                  {profile.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleAssignProfile}
              disabled={!selectedProfile}
              className="px-4 py-2 bg-jlc-purple-600 text-white rounded-md hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <PlusIcon className="h-4 w-4" />
              Ajouter
            </button>
          </div>
        </div>
        
        {loadingProfiles ? (
          <div className="animate-pulse space-y-2">
            <div className="h-12 bg-gray-200 rounded"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
          </div>
        ) : userProfiles.length === 0 ? (
          <p className="text-gray-500 text-sm">Aucun profil assigné</p>
        ) : (
          <div className="space-y-2">
            {userProfiles.map((profile) => (
              <div key={profile.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center gap-3">
                  {profile.icon && <span className="text-2xl">{profile.icon}</span>}
                  <div>
                    <p className="font-medium text-gray-900">{profile.name}</p>
                    <p className="text-xs text-gray-500">{profile.code}</p>
                    {profile.description && (
                      <p className="text-xs text-gray-500 mt-1">{profile.description}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleRemoveProfile(profile.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                  title="Retirer"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Permissions héritées */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Permissions Héritées</h3>
        {!userDetail.permissions || userDetail.permissions.length === 0 ? (
          <p className="text-gray-500 text-sm">Aucune permission</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {userDetail.permissions.map((permission) => (
              <span key={permission} className={`px-3 py-1 rounded-full text-xs font-semibold ${BADGE_VARIANTS.info}`}>
                {permission}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
