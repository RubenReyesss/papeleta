import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // En desarrollo, redirige /api al backend para evitar CORS
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Timeout generoso para el streaming del modelo en CPU
        timeout: 300000,
        proxyTimeout: 300000,
      },
    },
  },
})
