# To Do

## ✅ COMPLETADO: Configurar el proyecto Vue con todas las dependencias
1. ✅ Setup inicial del proyecto Vue
2. ✅ Instalación de dependencias (Tailwind, Axios, Pinia, etc.)
3. ✅ Configuración de servicios API
4. ✅ Configuración de stores (Pinia)
5. ✅ Crear componentes de autenticación (Login/Register)
6. ✅ Crear vista de lobby (Lista de juegos)
7. ✅ Configurar routing con guards de autenticación

## 🔄 EN PROGRESO: Componentes de autenticación y lobby
1. ✅ Crear LoginView.vue - Pantalla de inicio de sesión
2. ✅ Crear RegisterView.vue - Pantalla de registro
3. ✅ Crear GamesListView.vue - Lobby principal con lista de juegos
4. ⏳ **SIGUIENTE: Crear GameView.vue** - Vista principal del juego
5. ⏳ Integrar con API FastAPI real
6. ⏳ Testing de flujo de autenticación

## 📋 PENDIENTE: Interfaz principal del juego
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

