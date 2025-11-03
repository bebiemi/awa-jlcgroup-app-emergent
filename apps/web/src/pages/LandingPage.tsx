import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAppSelector } from '@/store/hooks'
import { 
  BriefcaseIcon, 
  BuildingOfficeIcon, 
  UserGroupIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  PhoneIcon,
  EnvelopeIcon,
  MapPinIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import LoginModal from '@/components/LoginModal'

export default function LandingPage() {
  const [showLoginModal, setShowLoginModal] = useState(false)
  const { isAuthenticated, user } = useAppSelector((state) => state.auth)
  const navigate = useNavigate()

  // Get dashboard path based on user role
  const getDashboardPath = () => {
    if (!user) return '/profile'
    if (user.roles.includes('admin') || user.roles.includes('super_admin')) return '/admin'
    if (user.roles.includes('interim')) return '/interimaire'
    if (user.roles.includes('company')) return '/entreprise'
    if (user.roles.includes('agency')) return '/agence'
    return '/profile'
  }
  
  const stats = [
    { label: 'Offres actives', value: '150+' },
    { label: 'Entreprises partenaires', value: '50+' },
    { label: 'Intérimaires inscrits', value: '500+' },
    { label: 'Missions réussies', value: '1000+' },
  ]

  const features = [
    {
      icon: BriefcaseIcon,
      title: 'Trouvez votre mission',
      description: 'Accédez à des centaines d\'offres d\'intérim dans tous les secteurs au Gabon',
    },
    {
      icon: BuildingOfficeIcon,
      title: 'Recrutez facilement',
      description: 'Trouvez les meilleurs profils pour vos missions temporaires',
    },
    {
      icon: UserGroupIcon,
      title: 'Accompagnement personnalisé',
      description: 'Notre équipe vous accompagne à chaque étape de votre parcours',
    },
  ]

  const recentJobs = [
    {
      title: 'Comptable H/F',
      company: 'Entreprise ABC',
      location: 'Libreville',
      type: 'CDI',
      posted: 'Il y a 2 jours',
    },
    {
      title: 'Développeur Full Stack',
      company: 'Tech Solutions',
      location: 'Port-Gentil',
      type: 'CDD',
      posted: 'Il y a 3 jours',
    },
    {
      title: 'Assistant RH',
      company: 'JLC Services',
      location: 'Libreville',
      type: 'Intérim',
      posted: 'Il y a 5 jours',
    },
  ]

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-jlc-purple-700">
                JLC GROUP ⭐
              </span>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <span className="text-gray-700 text-sm">
                    Bonjour, <span className="font-semibold">{user?.full_name || user?.username}</span>
                  </span>
                  <button
                    onClick={() => navigate(getDashboardPath())}
                    className="bg-jlc-purple-600 text-white hover:bg-jlc-purple-700 px-4 py-2 rounded-md text-sm font-medium inline-flex items-center"
                  >
                    Accéder à mon espace
                    <ArrowRightOnRectangleIcon className="ml-2 h-4 w-4" />
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setShowLoginModal(true)}
                    className="text-gray-700 hover:text-jlc-purple-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Connexion
                  </button>
                  <Link
                    to="/register"
                    className="bg-jlc-purple-600 text-white hover:bg-jlc-purple-700 px-4 py-2 rounded-md text-sm font-medium"
                  >
                    S'inscrire
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Votre partenaire intérim au Gabon
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-purple-100">
              Connectez talents et opportunités pour construire l'avenir du travail
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <button
                  onClick={() => navigate(getDashboardPath())}
                  className="bg-white text-jlc-purple-700 hover:bg-gray-100 px-8 py-3 rounded-lg text-lg font-semibold inline-flex items-center justify-center"
                >
                  Accéder à mon espace
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </button>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="bg-white text-jlc-purple-700 hover:bg-gray-100 px-8 py-3 rounded-lg text-lg font-semibold inline-flex items-center justify-center"
                  >
                    Trouver une mission
                    <ArrowRightIcon className="ml-2 h-5 w-5" />
                  </Link>
                  <Link
                    to="/register"
                    className="bg-jlc-purple-800 hover:bg-jlc-purple-900 text-white px-8 py-3 rounded-lg text-lg font-semibold inline-flex items-center justify-center"
                  >
                    Recruter des talents
                    <ArrowRightIcon className="ml-2 h-5 w-5" />
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-jlc-purple-700">
                  {stat.value}
                </div>
                <div className="text-gray-600 mt-2">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Pourquoi choisir JLC GROUP ?
            </h2>
            <p className="text-xl text-gray-600">
              La plateforme de référence pour l'intérim au Gabon
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
              >
                <feature.icon className="h-12 w-12 text-jlc-purple-600 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Recent Jobs Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Offres récentes
            </h2>
            <p className="text-xl text-gray-600">
              Découvrez les dernières opportunités disponibles
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {recentJobs.map((job, index) => (
              <div
                key={index}
                className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {job.title}
                </h3>
                <p className="text-gray-600 mb-2">{job.company}</p>
                <div className="flex items-center text-gray-500 text-sm mb-2">
                  <MapPinIcon className="h-4 w-4 mr-1" />
                  {job.location}
                </div>
                <div className="flex items-center justify-between mt-4">
                  <span className="bg-jlc-purple-100 text-jlc-purple-700 px-3 py-1 rounded-full text-sm font-medium">
                    {job.type}
                  </span>
                  <span className="text-gray-500 text-sm">{job.posted}</span>
                </div>
                <Link
                  to="/register"
                  className="mt-4 block w-full text-center bg-jlc-purple-600 text-white py-2 rounded-md hover:bg-jlc-purple-700 transition-colors"
                >
                  Postuler
                </Link>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link
              to="/register"
              className="inline-flex items-center text-jlc-purple-600 hover:text-jlc-purple-700 font-semibold"
            >
              Voir toutes les offres
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                À propos de JLC GROUP
              </h2>
              <p className="text-gray-600 mb-4">
                Depuis notre création, JLC GROUP s'est imposé comme le leader de l'intérim au Gabon. 
                Nous mettons en relation les meilleures entreprises avec les talents les plus qualifiés.
              </p>
              <p className="text-gray-600 mb-6">
                Notre mission : faciliter l'accès à l'emploi et contribuer au développement économique 
                du Gabon en offrant des solutions de recrutement flexibles et efficaces.
              </p>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-jlc-purple-600 mr-2 flex-shrink-0" />
                  <span className="text-gray-700">Expertise reconnue dans tous les secteurs</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-jlc-purple-600 mr-2 flex-shrink-0" />
                  <span className="text-gray-700">Accompagnement personnalisé</span>
                </li>
                <li className="flex items-start">
                  <CheckCircleIcon className="h-6 w-6 text-jlc-purple-600 mr-2 flex-shrink-0" />
                  <span className="text-gray-700">Processus de recrutement simplifié</span>
                </li>
              </ul>
            </div>
            <div className="bg-gradient-to-br from-jlc-purple-100 to-jlc-purple-200 rounded-2xl p-8 h-96 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">🤝</div>
                <p className="text-xl text-jlc-purple-800 font-semibold">
                  Votre partenaire de confiance
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-jlc-purple-700 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Prêt à nous rejoindre ?
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Créez votre compte gratuitement et accédez à toutes nos opportunités
          </p>
          <Link
            to="/register"
            className="inline-block bg-white text-jlc-purple-700 hover:bg-gray-100 px-8 py-3 rounded-lg text-lg font-semibold"
          >
            S'inscrire maintenant
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white text-lg font-semibold mb-4">JLC GROUP</h3>
              <p className="text-sm">
                La plateforme de référence pour l'intérim au Gabon
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Navigation</h4>
              <ul className="space-y-2 text-sm">
                <li><Link to="/register" className="hover:text-white">Trouver un emploi</Link></li>
                <li><Link to="/register" className="hover:text-white">Recruter</Link></li>
                <li><Link to="/login" className="hover:text-white">Connexion</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center">
                  <PhoneIcon className="h-4 w-4 mr-2 flex-shrink-0" />
                  <a href="tel:+241117259474" className="hover:text-white">
                    +241 (0)11 72 59 74
                  </a>
                </li>
                <li className="flex items-center">
                  <EnvelopeIcon className="h-4 w-4 mr-2 flex-shrink-0" />
                  <a href="mailto:info@jlcgroup.org" className="hover:text-white">
                    info@jlcgroup.org
                  </a>
                </li>
                <li className="flex items-start">
                  <MapPinIcon className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />
                  <span>
                    Immeuble Alfred Marche centre-ville,<br />
                    3ème et 5ème étage, derrière la poste<br />
                    BP: 6278 LBV - Gabon
                  </span>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Suivez-nous</h4>
              <div className="flex space-x-4">
                <a href="#" className="hover:text-white">Facebook</a>
                <a href="#" className="hover:text-white">LinkedIn</a>
                <a href="#" className="hover:text-white">Twitter</a>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-sm text-center">
            <p>
              &copy; {new Date().getFullYear()}{' '}
              <a 
                href="https://jlcgroup.org" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-white transition-colors font-medium"
              >
                JLC GROUP
              </a>
              . Tous droits réservés.
            </p>
            <p className="mt-2 text-xs text-gray-400">
              Designé et conçu par{' '}
              <a 
                href="https://awana-group.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="hover:text-white transition-colors font-medium"
              >
                Awana Group
              </a>
            </p>
          </div>
        </div>
      </footer>

      {/* Login Modal */}
      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </div>
  )
}
