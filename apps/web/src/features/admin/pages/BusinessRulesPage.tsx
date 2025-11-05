import { useState } from 'react'
import Layout from '@/components/Layout'
import Card from '@/components/Card'
import Modal from '@/components/Modal'
import { PlusIcon, PencilIcon, TrashIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'

interface BusinessRule {
  id: string
  name: string
  description?: string
  rule_type: string
  conditions: Record<string, any>
  actions: Record<string, any>
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

const RULE_TYPES = [
  { value: 'validation', label: 'Validation', color: 'bg-blue-100 text-blue-800' },
  { value: 'notification', label: 'Notification', color: 'bg-green-100 text-green-800' },
  { value: 'workflow', label: 'Workflow', color: 'bg-purple-100 text-purple-800' },
  { value: 'automation', label: 'Automation', color: 'bg-orange-100 text-orange-800' },
]

export default function BusinessRulesPage() {
  const [selectedType, setSelectedType] = useState<string>('all')
  const [showModal, setShowModal] = useState(false)
  const [editingRule, setEditingRule] = useState<BusinessRule | null>(null)
  
  // Mock data - À remplacer par l'API RTK Query
  const [rules, setRules] = useState<BusinessRule[]>([
    {
      id: '1',
      name: 'Auto-validation email domaines de confiance',
      description: 'Validation automatique pour les domaines email de confiance',
      rule_type: 'validation',
      conditions: { domains: ['gmail.com', 'awana-group.com'] },
      actions: { set_status: 'active', skip_validation: true },
      priority: 10,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      name: 'Notification candidat présélectionné',
      description: 'Envoyer email quand candidat présélectionné',
      rule_type: 'notification',
      conditions: { status_change: 'shortlisted' },
      actions: { send_email: true, template: 'shortlisted_notification' },
      priority: 5,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ])

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rule_type: 'validation',
    conditions: '{}',
    actions: '{}',
    priority: 0,
    is_active: true,
  })

  const filteredRules = selectedType === 'all' 
    ? rules 
    : rules.filter(rule => rule.rule_type === selectedType)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      // Valider JSON
      const conditions = JSON.parse(formData.conditions)
      const actions = JSON.parse(formData.actions)
      
      if (editingRule) {
        // Update
        setRules(rules.map(rule => 
          rule.id === editingRule.id 
            ? { ...rule, ...formData, conditions, actions, updated_at: new Date().toISOString() }
            : rule
        ))
      } else {
        // Create
        const newRule: BusinessRule = {
          id: Date.now().toString(),
          ...formData,
          conditions,
          actions,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        setRules([...rules, newRule])
      }
      
      setShowModal(false)
      resetForm()
    } catch (error) {
      alert('Format JSON invalide dans conditions ou actions')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      rule_type: 'validation',
      conditions: '{}',
      actions: '{}',
      priority: 0,
      is_active: true,
    })
    setEditingRule(null)
  }

  const handleEdit = (rule: BusinessRule) => {
    setEditingRule(rule)
    setFormData({
      name: rule.name,
      description: rule.description || '',
      rule_type: rule.rule_type,
      conditions: JSON.stringify(rule.conditions, null, 2),
      actions: JSON.stringify(rule.actions, null, 2),
      priority: rule.priority,
      is_active: rule.is_active,
    })
    setShowModal(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette règle ?')) {
      setRules(rules.filter(rule => rule.id !== id))
    }
  }

  const toggleActive = (id: string) => {
    setRules(rules.map(rule => 
      rule.id === id ? { ...rule, is_active: !rule.is_active } : rule
    ))
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Règles Métier
            </h1>
            <p className="text-gray-600">
              Gérez les règles automatiques de l'application
            </p>
          </div>
          <button
            onClick={() => {
              resetForm()
              setShowModal(true)
            }}
            className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
          >
            <PlusIcon className="h-5 w-5" />
            Nouvelle règle
          </button>
        </div>

        {/* Filtres par type */}
        <Card>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedType === 'all'
                  ? 'bg-jlc-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Toutes ({rules.length})
            </button>
            {RULE_TYPES.map((type) => (
              <button
                key={type.value}
                onClick={() => setSelectedType(type.value)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  selectedType === type.value
                    ? 'bg-jlc-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type.label} ({rules.filter(r => r.rule_type === type.value).length})
              </button>
            ))}
          </div>
        </Card>

        {/* Liste des règles */}
        <div className="space-y-4">
          {filteredRules.length === 0 ? (
            <Card>
              <div className="text-center py-8 text-gray-500">
                Aucune règle dans cette catégorie
              </div>
            </Card>
          ) : (
            filteredRules.map((rule) => {
              const typeInfo = RULE_TYPES.find(t => t.value === rule.rule_type)
              return (
                <Card key={rule.id}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {rule.name}
                        </h3>
                        <span className={`px-2 py-1 text-xs rounded-full ${typeInfo?.color}`}>
                          {typeInfo?.label}
                        </span>
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          Priorité: {rule.priority}
                        </span>
                      </div>
                      
                      {rule.description && (
                        <p className="text-gray-600 mb-3">{rule.description}</p>
                      )}

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="font-medium text-gray-700 mb-1">Conditions:</p>
                          <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                            {JSON.stringify(rule.conditions, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <p className="font-medium text-gray-700 mb-1">Actions:</p>
                          <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                            {JSON.stringify(rule.actions, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 ml-4">
                      <button
                        onClick={() => toggleActive(rule.id)}
                        className={`flex items-center px-3 py-2 text-sm rounded-lg transition ${
                          rule.is_active
                            ? 'bg-green-100 text-green-700 hover:bg-green-200'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {rule.is_active ? (
                          <>
                            <CheckCircleIcon className="h-4 w-4 mr-1" />
                            Actif
                          </>
                        ) : (
                          <>
                            <XCircleIcon className="h-4 w-4 mr-1" />
                            Inactif
                          </>
                        )}
                      </button>
                      
                      <button
                        onClick={() => handleEdit(rule)}
                        className="flex items-center px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
                        title="Modifier"
                      >
                        <PencilIcon className="h-4 w-4 mr-1" />
                        Modifier
                      </button>

                      <button
                        onClick={() => handleDelete(rule.id)}
                        className="flex items-center px-3 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                        title="Supprimer"
                      >
                        <TrashIcon className="h-4 w-4 mr-1" />
                        Supprimer
                      </button>
                    </div>
                  </div>
                </Card>
              )
            })
          )}
        </div>
      </div>

      {/* Modal Création/Édition */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          resetForm()
        }}
        title={editingRule ? 'Modifier la règle' : 'Nouvelle règle'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Nom de la règle *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Type de règle *
            </label>
            <select
              value={formData.rule_type}
              onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
              required
            >
              {RULE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Conditions (JSON) *
            </label>
            <textarea
              value={formData.conditions}
              onChange={(e) => setFormData({ ...formData, conditions: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500 font-mono text-sm"
              rows={4}
              placeholder='{"key": "value"}'
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Format JSON valide requis
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Actions (JSON) *
            </label>
            <textarea
              value={formData.actions}
              onChange={(e) => setFormData({ ...formData, actions: e.target.value })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500 font-mono text-sm"
              rows={4}
              placeholder='{"action": "value"}'
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Format JSON valide requis
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Priorité
            </label>
            <input
              type="number"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-jlc-purple-500 focus:ring-jlc-purple-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              Plus la priorité est élevée, plus la règle s'exécute en premier
            </p>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 text-jlc-purple-600 rounded focus:ring-jlc-purple-500"
            />
            <label className="ml-2 block text-sm text-gray-900">
              Règle active
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => {
                setShowModal(false)
                resetForm()
              }}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700"
            >
              {editingRule ? 'Modifier' : 'Créer'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  )
}
