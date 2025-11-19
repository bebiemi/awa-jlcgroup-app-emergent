/**
 * Composant de Visualisation de Hiérarchie de Profils
 */
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronRight, Shield, Users, Building, Briefcase } from 'lucide-react';

interface Profile {
  id: string;
  code: string;
  name: string;
  category: string;
  is_system: boolean;
  parent_profile_id?: string;
}

interface ProfileHierarchyTreeProps {
  profiles: Profile[];
  selectedProfileId?: string;
  onProfileClick?: (profile: Profile) => void;
}

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  system: <Shield className="h-4 w-4" />,
  business: <Briefcase className="h-4 w-4" />,
  admin: <Shield className="h-4 w-4 text-red-600" />,
  technical: <Users className="h-4 w-4" />,
};

const CATEGORY_COLORS: Record<string, string> = {
  system: 'bg-gray-100 text-gray-700 border-gray-300',
  business: 'bg-blue-50 text-blue-700 border-blue-300',
  admin: 'bg-red-50 text-red-700 border-red-300',
  technical: 'bg-purple-50 text-purple-700 border-purple-300',
};

const ProfileHierarchyTree: React.FC<ProfileHierarchyTreeProps> = ({
  profiles,
  selectedProfileId,
  onProfileClick,
}) => {
  // Construire l'arbre de hiérarchie
  const buildTree = (parentId?: string, level = 0): React.ReactNode[] => {
    const children = profiles.filter(
      (p) => p.parent_profile_id === parentId
    );

    if (children.length === 0) return [];

    return children.map((profile) => {
      const hasChildren = profiles.some(
        (p) => p.parent_profile_id === profile.id
      );
      const isSelected = profile.id === selectedProfileId;

      return (
        <div key={profile.id} className="space-y-2">
          <div
            className={`
              flex items-center gap-3 p-3 rounded-lg border-2 transition-all cursor-pointer
              ${isSelected 
                ? 'border-blue-500 bg-blue-50 shadow-sm' 
                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
              }
            `}
            style={{ marginLeft: `${level * 24}px` }}
            onClick={() => onProfileClick?.(profile)}
          >
            {/* Connecteur visuel */}
            {level > 0 && (
              <div className="flex items-center">
                <div className="w-6 h-px bg-gray-300" />
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </div>
            )}

            {/* Icône catégorie */}
            <div className={`
              p-2 rounded-lg border
              ${CATEGORY_COLORS[profile.category] || CATEGORY_COLORS.business}
            `}>
              {CATEGORY_ICONS[profile.category] || <Users className="h-4 w-4" />}
            </div>

            {/* Informations profil */}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold">{profile.name}</span>
                {profile.is_system && (
                  <Badge variant="outline" className="text-xs">
                    Système
                  </Badge>
                )}
              </div>
              <p className="text-xs text-gray-500 font-mono">{profile.code}</p>
            </div>

            {/* Indicateur enfants */}
            {hasChildren && (
              <Badge variant="secondary" className="text-xs">
                {profiles.filter((p) => p.parent_profile_id === profile.id).length} enfant(s)
              </Badge>
            )}
          </div>

          {/* Enfants */}
          {hasChildren && (
            <div className="space-y-2">
              {buildTree(profile.id, level + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  // Trouver les profils racines (sans parent ou parent inexistant)
  const rootProfiles = profiles.filter(
    (p) => !p.parent_profile_id || !profiles.find((parent) => parent.id === p.parent_profile_id)
  );

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Hiérarchie des Profils</h3>
            <Badge variant="outline">{profiles.length} profils</Badge>
          </div>

          {/* Racines */}
          {rootProfiles.map((rootProfile) => {
            const hasChildren = profiles.some(
              (p) => p.parent_profile_id === rootProfile.id
            );
            const isSelected = rootProfile.id === selectedProfileId;

            return (
              <div key={rootProfile.id} className="space-y-2">
                {/* Profil racine */}
                <div
                  className={`
                    flex items-center gap-3 p-4 rounded-lg border-2 transition-all cursor-pointer
                    ${isSelected 
                      ? 'border-blue-500 bg-blue-50 shadow-sm' 
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                    }
                  `}
                  onClick={() => onProfileClick?.(rootProfile)}
                >
                  <div className={`
                    p-2 rounded-lg border
                    ${CATEGORY_COLORS[rootProfile.category] || CATEGORY_COLORS.business}
                  `}>
                    {CATEGORY_ICONS[rootProfile.category] || <Users className="h-4 w-4" />}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{rootProfile.name}</span>
                      {rootProfile.is_system && (
                        <Badge variant="outline" className="text-xs">
                          Système
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 font-mono">{rootProfile.code}</p>
                  </div>

                  {hasChildren && (
                    <Badge variant="secondary" className="text-xs">
                      {profiles.filter((p) => p.parent_profile_id === rootProfile.id).length} enfant(s)
                    </Badge>
                  )}
                </div>

                {/* Enfants de la racine */}
                {buildTree(rootProfile.id, 1)}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProfileHierarchyTree;
