
# Especificación mínima de mensajes WebSocket (ws-messages)

Este documento es una especificación de referencia para los mensajes que el frontend puede recibir por WebSocket desde el backend. Importante: las comunicaciones que modifican el estado de la aplicación deben realizarse mediante las llamadas HTTP/REST al backend; el WebSocket se usa exclusivamente para que el backend notifique a los clientes los cambios (broadcasts, eventos y estados).

Este archivo es de consulta para desarrolladores y no modifica el comportamiento en tiempo de ejecución por sí mismo.

Principios clave: **REST (mutaciones) y WS (notificaciones).**
- Frontend -> Backend: usar la API REST para acciones que cambian estado (votar, usar habilidad, unirse formalmente a una partida, etc.).
- Backend -> Frontend: usar WebSocket para notificar a todos los clientes de una partida sobre cambios de estado (estado del juego, jugadores conectados/desconectados, resultados de acciones).
- Correlación: cuando se precise respuesta por WebSocket a una petición, incluir `request_id` en la petición HTTP o en el mensaje WS para correlacionar replies.

Tipos mínimos y ejemplos

- heartbeat
  - Propósito: mantener la conexión viva y medir latencia.
  - Dirección: bidireccional (cliente <-> servidor)
  - Ejemplo:
    { "type": "heartbeat", "timestamp": 1690000000000 }

- join_game
  - Propósito: notificación de que un usuario ha entrado en la partida.
  - Dirección: servidor -> clientes de la partida (broadcast). No usar como mecanismo primario para cambiar estado en el servidor; en su lugar, el cliente debe llamar al endpoint REST correspondiente para unirse.
  - Payload ejemplo (broadcast):
    { "type": "player_joined", "game_id": "g-abc", "player": { "id": "u-1", "username": "ana", "status": "in_game", "alive": true } }

- get_game_status
  - Propósito: petición/consulta del estado actual de la partida.
  - Recomendación: priorizar una llamada REST para obtener el estado canonico (`GET /games/{game_id}/status`). Permitir también una petición WS de solo lectura si es necesaria para diagnósticos.
  - Ejemplo de respuesta WS (si se usa):
    { "type": "game_status", "request_id": "req-1", "game_status": { "game_id": "g-abc", "phase": "waiting", "players": [...] } }

- player_connected / player_disconnected
  - Propósito: notificaciones broadcast sobre la conexión/estado de un jugador.
  - Dirección: servidor -> clientes de la partida
  - Ejemplo player_connected:
    { "type": "player_connected", "game_id": "g-abc", "player": { "id": "u-2", "username": "juan", "status": "connected", "alive": true } }
  - Ejemplo player_disconnected:
    { "type": "player_disconnected", "game_id": "g-abc", "player_id": "u-3", "reason": "transport_close" }

Convenciones y buenas prácticas
- Mensajes planos: preferir estructuras planas y objetos claros (`player`, `game_status`).
- Versionado: incluir opcionalmente `version` o `schema_version` en mensajes críticos para facilitar compatibilidad.
- Correlación: usar `request_id` cuando el cliente necesite correlacionar respuestas o events.
- Mapeo en cliente: el adaptador WS debe mapear los `type` del backend a constantes internas del frontend (por ejemplo `PLAYER_CONNECTED`, `GAME_STATUS_UPDATE`).
- Error handling: los mensajes de error del backend deben usar un tipo `error` con `code` y `message`:
  { "type": "error", "code": "INVALID_ACTION", "message": "You cannot vote now", "request_id": "req-2" }

Notas de implementación
- No cambiar la URL de conexión WS en este documento; el adaptador debe mantener compatibilidad con la conexión actual.
- El frontend debe confiar en la API REST para mutaciones. El WS es fuente de verdad para notificaciones en tiempo real.
- Evitar duplicar lógica: tras una acción HTTP satisfactoria, esperar el broadcast del backend para actualizar el estado compartido; usar optimistic UI sólo con rollback claro.

Referencias
- Handlers backend: `backend/app/services/game_state_service.py`, `backend/app/websocket/game_handlers.py`
- Plan de compatibilidad: `Docs/WEBSOCKET_COMPATIBILITY_PLAN.md`

---
Archivo actualizado para reflejar la política: Frontend usa API (REST) para cambios; WebSocket solo para notificaciones.
