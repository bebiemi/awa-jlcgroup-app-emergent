import React, { useState, useEffect } from 'react';
import {
  useGetEmailSettingsQuery,
  useUpdateEmailSettingsMutation,
  useTestEmailConfigMutation,
  EMAIL_PROVIDERS,
  PROVIDER_PRESETS,
  type EmailConfigUpdate,
  type EmailTestRequest,
} from '../api/emailSettingsApi';

export const EmailSettingsPage: React.FC = () => {
  const { data: settings, isLoading, error } = useGetEmailSettingsQuery();
  const [updateSettings, { isLoading: isUpdating }] = useUpdateEmailSettingsMutation();
  const [testConfig, { isLoading: isTesting }] = useTestEmailConfigMutation();

  const [formData, setFormData] = useState<EmailConfigUpdate>({
    enabled: false,
    provider: 'custom',
    smtp_host: '',
    smtp_port: 587,
    smtp_user: '',
    smtp_password: '',
    smtp_use_tls: true,
    from_email: '',
    from_name: 'JLC Application',
    admin_emails: [],
  });

  const [testEmail, setTestEmail] = useState('');
  const [newAdminEmail, setNewAdminEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    if (settings) {
      setFormData({
        enabled: settings.enabled,
        provider: settings.provider,
        smtp_host: settings.smtp_host,
        smtp_port: settings.smtp_port,
        smtp_user: settings.smtp_user,
        smtp_password: '',
        smtp_use_tls: settings.smtp_use_tls,
        from_email: settings.from_email,
        from_name: settings.from_name,
        admin_emails: settings.admin_emails,
      });
    }
  }, [settings]);

  const handleProviderChange = (provider: string) => {
    const preset = PROVIDER_PRESETS[provider] || {};
    setFormData((prev) => ({
      ...prev,
      provider,
      ...preset,
    }));
  };

  const handleAddAdminEmail = () => {
    if (newAdminEmail && !formData.admin_emails.includes(newAdminEmail)) {
      setFormData((prev) => ({
        ...prev,
        admin_emails: [...prev.admin_emails, newAdminEmail],
      }));
      setNewAdminEmail('');
    }
  };

  const handleRemoveAdminEmail = (email: string) => {
    setFormData((prev) => ({
      ...prev,
      admin_emails: prev.admin_emails.filter((e) => e !== email),
    }));
  };

  const handleTestConfig = async () => {
    if (!testEmail) {
      alert('Veuillez entrer un email de test');
      return;
    }

    const testData: EmailTestRequest = {
      smtp_host: formData.smtp_host,
      smtp_port: formData.smtp_port,
      smtp_user: formData.smtp_user,
      smtp_password: formData.smtp_password,
      smtp_use_tls: formData.smtp_use_tls,
      from_email: formData.from_email,
      to_email: testEmail,
    };

    try {
      const result = await testConfig(testData).unwrap();
      setTestResult({ success: true, message: result.message });
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err.data?.detail || 'Erreur lors du test',
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.admin_emails.length === 0) {
      alert('Veuillez ajouter au moins un email admin');
      return;
    }

    try {
      await updateSettings(formData).unwrap();
      alert('Configuration enregistrée avec succès !');
    } catch (err: any) {
      alert(`Erreur: ${err.data?.detail || 'Erreur inconnue'}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  const hasNoConfig = error && (error as any).status === 404;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Configuration Email</h1>
        <p className="text-gray-600 mt-2">
          Configurez les paramètres SMTP pour les notifications email
        </p>
      </div>

      {hasNoConfig && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <p className="text-yellow-700">
            Aucune configuration email trouvée. Créez-en une nouvelle ci-dessous.
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Notifications Email</h2>
              <p className="text-sm text-gray-600">Activer ou désactiver les notifications</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={formData.enabled}
                onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-purple-600 peer-focus:ring-4 peer-focus:ring-purple-300 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
            </label>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fournisseur SMTP
              </label>
              <select
                value={formData.provider}
                onChange={(e) => handleProviderChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {EMAIL_PROVIDERS.map((provider) => (
                  <option key={provider.value} value={provider.value}>
                    {provider.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Port SMTP
              </label>
              <input
                type="number"
                value={formData.smtp_port}
                onChange={(e) => setFormData({ ...formData, smtp_port: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hôte SMTP
              </label>
              <input
                type="text"
                value={formData.smtp_host}
                onChange={(e) => setFormData({ ...formData, smtp_host: e.target.value })}
                placeholder="smtp.gmail.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Utilisateur SMTP
              </label>
              <input
                type="text"
                value={formData.smtp_user}
                onChange={(e) => setFormData({ ...formData, smtp_user: e.target.value })}
                placeholder="your-email@gmail.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe SMTP
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.smtp_password}
                  onChange={(e) => setFormData({ ...formData, smtp_password: e.target.value })}
                  placeholder={settings ? '••••••••' : 'Votre mot de passe'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required={!settings}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2 top-2 text-gray-500"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email expéditeur
              </label>
              <input
                type="email"
                value={formData.from_email}
                onChange={(e) => setFormData({ ...formData, from_email: e.target.value })}
                placeholder="noreply@jlc.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom expéditeur
              </label>
              <input
                type="text"
                value={formData.from_name}
                onChange={(e) => setFormData({ ...formData, from_name: e.target.value })}
                placeholder="JLC Application"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>

            <div className="col-span-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.smtp_use_tls}
                  onChange={(e) => setFormData({ ...formData, smtp_use_tls: e.target.checked })}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">Utiliser TLS</span>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Emails Administrateurs</h2>
          <p className="text-sm text-gray-600 mb-4">
            Ces emails recevront les notifications critiques
          </p>

          <div className="flex gap-2 mb-4">
            <input
              type="email"
              value={newAdminEmail}
              onChange={(e) => setNewAdminEmail(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddAdminEmail())}
              placeholder="admin@jlc.com"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="button"
              onClick={handleAddAdminEmail}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
            >
              Ajouter
            </button>
          </div>

          <div className="space-y-2">
            {formData.admin_emails.map((email) => (
              <div key={email} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                <span className="text-sm text-gray-700">{email}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveAdminEmail(email)}
                  className="text-red-600 hover:text-red-800"
                >
                  ✕
                </button>
              </div>
            ))}
            {formData.admin_emails.length === 0 && (
              <p className="text-sm text-gray-500 italic">Aucun email admin ajouté</p>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Tester la Configuration</h2>
          
          <div className="flex gap-2 mb-4">
            <input
              type="email"
              value={testEmail}
              onChange={(e) => setTestEmail(e.target.value)}
              placeholder="email-test@example.com"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              type="button"
              onClick={handleTestConfig}
              disabled={isTesting}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isTesting ? 'Test...' : 'Tester'}
            </button>
          </div>

          {testResult && (
            <div className={\`p-3 rounded \${testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}\`}>
              {testResult.message}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-4">
          <button
            type="submit"
            disabled={isUpdating}
            className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {isUpdating ? 'Enregistrement...' : 'Enregistrer la Configuration'}
          </button>
        </div>
      </form>
    </div>
  );
};
