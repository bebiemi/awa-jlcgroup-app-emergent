import { Fragment, useState } from 'react'
import { Menu, Transition } from '@headlessui/react'
import { ChevronDownIcon } from '@heroicons/react/24/outline'
import {
  useGetMyPresenceQuery,
  useUpdateMyPresenceMutation,
  PresenceStatus,
} from '@/features/presence/api/presenceApi'
import UserStatusIndicator from './UserStatusIndicator'
import toast from 'react-hot-toast'
import clsx from 'clsx'

interface StatusOption {
  value: PresenceStatus
  label: string
  icon: string
  description: string
}

const STATUS_OPTIONS: StatusOption[] = [
  {
    value: 'online',
    label: 'En ligne',
    icon: '🟢',
    description: 'Disponible pour échanger',
  },
  {
    value: 'do_not_disturb',
    label: 'Ne pas déranger',
    icon: '🔴',
    description: 'En focus, notifications désactivées',
  },
  {
    value: 'offline',
    label: 'Absent',
    icon: '⚪',
    description: 'Hors bureau ou non disponible',
  },
]

interface UserStatusDropdownProps {
  userName?: string
  userEmail?: string
  compact?: boolean
}

export default function UserStatusDropdown({
  userName,
  userEmail,
  compact = false,
}: UserStatusDropdownProps) {
  // CRITICAL: Only fetch if token exists
  const hasToken = !!localStorage.getItem('access_token')
  
  // Use cached data only - Layout component handles the fetching
  const { data: presence, isLoading } = useGetMyPresenceQuery(undefined, {
    skip: !hasToken, // CRITICAL: Skip if no token
    refetchOnMountOrArgChange: false,
    refetchOnFocus: false,
    refetchOnReconnect: false,
  })
  const [updatePresence, { isLoading: isUpdating }] = useUpdateMyPresenceMutation()

  const handleStatusChange = async (status: PresenceStatus) => {
    try {
      await updatePresence({ status }).unwrap()
      const option = STATUS_OPTIONS.find((opt) => opt.value === status)
      toast.success(`Statut changé : ${option?.label}`)
    } catch (error) {
      console.error('Error updating status:', error)
      toast.error('Erreur lors du changement de statut')
    }
  }

  const currentStatus = presence?.presence_status || 'online'
  const currentOption = STATUS_OPTIONS.find((opt) => opt.value === currentStatus)

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2">
        <div className="w-3 h-3 bg-gray-300 rounded-full animate-pulse" />
        {!compact && <div className="w-20 h-4 bg-gray-300 rounded animate-pulse" />}
      </div>
    )
  }

  return (
    <Menu as="div" className="relative inline-block text-left w-full">
      <Menu.Button
        className={clsx(
          'flex items-center w-full gap-3 px-2 py-2',
          'text-white/90 hover:bg-jlc-magenta/20 rounded-lg transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-jlc-magenta'
        )}
      >
        {/* Avatar with Status Indicator */}
        <div className="relative flex-shrink-0">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-jlc-accent-yellow to-yellow-500 flex items-center justify-center text-jlc-purple-900 font-bold">
            {userName?.charAt(0) || 'U'}
          </div>
          <div className="absolute -bottom-0.5 -right-0.5">
            <UserStatusIndicator status={currentStatus} size="md" showTooltip={false} />
          </div>
        </div>

        {/* User Info */}
        {!compact && (
          <div className="flex-1 min-w-0 text-left">
            <p className="text-sm font-medium text-white truncate">{userName}</p>
            {userEmail && (
              <p className="text-xs text-white/60 truncate">{userEmail}</p>
            )}
            <p className="text-xs text-white/80 mt-0.5">{currentOption?.label}</p>
          </div>
        )}

        {/* Dropdown Icon */}
        {!compact && <ChevronDownIcon className="w-4 h-4 text-white/60 flex-shrink-0" />}
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute bottom-full left-0 mb-2 w-72 origin-bottom-left rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
          <div className="p-2">
            <div className="px-3 py-2 mb-2 border-b border-gray-100">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Définir votre statut
              </p>
            </div>

            {STATUS_OPTIONS.map((option) => (
              <Menu.Item key={option.value}>
                {({ active }) => (
                  <button
                    onClick={() => handleStatusChange(option.value)}
                    disabled={isUpdating || currentStatus === option.value}
                    className={clsx(
                      'group flex items-start w-full px-3 py-2 text-sm rounded-lg transition-colors',
                      active && 'bg-gray-50',
                      currentStatus === option.value && 'bg-jlc-magenta/10',
                      isUpdating && 'opacity-50 cursor-not-allowed'
                    )}
                  >
                    <span className="text-xl mr-3 flex-shrink-0">{option.icon}</span>
                    <div className="flex-1 text-left">
                      <p
                        className={clsx(
                          'font-medium',
                          currentStatus === option.value
                            ? 'text-jlc-magenta'
                            : 'text-gray-900'
                        )}
                      >
                        {option.label}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">{option.description}</p>
                    </div>
                    {currentStatus === option.value && (
                      <div className="ml-2 flex-shrink-0">
                        <div className="w-2 h-2 bg-jlc-magenta rounded-full" />
                      </div>
                    )}
                  </button>
                )}
              </Menu.Item>
            ))}

            <div className="mt-2 pt-2 border-t border-gray-100">
              <div className="px-3 py-2">
                <p className="text-xs text-gray-400">
                  <span className="font-medium">💡 Astuce :</span> Le statut "Inactif" est
                  défini automatiquement après 15 minutes d'inactivité
                </p>
              </div>
            </div>
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  )
}
