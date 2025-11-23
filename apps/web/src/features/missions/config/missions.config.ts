/**
 * Configuration de la page Missions
 * Architecture Config-Driven (EntityListTemplate)
 */

import {
  useListMissionsQuery,
  useGetMissionQuery,
  useCreateMissionMutation,
  useUpdateMissionMutation,
  useDeleteMissionMutation,
} from '../api/missionApi'

export const MissionsPageConfig = {
  title: "Gestion des Missions",
  subtitle: "Suivi opérationnel des missions et de leurs statuts",

  api: {
    list: useListMissionsQuery,
    get: useGetMissionQuery,
    create: useCreateMissionMutation,
    update: useUpdateMissionMutation,
    delete: useDeleteMissionMutation,
  },

  permissions: {
    view: "missions.read.all",
    create: "missions.create",
    edit: "missions.edit",
    delete: "missions.delete",
    archive: "missions.archive",
    cancel: "missions.cancel",
  },

  columns: [
    { key: "title", label: "Mission", sortable: true },
    { key: "job_type", label: "Type de poste", sortable: true },
    { key: "location", label: "Localisation", sortable: true },
    { key: "start_date", label: "Début", sortable: true },
    { key: "end_date", label: "Fin", sortable: true },
    { key: "status", label: "Statut", badge: true },
  ],

  filters: {
    status: ["ouverte", "en_cours", "en_pause", "terminee", "annulee"],
  },
}
