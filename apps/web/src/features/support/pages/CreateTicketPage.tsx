import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import { useCreateTicketMutation } from '../api/supportApi'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

export default function CreateTicketPage() {
  const navigate = useNavigate()
  const [createTicket, { isLoading }] = useCreateTicketMutation()

  const [formData, setFormData] = useState({
    subject: '',
    message: '',
    category: 'general',
    priority: 'medium',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    const newErrors: Record<string, string> = {}
    if (formData.subject.length < 5) {
      newErrors.subject = 'Le sujet doit contenir au moins 5 caractères'
    }
    if (formData.message.length < 10) {
      newErrors.message = 'Le message doit contenir au moins 10 caractères'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      const ticket = await createTicket(formData).unwrap()
      toast.success('Ticket créé avec succès')
      navigate(`/support/tickets/${ticket.id}`)
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la création du ticket')
    }
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/support/tickets')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Retour
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Nouveau Ticket Support</h1>
            <p className="text-gray-600 text-sm mt-1">
              Décrivez votre problème ou votre demande
            </p>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catégorie *
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
                required
              >
                <option value="general">Général</option>
                <option value="technical">Technique</option>
                <option value="commercial">Commercial</option>
                <option value="hr">Ressources Humaines</option>
                <option value="bug">Signaler un bug</option>
                <option value="feature">Demande de fonctionnalité</option>
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Priorité</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent"
              >
                <option value="low">Basse</option>
                <option value="medium">Moyenne</option>
                <option value="high">Haute</option>
                <option value="urgent">Urgente</option>
              </select>
              <p className="mt-1 text-sm text-gray-500">
                Sélectionnez "Urgente" uniquement pour les problèmes critiques
              </p>
            </div>

            {/* Subject */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sujet *</label>
              <input
                type="text"
                value={formData.subject}
                onChange={(e) => {
                  setFormData({ ...formData, subject: e.target.value })
                  if (errors.subject) setErrors({ ...errors, subject: '' })
                }}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                  errors.subject ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Ex: Problème de connexion à mon compte"
                required
                minLength={5}
                maxLength={200}
              />
              {errors.subject && <p className="mt-1 text-sm text-red-600">{errors.subject}</p>}
              <p className="mt-1 text-sm text-gray-500">
                {formData.subject.length}/200 caractères (minimum 5)
              </p>
            </div>

            {/* Message */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description détaillée *
              </label>
              <textarea
                value={formData.message}
                onChange={(e) => {
                  setFormData({ ...formData, message: e.target.value })
                  if (errors.message) setErrors({ ...errors, message: '' })
                }}
                rows={8}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent ${
                  errors.message ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Décrivez en détail votre problème ou votre demande..."
                required
                minLength={10}
                maxLength={5000}
              />
              {errors.message && <p className="mt-1 text-sm text-red-600">{errors.message}</p>}
              <p className="mt-1 text-sm text-gray-500">
                {formData.message.length}/5000 caractères (minimum 10)
              </p>
            </div>

            {/* Info Box */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="text-sm font-medium text-blue-900 mb-2">
                💡 Pour une réponse plus rapide
              </h4>
              <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
                <li>Soyez aussi précis que possible dans votre description</li>
                <li>Incluez les messages d'erreur si applicable</li>
                <li>Mentionnez les étapes pour reproduire le problème</li>
                <li>Indiquez votre navigateur et système d'exploitation si technique</li>
              </ul>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => navigate('/support/tickets')}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Création...' : 'Créer le ticket'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  )
}
