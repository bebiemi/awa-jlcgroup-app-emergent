import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useRegisterMutation } from '../api/authApi'
import { useLazyVerifyEmailDomainQuery } from '@/features/admin/api/emailDomainsApi'
import { useGetFormFieldsQuery } from '@/features/company/api/entrepriseFormConfigApi'
import DynamicFormField from '@/features/company/components/DynamicFormField'
import LocationSelector from '@/components/LocationSelector'
import PhoneInput from '@/components/PhoneInput'
import toast from 'react-hot-toast'
import { ArrowPathIcon, CheckCircleIcon, XCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'
import { ValidationTypes } from '@/constants/iamConstants'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [register, { isLoading }] = useRegisterMutation()
  const [verifyEmail, { data: emailVerification }] = useLazyVerifyEmailDomainQuery()
  
  // Charger les champs dynamiques pour les entreprises
  const { data: formConfig, isLoading: isLoadingFields } = useGetFormFieldsQuery({ is_active: true })
  
  const [accountType, setAccountType] = useState<'candidat' | 'company' | ''>('')
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    phone: '',
    dateOfBirth: '',
    // Company fields
    companyName: '',
    legalRepresentative: '',
    nif: '',
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
  
  // État pour les champs dynamiques d'entreprise
  const [dynamicCompanyData, setDynamicCompanyData] = useState<Record<string, any>>({})

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [passwordMatch, setPasswordMatch] = useState<boolean | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [emailDebounce, setEmailDebounce] = useState<NodeJS.Timeout | null>(null)

  // Real-time password match validation
  useEffect(() => {
    if (formData.password && formData.confirmPassword) {
      setPasswordMatch(formData.password === formData.confirmPassword)
    } else {
      setPasswordMatch(null)
    }
  }, [formData.password, formData.confirmPassword])

  // Real-time email validation with debounce
  useEffect(() => {
    if (emailDebounce) {
      clearTimeout(emailDebounce)
    }

    if (formData.email && /\S+@\S+\.\S+/.test(formData.email)) {
      const timeout = setTimeout(() => {
        verifyEmail(formData.email)
      }, 500)
      setEmailDebounce(timeout)
    }

    return () => {
      if (emailDebounce) {
        clearTimeout(emailDebounce)
      }
    }
  }, [formData.email])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!accountType) {
      newErrors.accountType = 'Veuillez choisir un type de compte'
    }

    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'L\'email utilisateur est requis'
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

    // Company-specific validation avec champs dynamiques
    if (accountType === 'company' && formConfig?.fields) {
      // Valider les champs obligatoires définis dans la configuration
      formConfig.fields.forEach((field) => {
        if (field.validation.required && field.visible_for_roles.includes('public')) {
          const value = dynamicCompanyData[field.field_key]
          if (!value || (typeof value === 'string' && !value.trim())) {
            newErrors[field.field_key] = field.validation.custom_error_message || `${field.field_label} est requis`
          }
          
          // Validation de longueur
          if (value && typeof value === 'string') {
            if (field.validation.min_length && value.length < field.validation.min_length) {
              newErrors[field.field_key] = `${field.field_label} doit contenir au moins ${field.validation.min_length} caractères`
            }
            if (field.validation.max_length && value.length > field.validation.max_length) {
              newErrors[field.field_key] = `${field.field_label} ne doit pas dépasser ${field.validation.max_length} caractères`
            }
          }
          
          // Validation de pattern
          if (value && typeof value === 'string' && field.validation.pattern) {
            const regex = new RegExp(field.validation.pattern)
            if (!regex.test(value)) {
              newErrors[field.field_key] = field.validation.custom_error_message || `Format de ${field.field_label} invalide`
            }
          }
        }
      })
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error('Veuillez corriger les erreurs du formulaire')
      return
    }

    try {
      const payload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName,
        phone: formData.phone || undefined,
        date_of_birth: formData.dateOfBirth || undefined,
        company_name: formData.companyName || undefined,
        legal_representative: formData.legalRepresentative || undefined,
        nif: formData.nif || undefined,
        location: Object.values(formData.location).some(v => v) ? formData.location : undefined,
      }

      const result = await register(payload).unwrap()
      
      // Success - redirect to login with message
      if (accountType === 'company') {
        toast.success('Inscription réussie !\nVotre espace entreprise a été créé. Votre compte sera activé après validation par l\'équipe JLC.', { duration: 5000 })
        navigate('/login', { 
          state: { 
            email: formData.email,
            message: 'Votre espace entreprise a été créé. Votre compte sera activé après validation par l\'équipe JLC.'
          }
        })
      } else if (emailVerification?.is_collaborator) {
        toast.success('Inscription réussie !\nVotre compte collaborateur a été créé. Il sera activé après validation par un administrateur.', { duration: 5000 })
        navigate('/login', { 
          state: { 
            email: formData.email,
            message: 'Votre compte collaborateur a été créé. Il sera activé après validation par un administrateur.'
          }
        })
      } else {
        toast.success('Inscription réussie !\nVotre compte candidat a été créé avec succès. Vous pouvez maintenant vous connecter.', { duration: 5000 })
        navigate('/login', { 
          state: { 
            email: formData.email,
            username: formData.username,
            message: 'Votre compte candidat a été créé avec succès. Vous pouvez maintenant vous connecter.'
          }
        })
      }
    } catch (error: any) {
      console.error('Registration error:', error)
      toast.error(error?.data?.detail || 'Erreur lors de l\'inscription')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-jlc-purple-50 to-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo & Header */}
        <div>
          <div className="flex justify-center">
            <img
              className="h-16 w-auto"
              src="/logo-jlc.png"
              alt="JLC Group"
            />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Créer un compte
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Choisissez votre type de compte
          </p>
        </div>

        {/* Account Type Selection */}
        {!accountType ? (
          <div className="space-y-4">
            <button
              onClick={() => setAccountType(ValidationTypes.CANDIDAT as 'candidat')}
              className="w-full p-6 border-2 border-gray-200 rounded-lg hover:border-jlc-purple-500 hover:bg-jlc-purple-50 transition-all text-left group"
            >
              <div className="flex items-start gap-4">
                <div className="text-4xl">👤</div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-jlc-purple-700">
                    Candidat
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Je cherche des missions d'intérim (devient intérimaire après signature du contrat)
                  </p>
                </div>
              </div>
            </button>

            <button
              onClick={() => setAccountType(ValidationTypes.COMPANY as 'company')}
              className="w-full p-6 border-2 border-gray-200 rounded-lg hover:border-jlc-purple-500 hover:bg-jlc-purple-50 transition-all text-left group"
            >
              <div className="flex items-start gap-4">
                <div className="text-4xl">🏢</div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 group-hover:text-jlc-purple-700">
                    Entreprise
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Je cherche à recruter des intérimaires
                  </p>
                </div>
              </div>
            </button>

            <div className="text-center pt-4">
              <p className="text-sm text-gray-600">
                Vous avez déjà un compte ?{' '}
                <Link
                  to="/login"
                  className="font-medium text-jlc-purple-600 hover:text-jlc-purple-500"
                >
                  Se connecter
                </Link>
              </p>
            </div>
          </div>
        ) : (
          /* Registration Form */
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {/* Back button */}
            <button
              type="button"
              onClick={() => setAccountType('')}
              className="text-sm text-jlc-purple-600 hover:text-jlc-purple-700 flex items-center gap-1"
            >
              ← Changer de type de compte
            </button>

            <div className="rounded-md shadow-sm space-y-4">
              {/* Company-specific fields */}
              {accountType === 'company' && (
                <>
                  <div>
                    <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">
                      Nom de l'entreprise *
                    </label>
                    <input
                      id="companyName"
                      name="companyName"
                      type="text"
                      required
                      value={formData.companyName}
                      onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
                      className={`appearance-none relative block w-full px-3 py-2 border ${
                        errors.companyName ? 'border-red-300' : 'border-gray-300'
                      } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 sm:text-sm`}
                      placeholder="Nom de votre entreprise"
                    />
                    {errors.companyName && (
                      <p className="mt-1 text-sm text-red-600">{errors.companyName}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="legalRepresentative" className="block text-sm font-medium text-gray-700 mb-1">
                      Représentant légal *
                    </label>
                    <input
                      id="legalRepresentative"
                      name="legalRepresentative"
                      type="text"
                      required
                      value={formData.legalRepresentative}
                      onChange={(e) => setFormData({ ...formData, legalRepresentative: e.target.value })}
                      className={`appearance-none relative block w-full px-3 py-2 border ${
                        errors.legalRepresentative ? 'border-red-300' : 'border-gray-300'
                      } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 sm:text-sm`}
                      placeholder="Nom du représentant"
                    />
                    {errors.legalRepresentative && (
                      <p className="mt-1 text-sm text-red-600">{errors.legalRepresentative}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="nif" className="block text-sm font-medium text-gray-700 mb-1">
                      NIF (optionnel)
                    </label>
                    <input
                      id="nif"
                      name="nif"
                      type="text"
                      value={formData.nif}
                      onChange={(e) => setFormData({ ...formData, nif: e.target.value })}
                      className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 sm:text-sm"
                      placeholder="Numéro d'identification fiscale"
                    />
                  </div>
                </>
              )}
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                Nom d'utilisateur *
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className={`appearance-none relative block w-full px-3 py-2 border ${
                  errors.username ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 focus:z-10 sm:text-sm`}
                placeholder="johndoe"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username}</p>
              )}
            </div>

            {/* Email with real-time verification */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={`appearance-none relative block w-full px-3 py-2 border ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 focus:z-10 sm:text-sm`}
                placeholder="vous@exemple.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
              
              {/* Email verification feedback */}
              {emailVerification && formData.email && !errors.email && (
                <div className={`mt-2 p-3 rounded-lg flex items-start gap-2 ${
                  emailVerification.is_collaborator 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'bg-green-50 border border-green-200'
                }`}>
                  <InformationCircleIcon className={`h-5 w-5 mt-0.5 ${
                    emailVerification.is_collaborator ? 'text-blue-600' : 'text-green-600'
                  }`} />
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${
                      emailVerification.is_collaborator ? 'text-blue-800' : 'text-green-800'
                    }`}>
                      {emailVerification.message}
                    </p>
                    {emailVerification.is_collaborator && (
                      <p className="text-xs text-blue-600 mt-1">
                        Votre compte nécessitera une validation manuelle par un administrateur.
                      </p>
                    )}
                    {!emailVerification.is_collaborator && (
                      <p className="text-xs text-green-600 mt-1">
                        Votre compte candidat sera activé immédiatement après inscription.
                      </p>
                    )}
                  </div>
                </div>
              )}

              <p className="mt-1 text-xs text-gray-500">
                Les adresses professionnelles JLC Group (@jlcgroup.*) nécessitent une validation
              </p>
            </div>

            {/* Full Name */}
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
                Nom complet *
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                required
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                className={`appearance-none relative block w-full px-3 py-2 border ${
                  errors.fullName ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 focus:z-10 sm:text-sm`}
                placeholder="Jean Dupont"
              />
              {errors.fullName && (
                <p className="mt-1 text-sm text-red-600">{errors.fullName}</p>
              )}
            </div>

            {/* Phone (optional) */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                Téléphone (optionnel)
              </label>
              <PhoneInput
                value={formData.phone}
                onChange={(value) => setFormData({ ...formData, phone: value })}
                placeholder="+241 XX XX XX XX"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe *
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className={`appearance-none relative block w-full px-3 py-2 border ${
                    errors.password ? 'border-red-300' : 'border-gray-300'
                  } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 focus:z-10 sm:text-sm`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-sm text-gray-600 hover:text-gray-900"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Minimum 8 caractères
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmer le mot de passe *
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className={`appearance-none relative block w-full px-3 py-2 border ${
                    errors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                  } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-jlc-purple-500 focus:border-jlc-purple-500 focus:z-10 sm:text-sm pr-10`}
                  placeholder="••••••••"
                />
                {passwordMatch !== null && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    {passwordMatch ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircleIcon className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                )}
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
              )}
            </div>
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-jlc-purple-600 hover:bg-jlc-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-jlc-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <>
                    <ArrowPathIcon className="animate-spin h-5 w-5 mr-2" />
                    Inscription en cours...
                  </>
                ) : (
                  "S'inscrire"
                )}
              </button>
            </div>

            {/* Login Link */}
            <div className="text-center">
              <p className="text-sm text-gray-600">
                Vous avez déjà un compte ?{' '}
                <Link
                  to="/login"
                  className="font-medium text-jlc-purple-600 hover:text-jlc-purple-500"
                >
                  Se connecter
                </Link>
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
