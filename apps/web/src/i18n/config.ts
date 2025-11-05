import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import HttpBackend from 'i18next-http-backend'

i18n
  // Charger les traductions depuis /public/locales
  .use(HttpBackend)
  // Détection automatique de la langue
  .use(LanguageDetector)
  // Intégration avec React
  .use(initReactI18next)
  // Configuration
  .init({
    // Langue par défaut
    fallbackLng: 'fr',
    // Langues supportées
    supportedLngs: ['fr', 'en'],
    // Namespace par défaut
    defaultNS: 'translation',
    // Debug en développement
    debug: import.meta.env.DEV,
    
    // Options de détection
    detection: {
      // Ordre de détection
      order: ['localStorage', 'navigator', 'htmlTag'],
      // Clé dans localStorage
      lookupLocalStorage: 'i18nextLng',
      // Cache la langue détectée
      caches: ['localStorage'],
    },
    
    // Backend (chargement des fichiers)
    backend: {
      // Path vers les fichiers de traduction
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    
    // Options d'interpolation
    interpolation: {
      // React échappe déjà les valeurs
      escapeValue: false,
    },
    
    // Options React
    react: {
      // Utiliser Suspense pour le chargement
      useSuspense: true,
    },
  })

export default i18n
