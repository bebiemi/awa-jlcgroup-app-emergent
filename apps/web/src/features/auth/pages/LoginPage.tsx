import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLocalLoginMutation } from '../api/authApi'
import toast from 'react-hot-toast'
import Button from '@/components/Button'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [login, { isLoading }] = useLocalLoginMutation()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await login({ username, password }).unwrap()
      toast.success('Connexion réussie!')
      navigate('/')
    } catch (error: any) {
      console.error('Login error:', error)
      toast.error(error?.data?.detail || 'Identifiants incorrects')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo */}
        <div className="text-center">
          <div className="text-white font-bold text-5xl flex items-center justify-center mb-2">
            <span className="bg-gradient-to-r from-purple-300 to-blue-200 bg-clip-text text-transparent">
              JLC
            </span>
            <span className="ml-3 text-jlc-accent-light text-3xl">GROUP</span>
            <span className="ml-2 text-jlc-accent-yellow text-4xl">★</span>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-white">
            Connexion
          </h2>
          <p className="mt-2 text-sm text-purple-200">
            Plateforme de Gestion d'Intérim
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Nom d'utilisateur
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                placeholder="admin"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Mot de passe
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                placeholder="••••••••"
              />
            </div>

            <div>
              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                className="w-full"
              >
                Se connecter
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Ou</span>
              </div>
            </div>

            <div className="mt-6">
              <button
                type="button"
                className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                disabled
              >
                <span className="mr-2">🔒</span>
                Se connecter avec Google (bientôt)
              </button>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Identifiants par défaut: <span className="font-mono bg-gray-100 px-2 py-1 rounded">admin</span> / <span className="font-mono bg-gray-100 px-2 py-1 rounded">awana2025</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
