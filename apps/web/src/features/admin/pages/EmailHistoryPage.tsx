import React, { useState } from 'react';
import { useGetEmailHistoryQuery, useGetEmailStatsQuery } from '../api/emailHistoryApi';
import { usePermissions } from '@/hooks/usePermission';

export const EmailHistoryPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { permissions } = usePermissions(['emails.read_history'])
  const canRead = permissions['emails.read_history']
  
  const { data: history, isLoading } = useGetEmailHistoryQuery({
    page,
    page_size: 20,
    status_filter: statusFilter || undefined,
  }, { skip: !canRead });
  
  const { data: stats } = useGetEmailStatsQuery(undefined, { skip: !canRead });

  if (!canRead) return null;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Historique des Emails</h1>
        <p className="text-gray-600 mt-2">Liste des emails envoyés par l'application</p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white shadow rounded-lg p-4">
            <p className="text-sm text-gray-600">Total</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          </div>
          <div className="bg-green-50 shadow rounded-lg p-4">
            <p className="text-sm text-green-600">Envoyés</p>
            <p className="text-2xl font-bold text-green-700">{stats.sent}</p>
          </div>
          <div className="bg-red-50 shadow rounded-lg p-4">
            <p className="text-sm text-red-600">Échoués</p>
            <p className="text-2xl font-bold text-red-700">{stats.failed}</p>
          </div>
          <div className="bg-blue-50 shadow rounded-lg p-4">
            <p className="text-sm text-blue-600">Taux de succès</p>
            <p className="text-2xl font-bold text-blue-700">{stats.success_rate}%</p>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-4 flex gap-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">Tous les statuts</option>
            <option value="sent">Envoyés</option>
            <option value="failed">Échoués</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Destinataires</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sujet</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Envoyé par</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history?.items.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(item.created_at).toLocaleString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {item.to_emails.join(', ')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{item.subject}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      item.status === 'sent'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.sent_by}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {history && history.total_pages > 1 && (
          <div className="mt-4 flex justify-between items-center">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
            >
              Précédent
            </button>
            <span className="text-sm text-gray-700">
              Page {page} sur {history.total_pages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(history.total_pages, p + 1))}
              disabled={page === history.total_pages}
              className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
            >
              Suivant
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
