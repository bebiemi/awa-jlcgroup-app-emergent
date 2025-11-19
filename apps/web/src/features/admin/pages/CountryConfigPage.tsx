import { useState } from 'react'
import Layout from '@/components/Layout'
import {
  GlobeAltIcon,
  SparklesIcon,
  StarIcon,
  BuildingOffice2Icon,
} from '@heroicons/react/24/outline'
import { StarIcon as StarSolidIcon } from '@heroicons/react/24/solid'
import {
  useGetCountriesQuery,
  useInitDefaultCountriesMutation,
  useSetDefaultCountryMutation,
  Country,
} from '../api/countryConfigApi'
import { toast } from 'react-hot-toast'
import ManageCitiesModal from '../components/ManageCitiesModal'

export default function CountryConfigPage() {
  const [selectedCountry, setSelectedCountry] = useState<Country | null>(null)
  const [showCitiesModal, setShowCitiesModal] = useState(false)

  const { data: countries = [], isLoading, refetch } = useGetCountriesQuery({ active_only: false })
  const [initDefault, { isLoading: isInitializing }] = useInitDefaultCountriesMutation()
  const [setDefault, { isLoading: isSettingDefault }] = useSetDefaultCountryMutation()

  const handleInitDefault = async () => {
    if (!confirm('Initialiser les pays et devises par défaut ?')) return

    try {
      const result = await initDefault().unwrap()
      toast.success(result.message || 'Données initialisées avec succès')
      refetch()
    } catch (error: any) {
      if (error?.data?.detail?.includes('already initialized')) {
        toast('Les données sont déjà initialisées')
      } else {
        toast.error(error?.data?.detail || 'Erreur lors de l\'initialisation')
      }
    }
  }

  const handleSetDefault = async (country: Country) => {
    try {
      await setDefault(country.id).unwrap()
      toast.success(`${country.name} défini comme pays par défaut`)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const handleManageCities = (country: Country) => {
    setSelectedCountry(country)
    setShowCitiesModal(true)
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <GlobeAltIcon className="h-8 w-8 text-jlc-purple-600" />
              Configuration des pays et devises
            </h1>
            <p className="mt-2 text-gray-600">Gérez les pays supportés et leurs devises</p>
          </div>

          <button
            onClick={handleInitDefault}
            disabled={isInitializing}
            className="px-4 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <SparklesIcon className="h-5 w-5" />
            {isInitializing ? 'Initialisation...' : 'Initialiser données par défaut'}
          </button>
        </div>

        {/* Countries Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-64 bg-gray-200 rounded-2xl" />
              </div>
            ))}
          </div>
        ) : countries.length === 0 ? (
          <div className="text-center py-12">
            <GlobeAltIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">Aucun pays configuré</h3>
            <p className="mt-1 text-sm text-gray-500">
              Cliquez sur "Initialiser données par défaut" pour commencer
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {countries.map((country) => (
              <div
                key={country.id}
                className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 hover:border-jlc-purple-200"
              >
                {/* Country Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-jlc-purple-100 to-indigo-100 flex items-center justify-center">
                      <span className="text-2xl font-bold text-jlc-purple-600">
                        {country.iso_code}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{country.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            country.active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {country.active ? 'Actif' : 'Inactif'}
                        </span>
                        {country.is_default && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <StarSolidIcon className="h-3 w-3 mr-1" />
                            Par défaut
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Country Details */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Code pays</span>
                    <span className="font-medium text-gray-900">{country.iso_code}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Téléphone</span>
                    <span className="font-medium text-gray-900">{country.phone_prefix}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Devise</span>
                    <span className="font-medium text-gray-900">{country.currency_code}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Symbole</span>
                    <span className="font-medium text-gray-900 text-base">
                      {country.currency_symbol}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-4 border-t border-gray-100">
                  <button
                    onClick={() => handleSetDefault(country)}
                    disabled={country.is_default || isSettingDefault}
                    className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1 ${
                      country.is_default
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                    }`}
                  >
                    <StarIcon className="h-4 w-4" />
                    {country.is_default ? 'Par défaut' : 'Définir'}
                  </button>
                  <button
                    onClick={() => handleManageCities(country)}
                    className="flex-1 px-3 py-2 bg-jlc-purple-50 text-jlc-purple-700 hover:bg-jlc-purple-100 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1"
                  >
                    <BuildingOffice2Icon className="h-4 w-4" />
                    Gérer villes
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Cities Modal */}
        <ManageCitiesModal
          isOpen={showCitiesModal}
          onClose={() => {
            setShowCitiesModal(false)
            setSelectedCountry(null)
          }}
          country={selectedCountry}
        />
      </div>
    </Layout>
  )
}
