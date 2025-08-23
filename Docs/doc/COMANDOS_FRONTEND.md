# 🚀 Guía Rápida de Comandos - Frontend Vue.js 3

## 📋 Instalación Paso a Paso

### ✅ Paso 1: Crear Proyecto Vue.js Base
```bash
cd /home/rafasb/desarrollo/hombres_lobo/frontend
npm create vue@latest . --typescript --router --pinia
```

### ✅ Paso 2: Instalar Dependencias Base
```bash
npm install
```

### ✅ Paso 3: Instalar PrimeVue Ecosystem
```bash
npm install primevue primeicons primeflex
```

### ✅ Paso 4: Instalar Cliente HTTP
```bash
npm install axios
```

### ✅ Paso 5: Instalar Tipos TypeScript
```bash
npm install --save-dev @types/node
```

### ✅ Paso 6: Verificar Instalación
```bash
npm run dev
```

## 🔧 Configuraciones Críticas

### 1. main.ts - Configurar PrimeVue
```typescript
import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/aura-light-green/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

const app = createApp(App)
app.use(PrimeVue)
```

### 2. vite.config.ts - Proxy Backend
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

### 3. API Service Base
```typescript
// src/services/api.ts
import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})
```

## 🔍 Verificaciones

### ✅ Checklist de Instalación
- [ ] `npm run dev` arranca sin errores
- [ ] Acceso a `http://localhost:5173`
- [ ] No errores de TypeScript
- [ ] PrimeVue componentes disponibles
- [ ] Axios configurado correctamente

### 🚨 Posibles Errores y Soluciones

#### Error: "Cannot resolve dependency"
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### Error: TypeScript compilation
```bash
npm run type-check
```

#### Error: Puerto 5173 ocupado
```bash
npm run dev -- --port 5174
```

## 📱 Desarrollo Mobile-First

### Componentes PrimeVue Recomendados
- `Button` - Botones
- `Card` - Contenedores
- `InputText` - Campos de texto
- `Password` - Campos de contraseña
- `Dialog` - Modales
- `DataTable` - Tablas
- `Toast` - Notificaciones
- `Menu` - Menús
- `Sidebar` - Menú lateral

### Utilities PrimeFlex
```css
/* Grid responsive */
.p-grid
.p-col-12 .p-md-6 .p-lg-4

/* Spacing */
.p-m-2  /* margin */
.p-p-3  /* padding */

/* Flex */
.p-d-flex
.p-jc-center
.p-ai-center
```

## 🎯 Próximos Pasos Post-Instalación

1. **Configurar estructura de carpetas:**
   - `src/components/common/`
   - `src/components/auth/`
   - `src/components/games/`
   - `src/stores/`
   - `src/services/`

2. **Crear servicios básicos:**
   - `authService.ts`
   - `userService.ts`
   - `gameService.ts`

3. **Configurar stores Pinia:**
   - `authStore.ts`
   - `userStore.ts`
   - `gameStore.ts`

4. **Crear vistas principales:**
   - `LoginView.vue`
   - `RegisterView.vue`
   - `GamesView.vue`
   - `GameView.vue`

---

**🔗 Enlaces Útiles:**
- [PrimeVue Documentation](https://primevue.org/)
- [Vue.js 3 Guide](https://vuejs.org/guide/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Axios Documentation](https://axios-http.com/)
