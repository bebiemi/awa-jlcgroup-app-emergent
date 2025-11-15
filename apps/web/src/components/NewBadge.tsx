/**
 * New Badge Component
 * Shows "NEW" badge on recent profiles based on config
 */
import React from 'react'
import { SparklesIcon } from '@heroicons/react/24/solid'
import { useBadgeConfig } from '@/features/config/api/appConfigApi'

interface NewBadgeProps {
  createdAt: string
  firstProfileViewAt?: string | null
  className?: string
}

export default function NewBadge({ createdAt, firstProfileViewAt, className = '' }: NewBadgeProps) {
  const { data: badgeConfig, isLoading } = useBadgeConfig()

  if (isLoading || !badgeConfig?.enabled) {
    return null
  }

  const { expiration_days, expiration_mode, badge_text } = badgeConfig

  // Calculate if badge should be shown
  const createdDate = new Date(createdAt)
  const now = new Date()
  const daysSinceCreation = Math.floor((now.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24))

  let shouldShowBadge = false

  if (expiration_mode === 'creation_date') {
    // Show badge for X days after creation
    shouldShowBadge = daysSinceCreation <= expiration_days
  } else if (expiration_mode === 'first_view') {
    // Show badge until first view or X days
    if (!firstProfileViewAt) {
      shouldShowBadge = daysSinceCreation <= expiration_days
    }
  } else if (expiration_mode === 'both') {
    // Show badge for X days after creation AND not yet viewed
    shouldShowBadge = daysSinceCreation <= expiration_days && !firstProfileViewAt
  }

  if (!shouldShowBadge) {
    return null
  }

  // Use French by default (can be extended with i18n later)
  const text = badge_text.fr || 'NOUVEAU'

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-bold text-white bg-gradient-to-r from-jlc-purple-500 to-jlc-purple-600 rounded-full shadow-sm animate-pulse ${className}`}
    >
      <SparklesIcon className="h-3 w-3" />
      {text}
    </span>
  )
}
