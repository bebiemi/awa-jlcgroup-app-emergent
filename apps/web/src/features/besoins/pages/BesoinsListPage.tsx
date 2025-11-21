/**
 * Page Liste des Besoins - Utilise le template réutilisable
 * Détecte automatiquement le contexte (Entreprise vs Commercial) via IAM
 */

import Layout from '@/components/Layout'
import NeedListTemplate from '@/templates/NeedListTemplate'
import { useCurrentContext } from '@/hooks/useNavigationConfig'
import { usePermissions } from '@/hooks/usePermission'

export default function BesoinsListPage() {
  const context = useCurrentContext()
  const { permissions } = usePermissions([
    'besoins.create.own',
    'besoins.create.all',
    'besoins.edit.own',
    'besoins.edit.all',
    'besoins.delete.own',
    'besoins.delete.all',
    'besoins.validate.all',
  ])

  // Déterminer le mode basé sur le contexte
  const mode = context === 'commercial' ? 'commercial' : 'entreprise'

  // Calculer les permissions
  const canCreate = permissions['besoins.create.own'] || permissions['besoins.create.all']
  const canEdit = permissions['besoins.edit.own'] || permissions['besoins.edit.all']
  const canDelete = permissions['besoins.delete.own'] || permissions['besoins.delete.all']
  const canValidate = permissions['besoins.validate.all']

  return (
    <Layout>
      <NeedListTemplate
        mode={mode}
        canCreate={canCreate}
        canEdit={canEdit}
        canDelete={canDelete}
        canValidate={canValidate}
      />
    </Layout>
  )
}
