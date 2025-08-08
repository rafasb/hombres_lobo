<template>
  <div class="profile-container">
    <!-- Navegación común -->
    <NavigationBar 
      :show-admin="auth.isAdmin"
      @navigate="handleNavigation"
    />
    
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
        <button @click="handleLogout" class="logout-btn">
          <span class="btn-icon">🚪</span>
          Cerrar sesión
        </button>
      </div>
    </div>
    
    <div v-else class="profile-empty">
      <div class="empty-icon">❓</div>
      <p>No hay datos de usuario disponibles</p>
      <button @click="navigateToLogin" class="login-btn">Iniciar sesión</button>
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

<style src="../styles/profile.css"></style>
