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
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <ShieldCheckIcon className="h-8 w-8 text-jlc-purple-600" />
            Configuration de la Rétention des Données
          </h1>
          <p className="mt-2 text-gray-600">
            Configurez la période de rétention des utilisateurs archivés avant suppression définitive
          </p>
        </div>

        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-gray-200 rounded-2xl" />
            <div className="h-48 bg-gray-200 rounded-2xl" />
          </div>
        ) : (
          <>
            {/* Configuration Card */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-jlc-purple-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <ClockIcon className="h-6 w-6 text-jlc-purple-600" />
                  Période de Rétention
                </h2>
              </div>

              <div className="p-6 space-y-6">
                {/* Current Config Info */}
                <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <InformationCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-900">
                      Configuration actuelle : {config?.retention_days} jours
                    </p>
                    <p className="text-sm text-blue-700 mt-1">
                      Source : {config?.source === 'database' ? 'Base de données (personnalisé)' : 'Configuration YAML (par défaut)'}
                    </p>
                  </div>
                </div>

                {/* Retention Days Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de jours avant suppression définitive
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="1"
                      max="365"
                      value={retentionDays}
                      onChange={(e) => handleChange(parseInt(e.target.value))}
                      disabled={!config?.can_override}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{
                        background: config?.can_override
                          ? `linear-gradient(to right, #6d28d9 0%, #6d28d9 ${((retentionDays - 1) / 364) * 100}%, #e5e7eb ${((retentionDays - 1) / 364) * 100}%, #e5e7eb 100%)`
                          : '#e5e7eb',
                      }}
                    />
                    <input
                      type="number"
                      min="1"
                      max="365"
                      value={retentionDays}
                      onChange={(e) => handleChange(parseInt(e.target.value) || 1)}
                      disabled={!config?.can_override}
                      className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                    />
                    <span className="text-sm font-medium text-gray-600 whitespace-nowrap">
                      jours
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    Les utilisateurs archivés seront automatiquement supprimés après cette période
                  </p>
                </div>

                {/* Warning Message */}
                {retentionDays < 30 && (
                  <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-yellow-900">
                        Attention : Période de rétention courte
                      </p>
                      <p className="text-sm text-yellow-700 mt-1">
                        Une période de rétention inférieure à 30 jours peut ne pas laisser suffisamment de temps pour restaurer des utilisateurs en cas d'erreur.
                      </p>
                    </div>
                  </div>
                )}

                {!config?.can_override && (
                  <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-900">
                        Modifications non autorisées
                      </p>
                      <p className="text-sm text-red-700 mt-1">
                        La période de rétention est verrouillée par la configuration YAML. Contactez l'administrateur système pour la modifier.
                      </p>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                {config?.can_override && (
                  <div className="flex gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={handleSave}
                      disabled={!hasChanges || isUpdating}
                      className="px-6 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-jlc-purple-600 disabled:hover:to-indigo-600"
                    >
                      {isUpdating ? 'Enregistrement...' : 'Enregistrer'}
                    </button>
                    <button
                      onClick={handleReset}
                      disabled={!hasChanges || isUpdating}
                      className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Annuler
                    </button>
                  </div>
                )}
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
