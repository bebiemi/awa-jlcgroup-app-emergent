import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'
import {
  useGetTicketQuery,
  useListMessagesQuery,
  useAddMessageMutation,
  useCloseTicketMutation,
} from '../api/supportApi'
import { ArrowLeftIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

const STATUS_LABELS: Record<string, string> = {
  open: 'Ouvert',
  in_progress: 'En cours',
  waiting_user: 'En attente de votre réponse',
  resolved: 'Résolu',
  closed: 'Fermé',
}

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  waiting_user: 'bg-orange-100 text-orange-800',
  resolved: 'bg-green-100 text-green-800',
  closed: 'bg-gray-100 text-gray-800',
}

const CATEGORY_LABELS: Record<string, string> = {
  technical: 'Technique',
  commercial: 'Commercial',
  hr: 'Ressources Humaines',
  general: 'Général',
  bug: 'Bug',
  feature: 'Nouvelle fonctionnalité',
}

const PRIORITY_LABELS: Record<string, string> = {
  low: 'Basse',
  medium: 'Moyenne',
  high: 'Haute',
  urgent: 'Urgente',
}

export default function TicketDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: ticket, isLoading: ticketLoading } = useGetTicketQuery(id!)
  const { data: messages = [], isLoading: messagesLoading } = useListMessagesQuery(id!)
  const [addMessage, { isLoading: sendingMessage }] = useAddMessageMutation()
  const [closeTicket, { isLoading: closingTicket }] = useCloseTicketMutation()

  const [newMessage, setNewMessage] = useState('')

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newMessage.trim()) {
      toast.error('Le message ne peut pas être vide')
      return
    }

    try {
      await addMessage({
        ticket_id: id!,
        data: { message: newMessage },
      }).unwrap()

      setNewMessage('')
      toast.success('Message envoyé')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'envoi du message')
    }
  }

  const handleCloseTicket = async () => {
    if (!confirm('Êtes-vous sûr de vouloir fermer ce ticket ?')) {
      return
    }

    try {
      await closeTicket(id!).unwrap()
      toast.success('Ticket fermé')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de la fermeture du ticket')
    }
  }

  if (ticketLoading || messagesLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    )
  }

  if (!ticket) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600">Ticket non trouvé</p>
        </div>
      </Layout>
    )
  }

  const isClosed = ticket.status === 'closed'

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/support/tickets')}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Retour
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{ticket.subject}</h1>
              <p className="text-gray-600 text-sm mt-1">
                Ticket #{ticket.id.slice(0, 8)} • Créé le{' '}
                {new Date(ticket.created_at).toLocaleString('fr-FR')}
              </p>
            </div>
          </div>

          {!isClosed && (
            <button
              onClick={handleCloseTicket}
              disabled={closingTicket}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {closingTicket ? 'Fermeture...' : 'Fermer le ticket'}
            </button>
          )}
        </div>

        {/* Ticket Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Statut</label>
              <span
                className={`mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[ticket.status]}`}
              >
                {STATUS_LABELS[ticket.status] || ticket.status}
              </span>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Catégorie</label>
              <p className="text-sm text-gray-900 mt-1">
                {CATEGORY_LABELS[ticket.category] || ticket.category}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Priorité</label>
              <p className="text-sm text-gray-900 mt-1">
                {PRIORITY_LABELS[ticket.priority] || ticket.priority}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Messages</label>
              <p className="text-sm text-gray-900 mt-1">{ticket.message_count}</p>
            </div>
          </div>

          {ticket.assigned_to_name && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <label className="text-sm font-medium text-gray-500">Assigné à</label>
              <p className="text-sm text-gray-900 mt-1">{ticket.assigned_to_name}</p>
            </div>
          )}

          {isClosed && ticket.closed_at && (
            <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-700">
                ✓ Ticket fermé le {new Date(ticket.closed_at).toLocaleString('fr-FR')}
              </p>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Conversation</h2>
          </div>

          <div className="p-6 space-y-4 max-h-[500px] overflow-y-auto">
            {messages.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Aucun message</p>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.user_id === ticket.user_id ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-4 ${
                      message.user_id === ticket.user_id
                        ? 'bg-jlc-purple-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium opacity-90">
                        {message.user_name || message.user_email}
                      </span>
                      <span className="text-xs opacity-75 ml-2">
                        {new Date(message.created_at).toLocaleString('fr-FR')}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.message}</p>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Reply Form */}
          {!isClosed && (
            <div className="p-6 border-t border-gray-200">
              <form onSubmit={handleSendMessage} className="flex gap-3">
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  rows={3}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent resize-none"
                  placeholder="Tapez votre message..."
                  disabled={sendingMessage}
                />
                <button
                  type="submit"
                  disabled={sendingMessage || !newMessage.trim()}
                  className="px-6 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  <PaperAirplaneIcon className="h-5 w-5" />
                  {sendingMessage ? 'Envoi...' : 'Envoyer'}
                </button>
              </form>
            </div>
          )}

          {isClosed && (
            <div className="p-6 border-t border-gray-200">
              <p className="text-center text-gray-500">
                Ce ticket est fermé. Vous ne pouvez plus envoyer de messages.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
