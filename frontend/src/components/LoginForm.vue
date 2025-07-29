<template>
  <div class="card">
    <h2>🐺 Iniciar Sesión</h2>
    <p class="subtitle">Ingresa a tu partida de Hombres Lobo</p>
    
    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">Usuario:</label>
        <input 
          id="username"
          v-model="username" 
          type="text" 
          required 
          placeholder="Ingresa tu usuario"
        />
      </div>
      
      <div class="form-group">
        <label for="password">Contraseña:</label>
        <input 
          id="password"
          v-model="password" 
          type="password" 
          required 
          placeholder="Ingresa tu contraseña"
        />
      </div>
      
      <button type="submit" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Iniciando...' : 'Iniciar Sesión' }}
      </button>
    </form>

    <div class="register-link">
      <p>¿No tienes cuenta?</p>
      <button @click="showRegister = !showRegister" class="btn btn-secondary">
        {{ showRegister ? 'Volver a Iniciar Sesión' : 'Registrarse' }}
      </button>
    </div>

    <!-- Register Form -->
    <form v-if="showRegister" @submit.prevent="register" class="register-form">
      <h3>Crear Cuenta</h3>
      
      <div class="form-group">
        <label for="reg-username">Usuario:</label>
        <input 
          id="reg-username"
          v-model="registerData.username" 
          type="text" 
          required 
          placeholder="Elige un usuario"
        />
      </div>
      
      <div class="form-group">
        <label for="reg-email">Email:</label>
        <input 
          id="reg-email"
          v-model="registerData.email" 
          type="email" 
          required 
          placeholder="tu@email.com"
        />
      </div>
      
      <div class="form-group">
        <label for="reg-password">Contraseña:</label>
        <input 
          id="reg-password"
          v-model="registerData.password" 
          type="password" 
          required 
          placeholder="Elige una contraseña"
        />
      </div>
      
      <button type="submit" class="btn btn-primary" :disabled="loading">
        {{ loading ? 'Registrando...' : 'Registrarse' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { authAPI } from '../services/api.js'

const emit = defineEmits(['login'])

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showRegister = ref(false)

const registerData = ref({
  username: '',
  email: '',
  password: ''
})

const login = async () => {
  if (!username.value || !password.value) {
    error.value = 'Por favor, completa todos los campos'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await authAPI.login(username.value, password.value)
    
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
      
      // Create user data object
      const userData = {
        username: username.value,
        token: response.data.access_token
      }
      localStorage.setItem('user_data', JSON.stringify(userData))
      
      emit('login', userData)
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = err.response?.data?.detail || 'Error al iniciar sesión'
  } finally {
    loading.value = false
  }
}

const register = async () => {
  if (!registerData.value.username || !registerData.value.email || !registerData.value.password) {
    error.value = 'Por favor, completa todos los campos'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authAPI.register(
      registerData.value.username, 
      registerData.value.email, 
      registerData.value.password
    )
    
    error.value = ''
    showRegister.value = false
    
    // Auto-login after registration
    username.value = registerData.value.username
    password.value = registerData.value.password
    await login()
    
  } catch (err) {
    console.error('Register error:', err)
    error.value = err.response?.data?.detail || 'Error al registrarse'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
h2 {
  text-align: center;
  margin-bottom: 0.5rem;
  color: #333;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.register-link p {
  margin-bottom: 0.5rem;
  color: #666;
}

.register-form {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.register-form h3 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>