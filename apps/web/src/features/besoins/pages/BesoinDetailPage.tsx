import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import {
  ArrowLeftIcon,
  PencilIcon,
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import {
  useGetBesoinQuery,
  useSubmitBesoinMutation,
  useGetCommentsQuery,
  useAddCommentMutation,
} from '../api/besoinApi'
import { useGetWorkflowConfigQuery } from '../api/configApi'
import { toast } from 'react-hot-toast'
import CommentThread from '../components/CommentThread'
import StatusTimeline from '../components/StatusTimeline'

export default function BesoinDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [showComments, setShowComments] = useState(false)

  const { data: besoin, isLoading } = useGetBesoinQuery(id!)
  const { data: workflowConfig } = useGetWorkflowConfigQuery('besoin')
  const [submitBesoin, { isLoading: submitting }] = useSubmitBesoinMutation()

  const handleSubmit = async () => {
    if (!besoin) return

    if (!window.confirm('Êtes-vous sûr de vouloir soumettre ce besoin à JLC ? Il ne pourra plus être modifié.')) {
      return
    }

    try {
      await submitBesoin(besoin.id).unwrap()
      toast.success('Besoin soumis à JLC avec succès')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la soumission')
    }
  }

  const getStatusConfig = () => {
    if (!workflowConfig || !besoin) return null
    return workflowConfig.statuses.find((s) => s.key === besoin.status)
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return null
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="animate-pulse space-y-6">
          <div className="h-10 bg-gray-200 rounded w-1/3" />
          <div className="h-64 bg-gray-200 rounded" />
        </div>
      </Layout>
    )
  }

  if (!besoin) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900">Besoin non trouvé</h3>
        </div>
      </Layout>
    )
  }

  const statusConfig = getStatusConfig()
  const isDraft = besoin.status === 'brouillon'
  const canEdit = isDraft

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/entreprise/besoins')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5 text-gray-600" />
            </button>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold text-gray-900">{besoin.titre}</h1>
                {statusConfig && (
                  <span
                    className="px-3 py-1 rounded-full text-sm font-medium"
                    style={{
                      backgroundColor: `${statusConfig.color}20`,
                      color: statusConfig.color,
                    }}
                  >
                    {statusConfig.label.fr}
                  </span>
                )}
              </div>
              <p className="text-gray-600 mt-1">{besoin.type_poste}</p>
            </div>
          </div>
          <div className="flex gap-3">
            {canEdit && (
              <button
                onClick={() => navigate(`/entreprise/besoins/${besoin.id}/edit`)}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <PencilIcon className="h-5 w-5" />
                Modifier
              </button>
            )}
            {isDraft && (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-jlc-purple-600 to-indigo-600 text-white rounded-lg hover:from-jlc-purple-700 hover:to-indigo-700 shadow-md transition-all disabled:opacity-50"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
                {submitting ? 'Soumission...' : 'Soumettre à JLC'}
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{besoin.description}</p>
            </div>

            {/* Competences */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Compétences attendues</h2>
              <div className="flex flex-wrap gap-2">
                {besoin.competences_attendues.map((comp) => (
                  <span
                    key={comp}
                    className="px-3 py-1 bg-jlc-purple-100 text-jlc-purple-700 rounded-full text-sm"
                  >
                    {comp}
                  </span>
                ))}
              </div>
            </div>

            {/* Comments Section */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 overflow-hidden">
              <button
                onClick={() => setShowComments(!showComments)}
                className="w-full flex items-center justify-between p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <ChatBubbleLeftRightIcon className="h-6 w-6 text-jlc-purple-600" />
                  <h2 className="text-lg font-semibold text-gray-900">
                    Discussion ({besoin.comments_count})
                  </h2>
                </div>
                <span className="text-gray-400">
                  {showComments ? '▼' : '▶'}
                </span>
              </button>
              
              {showComments && (
                <div className="border-t border-gray-200">
                  <CommentThread besoinId={besoin.id} />
                </div>
              )}
            </div>

            {/* JLC Analysis (if exists) */}
            {besoin.jlc_analysis && (
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
                <h2 className="text-lg font-semibold text-amber-900 mb-4">Analyse JLC</h2>
                {besoin.jlc_analysis.observations && (
                  <p className="text-amber-800 mb-3">{besoin.jlc_analysis.observations}</p>
                )}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {besoin.jlc_analysis.estimated_budget && (
                    <div>
                      <span className="text-amber-700 font-medium">Budget estimé:</span>
                      <span className="text-amber-900 ml-2">
                        {besoin.jlc_analysis.estimated_budget}€
                      </span>
                    </div>
                  )}
                  {besoin.jlc_analysis.priority && (
                    <div>
                      <span className="text-amber-700 font-medium">Priorité:</span>
                      <span className="text-amber-900 ml-2 capitalize">
                        {besoin.jlc_analysis.priority}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Info Card */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Informations</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">Créé par:</span>
                  <p className="font-medium text-gray-900">{besoin.created_by_name}</p>
                </div>
                <div>
                  <span className="text-gray-600">Créé le:</span>
                  <p className="font-medium text-gray-900">{formatDate(besoin.created_at)}</p>
                </div>
                {besoin.submitted_at && (
                  <div>
                    <span className="text-gray-600">Soumis le:</span>
                    <p className="font-medium text-gray-900">{formatDate(besoin.submitted_at)}</p>
                  </div>
                )}
                <div>
                  <span className="text-gray-600">Durée:</span>
                  <p className="font-medium text-gray-900 capitalize">
                    {besoin.duree === 'indeterminee' ? 'Indéterminée' : 'Période précise'}
                  </p>
                </div>
                {besoin.date_debut_souhaitee && (
                  <div>
                    <span className="text-gray-600">Date début:</span>
                    <p className="font-medium text-gray-900">
                      {new Date(besoin.date_debut_souhaitee).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                )}
                {besoin.date_fin_souhaitee && (
                  <div>
                    <span className="text-gray-600">Date fin:</span>
                    <p className="font-medium text-gray-900">
                      {new Date(besoin.date_fin_souhaitee).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <ClockIcon className="h-5 w-5" />
                Historique
              </h2>
              <StatusTimeline history={besoin.status_history} workflowConfig={workflowConfig} />
            </div>

            {/* Missions liées */}
            {besoin.mission_ids.length > 0 && (
              <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Missions créées</h2>
                <div className="space-y-2">
                  {besoin.mission_ids.map((missionId) => (
                    <a
                      key={missionId}
                      href={`/missions/${missionId}`}
                      className="block px-3 py-2 bg-jlc-purple-50 hover:bg-jlc-purple-100 rounded-lg text-sm text-jlc-purple-700 transition-colors"
                    >
                      Mission #{missionId.slice(0, 8)}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
