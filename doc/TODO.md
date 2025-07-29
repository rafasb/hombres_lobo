# TODO - Reorientación Frontend Vue.js 3

## 🔄 ESTADO ACTUAL: REORIENTACIÓN ARQUITECTURAL

### ❌ FRONTEND ANTERIOR (A ELIMINAR)
- Jinja2 Templates en `/app/templates/` - **ELIMINAR COMPLETAMENTE**
- Archivos estáticos en `/app/static/` - **ELIMINAR COMPLETAMENTE** 
- Dependencias Jinja2 en FastAPI - **REFACTORIZAR A API PURA**

### ✅ BACKEND EXISTENTE (FUNCIONAL)
- API REST FastAPI completa y funcional
- Modelos Pydantic definidos
- Sistema completo de Hombres Lobo implementado
- Base de datos JSON funcional

---

## 🚀 PLAN DE MIGRACIÓN INMEDIATO

### **FASE 1: LIMPIEZA Y RESTRUCTURACIÓN** (⏳ SIGUIENTE PRIORIDAD)
1. [ ] **CRÍTICO: Crear estructura backend/frontend separada**
2. [ ] **CRÍTICO: Eliminar templates y static del backend actual**
3. [ ] **CRÍTICO: Refactorizar main.py para API REST pura**
4. [ ] **CRÍTICO: Configurar CORS para comunicación frontend-backend**

### **FASE 2: CREAR PROYECTO VUE.JS 3** (📋 PENDIENTE)
1. [ ] Inicializar proyecto Vue.js 3 con TypeScript
2. [ ] Configurar Vite + Vue Router + Pinia
3. [ ] Instalar Vuetify/PrimeVue para UI components
4. [ ] Configurar Axios para comunicación con API

### **FASE 3: MIGRAR FUNCIONALIDADES** (📋 PENDIENTE)
1. [ ] Implementar autenticación JWT en frontend
2. [ ] Crear vistas principales (Login, Register, Games, Game)
3. [ ] Implementar gestión de estado con Pinia
4. [ ] Crear componentes de juego por roles

---

## ❗ TAREAS CRÍTICAS INMEDIATAS

### 🔥 ALTA PRIORIDAD (Esta semana)
1. **Eliminar código frontend obsoleto:**
   ```bash
   rm -rf app/templates/
   rm -rf app/static/
   ```

2. **Refactorizar main.py:**
   - Eliminar Jinja2Templates
   - Eliminar StaticFiles
   - Agregar CORS middleware
   - Convertir todos los endpoints a JSON-only

3. **Crear nueva estructura:**
   ```
   /home/rafasb/desarrollo/hombres_lobo/
   ├── backend/     # ← Mover contenido actual
   └── frontend/    # ← Nuevo proyecto Vue.js 3
   ```

### 📋 ARQUITECTURA OBJETIVO
```
backend/
├── app/
│   ├── main.py          # FastAPI + CORS (JSON only)
│   ├── api/             # REST endpoints
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   └── database.py      # Data persistence
└── tests/               # Backend tests

frontend/
├── src/
│   ├── views/           # Vue pages
│   ├── components/      # Vue components
│   ├── stores/          # Pinia stores
│   ├── services/        # API services
│   └── router/          # Vue Router
├── package.json
└── vite.config.js
```

---

## 📚 RECURSOS CREADOS

- **📄 [ESPECIFICACIONES_Y_PLANIFICACION.md](./ESPECIFICACIONES_Y_PLANIFICACION.md)** - Especificaciones actualizadas para arquitectura Vue.js + FastAPI
- **📄 [PLANIFICACION_REORIENTACION_FRONTEND.md](./PLANIFICACION_REORIENTACION_FRONTEND.md)** - Plan detallado de migración completa

---

## ⚠️ NOTAS IMPORTANTES

1. **El frontend Vue.js mencionado en el TODO anterior NO EXISTE aún**
2. **Todas las referencias a Vue.js eran planificación futura**
3. **El código actual usa Jinja2 templates que DEBE SER ELIMINADO**
4. **La migración requiere restructuración completa del proyecto**

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

1. **Seguir [PLANIFICACION_REORIENTACION_FRONTEND.md](./PLANIFICACION_REORIENTACION_FRONTEND.md)**
2. **Comenzar con Fase 1: Limpieza y Restructuración**
3. **Crear backup del código actual antes de eliminar templates**
4. **Probar que la API funciona correctamente sin frontend**
1. Crear GameView.vue - Vista principal del juego
2. Crear componentes para cada fase:
   - NightPhaseComponent.vue
   - DayPhaseComponent.vue
   - VotingPhaseComponent.vue
3. Crear componentes por rol:
   - WerewolfActionsComponent.vue
   - SeerActionsComponent.vue
   - WitchActionsComponent.vue
   - SheriffActionsComponent.vue
   - HunterActionsComponent.vue
   - CupidActionsComponent.vue
   - WildChildActionsComponent.vue
4. Crear componentes de UI:
   - PlayerCardComponent.vue
   - GameStatusComponent.vue
   - RoleInfoComponent.vue
   - ActionPanelComponent.vue

## 📡 PENDIENTE: Integración con WebSockets para tiempo real

## Arquitectura Frontend Actual

### 🎯 Stack Tecnológico
- **Vue 3** + TypeScript + Vite
- **Tailwind CSS** - Styling y componentes
- **Pinia** - State management
- **Vue Router** - Routing con guards
- **Axios** - HTTP client para API
- **Playwright** - Testing E2E

### 📁 Estructura de Archivos
```
frontend/src/
├── services/
│   └── api.ts                 ✅ Servicios de API completos
├── stores/
│   └── index.ts              ✅ Stores de Pinia (auth, game, etc.)
├── views/
│   ├── LoginView.vue         ✅ Pantalla de login
│   ├── RegisterView.vue      ✅ Pantalla de registro
│   ├── GamesListView.vue     ✅ Lobby principal
│   └── GameView.vue          ⏳ SIGUIENTE: Vista del juego
├── components/
│   └── (pendientes)          📋 Componentes de juego
├── router/
│   └── index.ts              ✅ Routing con autenticación
├── style.css                 ✅ Estilos Tailwind personalizados
└── main.ts                   ✅ App principal
```

### 🔌 Integración con Backend
- ✅ **AuthService** - Login, registro, verificación JWT
- ✅ **GameService** - CRUD de juegos, estado, unirse
- ✅ **VotingService** - Sistema de votación
- ✅ **Role Services** - Servicios para cada rol (Werewolf, Seer, Witch, etc.)
- ✅ **GameFlowService** - Control de flujo de fases

### 🎮 Funcionalidades Implementadas
- ✅ **Autenticación completa** con JWT
- ✅ **Creación y lista de juegos**
- ✅ **Unirse a juegos** existentes
- ✅ **Guards de navegación** para rutas protegidas
- ✅ **Responsive design** móvil-first
- ✅ **Estado global** con Pinia stores
- ✅ **Error handling** y notificaciones

## Próximos Pasos Inmediatos

### 1. **CREAR GAMEVIEW.VUE** (Prioridad Alta)
```bash
# Vista principal del juego que mostrará:
- Estado actual del juego (fase, jugadores vivos/muertos)
- Panel de acciones según el rol del jugador
- Lista de jugadores con estados
- Timer de fase
- Historial de eventos
```

