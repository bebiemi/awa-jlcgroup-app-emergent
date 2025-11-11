/**
 * Company Settings Page
 * Allows companies to view and edit their company information
 */
import React, { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {
  BuildingOfficeIcon,
  MapPinIcon,
  EnvelopeIcon,
  PhoneIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import {
  useGetMyEntrepriseQuery,
  useUpdateMyEntrepriseMutation,
  type EntrepriseUpdate,
} from '@/features/company/api/entrepriseApi'

export default function CompanySettingsPage() {
  const { data: entreprise, isLoading, error } = useGetMyEntrepriseQuery()
  const [updateEntreprise, { isLoading: isUpdating }] = useUpdateMyEntrepriseMutation()

  // Form state
  const [formData, setFormData] = useState<EntrepriseUpdate>({
    nom: '',
    raison_sociale: '',
    siret: '',
    adresse: '',
    code_postal: '',
    ville: '',
    pays: 'France',
    email: '',
    telephone: '',
    description: '',
    secteur_activite: '',
    effectif: '',
    site_web: '',
  })

  const [isEditing, setIsEditing] = useState(false)
  const [saveMessage, setSaveMessage] = useState<{
    type: 'success' | 'error'
    message: string
  } | null>(null)

  // Populate form when data loads
  useEffect(() => {
    if (entreprise) {
      setFormData({
        nom: entreprise.nom || '',
        raison_sociale: entreprise.raison_sociale || '',
        siret: entreprise.siret || '',
        adresse: entreprise.adresse || '',
        code_postal: entreprise.code_postal || '',
        ville: entreprise.ville || '',
        pays: entreprise.pays || 'France',
        email: entreprise.email || '',
        telephone: entreprise.telephone || '',
        description: entreprise.description || '',
        secteur_activite: entreprise.secteur_activite || '',
        effectif: entreprise.effectif || '',
        site_web: entreprise.site_web || '',
      })
    }
  }, [entreprise])

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaveMessage(null)

    try {
      await updateEntreprise(formData).unwrap()
      setSaveMessage({
        type: 'success',
        message: 'Les informations de votre entreprise ont été mises à jour avec succès.',
      })
      setIsEditing(false)
      // Clear message after 5 seconds
      setTimeout(() => setSaveMessage(null), 5000)
    } catch (err: any) {
      setSaveMessage({
        type: 'error',
        message: err?.data?.detail || 'Une erreur est survenue lors de la mise à jour.',
      })
    }
  }

  const handleCancel = () => {
    // Reset form to original data
    if (entreprise) {
      setFormData({
        nom: entreprise.nom || '',
        raison_sociale: entreprise.raison_sociale || '',
        siret: entreprise.siret || '',
        adresse: entreprise.adresse || '',
        code_postal: entreprise.code_postal || '',
        ville: entreprise.ville || '',
        pays: entreprise.pays || 'France',
        email: entreprise.email || '',
        telephone: entreprise.telephone || '',
        description: entreprise.description || '',
        secteur_activite: entreprise.secteur_activite || '',
        effectif: entreprise.effectif || '',
        site_web: entreprise.site_web || '',
      })
    }
    setIsEditing(false)
    setSaveMessage(null)
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout>
        <Card className="bg-red-50 border-red-200">
          <div className="flex items-center gap-3 text-red-700">
            <ExclamationTriangleIcon className="h-6 w-6" />
            <div>
              <h3 className="font-semibold">Erreur de chargement</h3>
              <p className="text-sm">
                {'data' in error && error.data && typeof error.data === 'object' && 'detail' in error.data
                  ? String(error.data.detail)
                  : 'Impossible de charger les informations de votre entreprise.'}
              </p>
            </div>
          </div>
        </Card>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Paramètres de l'Entreprise
            </h1>
            <p className="mt-2 text-gray-600">
              Gérez les informations de votre entreprise
            </p>
          </div>
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)} variant="primary">
              Modifier
            </Button>
          )}
        </div>

        {/* Success/Error Message */}
        {saveMessage && (
          <Card
            className={
              saveMessage.type === 'success'
                ? 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }
          >
            <div
              className={`flex items-center gap-3 ${
                saveMessage.type === 'success' ? 'text-green-700' : 'text-red-700'
              }`}
            >
              {saveMessage.type === 'success' ? (
                <CheckCircleIcon className="h-6 w-6" />
              ) : (
                <ExclamationTriangleIcon className="h-6 w-6" />
              )}
              <p>{saveMessage.message}</p>
            </div>
          </Card>
        )}

        {/* Company Information Form */}
        <form onSubmit={handleSubmit}>
          <Card>
            <div className="space-y-6">
              {/* Company Identity */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BuildingOfficeIcon className="h-6 w-6 text-jlc-purple-600" />
                  Identité de l'Entreprise
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom Commercial *
                    </label>
                    <input
                      type="text"
                      name="nom"
                      value={formData.nom}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      required
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Raison Sociale *
                    </label>
                    <input
                      type="text"
                      name="raison_sociale"
                      value={formData.raison_sociale}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      required
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      SIRET *
                    </label>
                    <input
                      type="text"
                      name="siret"
                      value={formData.siret}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      required
                      pattern="\d{14}"
                      maxLength={14}
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                      placeholder="14 chiffres"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Secteur d'Activité
                    </label>
                    <input
                      type="text"
                      name="secteur_activite"
                      value={formData.secteur_activite}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                      placeholder="Ex: Technologie, Commerce, Services"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Effectif
                    </label>
                    <select
                      name="effectif"
                      value={formData.effectif}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                    >
                      <option value="">Sélectionner</option>
                      <option value="TPE">TPE (1-9 employés)</option>
                      <option value="PME">PME (10-249 employés)</option>
                      <option value="ETI">ETI (250-4999 employés)</option>
                      <option value="GE">Grande Entreprise (5000+ employés)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Location */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <MapPinIcon className="h-6 w-6 text-jlc-purple-600" />
                  Adresse
                </h2>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Adresse *
                    </label>
                    <input
                      type="text"
                      name="adresse"
                      value={formData.adresse}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      required
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Code Postal
                      </label>
                      <input
                        type="text"
                        name="code_postal"
                        value={formData.code_postal}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                          !isEditing ? 'bg-gray-50' : ''
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ville
                      </label>
                      <input
                        type="text"
                        name="ville"
                        value={formData.ville}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                          !isEditing ? 'bg-gray-50' : ''
                        }`}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Pays
                      </label>
                      <input
                        type="text"
                        name="pays"
                        value={formData.pays}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                          !isEditing ? 'bg-gray-50' : ''
                        }`}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Contact */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <EnvelopeIcon className="h-6 w-6 text-jlc-purple-600" />
                  Contact
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <EnvelopeIcon className="h-4 w-4 inline mr-1" />
                      Email *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      required
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <PhoneIcon className="h-4 w-4 inline mr-1" />
                      Téléphone *
                    </label>
                    <input
                      type="tel"
                      name="telephone"
                      value={formData.telephone}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      required
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <GlobeAltIcon className="h-4 w-4 inline mr-1" />
                      Site Web
                    </label>
                    <input
                      type="url"
                      name="site_web"
                      value={formData.site_web}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                        !isEditing ? 'bg-gray-50' : ''
                      }`}
                      placeholder="https://www.example.com"
                    />
                  </div>
                </div>
              </div>

              {/* Description */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Description
                </h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Présentation de l'entreprise
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    rows={4}
                    className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                      !isEditing ? 'bg-gray-50' : ''
                    }`}
                    placeholder="Décrivez votre entreprise, vos activités principales..."
                  />
                </div>
              </div>

              {/* Action Buttons */}
              {isEditing && (
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button
                    type="button"
                    onClick={handleCancel}
                    variant="secondary"
                  >
                    Annuler
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={isUpdating}
                  >
                    Enregistrer
                  </Button>
                </div>
              )}
            </div>
          </Card>
        </form>

        {/* Status Info */}
        {entreprise && (
          <Card className="bg-gray-50">
            <div className="text-sm text-gray-600 space-y-2">
              <div className="flex justify-between">
                <span>Statut :</span>
                <span
                  className={`font-medium ${
                    entreprise.status === 'active'
                      ? 'text-green-600'
                      : 'text-gray-600'
                  }`}
                >
                  {entreprise.status === 'active' ? 'Actif' : entreprise.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Créé le :</span>
                <span>{new Date(entreprise.created_at).toLocaleDateString('fr-FR')}</span>
              </div>
              {entreprise.updated_at && (
                <div className="flex justify-between">
                  <span>Dernière modification :</span>
                  <span>
                    {new Date(entreprise.updated_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </Layout>
  )
}
