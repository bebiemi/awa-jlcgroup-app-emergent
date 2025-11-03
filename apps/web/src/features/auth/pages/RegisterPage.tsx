import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useRegisterMutation } from '../api/authApi'
import LocationSelector from '@/components/LocationSelector'
import toast from 'react-hot-toast'
import { ArrowPathIcon, CheckCircleIcon, XCircleIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

type UserRole = 'interim' | 'company'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [register, { isLoading }] = useRegisterMutation()
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    role: '' as UserRole | '',
    // Interim fields
    phone: '',
    dateOfBirth: '',
    // Company fields
    companyName: '',
    legalRepresentative: '',
    nif: '',
    companyPhone: '',
    // Location fields
    location: {
      country_id: '',
      province_id: '',
      city_id: '',
      district_id: '',
      neighborhood_id: '',
      custom_country: '',
    },
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [passwordMatch, setPasswordMatch] = useState<boolean | null>(null)
  const [captchaVerified, setCaptchaVerified] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  // Real-time password match validation
  useEffect(() => {
    if (formData.password && formData.confirmPassword) {
      setPasswordMatch(formData.password === formData.confirmPassword)
    } else {
      setPasswordMatch(null)
    }
  }, [formData.password, formData.confirmPassword])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'L\'email est requis'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email invalide'
    }

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Le nom complet est requis'
    }

    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Le mot de passe doit contenir au moins 8 caractères'
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas'
    }

    if (!formData.role) {
      newErrors.role = 'Veuillez choisir un type de profil'
    }

    // Role-specific validation
    if (formData.role === 'company') {
      if (!formData.companyName.trim()) {
        newErrors.companyName = 'Le nom de la société est requis'
      }
      if (!formData.legalRepresentative.trim()) {
        newErrors.legalRepresentative = 'Le représentant légal est requis'
      }
      // NIF is now optional - no validation required
    }

    if (!captchaVerified) {
      newErrors.captcha = 'Veuillez vérifier que vous n\'êtes pas un robot'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      const payload: any = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName,
        role: formData.role,
      }

      // Add role-specific fields
      if (formData.role === 'interim') {
        payload.phone = formData.phone
        payload.date_of_birth = formData.dateOfBirth
      } else if (formData.role === 'company') {
        payload.company_name = formData.companyName
        payload.legal_representative = formData.legalRepresentative
        payload.nif = formData.nif
        payload.phone = formData.companyPhone
      }

      // Add location data
      payload.location = formData.location

      await register(payload).unwrap()

      toast.success('Inscription réussie ! Vérifiez votre email pour activer votre compte.')
      navigate('/login')
    } catch (error: any) {
      console.error('Registration error:', error)
      toast.error(error.data?.detail || 'Échec de l\'inscription')
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const handleRoleSelect = (role: UserRole) => {
    setFormData((prev) => ({ ...prev, role }))
    if (errors.role) {
      setErrors((prev) => ({ ...prev, role: '' }))
    }
  }

  // Simple Captcha verification (can be replaced with Google reCAPTCHA)
  const handleCaptchaVerify = () => {
    setCaptchaVerified(true)
    setErrors((prev) => ({ ...prev, captcha: '' }))
    toast.success('Captcha vérifié !')
  }

  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 0, label: '', color: '' }
    
    let strength = 0
    if (password.length >= 8) strength += 25
    if (password.length >= 12) strength += 25
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25
    if (/\d/.test(password)) strength += 15
    if (/[^a-zA-Z0-9]/.test(password)) strength += 10
    
    if (strength < 40) return { strength, label: 'Faible', color: 'bg-red-500' }
    if (strength < 70) return { strength, label: 'Moyen', color: 'bg-yellow-500' }
    return { strength, label: 'Fort', color: 'bg-green-500' }
  }

  const passwordStrength = getPasswordStrength(formData.password)

  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4 py-6">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-2xl overflow-hidden my-4">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 p-6 text-white">
          <div className="flex items-center justify-between mb-3">
            <Link 
              to="/" 
              className="flex items-center text-white hover:text-purple-200 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Retour à l'accueil
            </Link>
          </div>
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-2">
              Rejoignez JLC GROUP ⭐
            </h1>
            <p className="text-purple-100 text-sm">
              Créez votre compte en quelques étapes
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Progress indicator - More compact */}
          <div className="flex justify-between items-center mb-3">
            <div className={`flex items-center ${formData.role ? 'text-jlc-purple-600' : 'text-gray-400'}`}>
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm ${formData.role ? 'bg-jlc-purple-600 text-white' : 'bg-gray-200'}`}>
                1
              </div>
              <span className="ml-2 text-xs font-medium hidden sm:inline">Type de profil</span>
            </div>
            <div className="flex-1 h-1 mx-2 bg-gray-200">
              <div className={`h-full ${formData.role ? 'bg-jlc-purple-600' : 'bg-gray-200'} transition-all`} style={{ width: formData.role ? '100%' : '0%' }}></div>
            </div>
            <div className={`flex items-center ${formData.username && formData.email ? 'text-jlc-purple-600' : 'text-gray-400'}`}>
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm ${formData.username && formData.email ? 'bg-jlc-purple-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="ml-2 text-xs font-medium hidden sm:inline">Informations</span>
            </div>
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Étape 1 : Choisissez votre profil *
            </label>
            <div className="grid grid-cols-2 gap-3">
              {/* Interim Role */}
              <button
                type="button"
                onClick={() => handleRoleSelect('interim')}
                className={`relative p-4 border-2 rounded-xl transition-all transform hover:scale-105 ${
                  formData.role === 'interim'
                    ? 'border-jlc-purple-600 bg-jlc-purple-50 shadow-lg'
                    : 'border-gray-300 hover:border-jlc-purple-400 bg-white'
                }`}
              >
                {formData.role === 'interim' && (
                  <CheckCircleIcon className="absolute top-2 right-2 h-5 w-5 text-jlc-purple-600" />
                )}
                <div className="text-center">
                  <div className="text-4xl mb-2">👤</div>
                  <div className="font-bold text-gray-900">Intérimaire</div>
                  <div className="text-xs text-gray-500 mt-1">
                    Je recherche des missions
                  </div>
                </div>
              </button>

              {/* Company Role */}
              <button
                type="button"
                onClick={() => handleRoleSelect('company')}
                className={`relative p-4 border-2 rounded-xl transition-all transform hover:scale-105 ${
                  formData.role === 'company'
                    ? 'border-jlc-purple-600 bg-jlc-purple-50 shadow-lg'
                    : 'border-gray-300 hover:border-jlc-purple-400 bg-white'
                }`}
              >
                {formData.role === 'company' && (
                  <CheckCircleIcon className="absolute top-2 right-2 h-5 w-5 text-jlc-purple-600" />
                )}
                <div className="text-center">
                  <div className="text-4xl mb-2">🏢</div>
                  <div className="font-bold text-gray-900">Société</div>
                  <div className="text-xs text-gray-500 mt-1">
                    Je propose des missions
                  </div>
                </div>
              </button>
            </div>
            {errors.role && (
              <p className="text-red-500 text-sm mt-2 flex items-center">
                <XCircleIcon className="h-4 w-4 mr-1" />
                {errors.role}
              </p>
            )}
          </div>

          {/* Common Fields */}
          {formData.role && (
            <>
              <div className="border-t pt-4">
                <h3 className="text-base font-semibold text-gray-900 mb-3">
                  Étape 2 : Informations de connexion
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Username */}
                  <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                      Nom d'utilisateur *
                    </label>
                    <input
                      type="text"
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                        errors.username ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="johndoe"
                    />
                    {errors.username && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <XCircleIcon className="h-4 w-4 mr-1" />
                        {errors.username}
                      </p>
                    )}
                  </div>

                  {/* Full Name */}
                  <div>
                    <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
                      Nom complet *
                    </label>
                    <input
                      type="text"
                      id="fullName"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                        errors.fullName ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder="John Doe"
                    />
                    {errors.fullName && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <XCircleIcon className="h-4 w-4 mr-1" />
                        {errors.fullName}
                      </p>
                    )}
                  </div>
                </div>

                {/* Email */}
                <div className="mt-6">
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                      errors.email ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="john@example.com"
                  />
                  {errors.email && (
                    <p className="text-red-500 text-sm mt-1 flex items-center">
                      <XCircleIcon className="h-4 w-4 mr-1" />
                      {errors.email}
                    </p>
                  )}
                </div>

                {/* Password with strength indicator */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                      Mot de passe *
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                          errors.password ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="••••••••"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword ? '🙈' : '👁️'}
                      </button>
                    </div>
                    {formData.password && (
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="text-gray-600">Force du mot de passe</span>
                          <span className={`font-medium ${
                            passwordStrength.strength < 40 ? 'text-red-600' :
                            passwordStrength.strength < 70 ? 'text-yellow-600' : 'text-green-600'
                          }`}>
                            {passwordStrength.label}
                          </span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all ${passwordStrength.color}`}
                            style={{ width: `${passwordStrength.strength}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                    {errors.password && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <XCircleIcon className="h-4 w-4 mr-1" />
                        {errors.password}
                      </p>
                    )}
                  </div>

                  {/* Confirm Password with real-time validation */}
                  <div>
                    <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                      Confirmer le mot de passe *
                    </label>
                    <div className="relative">
                      <input
                        type={showPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                          passwordMatch === false ? 'border-red-500' : 
                          passwordMatch === true ? 'border-green-500' : 'border-gray-300'
                        }`}
                        placeholder="••••••••"
                      />
                      {passwordMatch !== null && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          {passwordMatch ? (
                            <CheckCircleIcon className="h-5 w-5 text-green-500" />
                          ) : (
                            <XCircleIcon className="h-5 w-5 text-red-500" />
                          )}
                        </div>
                      )}
                    </div>
                    {passwordMatch === false && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <XCircleIcon className="h-4 w-4 mr-1" />
                        Les mots de passe ne correspondent pas
                      </p>
                    )}
                    {passwordMatch === true && (
                      <p className="text-green-500 text-sm mt-1 flex items-center">
                        <CheckCircleIcon className="h-4 w-4 mr-1" />
                        Les mots de passe correspondent
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Role-specific fields */}
              {formData.role === 'interim' && (
                <div className="border-t pt-6">
                  <h3 className="text-base font-semibold text-gray-900 mb-3">
                    Informations personnelles (Intérimaire)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                        Téléphone
                      </label>
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                        placeholder="+241 01 23 45 67"
                      />
                    </div>
                    <div>
                      <label htmlFor="dateOfBirth" className="block text-sm font-medium text-gray-700 mb-1">
                        Date de naissance
                      </label>
                      <input
                        type="date"
                        id="dateOfBirth"
                        name="dateOfBirth"
                        value={formData.dateOfBirth}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                      />
                    </div>
                  </div>
                </div>
              )}

              {formData.role === 'company' && (
                <div className="border-t pt-6">
                  <h3 className="text-base font-semibold text-gray-900 mb-3">
                    Informations entreprise (Société)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">
                        Nom de la société *
                      </label>
                      <input
                        type="text"
                        id="companyName"
                        name="companyName"
                        value={formData.companyName}
                        onChange={handleInputChange}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                          errors.companyName ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="ABC SARL"
                      />
                      {errors.companyName && (
                        <p className="text-red-500 text-sm mt-1">{errors.companyName}</p>
                      )}
                    </div>
                    <div>
                      <label htmlFor="legalRepresentative" className="block text-sm font-medium text-gray-700 mb-1">
                        Représentant légal *
                      </label>
                      <input
                        type="text"
                        id="legalRepresentative"
                        name="legalRepresentative"
                        value={formData.legalRepresentative}
                        onChange={handleInputChange}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                          errors.legalRepresentative ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Jean Dupont"
                      />
                      {errors.legalRepresentative && (
                        <p className="text-red-500 text-sm mt-1">{errors.legalRepresentative}</p>
                      )}
                    </div>
                    <div>
                      <label htmlFor="nif" className="block text-sm font-medium text-gray-700 mb-1">
                        NIF *
                      </label>
                      <input
                        type="text"
                        id="nif"
                        name="nif"
                        value={formData.nif}
                        onChange={handleInputChange}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition ${
                          errors.nif ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="123456789"
                      />
                      {errors.nif && (
                        <p className="text-red-500 text-sm mt-1">{errors.nif}</p>
                      )}
                    </div>
                    <div>
                      <label htmlFor="companyPhone" className="block text-sm font-medium text-gray-700 mb-1">
                        Téléphone de contact *
                      </label>
                      <input
                        type="tel"
                        id="companyPhone"
                        name="companyPhone"
                        value={formData.companyPhone}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 focus:border-transparent transition"
                        placeholder="+241 01 23 45 67"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Location Section */}
              <div className="border-t pt-6">
                <h3 className="text-base font-semibold text-gray-900 mb-3">Localisation</h3>
                <LocationSelector
                  value={formData.location}
                  onChange={(location) => setFormData({ ...formData, location })}
                  showCustomCountry={true}
                />
              </div>

              {/* Captcha Section */}
              <div className="border-t pt-6">
                <div className={`p-6 border-2 rounded-xl ${captchaVerified ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-gray-50'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <ShieldCheckIcon className={`h-8 w-8 ${captchaVerified ? 'text-green-600' : 'text-gray-400'}`} />
                      <div className="ml-4">
                        <p className="font-medium text-gray-900">
                          {captchaVerified ? 'Vérification réussie !' : 'Vérification anti-robot'}
                        </p>
                        <p className="text-sm text-gray-600">
                          {captchaVerified ? 'Vous êtes humain ✓' : 'Cliquez pour vérifier'}
                        </p>
                      </div>
                    </div>
                    {!captchaVerified && (
                      <button
                        type="button"
                        onClick={handleCaptchaVerify}
                        className="bg-jlc-purple-600 text-white px-6 py-2 rounded-lg hover:bg-jlc-purple-700 transition"
                      >
                        Je ne suis pas un robot
                      </button>
                    )}
                    {captchaVerified && (
                      <CheckCircleIcon className="h-8 w-8 text-green-600" />
                    )}
                  </div>
                </div>
                {errors.captcha && (
                  <p className="text-red-500 text-sm mt-2 flex items-center">
                    <XCircleIcon className="h-4 w-4 mr-1" />
                    {errors.captcha}
                  </p>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading || !captchaVerified}
                className="w-full bg-gradient-to-r from-jlc-purple-600 to-jlc-purple-800 text-white py-4 rounded-xl hover:from-jlc-purple-700 hover:to-jlc-purple-900 transition-all font-semibold text-base disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="w-6 h-6 mr-2 animate-spin" />
                    Inscription en cours...
                  </>
                ) : (
                  "Créer mon compte"
                )}
              </button>
            </>
          )}
        </form>

        {/* Login Link */}
        <div className="px-8 pb-8 text-center border-t pt-6">
          <p className="text-sm text-gray-600">
            Vous avez déjà un compte ?{' '}
            <Link
              to="/login"
              className="text-jlc-purple-600 hover:text-jlc-purple-700 font-semibold"
            >
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
