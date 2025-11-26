import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import http from 'http'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3001,  // Changed to 3001 to allow nginx to listen on 3000
    strictPort: true,
    // Permet d'override la cible API en local (évite le 503 si jlc-api est introuvable hors Docker)
    // Exemple: VITE_API_PROXY_TARGET=http://localhost:8001
    proxy: (() => {
      const apiTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8001'
      const agent = new http.Agent({ keepAlive: true })
      return {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
          ws: true,
          agent,
        },
        '/auth-api': {
          target: apiTarget,
          changeOrigin: true,
          secure: false,
          ws: true,
          agent,
        },
      }
    })(),
    // Allow dynamic preview domains (forked apps get different subdomains)
    allowedHosts: ['.preview.emergentagent.com', '.emergent.host', 'localhost', '127.0.0.1'],
    // Fix for ENOSPC error in Kubernetes containers (file watcher limit)
    watch: {
      usePolling: true,
      interval: 1000,
    },
    hmr: {
      // Use environment variable to determine HMR config
      // For local dev, HMR will use default settings (http://localhost:3000)
      ...(process.env.NODE_ENV === 'production' && {
        clientPort: 443,
        protocol: 'wss',
      }),
    },
  },
  // Preview configuration (for production builds)
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
})
