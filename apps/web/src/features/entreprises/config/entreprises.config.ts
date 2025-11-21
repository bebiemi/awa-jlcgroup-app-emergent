/**
 * Configuration de la page de gestion des entreprises
 * Architecture Config-Driven - Zéro duplication
 */

import {
  useListEntreprisesQuery,
  useGetEntrepriseQuery,
  useCreateEntrepriseMutation,
  useUpdateEntrepriseMutation,
  useDeleteEntrepriseMutation,
} from '../api/entreprisesApi'

import CreateEntrepriseModal from '../components/CreateEntrepriseModal'

export const EntreprisesPageConfig = {
  /** ------------------------------
   *   TITRE
   *  ------------------------------ */
  title: "Gestion des Entreprises",
  subtitle: "Gérez toutes les entreprises inscrites sur la plateforme",

  /** ------------------------------
   *  APIs génériques
   *  ------------------------------ */
  api: {
    list: useListEntreprisesQuery,
    get: useGetEntrepriseQuery,
    create: useCreateEntrepriseMutation,
    update: useUpdateEntrepriseMutation,
    delete: useDeleteEntrepriseMutation,
  },

  /** ------------------------------
   *   Permissions IAM
   *  ------------------------------ */
  permissions: {
    view: "entreprises.read.all",
    create: "company.create",
    edit: "company.edit",
    delete: "company.delete",
    related: {
      needs: "besoins.read.own",
      missions: "missions.read.own",
      validation: "entreprises.validate",
      documents: "documents.read.own",
    }
  },

  /** ------------------------------
   *   Colonnes
   *  ------------------------------ */
  columns: [
    { key: "nom", label: "Entreprise", sortable: true },
    { key: "email", label: "Contact", sortable: false },
    { key: "ville", label: "Localisation", sortable: true },
    { key: "secteur_activite", label: "Secteur", sortable: true },
    { key: "effectif", label: "Effectif", sortable: false },
    { key: "status", label: "Statut", badge: true },
  ],

  /** ------------------------------
   *   Modales & Actions
   *  ------------------------------ */
  actions: {
    create: CreateEntrepriseModal,
  },

  /** ------------------------------
   *   Filtres enrichis
   *  ------------------------------ */
  filters: {
    status: ["active", "inactive", "pending", "blocked"],
    localisation: {
      enabled: true,
      type: "select",
      source: "references.countries", // récupéré via config API (pas de hardcode)
    },
    secteur: {
      enabled: true,
      type: "select",
      source: "references.secteurs",
    },
    date_creation: {
      enabled: true,
      type: "daterange",
    },
  },

  /** ------------------------------
   *   Actions transverses (multi-modules)
   *  ------------------------------ */
  relatedActions: [
    {
      label: "Voir les besoins",
      to: (id: string) => `/admin/besoins?entreprise=${id}`,
      permission: "besoins.read.own",
    },
    {
      label: "Voir les missions",
      to: (id: string) => `/admin/missions?entreprise=${id}`,
      permission: "missions.read.own",
    },
    {
      label: "Valider cette entreprise",
      to: (id: string) => `/admin/validations/entreprise/${id}`,
      permission: "entreprises.validate",
    },
    {
      label: "Documents de l'entreprise",
      to: (id: string) => `/admin/documents?entreprise=${id}`,
      permission: "documents.read.own",
    }
  ],

  /** ------------------------------
   *   Pagination
   *  ------------------------------ */
  pagination: {
    pageSize: 20,
    serverSide: true,
  },
}
