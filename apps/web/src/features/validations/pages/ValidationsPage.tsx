/**
 * Page Validations – Clean, moderne, 100% config-driven
 * Centralise les approbations : candidats, entreprises, missions, etc.
 */

import { useState } from "react"
import EntityListTemplate from "@/templates/EntityListTemplate"
import { usePermissions } from "@/hooks/usePermission"
import { ValidationsPageConfig } from "../config/validations.config"
import type { Validation } from "../api/validationsApi"

export default function ValidationsPage() {
  const { permissions: userPermissions } = usePermissions([
    "validations.read.all",
    "validations.approve",
    "validations.reject",
  ])

  const [statusFilter, setStatusFilter] = useState("")
  const [typeFilter, setTypeFilter] = useState("")
  const [page, setPage] = useState(1)

  const { data, isLoading } = ValidationsPageConfig.api.list({
    status: statusFilter || undefined,
    type: typeFilter || undefined,
    page,
    page_size: 20,
  })

  const actions = {
    approve: (v: Validation) =>
      ValidationsPageConfig.api
        .approve({ id: v.id })
        .unwrap()
        .then(() => window.location.reload()),

    reject: (v: Validation) =>
      ValidationsPageConfig.api
        .reject({ id: v.id })
        .unwrap()
        .then(() => window.location.reload()),
  }

  const templateConfig = {
    entityName: "Validation",
    entityNamePlural: "Validations",

    title: ValidationsPageConfig.title,
    subtitle: ValidationsPageConfig.subtitle,

    columns: ValidationsPageConfig.columns,

    data: data?.items || [],
    isLoading,

    pagination: data
      ? {
          currentPage: data.page,
          totalPages: data.total_pages,
          onPageChange: setPage,
        }
      : undefined,

    filters: [
      {
        key: "status",
        type: "select",
        label: "Statut",
        onChange: setStatusFilter,
        options: [
          { value: "", label: "Tous" },
          { value: "en_attente", label: "En attente" },
          { value: "validé", label: "Validé" },
          { value: "rejeté", label: "Rejeté" },
        ],
      },
      {
        key: "type",
        type: "select",
        label: "Type",
        onChange: setTypeFilter,
        options: [
          { value: "", label: "Tous" },
          { value: "entreprise", label: "Entreprise" },
          { value: "candidat", label: "Candidat" },
          { value: "mission", label: "Mission" },
          { value: "collaborateur", label: "Collaborateur" },
          { value: "avertissement", label: "Avertissement" },
        ],
      },
    ],

    actions: {
      row: [
        {
          key: "approve",
          label: "Valider",
          permission: "validations.approve",
          onClick: actions.approve,
          show: (v: Validation) => v.status === "en_attente",
        },
        {
          key: "reject",
          label: "Rejeter",
          permission: "validations.reject",
          variant: "danger" as const,
          onClick: actions.reject,
          show: (v: Validation) => v.status === "en_attente",
        },
      ],
    },

    emptyState: {
      message: "Aucune validation en attente",
    },
  }

  return (
    <EntityListTemplate config={templateConfig} permissions={userPermissions} />
  )
}
