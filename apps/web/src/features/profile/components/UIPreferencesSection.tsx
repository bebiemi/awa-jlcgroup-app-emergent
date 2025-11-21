/**
 * Section des préférences UI utilisateur
 * Permet de choisir le style de sidebar et autres préférences d'interface
 */

import { useState } from 'react'
import { PaintBrushIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { useUIPreferences } from '@/hooks/useUIPreferences'

export default function UIPreferencesSection() {
  const { preferences, updatePreferences, isLoading, error } = useUIPreferences()
  const [isSaving, setIsSaving] = useState(false)

  const sidebarStyle = preferences.sidebar_style

  const handleStyleChange = async (newStyle: 'v2' | 'v3') => {
    setIsSaving(true)
    const success = await updatePreferences({ sidebar_style: newStyle })
    setIsSaving(false)
    
    if (success) {
      toast.success('Style de sidebar sauvegardé ! Rechargez la page pour voir les changements.')
    } else {
      toast.error('Erreur lors de la sauvegarde des préférences')
    }
  }

  const handleReload = () => {
    window.location.reload()
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <p className="text-gray-500">Chargement des préférences...</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <PaintBrushIcon className="h-6 w-6 text-jlc-purple-600" />
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Préférences d'Interface
          </h2>
          <p className="text-sm text-gray-600">
            Personnalisez l'apparence de votre interface
          </p>
        </div>
      </div>

      {/* Choix du style de sidebar */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Style de la barre latérale
          </label>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Option V2 - Classique */}
            <button
              onClick={() => handleStyleChange('v2')}
              className={`relative p-4 border-2 rounded-lg transition-all ${
                sidebarStyle === 'v2'
                  ? 'border-jlc-purple-600 bg-jlc-purple-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={sidebarStyle === 'v2'}
                  onChange={() => handleStyleChange('v2')}
                  className="mt-1"
                />
                <div className="flex-1 text-left">
                  <div className="font-medium text-gray-900 mb-1">
                    Classique
                  </div>
                  <div className="text-sm text-gray-600 mb-3">
                    Design clair avec fond blanc, parfait pour une utilisation professionnelle
                  </div>
                  {/* Aperçu miniature */}
                  <div className="bg-white border border-gray-300 rounded p-2 h-24 flex flex-col gap-1">
                    <div className="bg-gray-200 h-2 rounded w-3/4"></div>
                    <div className="bg-gray-100 h-2 rounded w-full"></div>
                    <div className="bg-gray-100 h-2 rounded w-2/3"></div>
                    <div className="bg-purple-600 h-2 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            </button>

            {/* Option V3 - Premium */}
            <button
              onClick={() => handleStyleChange('v3')}
              className={`relative p-4 border-2 rounded-lg transition-all ${
                sidebarStyle === 'v3'
                  ? 'border-jlc-purple-600 bg-jlc-purple-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  checked={sidebarStyle === 'v3'}
                  onChange={() => handleStyleChange('v3')}
                  className="mt-1"
                />
                <div className="flex-1 text-left">
                  <div className="font-medium text-gray-900 mb-1 flex items-center gap-2">
                    Premium
                    <span className="text-xs bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white px-2 py-0.5 rounded-full">
                      Nouveau
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-3">
                    Design moderne avec dégradé sombre et effets premium
                  </div>
                  {/* Aperçu miniature */}
                  <div className="bg-gradient-to-b from-purple-900 via-purple-800 to-slate-900 border border-purple-700 rounded p-2 h-24 flex flex-col gap-1">
                    <div className="bg-white/20 h-2 rounded w-3/4"></div>
                    <div className="bg-white/10 h-2 rounded w-full"></div>
                    <div className="bg-white/10 h-2 rounded w-2/3"></div>
                    <div className="bg-yellow-400 h-2 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Bouton pour recharger */}
        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handleReload}
            className="inline-flex items-center px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
          >
            <PaintBrushIcon className="h-5 w-5 mr-2" />
            Appliquer les changements
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Rechargez la page pour voir vos préférences appliquées
          </p>
        </div>
      </div>
    </div>
  )
}
