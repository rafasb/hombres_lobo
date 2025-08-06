<template>
  <div class="login-container">
    <h2 class="login-title">Iniciar sesión</h2>
    <div v-if="redirected" class="redirect-message">
      Debes iniciar sesión para acceder a tu perfil.
    </div>
    <form class="login-form" @submit.prevent="onLogin">
      <input 
        :value="username"
        @input="$emit('update:username', ($event.target as HTMLInputElement).value)"
        type="text" 
        placeholder="Usuario" 
        required 
      />
      <input 
        :value="password"
        @input="$emit('update:password', ($event.target as HTMLInputElement).value)"
        type="password" 
        placeholder="Contraseña" 
        required 
      />
      <button type="submit" :disabled="loading">
        Entrar
      </button>
    </form>
    <div v-if="error" class="login-error">
      {{ error }}
    </div>
    <div class="login-link">
      <p>
        ¿No tienes cuenta? 
        <button type="button" class="link-button" @click="navigateToRegister">
          Regístrate aquí
        </button>
      </p>
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
