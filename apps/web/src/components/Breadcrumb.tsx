import { Link, useLocation } from 'react-router-dom'
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline'

interface BreadcrumbItem {
  label: string
  path: string
}

const routeLabels: Record<string, string> = {
  '': 'Accueil',
  'admin': 'Administration',
  'users': 'Utilisateurs',
  'new': 'Nouvel utilisateur',
  'groups': 'Groupes',
  'profiles': 'Profils & Permissions',
  'validations': 'Validations',
  'profile': 'Mon Profil',
  'interimaire': 'Tableau de Bord Intérimaire',
  'entreprise': 'Tableau de Bord Entreprise',
  'agence': 'Tableau de Bord Agence',
  'login': 'Connexion',
  'register': 'Inscription',
  'forgot-password': 'Mot de passe oublié',
  'reset-password': 'Réinitialisation',
  'auth': 'Authentification',
  'google': 'Google',
  'callback': 'Callback',
  'role-selection': 'Sélection du rôle',
}

export default function Breadcrumb() {
  const location = useLocation()
  
  // Don't show breadcrumb on landing page
  if (location.pathname === '/') {
    return null
  }

  const pathSegments = location.pathname.split('/').filter(Boolean)
  
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Accueil', path: '/' },
  ]

  let currentPath = ''
  pathSegments.forEach((segment) => {
    currentPath += `/${segment}`
    breadcrumbs.push({
      label: routeLabels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1),
      path: currentPath,
    })
  })

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600">
      {breadcrumbs.map((crumb, index) => {
        const isLast = index === breadcrumbs.length - 1
        const isHome = index === 0

        return (
          <div key={crumb.path} className="flex items-center">
            {index > 0 && (
              <ChevronRightIcon className="h-4 w-4 mx-2 text-gray-400" />
            )}
            {isLast ? (
              <span className="font-medium text-gray-900 flex items-center">
                {isHome && <HomeIcon className="h-4 w-4 mr-1" />}
                {crumb.label}
              </span>
            ) : (
              <Link
                to={crumb.path}
                className="hover:text-jlc-purple-600 transition-colors flex items-center"
              >
                {isHome && <HomeIcon className="h-4 w-4 mr-1" />}
                {!isHome && crumb.label}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}
