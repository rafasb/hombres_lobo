# Plan de Adaptación WebSocket Frontend-Backend

## 📋 Incompatibilidades Identificadas

### 1. URL del Endpoint
- **Frontend**: `ws://localhost:8000/ws/games/{gameId}`
- **Backend**: `ws://localhost:8000/ws/{gameId}`
- **Solución**: Adaptar frontend para usar la URL correcta del backend

### 2. Tipos de Mensajes - Heartbeat
- **Frontend**: `ping/pong`
- **Backend**: `heartbeat`
- **Solución**: Adaptar frontend para usar `heartbeat`

### 3. Tipos de Mensajes - Estado del Juego
- **Frontend**: `get_game_state`
- **Backend**: `get_game_status`
- **Solución**: Adaptar frontend para usar `get_game_status`

### 4. Mensajes de Unión al Juego
- **Frontend**: `user_joined_lobby`
- **Backend**: `join_game`
- **Solución**: Adaptar frontend para usar `join_game`

### 5. Estructura de Respuestas
- **Frontend espera**: `game_connection_state`, `players_status_update`
- **Backend envía**: `system_message` con data específica
- **Solución**: Crear adaptadores en el frontend

## 🔧 Cambios Requeridos

### A. En el Frontend

#### 1. WebSocketManager.ts
- Cambiar URL de conexión
- Adaptar tipos de mensajes heartbeat
- Crear adaptadores para mensajes del backend

#### 2. useGameConnection.ts
- Cambiar `get_game_state` → `get_game_status`
- Cambiar `user_joined_lobby` → `join_game`
- Adaptar handlers de mensajes

### B. En el Backend (Opcional - Extensiones)

#### 1. Añadir tipos de mensaje adicionales
- `GAME_CONNECTION_STATE`
- `PLAYERS_STATUS_UPDATE`
- `USER_CONNECTION_STATUS`

#### 2. Crear handlers específicos para el frontend
- Handler para estado de conexión de jugadores
- Handler para actualizaciones de estado específicas

## 📝 Prioridad de Implementación

1. **ALTA**: Adaptar URLs y tipos de mensaje básicos en frontend
2. **MEDIA**: Crear adaptadores de mensajes en frontend
3. **BAJA**: Añadir tipos de mensaje específicos en backend

## 🎯 Resultado Esperado

Después de las adaptaciones:
- Frontend podrá conectarse correctamente al backend
- Heartbeat funcionará correctamente
- Estado del juego se sincronizará apropiadamente
- Compatibilidad completa entre ambos sistemas
