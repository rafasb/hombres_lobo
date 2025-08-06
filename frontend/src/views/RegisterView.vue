<template>
  <div class="register-container">
    <h2 class="register-title">Registro de usuario</h2>
    <form class="register-form" @submit.prevent="onRegister">
      <input 
        :value="username" 
        @input="$emit('update:username', ($event.target as HTMLInputElement).value)"
        type="text" 
        placeholder="Usuario" 
        required 
      />
      <input 
        :value="email" 
        @input="$emit('update:email', ($event.target as HTMLInputElement).value)"
        type="email" 
        placeholder="Email" 
        required 
      />
      <input 
        :value="password" 
        @input="$emit('update:password', ($event.target as HTMLInputElement).value)"
        type="password" 
        placeholder="Contraseña" 
        required 
      />
      <input 
        :value="confirmPassword" 
        @input="$emit('update:confirmPassword', ($event.target as HTMLInputElement).value)"
        type="password" 
        placeholder="Confirmar contraseña" 
        required 
      />
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
