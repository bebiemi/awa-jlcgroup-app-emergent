import { Fragment, useState } from 'react'
import { Dialog, Transition, Tab } from '@headlessui/react'
import { XMarkIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import { USER_DETAIL_TABS, MODAL_SIZES, SHADOWS, ROUNDED } from '@/constants/ui'
import { useGetUserDetailQuery, useToggleEmailVerificationMutation } from '../api/userDetailsApi'
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

  const tabs = [
    { ...USER_DETAIL_TABS.INFO, component: UserInfoTab },
    { ...USER_DETAIL_TABS.DOCUMENTS, component: UserDocumentsTab },
    { ...USER_DETAIL_TABS.PERMISSIONS, component: UserPermissionsTab },
    { ...USER_DETAIL_TABS.ACTIVITY, component: UserActivityTab },
  ]

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
                    <div className="flex items-center gap-3 mt-4">
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
