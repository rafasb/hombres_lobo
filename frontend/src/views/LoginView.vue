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

<style src="../assets/styles/login-view.css" scoped></style>
