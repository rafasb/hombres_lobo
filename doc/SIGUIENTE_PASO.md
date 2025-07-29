# 🔄 FASE 4: Autenticación - Plan de Acción Inmediato

## 🎯 Objetivo de Esta Fase
Implementar el sistema de autenticación completo en el frontend Vue.js 3, incluyendo login, register, gestión de tokens JWT y protección de rutas.

## ⏱️ Tiempo Estimado
**Duración:** 2-3 días  
**Prioridad:** ALTA (Funcionalidad crítica)

## ✅ PRERREQUISITOS COMPLETADOS
- ✅ PrimeVue configurado y funcionando
- ✅ Proxy backend configurado (`/api` → `localhost:8000`)
- ✅ Servicios API base creados con interceptors JWT
- ✅ Comunicación frontend-backend verificada exitosamente

---

## 📋 TAREAS ESPECÍFICAS

### 1️⃣ CREAR STORE DE AUTENTICACIÓN CON PINIA
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 45 minutos  
**Archivo:** `frontend/src/stores/auth.ts`

#### Acción
Crear el store centralizado para gestión de autenticación:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '@/services/api'
import { useRouter } from 'vue-router'

interface User {
  id: number
  username: string
  email: string
}

interface LoginCredentials {
  username: string
  password: string
}

interface RegisterData {
  username: string
  email: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  // Estado reactivo
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isLoading = ref(false)
  const error = ref<string>('')

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Acciones
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiService.post('/auth/login', credentials)
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      localStorage.setItem('access_token', access_token)
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error de autenticación'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    try {
      isLoading.value = true
      error.value = ''
      
      const response = await apiService.post('/auth/register', data)
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      localStorage.setItem('access_token', access_token)
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error de registro'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    // Redirigir a login si es necesario
  }

  const checkAuth = async () => {
    if (token.value) {
      try {
        const response = await apiService.get('/auth/me')
        user.value = response.data
      } catch (err) {
        logout()
      }
    }
  }

  return {
    // Estado
    user,
    token,
    isLoading,
    error,
    // Computed
    isAuthenticated,
    // Acciones
    login,
    register,
    logout,
    checkAuth
  }
})
```

#### Verificación
- [ ] Store se crea sin errores TypeScript
- [ ] Imports de Pinia funcionan correctamente
- [ ] Tipos TypeScript definidos correctamente

---

### 2️⃣ CREAR COMPONENTE DE LOGIN
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 30 minutos  
**Archivo:** `frontend/src/components/auth/LoginForm.vue`

#### Acción
Crear formulario de login con PrimeVue:

```vue
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
```

#### Verificación
- [ ] Componente se renderiza sin errores
- [ ] Campos de formulario funcionan
- [ ] Botón de submit responde
- [ ] Mensajes de error se muestran

---

### 3️⃣ CREAR VISTA DE LOGIN
**Prioridad:** 🟡 ALTA  
**Tiempo:** 15 minutos  
**Archivo:** `frontend/src/views/LoginView.vue`

#### Acción
Crear la vista completa de login:

```vue
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
```

#### Verificación
- [ ] Vista se carga correctamente
- [ ] Estilos se aplican
- [ ] Navegación funciona

---

### 4️⃣ CONFIGURAR RUTAS DE AUTENTICACIÓN
**Prioridad:** 🟡 ALTA  
**Tiempo:** 20 minutos  
**Archivo:** `frontend/src/router/index.ts`

#### Acción
Agregar las rutas de autenticación al router:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Guard de navegación
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
```

#### Verificación
- [ ] Rutas se configuran sin errores
- [ ] Guards de navegación funcionan
- [ ] Redirecciones automáticas operan

---

### 5️⃣ PROBAR FLUJO DE AUTENTICACIÓN
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 30 minutos  

#### Acción
Crear un componente de prueba temporal en App.vue:

```vue
<template>
  <div id="app">
    <div v-if="!authStore.isAuthenticated">
      <LoginView />
    </div>
    <div v-else>
      <h1>¡Autenticado exitosamente!</h1>
      <p>Usuario: {{ authStore.user?.username }}</p>
      <Button @click="authStore.logout" label="Cerrar Sesión" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import Button from 'primevue/button'

const authStore = useAuthStore()

onMounted(() => {
  authStore.checkAuth()
})
</script>
```

#### Verificación
- [ ] Login funciona con credenciales válidas
- [ ] Errores se muestran con credenciales inválidas
- [ ] Token se guarda en localStorage
- [ ] Logout limpia el estado
- [ ] Persistencia funciona al recargar página

---

## 🔧 COMANDOS NECESARIOS

### Verificar Backend Funcionando
```bash
curl http://localhost:8000/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

### Instalar Componentes PrimeVue (si es necesario)
```bash
# Ya están instalados, pero por si acaso:
npm install primevue primeicons
```

---

## ✅ CRITERIOS DE ÉXITO

### ✅ Store Funcionando
- [ ] Estados reactivos actualizándose
- [ ] Acciones ejecutándose sin errores
- [ ] Persistencia en localStorage

### ✅ Componentes Renderizando
- [ ] LoginForm con estilos PrimeVue
- [ ] Validación de campos funcionando
- [ ] Mensajes de error mostrándose

### ✅ Navegación Funcionando
- [ ] Guards protegiendo rutas
- [ ] Redirecciones automáticas
- [ ] Enlaces entre vistas

### ✅ Integración Backend
- [ ] Llamadas API exitosas
- [ ] Manejo de errores HTTP
- [ ] Tokens JWT gestionados correctamente

---

## 🚨 POSIBLES PROBLEMAS Y SOLUCIONES

### Error: Store no definido
**Solución:** Verificar que Pinia esté configurado en main.ts

### Error: Componentes PrimeVue no se cargan
**Solución:** Verificar imports correctos y PrimeVue configurado

### Error: Rutas no funcionan
**Solución:** Verificar que vue-router esté instalado y configurado

### Error: API calls fallan
**Solución:** Verificar que backend esté corriendo en puerto 8000

---

## 📊 PROGRESO ESPERADO

**Al completar esta fase:**
- ✅ Sistema de autenticación completo funcionando
- ✅ Interfaz de login moderna y responsive
- ✅ Gestión de estado centralizada con Pinia
- ✅ Navegación protegida implementada
- ✅ Base sólida para desarrollar gestión de juegos (Fase 5)

**Preparado para:** Fase 5 - Gestión de Juegos

---

> **⚠️ IMPORTANTE:** Esta fase establece la seguridad de toda la aplicación. Cada componente debe probarse minuciosamente antes de continuar.
