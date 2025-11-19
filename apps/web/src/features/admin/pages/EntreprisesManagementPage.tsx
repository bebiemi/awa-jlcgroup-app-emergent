/**
 * Entreprises Management Page
 * Admin page to view and manage all companies
 */
import React, { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {
  BuildingOfficeIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  MapPinIcon,
  EnvelopeIcon,
  PhoneIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline'
import { useListEntreprisesQuery, useUpdateEntrepriseMutation } from '@/features/company/api/entrepriseApi'
import type { Entreprise, EntrepriseUpdate } from '@/features/company/api/entrepriseApi'
import CreateEntrepriseModal from '../components/CreateEntrepriseModal'

export default function EntreprisesManagementPage() {
  const { data, isLoading, error, refetch } = useListEntreprisesQuery({ limit: 1000 })
  const [updateEntreprise] = useUpdateEntrepriseMutation()
  
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<EntrepriseUpdate>({})
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  const entreprises = data || []

  // Filter entreprises
  const filteredEntreprises = entreprises.filter((e: Entreprise) =>
    e.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.siret?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.email?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
    setEditingId(null) // Close edit mode when collapsing
  }

  const handleEdit = (entreprise: Entreprise) => {
    setEditingId(entreprise.id)
    setEditForm({
      nom: entreprise.nom,
      raison_sociale: entreprise.raison_sociale,
      siret: entreprise.siret,
      adresse: entreprise.adresse,
      code_postal: entreprise.code_postal,
      ville: entreprise.ville,
      pays: entreprise.pays,
      email: entreprise.email,
      telephone: entreprise.telephone,
      description: entreprise.description,
      secteur_activite: entreprise.secteur_activite,
      effectif: entreprise.effectif,
      site_web: entreprise.site_web,
    })
  }

  const handleSave = async (id: string) => {
    try {
      await updateEntreprise({ id, data: editForm }).unwrap()
      setEditingId(null)
    } catch (err) {
      console.error('Failed to update entreprise:', err)
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditForm({})
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setEditForm((prev) => ({ ...prev, [name]: value }))
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

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <BuildingOfficeIcon className="h-8 w-8 text-jlc-purple-600" />
              Gestion des Entreprises
            </h1>
            <p className="mt-2 text-gray-600">
              Gérez toutes les entreprises inscrites sur la plateforme
            </p>
          </div>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            variant="primary"
          >
            <BuildingOfficeIcon className="h-5 w-5 mr-2" />
            Créer une entreprise
          </Button>
        </div>

        {/* Create Modal */}
        <CreateEntrepriseModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSuccess={() => {
            refetch()
            setIsCreateModalOpen(false)
          }}
        />

        {/* Search Bar */}
        <Card>
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par nom, SIRET ou email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
            />
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-jlc-purple-100 rounded-lg">
                <BuildingOfficeIcon className="h-6 w-6 text-jlc-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Entreprises</p>
                <p className="text-2xl font-bold text-gray-900">{entreprises.length}</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckIcon className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Actives</p>
                <p className="text-2xl font-bold text-gray-900">
                  {entreprises.filter((e: Entreprise) => e.status === 'active').length}
                </p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <MagnifyingGlassIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Résultats</p>
                <p className="text-2xl font-bold text-gray-900">{filteredEntreprises.length}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Entreprises List */}
        {filteredEntreprises.length === 0 ? (
          <Card className="text-center py-12">
            <BuildingOfficeIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm ? 'Aucun résultat trouvé' : 'Aucune entreprise enregistrée'}
            </h3>
            <p className="text-gray-600">
              {searchTerm
                ? 'Essayez de modifier votre recherche'
                : 'Aucune société n\'est enregistrée à ce jour'}
            </p>
          </Card>
        ) : (
          <div className="space-y-3">
            {filteredEntreprises.map((entreprise: Entreprise) => (
              <Card key={entreprise.id} className="hover:shadow-md transition-shadow">
                {/* Header - Always Visible */}
                <div
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => handleExpand(entreprise.id)}
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="p-2 bg-jlc-purple-100 rounded-lg">
                      <BuildingOfficeIcon className="h-6 w-6 text-jlc-purple-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {entreprise.nom}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                        <span className="flex items-center gap-1">
                          <MapPinIcon className="h-4 w-4" />
                          {entreprise.ville}, {entreprise.pays}
                        </span>
                        <span>SIRET: {entreprise.siret}</span>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            entreprise.status === 'active'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {entreprise.status === 'active' ? 'Active' : entreprise.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  {expandedId === entreprise.id ? (
                    <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronRightIcon className="h-5 w-5 text-gray-400" />
                  )}
                </div>

                {/* Expanded Content */}
                {expandedId === entreprise.id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    {editingId === entreprise.id ? (
                      /* Edit Mode */
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Nom Commercial
                            </label>
                            <input
                              type="text"
                              name="nom"
                              value={editForm.nom || ''}
                              onChange={handleInputChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Raison Sociale
                            </label>
                            <input
                              type="text"
                              name="raison_sociale"
                              value={editForm.raison_sociale || ''}
                              onChange={handleInputChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              SIRET
                            </label>
                            <input
                              type="text"
                              name="siret"
                              value={editForm.siret || ''}
                              onChange={handleInputChange}
                              maxLength={14}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Email
                            </label>
                            <input
                              type="email"
                              name="email"
                              value={editForm.email || ''}
                              onChange={handleInputChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Téléphone
                            </label>
                            <input
                              type="tel"
                              name="telephone"
                              value={editForm.telephone || ''}
                              onChange={handleInputChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Site Web
                            </label>
                            <input
                              type="url"
                              name="site_web"
                              value={editForm.site_web || ''}
                              onChange={handleInputChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                            />
                          </div>
                        </div>
                        
                        <div className="flex justify-end gap-2 pt-4 border-t">
                          <Button onClick={handleCancel} variant="secondary" size="sm">
                            <XMarkIcon className="h-4 w-4 mr-1" />
                            Annuler
                          </Button>
                          <Button onClick={() => handleSave(entreprise.id)} variant="primary" size="sm">
                            <CheckIcon className="h-4 w-4 mr-1" />
                            Enregistrer
                          </Button>
                        </div>
                      </div>
                    ) : (
                      /* View Mode */
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-gray-600">Raison Sociale</p>
                            <p className="text-gray-900">{entreprise.raison_sociale || '-'}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Secteur</p>
                            <p className="text-gray-900">{entreprise.secteur_activite || '-'}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Effectif</p>
                            <p className="text-gray-900">{entreprise.effectif || '-'}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Email</p>
                            <p className="text-gray-900 flex items-center gap-1">
                              <EnvelopeIcon className="h-4 w-4 text-gray-400" />
                              {entreprise.email || '-'}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Téléphone</p>
                            <p className="text-gray-900 flex items-center gap-1">
                              <PhoneIcon className="h-4 w-4 text-gray-400" />
                              {entreprise.telephone || '-'}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-600">Adresse</p>
                            <p className="text-gray-900">
                              {entreprise.adresse}, {entreprise.code_postal} {entreprise.ville}
                            </p>
                          </div>
                        </div>
                        
                        {entreprise.description && (
                          <div>
                            <p className="text-sm font-medium text-gray-600 mb-1">Description</p>
                            <p className="text-gray-900">{entreprise.description}</p>
                          </div>
                        )}
                        
                        <div className="flex justify-end pt-4 border-t">
                          <Button onClick={() => handleEdit(entreprise)} variant="secondary" size="sm">
                            <PencilIcon className="h-4 w-4 mr-1" />
                            Modifier
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
