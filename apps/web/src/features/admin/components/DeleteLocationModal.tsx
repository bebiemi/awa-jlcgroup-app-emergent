import { useState } from 'react'
import { useDeleteLocationMutation, type LocationTree } from '../api/locationsApi'
import toast from 'react-hot-toast'
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface DeleteLocationModalProps {
  isOpen: boolean
  onClose: () => void
  location: LocationTree
}

export default function DeleteLocationModal({ isOpen, onClose, location }: DeleteLocationModalProps) {
  const [deleteLocation, { isLoading }] = useDeleteLocationMutation()
  const [confirmed, setConfirmed] = useState(false)

  const hasChildren = location.children && location.children.length > 0

  const handleDelete = async () => {
    if (!confirmed) {
      toast.error('Veuillez confirmer la suppression')
      return
    }

    try {
      await deleteLocation(location.id).unwrap()
      toast.success('Localisation supprimée avec succès')
      onClose()
      setConfirmed(false)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">Supprimer la localisation</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-4">
            Vous êtes sur le point de supprimer :
          </p>

          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <p className="font-semibold text-gray-900">{location.name}</p>
            <p className="text-sm text-gray-600">Type: {location.type}</p>
          </div>

          {hasChildren && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-red-800">
                <strong>Attention :</strong> Cette localisation a {location.children.length} enfant(s).
                Vous devez d'abord supprimer les enfants.
              </p>
            </div>
          )}

          {!hasChildren && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-orange-800">
                <strong>Attention :</strong> Cette action est irréversible.
              </p>
            </div>
          )}

          {!hasChildren && (
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
                className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
              />
              <span className="text-sm text-gray-700">
                Je confirme vouloir supprimer cette localisation
              </span>
            </label>
          )}
        </div>

        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Annuler
          </button>
          {!hasChildren && (
            <button
              onClick={handleDelete}
              disabled={!confirmed || isLoading}
              className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Suppression...' : 'Supprimer'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
