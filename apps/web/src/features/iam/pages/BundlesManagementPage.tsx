/**
 * Page de Gestion des Capability Bundles
 */
import React, { useState } from 'react';
import { 
  useGetBundlesQuery, 
  useDeleteBundleMutation,
  CapabilityBundle 
} from '../api/bundlesApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2, Plus, Search, Trash2, Edit, Package, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const CATEGORY_COLORS: Record<string, string> = {
  missions: 'bg-blue-500',
  applications: 'bg-green-500',
  documents: 'bg-yellow-500',
  profile: 'bg-purple-500',
  security: 'bg-red-500',
  admin: 'bg-gray-700',
  besoins: 'bg-indigo-500',
  entreprises: 'bg-cyan-500',
  dashboard: 'bg-pink-500',
  emargements: 'bg-orange-500',
  payroll: 'bg-teal-500',
  recruitment: 'bg-lime-500',
  system: 'bg-slate-500',
};

const BundlesManagementPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [bundleToDelete, setBundleToDelete] = useState<CapabilityBundle | null>(null);

  const { data: bundles, isLoading, error } = useGetBundlesQuery({});
  const [deleteBundle, { isLoading: isDeleting }] = useDeleteBundleMutation();

  // Filtrer les bundles
  const filteredBundles = bundles?.filter((bundle) => {
    const matchesSearch = 
      bundle.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bundle.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bundle.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = 
      categoryFilter === 'all' || bundle.category === categoryFilter;
    
    return matchesSearch && matchesCategory;
  }) || [];

  // Grouper par catégorie
  const bundlesByCategory = filteredBundles.reduce((acc, bundle) => {
    const category = bundle.category;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(bundle);
    return acc;
  }, {} as Record<string, CapabilityBundle[]>);

  const handleDelete = async () => {
    if (!bundleToDelete) return;

    if (bundleToDelete.is_system) {
      toast.error('Impossible de supprimer un bundle système');
      setBundleToDelete(null);
      return;
    }

    try {
      await deleteBundle(bundleToDelete.id).unwrap();
      toast.success(`Bundle "${bundleToDelete.name}" supprimé avec succès`);
      setBundleToDelete(null);
    } catch (error) {
      toast.error('Erreur lors de la suppression du bundle');
      console.error(error);
    }
  };

  // Statistiques
  const stats = {
    total: bundles?.length || 0,
    system: bundles?.filter(b => b.is_system).length || 0,
    custom: bundles?.filter(b => !b.is_system).length || 0,
    categories: Object.keys(bundlesByCategory).length,
  };

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card className="border-red-200">
          <CardHeader>
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <CardTitle>Erreur de chargement</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              Impossible de charger les bundles. Veuillez réessayer.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Gestion des Capability Bundles</h1>
        <p className="text-gray-600">
          Gérez les bundles de capacités réutilisables pour les profils IAM
        </p>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Bundles</CardDescription>
            <CardTitle className="text-3xl">{stats.total}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Système</CardDescription>
            <CardTitle className="text-3xl text-blue-600">{stats.system}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Personnalisés</CardDescription>
            <CardTitle className="text-3xl text-green-600">{stats.custom}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Catégories</CardDescription>
            <CardTitle className="text-3xl text-purple-600">{stats.categories}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Filtres et Actions */}
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="flex-1 w-full md:w-auto">
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
            
            <div className="flex gap-2 w-full md:w-auto">
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <SelectValue placeholder="Catégorie" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes catégories</SelectItem>
                  <SelectItem value="missions">Missions</SelectItem>
                  <SelectItem value="applications">Candidatures</SelectItem>
                  <SelectItem value="documents">Documents</SelectItem>
                  <SelectItem value="entreprises">Entreprises</SelectItem>
                  <SelectItem value="admin">Administration</SelectItem>
                  <SelectItem value="system">Système</SelectItem>
                </SelectContent>
              </Select>

              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Nouveau Bundle
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : filteredBundles.length === 0 ? (
            <div className="text-center py-8">
              <Package className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Aucun bundle trouvé</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Nom</TableHead>
                  <TableHead>Catégorie</TableHead>
                  <TableHead>Permissions</TableHead>
                  <TableHead>Tags</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredBundles.map((bundle) => (
                  <TableRow key={bundle.id}>
                    <TableCell className="font-mono text-sm">
                      {bundle.code}
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{bundle.name}</p>
                        <p className="text-xs text-gray-500 line-clamp-1">
                          {bundle.description}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        className={`${CATEGORY_COLORS[bundle.category] || 'bg-gray-500'} text-white`}
                      >
                        {bundle.category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {bundle.permission_ids.length} permissions
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {bundle.tags.slice(0, 2).map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {bundle.tags.length > 2 && (
                          <Badge variant="secondary" className="text-xs">
                            +{bundle.tags.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {bundle.is_system ? (
                        <Badge variant="outline" className="border-blue-500 text-blue-600">
                          Système
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="border-green-500 text-green-600">
                          Custom
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button size="sm" variant="ghost">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => setBundleToDelete(bundle)}
                          disabled={bundle.is_system}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Dialog de confirmation de suppression */}
      <AlertDialog open={!!bundleToDelete} onOpenChange={() => setBundleToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
            <AlertDialogDescription>
              Êtes-vous sûr de vouloir supprimer le bundle "{bundleToDelete?.name}" ?
              Cette action est irréversible et peut affecter les profils utilisant ce bundle.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Suppression...
                </>
              ) : (
                'Supprimer'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default BundlesManagementPage;
