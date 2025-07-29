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

<style scoped>
.register-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  overflow: hidden;
  min-width: 400px;
}

.register-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
  background: #f8f9fa;
}

.register-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.register-form {
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

.register-footer {
  text-align: center;
  padding: 1rem 2rem 2rem;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
}

.login-link:hover {
  text-decoration: underline;
}
</style>
