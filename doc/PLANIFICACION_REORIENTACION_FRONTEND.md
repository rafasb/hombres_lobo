# Planificación Detallada: Reorientación Frontend Vue.js 3

## 📋 Estado Actual del Proyecto

### ✅ Backend Existente (FastAPI)
- **Estructura:** `/app/` con API REST funcional
- **Endpoints:** Autenticación, usuarios, juegos, roles especiales
- **Base de datos:** JSON file-based con modelos Pydantic
- **Funcionalidades:** Sistema completo de Hombres Lobo implementado

### ❌ Frontend Actual (A Eliminar)
- **Templates Jinja2:** `/app/templates/` - **ELIMINAR**
- **Archivos estáticos:** `/app/static/` - **ELIMINAR**
- **Dependencias:** Integración con Jinja2 en FastAPI - **REFACTORIZAR**

### 🎯 Objetivo
Crear una arquitectura completamente separada:
- **Backend:** API REST pura (FastAPI)
- **Frontend:** SPA independiente (Vue.js 3)

---

## 🚀 PLAN DE TRABAJO DETALLADO

### **FASE 1: LIMPIEZA Y RESTRUCTURACIÓN** (1-2 días)

#### 1.1 Crear Nueva Estructura de Directorios
```bash
# Crear estructura nueva
/home/rafasb/desarrollo/hombres_lobo/
├── backend/          # ← Mover contenido actual de /app/
└── frontend/         # ← Nuevo proyecto Vue.js 3
```

#### 1.2 Migrar Backend a Nueva Estructura
- [ ] Crear directorio `/backend/`
- [ ] Mover `/app/` completo a `/backend/app/`
- [ ] Mover `/tests/` a `/backend/tests/`
- [ ] Mover `requirements.txt` a `/backend/`
- [ ] Actualizar imports y rutas en el código backend

#### 1.3 Limpiar Código Frontend Antiguo
- [ ] **ELIMINAR** `/backend/app/templates/` completamente
- [ ] **ELIMINAR** `/backend/app/static/` completamente
- [ ] **REFACTORIZAR** `main.py` para eliminar:
  - Jinja2Templates
  - StaticFiles mount
  - HTMLResponse endpoints
- [ ] **AGREGAR** configuración CORS para comunicación con frontend

#### 1.4 Actualizar Backend para API REST Pura
- [ ] Modificar todos los endpoints para devolver solo JSON
- [ ] Eliminar dependencias de Jinja2 del `requirements.txt`
- [ ] Configurar CORS middleware
- [ ] Actualizar documentación de API

---

### **FASE 2: CONFIGURACIÓN FRONTEND VUE.JS 3** (2-3 días)

#### 2.1 Inicializar Proyecto Vue.js 3
```bash
cd /home/rafasb/desarrollo/hombres_lobo/
npm create vue@latest frontend
cd frontend
npm install
```

#### 2.2 Configurar Stack Tecnológico
- [ ] **Vite** - Build tool y dev server
- [ ] **TypeScript** - Para tipado fuerte
- [ ] **Vue Router 4** - Enrutamiento SPA
- [ ] **Pinia** - State management
- [ ] **Axios** - HTTP client
- [ ] **Vuetify 3** o **PrimeVue** - UI Components
- [ ] **Tailwind CSS** - Utility-first CSS (opcional)

#### 2.3 Instalación de Dependencias
```bash
npm install axios pinia vue-router@4
npm install @vuetify/vite-plugin vuetify@next
# o alternativamente
npm install primevue@next primeicons
npm install @tailwindcss/typography tailwindcss
```

#### 2.4 Configuración Base
- [ ] Configurar `vite.config.js` con plugins
- [ ] Configurar proxy para desarrollo (backend en puerto 8000)
- [ ] Configurar TypeScript (tsconfig.json)
- [ ] Configurar rutas base en Vue Router

---

### **FASE 3: ARQUITECTURA FRONTEND BASE** (3-4 días)

#### 3.1 Estructura de Directorios Frontend
```
frontend/src/
├── components/       # Componentes reutilizables
│   ├── common/      # Header, Footer, Loading, etc.
│   ├── auth/        # Login, Register forms
│   ├── games/       # Game cards, lists, etc.
│   ├── game/        # In-game components
│   └── ui/          # UI específicos
├── views/           # Páginas principales
├── stores/          # Pinia stores
├── services/        # API services
├── composables/     # Vue 3 composables
├── router/          # Router configuration
├── types/           # TypeScript types
├── utils/           # Utilidades
└── assets/          # Assets estáticos
```

#### 3.2 Servicios de API (TypeScript)
- [ ] `apiClient.ts` - Configuración Axios base
- [ ] `authService.ts` - Login, register, token management
- [ ] `userService.ts` - CRUD usuarios
- [ ] `gameService.ts` - CRUD juegos, join/leave
- [ ] `gameFlowService.ts` - Control de fases del juego
- [ ] `roleServices.ts` - Servicios específicos por rol

#### 3.3 Stores Pinia
- [ ] `authStore.ts` - Estado de autenticación
- [ ] `userStore.ts` - Datos del usuario actual
- [ ] `gamesStore.ts` - Lista de juegos
- [ ] `gameStore.ts` - Estado del juego actual
- [ ] `uiStore.ts` - Estado UI global

#### 3.4 Router y Guards
- [ ] Configurar rutas principales
- [ ] Guards de autenticación
- [ ] Guards de roles/permisos
- [ ] Lazy loading de componentes

---

### **FASE 4: COMPONENTES DE AUTENTICACIÓN** (2-3 días)

#### 4.1 Vistas de Autenticación
- [ ] `LoginView.vue` - Pantalla login
- [ ] `RegisterView.vue` - Pantalla registro
- [ ] `ProfileView.vue` - Perfil de usuario

#### 4.2 Componentes de Autenticación
- [ ] `LoginForm.vue` - Formulario login
- [ ] `RegisterForm.vue` - Formulario registro
- [ ] `AuthGuard.vue` - Wrapper para rutas protegidas

#### 4.3 Integración con Backend
- [ ] Implementar JWT token management
- [ ] Auto-refresh de tokens
- [ ] Interceptors para errores de autenticación

---

### **FASE 5: GESTIÓN DE JUEGOS** (3-4 días)

#### 5.1 Vistas de Juegos
- [ ] `GamesListView.vue` - Lobby principal
- [ ] `CreateGameView.vue` - Crear nuevo juego
- [ ] `GameLobbyView.vue` - Sala de espera del juego
- [ ] `GameView.vue` - Vista principal del juego

#### 5.2 Componentes de Juegos
- [ ] `GameCard.vue` - Tarjeta de juego en lista
- [ ] `CreateGameForm.vue` - Formulario crear juego
- [ ] `PlayersList.vue` - Lista de jugadores
- [ ] `GameControls.vue` - Controles de creador

---

### **FASE 6: INTERFAZ DE JUEGO** (5-7 días)

#### 6.1 Componentes de Fases
- [ ] `NightPhaseComponent.vue` - Fase nocturna
- [ ] `DayPhaseComponent.vue` - Fase diurna
- [ ] `VotingPhaseComponent.vue` - Fase de votación
- [ ] `ResultsPhaseComponent.vue` - Resultados de fase

#### 6.2 Componentes por Rol
- [ ] `WerewolfActionsComponent.vue` - Acciones hombre lobo
- [ ] `SeerActionsComponent.vue` - Acciones vidente
- [ ] `WitchActionsComponent.vue` - Acciones bruja
- [ ] `SheriffActionsComponent.vue` - Acciones sheriff
- [ ] `HunterActionsComponent.vue` - Acciones cazador
- [ ] `CupidActionsComponent.vue` - Acciones cupido
- [ ] `WildChildActionsComponent.vue` - Acciones niño salvaje

#### 6.3 Componentes de UI Juego
- [ ] `PlayerCardComponent.vue` - Tarjeta de jugador
- [ ] `GameStatusComponent.vue` - Estado del juego
- [ ] `RoleInfoComponent.vue` - Info del rol
- [ ] `ActionPanelComponent.vue` - Panel de acciones
- [ ] `TimerComponent.vue` - Temporizador de fase
- [ ] `EventLogComponent.vue` - Log de eventos

---

### **FASE 7: FUNCIONALIDADES AVANZADAS** (3-4 días)

#### 7.1 Estado Reactivo Avanzado
- [ ] Sincronización automática con backend
- [ ] Optimistic updates
- [ ] Cache inteligente de datos
- [ ] Manejo de errores de red

#### 7.2 UX/UI Mejoradas
- [ ] Transiciones y animaciones
- [ ] Loading states
- [ ] Error boundaries
- [ ] Notificaciones toast
- [ ] Modales reutilizables

#### 7.3 WebSockets (Opcional)
- [ ] Configurar WebSocket client
- [ ] Updates en tiempo real del juego
- [ ] Sincronización de estado entre jugadores

---

### **FASE 8: TESTING Y OPTIMIZACIÓN** (2-3 días)

#### 8.1 Testing
- [ ] Unit tests (Vitest)
- [ ] Component tests (Vue Test Utils)
- [ ] E2E tests (Playwright)

#### 8.2 Optimización
- [ ] Code splitting
- [ ] Lazy loading
- [ ] Bundle analysis
- [ ] Performance optimization

#### 8.3 Build y Deploy
- [ ] Configuración de build de producción
- [ ] Variables de entorno
- [ ] Docker configuration
- [ ] Deploy scripts

---

## 📅 CRONOGRAMA ESTIMADO

| Fase | Duración | Entregables |
|------|----------|-------------|
| **Fase 1** | 1-2 días | Backend restructurado, frontend limpio |
| **Fase 2** | 2-3 días | Proyecto Vue.js configurado |
| **Fase 3** | 3-4 días | Arquitectura base frontend |
| **Fase 4** | 2-3 días | Autenticación funcional |
| **Fase 5** | 3-4 días | Gestión de juegos |
| **Fase 6** | 5-7 días | Interfaz de juego completa |
| **Fase 7** | 3-4 días | Funcionalidades avanzadas |
| **Fase 8** | 2-3 días | Testing y optimización |

**Total estimado: 21-30 días**

---

## 🔧 COMANDOS DE MIGRACIÓN

### Paso 1: Restructurar Proyecto
```bash
cd /home/rafasb/desarrollo/hombres_lobo

# Crear nueva estructura
mkdir -p backend frontend

# Mover backend
mv app backend/
mv tests backend/
mv requirements.txt backend/
mv .env backend/
mv .env.example backend/

# Limpiar frontend antiguo
rm -rf backend/app/templates
rm -rf backend/app/static
```

### Paso 2: Crear Frontend Vue.js
```bash
# Crear proyecto Vue
cd frontend
npm create vue@latest . --typescript --router --pinia
npm install

# Instalar dependencias adicionales
npm install axios @types/node
npm install vuetify@next @vuetify/vite-plugin
```

### Paso 3: Configurar Backend API Pura
```python
# Actualizar backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hombres Lobo API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 CRITERIOS DE ÉXITO

### ✅ Técnicos
- [ ] Frontend y backend completamente separados
- [ ] API REST pura sin dependencias de templates
- [ ] SPA Vue.js 3 funcional con todas las características
- [ ] Autenticación JWT implementada
- [ ] Estado reactivo funcionando correctamente
- [ ] Responsive design para móviles
- [ ] Tests unitarios y E2E pasando

### ✅ Funcionales
- [ ] Registro e inicio de sesión
- [ ] Crear y unirse a juegos
- [ ] Jugar partidas completas de Hombres Lobo
- [ ] Todos los roles especiales funcionando
- [ ] Votaciones y fases del juego
- [ ] Panel de administración (opcional)

### ✅ UX/UI
- [ ] Interfaz intuitiva y moderna
- [ ] Optimizada para móviles
- [ ] Feedback visual apropiado
- [ ] Navegación fluida
- [ ] Manejo de errores elegante

---

## 📚 RECURSOS Y REFERENCIAS

### Documentación
- [Vue.js 3 Guide](https://vuejs.org/guide/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vuetify 3 Documentation](https://vuetifyjs.com/)
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)

### Tools
- [Vue DevTools](https://devtools.vuejs.org/)
- [Vite Plugin](https://vitejs.dev/plugins/)
- [TypeScript](https://www.typescriptlang.org/)

---

> **Nota:** Esta planificación puede ajustarse según el progreso y las necesidades específicas que surjan durante el desarrollo.
