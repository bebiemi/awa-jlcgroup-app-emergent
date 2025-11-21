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
    { key: "titre", label: "Mission", sortable: true },
    { key: "entreprise_nom", label: "Entreprise", sortable: true },
    { key: "interimaire_nom", label: "Intérimaire", sortable: true },
    { key: "date_debut", label: "Début", sortable: true },
    { key: "date_fin", label: "Fin", sortable: true },
    { key: "status", label: "Statut", badge: true },
  ],

  filters: {
    status: ["ouverte", "en_cours", "en_pause", "terminee", "annulee"],
  },
}
