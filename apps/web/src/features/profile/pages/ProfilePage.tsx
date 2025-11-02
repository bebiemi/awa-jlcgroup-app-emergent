import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {
  useGetMyProfileQuery,
  useUpdateMyProfileMutation,
  useUploadAvatarMutation,
} from '../api/profileApi'
import { useState, useRef } from 'react'
import toast from 'react-hot-toast'
import { UserCircleIcon, CameraIcon } from '@heroicons/react/24/outline'

export default function ProfilePage() {
  const { data: profile, isLoading } = useGetMyProfileQuery()
  const [updateProfile, { isLoading: isUpdating }] = useUpdateMyProfileMutation()
  const [uploadAvatar, { isLoading: isUploading }] = useUploadAvatarMutation()

  const [formData, setFormData] = useState<any>({})
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Initialize form data when profile loads
  useState(() => {
    if (profile) {
      setFormData({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        phone: profile.phone || '',
        // Interim fields
        skills: profile.skills || [],
        experience_years: profile.experience_years || '',
        availability: profile.availability || '',
        date_of_birth: profile.date_of_birth || '',
        place_of_birth: profile.place_of_birth || '',
        nationality: profile.nationality || 'Gabonaise',
        address: profile.address || '',
        city: profile.city || '',
        postal_code: profile.postal_code || '',
        // Company fields (Gabon specific)
        legal_representative: profile.legal_representative || '',
        company_name: profile.company_name || '',
        nif: profile.nif || '',
        circuit_file_number: profile.circuit_file_number || '',
        country: profile.country || 'Gabon',
        contact_email: profile.contact_email || profile.email || '',
        industry: profile.industry || '',
        company_size: profile.company_size || '',
        website: profile.website || '',
        description: profile.description || '',
      })
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await updateProfile(formData).unwrap()
      toast.success('Profil mis à jour avec succès!')
    } catch (error: any) {
      console.error('Update error:', error)
      toast.error(error?.data?.detail || 'Échec de la mise à jour')
    }
  }

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Veuillez sélectionner une image')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('L’image ne doit pas dépasser 5 Mo')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)
      await uploadAvatar(formData).unwrap()
      toast.success('Photo de profil mise à jour!')
    } catch (error: any) {
      console.error('Upload error:', error)
      toast.error(error?.data?.detail || 'Échec de l’upload')
    }
  }

  const handleSkillAdd = (skill: string) => {
    if (skill && !formData.skills?.includes(skill)) {
      setFormData({
        ...formData,
        skills: [...(formData.skills || []), skill],
      })
    }
  }

  const handleSkillRemove = (skill: string) => {
    setFormData({
      ...formData,
      skills: formData.skills?.filter((s: string) => s !== skill) || [],
    })
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
          <p className="mt-2 text-gray-600">
            Mettez à jour vos informations personnelles et professionnelles
          </p>
        </div>

        {/* Avatar Section */}
        <Card title="Photo de profil">
          <div className="flex items-center space-x-6">
            <div className="relative">
              {profile?.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt="Avatar"
                  className="h-24 w-24 rounded-full object-cover ring-4 ring-jlc-purple-100"
                />
              ) : (
                <UserCircleIcon className="h-24 w-24 text-gray-400" />
              )}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-0 right-0 bg-jlc-purple-600 text-white p-2 rounded-full shadow-lg hover:bg-jlc-purple-700 transition-colors"
                disabled={isUploading}
              >
                <CameraIcon className="h-4 w-4" />
              </button>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-900">
                {profile?.first_name} {profile?.last_name}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                JPG, PNG ou GIF. Max 5 Mo.
              </p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                isLoading={isUploading}
                className="mt-2"
              >
                Changer la photo
              </Button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarUpload}
              className="hidden"
            />
          </div>
        </Card>

        {/* Profile Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <Card title="Informations personnelles">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prénom *
                </label>
                <input
                  type="text"
                  value={formData.first_name || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, first_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom *
                </label>
                <input
                  type="text"
                  value={formData.last_name || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, last_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone
                </label>
                <input
                  type="tel"
                  value={formData.phone || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  placeholder="+33 6 12 34 56 78"
                />
              </div>
            </div>
          </Card>

          {/* Interim-specific fields */}
          {profile?.profile_type === 'interim' && (
            <Card title="Informations professionnelles (Intérimaire)">
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date de naissance
                    </label>
                    <input
                      type="date"
                      value={formData.date_of_birth || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, date_of_birth: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Lieu de naissance
                    </label>
                    <input
                      type="text"
                      value={formData.place_of_birth || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, place_of_birth: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nationalité
                    </label>
                    <input
                      type="text"
                      value={formData.nationality || 'Gabonaise'}
                      onChange={(e) =>
                        setFormData({ ...formData, nationality: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ville
                    </label>
                    <input
                      type="text"
                      value={formData.city || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, city: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adresse complète
                  </label>
                  <input
                    type="text"
                    value={formData.address || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, address: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Compétences
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {formData.skills?.map((skill: string, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-jlc-purple-100 text-jlc-purple-800 rounded-full text-sm flex items-center"
                      >
                        {skill}
                        <button
                          type="button"
                          onClick={() => handleSkillRemove(skill)}
                          className="ml-2 text-jlc-purple-600 hover:text-jlc-purple-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Ajouter une compétence (appuyez sur Entrée)"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleSkillAdd(e.currentTarget.value)
                        e.currentTarget.value = ''
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Années d'expérience
                    </label>
                    <input
                      type="number"
                      value={formData.experience_years || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          experience_years: parseInt(e.target.value) || 0,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      min="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Disponibilité
                    </label>
                    <select
                      value={formData.availability || 'available'}
                      onChange={(e) =>
                        setFormData({ ...formData, availability: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    >
                      <option value="available">Disponible immédiatement</option>
                      <option value="2weeks">Disponible sous 2 semaines</option>
                      <option value="1month">Disponible sous 1 mois</option>
                      <option value="unavailable">Non disponible</option>
                    </select>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Company-specific fields */}
          {profile?.profile_type === 'company' && (
            <Card title="Informations entreprise">
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom de la société *
                    </label>
                    <input
                      type="text"
                      value={formData.company_name || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, company_name: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Représentant légal *
                    </label>
                    <input
                      type="text"
                      value={formData.legal_representative || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          legal_representative: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      NIF (Numéro d'Identification Fiscale) *
                    </label>
                    <input
                      type="text"
                      value={formData.nif || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          nif: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Numéro de la fiche circuit
                    </label>
                    <input
                      type="text"
                      value={formData.circuit_file_number || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          circuit_file_number: e.target.value,
                        })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adresse *
                  </label>
                  <input
                    type="text"
                    value={formData.address || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, address: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pays *
                    </label>
                    <input
                      type="text"
                      value={formData.country || 'Gabon'}
                      onChange={(e) =>
                        setFormData({ ...formData, country: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Numéro de téléphone *
                    </label>
                    <input
                      type="tel"
                      value={formData.phone || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, phone: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      placeholder="+241 01 23 45 67"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email de contact *
                  </label>
                  <input
                    type="email"
                    value={formData.contact_email || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, contact_email: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Secteur d'activité
                    </label>
                    <input
                      type="text"
                      value={formData.industry || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, industry: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Taille de l'entreprise
                    </label>
                    <select
                      value={formData.company_size || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, company_size: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    >
                      <option value="">Sélectionnez</option>
                      <option value="1-10 employés">1-10 employés</option>
                      <option value="10-50 employés">10-50 employés</option>
                      <option value="50-200 employés">50-200 employés</option>
                      <option value="200+ employés">200+ employés</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Site web
                  </label>
                  <input
                    type="url"
                    value={formData.website || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, website: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    placeholder="https://"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                    placeholder="Décrivez votre entreprise..."
                  />
                </div>
              </div>
            </Card>
          )}

          {/* Save Button */}
          <div className="flex justify-end">
            <Button type="submit" variant="primary" size="lg" isLoading={isUpdating}>
              Enregistrer les modifications
            </Button>
          </div>
        </form>
      </div>
    </Layout>
  )
}
