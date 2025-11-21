/**
 * Page Besoins – Version améliorée, clean et 100% config-driven
 * Préfusée pour migration NeedListTemplate
 */

import { useState, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import EntityListTemplate from "@/templates/EntityListTemplate"
import { usePermissions } from "@/hooks/usePermission"
import { BesoinsPageConfig } from "../config/besoins.config"
import type { Besoin } from "../api/besoinsApi"
import toast from "react-hot-toast"

export default function BesoinsPage() {
  const navigate = useNavigate()

  /** 👉 Permissions */
  const { permissions: userPermissions } = usePermissions([
    "besoins.read.all",
    "besoins.create",
    "besoins.edit",
    "besoins.delete",
    "besoins.validate",
  ])

  /** 👉 Local UI state (recherche + filtre + pagination) */
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [page, setPage] = useState(1)

  /** 👉 API list */
  const { data, isLoading } = BesoinsPageConfig.api.list({
    status: statusFilter || undefined,
    page,
    page_size: 20,
    search: searchQuery || undefined,
  })

  /** 👉 Actions centralisées (navigation + workflows) */
  const actions = useMemo(
    () => ({
      create: () => navigate("/admin/besoins/new"),

      view: (b: Besoin) => navigate(`/admin/besoins/${b.id}`),

      edit: (b: Besoin) => navigate(`/admin/besoins/${b.id}/edit`),

      validate: (b: Besoin) =>
        toast.success(
          `Validation en attente de modale – besoin: ${b.titre}`
        ),

      reject: (b: Besoin) =>
        toast.error(`Rejet en attente de modale – besoin: ${b.titre}`),

      delete: (b: Besoin) => {
        if (window.confirm(`Supprimer le besoin "${b.titre}" ?`)) {
          toast.error("Suppression à implémenter dans besoinsApi")
        }
      },
    }),
    [navigate]
  )

  /** 👉 Colonnes enrichies (badges, dates, etc.) */
  const columns = useMemo(
    () =>
      BesoinsPageConfig.columns.map((col) => ({
        ...col,
        render:
          col.key === "status"
            ? (status: string) => {
                const map = {
                  brouillon: "bg-gray-100 text-gray-700",
                  soumis: "bg-blue-100 text-blue-700",
                  validé: "bg-green-100 text-green-700",
                  rejeté: "bg-red-100 text-red-700",
                  annulé: "bg-gray-200 text-gray-600",
                }
                return (
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      map[status] ?? map.brouillon
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </span>
                )
              }
            : col.key.includes("date")
            ? (value: string) =>
                value
                  ? new Date(value).toLocaleDateString("fr-FR")
                  : "-"
            : undefined,
      })),
    []
  )

  /** 👉 Template config unifiée */
  const templateConfig = {
    entityName: "Besoin",
    entityNamePlural: "Besoins",
    title: BesoinsPageConfig.title,
    subtitle: BesoinsPageConfig.subtitle,

    columns,
    data: data?.items || [],
    isLoading,

    pagination: data
      ? {
          currentPage: data.page,
          totalPages: data.total_pages,
          onPageChange: setPage,
        }
      : undefined,

    onSearch: setSearchQuery,
    searchPlaceholder: "Rechercher par titre, entreprise…",

    filters: [
      {
        key: "status",
        label: "Statut",
        type: "select",
        options: [
          { value: "", label: "Tous" },
          { value: "brouillon", label: "Brouillon" },
          { value: "soumis", label: "Soumis" },
          { value: "validé", label: "Validé" },
          { value: "rejeté", label: "Rejeté" },
          { value: "annulé", label: "Annulé" },
        ],
      },
    ],

    actions: {
      create: {
        label: "Créer un besoin",
        onClick: actions.create,
        permission: "besoins.create",
      },

      row: [
        {
          key: "view",
          label: "Voir",
          onClick: actions.view,
        },
        {
          key: "edit",
          label: "Modifier",
          onClick: actions.edit,
          permission: "besoins.edit",
        },
        {
          key: "validate",
          label: "Valider",
          show: (b: Besoin) => b.status === "soumis",
          onClick: actions.validate,
          permission: "besoins.validate",
        },
        {
          key: "reject",
          label: "Rejeter",
          show: (b: Besoin) => b.status === "soumis",
          onClick: actions.reject,
          permission: "besoins.validate",
        },
        {
          key: "delete",
          label: "Supprimer",
          onClick: actions.delete,
          permission: "besoins.delete",
        },
      ],
    },

    emptyState: {
      message: "Aucun besoin pour le moment",
      action: {
        label: "Créer un besoin",
        onClick: actions.create,
      },
    },
  }

  /** 👉 Utilisation d'EntityListTemplate (plus cohérent avec l'architecture) */
  return <EntityListTemplate config={templateConfig} permissions={userPermissions} />
}
