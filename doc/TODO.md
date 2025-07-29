# 📋 TODO - Lista de Tareas del Proyecto

## 🎯 ESTADO ACTUAL
**Progreso:** 2/8 fases completadas (25%)  
**Última actualización:** 29 Julio 2025

## 📚 DOCUMENTACIÓN REORGANIZADA
- **📄 PLANIFICACION_GLOBAL.md** - Vista general del proyecto (8 fases)
- **📄 SIGUIENTE_PASO.md** - Plan detallado inmediato (Fase 3)

## ✅ FASES COMPLETADAS

### ✅ Fase 1: Restructuración Backend (COMPLETADA - 29 Jul)
- [x] Crear estructura `/backend/` y `/frontend/`
- [x] Mover código existente a nueva estructura
- [x] Eliminar dependencias frontend legacy
- [x] Refactorizar `main.py` para API REST pura
- [x] Configurar CORS para comunicación frontend
- [x] Verificar API funcionando correctamente

### ✅ Fase 2: Instalación Frontend Vue.js (COMPLETADA - 29 Jul)
- [x] Crear proyecto Vue.js 3 con TypeScript
- [x] Instalar PrimeVue + PrimeIcons + PrimeFlex
- [x] Instalar Axios y dependencias
- [x] Configurar Vite y herramientas de desarrollo
- [x] Verificar servidor de desarrollo funcionando

### ✅ Fase 3: Configuraciones Base (COMPLETADA - 29 Jul)
- [x] **Configurar PrimeVue en main.ts** ✅
- [x] **Configurar proxy backend en vite.config.ts** ✅
- [x] **Crear servicios API base** ✅
- [x] **Crear estructura de carpetas** ✅
- [x] **Probar comunicación frontend-backend** ✅ EXITOSA

---

## 🔄 EN PROGRESO: FASE 4 - AUTENTICACIÓN

### ⏳ SIGUIENTE PRIORIDAD (Ver SIGUIENTE_PASO.md para detalles)
- [ ] **Crear stores de autenticación con Pinia**
- [ ] **Crear componentes de login/register**
- [ ] **Integrar JWT token management**
- [ ] **Crear guards de navegación**
- [ ] **Probar flujo de autenticación completo**


---

## 📋 FASES PENDIENTES (Ver PLANIFICACION_GLOBAL.md para detalles)

### **FASE 4: Autenticación** (📋 PENDIENTE - 2-3 días)
- [ ] Implementar login/register en frontend
- [ ] Configurar JWT token management
- [ ] Crear guards de navegación

### **FASE 5: Gestión de Juegos** (📋 PENDIENTE - 3-4 días)
- [ ] Crear interfaces para gestión de juegos
- [ ] Implementar lobby y salas de espera
- [ ] Conectar con endpoints de backend

### **FASE 6: Interfaz de Juego** (📋 PENDIENTE - 5-7 días)
- [ ] Crear interfaz completa del juego
- [ ] Implementar todos los roles especiales
- [ ] Gestionar fases del juego

### **FASE 7: Funcionalidades Avanzadas** (📋 PENDIENTE - 3-4 días)
- [ ] Optimizar UX/UI
- [ ] Implementar funcionalidades premium
- [ ] Añadir responsive design completo

### **FASE 8: Testing y Optimización** (📋 PENDIENTE - 2-3 días)
- [ ] Asegurar calidad del código
- [ ] Optimizar performance
- [ ] Preparar para producción

---

## 🎯 PRÓXIMA ACCIÓN INMEDIATA

**📄 Consultar:** `SIGUIENTE_PASO.md` para plan detallado de Fase 3  
**🔧 Comando:** `cd frontend && npm run dev`  
**🌐 URLs:** Frontend: 5173 | Backend: 8000  

**Tiempo estimado para Fase 3:** 2-3 días  
**Prioridad:** � CRÍTICA (bloquea desarrollo posterior)

---

## 📊 CRONOGRAMA RESUMIDO

| Fase | Estado | Duración | Fecha Objetivo |
|------|--------|----------|----------------|
| 1-2 | ✅ Completadas | 2 días | 29 Jul 2025 |
| 3 | 🔄 En progreso | 2-3 días | 1 Ago 2025 |
| 4-5 | 📋 Pendientes | 5-7 días | 8 Ago 2025 |
| 6 | 📋 Pendiente | 5-7 días | 15 Ago 2025 |
| 7-8 | 📋 Pendientes | 5-7 días | 22 Ago 2025 |

**Entrega estimada:** 22 Agosto 2025
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

