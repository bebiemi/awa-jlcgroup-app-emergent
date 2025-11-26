import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { XMarkIcon, MagnifyingGlassIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline'
import { BuildingOffice2Icon } from '@heroicons/react/24/solid'
import { useGetCitiesQuery, useCreateCityMutation, useDeleteCityMutation, City } from '../api/countryConfigApi'
import { toast } from 'react-hot-toast'
import { usePermissions } from '@/hooks/usePermission'

interface ManageCitiesModalProps {
  isOpen: boolean
  onClose: () => void
  country: {
    id: string
    name: string
    iso_code: string
  } | null
}

export default function ManageCitiesModal({ isOpen, onClose, country }: ManageCitiesModalProps) {
  const [search, setSearch] = useState('')
  const [newCityName, setNewCityName] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const { permissions } = usePermissions(['locations.manage'])

  const { data: cities = [], isLoading, refetch } = useGetCitiesQuery(
    { countryId: country?.id || '', search, active_only: false },
    { skip: !country }
  )

  const [createCity, { isLoading: isCreating }] = useCreateCityMutation()
  const [deleteCity] = useDeleteCityMutation()

  const handleAddCity = async () => {
    if (!country || !newCityName.trim()) return

    try {
      await createCity({
        countryId: country.id,
        data: { name: newCityName.trim(), active: true },
      }).unwrap()

      toast.success(`Ville "${newCityName}" ajoutée avec succès`)
      setNewCityName('')
      setShowAddForm(false)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'ajout de la ville')
    }
  }

  const handleDeleteCity = async (city: City) => {
    if (!confirm(`Supprimer la ville "${city.name}" ?`)) return

    try {
      await deleteCity(city.id).unwrap()
      toast.success(`Ville "${city.name}" supprimée`)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  if (!(permissions['locations.manage'])) {
    return null
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <BuildingOffice2Icon className="h-8 w-8 text-jlc-purple-600" />
                    <div>
                      <Dialog.Title className="text-xl font-bold text-gray-900">
                        Gestion des villes
                      </Dialog.Title>
                      <p className="text-sm text-gray-600">
                        {country?.name} ({country?.iso_code})
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-500 transition-colors"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                {/* Search & Add */}
                <div className="flex gap-3 mb-4">
                  <div className="flex-1 relative">
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="Rechercher une ville..."
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                    />
                  </div>
                  <button
                    onClick={() => setShowAddForm(!showAddForm)}
                    className="px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors flex items-center gap-2"
                  >
                    <PlusIcon className="h-5 w-5" />
                    Ajouter
                  </button>
                </div>

                {/* Add Form */}
                {showAddForm && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom de la ville
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newCityName}
                        onChange={(e) => setNewCityName(e.target.value)}
                        placeholder="Ex: Libreville"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                        onKeyDown={(e) => e.key === 'Enter' && handleAddCity()}
                      />
                      <button
                        onClick={handleAddCity}
                        disabled={!newCityName.trim() || isCreating}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {isCreating ? 'Ajout...' : 'Confirmer'}
                      </button>
                      <button
                        onClick={() => {
                          setShowAddForm(false)
                          setNewCityName('')
                        }}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Annuler
                      </button>
                    </div>
                  </div>
                )}

                {/* Cities List */}
                <div className="max-h-96 overflow-y-auto">
                  {isLoading ? (
                    <div className="text-center py-8 text-gray-500">Chargement...</div>
                  ) : cities.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      {search ? 'Aucune ville trouvée' : 'Aucune ville configurée'}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {cities.map((city) => (
                        <div
                          key={city.id}
                          className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                        >
                          <span className="font-medium text-gray-900">{city.name}</span>
                          <button
                            onClick={() => handleDeleteCity(city)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Supprimer"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Footer */}
                <div className="mt-6 flex justify-between items-center">
                  <p className="text-sm text-gray-600">
                    {cities.length} ville(s) configurée(s)
                  </p>
                  <button
                    onClick={onClose}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Fermer
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
