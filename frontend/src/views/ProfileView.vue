<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
  <!-- Navegación común -->
  <PageWithNav :show-admin="isAdmin" @navigate="handleNavigation">

  <div class="mobile-container">
      <div class="container-fluid">
        <div class="row justify-content-center">
          <div class="col-12 col-sm-8 col-md-6">
            <!-- Header -->
            <div class="card mb-4" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
              <div class="card-body d-flex align-items-center gap-3">
                <div class="profile-avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" 
                     style="width: 60px; height: 60px; font-size: 24px; font-weight: bold;">
                  {{ username?.charAt(0).toUpperCase() || 'U' }}
                </div>
                <h1 class="mb-0 fw-bold text-dark">
                  <i class="bi bi-person-circle me-2"></i>
                  Perfil de usuario
                </h1>
              </div>
            </div>
            
            <div v-if="user">
              <div class="card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
                <div class="card-header border-0 pb-2" style="background: transparent;">
                  <h5 class="card-title mb-0 fw-bold text-dark">
                    <i class="bi bi-info-circle me-2"></i>
                    Información de Usuario
                  </h5>
                </div>
                
                <div class="card-body pt-2">
                  <div class="mb-3">
                    <div class="d-flex justify-content-between mb-3 p-2 bg-light rounded">
                      <span class="text-muted fw-semibold">Usuario:</span>
                      <span class="fw-bold">{{ username }}</span>
                    </div>
                    
                    <div class="d-flex justify-content-between mb-3 p-2 bg-light rounded">
                      <span class="text-muted fw-semibold">ID:</span>
                      <span class="fw-bold font-monospace text-primary">{{ user.id }}</span>
                    </div>
                    
                    <div class="d-flex justify-content-between mb-3 p-2 bg-light rounded">
                      <span class="text-muted fw-semibold">Rol:</span>
                      <span class="badge fs-6" :class="roleInfo.class">{{ roleInfo.text }}</span>
                    </div>
                  </div>
                  
                  <div class="d-grid">
                    <button @click="goToLogin(true)" class="btn btn-danger btn-lg d-flex align-items-center justify-content-center gap-2"
                            style="border-radius: 10px;">
                      <i class="bi bi-box-arrow-right"></i>
                      Cerrar sesión
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center">
              <div class="card" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: none; border-radius: 15px;">
                <div class="card-body py-5">
                  <i class="bi bi-question-circle display-1 text-muted mb-3"></i>
                  <h4 class="text-muted mb-3">No hay datos de usuario disponibles</h4>
                  <button @click="goToLogin(true)" class="btn btn-primary btn-lg d-flex align-items-center gap-2 mx-auto"
                          style="border-radius: 25px;">
                    <i class="bi bi-box-arrow-in-right"></i>
                    Iniciar sesión
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </PageWithNav>
  </div>
</template>

<script setup lang="ts">
import PageWithNav from '../components/PageWithNav.vue'
import { useProfile } from '../composables/useProfile'
import { useNavigation } from '../composables/useNavigation'

const {
  user,
  username,
  isAdmin,
  roleInfo,
  goToLogin
} = useProfile()

const { handleNavigation } = useNavigation()
</script>


