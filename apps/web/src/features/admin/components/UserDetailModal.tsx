import { Fragment, useState, useEffect } from 'react'
import { Dialog, Transition, Tab } from '@headlessui/react'
import { XMarkIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import { USER_DETAIL_TABS, MODAL_SIZES, SHADOWS, ROUNDED } from '@/constants/ui'
import { useGetUserDetailQuery, useToggleEmailVerificationMutation, useMarkUserAsViewedMutation } from '../api/userDetailsApi'
import UserInfoTab from './UserDetailTabs/UserInfoTab'
import UserDocumentsTab from './UserDetailTabs/UserDocumentsTab'
import UserPermissionsTab from './UserDetailTabs/UserPermissionsTab'
import UserActivityTab from './UserDetailTabs/UserActivityTab'
import toast from 'react-hot-toast'

interface UserDetailModalProps {
  isOpen: boolean
  onClose: () => void
  userId: string
}

export default function UserDetailModal({ isOpen, onClose, userId }: UserDetailModalProps) {
  const { data: userDetail, isLoading, error } = useGetUserDetailQuery(userId, {
    skip: !isOpen || !userId,
  })
  const [toggleEmailVerification, { isLoading: isToggling }] = useToggleEmailVerificationMutation()
  const [isVerifying, setIsVerifying] = useState(false)

  const tabs = [
    { ...USER_DETAIL_TABS.INFO, component: UserInfoTab },
    { ...USER_DETAIL_TABS.DOCUMENTS, component: UserDocumentsTab },
    { ...USER_DETAIL_TABS.PERMISSIONS, component: UserPermissionsTab },
    { ...USER_DETAIL_TABS.ACTIVITY, component: UserActivityTab },
  ]

  const handleToggleEmailVerification = async () => {
    if (!userDetail) return
    
    const newStatus = !userDetail.is_verified
    const action = newStatus ? 'vérifier' : 'dévérifier'
    
    if (!confirm(`Êtes-vous sûr de vouloir ${action} l'email de ${userDetail.username} ?`)) {
      return
    }

    setIsVerifying(true)
    try {
      await toggleEmailVerification({
        user_id: userDetail.id,
        is_verified: newStatus,
        reason: `Manuel ${action}ication par admin depuis la modal utilisateur`
      }).unwrap()
      
      toast.success(`Email ${newStatus ? 'vérifié' : 'dévérifié'} avec succès`)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la modification')
    } finally {
      setIsVerifying(false)
    }
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className={`w-full ${MODAL_SIZES.xl} transform overflow-hidden ${ROUNDED['2xl']} bg-white text-left align-middle ${SHADOWS.xl} transition-all`}>
                {/* Header */}
                <div className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-700 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      {isLoading ? (
                        <div className="animate-pulse">
                          <div className="h-6 bg-white/20 rounded w-48 mb-2"></div>
                          <div className="h-4 bg-white/20 rounded w-64"></div>
                        </div>
                      ) : userDetail ? (
                        <>
                          <Dialog.Title className="text-xl font-bold text-white">
                            {userDetail.full_name || userDetail.username}
                          </Dialog.Title>
                          <p className="text-sm text-white/80 mt-1">
                            {userDetail.email}
                          </p>
                        </>
                      ) : (
                        <Dialog.Title className="text-xl font-bold text-white">
                          Détails utilisateur
                        </Dialog.Title>
                      )}
                    </div>
                    <button
                      onClick={onClose}
                      className="text-white hover:text-white/80 transition-colors"
                    >
                      <XMarkIcon className="h-6 w-6" />
                    </button>
                  </div>

                  {/* Status Bar */}
                  {userDetail && (
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          userDetail.status === 'active' 
                            ? 'bg-green-500 text-white' 
                            : userDetail.status === 'pending'
                            ? 'bg-yellow-500 text-white'
                            : 'bg-red-500 text-white'
                        }`}>
                          {userDetail.status === 'active' ? '✓ Actif' : 
                           userDetail.status === 'pending' ? '⏱ En attente' : 
                           '⊗ Suspendu'}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          userDetail.is_verified 
                            ? 'bg-green-500 text-white' 
                            : 'bg-yellow-500 text-white'
                        }`}>
                          {userDetail.is_verified ? '✓ Email vérifié' : '⚠️ Email non vérifié'}
                        </span>
                        {userDetail.mfa_enabled && (
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500 text-white">
                            🔐 MFA Activé
                          </span>
                        )}
                        {userDetail.last_activity_at && (
                          <span className="text-xs text-white/70">
                            Dernière activité: {new Date(userDetail.last_activity_at).toLocaleString('fr-FR')}
                          </span>
                        )}
                      </div>
                      
                      {/* Quick Actions */}
                      <div className="flex items-center gap-2">
                        <button
                          onClick={handleToggleEmailVerification}
                          disabled={isVerifying}
                          className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                            userDetail.is_verified
                              ? 'bg-white/20 hover:bg-white/30 text-white'
                              : 'bg-yellow-500 hover:bg-yellow-600 text-white'
                          } disabled:opacity-50 disabled:cursor-not-allowed`}
                          title={userDetail.is_verified ? 'Dévérifier l\'email (tests)' : 'Vérifier l\'email manuellement'}
                        >
                          <ShieldCheckIcon className="h-4 w-4" />
                          {isVerifying ? 'Modification...' : userDetail.is_verified ? 'Dévérifier' : 'Vérifier email'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="bg-gray-50">
                  {isLoading ? (
                    <div className="p-6">
                      <div className="animate-pulse space-y-4">
                        <div className="h-12 bg-gray-200 rounded"></div>
                        <div className="h-64 bg-gray-200 rounded"></div>
                      </div>
                    </div>
                  ) : error ? (
                    <div className="p-6 text-center">
                      <p className="text-red-600">Erreur lors du chargement des détails</p>
                    </div>
                  ) : userDetail ? (
                    <Tab.Group>
                      <Tab.List className="flex space-x-1 bg-white border-b px-6">
                        {tabs.map((tab) => (
                          <Tab
                            key={tab.id}
                            className={({ selected }) =>
                              `py-3 px-4 text-sm font-medium leading-5 transition-all
                              ${selected
                                ? 'border-b-2 border-jlc-purple-600 text-jlc-purple-700'
                                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                              }`
                            }
                          >
                            <span className="mr-2">{tab.icon}</span>
                            {tab.label}
                          </Tab>
                        ))}
                      </Tab.List>
                      <Tab.Panels className="p-6">
                        {tabs.map((tab) => {
                          const TabComponent = tab.component
                          return (
                            <Tab.Panel key={tab.id}>
                              <TabComponent userId={userId} userDetail={userDetail} />
                            </Tab.Panel>
                          )
                        })}
                      </Tab.Panels>
                    </Tab.Group>
                  ) : null}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
