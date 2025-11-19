/**
 * Admin Update Password Modal
 * Permet aux admins/super-admins de modifier le mot de passe d'un utilisateur
 */
import { useState } from 'react'
import Modal from '@/components/Modal'
import Button from '@/components/Button'
import {
  KeyIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Props {
  isOpen: boolean
  onClose: () => void
  userId: string
  username: string
  onSuccess: () => void
}

export default function AdminUpdatePasswordModal({
  isOpen,
  onClose,
  userId,
  username,
  onSuccess,
}: Props) {
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!newPassword) {
      newErrors.newPassword = 'Le nouveau mot de passe est requis'
    } else if (newPassword.length < 8) {
      newErrors.newPassword = 'Le mot de passe doit contenir au moins 8 caractères'
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Veuillez confirmer le mot de passe'
    } else if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch(
        `/api/iam/users/${userId}/password/admin-update`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            new_password: newPassword,
            confirm_password: confirmPassword,
          }),
        }
      )

      if (response.ok) {
        const result = await response.json()
        toast.success(result.message || 'Mot de passe mis à jour avec succès')
        onSuccess()
        handleClose()
      } else {
        const error = await response.json()
        
        if (response.status === 403) {
          toast.error('Vous ne pouvez pas modifier le mot de passe de cet utilisateur')
        } else {
          toast.error(error.detail || 'Erreur lors de la mise à jour du mot de passe')
        }
      }
    } catch (error) {
      console.error('Error updating password:', error)
      toast.error('Erreur de connexion')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    setNewPassword('')
    setConfirmPassword('')
    setShowPassword(false)
    setShowConfirm(false)
    setErrors({})
    onClose()
  }

  const getPasswordStrength = (password: string) => {
    if (password.length === 0) return { strength: 0, label: '', color: '' }
    if (password.length < 8) return { strength: 1, label: 'Faible', color: 'bg-red-500' }
    
    let strength = 1
    if (password.length >= 12) strength++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++

    const levels = [
      { strength: 1, label: 'Faible', color: 'bg-red-500' },
      { strength: 2, label: 'Moyen', color: 'bg-orange-500' },
      { strength: 3, label: 'Bon', color: 'bg-yellow-500' },
      { strength: 4, label: 'Fort', color: 'bg-green-500' },
      { strength: 5, label: 'Très fort', color: 'bg-green-600' },
    ]

    return levels[strength - 1] || levels[0]
  }

  const passwordStrength = getPasswordStrength(newPassword)

  return (
    <Modal isOpen={isOpen} onClose={handleClose}>
      <form onSubmit={handleSubmit} className="p-6">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-jlc-purple-100 rounded-lg">
            <KeyIcon className="h-6 w-6 text-jlc-purple-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">
              Modifier le mot de passe
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Utilisateur : <strong>{username}</strong>
            </p>
          </div>
        </div>

        {/* Warning */}
        <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-yellow-800">
                <strong>Attention :</strong> Cette action modifiera immédiatement le mot de passe de l'utilisateur. 
                L'utilisateur devra utiliser le nouveau mot de passe pour se connecter.
              </p>
            </div>
          </div>
        </div>

        {/* New Password */}
        <div className="mb-4">
          <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-2">
            Nouveau mot de passe *
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className={`w-full px-4 py-3 pr-10 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500 ${
                errors.newPassword ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Entrez le nouveau mot de passe"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          </div>
          {errors.newPassword && (
            <p className="mt-1 text-sm text-red-600">{errors.newPassword}</p>
          )}

          {/* Password Strength Indicator */}
          {newPassword && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>Force du mot de passe</span>
                <span className="font-medium">{passwordStrength.label}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                  style={{ width: `${(passwordStrength.strength / 5) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Confirm Password */}
        <div className="mb-6">
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
            Confirmer le mot de passe *
          </label>
          <div className="relative">
            <input
              type={showConfirm ? 'text' : 'password'}
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className={`w-full px-4 py-3 pr-10 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500 ${
                errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Confirmez le nouveau mot de passe"
            />
            <button
              type="button"
              onClick={() => setShowConfirm(!showConfirm)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {showConfirm ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
          )}
          
          {/* Match indicator */}
          {newPassword && confirmPassword && !errors.confirmPassword && (
            <div className="mt-2 flex items-center text-xs text-green-600">
              <CheckCircleIcon className="h-4 w-4 mr-1" />
              <span>Les mots de passe correspondent</span>
            </div>
          )}
        </div>

        {/* Password requirements */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-xs font-semibold text-gray-700 mb-2">Exigences du mot de passe :</p>
          <ul className="text-xs text-gray-600 space-y-1">
            <li className="flex items-center">
              <span className={`mr-2 ${newPassword.length >= 8 ? 'text-green-600' : 'text-gray-400'}`}>
                {newPassword.length >= 8 ? '✓' : '•'}
              </span>
              Au moins 8 caractères
            </li>
            <li className="flex items-center">
              <span className={`mr-2 ${/[a-z]/.test(newPassword) && /[A-Z]/.test(newPassword) ? 'text-green-600' : 'text-gray-400'}`}>
                {/[a-z]/.test(newPassword) && /[A-Z]/.test(newPassword) ? '✓' : '•'}
              </span>
              Majuscules et minuscules (recommandé)
            </li>
            <li className="flex items-center">
              <span className={`mr-2 ${/\d/.test(newPassword) ? 'text-green-600' : 'text-gray-400'}`}>
                {/\d/.test(newPassword) ? '✓' : '•'}
              </span>
              Au moins un chiffre (recommandé)
            </li>
            <li className="flex items-center">
              <span className={`mr-2 ${/[!@#$%^&*(),.?":{}|<>]/.test(newPassword) ? 'text-green-600' : 'text-gray-400'}`}>
                {/[!@#$%^&*(),.?":{}|<>]/.test(newPassword) ? '✓' : '•'}
              </span>
              Caractères spéciaux (recommandé)
            </li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          <Button
            type="button"
            onClick={handleClose}
            variant="secondary"
            disabled={isSubmitting}
          >
            Annuler
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={isSubmitting || !newPassword || !confirmPassword}
          >
            {isSubmitting ? (
              <>
                <div className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"></div>
                Mise à jour...
              </>
            ) : (
              <>
                <KeyIcon className="h-5 w-5 mr-2" />
                Mettre à jour le mot de passe
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
