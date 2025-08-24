# Cambio de estrategia de comunicación

Este documento pretende plantear un cambio en las estrategia de comunicación entre Frontend y Backend.

El principal objetivo es simplificar el proceso de comunicación, así como los mensajes e interacciones, manteniendo la funcionalidad de la aplicación.

Dado que existe una API con endpoints para la gestión de toda la información del juego, y que el flujo de la partida se gestiona en el backend, el frontend enviará la información mediante llamadas a la API, para actualizar la información de la base de datos del backend y activar los cambios de flujo de la partida, si es el caso.

Para permitir la interactividad entre los miembros de cada partida, será el backend el responsable de enviar mensajes a través del websocket a todos los miembros de una misma partida, cuando alguno de los datos asociados a los miembros de la partida o asociados a la partida hayan sido modificados.

El frontend, al recibir los mensajes del backend con las actualizaciones de los datos de la partida y sus participantes, almacenará esta información en local (usando Pinia).

Las modificaciones en los datos de pínia se realizarán mediante los stores siguientes Auth, (ya existente), User (para los datos de usuario: id, username, estado: connected, in_game, disconnected), Player (para la información del usuario relacionada con el juego, como el rol, vivo/muerto, etc).

Las modificaciones de datos en Pinia permitirán que los datos mostrados en los componentes VUE sean reactivos, actualizandose cuando se modifiquen en el store.

## Plan de trabajo para la migración (tareas pequeñas y verificables)

Objetivo: migrar la comunicación hacia el modelo propuesto (API para cambios; backend broadcast vía WebSocket) en pasos atómicos que permitan verificar que la aplicación sigue funcionando en cada paso.

1) Crear rama de trabajo
- Tarea: crear rama git para la migración: migracion/comunicacion-pinia
- Verificación: `git checkout -b migracion/comunicacion-pinia` y `git status` (no cambia la app)
- Referencias: [Docs/TODO.md](Docs/TODO.md)

2) Añadir especificación mínima de mensajes WebSocket (documento local)
- Tarea: añadir archivo de especificación breve en `frontend/src/services/ws-messages.md` con tipos `heartbeat`, `join_game`, `get_game_status`, `player_connected`, `player_disconnected`.
- Verificación: abrir el archivo y confirmar contenido; no hay cambio en runtime.
- Referencias: backend handlers [`game_state_service`](backend/app/services/game_state_service.py) and [`game_handlers`](backend/app/websocket/game_handlers.py).

3) Crear stores Pinia (esqueleto) para User y Player
- Tarea: añadir archivos `frontend/src/stores/user.ts` y `frontend/src/stores/player.ts` con estado y mutaciones mínimas (export default store vacío/estable por defecto).
- Verificación: arrancar frontend dev server (`npm run dev`) y confirmar que compila sin errores.
- Referencias: ejemplo store existente [`frontend/src/stores/games.ts`](frontend/src/stores/games.ts) y store de auth [`frontend/src/stores/auth.ts`](frontend/src/stores/auth.ts).

4) Integración ligera en componente de lobby / PlayersGrid (lectura sólo)
- Tarea: modificar temporalmente el componente que muestra jugadores para que lea desde `user`/`player` stores, sin alterar lógica de envío. (Ej. en [`PlayersGrid.vue`](frontend/src/components/game/PlayersGrid.vue) añadir bindings a los stores).
- Verificación: la UI visual no debe cambiar fuera de usar datos desde Pinia; probar sala de espera localmente.
- Referencias: [`PlayersGrid.vue`](frontend/src/components/game/PlayersGrid.vue), stores: [`frontend/src/stores/user.ts`](frontend/src/stores/user.ts), [`frontend/src/stores/player.ts`](frontend/src/stores/player.ts).

5) Añadir adaptadores en cliente WebSocket (sin cambiar URL)
- Tarea: en `frontend/src/services/WebSocketManager.ts` añadir handlers que conviertan mensajes backend (`system_message`, `player_connected`, ...) a la forma interna esperada (`GAME_CONNECTION_STATE`, `USER_CONNECTION_STATUS`, `PLAYERS_STATUS_UPDATE`). No cambiar la conexión actual.
- Verificación: conectar cliente en entorno dev y comprobar en consola que los mensajes se adaptan, sin romper la conexión.
- Referencias: [`WebSocketManager`](frontend/src/services/WebSocketManager.ts), plan de incompatibilidades [Docs/WEBSOCKET_COMPATIBILITY_PLAN.md](Docs/WEBSOCKET_COMPATIBILITY_PLAN.md).

6) Consumir actualizaciones WebSocket para poblar Pinia (lectura)
- Tarea: cuando el WebSocket reciba actualizaciones adaptadas, actualizar solo el estado de lectura en los stores `user`/`player` (acciones tipo `setPlayers`, `setUserStatus`) sin condicionar lógica de envío.
- Verificación: al emitir un evento de prueba desde backend, los stores se actualizan y la UI refleja cambios.
- Referencias: [`useGameConnection`](frontend/src/composables/useGameConnection.ts), adaptadores [Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md](Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md).

7) Migrar llamadas que causan cambios de estado a API (separado, controlado)
- Tarea: identificar llamadas actuales que modifican estado en tiempo real y, por cada una, cambiar el flujo para que primero invoque el endpoint REST correspondiente (p. ej. votar, usar habilidad), dejando el backend responsable de notificar el resto vía WebSocket.
- Verificación: realizar la acción en UI → HTTP 200/201 del backend y luego recibir broadcast WebSocket que sincronice el estado en todos los clientes. Ejecutar tests de backend (`pytest -q`) y verificar que no se rompen.
- Referencias: endpoints documentados en `openapi.json` y servicios en frontend [`frontend/src/services/api.ts`](frontend/src/services/api.ts) (o similar).

8) Validación y limpieza incremental
- Tarea: por cada endpoint migrado, eliminar la lógica cliente que duplicaba cambios (ej. actualizar local store inmediatamente) y confiar en la notificación del backend. Mantener un fallback temporal (optimistic UI) solo si hay rollback manejado.
- Verificación: pruebas manuales en sala de espera / juego y ejecución de la suite de tests backend (`backend/tests/`) para asegurar integridad. Ejecutar `npm run build` (preview) para asegurar que el frontend compila.

9) Harden backend WebSocket (asegurarse de no enviar a websockets cerrados)
- Tarea: revisar/ejecutar las correcciones ya propuestas en [Docs/WEBSOCKET_BACKEND_FIXES.md](Docs/WEBSOCKET_BACKEND_FIXES.md) (p. ej. [`connection_manager`](backend/app/connection_manager.py) verificaciones antes de enviar).
- Verificación: ejecutar tests específicos websocket (`backend/test_websocket_fixed.py`, `backend/test_websocket_status.py`) y confirmar que pasan.

10) Documentación y despliegue
- Tarea: actualizar documentación de integración (`Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md`, `Docs/TODO.md`) con los cambios y pasos para rollback.
- Verificación: abrir documentación y confirmar que refleja la arquitectura actual; una última validación: arranque conjunto `npm run dev` (frontend) y `uvicorn backend.app.main:app --reload` y prueba de flujo completo.

Notas de verificación comunes (rápidas)
- Frontend dev: `cd frontend && npm install && npm run dev` (ver puerto y consola).
- Backend tests: `cd backend && pytest -q` (verificar que suite existente sigue pasando).
- WebSocket manual test: usar script/simple client para conectar a `ws://localhost:8000/ws/{game_id}?token={access_token}` y enviar `get_game_status` / `join_game`.

Archivos y símbolos clave (consultar)
- Plan original: [Docs/TODO.md](Docs/TODO.md)  
- Frontend stores: [`frontend/src/stores/games.ts`](frontend/src/stores/games.ts), [`frontend/src/stores/auth.ts`](frontend/src/stores/auth.ts), [`frontend/src/stores/user.ts`](frontend/src/stores/user.ts), [`frontend/src/stores/player.ts`](frontend/src/stores/player.ts)  
- Frontend WebSocket: [`frontend/src/services/WebSocketManager.ts`](frontend/src/services/WebSocketManager.ts), [`frontend/src/composables/useGameConnection.ts`](frontend/src/composables/useGameConnection.ts)  
- Frontend component: [`frontend/src/components/game/PlayersGrid.vue`](frontend/src/components/game/PlayersGrid.vue)  
- Backend services/handlers: [`backend/app/services/game_state_service.py`](backend/app/services/game_state_service.py), [`backend/app/websocket/game_handlers.py`](backend/app/websocket/game_handlers.py), [`backend/app/connection_manager.py`](backend/app/connection_manager.py)  
- Documentación WebSocket: [Docs/WEBSOCKET_COMPATIBILITY_PLAN.md](Docs/WEBSOCKET_COMPATIBILITY_PLAN.md), [Docs/WEBSOCKET_BACKEND_FIXES.md](Docs/WEBSOCKET_BACKEND_FIXES.md), [Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md](Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md)

Al final de cada paso: confirmar que la app compila / tests pasan / operaciones manuales críticas funcionan antes de proceder al siguiente paso. Esto asegura cambios pequeños y reversibles y mantiene la aplicación funcional durante toda