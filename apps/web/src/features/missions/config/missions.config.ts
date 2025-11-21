/**
 * Configuration de la page Missions
 * Basé sur NeedListTemplate (workflow + suivi + RH + Paie + Emargement)
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
  subtitle: "Suivi complet des missions, affectations et émargements",

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
    related: {
      emargements: "missions.emargements.read",
      candidats: "candidatures.read.all",
      besoins: "besoins.read.all",
    }
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
    status: ["ouverte", "en_cours", "en_pause", "terminée", "annulée"],
    entreprise: {
      enabled: true,
      type: "select",
      source: "references.entreprises",
    },
    interimaire: {
      enabled: true,
      type: "select",
      source: "references.interimaires",
    },
  },

  relatedActions: [
    {
      label: "Émargements",
      to: (id: string) => `/admin/missions/${id}/emargements`,
      permission: "missions.emargements.read",
    },
    {
      label: "Suivi RH",
      to: (id: string) => `/admin/missions/${id}/rh`,
      permission: "missions.rh.read",
    },
    {
      label: "Archive missions",
      to: (id: string) => `/admin/missions/${id}/archive`,
      permission: "missions.archive.read",
    }
  ],

  pagination: {
    pageSize: 20,
    serverSide: true,
  },
}
