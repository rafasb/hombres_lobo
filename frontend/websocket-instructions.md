# WebSocket - Documentación Técnica para Frontend

## Conexión WebSocket

### Endpoint
```
ws://localhost:8000/ws/{game_id}?token={access_token}
```

### Parámetros de Conexión
- **game_id** (string): ID único del juego al que se desea conectar
- **token** (string, query parameter): Token JWT de autenticación obtenido del endpoint `/login`

### Autenticación
El WebSocket requiere autenticación obligatoria:
1. Realizar login via POST `/login` para obtener `access_token`
2. Incluir el token como query parameter en la URL de conexión
3. El token será validado al momento de la conexión

### Ejemplo de Conexión (JavaScript)
```javascript
// 1. Primero hacer login
const loginResponse = await fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=tu_usuario&password=tu_password'
});
const { access_token } = await loginResponse.json();

// 2. Conectar WebSocket
const gameId = 'game-123';
const ws = new WebSocket(`ws://localhost:8000/ws/${gameId}?token=${access_token}`);
```

---

## Tipos de Mensajes

### Estructura Base
Todos los mensajes siguen esta estructura base:
```json
{
  "type": "message_type",
  "timestamp": "2025-01-30T22:00:00Z",
  "game_id": "game-123",
  // ... campos específicos del mensaje
}
```

### 1. Mensajes de Conexión

#### PLAYER_CONNECTED
Se recibe cuando un jugador se conecta al juego:
```json
{
  "type": "player_connected",
  "user_id": "user123",
  "username": "PlayerName",
  "timestamp": "2025-01-30T22:00:00Z",
  "game_id": "game-123"
}
```

#### PLAYER_DISCONNECTED
Se recibe cuando un jugador se desconecta:
```json
{
  "type": "player_disconnected",
  "user_id": "user123",
  "timestamp": "2025-01-30T22:00:00Z",
  "game_id": "game-123"
}
```

### 2. Comandos de Juego (Envío)

#### JOIN_GAME
Para unirse a un juego:
```json
{
  "type": "join_game"
}
```

#### START_GAME
Para iniciar el juego (requiere permisos de admin/creador):
```json
{
  "type": "start_game"
}
```

#### GET_GAME_STATUS
Para obtener el estado actual del juego:
```json
{
  "type": "get_game_status"
}
```

#### FORCE_NEXT_PHASE
Para forzar cambio a la siguiente fase (admin):
```json
{
  "type": "force_next_phase"
}
```

### 3. Eventos de Juego (Recepción)

#### GAME_STARTED
Se recibe cuando el juego se inicia:
```json
{
  "type": "game_started",
  "players": [
    {"id": "user1", "name": "Player1"},
    {"id": "user2", "name": "Player2"}
  ],
  "roles_assigned": true,
  "timestamp": "2025-01-30T22:00:00Z"
}
```

#### PHASE_CHANGED
Se recibe cuando cambia la fase del juego:
```json
{
  "type": "phase_changed",
  "phase": "night", // night, day, voting, trial, execution
  "duration": 60, // duración en segundos
  "timestamp": "2025-01-30T22:00:00Z"
}
```

#### PHASE_TIMER
Se recibe periódicamente durante las fases para mostrar tiempo restante:
```json
{
  "type": "phase_timer",
  "phase": "night",
  "time_remaining": 45, // segundos restantes
  "timestamp": "2025-01-30T22:00:00Z"
}
```

### 4. Sistema de Votación

#### CAST_VOTE (Envío)
Para emitir un voto:
```json
{
  "type": "cast_vote",
  "target_id": "user123"
}
```

#### VOTE_CAST (Recepción)
Se recibe cuando alguien vota:
```json
{
  "type": "vote_cast",
  "voter_id": "user456",
  "target_id": "user123",
  "vote_type": "day_vote",
  "timestamp": "2025-01-30T22:00:00Z"
}
```

#### GET_VOTING_STATUS (Envío)
Para obtener el estado actual de la votación:
```json
{
  "type": "get_voting_status"
}
```

#### VOTING_RESULTS (Recepción)
Se recibe al finalizar una votación:
```json
{
  "type": "voting_results",
  "vote_type": "day_vote",
  "results": {
    "user123": 3,
    "user456": 2
  },
  "eliminated_player": "user123",
  "is_tie": false,
  "timestamp": "2025-01-30T22:00:00Z"
}
```

### 5. Sistema de Chat

#### CHAT_MESSAGE (Envío)
Para enviar mensaje de chat:
```json
{
  "type": "chat_message",
  "message": "Hola a todos!",
  "channel": "all" // all, living, dead, wolves
}
```

#### CHAT_MESSAGE (Recepción)
Se recibe cuando alguien envía un mensaje:
```json
{
  "type": "chat_message",
  "sender_id": "user123",
  "sender_name": "PlayerName",
  "message": "Hola a todos!",
  "channel": "all",
  "timestamp": "2025-01-30T22:00:00Z"
}
```

### 6. Mensajes del Sistema

#### SYSTEM_MESSAGE
Mensajes informativos del sistema:
```json
{
  "type": "system_message",
  "message": "Estado del juego: night",
  "message_key": "game_status_update", // para i18n
  "params": {"phase": "night"},
  "data": {
    "game_id": "game-123",
    "phase": "night",
    "players": [
      {
        "id": "user1",
        "name": "Player1",
        "is_alive": true,
        "is_connected": true,
        "role": "villager"
      }
    ],
    "connected_players": ["user1", "user2"],
    "living_players": ["user1", "user2"],
    "dead_players": [],
    "time_remaining": 45
  },
  "timestamp": "2025-01-30T22:00:00Z"
}
```

### 7. Heartbeat/Ping

#### HEARTBEAT (Envío/Recepción)
Para mantener la conexión viva:
```json
{
  "type": "heartbeat",
  "timestamp": "2025-01-30T22:00:00Z"
}
```

Respuesta del servidor:
```json
{
  "type": "heartbeat",
  "response": "pong",
  "timestamp": "2025-01-30T22:00:00Z"
}
```

### 8. Manejo de Errores

#### ERROR
Se recibe cuando ocurre un error:
```json
{
  "type": "error",
  "error_code": "INVALID_MESSAGE",
  "message": "Tipo de mensaje requerido",
  "details": {},
  "timestamp": "2025-01-30T22:00:00Z"
}
```

**Códigos de error comunes:**
- `INVALID_MESSAGE`: Mensaje mal formado
- `INVALID_MESSAGE_TYPE`: Tipo de mensaje no válido
- `CONNECTION_NOT_FOUND`: Conexión no encontrada
- `USER_NOT_FOUND`: Usuario no encontrado
- `GAME_NOT_FOUND`: Juego no encontrado
- `VOTE_FAILED`: Error en votación
- `INTERNAL_ERROR`: Error interno del servidor
- `INVALID_TOKEN`: Token inválido
- `NO_PERMISSIONS`: Sin permisos para la acción

#### SUCCESS
Se recibe para confirmar acciones exitosas:
```json
{
  "type": "success",
  "action": "vote_cast",
  "message": "Voto registrado correctamente",
  "data": {},
  "timestamp": "2025-01-30T22:00:00Z"
}
```

---

## Eventos de Roles Especiales

### ROLE_ACTION
Para acciones específicas de roles:
```json
{
  "type": "role_action",
  "actor_id": "user123",
  "action": "see", // see, heal, poison, shoot, etc
  "target_id": "user456",
  "timestamp": "2025-01-30T22:00:00Z"
}
```

### PLAYER_ELIMINATED
Cuando un jugador es eliminado:
```json
{
  "type": "player_eliminated",
  "player_id": "user123",
  "player_name": "PlayerName",
  "role": "villager",
  "elimination_type": "vote", // vote, night_kill, poison, etc
  "timestamp": "2025-01-30T22:00:00Z"
}
```

---

## Funcionalidades Automáticas

### 1. Auto-inicio de Juegos
- Cuando se alcanza el número máximo de jugadores, el juego se inicia automáticamente
- Se envía mensaje `GAME_STARTED` a todos los conectados

### 2. Heartbeat Automático
- El servidor envía pings cada 30 segundos
- Conexiones que no respondan son eliminadas automáticamente

### 3. Gestión de Rooms
- Los jugadores se agrupan automáticamente por `game_id`
- Los mensajes se envían solo a jugadores del mismo juego
- Desconexiones se notifican automáticamente al resto

### 4. Sistema de Fases
- Cambios de fase automáticos con timers
- Notificaciones de tiempo restante
- Callbacks para eventos de fase

---

## Implementación Frontend Recomendada

### 1. Manejo de Conexión
```javascript
class GameWebSocket {
  constructor(gameId, token) {
    this.gameId = gameId;
    this.token = token;
    this.ws = null;
    this.eventHandlers = {};
  }

  connect() {
    const url = `ws://localhost:8000/ws/${this.gameId}?token=${this.token}`;
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.sendMessage({ type: 'join_game' });
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    const handler = this.eventHandlers[message.type];
    if (handler) {
      handler(message);
    }
  }

  on(eventType, handler) {
    this.eventHandlers[eventType] = handler;
  }

  sendMessage(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}
```

### 2. Uso en Vue Component
```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const gameWs = ref(null)
const players = ref([])
const currentPhase = ref('')
const timeRemaining = ref(0)

onMounted(() => {
  // Asumir que ya tienes token y gameId
  gameWs.value = new GameWebSocket(gameId, token)
  
  // Registrar handlers
  gameWs.value.on('player_connected', (message) => {
    // Actualizar lista de jugadores
  })
  
  gameWs.value.on('phase_changed', (message) => {
    currentPhase.value = message.phase
  })
  
  gameWs.value.on('phase_timer', (message) => {
    timeRemaining.value = message.time_remaining
  })
  
  gameWs.value.on('system_message', (message) => {
    if (message.data?.players) {
      players.value = message.data.players
    }
  })
  
  gameWs.value.connect()
})

onUnmounted(() => {
  gameWs.value?.ws?.close()
})
</script>
```

### 3. Manejo de Estados
Se recomienda usar un store (Pinia/Vuex) para manejar el estado del juego compartido entre componentes.

---

## Notas Importantes

1. **Autenticación Obligatoria**: Todas las conexiones requieren un token válido
2. **Reconexión**: Implementar lógica de reconexión automática en caso de desconexión
3. **Manejo de Errores**: Siempre manejar mensajes de error apropiadamente
4. **Heartbeat**: Responder a pings del servidor para mantener conexión
5. **JSON Válido**: Todos los mensajes deben ser JSON válido
6. **Case Sensitive**: Los tipos de mensajes son sensibles a mayúsculas/minúsculas
7. **CORS**: El backend ya está configurado para localhost:5173 y 5174 (Vite)

---

## Códigos de Cierre WebSocket

- **4000**: Error interno del servidor
- **4001**: Token inválido o usuario no encontrado
- **1000**: Cierre normal
- **1006**: Conexión perdida inesperadamente
