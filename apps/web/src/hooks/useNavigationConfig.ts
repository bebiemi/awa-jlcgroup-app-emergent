/**
 * Hook pour accéder à la configuration de navigation
 * et obtenir des items filtrés par contexte et permissions IAM
 */

import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { usePermissions } from './usePermission'
import {
  navigationConfig,
  filterNavigationItems,
  buildNavigationTree,
  findNavigationItemByPath,
  buildBreadcrumbPath,
  type NavigationContext,
  type NavigationItem,
} from '@/config/navigation.config'

/**
 * Détecte le contexte utilisateur basé sur ses permissions
 */
export function useCurrentContext(): NavigationContext {
  const { permissions } = usePermissions([
    'admin.dashboard',
    'dashboard.commercial.access',
    'dashboard.company.access',
    'dashboard.candidat.access',
  ])
  
  if (permissions['admin.dashboard']) return 'admin'
  if (permissions['dashboard.commercial.access']) return 'commercial'
  if (permissions['dashboard.company.access']) return 'entreprise'
  if (permissions['dashboard.candidat.access']) return 'candidat'
  
  return 'public'
}

/**
 * Hook pour obtenir la configuration de navigation filtrée
 */
export function useNavigationConfig(context?: NavigationContext) {
  const detectedContext = useCurrentContext()
  const effectiveContext = context || detectedContext
  const { t } = useTranslation()
  
  // Récupérer toutes les permissions de l'utilisateur
  const allPermissionsToCheck = useMemo(() => {
    const perms = new Set<string>()
    Object.values(navigationConfig).forEach(item => {
      item.requiredPermissions?.forEach(p => perms.add(p))
      item.requiredAllPermissions?.forEach(p => perms.add(p))
    })
    return Array.from(perms)
  }, [])
  
  const { permissions } = usePermissions(allPermissionsToCheck)
  
  // Transformer les permissions en tableau
  const userPermissions = useMemo(() => {
    return Object.entries(permissions)
      .filter(([_, hasPermission]) => hasPermission)
      .map(([perm]) => perm)
  }, [permissions])
  
  // Filtrer et construire l'arbre de navigation
  const navigationItems = useMemo(() => {
    const filtered = filterNavigationItems(effectiveContext, userPermissions)
    return buildNavigationTree(filtered)
  }, [effectiveContext, userPermissions])
  
  // Traduire les labels (utilise label direct si disponible, sinon i18n)
  const translatedItems = useMemo(() => {
    return navigationItems.map(item => ({
      ...item,
      label: item.label || t(item.labelKey, { defaultValue: item.labelKey }),
    }))
  }, [navigationItems, t])
  
  return {
    context: effectiveContext,
    items: translatedItems,
    rawConfig: navigationConfig,
  }
}

/**
 * Hook pour obtenir les items de la sidebar
 */
export function useSidebarItems(context?: NavigationContext) {
  const { items } = useNavigationConfig(context)
  
  // Filtrer les items cachés
  const sidebarItems = useMemo(() => {
    return items.filter(item => !item.hidden)
  }, [items])
  
  return sidebarItems
}

/**
 * Hook pour générer le breadcrumb (fil d'Ariane)
 */
export function useBreadcrumb(currentPath: string) {
  const { t } = useTranslation()
  const { context } = useNavigationConfig()
  
  const breadcrumb = useMemo(() => {
    // Trouver l'item correspondant au path actuel
    const currentItem = findNavigationItemByPath(currentPath)
    if (!currentItem) return []
    
    // Construire le chemin complet
    const path = buildBreadcrumbPath(currentItem.id)
    
    // Traduire les labels
    return path.map(item => ({
      id: item.id,
      label: t(item.labelKey),
      path: item.path,
      icon: item.icon,
    }))
  }, [currentPath, context, t])
  
  return breadcrumb
}

/**
 * Hook pour vérifier si un path est actif
 */
export function useIsPathActive(path: string, exact = false) {
  const location = window.location.pathname
  
  if (exact) {
    return location === path
  }
  
  return location.startsWith(path)
}

/**
 * Hook pour obtenir un item de navigation par son ID
 */
export function useNavigationItem(itemId: string) {
  const { t } = useTranslation()
  const item = navigationConfig[itemId]
  
  if (!item) return null
  
  return {
    ...item,
    label: t(item.labelKey),
  }
}
