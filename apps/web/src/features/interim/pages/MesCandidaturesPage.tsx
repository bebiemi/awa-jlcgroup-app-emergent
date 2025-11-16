import { useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Modal from '@/components/Modal';
import { useGetMyApplicationsQuery } from '../api/applicationApi';
import { useGetActiveContractQuery } from '@/features/contracts/api/contractApi';
import { useUpdateMyApplicationMutation, useCancelMyApplicationMutation } from '@/features/missions/api/missionApi';
import { useApplicationStatuses } from '@/hooks/useAppConfig';
import {
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  BriefcaseIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import { useAppSelector } from '@/store/hooks';
import toast from 'react-hot-toast';

// Timeline des étapes de candidature
const WORKFLOW_STEPS = [
  { key: 'submitted', label: 'Candidature envoyée', icon: '📝' },
  { key: 'review', label: 'Analyse / Pré-sélection', icon: '🔍' },
  { key: 'interviewed', label: 'Entretien', icon: '🤝' },
  { key: 'selected', label: 'Transmission au client', icon: '📤' },
  { key: 'contract_pending', label: 'Validation contrat', icon: '📋' },
  { key: 'contract_signed', label: 'Démarrage mission', icon: '🎯' },
];

interface Application {
  id: string;
  mission_id: string;
  mission_title: string;
  company_name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

function ApplicationTimeline({ currentStatus }: { currentStatus: string }) {
  const getCurrentStepIndex = () => {
    const index = WORKFLOW_STEPS.findIndex((step) => step.key === currentStatus);
    return index >= 0 ? index : 0;
  };

  const currentStepIndex = getCurrentStepIndex();

  return (
    <div className="relative">
      <div className="flex items-center justify-between">
        {WORKFLOW_STEPS.map((step, index) => {
          const isCompleted = index <= currentStepIndex;
          const isCurrent = index === currentStepIndex;

          return (
            <div key={step.key} className="flex flex-col items-center flex-1">
              {/* Ligne de connexion */}
              {index > 0 && (
                <div
                  className={clsx(
                    'absolute h-1 top-4',
                    isCompleted ? 'bg-green-500' : 'bg-gray-300'
                  )}
                  style={{
                    left: `${((index - 1) / (WORKFLOW_STEPS.length - 1)) * 100}%`,
                    width: `${100 / (WORKFLOW_STEPS.length - 1)}%`,
                  }}
                />
              )}

              {/* Cercle d'étape */}
              <div
                className={clsx(
                  'relative z-10 w-10 h-10 rounded-full flex items-center justify-center text-lg',
                  isCompleted
                    ? isCurrent
                      ? 'bg-green-500 ring-4 ring-green-200'
                      : 'bg-green-500'
                    : 'bg-gray-300'
                )}
              >
                {step.icon}
              </div>

              {/* Label */}
              <div className="mt-2 text-center">
                <p
                  className={clsx(
                    'text-xs font-medium',
                    isCompleted ? 'text-gray-900' : 'text-gray-500'
                  )}
                >
                  {step.label}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ApplicationCard({ application, showMissionName }: { application: Application; showMissionName: boolean }) {
  const [showDetails, setShowDetails] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [additionalInfo, setAdditionalInfo] = useState(application.additional_info || '');
  const [cancellationReason, setCancellationReason] = useState('');
  
  const [updateApplication, { isLoading: isUpdating }] = useUpdateMyApplicationMutation();
  const [cancelApplication, { isLoading: isCancelling }] = useCancelMyApplicationMutation();
  
  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; color: string; icon: any }> = {
      pending: { label: 'En attente', color: 'bg-yellow-100 text-yellow-800', icon: ClockIcon },
      submitted: { label: 'Envoyée', color: 'bg-blue-100 text-blue-800', icon: CheckCircleIcon },
      under_review: { label: 'En cours d\'examen', color: 'bg-purple-100 text-purple-800', icon: EyeIcon },
      review: { label: 'En analyse', color: 'bg-purple-100 text-purple-800', icon: EyeIcon },
      interviewed: { label: 'Entretien', color: 'bg-indigo-100 text-indigo-800', icon: EyeIcon },
      selected: { label: 'Sélectionné', color: 'bg-green-100 text-green-800', icon: CheckCircleIcon },
      contract_pending: { label: 'Contrat en attente', color: 'bg-orange-100 text-orange-800', icon: ClockIcon },
      contract_signed: { label: 'Contrat signé', color: 'bg-green-100 text-green-800', icon: BriefcaseIcon },
      rejected: { label: 'Refusée', color: 'bg-red-100 text-red-800', icon: XCircleIcon },
      withdrawn: { label: 'Retirée', color: 'bg-gray-100 text-gray-800', icon: XCircleIcon },
    };

    const config = statusConfig[status] || { label: status, color: 'bg-gray-100 text-gray-800', icon: ClockIcon };
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <Icon className="h-4 w-4 mr-1" />
        {config.label}
      </span>
    );
  };

  // Vérifier si la candidature peut être modifiée
  const canEdit = ['submitted', 'under_review'].includes(application.status);
  
  // Vérifier si la candidature peut être annulée
  const canCancel = !['hired', 'withdrawn', 'contract_signed'].includes(application.status);

  const handleEdit = async () => {
    try {
      await updateApplication({
        application_id: application.id,
        additional_info: additionalInfo,
      }).unwrap();
      
      toast.success('✅ Candidature mise à jour');
      setShowEditModal(false);
    } catch (error: any) {
      toast.error(`❌ ${error?.data?.detail || 'Erreur lors de la mise à jour'}`);
    }
  };

  const handleCancel = async () => {
    try {
      await cancelApplication({
        application_id: application.id,
        cancellation_reason: cancellationReason,
      }).unwrap();
      
      toast.success('✅ Candidature annulée');
      setShowCancelModal(false);
    } catch (error: any) {
      toast.error(`❌ ${error?.data?.detail || 'Erreur lors de l\'annulation'}`);
    }
  };

  const missionDisplayName = showMissionName
    ? application.mission_title
    : 'Mission en cours de sélection';

  return (
    <>
      <Card className="hover:shadow-md transition-shadow">
        <div className="space-y-4">
          {/* En-tête */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">{missionDisplayName}</h3>
              <p className="text-sm text-gray-600 mt-1">{application.company_name}</p>
              <p className="text-xs text-gray-500 mt-1">
                Candidature envoyée le {new Date(application.created_at).toLocaleDateString('fr-FR')}
              </p>
            </div>
            <div>{getStatusBadge(application.status)}</div>
          </div>

          {/* Informations additionnelles */}
          {application.additional_info && showDetails && (
            <div className="pt-2 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Informations additionnelles :</span> {application.additional_info}
              </p>
            </div>
          )}

          {/* Timeline */}
          {showDetails && (
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-4">Progression de votre candidature</h4>
              <ApplicationTimeline currentStatus={application.status} />
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-200">
            <div className="flex gap-2">
              {canEdit && (
                <button
                  onClick={() => setShowEditModal(true)}
                  className="inline-flex items-center px-3 py-1.5 text-sm text-jlc-purple-600 hover:text-jlc-purple-800 font-medium border border-jlc-purple-300 rounded-lg hover:bg-jlc-purple-50 transition"
                >
                  <PencilIcon className="h-4 w-4 mr-1" />
                  Modifier
                </button>
              )}
              {canCancel && (
                <button
                  onClick={() => setShowCancelModal(true)}
                  className="inline-flex items-center px-3 py-1.5 text-sm text-red-600 hover:text-red-800 font-medium border border-red-300 rounded-lg hover:bg-red-50 transition"
                >
                  <TrashIcon className="h-4 w-4 mr-1" />
                  Annuler
                </button>
              )}
            </div>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-sm text-jlc-purple-600 hover:text-jlc-purple-800 font-medium"
            >
              {showDetails ? 'Masquer les détails' : 'Voir les détails'}
            </button>
          </div>
        </div>
      </Card>

      {/* Modal de modification */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Modifier ma candidature"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Informations additionnelles
            </label>
            <textarea
              value={additionalInfo}
              onChange={(e) => setAdditionalInfo(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              placeholder="Ajoutez des informations complémentaires..."
            />
            <p className="text-xs text-gray-500 mt-1">
              💡 Vous pouvez ajouter des détails sur votre motivation, vos disponibilités, etc.
            </p>
          </div>
          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() => setShowEditModal(false)}
              disabled={isUpdating}
            >
              Annuler
            </Button>
            <Button
              variant="primary"
              onClick={handleEdit}
              isLoading={isUpdating}
              disabled={isUpdating}
            >
              Enregistrer
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal d'annulation */}
      <Modal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        title="Annuler ma candidature"
      >
        <div className="space-y-4">
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ Cette action est irréversible. Vous ne pourrez plus postuler à cette mission.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Raison de l'annulation (optionnel)
            </label>
            <textarea
              value={cancellationReason}
              onChange={(e) => setCancellationReason(e.target.value)}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Pourquoi annulez-vous cette candidature ?"
            />
          </div>
          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() => setShowCancelModal(false)}
              disabled={isCancelling}
            >
              Retour
            </Button>
            <Button
              variant="danger"
              onClick={handleCancel}
              isLoading={isCancelling}
              disabled={isCancelling}
            >
              Confirmer l'annulation
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}

export default function MesCandidaturesPage() {
  const currentUser = useAppSelector((state) => state.auth.user);
  const isInterimaire = currentUser?.roles?.includes('intérimaire') ?? false;

  const { data: applicationsData, isLoading: applicationsLoading } = useGetMyApplicationsQuery();
  // Only fetch active contract for intérimaires
  const { data: contractData } = useGetActiveContractQuery(undefined, {
    skip: !isInterimaire,
  });
  const applicationStatuses = useApplicationStatuses();

  const activeContract = contractData?.active_contract;
  const canApply = contractData?.can_apply ?? true;

  if (applicationsLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    );
  }

  const applications = applicationsData?.applications || [];

  // Regrouper les candidatures par statut
  const groupedApplications = {
    enCours: applications.filter((app) =>
      ['submitted', 'review', 'interviewed', 'selected', 'contract_pending'].includes(app.status)
    ),
    acceptees: applications.filter((app) => app.status === 'contract_signed'),
    refusees: applications.filter((app) => app.status === 'rejected'),
    retirees: applications.filter((app) => app.status === 'withdrawn'),
  };

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* En-tête */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mes Candidatures</h1>
          <p className="text-gray-600 mt-2">Suivez l'évolution de vos candidatures</p>
        </div>

        {/* Alerte mission active */}
        {activeContract && !canApply && (
          <Card className="border-l-4 border-blue-500 bg-blue-50">
            <div className="flex items-start">
              <BriefcaseIcon className="h-6 w-6 text-blue-600 mt-0.5 mr-3" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-blue-900">Mission en cours</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Vous êtes actuellement en mission sur <strong>{activeContract.mission_title}</strong>.
                  Les nouvelles candidatures seront possibles 5 jours ouvrés avant la fin de votre mission.
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Stats rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Total</p>
            <p className="text-2xl font-bold text-gray-900">{applications.length}</p>
          </div>
          <div className="bg-blue-50 rounded-lg shadow p-4">
            <p className="text-sm text-blue-600">En cours</p>
            <p className="text-2xl font-bold text-blue-900">{groupedApplications.enCours.length}</p>
          </div>
          <div className="bg-green-50 rounded-lg shadow p-4">
            <p className="text-sm text-green-600">Acceptées</p>
            <p className="text-2xl font-bold text-green-900">{groupedApplications.acceptees.length}</p>
          </div>
          <div className="bg-red-50 rounded-lg shadow p-4">
            <p className="text-sm text-red-600">Refusées</p>
            <p className="text-2xl font-bold text-red-900">{groupedApplications.refusees.length}</p>
          </div>
        </div>

        {/* Candidatures en cours */}
        {groupedApplications.enCours.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">📋 Candidatures en cours</h2>
            <div className="space-y-4">
              {groupedApplications.enCours.map((app) => (
                <ApplicationCard
                  key={app.id}
                  application={app}
                  showMissionName={app.status === 'contract_signed'}
                />
              ))}
            </div>
          </div>
        )}

        {/* Candidatures acceptées */}
        {groupedApplications.acceptees.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">✅ Candidatures acceptées</h2>
            <div className="space-y-4">
              {groupedApplications.acceptees.map((app) => (
                <ApplicationCard key={app.id} application={app} showMissionName={true} />
              ))}
            </div>
          </div>
        )}

        {/* Candidatures refusées */}
        {groupedApplications.refusees.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">❌ Candidatures refusées</h2>
            <div className="space-y-4">
              {groupedApplications.refusees.map((app) => (
                <ApplicationCard key={app.id} application={app} showMissionName={true} />
              ))}
            </div>
          </div>
        )}

        {/* Aucune candidature */}
        {applications.length === 0 && (
          <Card className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <BriefcaseIcon className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune candidature</h3>
            <p className="text-gray-600 mb-6">
              Vous n'avez pas encore postulé à des missions.
            </p>
            <a
              href="/offres"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-jlc-purple-600 hover:bg-jlc-purple-700"
            >
              Découvrir les offres
            </a>
          </Card>
        )}
      </div>
    </Layout>
  );
}
