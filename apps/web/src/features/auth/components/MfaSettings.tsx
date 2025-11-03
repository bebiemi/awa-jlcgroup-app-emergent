import { useState } from 'react'
import {
  useGetMfaStatusQuery,
  useSetupTotpMutation,
  useVerifyTotpMutation,
  useSetupEmailOtpMutation,
  useDisableMfaMethodMutation,
  useGetBackupCodesQuery,
  useGenerateBackupCodesMutation,
} from '../api/mfaApi'
import toast from 'react-hot-toast'
import {
  ShieldCheckIcon,
  QrCodeIcon,
  EnvelopeIcon,
  KeyIcon,
  XMarkIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  DocumentDuplicateIcon,
} from '@heroicons/react/24/outline'

export default function MfaSettings() {
  const { data: mfaStatus, isLoading: statusLoading, refetch: refetchStatus } = useGetMfaStatusQuery()
  const [setupTotp] = useSetupTotpMutation()
  const [verifyTotp] = useVerifyTotpMutation()
  const [setupEmailOtp] = useSetupEmailOtpMutation()
  const [disableMfaMethod] = useDisableMfaMethodMutation()
  const [generateBackupCodes] = useGenerateBackupCodesMutation()

  const [showTotpSetup, setShowTotpSetup] = useState(false)
  const [showEmailSetup, setShowEmailSetup] = useState(false)
  const [showDisableConfirm, setShowDisableConfirm] = useState(false)
  const [showRecoveryCodes, setShowRecoveryCodes] = useState(false)

  const [qrCode, setQrCode] = useState('')
  const [manualKey, setManualKey] = useState('')
  const [totpSecret, setTotpSecret] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [disablePassword, setDisablePassword] = useState('')
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([])

  const [setupLoading, setSetupLoading] = useState(false)

  // Handle TOTP Setup
  const handleStartTotpSetup = async () => {
    setSetupLoading(true)
    try {
      const result = await setupTotp().unwrap()
      setQrCode(result.qr_code)
      setManualKey(result.manual_entry_key)
      setTotpSecret(result.secret)
      setShowTotpSetup(true)
      toast.success('Scannez le code QR avec votre application d\'authentification')
    } catch (error: any) {
      console.error('TOTP setup error:', error)
      toast.error(error?.data?.detail || 'Erreur lors de la configuration TOTP')
    } finally {
      setSetupLoading(false)
    }
  }

  const handleVerifyAndEnableTotp = async () => {
    if (!verificationCode.trim()) {
      toast.error('Veuillez entrer le code de vérification')
      return
    }

    setSetupLoading(true)
    try {
      // Verify TOTP (this also enables MFA automatically in the backend)
      await verifyTotp({ code: verificationCode }).unwrap()

      toast.success('TOTP activé avec succès!')

      // Get backup codes
      const codesResult = await generateBackupCodes({ password: '' }).unwrap()
      setRecoveryCodes(codesResult.codes || [])
      setShowRecoveryCodes(true)
      setShowTotpSetup(false)
      setVerificationCode('')

      refetchStatus()
    } catch (error: any) {
      console.error('TOTP verification error:', error)
      toast.error(error?.data?.detail || 'Code invalide')
    } finally {
      setSetupLoading(false)
    }
  }

  // Handle Email OTP Setup
  const handleStartEmailSetup = async () => {
    setSetupLoading(true)
    try {
      const result = await setupEmailOtp().unwrap()

      toast.success(`Email OTP activé pour ${result.email}`)

      // Get backup codes
      const codesResult = await generateBackupCodes({ password: '' }).unwrap()
      setRecoveryCodes(codesResult.codes || [])
      setShowRecoveryCodes(true)

      refetchStatus()
    } catch (error: any) {
      console.error('Email OTP setup error:', error)
      toast.error(error?.data?.detail || 'Erreur lors de la configuration Email OTP')
    } finally {
      setSetupLoading(false)
    }
  }

  // Handle Disable MFA
  const handleDisableMfa = async () => {
    if (!disablePassword.trim()) {
      toast.error('Veuillez entrer votre mot de passe')
      return
    }

    if (!mfaStatus?.method) {
      toast.error('Aucune méthode MFA active')
      return
    }

    setSetupLoading(true)
    try {
      await disableMfaMethod({ method: mfaStatus.method, password: disablePassword }).unwrap()
      toast.success('MFA désactivé')
      setShowDisableConfirm(false)
      setDisablePassword('')
      refetchStatus()
    } catch (error: any) {
      console.error('Disable MFA error:', error)
      toast.error(error?.data?.detail || 'Mot de passe incorrect')
    } finally {
      setSetupLoading(false)
    }
  }

  // Copy to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copié dans le presse-papier')
  }

  const downloadRecoveryCodes = () => {
    const text = recoveryCodes.join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'jlc-recovery-codes.txt'
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Codes téléchargés')
  }

  if (statusLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-jlc-purple-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* MFA Status Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <div className={`p-3 rounded-lg ${mfaStatus?.enabled ? 'bg-green-100' : 'bg-gray-100'}`}>
              <ShieldCheckIcon className={`h-8 w-8 ${mfaStatus?.enabled ? 'text-green-600' : 'text-gray-400'}`} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Authentification à Deux Facteurs (MFA)
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {mfaStatus?.enabled
                  ? `Activé avec ${mfaStatus.method === 'totp' ? 'Authenticator' : 'Email OTP'}`
                  : 'Non activé - Renforcez la sécurité de votre compte'}
              </p>
              {mfaStatus?.enabled && mfaStatus?.has_recovery_codes && (
                <p className="text-xs text-gray-500 mt-1">
                  {mfaStatus.recovery_codes_count} code(s) de secours disponible(s)
                </p>
              )}
            </div>
          </div>
          <div>
            {mfaStatus?.enabled ? (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Activé
              </span>
            ) : (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                Désactivé
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      {!mfaStatus?.enabled ? (
        <div className="grid md:grid-cols-2 gap-4">
          {/* TOTP Option */}
          <div className="bg-white rounded-lg shadow p-6 border-2 border-transparent hover:border-jlc-purple-200 transition">
            <div className="flex items-center space-x-3 mb-4">
              <QrCodeIcon className="h-8 w-8 text-jlc-purple-600" />
              <h4 className="text-lg font-semibold text-gray-900">Authenticator App</h4>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Utilisez Google Authenticator, Microsoft Authenticator ou une autre application compatible.
            </p>
            <button
              onClick={handleStartTotpSetup}
              disabled={setupLoading}
              className="w-full bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition disabled:opacity-50"
            >
              Configurer TOTP
            </button>
          </div>

          {/* Email OTP Option */}
          <div className="bg-white rounded-lg shadow p-6 border-2 border-transparent hover:border-jlc-purple-200 transition">
            <div className="flex items-center space-x-3 mb-4">
              <EnvelopeIcon className="h-8 w-8 text-jlc-purple-600" />
              <h4 className="text-lg font-semibold text-gray-900">Email OTP</h4>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Recevez un code de vérification par email à chaque connexion.
            </p>
            <button
              onClick={handleStartEmailSetup}
              disabled={setupLoading}
              className="w-full bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition disabled:opacity-50"
            >
              Configurer Email OTP
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <button
            onClick={() => setShowDisableConfirm(true)}
            className="text-red-600 hover:text-red-700 font-medium text-sm"
          >
            Désactiver MFA
          </button>
        </div>
      )}

      {/* TOTP Setup Modal */}
      {showTotpSetup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900">Configuration TOTP</h3>
              <button onClick={() => setShowTotpSetup(false)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              {/* QR Code */}
              <div className="flex justify-center">
                {qrCode && <img src={qrCode} alt="QR Code" className="w-48 h-48" />}
              </div>

              {/* Manual Entry Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clé manuelle (si le QR code ne fonctionne pas)
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={manualKey}
                    readOnly
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(manualKey)}
                    className="p-2 text-gray-600 hover:text-gray-800"
                  >
                    <DocumentDuplicateIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Verification Code */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code de vérification
                </label>
                <input
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500 font-mono text-center text-lg"
                  placeholder="123456"
                  maxLength={6}
                />
              </div>

              {/* Actions */}
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowTotpSetup(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Annuler
                </button>
                <button
                  onClick={handleVerifyAndEnableTotp}
                  disabled={setupLoading || verificationCode.length !== 6}
                  className="flex-1 bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition disabled:opacity-50"
                >
                  {setupLoading ? 'Vérification...' : 'Activer'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Disable MFA Confirm Modal */}
      {showDisableConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900">Désactiver MFA</h3>
              <button onClick={() => setShowDisableConfirm(false)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Entrez votre mot de passe pour confirmer la désactivation de l'authentification à deux facteurs.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Mot de passe</label>
                <input
                  type="password"
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-jlc-purple-500"
                  placeholder="Votre mot de passe"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={() => setShowDisableConfirm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Annuler
                </button>
                <button
                  onClick={handleDisableMfa}
                  disabled={setupLoading || !disablePassword}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition disabled:opacity-50"
                >
                  {setupLoading ? 'Désactivation...' : 'Désactiver'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recovery Codes Modal */}
      {showRecoveryCodes && recoveryCodes.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900">Codes de Secours</h3>
              <button onClick={() => setShowRecoveryCodes(false)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="mb-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-yellow-800">
                  <strong>Important:</strong> Sauvegardez ces codes dans un endroit sûr. Chaque code ne peut être
                  utilisé qu'une seule fois.
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm space-y-2 max-h-60 overflow-y-auto">
                {recoveryCodes.map((code, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span>{code}</span>
                    <button
                      onClick={() => copyToClipboard(code)}
                      className="text-jlc-purple-600 hover:text-jlc-purple-700"
                    >
                      <DocumentDuplicateIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={downloadRecoveryCodes}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Télécharger
              </button>
              <button
                onClick={() => setShowRecoveryCodes(false)}
                className="flex-1 bg-jlc-purple-600 text-white px-4 py-2 rounded-lg hover:bg-jlc-purple-700 transition"
              >
                J'ai sauvegardé
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
