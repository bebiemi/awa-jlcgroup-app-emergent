/**
 * Module Entreprises - Exports
 * Architecture Config-Driven
 */

// Page principale
export { default as EntreprisesPage } from './pages/EntreprisesPage'

// Configuration
export { EntreprisesPageConfig } from './config/entreprises.config'

// API
export * from './api/entreprisesApi'

// Composants (si besoin d'être réutilisés ailleurs)
export { default as CreateEntrepriseModal } from './components/CreateEntrepriseModal'
