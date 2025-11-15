import { useState } from 'react'
import Layout from '@/components/Layout'
import { useGetMyProfileQuery, useUpdateMyProfileMutation } from '../api/profileApi'
import InterimProfileForm from '../components/InterimProfileForm'
import CompanyProfileForm from '../components/CompanyProfileForm'
import CandidatProfileForm from '../components/CandidatProfileForm'
import DocumentsSection from '../components/DocumentsSection'
import { UserCircleIcon, DocumentTextIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { data, isLoading } = useGetMyProfileQuery()
  const [updateProfile] = useUpdateMyProfileMutation()
  const [activeTab, setActiveTab] = useState<'info' | 'documents'>('info')

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  const profileType = data?.profile_type
  const profile = data?.profile

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
          <p className="text-gray-600 mt-2">
            Gérez vos informations personnelles et professionnelles
          </p>
          
          {profile?.profile_completion_percentage !== undefined && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Complétude du profil
                </span>
                <span className="text-sm font-semibold text-jlc-purple-600">
                  {profile.profile_completion_percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-jlc-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${profile.profile_completion_percentage}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('info')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'info'
                  ? 'border-jlc-purple-600 text-jlc-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <UserCircleIcon className="h-5 w-5 inline mr-2" />
              Informations
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'documents'
                  ? 'border-jlc-purple-600 text-jlc-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <DocumentTextIcon className="h-5 w-5 inline mr-2" />
              Documents
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'info' && (
            <>
              {profileType === 'interim' && <InterimProfileForm profile={profile} />}
              {profileType === 'company' && <CompanyProfileForm profile={profile} />}
              {profileType === 'collaborator' && (
                <div className="text-center py-12 text-gray-500">
                  <p>Profil collaborateur - Configuration minimale</p>
                </div>
              )}
            </>
          )}

          {activeTab === 'documents' && <DocumentsSection />}
        </div>
      </div>
    </Layout>
  )
}
