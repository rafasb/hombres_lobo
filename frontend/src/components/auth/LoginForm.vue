<template>
  <div class="login-form">
    <form @submit.prevent="handleLogin" class="p-fluid">
      <div class="field">
        <label for="username">Usuario</label>
        <InputText
          id="username"
          v-model="credentials.username"
          :class="{ 'p-invalid': !!authStore.error }"
          placeholder="Ingresa tu usuario"
          required
        />
      </div>

      <div class="field">
        <label for="password">Contraseña</label>
        <Password
          id="password"
          v-model="credentials.password"
          :class="{ 'p-invalid': !!authStore.error }"
          placeholder="Ingresa tu contraseña"
          :feedback="false"
          required
        />
      </div>

      <Message v-if="authStore.error" severity="error" :closable="false">
        {{ authStore.error }}
      </Message>

      <Button
        type="submit"
        label="Iniciar Sesión"
        :loading="authStore.isLoading"
        class="w-full"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  const success = await authStore.login(credentials.value)
  if (success) {
    router.push('/dashboard') // Redirigir después del login
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
}

.field {
  margin-bottom: 1rem;
}

label {
  font-weight: bold;
  margin-bottom: 0.5rem;
  display: block;
}
</style>
