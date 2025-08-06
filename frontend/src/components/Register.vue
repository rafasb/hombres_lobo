<template>
  <RegisterView 
    :username="username"
    :email="email"
    :password="password"
    :confirm-password="confirmPassword"
    :error="error"
    :success="success"
    :loading="loading"
    @update:username="username = $event"
    @update:email="email = $event"
    @update:password="password = $event"
    @update:confirm-password="confirmPassword = $event"
    @register="onRegister"
  />
</template>

<script setup lang="ts">
import RegisterView from '../views/RegisterView.vue'
import { useRegister } from '../composables/useRegister'
import '../styles/register.css'

const {
  username,
  email,
  password,
  confirmPassword,
  error,
  success,
  loading,
  onRegister
} = useRegister()
</script>
