/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // JLC Official Brand Colors
        jlc: {
          magenta: '#913975',           // Couleur principale Magenta
          'indigo-dark': '#362f50',     // Indigo grisé foncé
          'neon-pink-gray': '#56335d',  // Néon rose grisé
          'neon-pink': '#743669',       // Néon rose
          
          // Palette étendue pour variations
          purple: {
            50: '#faf5f9',
            100: '#f4e9f1',
            200: '#ecd4e6',
            300: '#ddb3d4',
            400: '#c889b9',
            500: '#913975',  // Magenta principal
            600: '#743669',  // Néon rose
            700: '#56335d',  // Néon rose grisé
            800: '#362f50',  // Indigo grisé foncé
            900: '#2a2440',
          },
          accent: {
            yellow: '#FFD700',      // Star yellow (conservé)
            magenta: '#913975',     // Magenta accent
            pink: '#743669',        // Pink accent
          },
        },
        // Keep primary for general use (utilise les couleurs JLC)
        primary: {
          50: '#faf5f9',
          100: '#f4e9f1',
          200: '#ecd4e6',
          300: '#ddb3d4',
          400: '#c889b9',
          500: '#913975',  // Magenta
          600: '#743669',  // Néon rose
          700: '#56335d',  // Néon rose grisé
          800: '#362f50',  // Indigo grisé foncé
          900: '#2a2440',
        },
      },
    },
  },
  plugins: [],
}
