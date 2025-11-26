import React, { useState } from 'react'
import {
  useListEmailDomainsQuery,
  useCreateEmailDomainMutation,
  useUpdateEmailDomainMutation,
  useDeleteEmailDomainMutation,
  AllowedEmailDomain,
  AllowedEmailDomainCreate
} from '../api/emailDomainsApi'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Modal from '@/components/Modal'
import Tooltip from '@/components/Tooltip'
import { toast } from 'react-hot-toast'
import { PlusIcon, GlobeAltIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { usePermissions } from '@/hooks/usePermission'

const EmailDomainsPage: React.FC = () => {
  const { permissions } = usePermissions(['security.email_domains.read', 'security.email_domains.manage'])
  const canRead = permissions['security.email_domains.read'] || permissions['security.email_domains.manage']
  const canManage = permissions['security.email_domains.manage']

  const { data: domains, isLoading } = useListEmailDomainsQuery(undefined)
  const [createDomain] = useCreateEmailDomainMutation()
  const [updateDomain] = useUpdateEmailDomainMutation()
  const [deleteDomain] = useDeleteEmailDomainMutation()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [selectedDomain, setSelectedDomain] = useState<AllowedEmailDomain | null>(null)

  const [formData, setFormData] = useState<AllowedEmailDomainCreate>({
    domain: '',
    country_code: '',
    is_active: true,
    metadata: {}
  })

  const resetForm = () => {
    setFormData({
      domain: '',
      country_code: '',
      is_active: true,
      metadata: {}
    })
  }

  const handleCreateClick = () => {
    if (!canManage) return
    resetForm()
    setShowCreateModal(true)
  }

  const handleEditClick = (domain: AllowedEmailDomain) => {
    if (!canManage) return
    setSelectedDomain(domain)
    setFormData({
      domain: domain.domain,
      country_code: domain.country_code || '',
      is_active: domain.is_active,
      metadata: domain.metadata || {}
    })
    setShowEditModal(true)
  }

  const handleDeleteClick = (domain: AllowedEmailDomain) => {
    if (!canManage) return
    setSelectedDomain(domain)
    setShowDeleteModal(true)
  }

  const handleCreateSubmit = async () => {
    if (!canManage) return
    if (!formData.domain) {
      toast.error('Le domaine est requis')
      return
    }

    try {
      await createDomain({
        ...formData,
        country_code: formData.country_code || undefined
      }).unwrap()
      toast.success('Domaine créé avec succès')
      setShowCreateModal(false)
      resetForm()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création')
    }
  }

  const handleEditSubmit = async () => {
    if (!canManage) return
    if (!selectedDomain) return

    try {
      await updateDomain({
        id: selectedDomain.id,
        data: {
          country_code: formData.country_code || undefined,
          is_active: formData.is_active,
          metadata: formData.metadata
        }
      }).unwrap()
      toast.success('Domaine mis à jour avec succès')
      setShowEditModal(false)
      setSelectedDomain(null)
      resetForm()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const handleDeleteConfirm = async () => {
    if (!canManage) return
    if (!selectedDomain) return

    try {
      await deleteDomain(selectedDomain.id).unwrap()
      toast.success('Domaine supprimé avec succès')
      setShowDeleteModal(false)
      setSelectedDomain(null)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la suppression')
    }
  }

  const stats = {
    total: domains?.length || 0,
    active: domains?.filter(d => d.is_active).length || 0,
    inactive: domains?.filter(d => !d.is_active).length || 0,
    withCountry: domains?.filter(d => d.country_code).length || 0
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  if (!canRead) return null

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Domaines Email Autorisés</h1>
            <p className="text-gray-600 mt-1">
              Gérer les domaines email pour les comptes collaborateurs
            </p>
          </div>
          <button
            onClick={handleCreateClick}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors shadow-md hover:shadow-lg"
          >
            <PlusIcon className="h-5 w-5" />
            Nouveau Domaine
          </button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Tooltip content="Nombre total de domaines configurés" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Domaines</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                </div>
                <div className="text-3xl">🌐</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Domaines actuellement actifs" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Actifs</p>
                  <p className="text-2xl font-bold text-green-600">{stats.active}</p>
                </div>
                <div className="text-3xl">✅</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Domaines désactivés" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Inactifs</p>
                  <p className="text-2xl font-bold text-red-600">{stats.inactive}</p>
                </div>
                <div className="text-3xl">❌</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Domaines avec code pays" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avec Pays</p>
                  <p className="text-2xl font-bold text-jlc-purple-600">{stats.withCountry}</p>
                </div>
                <div className="text-3xl">🏳️</div>
              </div>
            </Card>
          </Tooltip>
        </div>

        {/* Domains List */}
        <Card>
          {!domains || domains.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🌐</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun domaine configuré</h3>
              <p className="text-gray-500 mb-4">
                Ajoutez des domaines email autorisés pour les collaborateurs
              </p>
              <button
                onClick={handleCreateClick}
                className="inline-flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
              >
                <PlusIcon className="h-5 w-5" />
                Créer le premier domaine
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Domaine
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pays
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Créé le
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {domains.map((domain) => (
                    <tr key={domain.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <GlobeAltIcon className="h-5 w-5 text-jlc-purple-600 mr-2" />
                          <span className="text-sm font-medium text-gray-900">
                            {domain.domain}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {domain.country_code ? (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                            {domain.country_code}
                          </span>
                        ) : (
                          <span className="text-sm text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {domain.is_active ? (
                          <span className="flex items-center gap-1 text-green-600">
                            <CheckCircleIcon className="h-5 w-5" />
                            <span className="text-sm font-medium">Actif</span>
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600">
                            <XCircleIcon className="h-5 w-5" />
                            <span className="text-sm font-medium">Inactif</span>
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(domain.created_at).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEditClick(domain)}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          Modifier
                        </button>
                        <button
                          onClick={() => handleDeleteClick(domain)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          resetForm()
        }}
        title="Créer un Domaine Email"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Domaine Email *
            </label>
            <input
              type="text"
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
              placeholder="@jlcgroup.org"
            />
            <p className="text-xs text-gray-500 mt-1">
              Le domaine doit commencer par @ (ex: @jlcgroup.org)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code Pays
            </label>
            <input
              type="text"
              value={formData.country_code}
              onChange={(e) => setFormData({ ...formData, country_code: e.target.value.toUpperCase() })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
              placeholder="GA, CM, CG..."
              maxLength={2}
            />
            <p className="text-xs text-gray-500 mt-1">
              Code pays ISO à 2 lettres (optionnel)
            </p>
          </div>

          <div>
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500 h-4 w-4"
              />
              <span className="ml-2 text-sm text-gray-700">Domaine actif</span>
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowCreateModal(false)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleCreateSubmit}
              disabled={!formData.domain}
              className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Créer
            </button>
          </div>
        </div>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false)
          setSelectedDomain(null)
          resetForm()
        }}
        title="Modifier le Domaine"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Domaine Email
            </label>
            <input
              type="text"
              value={formData.domain}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Code Pays
            </label>
            <input
              type="text"
              value={formData.country_code}
              onChange={(e) => setFormData({ ...formData, country_code: e.target.value.toUpperCase() })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
              placeholder="GA, CM, CG..."
              maxLength={2}
            />
          </div>

          <div>
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500 h-4 w-4"
              />
              <span className="ml-2 text-sm text-gray-700">Domaine actif</span>
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowEditModal(false)
                setSelectedDomain(null)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleEditSubmit}
              className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors"
            >
              Mettre à jour
            </button>
          </div>
        </div>
      </Modal>

      {/* Delete Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false)
          setSelectedDomain(null)
        }}
        title="Supprimer le Domaine"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Êtes-vous sûr de vouloir supprimer le domaine{' '}
            <span className="font-semibold">{selectedDomain?.domain}</span> ?
          </p>
          <p className="text-sm text-red-600">
            Cette action désactivera le domaine. Les collaborateurs avec ce domaine ne pourront plus créer de comptes.
          </p>

          <div className="flex gap-3 pt-4">
            <button
              onClick={() => {
                setShowDeleteModal(false)
                setSelectedDomain(null)
              }}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleDeleteConfirm}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Supprimer
            </button>
          </div>
        </div>
      </Modal>
    </Layout>
  )
}

export default EmailDomainsPage
