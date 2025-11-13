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
    // Allow dynamic preview domains (forked apps get different subdomains)
    allowedHosts: ['.preview.emergentagent.com', '.emergent.host', 'localhost', '127.0.0.1'],
    hmr: {
      // Use environment variable to determine HMR config
      // For local dev, HMR will use default settings (http://localhost:3000)
      ...(process.env.NODE_ENV === 'production' && {
        clientPort: 443,
        protocol: 'wss',
      }),
    },
    proxy: {
      // ALL /api requests go to backend (port 8001)
      // Backend has proxy routes to forward to auth-microservice (port 8000) as needed
      // This architecture works in both dev and production/preview environments
      '/api': {
        target: 'http://jlc-api:8001',
        changeOrigin: true,
        secure: false,
        ws: true,
        // Force HTTP/1.1 to avoid ALPN negotiation errors
        agent: new http.Agent({ keepAlive: true }),
      },
      // /auth-api also goes to backend (legacy compatibility)
      '/auth-api': {
        target: 'http://jlc-api:8001',
        changeOrigin: true,
        secure: false,
        ws: true,
        // Force HTTP/1.1 to avoid ALPN negotiation errors
        agent: new http.Agent({ keepAlive: true }),
      },
    },
  },
  // Preview configuration (for production builds)
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
})
