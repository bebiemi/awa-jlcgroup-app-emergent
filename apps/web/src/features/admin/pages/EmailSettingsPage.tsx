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
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Tooltip from '@/components/Tooltip';
import { PlusIcon, EnvelopeIcon, Cog6ToothIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { usePermissions } from '@/hooks/usePermission';
import { IAMPermissions } from '@/constants/iamConstants';

type SectionType = 'smtp' | 'admin' | 'test'

export const EmailSettingsPage: React.FC = () => {
  const { data: settings, isLoading, error } = useGetEmailSettingsQuery();
  const [updateSettings, { isLoading: isUpdating }] = useUpdateEmailSettingsMutation();
  const [testConfig, { isLoading: isTesting }] = useTestEmailConfigMutation();
  const { permissions } = usePermissions([
    IAMPermissions.EMAILS_READ_CONFIG,
    IAMPermissions.EMAILS_CONFIGURE,
    IAMPermissions.EMAILS_TEST,
  ])
  const canRead = permissions[IAMPermissions.EMAILS_READ_CONFIG] || permissions[IAMPermissions.EMAILS_CONFIGURE]
  const canConfigure = permissions[IAMPermissions.EMAILS_CONFIGURE]
  const canTest = permissions[IAMPermissions.EMAILS_TEST] || permissions[IAMPermissions.EMAILS_CONFIGURE]

  const [activeSection, setActiveSection] = useState<SectionType>('smtp')

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
    if (!canTest) return
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
    
    if (!canConfigure) return;
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

  if (!canRead) return null;

  if (isLoading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-jlc-purple-600"></div>
        </div>
      </Layout>
    );
  }

  const hasNoConfig = error && (error as any).status === 404;

  // Statistics
  const stats = {
    status: formData.enabled ? 'Actif' : 'Inactif',
    adminCount: formData.admin_emails.length,
    provider: formData.provider,
    tls: formData.smtp_use_tls ? 'Activé' : 'Désactivé'
  }

  const sections = [
    { value: 'smtp', label: 'Configuration SMTP', icon: Cog6ToothIcon },
    { value: 'admin', label: 'Emails Admin', icon: EnvelopeIcon },
    { value: 'test', label: 'Test Configuration', icon: CheckCircleIcon },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Configuration Email</h1>
            <p className="text-gray-600 mt-2">
              Configurez les paramètres SMTP pour les notifications email
            </p>
          </div>
        </div>

        {hasNoConfig && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
            <div className="flex">
              <div className="text-4xl mr-3">⚠️</div>
              <p className="text-yellow-700">
                Aucune configuration email trouvée. Créez-en une nouvelle ci-dessous.
              </p>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Tooltip content="État actuel des notifications email" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Statut</p>
                  <p className={`text-2xl font-bold ${
                    formData.enabled ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stats.status}
                  </p>
                </div>
                <div className="text-3xl">{formData.enabled ? '✅' : '❌'}</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Nombre d'emails administrateurs configurés" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Emails Admin</p>
                  <p className="text-2xl font-bold text-jlc-purple-600">{stats.adminCount}</p>
                </div>
                <div className="text-3xl">📧</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="Fournisseur de service email configuré" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Fournisseur</p>
                  <p className="text-lg font-bold text-gray-900 capitalize">{stats.provider}</p>
                </div>
                <div className="text-3xl">📨</div>
              </div>
            </Card>
          </Tooltip>
          <Tooltip content="État de la sécurité TLS/SSL" position="top">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Sécurité TLS</p>
                  <p className={`text-lg font-bold ${
                    formData.smtp_use_tls ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stats.tls}
                  </p>
                </div>
                <div className="text-3xl">🔒</div>
              </div>
            </Card>
          </Tooltip>
        </div>

        {/* Section Selector */}
        <Card>
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Sections</h3>
            <p className="text-sm text-gray-600">Sélectionnez une section pour configurer</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {sections.map((section) => {
              const Icon = section.icon
              return (
                <Tooltip 
                  key={section.value}
                  content={`Gérer ${section.label.toLowerCase()}`}
                  position="top"
                >
                  <button
                    onClick={() => setActiveSection(section.value as SectionType)}
                    className={`px-6 py-4 rounded-lg transition-all text-left ${
                      activeSection === section.value
                        ? 'bg-jlc-purple-600 text-white shadow-lg scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:scale-102 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-8 w-8" />
                      <div className="font-semibold">{section.label}</div>
                    </div>
                  </button>
                </Tooltip>
              )
            })}
          </div>
        </Card>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* SMTP Configuration Section */}
          {activeSection === 'smtp' && (
            <Card>
              <div className="space-y-4">
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
                    <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-jlc-purple-600 peer-focus:ring-4 peer-focus:ring-purple-300 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full peer-checked:after:border-white"></div>
                  </label>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fournisseur SMTP
                    </label>
                    <select
                      value={formData.provider}
                      onChange={(e) => handleProviderChange(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                        required={!settings}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-2 top-2 text-gray-500 hover:text-gray-700"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                      required
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.smtp_use_tls}
                        onChange={(e) => setFormData({ ...formData, smtp_use_tls: e.target.checked })}
                        className="rounded border-gray-300 text-jlc-purple-600 focus:ring-jlc-purple-500 h-4 w-4"
                      />
                      <span className="ml-2 text-sm text-gray-700">Utiliser TLS (Recommandé)</span>
                    </label>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Admin Emails Section */}
          {activeSection === 'admin' && (
            <Card>
              <div className="space-y-4">
                <div className="mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Emails Administrateurs</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Ces emails recevront les notifications critiques
                  </p>
                </div>

                <div className="flex gap-2">
                  <input
                    type="email"
                    value={newAdminEmail}
                    onChange={(e) => setNewAdminEmail(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddAdminEmail())}
                    placeholder="admin@jlc.com"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  />
                  <button
                    type="button"
                    onClick={handleAddAdminEmail}
                    className="flex items-center gap-2 px-4 py-2 bg-jlc-purple-600 text-white rounded-md hover:bg-jlc-purple-700 transition-colors shadow-md"
                  >
                    <PlusIcon className="h-5 w-5" />
                    Ajouter
                  </button>
                </div>

                <div className="space-y-2">
                  {formData.admin_emails.map((email) => (
                    <div key={email} className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-white px-4 py-3 rounded-lg border border-gray-200 hover:shadow-md transition-all">
                      <div className="flex items-center gap-2">
                        <EnvelopeIcon className="h-5 w-5 text-jlc-purple-600" />
                        <span className="text-sm text-gray-700 font-medium">{email}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveAdminEmail(email)}
                        className="text-red-600 hover:text-red-800 hover:bg-red-50 p-2 rounded transition-colors"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                  {formData.admin_emails.length === 0 && (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-2">📧</div>
                      <p className="text-sm text-gray-500 italic">Aucun email admin ajouté</p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          )}

          {/* Test Configuration Section */}
          {activeSection === 'test' && (
            <Card>
              <div className="space-y-4">
                <div className="mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Tester la Configuration</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Envoyez un email de test pour vérifier la configuration
                  </p>
                </div>
                
                <div className="flex gap-2">
                  <input
                    type="email"
                    value={testEmail}
                    onChange={(e) => setTestEmail(e.target.value)}
                    placeholder="email-test@example.com"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-jlc-purple-500 focus:border-jlc-purple-500"
                  />
                  <button
                    type="button"
                    onClick={handleTestConfig}
                    disabled={isTesting}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md"
                  >
                    {isTesting ? 'Test en cours...' : 'Tester'}
                  </button>
                </div>

                {testResult && (
                  <div className={`p-4 rounded-lg border-l-4 ${
                    testResult.success 
                      ? 'bg-green-50 border-green-500 text-green-700' 
                      : 'bg-red-50 border-red-500 text-red-700'
                  }`}>
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">
                        {testResult.success ? '✅' : '❌'}
                      </div>
                      <div>
                        <div className="font-semibold mb-1">
                          {testResult.success ? 'Test réussi !' : 'Test échoué'}
                        </div>
                        <div className="text-sm">{testResult.message}</div>
                      </div>
                    </div>
                  </div>
                )}

                {!testResult && (
                  <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">💡</div>
                      <div className="text-sm text-blue-700">
                        <p className="font-semibold mb-1">Conseil</p>
                        <p>Assurez-vous d'avoir enregistré la configuration avant de tester. Le test utilisera les paramètres actuels du formulaire.</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Save Button */}
          <div className="flex justify-end gap-4">
            <button
              type="submit"
              disabled={isUpdating}
              className="px-6 py-3 bg-jlc-purple-600 text-white rounded-lg hover:bg-jlc-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg font-medium"
            >
              {isUpdating ? 'Enregistrement...' : 'Enregistrer la Configuration'}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
};
