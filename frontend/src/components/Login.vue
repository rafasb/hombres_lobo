<template>
  <LoginView
    :username="username"
    :password="password"
    :error="error"
    :loading="loading"
    :redirected="redirected"
    @update:username="username = $event"
    @update:password="password = $event"
    @login="onLogin"
    @navigateToRegister="navigateToRegister"
  />
</template>

<script setup lang="ts">
import LoginView from '../views/LoginView.vue'
import { useLogin } from '../composables/useLogin'
// Ya no necesitamos importar el CSS específico, usamos Bootstrap

// Usar el composable
const {
  username,
  password,
  error,
  loading,
  redirected,
  onLogin,
  navigateToRegister
} = useLogin()
</script>
