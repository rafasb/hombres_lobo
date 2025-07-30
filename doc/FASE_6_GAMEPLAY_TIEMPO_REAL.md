# 🎮 FASE 6: Sistema de Juego en Tiempo Real - Plan Detallado

## 🎯 Objetivo de Esta Fase
Implementar el sistema de gameplay en tiempo real con WebSockets, incluyendo fases de juego (día/noche), votaciones, chat en vivo y acciones básicas de roles.

## ⏱️ Tiempo Estimado
**Duración:** 4-5 días  
**Prioridad:** 🔴 CRÍTICA (Core gameplay)

## ✅ PRERREQUISITOS COMPLETADOS
- ✅ Fase 5: Gestión de juegos completada
- ✅ Sistema de salas de espera funcional
- ✅ Autenticación y autorización implementada
- ✅ Base de datos con modelos de juego y roles
- ✅ Frontend responsive con PrimeVue

---

## 📋 TAREAS ESPECÍFICAS DETALLADAS

### 1️⃣ SETUP DE WEBSOCKETS EN BACKEND
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1 día  

#### 1.1 Configuración de WebSocket Server
**Archivo:** `backend/app/websocket.py`
- [ ] Instalar dependencias: `websockets`, `python-socketio`
- [ ] Configurar FastAPI WebSocket manager
- [ ] Implementar conexión/desconexión de clientes
- [ ] Sistema de rooms por juego (game_id)
- [ ] Manejo de errores y reconexión

#### 1.2 Protocolo de Mensajes
**Archivo:** `backend/app/websocket/messages.py`
- [ ] Definir tipos de mensajes:
  ```python
  # Ejemplos de mensajes
  - PLAYER_JOINED
  - PLAYER_LEFT  
  - GAME_PHASE_CHANGED
  - VOTE_CAST
  - CHAT_MESSAGE
  - ROLE_ACTION
  - GAME_EVENT
  ```
- [ ] Validación de mensajes con Pydantic
- [ ] Serialización JSON optimizada

#### 1.3 Game State Manager
**Archivo:** `backend/app/services/game_state_service.py`
- [ ] Gestor de estados de juego en memoria
- [ ] Sincronización con base de datos
- [ ] Sistema de heartbeat/keepalive
- [ ] Manejo de desconexiones abruptas

### 2️⃣ SISTEMA DE FASES DE JUEGO
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1.5 días

#### 2.1 Game Phase Controller
**Archivo:** `backend/app/services/game_phases_service.py`
- [ ] Estados de juego:
  ```python
  class GamePhase(Enum):
      WAITING = "waiting"      # Sala de espera
      STARTING = "starting"    # Iniciando juego
      NIGHT = "night"         # Fase nocturna
      DAY = "day"             # Fase diurna  
      VOTING = "voting"       # Votaciones
      TRIAL = "trial"         # Juicio/defensa
      EXECUTION = "execution" # Ejecución
      FINISHED = "finished"   # Juego terminado
  ```
- [ ] Transiciones automáticas entre fases
- [ ] Timers configurables por fase
- [ ] Validaciones de estado

#### 2.2 Sistema de Turnos
**Archivo:** `backend/app/services/turn_service.py`
- [ ] Cola de turnos por rol
- [ ] Manejo de acciones nocturnas
- [ ] Sistema de prioridades de roles
- [ ] Timeout de acciones

#### 2.3 Condiciones de Victoria
**Archivo:** `backend/app/services/victory_service.py`
- [ ] Verificar condiciones después de cada fase
- [ ] Victoria de Hombres Lobo vs Aldeanos
- [ ] Condiciones especiales (amantes, niño salvaje)
- [ ] Calcular estadísticas finales

### 3️⃣ SISTEMA DE VOTACIONES
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1 día

#### 3.1 Voting Service
**Archivo:** `backend/app/services/voting_service.py`
- [ ] Crear votación (día/sheriff/other)
- [ ] Registrar votos de jugadores
- [ ] Conteo automático de votos
- [ ] Manejo de empates
- [ ] Voto doble del sheriff
- [ ] Eliminación por mayoría

#### 3.2 Voting WebSocket Handlers
**Archivo:** `backend/app/websocket/voting_handlers.py`
- [ ] `cast_vote` - Emitir voto
- [ ] `get_voting_status` - Estado actual
- [ ] Broadcast de cambios en tiempo real
- [ ] Validar derecho a voto (vivo/muerto)

### 4️⃣ FRONTEND WEBSOCKET CLIENT
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1 día

#### 4.1 WebSocket Service
**Archivo:** `frontend/src/services/websocket.ts`
- [ ] Cliente WebSocket con reconexión automática
- [ ] Sistema de eventos reactivos
- [ ] Queue de mensajes offline
- [ ] Heartbeat/ping-pong
- [ ] Manejo de errores de conexión

#### 4.2 Game Store con WebSocket
**Archivo:** `frontend/src/stores/realtime-game.ts`
- [ ] Store Pinia para estado de juego en tiempo real
- [ ] Sincronización bidireccional con backend
- [ ] Estado de conexión WebSocket
- [ ] Cache local para offline mode

#### 4.3 Composables para WebSocket
**Archivo:** `frontend/src/composables/useWebSocket.ts`
- [ ] `useGameSocket()` - Conexión por juego
- [ ] `useVoting()` - Sistema de votación
- [ ] `useChat()` - Chat en tiempo real
- [ ] `useGamePhase()` - Estados de juego

### 5️⃣ INTERFAZ DE GAMEPLAY
**Prioridad:** 🔴 CRÍTICA  
**Tiempo:** 1.5 días

#### 5.1 GamePlayView
**Archivo:** `frontend/src/views/GamePlayView.vue`
- [ ] Layout principal del juego activo
- [ ] Panel de información del juego
- [ ] Lista de jugadores vivos/muertos
- [ ] Indicador de fase actual
- [ ] Timer de fase
- [ ] Panel de acciones según rol

#### 5.2 VotingPanel Component
**Archivo:** `frontend/src/components/game/VotingPanel.vue`
- [ ] Lista de jugadores para votar
- [ ] Botones de votación
- [ ] Contador de votos en tiempo real
- [ ] Resultados de votación
- [ ] Estados: abierta/cerrada/completada

#### 5.3 GamePhaseIndicator
**Archivo:** `frontend/src/components/game/GamePhaseIndicator.vue`
- [ ] Indicador visual de fase actual
- [ ] Countdown timer animado
- [ ] Transiciones entre fases
- [ ] Instrucciones contextuales

#### 5.4 PlayersGrid
**Archivo:** `frontend/src/components/game/PlayersGrid.vue`
- [ ] Grid de jugadores en el juego
- [ ] Estados: vivo/muerto/sospechoso
- [ ] Avatares con indicadores de rol (si revelado)
- [ ] Acciones disponibles (votar, usar habilidad)
- [ ] Animaciones de eliminación

### 6️⃣ SISTEMA DE CHAT EN TIEMPO REAL
**Prioridad:** 🟡 ALTA  
**Tiempo:** 0.5 días

#### 6.1 Chat Backend
**Archivo:** `backend/app/websocket/chat_handlers.py`
- [ ] Mensajes de chat por canal
- [ ] Filtros por estado (vivos/muertos)
- [ ] Sistema de moderación básico
- [ ] Historial de mensajes

#### 6.2 Chat Component
**Archivo:** `frontend/src/components/game/ChatComponent.vue`
- [ ] Input de mensaje con validación
- [ ] Lista de mensajes en tiempo real
- [ ] Diferentes canales según estado
- [ ] Indicadores de escritura
- [ ] Scroll automático

---

## 🎯 ARQUITECTURA TÉCNICA DETALLADA

### Backend WebSocket Architecture
```
backend/app/
├── websocket/
│   ├── __init__.py
│   ├── connection_manager.py    # Gestor de conexiones WS
│   ├── message_handlers.py      # Handlers por tipo mensaje
│   ├── game_handlers.py         # Handlers específicos de juego
│   ├── voting_handlers.py       # Handlers de votación
│   └── chat_handlers.py         # Handlers de chat
├── services/
│   ├── game_state_service.py    # Estado de juego en memoria
│   ├── game_phases_service.py   # Lógica de fases
│   ├── voting_service.py        # Sistema de votación
│   ├── turn_service.py          # Manejo de turnos
│   └── victory_service.py       # Condiciones de victoria
└── models/
    ├── websocket_models.py      # Modelos para WebSocket
    └── game_events.py           # Eventos de juego
```

### Frontend Real-time Architecture
```
frontend/src/
├── services/
│   └── websocket.ts             # Cliente WebSocket
├── stores/
│   └── realtime-game.ts         # Store para tiempo real
├── composables/
│   ├── useWebSocket.ts          # WebSocket composable
│   ├── useVoting.ts             # Votación composable
│   └── useGamePhase.ts          # Fases composable
├── views/
│   └── GamePlayView.vue         # Vista principal del juego
└── components/game/
    ├── VotingPanel.vue          # Panel de votación
    ├── GamePhaseIndicator.vue   # Indicador de fase
    ├── PlayersGrid.vue          # Grid de jugadores
    ├── ChatComponent.vue        # Chat en tiempo real
    └── RoleActions.vue          # Acciones por rol
```

### Protocolo de Mensajes WebSocket
```typescript
interface WebSocketMessage {
  type: MessageType
  game_id: string
  player_id: string
  timestamp: string
  data: any
}

enum MessageType {
  // Connection
  PLAYER_CONNECTED = "player_connected"
  PLAYER_DISCONNECTED = "player_disconnected"
  
  // Game phases
  PHASE_CHANGED = "phase_changed"
  PHASE_TIMER = "phase_timer"
  
  // Voting
  VOTE_CAST = "vote_cast"
  VOTING_RESULTS = "voting_results"
  
  // Chat
  CHAT_MESSAGE = "chat_message"
  
  // Role actions
  ROLE_ACTION = "role_action"
  
  // Game events
  PLAYER_ELIMINATED = "player_eliminated"
  GAME_ENDED = "game_ended"
}
```

---

## 🎯 CRITERIOS DE ÉXITO

### ✅ Comunicación en Tiempo Real
- [ ] Conexión WebSocket estable con reconexión automática
- [ ] Latencia < 100ms para mensajes críticos
- [ ] Manejo robusto de desconexiones
- [ ] Sincronización perfecta entre clientes

### ✅ Sistema de Fases
- [ ] Transiciones automáticas entre día/noche
- [ ] Timers configurables y sincronizados
- [ ] Estados consistentes entre todos los clientes
- [ ] Manejo de edge cases (desconexiones durante transición)

### ✅ Votaciones Funcionales
- [ ] Registro de votos en tiempo real
- [ ] Conteo automático y preciso
- [ ] Manejo correcto de empates
- [ ] Feedback visual inmediato

### ✅ Interfaz de Usuario
- [ ] UI responsive durante el gameplay
- [ ] Indicadores claros de fase y tiempo
- [ ] Interacciones fluidas e intuitivas
- [ ] Feedback visual para todas las acciones

---

## 🚀 PREPARACIÓN PARA FASE 7

Esta fase establece la base para:
- Implementación de roles especiales complejos
- Acciones nocturnas específicas por rol
- Mecánicas avanzadas (amantes, transformaciones)
- Sistema de habilidades especiales

---

## 📊 IMPACTO EN EL PROYECTO

**Al completar esta fase tendremos:**
- 🎮 Gameplay básico completamente funcional
- ⚡ Comunicación en tiempo real establecida
- 🗳️ Sistema de votaciones operativo
- 💬 Chat en vivo durante partidas
- 🔄 Base sólida para roles especiales complejos

**Progreso del proyecto:** 62.5% → 87.5% (completando 6/8 fases)

---

## 🔧 DEPENDENCIAS TÉCNICAS

### Backend Dependencies
```bash
# Nuevas dependencias para WebSocket
pip install websockets
pip install python-socketio
pip install python-socketio[asyncio_client]
```

### Frontend Dependencies
```bash
# Cliente WebSocket para Vue.js
npm install socket.io-client
npm install @types/socket.io-client
```

---

## ⚠️ RIESGOS Y CONSIDERACIONES

### Riesgos Técnicos:
- **Complejidad de sincronización** - Estados distribuidos pueden desincronizarse
- **Manejo de desconexiones** - Usuarios perdiendo conexión durante el juego
- **Escalabilidad WebSocket** - Performance con múltiples juegos simultáneos
- **Estado inconsistente** - Race conditions en votaciones

### Mitigaciones:
- Implementar sistema robusto de reconexión
- Cache de estado local para recuperación
- Validación de estado en backend
- Sistema de locks para operaciones críticas

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Orden de Desarrollo Recomendado:
1. **Backend WebSocket básico** - Conexión y mensajes simples
2. **Frontend WebSocket client** - Integración con Vue.js
3. **Sistema de fases básico** - Día/noche automático
4. **Votaciones simples** - Eliminación por mayoría
5. **Interfaz de gameplay** - UI completa
6. **Chat en tiempo real** - Comunicación entre jugadores
7. **Pulido y testing** - Casos edge y optimización

### Testing Strategy:
- Unit tests para lógica de votación
- Integration tests para WebSocket
- E2E tests para flujo completo de juego
- Load testing para múltiples usuarios

---

> **🎯 OBJETIVO:** Sistema de juego en tiempo real completamente funcional
> 
> **🏁 RESULTADO ESPERADO:** Jugadores pueden jugar partidas completas con votaciones, chat y fases automáticas
