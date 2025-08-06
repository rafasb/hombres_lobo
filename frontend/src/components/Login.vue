<template>
  <div class="login-container">
    <h2 class="login-title">Iniciar sesión</h2>
    <div v-if="redirected" class="redirect-message">Debes iniciar sesión para acceder a tu perfil.</div>
    <form class="login-form" @submit.prevent="onLogin">
      <input v-model="username" type="text" placeholder="Usuario" required />
      <input v-model="password" type="password" placeholder="Contraseña" required />
      <button type="submit" :disabled="loading">Entrar</button>
    </form>
    <div v-if="error" class="login-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { login } from '../services/authService'
import '../styles/login.css'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const redirected = ref(false)
const router = useRouter()
const auth = useAuthStore()

if (window.history.state && window.history.state.redirected) {
  redirected.value = true
}

const onLogin = async () => {
  error.value = ''
  loading.value = true
  const result = await login(username.value, password.value)
  if (result && result.access_token) {
    router.push('/perfil')
  } else if (result && result.error) {
    error.value = result.error
    auth.logout()
  }
  loading.value = false
}
</script>
