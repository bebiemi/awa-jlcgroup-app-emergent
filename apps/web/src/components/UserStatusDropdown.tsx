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
  compact?: boolean
}

export default function UserStatusDropdown({
  userName,
  compact = false,
}: UserStatusDropdownProps) {
  const { data: presence, isLoading } = useGetMyPresenceQuery()
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
          'flex items-center justify-between w-full px-3 py-2 text-sm',
          'text-gray-700 hover:bg-gray-50 rounded-lg transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:ring-offset-2'
        )}
      >
        <div className="flex items-center space-x-2 min-w-0 flex-1">
          <UserStatusIndicator status={currentStatus} size="md" showTooltip={false} />
          {!compact && (
            <div className="flex flex-col items-start min-w-0">
              {userName && (
                <span className="text-xs font-medium text-gray-900 truncate max-w-[150px]">
                  {userName}
                </span>
              )}
              <span className="text-xs text-gray-500">{currentOption?.label}</span>
            </div>
          )}
        </div>
        {!compact && <ChevronDownIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />}
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
                      currentStatus === option.value && 'bg-jlc-purple-50',
                      isUpdating && 'opacity-50 cursor-not-allowed'
                    )}
                  >
                    <span className="text-xl mr-3 flex-shrink-0">{option.icon}</span>
                    <div className="flex-1 text-left">
                      <p
                        className={clsx(
                          'font-medium',
                          currentStatus === option.value
                            ? 'text-jlc-purple-700'
                            : 'text-gray-900'
                        )}
                      >
                        {option.label}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">{option.description}</p>
                    </div>
                    {currentStatus === option.value && (
                      <div className="ml-2 flex-shrink-0">
                        <div className="w-2 h-2 bg-jlc-purple-600 rounded-full" />
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
