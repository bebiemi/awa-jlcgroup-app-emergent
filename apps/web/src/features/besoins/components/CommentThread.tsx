import { useState } from 'react'
import { useGetCommentsQuery, useAddCommentMutation, CommentResponse } from '../api/besoinApi'
import { PaperAirplaneIcon, UserCircleIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

interface CommentThreadProps {
  besoinId: string
}

export default function CommentThread({ besoinId }: CommentThreadProps) {
  const [newComment, setNewComment] = useState('')
  const { data: comments = [], isLoading } = useGetCommentsQuery(besoinId)
  const [addComment, { isLoading: adding }] = useAddCommentMutation()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim()) return

    try {
      await addComment({ besoinId, content: newComment }).unwrap()
      setNewComment('')
      toast.success('Commentaire ajouté')
    } catch (error: any) {
      toast.error(error?.data?.detail || 'Erreur lors de l\'ajout du commentaire')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60)
      return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`
    } else if (diffInHours < 24) {
      const hours = Math.floor(diffInHours)
      return `il y a ${hours} heure${hours > 1 ? 's' : ''}`
    } else if (diffInHours < 48) {
      return 'hier'
    } else {
      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      })
    }
  }

  const getAuthorBadge = (authorType: 'entreprise' | 'jlc') => {
    if (authorType === 'jlc') {
      return (
        <span className="px-2 py-0.5 bg-jlc-purple-100 text-jlc-purple-700 text-xs font-medium rounded">
          JLC
        </span>
      )
    }
    return (
      <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded">
        Entreprise
      </span>
    )
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/4" />
                <div className="h-16 bg-gray-200 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Comments List */}
      {comments.length > 0 ? (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {comments.map((comment: CommentResponse) => (
            <div key={comment.id} className="flex gap-3">
              <div className="flex-shrink-0">
                <UserCircleIcon className="h-10 w-10 text-gray-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-gray-900">{comment.author_name}</span>
                  {getAuthorBadge(comment.author_type)}
                  <span className="text-xs text-gray-500">{formatDate(comment.created_at)}</span>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <p className="text-gray-700 text-sm whitespace-pre-wrap">{comment.content}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <ChatBubbleLeftRightIcon className="h-12 w-12 mx-auto mb-2 text-gray-400" />
          <p>Aucun commentaire pour le moment</p>
          <p className="text-sm mt-1">Soyez le premier à commenter</p>
        </div>
      )}

      {/* Add Comment Form */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 pt-4">
        <div className="flex gap-3">
          <div className="flex-shrink-0">
            <UserCircleIcon className="h-10 w-10 text-gray-400" />
          </div>
          <div className="flex-1">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Écrivez un commentaire..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent resize-none text-sm"
              disabled={adding}
            />
            <div className="flex justify-end mt-2">
              <button
                type="submit"
                disabled={!newComment.trim() || adding}
                className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                <PaperAirplaneIcon className="h-4 w-4" />
                {adding ? 'Envoi...' : 'Envoyer'}
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  )
}
