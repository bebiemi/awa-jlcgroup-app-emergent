/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // JLC Brand Colors from logo
        jlc: {
          purple: {
            50: '#f5f3ff',
            100: '#ede9fe',
            200: '#ddd6fe',
            300: '#c4b5fd',
            400: '#a78bfa',
            500: '#7D4CAA',  // Main brand purple
            600: '#583A7B',  // Deep purple
            700: '#4A3A6B',  // Dark blue-purple
            800: '#30274D',  // Very dark
            900: '#1e1b29',
          },
          accent: {
            yellow: '#FFD700',  // Star yellow
            light: '#A28BC2',   // Light purple (GROUP text)
          },
        },
        // Keep primary for general use
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#7D4CAA',
          600: '#583A7B',
          700: '#4A3A6B',
          800: '#30274D',
          900: '#1e1b29',
        },
      },
    },
  },
  plugins: [],
}
