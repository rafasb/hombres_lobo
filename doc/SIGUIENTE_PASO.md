# 🔄 FASE 3: Configuraciones Base - Plan de Acción Inmediato

## 🎯 Objetivo de Esta Fase
Configurar el frontend Vue.js 3 para comunicarse con el backend FastAPI y establecer la base para el desarrollo de funcionalidades.

## ⏱️ Tiempo Estimado
**Duración:** 2-3 días  
**Prioridad:** ALTA (Bloquea siguientes fases)

---

## 📋 TAREAS ESPECÍFICAS

### 1️⃣ CONFIGURAR PRIMEVUE EN MAIN.TS
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 30 minutos  
**Archivo:** `frontend/src/main.ts`

#### Acción
Modificar el archivo para importar y configurar PrimeVue:

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

import App from './App.vue'
import router from './router'

// CSS de PrimeVue
import 'primevue/resources/themes/aura-light-green/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue)

app.mount('#app')
```

#### Verificación
- [ ] Frontend sigue funcionando en puerto 5173
- [ ] Estilos PrimeVue se cargan correctamente
- [ ] No hay errores en consola del navegador

---

### 2️⃣ CONFIGURAR PROXY BACKEND EN VITE.CONFIG.TS
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 15 minutos  
**Archivo:** `frontend/vite.config.ts`

#### Acción
Modificar la configuración de Vite para proxificar llamadas al backend:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

#### Verificación
- [ ] Reiniciar dev server
- [ ] Probar que `http://localhost:5173/api/docs` redirecciona a backend
- [ ] Verificar comunicación frontend-backend

---

### 3️⃣ CREAR SERVICIOS API BASE
**Prioridad:** 🟡 ALTA  
**Tiempo:** 45 minutos  
**Archivo:** `frontend/src/services/api.ts`

#### Acción
Crear el servicio base para comunicación HTTP:

```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios'

// Configuración base de Axios
const api: AxiosInstance = axios.create({
  baseURL: '/api', // Usa el proxy configurado en Vite
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para requests (agregar token JWT si existe)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para responses (manejo de errores)
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado, redirigir a login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Funciones de utilidad
export const apiService = {
  get: <T>(url: string) => api.get<T>(url),
  post: <T>(url: string, data?: any) => api.post<T>(url, data),
  put: <T>(url: string, data?: any) => api.put<T>(url, data),
  delete: <T>(url: string) => api.delete<T>(url),
}

export default api
```

#### Verificación
- [ ] Archivo se crea sin errores TypeScript
- [ ] Imports de Axios funcionan correctamente

---

### 4️⃣ CREAR ESTRUCTURA DE CARPETAS
**Prioridad:** 🟡 ALTA  
**Tiempo:** 15 minutos  

#### Acción
Crear la estructura de carpetas estándar:

```bash
mkdir -p frontend/src/components/common
mkdir -p frontend/src/components/auth
mkdir -p frontend/src/components/games
mkdir -p frontend/src/components/game
mkdir -p frontend/src/services
mkdir -p frontend/src/types
mkdir -p frontend/src/composables
mkdir -p frontend/src/utils
```

#### Verificación
- [ ] Todas las carpetas se crean correctamente
- [ ] Estructura visible en VS Code

---

### 5️⃣ PROBAR COMUNICACIÓN FRONTEND-BACKEND
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 30 minutos  

#### Acción
Crear un componente de prueba para verificar la comunicación:

**Archivo:** `frontend/src/components/common/ApiTest.vue`
```vue
<template>
  <div class="api-test">
    <h3>Test de Comunicación API</h3>
    <Button @click="testConnection" label="Probar Conexión" />
    <div v-if="result" class="result">
      <p><strong>Estado:</strong> {{ result.status }}</p>
      <p><strong>Respuesta:</strong> {{ result.data }}</p>
    </div>
    <div v-if="error" class="error">
      <p><strong>Error:</strong> {{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import { apiService } from '@/services/api'

const result = ref<any>(null)
const error = ref<string>('')

const testConnection = async () => {
  try {
    error.value = ''
    const response = await apiService.get('/docs')
    result.value = {
      status: 'Conexión exitosa',
      data: 'Backend respondiendo correctamente'
    }
  } catch (err: any) {
    error.value = err.message || 'Error de conexión'
    result.value = null
  }
}
</script>

<style scoped>
.api-test {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin: 1rem;
}
.result {
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #d4edda;
  border-radius: 4px;
}
.error {
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #f8d7da;
  border-radius: 4px;
}
</style>
```

#### Integrar en App.vue temporalmente:
```vue
<template>
  <div id="app">
    <ApiTest />
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import ApiTest from '@/components/common/ApiTest.vue'
</script>
```

#### Verificación
- [ ] Componente se renderiza sin errores
- [ ] Botón responde al click
- [ ] Comunicación con backend funciona
- [ ] Errores se manejan correctamente

---

## 🔧 COMANDOS NECESARIOS

### Preparar Entorno
```bash
cd /home/rafasb/desarrollo/hombres_lobo/frontend
npm run dev
```

### Verificar Backend
```bash
cd /home/rafasb/desarrollo/hombres_lobo/backend
# Activar entorno virtual si es necesario
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Probar Conexión
```bash
# En otra terminal
curl http://localhost:8000/docs
curl http://localhost:5173/api/docs
```

---

## ✅ CRITERIOS DE ÉXITO

### ✅ PrimeVue Funcionando
- [ ] Estilos PrimeVue cargados
- [ ] Componentes PrimeVue disponibles
- [ ] Tema Aura Light Green aplicado

### ✅ Comunicación Establecida
- [ ] Proxy funcionando `/api` → backend
- [ ] Axios configurado correctamente
- [ ] Interceptors JWT listos

### ✅ Estructura Lista
- [ ] Carpetas creadas
- [ ] Servicios base funcionando
- [ ] Test de comunicación exitoso

---

## 🚨 POSIBLES PROBLEMAS Y SOLUCIONES

### Error: PrimeVue no se carga
**Solución:** Verificar que todas las dependencias estén instaladas:
```bash
npm install primevue primeicons primeflex
```

### Error: Proxy no funciona
**Solución:** Verificar que backend esté ejecutándose en puerto 8000:
```bash
curl http://localhost:8000/docs
```

### Error: CORS
**Solución:** Verificar configuración CORS en backend incluye puerto 5173

### Error: TypeScript
**Solución:** Verificar tipos en `tsconfig.json` y reinstalar dependencias

---

## 📊 PROGRESO ESPERADO

**Al completar esta fase:**
- ✅ Frontend y backend comunicándose correctamente
- ✅ PrimeVue configurado y funcionando
- ✅ Base sólida para desarrollar autenticación (Fase 4)
- ✅ Estructura de proyecto profesional establecida

**Preparado para:** Fase 4 - Implementación de autenticación JWT

---

> **⚠️ IMPORTANTE:** Esta fase es crítica. Sin completar estos pasos, las siguientes fases no pueden avanzar. Cada tarea debe verificarse antes de continuar.
