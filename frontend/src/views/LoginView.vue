<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <h1>Hombres Lobo</h1>
        <p>Inicia sesión para jugar</p>
      </div>

      <LoginForm />

      <div class="login-footer">
        <p>¿No tienes cuenta?
          <router-link to="/register" class="register-link">
            Regístrate aquí
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/auth/LoginForm.vue'
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  overflow: hidden;
  min-width: 400px;
}

.login-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
  background: #f8f9fa;
}

.login-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.login-footer {
  text-align: center;
  padding: 1rem 2rem 2rem;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
