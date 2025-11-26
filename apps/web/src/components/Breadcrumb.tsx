/**
 * Composant Breadcrumb (Fil d'Ariane) Unifié
 * Utilise la configuration de navigation centralisée
 */

import { Link, useLocation } from 'react-router-dom'
import { useMemo } from 'react'
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline'
import { useBreadcrumb, useNavigationConfig } from '@/hooks/useNavigationConfig'

interface BreadcrumbProps {
  className?: string
  showHome?: boolean
}

export default function Breadcrumb({ className = '', showHome = true }: BreadcrumbProps) {
  const location = useLocation()
  const breadcrumbPath = useBreadcrumb(location.pathname)
  const { context, rawConfig } = useNavigationConfig()

  const contextRoot = useMemo(() => {
    return Object.values(rawConfig).find(
      (item) => item.contexts.includes(context) && !item.parentId && item.order === 1
    )
  }, [context, rawConfig])

  const homePath = contextRoot?.path || '/'
  const homeLabel = contextRoot?.label || 'Accueil'
  
  // Si pas de breadcrumb ou juste un élément, ne rien afficher
  if (breadcrumbPath.length === 0 || (breadcrumbPath.length === 1 && !showHome)) {
    return null
  }
  
  return (
    <nav className={`flex items-center space-x-2 text-sm ${className}`} aria-label="Breadcrumb">
      {showHome && (
        <>
          <Link
            to={homePath}
            className="text-gray-500 hover:text-gray-700 transition-colors"
            aria-label={homeLabel}
          >
            <HomeIcon className="h-4 w-4" />
          </Link>
          {breadcrumbPath.length > 0 && (
            <ChevronRightIcon className="h-4 w-4 text-gray-400" />
          )}
        </>
      )}
      
      {breadcrumbPath.map((item, index) => {
        const isLast = index === breadcrumbPath.length - 1
        
        return (
          <div key={item.id} className="flex items-center space-x-2">
            {isLast ? (
              <span className="text-gray-900 font-medium" aria-current="page">
                {item.label}
              </span>
            ) : (
              <>
                <Link
                  to={item.path.replace(/:[^/]+/g, '')} 
                  className="text-gray-500 hover:text-gray-700 transition-colors"
                >
                  {item.label}
                </Link>
                <ChevronRightIcon className="h-4 w-4 text-gray-400" />
              </>
            )}
          </div>
        )
      })}
    </nav>
  )
}
