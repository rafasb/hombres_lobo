<template>
  <div class="min-vh-100" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container-fluid vh-100">
      <div class="row justify-content-center align-items-center h-100">
        <div class="col-12 col-sm-8 col-md-6 col-lg-4">
          <!-- Card principal del registro -->
          <div class="card shadow border-0" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
            <div class="card-body p-4">
              <!-- Header con título -->
              <div class="text-center mb-4">
                <div class="mb-3">
                  <i class="bi bi-person-plus-fill" style="font-size: 3rem; color: var(--bs-primary);"></i>
                </div>
                <h2 class="card-title mb-1" style="color: var(--bs-primary); font-weight: bold;">Hombres Lobo</h2>
                <p class="text-muted small">Registro de usuario</p>
              </div>
              
              <!-- Formulario de registro -->
              <form @submit.prevent="onRegister">
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
                    placeholder="Introduce tu nombre de usuario" 
                    required 
                    autocomplete="username"
                  />
                </div>
                
                <!-- Campo Email -->
                <div class="mb-3">
                  <label class="form-label fw-semibold">
                    <i class="bi bi-envelope me-1"></i>
                    Email
                  </label>
                  <input 
                    :value="email" 
                    @input="$emit('update:email', ($event.target as HTMLInputElement).value)"
                    type="email" 
                    class="form-control form-control-lg"
                    placeholder="Introduce tu email" 
                    required 
                    autocomplete="email"
                  />
                </div>
                
                <!-- Campo Contraseña -->
                <div class="mb-3">
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
                    autocomplete="new-password"
                  />
                </div>
                
                <!-- Campo Confirmar Contraseña -->
                <div class="mb-4">
                  <label class="form-label fw-semibold">
                    <i class="bi bi-lock-fill me-1"></i>
                    Confirmar Contraseña
                  </label>
                  <input 
                    :value="confirmPassword" 
                    @input="$emit('update:confirmPassword', ($event.target as HTMLInputElement).value)"
                    type="password" 
                    class="form-control form-control-lg"
                    placeholder="Confirma tu contraseña" 
                    required 
                    autocomplete="new-password"
                  />
                </div>
                
                <!-- Botón de registro -->
                <div class="d-grid mb-3">
                  <button 
                    type="submit" 
                    :disabled="loading"
                    class="btn btn-lg py-3"
                    :class="loading ? 'btn-secondary' : 'btn-primary'"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-person-plus me-2"></i>
                    {{ loading ? 'Registrando...' : 'Crear Cuenta' }}
                  </button>
                </div>
              </form>
              
              <!-- Mensaje de error -->
              <div v-if="error" class="alert alert-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                <strong>Error:</strong> {{ error }}
              </div>
              
              <!-- Mensaje de éxito -->
              <div v-if="success" class="alert alert-success">
                <i class="bi bi-check-circle me-2"></i>
                <strong>¡Éxito!</strong> {{ success }}
              </div>
              
              <!-- Enlace de login -->
              <hr class="my-4">
              <div class="text-center">
                <p class="text-muted mb-2">¿Ya tienes una cuenta?</p>
                <router-link to="/login" class="btn btn-outline-primary">
                  <i class="bi bi-box-arrow-in-right me-1"></i>
                  Iniciar Sesión
                </router-link>
              </div>
            </div>
          </div>
          
          <!-- Footer informativo -->
          <div class="text-center mt-3">
            <small class="text-white">
              <i class="bi bi-shield-check me-1"></i>
              Únete a la comunidad de Hombres Lobo
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  username: string
  email: string
  password: string
  confirmPassword: string
  error: string
  success: string
  loading: boolean
}

interface Emits {
  (e: 'update:username', value: string): void
  (e: 'update:email', value: string): void
  (e: 'update:password', value: string): void
  (e: 'update:confirmPassword', value: string): void
  (e: 'register'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const onRegister = () => {
  emit('register')
}
</script>
