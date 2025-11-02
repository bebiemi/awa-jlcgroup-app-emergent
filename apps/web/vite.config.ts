import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

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
    hmr: {
      clientPort: 443,
      protocol: 'wss',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/auth-api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth-api/, '/api'),
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
