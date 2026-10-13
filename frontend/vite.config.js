import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/upload': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/match': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/entities': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/results': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/statistics': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/evaluation': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
