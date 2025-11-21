/**
 * Configuration page Validations (Candidatures / Entreprises / Comptes / Avertissements)
 * Zero duplication – Entièrement piloté par config
 */

import {
  useListValidationsQuery,
  useGetValidationQuery,
  useApproveValidationMutation,
  useRejectValidationMutation,
} from '../api/validationsApi'

export const ValidationsPageConfig = {
  title: "Centre de Validation",
  subtitle: "Validez, rejetez et contrôlez les actions importantes de la plateforme",

  api: {
    list: useListValidationsQuery,
    get: useGetValidationQuery,
    approve: useApproveValidationMutation,
    reject: useRejectValidationMutation,
  },

  permissions: {
    view: "validations.read.all",
    approve: "validations.approve",
    reject: "validations.reject",
  },

  columns: [
    { key: "type", label: "Type", sortable: true, badge: true },
    { key: "cible_nom", label: "Cible", sortable: true },
    { key: "soumis_par", label: "Soumis par", sortable: true },
    { key: "date_soumission", label: "Soumis le", sortable: true },
    { key: "status", label: "Statut", badge: true },
  ],

  filters: {
    type: ["entreprise", "candidat", "collaborateur", "mission", "avertissement"],
    status: ["en_attente", "validé", "rejeté"],
  },

  relatedActions: [
    {
      label: "Voir la fiche complète",
      to: (id: string) => `/admin/validations/${id}/details`,
      permission: "validations.read.all",
    }
  ],

  pagination: {
    pageSize: 20,
    serverSide: true,
  },
}
