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
 * Retourne TOUS les items filtrés (pas seulement l'arbre)
 */
export function useSidebarItems(context?: NavigationContext) {
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
  
  // Filtrer TOUS les items (pas seulement construire l'arbre)
  const filteredItems = useMemo(() => {
    const filtered = filterNavigationItems(effectiveContext, userPermissions)
    // Traduire et retourner TOUS les items filtrés (pas l'arbre)
    return filtered.map(item => ({
      ...item,
      label: item.label || t(item.labelKey, { defaultValue: item.labelKey }),
    })).filter(item => !item.hidden)
  }, [effectiveContext, userPermissions, t])
  
  return filteredItems
}

/**
 * Hook pour générer le breadcrumb (fil d'Ariane) - Contextuel
 * Construit le breadcrumb en fonction du contexte utilisateur
 */
export function useBreadcrumb(currentPath: string) {
  const { t } = useTranslation()
  const currentContext = useCurrentContext()
  
  const breadcrumb = useMemo(() => {
    // Trouver TOUS les items qui correspondent au path actuel
    const allItems = Object.values(navigationConfig)
    const matchingItems = allItems.filter(item => {
      if (!item.path.includes(':')) {
        return item.path === currentPath
      }
      const pattern = item.path.replace(/:[^/]+/g, '[^/]+')
      const regex = new RegExp(`^${pattern}$`)
      return regex.test(currentPath)
    })
    
    // Filtrer pour ne garder que l'item du contexte actuel
    let currentItem = matchingItems.find(item => 
      item.contexts.includes(currentContext)
    )
    
    // Si pas trouvé, prendre le premier item correspondant
    if (!currentItem && matchingItems.length > 0) {
      currentItem = matchingItems[0]
    }
    
    if (!currentItem) return []
    
    // Construire le chemin en remontant par parentId
    // MAIS ne remonter que si le parent est aussi dans le contexte actuel
    const path: NavigationItem[] = []
    let current: NavigationItem | undefined = currentItem
    
    while (current) {
      path.unshift(current)
      
      if (!current.parentId) break
      
      const parent = navigationConfig[current.parentId]
      // Vérifier si le parent est dans le bon contexte
      if (parent && parent.contexts.includes(currentContext)) {
        current = parent
      } else {
        // Chercher un parent alternatif dans le contexte actuel
        const contextRoot = allItems.find(item => 
          item.contexts.includes(currentContext) && 
          !item.parentId &&
          item.order === 1 // Dashboard principal
        )
        if (contextRoot && path[0].id !== contextRoot.id) {
          path.unshift(contextRoot)
        }
        break
      }
    }
    
    // Traduire les labels (utilise label direct si disponible, sinon i18n)
    return path.map(item => ({
      id: item.id,
      label: item.label || t(item.labelKey, { defaultValue: item.labelKey }),
      path: item.path,
      icon: item.icon,
    }))
  }, [currentPath, currentContext, t])
  
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
