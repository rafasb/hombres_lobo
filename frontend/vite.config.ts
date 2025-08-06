import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/users': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/games': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/login': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/register': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
