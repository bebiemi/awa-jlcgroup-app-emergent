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
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/auth-api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
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
