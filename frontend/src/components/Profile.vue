<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="profile-avatar">
        <span class="avatar-text">{{ auth.user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
      </div>
      <h2>Perfil de usuario</h2>
    </div>
    
    <div v-if="auth.user" class="profile-content">
      <div class="profile-info">
        <div class="info-card">
          <div class="info-label">Usuario</div>
          <div class="info-value">{{ auth.user.username }}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">ID</div>
          <div class="info-value user-id">{{ auth.user.id }}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Rol</div>
          <div class="info-value" :class="roleClass">{{ roleText }}</div>
        </div>
      </div>
      
      <div class="profile-actions">
        <button v-if="auth.isAdmin" @click="router.push('/admin')" class="admin-btn">
          <span class="btn-icon">⚙️</span>
          Administración de usuarios
        </button>
        <button @click="handleLogout" class="logout-btn">
          <span class="btn-icon">🚪</span>
          Cerrar sesión
        </button>
      </div>
    </div>
    
    <div v-else class="profile-empty">
      <div class="empty-icon">❓</div>
      <p>No hay datos de usuario disponibles</p>
      <button @click="router.push('/login')" class="login-btn">Iniciar sesión</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const auth = useAuthStore()

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

const roleClass = computed(() => {
  return auth.user?.role === 'admin' ? 'role-admin' : 'role-player'
})

const roleText = computed(() => {
  return auth.user?.role === 'admin' ? 'Administrador' : 'Jugador'
})
</script>

<style src="../styles/profile.css"></style>
