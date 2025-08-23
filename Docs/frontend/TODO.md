# TODO - Proyecto Hombres Lobo

Resumen breve (estado actual)
- Se centralizó el cliente HTTP en `src/services/api.ts` con un interceptor que añade el Authorization header.
- Se refactorizaron servicios para usar `api` y reducir lecturas repetidas de `localStorage`.
- Se añadió `src/services/errorHelper.ts` para normalizar mensajes de error.
- Se reemplazaron varios `any` en `src/services` por tipos concretos y se exportaron tipos nuevos (`VoteCount`, `CastVoteResponse`).
- Se creó el componente presentacional `GameCard.vue` y se refactorizó `GamesListView.vue` (cambios previos).
- Se tipó `ConnectionStatus.vue` y se arreglaron problemas de reactividad en vistas relacionadas.

Prioridad inmediata (hacer en orden)
1. Revisar y tipar los mensajes de WebSocket en `src/composables/useGameConnection.ts` y `src/types/websocket.ts`.
   - Definir interfaces para `SystemMessage`, `UserStatusChange`, `HeartbeatMessage`, etc.
   - Reemplazar `any` por `unknown` y añadir type guards antes de mapear datos.
   - Tiempo estimado: 1-2 horas.

2. Barrido por componentes y vistas para eliminar `any` restantes y ajustar props/emits:
   - Priorizar `src/components` y `src/views` que procesan respuestas de la API o WS.
   - Añadir tests unitarios mínimos (donde sea trivial) para composables críticos.
   - Tiempo estimado: 2-4 horas (dependiendo del alcance).

3. Mejorar el manejo del token (opcional, recomendable): crear un "token provider" o inicializar `api` después de Pinia.
   - Opciones:
     - `api.setToken(token)` y llamar desde `authStore.setToken`
     - o reimportar `api` en runtime cuando Pinia esté listo (evitar ciclos)
   - Beneficio: eliminar dependencia de `localStorage` como única fuente y facilitar refresh token.
   - Tiempo estimado: 1-2 horas.

4. Centralizar y documentar contratos de API (mini-README o comments) para endpoints usados (games, users, ws).

Tareas de calidad / mantenimiento
- Añadir tests unitarios para `useStatusHelpers`, `useGamesList` y `GameCard`.
- Crear una tarea de CI que ejecute `npm run build` y `npm run lint`.
- Considerar un `axios` instance con manejo de refresh token y reintentos (exponiendo hooks).

Notas prácticas y comandos útiles
- Build local rápida: `npm run build` (desde la carpeta `frontend`).
- Ejecutar dev: `npm run dev`.

Decisiones tomadas / razones
- Se eligió leer `access_token` desde `localStorage` en el interceptor para evitar ciclos de importación con Pinia.
  Si se prefiere usar Pinia como fuente única, implementar `api.setToken()` y actualizar `authStore.setToken`.

Siguiente paso recomendado ahora
- Empezar por tipar los mensajes de WebSocket (Prioridad 1). Puedo hacerlo ahora: definir tipos, agregar guards y actualizar `useGameConnection.ts` en pequeños commits.

Si quieres que empiece con eso, dime y lo implemento paso a paso.
