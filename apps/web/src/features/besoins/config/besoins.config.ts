/**
 * Configuration de la page des Besoins (demande de missions)
 * Utilise NeedListTemplate – workflow, statuts, commentaires, validations
 */

import {
  useListBesoinsQuery,
  useGetBesoinQuery,
  useCreateBesoinMutation,
  useUpdateBesoinMutation,
  useDeleteBesoinMutation,
  useValidateBesoinMutation,
} from '../api/besoinsApi'

export const BesoinsPageConfig = {
  title: "Gestion des Besoins",
  subtitle: "Consultez et gérez les besoins exprimés par les entreprises",

  api: {
    list: useListBesoinsQuery,
    get: useGetBesoinQuery,
    create: useCreateBesoinMutation,
    update: useUpdateBesoinMutation,
    delete: useDeleteBesoinMutation,
    validate: useValidateBesoinMutation,
  },

  /** IAM */
  permissions: {
    view: "besoins.read.all",
    create: "besoins.create",
    edit: "besoins.edit",
    delete: "besoins.delete",
    validate: "besoins.validate",
    related: {
      missions: "missions.read.own",
    }
  },

  /** Colonnes */
  columns: [
    { key: "titre", label: "Titre", sortable: true },
    { key: "entreprise_name", label: "Entreprise", sortable: true },
    { key: "type_poste", label: "Type de besoin", sortable: true },
    { key: "date_debut_souhaitee", label: "Début", sortable: true },
    { key: "date_fin_souhaitee", label: "Fin", sortable: true },
    { key: "status", label: "Statut", badge: true },
  ],

  filters: {
    status: ["brouillon", "soumis", "validé", "rejeté", "annulé"],
    entreprise: {
      enabled: true,
      type: "select",
      source: "references.entreprises",
    },
    type: {
      enabled: true,
      type: "select",
      source: "references.types_besoin",
    },
  },

  relatedActions: [
    {
      label: "Créer une mission",
      to: (id: string) => `/admin/missions?fromBesoin=${id}`,
      permission: "missions.create",
    },
    {
      label: "Voir la mission liée",
      to: (id: string) => `/admin/missions?besoin=${id}`,
      permission: "missions.read.own",
    }
  ],

  pagination: {
    pageSize: 20,
    serverSide: true,
  },
}
