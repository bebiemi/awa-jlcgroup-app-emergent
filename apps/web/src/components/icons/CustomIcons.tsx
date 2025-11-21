/**
 * Custom Icons for JLC Group Application
 * Collection of custom SVG icons for specific business contexts
 */

import React from 'react'

interface IconProps {
  className?: string
  width?: number | string
  height?: number | string
}

/**
 * Talents / Intérimaires Icon
 * Représente les travailleurs intérimaires et talents
 */
export const TalentsIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <circle cx="12" cy="8" r="3.2" stroke="currentColor" strokeWidth="1.6" />
    <path 
      d="M6.2 18.5C7.2 15.8 9.4 14 12 14c2.6 0 4.8 1.8 5.8 4.5"
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
    <path 
      d="M4 10.5c.8-1.2 1.9-2 3.3-2.3" 
      stroke="currentColor"
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M20 10.5c-.8-1.2-1.9-2-3.3-2.3" 
      stroke="currentColor"
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
  </svg>
)

/**
 * Missions / Assignations Icon
 * Représente les missions et assignations de travail
 */
export const MissionsIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <rect 
      x="3.5" 
      y="7.5" 
      width="17" 
      height="11" 
      rx="1.8" 
      ry="1.8" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M9 7.5V6.8C9 5.8 9.8 5 10.8 5h2.4C14.2 5 15 5.8 15 6.8v0.7"
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
    <path 
      d="M3.5 11.5h17" 
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
    <path 
      d="M10 12.2v1.8h4v-1.8" 
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
  </svg>
)

/**
 * Entreprises Clientes Icon
 * Représente les entreprises clientes
 */
export const EntreprisesIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <rect 
      x="4.5" 
      y="6" 
      width="7" 
      height="13" 
      rx="1.2" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <rect 
      x="12.5" 
      y="9" 
      width="7" 
      height="10" 
      rx="1.2" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M7 8h2M7 11h2M7 14h2" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M15 11h2M15 14h2" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M3 19h18" 
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
  </svg>
)

/**
 * RRH (Ressources Humaines) Icon
 * Représente la gestion RH et les documents
 */
export const RRHIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <path 
      d="M8.5 4.5h6l3 3v11a1.8 1.8 0 0 1-1.8 1.8H8.5A1.8 1.8 0 0 1 6.7 18.5V6.3A1.8 1.8 0 0 1 8.5 4.5Z"
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M14.5 4.5v3h3" 
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
    <path 
      d="M9.5 10h5" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M9.5 13h3.8" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M9 17c.7.6 1.3.9 1.8.9.6 0 1-.4 1.4-.8.4-.4.7-.7 1.1-.7.5 0 .9.4 1.4 1.2"
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
    />
  </svg>
)

/**
 * Planning / Disponibilités Icon
 * Représente la gestion du planning et des disponibilités
 */
export const PlanningIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <rect 
      x="4" 
      y="6.5" 
      width="16" 
      height="12.5" 
      rx="1.8" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M8 5v2.5M16 5v2.5"
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
    <path 
      d="M4 10h16" 
      stroke="currentColor" 
      strokeWidth="1.6" 
      strokeLinecap="round" 
    />
    <path 
      d="M10 14.5l1.7 1.7L15 13.1"
      stroke="currentColor" 
      strokeWidth="1.6"
      strokeLinecap="round" 
      strokeLinejoin="round" 
    />
  </svg>
)

/**
 * Paie / Facturation Icon
 * Représente la gestion de la paie et de la facturation
 */
export const PaieIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <rect 
      x="4.5" 
      y="4.5" 
      width="10" 
      height="15" 
      rx="1.6" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M7.5 8h4.5M7.5 11h3.5M7.5 14h2.5"
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <circle 
      cx="17.5" 
      cy="15.5" 
      r="2.7" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M17.5 13.7v3.6M16.5 14.7h2"
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
  </svg>
)

/**
 * Relation Tripartite Icon
 * Représente la relation tripartite (JLC – Client – Intérimaire)
 */
export const RelationTripartiteIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <circle 
      cx="12" 
      cy="6.5" 
      r="2.3" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <circle 
      cx="6" 
      cy="17.5" 
      r="2.3" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <circle 
      cx="18" 
      cy="17.5" 
      r="2.3" 
      stroke="currentColor" 
      strokeWidth="1.6" 
    />
    <path 
      d="M10.6 8.4 7.4 15.6" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M13.4 8.4 16.6 15.6" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <path 
      d="M8.3 17.5h7.4" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
  </svg>
)

/**
 * Présence Afrique Icon
 * Pictogramme stylisé représentant la présence en Afrique
 */
export const PresenceAfriqueIcon: React.FC<IconProps> = ({ 
  className = '', 
  width = 24, 
  height = 24 
}) => (
  <svg 
    viewBox="0 0 24 24" 
    width={width} 
    height={height} 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    className={className}
  >
    <path 
      d="M8 4.5 14 4l2.8 3.2-1.6 2.6-1.2 2.1.5 2.4-1.9 1.8-1.4-.4-.8 2.3"
      stroke="currentColor" 
      strokeWidth="1.6"
      strokeLinecap="round" 
      strokeLinejoin="round" 
    />
    <path 
      d="M9 7.2 11 7l1.2 1.1" 
      stroke="currentColor" 
      strokeWidth="1.4" 
      strokeLinecap="round" 
    />
    <circle 
      cx="13.4" 
      cy="10.2" 
      r="0.6" 
      fill="currentColor" 
    />
  </svg>
)

// Export all icons as a collection for easy access
export const CustomIcons = {
  Talents: TalentsIcon,
  Missions: MissionsIcon,
  Entreprises: EntreprisesIcon,
  RRH: RRHIcon,
  Planning: PlanningIcon,
  Paie: PaieIcon,
  RelationTripartite: RelationTripartiteIcon,
  PresenceAfrique: PresenceAfriqueIcon,
}

export default CustomIcons
