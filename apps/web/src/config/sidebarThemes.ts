/**
 * Thèmes officiels JLC pour la sidebar
 * Palette :
 *  - Magenta: #913975
 *  - Indigo grisé foncé: #362f50
 *  - Néon rose grisé: #56335d
 *  - Néon rose: #743669
 */

export const SIDEBAR_THEMES = {
  dark: {
    name: 'dark',
    // Fond principal : gradient profond basé sur Indigo + Néon rose grisé + Magenta
    bg: 'bg-gradient-to-b from-[#362f50]/85 via-[#56335d]/80 to-[#913975]/75',
    contentBg: 'linear-gradient(135deg, rgba(32, 26, 52, 0.65), rgba(41, 31, 62, 0.7))',
    contentBorder: 'rgba(255,255,255,0.08)',
    accent: '#913975',
    glow: '0 20px 60px rgba(145,57,117,0.18)',
    textPrimary: '#f8fafc',
    textSecondary: '#cbd5e1',
    textHeading: '#f1f5f9',
    textAccent: '#fbbf24',
    pageBg: 'linear-gradient(135deg, rgba(32,26,52,0.65), rgba(41,31,62,0.7), rgba(145,57,117,0.35))',
    // Couleur de texte par défaut
    text: 'text-gray-100',
    // Hover sur les sections/groupes
    sectionHover: 'hover:bg-white/10',
    // Lien inactif
    itemInactive: 'text-gray-300 hover:bg-white/5',
    // Lien actif
    activeHighlight: 'bg-white/10 text-white shadow-sm',
    // Barre d’indication active
    indicator: 'bg-[#743669]',
  },

  magenta: {
    name: 'magenta',
    // Gradient plus lumineux, effet "glow" néon
    bg: 'bg-gradient-to-b from-[#743669]/85 via-[#913975]/80 to-[#56335d]/75',
    contentBg: 'linear-gradient(135deg, rgba(116,54,105,0.12), rgba(145,57,117,0.18), rgba(86,51,93,0.14))',
    contentBorder: 'rgba(145,57,117,0.22)',
    accent: '#743669',
    glow: '0 20px 60px rgba(145,57,117,0.16)',
    textPrimary: '#fdf2f8',
    textSecondary: '#f5d0fe',
    textHeading: '#fce7f3',
    textAccent: '#fde68a',
    pageBg: 'linear-gradient(135deg, rgba(116,54,105,0.12), rgba(145,57,117,0.18), rgba(86,51,93,0.14))',
    text: 'text-white',
    sectionHover: 'hover:bg-[#913975]/30',
    itemInactive: 'text-gray-100/80 hover:bg-[#913975]/30',
    activeHighlight: 'bg-[#913975]/45 text-white shadow-sm',
    indicator: 'bg-[#ffb3e6]',
  },

  light: {
    name: 'light',
    // Mode clair corporate
    bg: 'bg-white',
    contentBg: 'linear-gradient(135deg, rgba(255,255,255,0.9), rgba(247,244,255,0.88))',
    contentBorder: 'rgba(116,54,105,0.12)',
    accent: '#913975',
    glow: '0 16px 50px rgba(17, 24, 39, 0.08)',
    textPrimary: '#0f172a',
    textSecondary: '#475569',
    textHeading: '#0b1220',
    textAccent: '#7c3aed',
    pageBg: 'linear-gradient(135deg, #f7f7fb, #f0f4ff 45%, #f9f6ff)',
    text: 'text-[#362f50]',
    sectionHover: 'hover:bg-[#913975]/8',
    itemInactive: 'text-[#362f50] hover:bg-[#913975]/8',
    activeHighlight: 'bg-[#913975]/15 text-[#362f50] shadow-sm',
    indicator: 'bg-[#913975]',
  },
} as const
