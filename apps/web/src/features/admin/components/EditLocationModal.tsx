import { useState, useEffect } from 'react'
import { useUpdateLocationMutation, type LocationTree } from '../api/locationsApi'
import toast from 'react-hot-toast'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { usePermissions } from '@/hooks/usePermission'

interface EditLocationModalProps {
  isOpen: boolean
  onClose: () => void
  location: LocationTree
}

export default function EditLocationModal({ isOpen, onClose, location }: EditLocationModalProps) {
  const [updateLocation, { isLoading }] = useUpdateLocationMutation()
  const { permissions } = usePermissions(['locations.manage'])
  const [formData, setFormData] = useState({
    name: location.name,
    postal_code: location.postal_code || '',
    gps_latitude: location.gps_latitude?.toString() || '',
    gps_longitude: location.gps_longitude?.toString() || '',
    custom_field_1: location.custom_field_1 || '',
    custom_field_2: location.custom_field_2 || '',
    custom_field_3: location.custom_field_3 || '',
    custom_field_1_label: location.custom_field_1_label || 'Code administratif',
    custom_field_2_label: location.custom_field_2_label || 'Zone économique',
    custom_field_3_label: location.custom_field_3_label || 'Particularité',
  })

  useEffect(() => {
    if (location) {
      setFormData({
        name: location.name,
        postal_code: location.postal_code || '',
        gps_latitude: location.gps_latitude?.toString() || '',
        gps_longitude: location.gps_longitude?.toString() || '',
        custom_field_1: location.custom_field_1 || '',
        custom_field_2: location.custom_field_2 || '',
        custom_field_3: location.custom_field_3 || '',
        custom_field_1_label: location.custom_field_1_label || 'Code administratif',
        custom_field_2_label: location.custom_field_2_label || 'Zone économique',
        custom_field_3_label: location.custom_field_3_label || 'Particularité',
      })
    }
  }, [location])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const payload: any = {
        name: formData.name.trim(),
      }

      if (formData.postal_code) payload.postal_code = formData.postal_code
      if (formData.gps_latitude) payload.gps_latitude = parseFloat(formData.gps_latitude)
      if (formData.gps_longitude) payload.gps_longitude = parseFloat(formData.gps_longitude)
      if (formData.custom_field_1) {
        payload.custom_field_1 = formData.custom_field_1
        payload.custom_field_1_label = formData.custom_field_1_label
      }
      if (formData.custom_field_2) {
        payload.custom_field_2 = formData.custom_field_2
        payload.custom_field_2_label = formData.custom_field_2_label
      }
      if (formData.custom_field_3) {
        payload.custom_field_3 = formData.custom_field_3
        payload.custom_field_3_label = formData.custom_field_3_label
      }

      await updateLocation({ id: location.id, data: payload }).unwrap()
      toast.success('Localisation modifiée avec succès')
      onClose()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la modification')
    }
  }

  if (!isOpen) return null

  if (!permissions['locations.manage']) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full my-8">
        <div className="flex justify-between items-center p-6 border-b">
          <h3 className="text-xl font-bold text-gray-900">Modifier "{location.name}"</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Code Postal</label>
              <input
                type="text"
                value={formData.postal_code}
                onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>

            <div />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">GPS Latitude</label>
              <input
                type="number"
                step="0.000001"
                value={formData.gps_latitude}
                onChange={(e) => setFormData({ ...formData, gps_latitude: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">GPS Longitude</label>
              <input
                type="number"
                step="0.000001"
                value={formData.gps_longitude}
                onChange={(e) => setFormData({ ...formData, gps_longitude: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
              />
            </div>

            <div className="col-span-2">
              <h4 className="font-medium text-gray-700 mb-2">Champs Personnalisés</h4>
            </div>

            {[1, 2, 3].map((num) => (
              <div key={num} className="col-span-2 grid grid-cols-3 gap-2">
                <input
                  type="text"
                  value={formData[`custom_field_${num}_label` as keyof typeof formData]}
                  onChange={(e) =>
                    setFormData({ ...formData, [`custom_field_${num}_label`]: e.target.value })
                  }
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 text-sm"
                  placeholder="Label"
                />
                <input
                  type="text"
                  value={formData[`custom_field_${num}` as keyof typeof formData]}
                  onChange={(e) => setFormData({ ...formData, [`custom_field_${num}`]: e.target.value })}
                  className="col-span-2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  placeholder="Valeur"
                />
              </div>
            ))}
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition disabled:opacity-50"
            >
              {isLoading ? 'Modification...' : 'Modifier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
