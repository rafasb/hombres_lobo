<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container-fluid vh-100">
    <div class="row justify-content-center align-items-center h-100">
      <div class="col-12 col-sm-8 col-md-6 col-lg-4">
        <!-- Card principal del login -->
        <div class="card shadow border-0">
          <div class="card-body p-4">
            <!-- Header con título -->
            <div class="text-center mb-4">
              <div class="mb-3">
                <i class="bi bi-person-circle" style="font-size: 3rem; color: var(--bs-primary);"></i>
              </div>
              <h2 class="card-title mb-1" style="color: var(--bs-primary); font-weight: bold;">Hombres Lobo</h2>
              <p class="text-muted small">Iniciar sesión</p>
            </div>

            <!-- Mensaje de redirección -->
            <div v-if="redirected" class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Debes iniciar sesión para acceder a tu perfil.
            </div>
            
            <!-- Formulario de login -->
            <form @submit.prevent="onLogin">
              <!-- Campo Usuario -->
              <div class="mb-3">
                <label class="form-label fw-semibold">
                  <i class="bi bi-person me-1"></i>
                  Usuario
                </label>
                <input 
                  :value="username"
                  @input="$emit('update:username', ($event.target as HTMLInputElement).value)"
                  type="text" 
                  class="form-control form-control-lg"
                  placeholder="Introduce tu usuario" 
                  required 
                  autocomplete="username"
                />
              </div>
              
              <!-- Campo Contraseña -->
              <div class="mb-4">
                <label class="form-label fw-semibold">
                  <i class="bi bi-lock me-1"></i>
                  Contraseña
                </label>
                <input 
                  :value="password"
                  @input="$emit('update:password', ($event.target as HTMLInputElement).value)"
                  type="password" 
                  class="form-control form-control-lg"
                  placeholder="Introduce tu contraseña" 
                  required 
                  autocomplete="current-password"
                />
              </div>
              
              <!-- Botón de envío -->
              <div class="d-grid mb-3">
                <button 
                  type="submit" 
                  :disabled="loading"
                  class="btn btn-lg py-3"
                  :class="loading ? 'btn-secondary' : 'btn-primary'"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                  {{ loading ? 'Conectando...' : 'Iniciar Sesión' }}
                </button>
              </div>
            </form>
            
            <!-- Mensaje de error -->
            <div v-if="error" class="alert alert-danger">
              <i class="bi bi-exclamation-triangle me-2"></i>
              <strong>Error:</strong> {{ error }}
            </div>
            
            <!-- Enlace de registro -->
            <hr class="my-4">
            <div class="text-center">
              <p class="text-muted mb-2">¿Primera vez jugando?</p>
              <button 
                type="button" 
                class="btn btn-outline-primary"
                @click="navigateToRegister"
              >
                <i class="bi bi-person-plus me-1"></i>
                Crear cuenta nueva
              </button>
            </div>
          </div>
        </div>
        
        <!-- Footer informativo -->
        <div class="text-center mt-3">
          <small class="text-muted">
            <i class="bi bi-shield-check me-1"></i>
            Aplicación segura para jugar Hombres Lobo
          </small>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props para recibir los datos y métodos del composable
interface Props {
  username: string
  password: string
  error: string
  loading: boolean
  redirected: boolean
}

interface Emits {
  (e: 'update:username', value: string): void
  (e: 'update:password', value: string): void
  (e: 'login'): void
  (e: 'navigateToRegister'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// Métodos que emiten eventos al padre
const onLogin = () => emit('login')
const navigateToRegister = () => emit('navigateToRegister')
</script>
