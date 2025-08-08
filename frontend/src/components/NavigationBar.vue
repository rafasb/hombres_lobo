<template>
  <nav class="navbar navbar-expand-sm p-3" 
       style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2);">
    <div class="container-fluid">
      <!-- Brand/Logo -->
      <span class="navbar-brand mb-0 h5 text-white fw-bold d-none d-sm-block">
        <i class="bi bi-moon-stars-fill me-2"></i>
        Hombres Lobo
      </span>
      
      <!-- Navigation buttons -->
      <div class="navbar-nav flex-row gap-2 flex-grow-1 justify-content-start justify-content-sm-center">
        <!-- Botón Partidas -->
        <button 
          @click="$emit('navigate', 'games')" 
          :class="[
            'btn btn-sm px-3 py-2 rounded-pill fw-medium transition-all',
            isActive('/partidas') 
              ? 'btn-warning shadow' 
              : 'btn-outline-light'
          ]"
          style="backdrop-filter: blur(5px);"
        >
          <i class="bi bi-controller me-1"></i>
          <span class="d-none d-sm-inline">Partidas</span>
          <span class="d-sm-none">🎮</span>
        </button>
        
        <!-- Botón Perfil -->
        <button 
          @click="$emit('navigate', 'profile')" 
          :class="[
            'btn btn-sm px-3 py-2 rounded-pill fw-medium',
            isActive('/perfil') 
              ? 'btn-warning shadow' 
              : 'btn-outline-light'
          ]"
          style="backdrop-filter: blur(5px);"
        >
          <i class="bi bi-person-circle me-1"></i>
          <span class="d-none d-sm-inline">Perfil</span>
          <span class="d-sm-none">👤</span>
        </button>
        
        <!-- Botón Admin (condicional) -->
        <button 
          v-if="showAdmin"
          @click="$emit('navigate', 'admin')" 
          :class="[
            'btn btn-sm px-3 py-2 rounded-pill fw-medium',
            isActive('/admin') 
              ? 'btn-warning shadow' 
              : 'btn-outline-light'
          ]"
          style="backdrop-filter: blur(5px);"
        >
          <i class="bi bi-gear-fill me-1"></i>
          <span class="d-none d-sm-inline">Admin</span>
          <span class="d-sm-none">⚙️</span>
        </button>
      </div>
      
      <!-- Botón Logout -->
      <div class="navbar-nav">
        <button 
          @click="handleLogout" 
          class="btn btn-danger btn-sm px-3 py-2 rounded-pill fw-medium shadow-sm"
          title="Cerrar sesión"
          style="backdrop-filter: blur(5px);"
        >
          <i class="bi bi-box-arrow-right me-1"></i>
          <span class="d-none d-sm-inline">Salir</span>
          <span class="d-sm-none">🚪</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

interface Props {
  showAdmin?: boolean
}

interface Emits {
  (e: 'navigate', view: string): void
}

defineProps<Props>()
defineEmits<Emits>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isActive = (path: string) => {
  return route.path === path
}

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>
