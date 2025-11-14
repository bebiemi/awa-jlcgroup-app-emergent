import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Configuration Vite pour Docker
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
    port: 3000,
    strictPort: true,
    allowedHosts: ['.preview.emergentagent.com', '.emergent.host', 'localhost', '127.0.0.1'],
    hmr: {
      ...(process.env.NODE_ENV === 'production' && {
        clientPort: 443,
        protocol: 'wss',
      }),
    },
    proxy: {
      '/api': {
        // Backend principal (port 8001)
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/auth-api': {
        // Auth microservice (port 8000)
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
})
