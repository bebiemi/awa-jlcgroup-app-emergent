export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-jlc-purple-600 via-jlc-purple-700 to-jlc-purple-800 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-2xl p-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-6">
          Inscription
        </h2>
        <p className="text-center text-gray-600">
          La création de compte sera disponible bientôt.
        </p>
        <div className="mt-6">
          <a
            href="/login"
            className="block w-full text-center px-4 py-2 bg-jlc-purple-600 text-white rounded-md hover:bg-jlc-purple-700 transition-colors"
          >
            Retour à la connexion
          </a>
        </div>
      </div>
    </div>
  )
}
