/**
 * Module Besoins - Exports
 * Architecture Config-Driven
 */

// Page principale
export { default as BesoinsPage } from './pages/BesoinsPage'

// Configuration
export { BesoinsPageConfig } from './config/besoins.config'

// API
export * from './api/besoinsApi'

// Composants
export { default as CommentThread } from './components/CommentThread'
export { default as StatusTimeline } from './components/StatusTimeline'
export { default as DynamicForm } from './components/DynamicForm'
