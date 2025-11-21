/**
 * Icon Showcase Component
 * Demonstrates all custom icons with different sizes and colors
 */

import React from 'react'
import {
  TalentsIcon,
  MissionsIcon,
  EntreprisesIcon,
  RRHIcon,
  PlanningIcon,
  PaieIcon,
  RelationTripartiteIcon,
  PresenceAfriqueIcon,
} from './CustomIcons'

const IconShowcase: React.FC = () => {
  const icons = [
    { 
      name: 'Talents / Intérimaires', 
      Icon: TalentsIcon, 
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      description: 'Travailleurs intérimaires et talents'
    },
    { 
      name: 'Missions / Assignations', 
      Icon: MissionsIcon, 
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
      description: 'Missions et assignations de travail'
    },
    { 
      name: 'Entreprises Clientes', 
      Icon: EntreprisesIcon, 
      color: 'text-purple-600',
      bg: 'bg-purple-50',
      description: 'Gestion des entreprises clientes'
    },
    { 
      name: 'RRH', 
      Icon: RRHIcon, 
      color: 'text-green-600',
      bg: 'bg-green-50',
      description: 'Ressources Humaines et documents'
    },
    { 
      name: 'Planning / Disponibilités', 
      Icon: PlanningIcon, 
      color: 'text-orange-600',
      bg: 'bg-orange-50',
      description: 'Gestion du planning et disponibilités'
    },
    { 
      name: 'Paie / Facturation', 
      Icon: PaieIcon, 
      color: 'text-teal-600',
      bg: 'bg-teal-50',
      description: 'Gestion de la paie et facturation'
    },
    { 
      name: 'Relation Tripartite', 
      Icon: RelationTripartiteIcon, 
      color: 'text-pink-600',
      bg: 'bg-pink-50',
      description: 'JLC – Client – Intérimaire'
    },
    { 
      name: 'Présence Afrique', 
      Icon: PresenceAfriqueIcon, 
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      description: 'Présence géographique en Afrique'
    },
  ]

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Icônes Personnalisées JLC Group
          </h1>
          <p className="text-gray-600">
            Collection d'icônes SVG optimisées pour l'application
          </p>
        </div>

        {/* Grid of icons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {icons.map(({ name, Icon, color, bg, description }) => (
            <div 
              key={name}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className={`${bg} rounded-lg p-4 mb-4 flex items-center justify-center`}>
                <Icon className={`${color} w-12 h-12`} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{name}</h3>
              <p className="text-sm text-gray-600">{description}</p>
            </div>
          ))}
        </div>

        {/* Size variations */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-12">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Variations de Taille
          </h2>
          <div className="flex items-end space-x-8">
            <div className="text-center">
              <TalentsIcon className="w-4 h-4 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600">16px</p>
            </div>
            <div className="text-center">
              <TalentsIcon className="w-5 h-5 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600">20px</p>
            </div>
            <div className="text-center">
              <TalentsIcon className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600">24px</p>
            </div>
            <div className="text-center">
              <TalentsIcon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600">32px</p>
            </div>
            <div className="text-center">
              <TalentsIcon className="w-12 h-12 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600">48px</p>
            </div>
            <div className="text-center">
              <TalentsIcon className="w-16 h-16 text-blue-600 mx-auto mb-2" />
              <p className="text-xs text-gray-600">64px</p>
            </div>
          </div>
        </div>

        {/* Color variations */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            Variations de Couleur
          </h2>
          <div className="flex items-center space-x-6">
            <MissionsIcon className="w-10 h-10 text-gray-400" />
            <MissionsIcon className="w-10 h-10 text-gray-600" />
            <MissionsIcon className="w-10 h-10 text-blue-600" />
            <MissionsIcon className="w-10 h-10 text-indigo-600" />
            <MissionsIcon className="w-10 h-10 text-purple-600" />
            <MissionsIcon className="w-10 h-10 text-green-600" />
            <MissionsIcon className="w-10 h-10 text-red-600" />
          </div>
        </div>

        {/* Usage example */}
        <div className="bg-gray-800 rounded-lg shadow-sm p-8 mt-12">
          <h2 className="text-xl font-bold text-white mb-4">
            Exemple d'Utilisation
          </h2>
          <pre className="text-sm text-gray-300 overflow-x-auto">
{`import { TalentsIcon, MissionsIcon } from '@/components/icons/CustomIcons'

function NavigationMenu() {
  return (
    <nav>
      <a href="/talents">
        <TalentsIcon className="w-5 h-5 text-blue-600" />
        <span>Talents</span>
      </a>
      <a href="/missions">
        <MissionsIcon className="w-5 h-5 text-indigo-600" />
        <span>Missions</span>
      </a>
    </nav>
  )
}`}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default IconShowcase
