/**
 * Page Missions – Version propre et 100% config-driven
 * Utilise NeedListTemplate pour workflow avancé
 */

import { useState, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import NeedListTemplate from "@/templates/NeedListTemplate"
import EntityListTemplate from "@/templates/EntityListTemplate"
import { usePermissions } from "@/hooks/usePermission"
import { MissionsPageConfig } from "../config/missions.config"
import type { Mission } from "../api/missionApi"
import toast from "react-hot-toast"

export default function MissionsPage() {
  const navigate = useNavigate()

  /** 👉 Permissions */
  const { permissions: userPermissions } = usePermissions([
    "missions.read.all",
    "missions.create",
    "missions.edit",
    "missions.delete",
  ])

  /** 👉 Local UI state */
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [page, setPage] = useState(1)

  /** 👉 API list */
  const { data, isLoading } = MissionsPageConfig.api.list({
    status: statusFilter || undefined,
    page,
    page_size: 20,
    search: searchQuery || undefined,
  })

  /** 👉 Actions centralisées */
  const actions = useMemo(
    () => ({
      create: () => navigate("/admin/missions/new"),

      view: (m: Mission) => navigate(`/admin/missions/${m.id}`),

      edit: (m: Mission) => navigate(`/admin/missions/${m.id}/edit`),

      delete: (m: Mission) => {
        if (window.confirm(`Supprimer la mission "${m.titre}" ?`)) {
          toast.error("Suppression à implémenter dans missionApi")
        }
      },
    }),
    [navigate]
  )

  /** 👉 Colonnes enrichies */
  const columns = useMemo(
    () =>
      MissionsPageConfig.columns.map((col) => ({
        ...col,
        render:
          col.key === "status"
            ? (status: string) => {
                const map = {
                  ouverte: "bg-blue-100 text-blue-700",
                  en_cours: "bg-green-100 text-green-700",
                  en_pause: "bg-yellow-100 text-yellow-700",
                  terminée: "bg-gray-100 text-gray-700",
                  annulée: "bg-red-100 text-red-700",
                }
                return (
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      map[status] ?? map.ouverte
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </span>
                )
              }
            : col.key.includes("date")
            ? (value: string) =>
                value ? new Date(value).toLocaleDateString("fr-FR") : "-"
            : undefined,
      })),
    []
  )

  /** 👉 Template config */
  const templateConfig = {
    entityName: "Mission",
    entityNamePlural: "Missions",
    title: MissionsPageConfig.title,
    subtitle: MissionsPageConfig.subtitle,

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
    searchPlaceholder: "Rechercher par titre, entreprise, intérimaire…",

    filters: [
      {
        key: "status",
        label: "Statut",
        type: "select",
        options: [
          { value: "", label: "Tous" },
          { value: "ouverte", label: "Ouverte" },
          { value: "en_cours", label: "En cours" },
          { value: "en_pause", label: "En pause" },
          { value: "terminée", label: "Terminée" },
          { value: "annulée", label: "Annulée" },
        ],
      },
    ],

    actions: {
      create: {
        label: "Créer une mission",
        onClick: actions.create,
        permission: "missions.create",
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
          permission: "missions.edit",
        },
        {
          key: "delete",
          label: "Supprimer",
          onClick: actions.delete,
          permission: "missions.delete",
        },
      ],
    },

    emptyState: {
      message: "Aucune mission pour le moment",
      action: {
        label: "Créer une mission",
        onClick: actions.create,
      },
    },
  }

  /** 👉 Utilisation d'EntityListTemplate (plus cohérent avec l'architecture) */
  return <EntityListTemplate config={templateConfig} permissions={userPermissions} />
}
