/**
 * Console de Gestion des Expirations de Profils
 */
import React, { useState } from 'react';
import {
  useCheckAllExpirationsQuery,
  useGetExpirationStatsQuery,
  useProcessExpirationsMutation,
  useSendNotificationsMutation,
  useManualDowngradeMutation,
  ExpirationCheck,
} from '../api/expirationsApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { 
  Loader2, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Bell,
  XCircle,
  TrendingDown
} from 'lucide-react';
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
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

const ExpirationsConsolePage: React.FC = () => {
  const [showProcessDialog, setShowProcessDialog] = useState(false);
  const [userToDowngrade, setUserToDowngrade] = useState<{
    userId: string;
    profileId: string;
    username: string;
  } | null>(null);

  const { 
    data: expirations, 
    isLoading: isLoadingExpirations,
    refetch: refetchExpirations
  } = useCheckAllExpirationsQuery();
  
  const { 
    data: stats, 
    isLoading: isLoadingStats 
  } = useGetExpirationStatsQuery();

  const [processExpirations, { isLoading: isProcessing }] = useProcessExpirationsMutation();
  const [sendNotifications, { isLoading: isSendingNotifications }] = useSendNotificationsMutation();
  const [manualDowngrade, { isLoading: isDowngrading }] = useManualDowngradeMutation();

  const handleProcessExpirations = async () => {
    try {
      const result = await processExpirations().unwrap();
      toast.success(
        `Traitement terminé: ${result.downgraded}/${result.total_expired} profils downgradés`
      );
      setShowProcessDialog(false);
      refetchExpirations();
    } catch (error) {
      toast.error('Erreur lors du traitement des expirations');
      console.error(error);
    }
  };

  const handleSendNotifications = async () => {
    try {
      const result = await sendNotifications().unwrap();
      toast.success(`${result.notified} notifications envoyées`);
      refetchExpirations();
    } catch (error) {
      toast.error('Erreur lors de l\'envoi des notifications');
      console.error(error);
    }
  };

  const handleManualDowngrade = async () => {
    if (!userToDowngrade) return;

    try {
      await manualDowngrade({
        userId: userToDowngrade.userId,
        profileId: userToDowngrade.profileId,
      }).unwrap();
      
      toast.success(
        `Profil downgradé pour ${userToDowngrade.username}`
      );
      setUserToDowngrade(null);
      refetchExpirations();
    } catch (error) {
      toast.error('Erreur lors du downgrade manuel');
      console.error(error);
    }
  };

  // Statistiques calculées
  const totalUsers = expirations?.length || 0;
  const totalExpired = expirations?.reduce((sum, e) => sum + e.expired_count, 0) || 0;
  const totalExpiringSoon = expirations?.reduce((sum, e) => sum + e.expiring_soon_count, 0) || 0;

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold mb-2">Console des Expirations</h1>
          <p className="text-gray-600">
            Gestion des profils temporaires et expirations automatiques
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => refetchExpirations()}
            disabled={isLoadingExpirations}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoadingExpirations ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
          
          <Button
            variant="outline"
            onClick={handleSendNotifications}
            disabled={isSendingNotifications || totalExpiringSoon === 0}
          >
            <Bell className="h-4 w-4 mr-2" />
            Notifier ({totalExpiringSoon})
          </Button>

          <Button
            onClick={() => setShowProcessDialog(true)}
            disabled={totalExpired === 0}
            className="bg-orange-600 hover:bg-orange-700"
          >
            <TrendingDown className="h-4 w-4 mr-2" />
            Traiter Expirations ({totalExpired})
          </Button>
        </div>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription>Utilisateurs Vérifiés</CardDescription>
              <Clock className="h-4 w-4 text-gray-400" />
            </div>
            <CardTitle className="text-3xl">{totalUsers}</CardTitle>
          </CardHeader>
        </Card>

        <Card className="border-red-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription>Profils Expirés</CardDescription>
              <XCircle className="h-4 w-4 text-red-500" />
            </div>
            <CardTitle className="text-3xl text-red-600">{totalExpired}</CardTitle>
          </CardHeader>
        </Card>

        <Card className="border-yellow-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription>Expire Bientôt (&lt;3j)</CardDescription>
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            </div>
            <CardTitle className="text-3xl text-yellow-600">{totalExpiringSoon}</CardTitle>
          </CardHeader>
        </Card>

        <Card className="border-green-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardDescription>Conforme</CardDescription>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            </div>
            <CardTitle className="text-3xl text-green-600">
              {totalUsers - (expirations?.length || 0)}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Table des expirations */}
      <Card>
        <CardHeader>
          <CardTitle>Utilisateurs avec Expirations</CardTitle>
          <CardDescription>
            Liste des utilisateurs ayant des profils temporaires expirés ou expirant bientôt
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingExpirations ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : !expirations || expirations.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle2 className="h-12 w-12 text-green-400 mx-auto mb-3" />
              <p className="text-gray-500">Aucune expiration à traiter</p>
              <p className="text-sm text-gray-400 mt-1">
                Tous les profils temporaires sont valides
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Utilisateur</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Profils Expirés</TableHead>
                  <TableHead>Expire Bientôt</TableHead>
                  <TableHead>Détails</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {expirations.map((expiration) => (
                  <TableRow key={expiration.user_id}>
                    <TableCell className="font-medium">
                      {expiration.username}
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {expiration.email}
                    </TableCell>
                    <TableCell>
                      {expiration.expired_count > 0 ? (
                        <Badge variant="destructive" className="flex items-center gap-1 w-fit">
                          <XCircle className="h-3 w-3" />
                          {expiration.expired_count}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {expiration.expiring_soon_count > 0 ? (
                        <Badge variant="outline" className="border-yellow-500 text-yellow-600 flex items-center gap-1 w-fit">
                          <AlertTriangle className="h-3 w-3" />
                          {expiration.expiring_soon_count}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {expiration.expired_profiles.map((profile) => (
                          <div key={profile.profile_id} className="text-xs text-red-600">
                            Expiré {formatDistanceToNow(new Date(profile.expires_at), { 
                              addSuffix: true,
                              locale: fr 
                            })}
                          </div>
                        ))}
                        {expiration.expiring_soon.map((profile) => (
                          <div key={profile.profile_id} className="text-xs text-yellow-600">
                            Expire dans {profile.days_until_expiration}j
                          </div>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      {expiration.expired_profiles.length > 0 && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-orange-600 hover:text-orange-700"
                          onClick={() => setUserToDowngrade({
                            userId: expiration.user_id,
                            profileId: expiration.expired_profiles[0].profile_id,
                            username: expiration.username,
                          })}
                        >
                          Downgrader
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Dialog de traitement automatique */}
      <AlertDialog open={showProcessDialog} onOpenChange={setShowProcessDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Traiter les Expirations</AlertDialogTitle>
            <AlertDialogDescription>
              Cette action va automatiquement downgrader tous les profils expirés ({totalExpired}) 
              vers le profil "Restreint". Cette opération est réversible mais nécessite une intervention manuelle.
              <br /><br />
              Voulez-vous continuer ?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleProcessExpirations}
              disabled={isProcessing}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Traitement...
                </>
              ) : (
                'Traiter'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Dialog de downgrade manuel */}
      <AlertDialog open={!!userToDowngrade} onOpenChange={() => setUserToDowngrade(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Downgrade Manuel</AlertDialogTitle>
            <AlertDialogDescription>
              Êtes-vous sûr de vouloir downgrader le profil de l'utilisateur "{userToDowngrade?.username}" ?
              Le profil sera remplacé par "Restreint".
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleManualDowngrade}
              disabled={isDowngrading}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {isDowngrading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Downgrade...
                </>
              ) : (
                'Confirmer'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ExpirationsConsolePage;
