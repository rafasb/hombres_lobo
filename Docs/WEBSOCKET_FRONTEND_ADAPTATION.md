# Adaptación del WebSocket Frontend

## Resumen de Cambios

Se ha adaptado el sistema WebSocket del frontend para seguir los principios de arquitectura definidos donde:

1. **El frontend solo RECIBE mensajes del backend vía WebSocket**
2. **El frontend solo RESPONDE a mensajes de heartbeat (único mensaje saliente)**
3. **Todas las interacciones del usuario deben generar llamadas a la API, no mensajes WebSocket**
4. **Los tipos de mensajes están sincronizados con `backend/app/websocket/messages_types.py`**

## Archivos Modificados

### `frontend/src/websocket/BaseWebSocketManager.ts`

#### Cambios Principales:

1. **Imports actualizados:**
   - Cambió de `WebSocketMessage` genérico a `GameWebSocketMessage` tipado
   - Añadido `WebSocketMessageMap` para tipado estricto

2. **Método `subscribe` mejorado:**
   - Ahora tiene tipado estricto basado en `WebSocketMessageMap`
   - Garantiza que los handlers reciban el tipo correcto de payload

3. **Método `dispatchMessage` refactorizado:**
   - Maneja automáticamente los mensajes de heartbeat
   - Mejor validación de estructura de mensajes
   - Tipado más estricto

4. **Gestión de Heartbeat:**
   - Eliminado el heartbeat proactivo (frontend no inicia heartbeats)
   - Añadido `handleHeartbeat()` para responder automáticamente
   - Implementado `sendHeartbeatResponse()` abstracto

5. **Método `cleanup()` añadido:**
   - Limpieza centralizada de recursos
   - Detiene timers de heartbeat response
   - Limpia handlers de mensajes

#### Principios Implementados:

- **Solo Recepción:** El frontend solo procesa mensajes entrantes
- **Solo Respuesta a Heartbeat:** Única comunicación saliente permitida
- **Tipado Estricto:** Sincronización con tipos del backend
- **Gestión Automática:** Respuesta automática a heartbeat sin intervención manual

### `frontend/src/websocket/WebSocketManager.ts`

#### Cambios Principales:

1. **Eliminación del método `send()`:**
   - Ya no es posible enviar mensajes arbitrarios
   - Solo se permite respuesta a heartbeat

2. **Implementación de `sendHeartbeatResponse()`:**
   - Única forma de enviar mensajes al backend
   - Respuesta automática cuando se recibe heartbeat del backend

3. **Simplificación de conexión:**
   - Eliminado el inicio proactivo de heartbeat
   - El heartbeat es manejado automáticamente por la clase base

4. **Mejor gestión de cleanup:**
   - Llamada a `cleanup()` en desconexión
   - Gestión correcta de timers y recursos

## Tipos de Mensajes Sincronizados

Los tipos de mensajes están ahora completamente sincronizados con el backend:

### Mensajes de Conexión:
- `player_connected`, `player_disconnected`, `player_banned`
- `user_status_changed`, `user_connection_status`

### Mensajes de Juego:
- `game_started`, `game_ended`, `game_restarted`
- `phase_changed`, `phase_timer`
- `game_status`, `game_connection_state`

### Mensajes de Votación:
- `voting_started`, `voting_ended`, `vote_cast`
- `voting_results`

### Mensajes de Roles:
- `role_action`, `night_action`
- `player_eliminated`, `player_role_revealed`

### Mensajes del Sistema:
- `heartbeat`, `error`, `success`, `system_message`
- `players_status_update`

## Flujo de Comunicación

### Antes (Bidireccional):
```
Frontend ↔ WebSocket ↔ Backend
      ↓
   También envía mensajes de comando
```

### Después (Solo Recepción + Heartbeat Response):
```
Frontend ← WebSocket ← Backend (solo recibe)
      ↓
   heartbeat response (única excepción)
      ↓
Frontend → API → Backend (para acciones del usuario)
```

## Beneficios de la Adaptación

1. **Arquitectura Más Clara:** Separación clara entre comunicación en tiempo real (WebSocket) y acciones del usuario (API)

2. **Mejor Tipado:** Sincronización estricta con los tipos del backend

3. **Menos Complejidad:** El frontend no necesita manejar el envío de comandos vía WebSocket

4. **Más Robusto:** Gestión automática de heartbeat sin intervención manual

5. **Escalabilidad:** Facilita la implementación de features sin tocar el WebSocket

## Próximos Pasos

1. **Actualizar Stores de Pinia:** Adaptar los stores para usar solo recepción WebSocket + API calls

2. **Revisar Componentes:** Asegurar que los componentes usen API calls para acciones del usuario

3. **Testing:** Verificar que la comunicación funciona correctamente con el backend

4. **Documentación:** Actualizar la documentación de desarrollo para reflejar estos cambios
