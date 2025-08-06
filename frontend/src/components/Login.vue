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
import '../styles/login.css'

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
