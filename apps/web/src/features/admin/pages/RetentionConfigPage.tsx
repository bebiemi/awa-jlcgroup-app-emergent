import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import {
  ShieldCheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  PlusIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import {
  useGetRetentionPoliciesQuery,
  useGetRetentionStatsQuery,
  useUpdateRetentionPolicyMutation,
  useInitializeDefaultPoliciesMutation,
} from '../api/retentionPoliciesApi'
import { toast } from 'react-hot-toast'

export default function RetentionConfigPage() {
  const { data: policiesData, isLoading, refetch } = useGetRetentionPoliciesQuery({})
  const { data: stats } = useGetRetentionStatsQuery()
  const [updatePolicy, { isLoading: isUpdating }] = useUpdateRetentionPolicyMutation()
  const [initDefaults, { isLoading: isInitializing }] = useInitializeDefaultPoliciesMutation()

  const [editingPolicy, setEditingPolicy] = useState<string | null>(null)
  const [editValues, setEditValues] = useState<{ [key: string]: number }>({})

  const policies = policiesData?.policies || []

  const handleInitDefaults = async () => {
    try {
      const result = await initDefaults().unwrap()
      toast.success(result.message)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'initialisation')
    }
  }

  const startEditing = (policyId: string, currentDays: number) => {
    setEditingPolicy(policyId)
    setEditValues({ ...editValues, [policyId]: currentDays })
  }

  const cancelEditing = () => {
    setEditingPolicy(null)
  }

  const savePolicy = async (policyId: string) => {
    const newDays = editValues[policyId]
    
    if (newDays < 7 || newDays > 3650) {
      toast.error('La période de rétention doit être entre 7 et 3650 jours (10 ans)')
      return
    }

    try {
      await updatePolicy({
        policyId,
        data: { retention_days: newDays }
      }).unwrap()
      
      toast.success('Politique mise à jour avec succès')
      setEditingPolicy(null)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la mise à jour')
    }
  }

  const togglePolicy = async (policyId: string, currentState: boolean) => {
    try {
      await updatePolicy({
        policyId,
        data: { is_enabled: !currentState }
      }).unwrap()
      
      toast.success(`Politique ${!currentState ? 'activée' : 'désactivée'}`)
      refetch()
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la modification')
    }
  }

  const getEntityIcon = (entityType: string) => {
    switch (entityType) {
      case 'users': return '👤'
      case 'documents': return '📄'
      case 'missions': return '💼'
      case 'companies': return '🏢'
      case 'applications': return '📝'
      case 'contracts': return '📋'
      case 'audit_logs': return '🔍'
      default: return '📦'
    }
  }

  const getRetentionLabel = (days: number) => {
    if (days < 30) return `${days} jours`
    if (days < 365) {
      const months = Math.floor(days / 30)
      return `${months} mois (${days}j)`
    }
    const years = Math.floor(days / 365)
    const remainingDays = days % 365
    return remainingDays > 0 
      ? `${years} an${years > 1 ? 's' : ''} et ${remainingDays}j`
      : `${years} an${years > 1 ? 's' : ''}`
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <ShieldCheckIcon className="h-8 w-8 text-jlc-purple-600" />
              Rétention des Données (RGPD)
            </h1>
            <p className="mt-2 text-gray-600">
              Configurez les délais de conservation pour tous les types de données conformément au RGPD
            </p>
          </div>
          
          {policies.length === 0 && !isLoading && (
            <button
              onClick={handleInitDefaults}
              disabled={isInitializing}
              className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors disabled:opacity-50"
            >
              <PlusIcon className="h-5 w-5" />
              {isInitializing ? 'Initialisation...' : 'Initialiser les politiques'}
            </button>
          )}
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-xl border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-700 font-medium">Total Politiques</p>
                  <p className="text-2xl font-bold text-blue-900">{stats.total_policies}</p>
                </div>
                <ChartBarIcon className="h-10 w-10 text-blue-600 opacity-50" />
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-xl border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-700 font-medium">Actives</p>
                  <p className="text-2xl font-bold text-green-900">{stats.active_policies}</p>
                </div>
                <CheckIcon className="h-10 w-10 text-green-600 opacity-50" />
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-xl border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-700 font-medium">Inactives</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.inactive_policies}</p>
                </div>
                <XMarkIcon className="h-10 w-10 text-gray-600 opacity-50" />
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-xl border border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-700 font-medium">Entités archivées</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {Object.values(stats.total_entities_in_retention).reduce((a, b) => a + b, 0)}
                  </p>
                </div>
                <ClockIcon className="h-10 w-10 text-purple-600 opacity-50" />
              </div>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-gray-200 rounded-2xl" />
            <div className="h-48 bg-gray-200 rounded-2xl" />
          </div>
        ) : policies.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-12 text-center">
            <InformationCircleIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucune politique configurée</h3>
            <p className="text-gray-600 mb-6">
              Initialisez les politiques de rétention par défaut pour commencer
            </p>
            <button
              onClick={handleInitDefaults}
              disabled={isInitializing}
              className="px-6 py-3 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors disabled:opacity-50"
            >
              {isInitializing ? 'Initialisation...' : 'Initialiser les politiques par défaut'}
            </button>
          </div>
        ) : (
          <>
            {/* Policies List */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-jlc-purple-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <ClockIcon className="h-6 w-6 text-jlc-purple-600" />
                  Politiques de Rétention Configurées
                </h2>
              </div>

              <div className="divide-y divide-gray-200">
                {policies.map((policy) => {
                  const isEditing = editingPolicy === policy.id
                  const currentValue = isEditing ? editValues[policy.id] : policy.retention_days
                  
                  return (
                    <div key={policy.id} className="p-6 hover:bg-gray-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-2xl">{getEntityIcon(policy.entity_type)}</span>
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900">
                                {policy.entity_label}
                              </h3>
                              <p className="text-sm text-gray-600">{policy.description}</p>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-6 mt-4">
                            {/* Retention Days */}
                            <div className="flex items-center gap-3">
                              <span className="text-sm font-medium text-gray-700">Délai de rétention :</span>
                              {isEditing ? (
                                <div className="flex items-center gap-2">
                                  <input
                                    type="number"
                                    min="7"
                                    max="3650"
                                    value={currentValue}
                                    onChange={(e) => setEditValues({ 
                                      ...editValues, 
                                      [policy.id]: parseInt(e.target.value) || 7 
                                    })}
                                    className="w-24 px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                                  />
                                  <span className="text-sm text-gray-600">jours</span>
                                </div>
                              ) : (
                                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                                  {getRetentionLabel(policy.retention_days)}
                                </span>
                              )}
                            </div>
                            
                            {/* Workflow Stages */}
                            {policy.workflow_stages_count > 0 && (
                              <div className="flex items-center gap-2 text-sm text-gray-600">
                                <span>🔄</span>
                                <span>{policy.workflow_stages_count} étapes configurées</span>
                              </div>
                            )}
                            
                            {/* Status Badge */}
                            <div>
                              <button
                                onClick={() => togglePolicy(policy.id, policy.is_enabled)}
                                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                  policy.is_enabled
                                    ? 'bg-green-100 text-green-800 hover:bg-green-200'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                              >
                                {policy.is_enabled ? '✓ Active' : '✕ Inactive'}
                              </button>
                            </div>
                          </div>
                        </div>
                        
                        {/* Actions */}
                        <div className="flex items-center gap-2 ml-4">
                          {isEditing ? (
                            <>
                              <button
                                onClick={() => savePolicy(policy.id)}
                                disabled={isUpdating}
                                className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50"
                                title="Enregistrer"
                              >
                                <CheckIcon className="h-5 w-5" />
                              </button>
                              <button
                                onClick={cancelEditing}
                                disabled={isUpdating}
                                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
                                title="Annuler"
                              >
                                <XMarkIcon className="h-5 w-5" />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => startEditing(policy.id, policy.retention_days)}
                              className="p-2 text-jlc-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                              title="Modifier"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {/* Warning for short retention */}
                      {currentValue < 30 && (
                        <div className="mt-4 flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0" />
                          <p className="text-sm text-yellow-800">
                            Attention : Période de rétention très courte. Recommandé : minimum 30 jours.
                          </p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Information Panel */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Informations importantes
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex gap-3">
                  <span className="text-jlc-purple-600 font-bold">•</span>
                  <p>
                    <strong>Archivage :</strong> Les utilisateurs archivés restent dans la base de données mais sont marqués comme inactifs et ne peuvent plus se connecter.
                  </p>
                </div>
                <div className="flex gap-3">
                  <span className="text-jlc-purple-600 font-bold">•</span>
                  <p>
                    <strong>Période de rétention :</strong> Après archivage, les données sont conservées pendant la période configurée avant suppression définitive.
                  </p>
                </div>
                <div className="flex gap-3">
                  <span className="text-jlc-purple-600 font-bold">•</span>
                  <p>
                    <strong>Restauration :</strong> Les utilisateurs archivés peuvent être restaurés à tout moment pendant la période de rétention.
                  </p>
                </div>
                <div className="flex gap-3">
                  <span className="text-jlc-purple-600 font-bold">•</span>
                  <p>
                    <strong>Suppression définitive :</strong> Une fois la période de rétention écoulée, les données sont supprimées de manière irréversible.
                  </p>
                </div>
                <div className="flex gap-3">
                  <span className="text-jlc-purple-600 font-bold">•</span>
                  <p>
                    <strong>Recommandation :</strong> Une période de 90 jours (3 mois) est généralement recommandée pour un bon équilibre entre sécurité et gestion de l'espace disque.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}
