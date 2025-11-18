import { useState } from 'react'
import { useListProfilesQuery, useListGroupsQuery, useListIAMRolesQuery } from '../api/iamApi'
import Layout from '@/components/Layout'
import ProfileIAMRolesSection from '@/features/admin/components/ProfileIAMRolesSection'
import GroupIAMRolesSection from '@/features/admin/components/GroupIAMRolesSection'
import ProfilePermissionsDisplay from '../components/ProfilePermissionsDisplay'
import { ChevronDownIcon, ChevronRightIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function IAMRolesManagementPage() {
  const { data: profiles = [], isLoading: profilesLoading } = useListProfilesQuery()
  const { data: groups = [], isLoading: groupsLoading } = useListGroupsQuery()
  const { data: iamRoles = [], isLoading: iamRolesLoading } = useListIAMRolesQuery()
  
  const [expandedProfiles, setExpandedProfiles] = useState<Set<string>>(new Set())
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())

  const toggleProfile = (profileId: string) => {
    setExpandedProfiles(prev => {
      const newSet = new Set(prev)
      if (newSet.has(profileId)) {
        newSet.delete(profileId)
      } else {
        newSet.add(profileId)
      }
      return newSet
    })
  }

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev)
      if (newSet.has(groupId)) {
        newSet.delete(groupId)
      } else {
        newSet.add(groupId)
      }
      return newSet
    })
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Rôles IAM</h1>
          <p className="mt-2 text-gray-600">
            Assignez des rôles IAM techniques aux profils métier et aux groupes organisationnels
          </p>
          
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">📚 Modèle IAM Hybride</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Profils métier</strong> : Rôles métier (Intérimaire, Entreprise, etc.)</li>
              <li>• <strong>Groupes organisationnels</strong> : Équipes (RH, Commercial, etc.)</li>
              <li>• <strong>Rôles IAM</strong> : Permissions techniques avancées (Auditor, etc.)</li>
              <li>• <strong>Utilisateurs</strong> : Héritent automatiquement des permissions de leurs profils/groupes + rôles IAM</li>
            </ul>
          </div>
        </div>

        {/* IAM Roles Overview Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Vue d'ensemble des Rôles IAM ({iamRoles.length})
          </h2>
          
          {iamRolesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse bg-gray-100 h-32 rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {iamRoles.map((role: any) => (
                <div key={role.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <ShieldCheckIcon className="h-5 w-5 text-purple-600" />
                      <h3 className="font-semibold text-gray-900">{role.label || role.code}</h3>
                    </div>
                    <span className="px-2 py-1 text-xs font-bold bg-purple-100 text-purple-700 rounded-full">
                      {role.profile_count || 0}
                    </span>
                  </div>
                  
                  {role.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{role.description}</p>
                  )}
                  
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">
                      {role.permissions?.length || 0} permission(s)
                    </span>
                    <span className="text-gray-500">
                      {role.profile_count || 0} profil{role.profile_count > 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Profiles Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Profils Métier ({profiles.length})
          </h2>
          
          {profilesLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse bg-gray-100 h-20 rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {profiles.filter((profile: any) => profile.id).map((profile: any) => (
                <div key={profile.id} className="bg-white rounded-lg shadow-sm border border-gray-200">
                  {/* Profile Header */}
                  <button
                    onClick={() => toggleProfile(profile.id)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: profile.color || '#6366F1' }}
                      />
                      <div className="text-left">
                        <h3 className="font-semibold text-gray-900">{profile.name}</h3>
                        <p className="text-sm text-gray-500">{profile.description}</p>
                      </div>
                      <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                        {profile.permission_ids?.length || 0} permissions
                      </span>
                    </div>
                    
                    {expandedProfiles.has(profile.id) ? (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  
                  {/* IAM Roles Section (collapsible) */}
                  {expandedProfiles.has(profile.id) && (
                    <div className="px-6 pb-6">
                      <ProfileIAMRolesSection 
                        profileId={profile.id}
                        profileName={profile.name}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Groups Section */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Groupes Organisationnels ({groups.length})
          </h2>
          
          {groupsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="animate-pulse bg-gray-100 h-20 rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {groups.filter((group: any) => group.id).map((group: any) => (
                <div key={group.id} className="bg-white rounded-lg shadow-sm border border-gray-200">
                  {/* Group Header */}
                  <button
                    onClick={() => toggleGroup(group.id)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="text-left">
                        <h3 className="font-semibold text-gray-900">{group.name}</h3>
                        <p className="text-sm text-gray-500">{group.description}</p>
                      </div>
                      <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                        {group.member_count || 0} membres
                      </span>
                    </div>
                    
                    {expandedGroups.has(group.id) ? (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                  
                  {/* IAM Roles Section (collapsible) */}
                  {expandedGroups.has(group.id) && (
                    <div className="px-6 pb-6">
                      <GroupIAMRolesSection 
                        groupId={group.id}
                        groupName={group.name}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
