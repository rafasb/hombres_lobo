# GameResponse y GameResponsesService - Documentación

## Descripción General

Se han creado nuevas clases y servicios para manejar respuestas públicas de partidas que pueden ser compartidas con todos los jugadores sin revelar información sensible como roles o acciones nocturnas.

## Clases Creadas

### 1. PublicPlayerInfo
**Archivo:** `backend/app/models/game_responses.py`

Información pública de un jugador que puede ser compartida con todos los participantes:
- `player_id`: ID único del jugador
- `username`: Nombre de usuario visible
- `is_alive`: Estado vital del jugador
- `is_connected`: Estado de conexión actual
- `user_status`: Estado del usuario (connected, disconnected, in_game)

### 2. GameResponse
**Archivo:** `backend/app/models/game_responses.py`

Respuesta completa del estado de una partida con información pública:
- **Información básica:** game_id, name, creator_id, creator_name
- **Estado actual:** status, current_round, is_first_night
- **Información de jugadores:** max_players, current_players, players (lista de PublicPlayerInfo)
- **Estadísticas:** eliminated_players, connected_players_count
- **Metadatos:** success, message, created_at

### 3. GameStateUpdateResponse
**Archivo:** `backend/app/models/game_responses.py`

Respuesta simplificada para actualizaciones de estado via WebSocket:
- Incluye solo los campos que cambian frecuentemente
- Optimizada para mensajes WebSocket
- Incluye `update_type` y `timestamp` para identificar el tipo de actualización

## Servicio Principal: GameResponsesService

### Archivo: `backend/app/services/game_responses_service.py`

Servicio principal que contiene métodos estáticos para construir las respuestas públicas:

#### Métodos Principales:

1. **build_public_player_info(player_id, user, game)**
   - Construye información pública de un jugador específico

2. **build_public_players_list(game, users_dict)**
   - Construye lista de información pública de todos los jugadores

3. **build_game_response(game, users_dict, success, message)**
   - Construye respuesta completa del estado de la partida

4. **build_game_state_update(game, users_dict, update_type)**
   - Construye respuesta simplificada para actualizaciones

5. **get_game_response_by_id(game_id, success, message)**
   - Obtiene respuesta completa de partida por ID (incluye carga de datos)

6. **get_game_state_update_by_id(game_id, update_type)**
   - Obtiene actualización de estado por ID

#### Métodos Especializados para WebSocket:

7. **create_player_connection_update(game_id, player_id, is_connected)**
   - Actualización para cambios de conexión de jugadores

8. **create_phase_change_update(game_id, new_phase)**
   - Actualización para cambios de fase del juego

9. **create_player_elimination_update(game_id, eliminated_player_id)**
   - Actualización para eliminación de jugadores

## Archivos de Soporte

### Tests Unitarios
**Archivo:** `backend/test_game_responses_service.py`
- Tests completos para todos los métodos del servicio
- Mocks para dependencias externas
- Validación de casos edge y errores

### Ejemplos de Uso
**Archivo:** `backend/app/examples/game_responses_usage.py`
- Ejemplos de endpoints FastAPI
- Implementación de WebSocket manager
- Patrones de uso en diferentes escenarios

### Ejemplos de Datos
**Archivo:** `backend/app/models/game_response_examples.py`
- Ejemplos de construcción de objetos
- Función helper para construcción desde objetos Game y User
- Scripts de prueba y validación

## Casos de Uso

### 1. Endpoints de API
```python
@router.get("/{game_id}/status", response_model=GameResponse)
async def get_game_status(game_id: str) -> GameResponse:
    game_response = GameResponsesService.get_game_response_by_id(game_id)
    if not game_response:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_response
```

### 2. Mensajes WebSocket
```python
# Enviar actualización de estado a todos los jugadores
state_update = GameResponsesService.get_game_state_update_by_id(game_id, "phase_change")
message = {"type": "game_update", "data": state_update.model_dump()}
await websocket.send_json(message)
```

### 3. Notificaciones de Eventos
```python
# Notificar cambio de fase
update = GameResponsesService.create_phase_change_update(game_id, GameStatus.DAY)

# Notificar eliminación de jugador
update = GameResponsesService.create_player_elimination_update(game_id, player_id)

# Notificar cambio de conexión
update = GameResponsesService.create_player_connection_update(game_id, player_id, True)
```

## Beneficios

1. **Seguridad:** No expone información sensible como roles o acciones nocturnas
2. **Eficiencia:** Respuestas optimizadas para diferentes casos de uso
3. **Consistencia:** Estructura uniforme para todas las respuestas públicas
4. **Flexibilidad:** Métodos especializados para diferentes tipos de actualizaciones
5. **Testabilidad:** Servicios bien estructurados con tests completos
6. **Documentación:** Ejemplos claros de implementación y uso

## Próximos Pasos

1. **Integración con endpoints existentes:** Actualizar endpoints actuales para usar GameResponse
2. **Implementación WebSocket:** Integrar con el sistema WebSocket existente
3. **Optimización:** Añadir caché si es necesario para partidas muy activas
4. **Logs:** Añadir logging para debugging y monitoreo
5. **Validación:** Añadir validaciones adicionales según requisitos específicos

## Dependencias

- `app.models.game_and_player`: Para tipos Game, GameStatus, PlayerInfo
- `app.models.user`: Para tipos User, UserStatus
- `app.services.game_service`: Para get_game()
- `app.services.user_service`: Para UserService.get_user()
- `pydantic`: Para validación y serialización de modelos
- `datetime`: Para timestamps

## Notas de Implementación

- Todos los servicios son métodos estáticos para facilitar el uso
- Los datos son copiados (no referenciados) para evitar modificaciones accidentales
- Las respuestas incluyen metadatos para facilitar el manejo en el frontend
- El diseño permite extensiones futuras sin breaking changes
