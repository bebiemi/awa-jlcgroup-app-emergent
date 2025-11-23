/**
 * Page Missions - Version stable, alignée avec Entreprises/Users
 * Architecture Config-Driven (EntityListTemplate)
 */

import { EyeIcon, PencilIcon, ArchiveBoxIcon, XCircleIcon, TrashIcon } from "@heroicons/react/24/outline"
import EntityListTemplate from "@/templates/EntityListTemplate"
import { usePermissions } from "@/hooks/usePermission"
import { MissionsPageConfig } from "../config/missions.config"
import type { EntityListConfig } from "@/templates/EntityListTemplate"
import type { Mission } from "../api/missionApi"
import { useNavigate } from "react-router-dom"
import { useState } from "react"
import toast from "react-hot-toast"

export default function MissionsPage() {
  const navigate = useNavigate()
  const { permissions: userPermissions } = usePermissions([
    "missions.read.all",
    "missions.create",
    "missions.edit",
    "missions.delete",
    "missions.archive",
    "missions.cancel",
  ])

  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("")

  const { data: missionsData, isLoading } = MissionsPageConfig.api.list({
    status: statusFilter || undefined,
    // Note: L'API missions utilise skip/limit au lieu de page/page_size
    skip: (page - 1) * 20,
    limit: 20,
  })

  // Actions rapides
  const handleView = (mission: Mission) =>
    navigate(`/admin/missions/${mission.id}`)

  const handleEdit = (mission: Mission) =>
    navigate(`/admin/missions/${mission.id}/edit`)

  const handleArchive = (mission: Mission) => {
    toast.success("Archivage à implémenter")
  }

  const handleCancel = (mission: Mission) => {
    toast.error("Annulation à implémenter")
  }

  const handleDelete = (mission: Mission) => {
    if (window.confirm(`Supprimer la mission "${mission.title}" ?`)) {
      toast.error("Suppression à implémenter")
    }
  }

  // Mapping colonnes
  const renderColumns = MissionsPageConfig.columns.map((col) => ({
    ...col,
    render:
      col.key === "start_date" || col.key === "end_date"
        ? (date: string) => (date ? new Date(date).toLocaleDateString("fr-FR") : "-")
        : undefined,
  }))

  // Template Config
  const templateConfig: EntityListConfig = {
    entityName: "Mission",
    entityNamePlural: "Missions",
    title: MissionsPageConfig.title,
    subtitle: MissionsPageConfig.subtitle,
    icon: EyeIcon,

    columns: renderColumns,
    data: missionsData || [],
    isLoading,

    // Note: L'API missions ne retourne pas de pagination, on désactive pour l'instant
    pagination: undefined,

    onSearch: setSearchQuery,
    searchPlaceholder: "Rechercher une mission...",

    filters: [
      {
        key: "status",
        label: "Par statut",
        type: "select",
        options: [
          { value: "", label: "Tous" },
          { value: "ouverte", label: "Ouverte" },
          { value: "en_cours", label: "En cours" },
          { value: "en_pause", label: "En pause" },
          { value: "terminee", label: "Terminée" },
          { value: "annulee", label: "Annulée" },
        ],
      },
    ],

    actions: {
      create: {
        label: "Créer une mission",
        onClick: () => navigate("/admin/missions/new"),
        permission: "missions.create",
      },
      row: [
        {
          key: "view",
          label: "Voir",
          icon: EyeIcon,
          onClick: handleView,
        },
        {
          key: "edit",
          label: "Modifier",
          icon: PencilIcon,
          onClick: handleEdit,
          permission: "missions.edit",
        },
        {
          key: "archive",
          label: "Archiver",
          icon: ArchiveBoxIcon,
          onClick: handleArchive,
          permission: "missions.archive",
        },
        {
          key: "cancel",
          label: "Annuler",
          icon: XCircleIcon,
          variant: "danger" as const,
          onClick: handleCancel,
          permission: "missions.cancel",
        },
        {
          key: "delete",
          label: "Supprimer",
          icon: TrashIcon,
          variant: "danger" as const,
          onClick: handleDelete,
          permission: "missions.delete",
        },
      ],
    },

    emptyState: {
      message: "Aucune mission trouvée",
      action: {
        label: "Créer une mission",
        onClick: () => navigate("/admin/missions/new"),
      },
    },
  }

  return <EntityListTemplate config={templateConfig} permissions={userPermissions} />
}
