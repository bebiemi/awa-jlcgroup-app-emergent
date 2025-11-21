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
   *   TITRE ⟶ affiché dans le header
   *  ------------------------------ */
  title: "Gestion des Entreprises",
  subtitle: "Gérez toutes les entreprises inscrites sur la plateforme",

  /** ------------------------------
   *  APIs génériques du template
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
   *   (utilisées par EntityListTemplate)
   *  ------------------------------ */
  permissions: {
    view: "entreprises.read.all",
    create: "company.create",
    edit: "company.edit",
    delete: "company.delete",
  },

  /** ------------------------------
   *   Colonnes du tableau
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
   *   Modales Actions
   *  ------------------------------ */
  actions: {
    create: CreateEntrepriseModal,
    // edit: EditEntrepriseModal, // À créer si besoin
    // delete: DeleteEntrepriseModal, // À créer si besoin
  },

  /** ------------------------------
   *   Filtres
   *  ------------------------------ */
  filters: {
    status: ["active", "inactive", "pending"],
  },
}
