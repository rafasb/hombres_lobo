<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <!-- Navegación común -->
    <NavigationBar 
      :show-admin="auth.isAdmin"
      @navigate="handleNavigation"
    />
    
    <div class="container-lg py-4">
    
    <div class="games-header">
      <div class="profile-header-content">
        <div class="profile-avatar">
          <span class="avatar-text">{{ auth.user?.username?.charAt(0).toUpperCase() || 'U' }}</span>
        </div>
        <h1>Perfil de usuario</h1>
      </div>
    </div>
    
    <div v-if="auth.user" class="profile-content">
      <div class="games-grid">
        <div class="game-card">
          <div class="game-header">
            <h3 class="game-title">Información de Usuario</h3>
          </div>
          
          <div class="game-info">
            <div class="game-detail">
              <span class="detail-label">Usuario:</span>
              <span class="detail-value">{{ auth.user.username }}</span>
            </div>
            
            <div class="game-detail">
              <span class="detail-label">ID:</span>
              <span class="detail-value user-id">{{ auth.user.id }}</span>
            </div>
            
            <div class="game-detail">
              <span class="detail-label">Rol:</span>
              <span class="detail-value" :class="roleClass">{{ roleText }}</span>
            </div>
          </div>
          
          <div class="game-actions">
            <button @click="handleLogout" class="btn btn-leave">
              <span class="btn-icon">🚪</span>
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <div class="empty-icon">❓</div>
      <p>No hay datos de usuario disponibles</p>
      <button @click="navigateToLogin" class="btn btn-join">Iniciar sesión</button>
    </div>
    
    </div>
  </div>
</template>

<script setup lang="ts">
import NavigationBar from '../components/NavigationBar.vue'
import { useProfile } from '../composables/useProfile'
import { useNavigation } from '../composables/useNavigation'

const {
  auth,
  handleLogout,
  roleClass,
  roleText,
  navigateToLogin
} = useProfile()

const { handleNavigation } = useNavigation()
</script>

<style src="../styles/games.css"></style>
