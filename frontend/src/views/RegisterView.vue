<template>
  <div class="register-view">
    <div class="register-container">
      <div class="register-header">
        <h1>Hombres Lobo</h1>
        <p>Crea tu cuenta para empezar a jugar</p>
      </div>

      <div class="register-form">
        <form @submit.prevent="handleRegister" class="p-fluid">
          <div class="field">
            <label for="username">Usuario</label>
            <InputText
              id="username"
              v-model="registerData.username"
              :class="{ 'p-invalid': !!authStore.error }"
              placeholder="Elige un nombre de usuario"
              required
            />
          </div>

          <div class="field">
            <label for="email">Email</label>
            <InputText
              id="email"
              v-model="registerData.email"
              :class="{ 'p-invalid': !!authStore.error }"
              placeholder="tu@email.com"
              type="email"
              required
            />
          </div>

          <div class="field">
            <label for="password">Contraseña</label>
            <Password
              id="password"
              v-model="registerData.password"
              :class="{ 'p-invalid': !!authStore.error }"
              placeholder="Crea una contraseña segura"
              required
            />
          </div>

          <Message v-if="authStore.error" severity="error" :closable="false">
            {{ authStore.error }}
          </Message>

          <Button
            type="submit"
            label="Crear Cuenta"
            :loading="authStore.isLoading"
            class="w-full"
          />
        </form>
      </div>

      <div class="register-footer">
        <p>¿Ya tienes cuenta?
          <router-link to="/login" class="login-link">
            Inicia sesión aquí
          </router-link>
        </p>
      </div>
    </div>
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

const registerData = ref({
  username: '',
  email: '',
  password: ''
})

const handleRegister = async () => {
  const success = await authStore.register(registerData.value)
  if (success) {
    router.push('/dashboard')
  }
}
</script>

<style src="../assets/styles/register-view.css" scoped></style>
