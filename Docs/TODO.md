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

1) [Front] Crear rama de trabajo
- Tarea: crear rama git para la migración: migracion/comunicacion-pinia
- Verificación: `git checkout -b migracion/comunicacion-pinia` y `git status` (no cambia la app)
- Referencias: [Docs/TODO.md](Docs/TODO.md)

2) [Back] Crear rama backend sincronizada y establecer CI local
- Tarea: crear rama backend: migracion/comunicacion-pinia-back, añadir job CI local (pytest) y ejecutar tests básicos.
- Verificación: `git checkout -b migracion/comunicacion-pinia-back` y `cd backend && pytest -q`
- Referencias: tests websocket [`backend/test_websocket_fixed.py`](backend/test_websocket_fixed.py), [`backend/test_websocket_status.py`](backend/test_websocket_status.py)

3) [Front] Añadir especificación mínima de mensajes WebSocket (documento local)
- Tarea: añadir archivo de especificación breve en `frontend/src/services/ws-messages.md` con tipos `heartbeat`, `join_game`, `get_game_status`, `player_connected`, `player_disconnected`.
- Verificación: abrir el archivo y confirmar contenido; no hay cambio en runtime.
- Referencias: backend handlers [`game_state_service`](backend/app/services/game_state_service.py) and [`game_handlers`](backend/app/websocket/game_handlers.py).

4) [Back] Alinear tipos de mensaje y comandos en backend
- Tarea: revisar/añadir aliases y adaptadores en backend para soportar los comandos esperados por el frontend (`get_game_status`, `join_game`, `heartbeat`) y emitir tipos compatibles (`GAME_CONNECTION_STATE`, `PLAYERS_STATUS_UPDATE`, `USER_CONNECTION_STATUS`).
- Verificación: ejecutar tests unitarios y un cliente WS de prueba que envíe `get_game_status`/`join_game` a `ws://localhost:8000/ws/{game_id}?token={access_token}`.
- Referencias: handlers [`backend/app/websocket/game_handlers.py`](backend/app/websocket/game_handlers.py), mensajes de referencia [`backend/app/websocket/copilot-ws-messages.md`](backend/app/websocket/copilot-ws-messages.md)

5) [Front] Crear stores Pinia (esqueleto) para User y Player
- Tarea: añadir archivos `frontend/src/stores/user.ts` y `frontend/src/stores/player.ts` con estado y mutaciones mínimas (export default store vacío/estable por defecto).
- Verificación: arrancar frontend dev server (`npm run dev`) y confirmar que compila sin errores.
- Referencias: ejemplo store existente [`frontend/src/stores/games.ts`](frontend/src/stores/games.ts) y store de auth [`frontend/src/stores/auth.ts`](frontend/src/stores/auth.ts).

6) [Back] Exponer endpoints REST y documentar en OpenAPI
- Tarea: asegurar que los endpoints necesarios para las mutaciones (ej. votar, join/leave, usar habilidad) existen y están documentados en [`openapi.json`](openapi.json). Si falta alguno, crearlo en `app/api/`.
- Verificación: abrir `http://localhost:8000/docs` y comprobar los endpoints; ejecutar llamadas curl para validar.
- Referencias: [openapi.json](openapi.json), rutas objetivo: [`app/api/routes_game_flow.py`](backend/app/api/routes_game_flow.py) (documentado en [Docs/SISTEMA_UNIFICADO.md](Docs/SISTEMA_UNIFICADO.md))

7) [Front] Integración ligera en componente de lobby / PlayersGrid (lectura sólo)
- Tarea: modificar temporalmente el componente que muestra jugadores para que lea desde `user`/`player` stores, sin alterar lógica de envío. (Ej. en [`PlayersGrid.vue`](frontend/src/components/game/PlayersGrid.vue) añadir bindings a los stores).
- Verificación: la UI visual no debe cambiar fuera de usar datos desde Pinia; probar sala de espera localmente.
- Referencias: [`PlayersGrid.vue`](frontend/src/components/game/PlayersGrid.vue), stores: [`frontend/src/stores/user.ts`](frontend/src/stores/user.ts), [`frontend/src/stores/player.ts`](frontend/src/stores/player.ts).

8) [Back] Emitir broadcasts consistentes desde el servicio de estado de juego
- Tarea: en [`backend/app/services/game_state_service.py`](backend/app/services/game_state_service.py) asegurar que, tras mutaciones REST, se emite un broadcast WS con la forma esperada por frontend (usar adaptadores si es necesario).
- Verificación: ejecutar flujo: HTTP mutación → backend procesa → backend envía broadcast → cliente WS de prueba recibe `GAME_CONNECTION_STATE`/`PLAYERS_STATUS_UPDATE`.
- Referencias: [`backend/app/services/game_state_service.py`](backend/app/services/game_state_service.py), handlers [`backend/app/websocket/game_handlers.py`](backend/app/websocket/game_handlers.py)

9) [Front] Añadir adaptadores en cliente WebSocket (sin cambiar URL)
- Tarea: en `frontend/src/services/WebSocketManager.ts` añadir handlers que conviertan mensajes backend (`system_message`, `player_connected`, ...) a la forma interna esperada (`GAME_CONNECTION_STATE`, `USER_CONNECTION_STATUS`, `PLAYERS_STATUS_UPDATE`). No cambiar la conexión actual.
- Verificación: conectar cliente en entorno dev y comprobar en consola que los mensajes se adaptan, sin romper la conexión.
- Referencias: [`WebSocketManager`](frontend/src/services/WebSocketManager.ts), plan de incompatibilidades [Docs/WEBSOCKET_COMPATIBILITY_PLAN.md](Docs/WEBSOCKET_COMPATIBILITY_PLAN.md).

10) [Back] Robustecer Connection Manager y manejo de websockets cerrados
- Tarea: aplicar las correcciones de [`Docs/WEBSOCKET_BACKEND_FIXES.md`](Docs/WEBSOCKET_BACKEND_FIXES.md): comprobar `connection_manager` en [`backend/app/connection_manager.py`](backend/app/connection_manager.py) para no enviar a sockets cerrados, limpiar conexiones muertas y mejorar heartbeat server-side.
- Verificación: ejecutar tests websocket (`backend/test_websocket_fixed.py`, `backend/test_websocket_status.py`) y revisar logs para errores "Need to call accept first" o envío a sockets cerrados.
- Referencias: [`backend/app/connection_manager.py`](backend/app/connection_manager.py), [Docs/WEBSOCKET_BACKEND_FIXES.md](Docs/WEBSOCKET_BACKEND_FIXES.md)

11) [Front] Consumir actualizaciones WebSocket para poblar Pinia (lectura)
- Tarea: cuando el WebSocket reciba actualizaciones adaptadas, actualizar solo el estado de lectura en los stores `user`/`player` (acciones tipo `setPlayers`, `setUserStatus`) sin condicionar lógica de envío.
- Verificación: al emitir un evento de prueba desde backend, los stores se actualizan y la UI refleja cambios.
- Referencias: [`useGameConnection`](frontend/src/composables/useGameConnection.ts), adaptadores [Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md](Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md).

12) [Back] Integración tests: End-to-end backend WS + REST
- Tarea: crear tests de integración que simulen: 1) cliente hace POST a endpoint REST, 2) backend actualiza estado y 3) backend broadcast via WS a otros clientes. Añadir a `backend/tests/integration/`.
- Verificación: `cd backend && pytest backend/tests/integration -q` y confirmar flujo.
- Referencias: tests existentes [`backend/test_websocket_fixed.py`](backend/test_websocket_fixed.py)

13) [Front] Migrar llamadas que causan cambios de estado a API (separado, controlado)
- Tarea: identificar llamadas actuales que modifican estado en tiempo real y, por cada una, cambiar el flujo para que primero invoque el endpoint REST correspondiente (p. ej. votar, usar habilidad), dejando el backend responsable de notificar el resto vía WebSocket.
- Verificación: realizar la acción en UI → HTTP 200/201 del backend y luego recibir broadcast WebSocket que sincronice el estado en todos los clientes. Ejecutar tests de backend (`pytest -q`) y verificar que no se rompen.
- Referencias: endpoints documentados en `openapi.json` y servicios en frontend [`frontend/src/services/api.ts`](frontend/src/services/api.ts) (o similar).

14) [Back] Validación de permisos y seguridad en endpoints REST
- Tarea: asegurar que las mutaciones REST validan permisos/estado de fase (ej. no permitir votar fuera de fase) y usar dependencias de seguridad (`backend/app/core/security.py` o similares).
- Verificación: pruebas unitarias de reglas de negocio y revisión de OpenAPI para códigos HTTP correctos.
- Referencias: rutas de flujo [`backend/app/api/routes_game_flow.py`](backend/app/api/routes_game_flow.py), servicios [`backend/app/services/game_state_service.py`](backend/app/services/game_state_service.py)

15) [Front] Validación y limpieza incremental
- Tarea: por cada endpoint migrado, eliminar la lógica cliente que duplicaba cambios (ej. actualizar local store inmediatamente) y confiar en la notificación del backend. Mantener un fallback temporal (optimistic UI) solo si hay rollback manejado.
- Verificación: pruebas manuales en sala de espera / juego y ejecución de la suite de tests backend (`backend/tests/`) para asegurar integridad. Ejecutar `npm run build` (preview) para asegurar que el frontend compila.

16) [Back] Telemetría y logs para debugging de WS/REST flujo
- Tarea: añadir logs estructurados en puntos críticos: recepción de comando REST, procesamiento de mutación, broadcast WS, errores de envío, reconexiones. Considerar contador de intentos y métricas simples.
- Verificación: revisar logs durante pruebas end-to-end y confirmar trazabilidad completa (request_id correlacionado).
- Referencias: puntos en [`backend/app/websocket/game_handlers.py`](backend/app/websocket/game_handlers.py) y [`backend/app/services/game_state_service.py`](backend/app/services/game_state_service.py)

17) [Front] Harden backend WebSocket (asegurarse de no enviar a websockets cerrados)
- Tarea: revisar/ejecutar las correcciones ya propuestas en [Docs/WEBSOCKET_BACKEND_FIXES.md](Docs/WEBSOCKET_BACKEND_FIXES.md) (p. ej. [`connection_manager`](backend/app/connection_manager.py) verificaciones antes de enviar).
- Verificación: ejecutar tests específicos websocket (`backend/test_websocket_fixed.py`, `backend/test_websocket_status.py`) y confirmar que pasan.

18) [Back] Manejo de versionado de protocolo y adaptadores backwards-compatible
- Tarea: introducir un campo `protocol_version` o `client_version` en los mensajes WS y handlers para permitir adaptadores en backend que mantengan retrocompatibilidad con frontends antiguos.
- Verificación: simular clientes con versiones diferentes y comprobar que los adaptadores transforman mensajes correctamente.
- Referencias: documentación WS [`backend/app/websocket/copilot-ws-messages.md`](backend/app/websocket/copilot-ws-messages.md), adaptadores frontend [`frontend/src/services/WebSocketManager.ts`](frontend/src/services/WebSocketManager.ts)

19) [Front] Documentación y despliegue
- Tarea: actualizar documentación de integración (`Docs/WEBSOCKET_ADAPTATIONS_SUMMARY.md`, `Docs/TODO.md`) con los cambios y pasos para rollback.
- Verificación: abrir documentación y confirmar que refleja la arquitectura actual; una última validación: arranque conjunto `npm run dev` (frontend) y `uvicorn backend.app.main:app --reload` y prueba de flujo completo.

20) [Back] Despliegue controlado y rollback plan
- Tarea: preparar despliegue incremental (staging) con migración de dependencias WS/REST, incluir rollback scripts y feature-flags si es necesario.
- Verificación: desplegar en staging, ejecutar suite completa (`cd backend && pytest -q`) y tests de integración con frontend en staging; validar rollback.
- Referencias: despliegue y CI en `.github/workflows/` and [Docs/PLANIFICACION_GLOBAL.md](Docs/PLANIFICACION_GLOBAL.md)

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