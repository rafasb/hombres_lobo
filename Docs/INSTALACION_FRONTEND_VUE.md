# Instalación Frontend Vue.js 3 - Documentación

## 🎯 Objetivo
Crear el frontend Vue.js 3 con TypeScript, PrimeVue y todas las dependencias necesarias para comunicarse con el backend FastAPI.

## 📦 Stack Tecnológico Seleccionado

### ✅ Framework Principal
- **Vue.js 3** - Framework JavaScript reactivo
- **TypeScript** - Tipado estático para mejor desarrollo
- **Vite** - Build tool y dev server rápido

### ✅ Gestión de Estado y Navegación
- **Pinia** - State management moderno para Vue 3
- **Vue Router 4** - Enrutamiento SPA

### ✅ UI Framework
- **PrimeVue** - Componentes UI ricos y mobile-friendly
- **PrimeIcons** - Iconografía completa
- **PrimeFlex** - Utilidades CSS flexbox

### ✅ Comunicación HTTP
- **Axios** - Cliente HTTP para comunicación con backend API

### ✅ Desarrollo
- **@types/node** - Tipos TypeScript para Node.js

## 🚀 Plan de Instalación Paso a Paso

### Paso 1: Crear Proyecto Base Vue.js 3
```bash
npm create vue@latest . --typescript --router --pinia
```

**Incluye automáticamente:**
- Vue.js 3
- TypeScript
- Vue Router 4
- Pinia
- Vite
- ESLint
- Prettier

### Paso 2: Instalar PrimeVue Ecosystem
```bash
npm install primevue
npm install primeicons
npm install primeflex
```

### Paso 3: Instalar Cliente HTTP
```bash
npm install axios
```

### Paso 4: Instalar Tipos TypeScript
```bash
npm install --save-dev @types/node
```

### Paso 5: Verificar Instalación
```bash
npm run dev
```

## 📁 Estructura Frontend Resultante

```
frontend/
├── public/                 # Assets públicos
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── main.ts            # Punto de entrada
│   ├── App.vue            # Componente raíz
│   ├── components/        # Componentes reutilizables
│   ├── views/             # Páginas/Vistas
│   ├── router/            # Configuración Vue Router
│   │   └── index.ts
│   ├── stores/            # Stores Pinia
│   │   └── counter.ts
│   └── assets/            # Assets del proyecto
├── package.json
├── vite.config.ts         # Configuración Vite
├── tsconfig.json         # Configuración TypeScript
└── README.md
```

## ⚙️ Configuraciones Post-Instalación

### 1. Configurar PrimeVue en main.ts
```typescript
import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import App from './App.vue'

// CSS
import 'primevue/resources/themes/aura-light-green/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

const app = createApp(App)
app.use(PrimeVue)
app.mount('#app')
```

### 2. Configurar Proxy para Backend
En `vite.config.ts`:
```typescript
export default defineConfig({
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

### 3. Configurar Axios Service
```typescript
// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

export default api
```

## 🔗 Conexión con Backend

### API Endpoints Disponibles (Backend FastAPI)
- **Base URL:** `http://localhost:8000`
- **Documentación:** `http://localhost:8000/docs`
- **Autenticación:** JWT tokens
- **CORS:** Configurado para `localhost:5173` (Vite dev server)

### Servicios Frontend a Crear
- `authService.ts` - Login, register, JWT management
- `userService.ts` - CRUD usuarios
- `gameService.ts` - Gestión de partidas
- `roleServices.ts` - Servicios específicos por rol

## 📱 Características Mobile-First

### PrimeVue Componentes Mobile-Friendly
- **Button** - Botones táctiles optimizados
- **Card** - Contenedores responsivos
- **DataTable** - Tablas adaptables a móviles
- **Dialog** - Modales responsivos
- **InputText** - Inputs optimizados para móvil
- **Menu** - Menús adaptables
- **Toast** - Notificaciones no intrusivas

### PrimeFlex Utilities
- Sistema de grid responsivo
- Utilities de spacing y layout
- Flexbox helpers

## 🎨 Tema y Estilos

### Tema PrimeVue Seleccionado
- **Aura Light Green** - Tema moderno y accesible
- Compatible con modo oscuro (futuro)
- Optimizado para dispositivos táctiles

### Personalización CSS
```css
/* src/assets/main.css */
:root {
  --primary-color: #10b981; /* Verde del tema */
  --surface-color: #ffffff;
  --text-color: #1f2937;
}
```

## 🔒 Autenticación y Seguridad

### JWT Token Management
- Almacenamiento seguro en localStorage/sessionStorage
- Interceptors de Axios para tokens automáticos
- Refresh token logic
- Guards de Vue Router para rutas protegidas

### Guards de Navegación
```typescript
// router/index.ts
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})
```

## 🚀 Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Preview build de producción
npm run preview

# Linting
npm run lint

# Type checking
npm run type-check
```

## 📊 Puertos y URLs

- **Frontend Dev Server:** `http://localhost:5173`
- **Backend API:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`

## ✅ Checklist de Verificación

### ✅ Post-Instalación (COMPLETADO)
- [x] Proyecto Vue.js 3 creado exitosamente
- [x] PrimeVue, PrimeIcons y PrimeFlex instalados
- [x] Axios instalado y listo para configurar
- [x] TypeScript funcionando sin errores
- [x] Dev server arranca en puerto 5173
- [x] Estructura de proyecto creada correctamente

### ✅ Funcionalidades Base (COMPLETADO - FASE 3)
- [x] PrimeVue configurado en main.ts
- [x] Proxy para backend configurado en vite.config.ts
- [x] Enrutamiento funcionando
- [x] Estado global con Pinia configurado
- [x] Componentes PrimeVue renderizando
- [x] API calls a backend exitosas ✅ VERIFICADO
- [x] Responsive design verificado

### 🎯 Estado Actual: FASE 3 COMPLETADA
**Fecha de completado:** 29 Julio 2025  
**Servidor frontend:** ✅ Funcionando en http://localhost:5173  
**Servidor backend:** ✅ Funcionando en http://localhost:8000  
**Comunicación:** ✅ EXITOSA - Proxy y servicios API verificados

**Próximo paso:** FASE 4 - Autenticación (ver SIGUIENTE_PASO.md)

---

> **Nota:** Esta documentación se actualizará conforme avance el desarrollo del frontend.
