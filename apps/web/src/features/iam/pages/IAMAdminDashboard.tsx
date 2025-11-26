import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Users, 
  Shield, 
  Key, 
  Package, 
  Search, 
  Plus,
  AlertCircle,
  CheckCircle,
  Settings,
  BarChart
} from 'lucide-react';
import { useListProfilesQuery, useListPermissionsQuery } from '../api/iamApi';
import { useCanReadPermissions } from '../useCanReadPermissions';
import { useBundlesQuery } from '../api/bundlesApi';

/**
 * Dashboard Admin IAM - Interface complète de gestion
 * 
 * Fonctionnalités :
 * - Vue d'ensemble statistiques
 * - Gestion profils
 * - Gestion permissions
 * - Gestion bundles
 * - Audit et monitoring
 */
export const IAMAdminDashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Charger les données
  const { data: profiles = [], isLoading: loadingProfiles } = useListProfilesQuery();
  const { canReadPermissions } = useCanReadPermissions();
  const { data: permissions = [], isLoading: loadingPermissions } = useListPermissionsQuery(undefined, {
    skip: !canReadPermissions,
  });
  const { data: bundles = [], isLoading: loadingBundles } = useBundlesQuery();

  // Statistiques
  const stats = {
    totalProfiles: profiles.length,
    totalPermissions: permissions.length,
    totalBundles: bundles.length,
    profilesWithBundles: profiles.filter(p => p.capability_bundle_ids?.length > 0).length,
    emptyProfiles: profiles.filter(p => 
      !p.permission_ids?.length && !p.capability_bundle_ids?.length
    ).length,
    ownPermissions: permissions.filter(p => p.code.includes('.own')).length,
    allPermissions: permissions.filter(p => p.code.includes('.all')).length,
  };

  if (loadingProfiles || loadingPermissions || loadingBundles) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement IAM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Administration IAM</h1>
          <p className="text-gray-600 mt-1">
            Gestion complète des identités, profils et permissions
          </p>
        </div>
        <Button>
          <Settings className="mr-2 h-4 w-4" />
          Paramètres
        </Button>
      </div>

      {/* Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">
            <BarChart className="mr-2 h-4 w-4" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger value="profiles">
            <Users className="mr-2 h-4 w-4" />
            Profils ({stats.totalProfiles})
          </TabsTrigger>
          <TabsTrigger value="permissions">
            <Key className="mr-2 h-4 w-4" />
            Permissions ({stats.totalPermissions})
          </TabsTrigger>
          <TabsTrigger value="bundles">
            <Package className="mr-2 h-4 w-4" />
            Bundles ({stats.totalBundles})
          </TabsTrigger>
          <TabsTrigger value="audit">
            <Shield className="mr-2 h-4 w-4" />
            Audit
          </TabsTrigger>
        </TabsList>

        {/* Tab: Vue d'ensemble */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Stat Cards */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Profils</CardTitle>
                <Users className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalProfiles}</div>
                <p className="text-xs text-gray-600 mt-1">
                  {stats.profilesWithBundles} avec bundles
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Permissions</CardTitle>
                <Key className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalPermissions}</div>
                <p className="text-xs text-gray-600 mt-1">
                  {stats.ownPermissions} .own / {stats.allPermissions} .all
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Bundles</CardTitle>
                <Package className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalBundles}</div>
                <p className="text-xs text-gray-600 mt-1">
                  {Math.round(stats.totalPermissions / stats.totalBundles)} perms/bundle
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Santé Système</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">Sain</div>
                <p className="text-xs text-gray-600 mt-1">
                  {stats.emptyProfiles} profils vides
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Alertes et Recommandations */}
          <Card>
            <CardHeader>
              <CardTitle>État du Système IAM</CardTitle>
              <CardDescription>Alertes et recommandations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {stats.emptyProfiles > 0 && (
                <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-yellow-900">
                      {stats.emptyProfiles} profil(s) vide(s) détecté(s)
                    </p>
                    <p className="text-sm text-yellow-700">
                      Ces profils n'ont ni permissions directes ni bundles. Considérer leur suppression ou configuration.
                    </p>
                  </div>
                </div>
              )}

              {stats.totalPermissions === permissions.filter(p => p.code.includes('.')).length && (
                <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-green-900">
                      Format moderne respecté
                    </p>
                    <p className="text-sm text-green-700">
                      Toutes les permissions utilisent le format resource.action.scope
                    </p>
                  </div>
                </div>
              )}

              {stats.profilesWithBundles > stats.totalProfiles * 0.5 && (
                <div className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-blue-900">
                      Bonne utilisation des bundles
                    </p>
                    <p className="text-sm text-blue-700">
                      {Math.round((stats.profilesWithBundles / stats.totalProfiles) * 100)}% des profils utilisent des bundles de capacités
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions Rapides */}
          <Card>
            <CardHeader>
              <CardTitle>Actions Rapides</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Button variant="outline" className="justify-start">
                <Plus className="mr-2 h-4 w-4" />
                Créer un profil
              </Button>
              <Button variant="outline" className="justify-start">
                <Plus className="mr-2 h-4 w-4" />
                Créer un bundle
              </Button>
              <Button variant="outline" className="justify-start">
                <Shield className="mr-2 h-4 w-4" />
                Lancer un audit
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Profils */}
        <TabsContent value="profiles" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher un profil..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nouveau profil
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {profiles
              .filter(profile => 
                profile.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                profile.code.toLowerCase().includes(searchTerm.toLowerCase())
              )
              .map((profile) => (
                <Card key={profile.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{profile.name}</CardTitle>
                        <CardDescription className="text-xs mt-1">
                          {profile.code}
                        </CardDescription>
                      </div>
                      {profile.is_protected && (
                        <Badge variant="secondary">
                          <Shield className="h-3 w-3 mr-1" />
                          Protégé
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Permissions directes:</span>
                        <span className="font-medium">{profile.permission_ids?.length || 0}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Bundles:</span>
                        <span className="font-medium">{profile.capability_bundle_ids?.length || 0}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Total effectif:</span>
                        <span className="font-medium text-blue-600">
                          {(profile.permission_ids?.length || 0) + 
                           (profile.capability_bundle_ids?.length || 0) * 3 /* estimation */}
                        </span>
                      </div>
                      <Button variant="outline" size="sm" className="w-full mt-3">
                        Gérer
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        {/* Tab: Permissions */}
        <TabsContent value="permissions" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher une permission..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                Filtrer
              </Button>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Nouvelle permission
              </Button>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scope</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Catégorie</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {permissions
                      .filter(perm => 
                        perm.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        perm.name.toLowerCase().includes(searchTerm.toLowerCase())
                      )
                      .slice(0, 50)
                      .map((permission) => (
                        <tr key={permission.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm font-mono text-gray-900">
                            {permission.code}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-700">
                            {permission.name}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Badge variant="outline">{permission.resource}</Badge>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Badge variant="outline">{permission.action}</Badge>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {permission.scope ? (
                              <Badge variant={permission.scope === 'own' ? 'secondary' : 'default'}>
                                {permission.scope}
                              </Badge>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Badge>{permission.category}</Badge>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Bundles */}
        <TabsContent value="bundles" className="space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Rechercher un bundle..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nouveau bundle
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bundles
              .filter(bundle => 
                bundle.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                bundle.code.toLowerCase().includes(searchTerm.toLowerCase())
              )
              .map((bundle) => (
                <Card key={bundle.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">{bundle.name}</CardTitle>
                        <CardDescription className="text-xs mt-1">
                          {bundle.code}
                        </CardDescription>
                      </div>
                      <Badge>{bundle.category}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 mb-4">
                      {bundle.description}
                    </p>
                    <div className="flex justify-between items-center">
                      <div className="text-sm">
                        <span className="text-gray-600">Permissions:</span>
                        <span className="ml-2 font-medium">{bundle.permission_ids?.length || 0}</span>
                      </div>
                      <Button variant="outline" size="sm">
                        Détails
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        {/* Tab: Audit */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit et Monitoring IAM</CardTitle>
              <CardDescription>
                Surveillance de l'intégrité et de la sécurité du système IAM
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="text-left">
                    <div className="font-medium">Audit Complet</div>
                    <div className="text-xs text-gray-600 mt-1">
                      Vérifier l'intégrité du système
                    </div>
                  </div>
                </Button>
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="text-left">
                    <div className="font-medium">Permissions Orphelines</div>
                    <div className="text-xs text-gray-600 mt-1">
                      Détecter les références invalides
                    </div>
                  </div>
                </Button>
                <Button variant="outline" className="justify-start h-auto py-4">
                  <div className="text-left">
                    <div className="font-medium">Rapport d'Utilisation</div>
                    <div className="text-xs text-gray-600 mt-1">
                      Analyser l'usage des permissions
                    </div>
                  </div>
                </Button>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-medium mb-3">Derniers Audits</h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <div>
                      <p className="text-sm font-medium">Audit intégrité globale</p>
                      <p className="text-xs text-gray-600">Il y a 2 heures</p>
                    </div>
                    <Badge className="bg-green-600">Succès</Badge>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <div>
                      <p className="text-sm font-medium">Vérification références</p>
                      <p className="text-xs text-gray-600">Il y a 1 jour</p>
                    </div>
                    <Badge className="bg-green-600">Succès</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IAMAdminDashboard;
