import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Open the site at http://campuscustoms.localhost:5174 (*.localhost resolves to this machine).
    port: 5174,
    strictPort: true,
    allowedHosts: ['.localhost'],
    // FastAPI backend (backend/main.py) serves the API and product images in development.
    proxy: {
      '/api': 'http://localhost:8000',
      '/images': 'http://localhost:8000',
    },
  },
})
