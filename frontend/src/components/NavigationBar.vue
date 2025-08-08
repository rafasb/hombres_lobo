<template>
  <nav class="main-nav">
    <button class="nav-btn" @click="$emit('navigate', 'games')" :class="{ active: isActive('/partidas') }">
      🎮 Partidas
    </button>
    <button class="nav-btn" @click="$emit('navigate', 'profile')" :class="{ active: isActive('/perfil') }">
      👤 Perfil
    </button>
    <button v-if="showAdmin" class="nav-btn" @click="$emit('navigate', 'admin')" :class="{ active: isActive('/admin') }">
      ⚙️ Admin
    </button>
    <button class="nav-btn logout-nav-btn" @click="handleLogout" title="Cerrar sesión">
      🚪 Salir
    </button>
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
