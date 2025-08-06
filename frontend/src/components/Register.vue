<template>
  <div class="register-container">
    <h2 class="register-title">Registro de usuario</h2>
    <form class="register-form" @submit.prevent="onRegister">
      <input v-model="username" type="text" placeholder="Usuario" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Contraseña" required />
      <input v-model="confirmPassword" type="password" placeholder="Confirmar contraseña" required />
      <button type="submit" :disabled="loading">Registrarse</button>
    </form>
    <div v-if="error" class="register-error">{{ error }}</div>
    <div v-if="success" class="register-success">{{ success }}</div>
    <div class="register-link">
      <p>¿Ya tienes cuenta? <router-link to="/login">Inicia sesión aquí</router-link></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../services/registerService'
import '../styles/register.css'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)
const router = useRouter()

const onRegister = async () => {
  error.value = ''
  success.value = ''
  
  // Validaciones del lado del cliente
  if (password.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  
  if (password.value.length < 6) {
    error.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }
  
  loading.value = true
  const result = await register(username.value, email.value, password.value)
  
  if (result && result.success) {
    success.value = 'Usuario registrado correctamente. Redirigiendo al login...'
    // Redirigir al login después de 2 segundos
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } else if (result && result.error) {
    error.value = result.error
  }
  loading.value = false
}
</script>
