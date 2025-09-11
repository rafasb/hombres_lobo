# Envío de Datos de Partida por WebSocket

## Resumen

Se ha implementado el envío automático de los datos de la partida (usando `GameResponse`) inmediatamente después del mensaje de bienvenida cuando un usuario se conecta por WebSocket a una partida.

## Cambios Implementados

### 1. Import del GameResponsesService

Se agregó el import necesario en `message_handlers.py`:

```python
from app.services.game_responses_service import GameResponsesService
```

### 2. Envío de Datos de Partida

Después del mensaje de bienvenida, se envía automáticamente un mensaje con los datos públicos de la partida:

```python
# Enviar datos de la partida usando GameResponse
try:
    game_response = GameResponsesService.get_game_response_by_id(game_id)
    if game_response:
        game_data_message = WebSocketMessageV2(
            type=MessageType.GAME_STATUS,
            data=game_response.dict(),
            timestamp=datetime.now()
        )
        
        await connection_manager.send_personal_message(
            connection_id,
            game_data_message
        )
        logger.info(f"Datos de partida enviados a usuario {user_id} en juego {game_id}")
    else:
        logger.warning(f"No se pudieron obtener datos de la partida {game_id} para usuario {user_id}")
except Exception as e:
    logger.error(f"Error enviando datos de partida a {user_id}: {e}")
```

## Flujo de Conexión Actualizado

1. **Verificación de token y usuario**
2. **Conexión al WebSocket**
3. **Actualización automática del estado de usuario a 'connected'**
4. **Envío del mensaje de bienvenida** (`SYSTEM_MESSAGE` con `CONNECTED_TO_GAME`)
5. **🆕 Envío de datos de la partida** (`GAME_STATUS` con datos de `GameResponse`)
6. **Inicio del loop de mensajes** (principalmente HEARTBEAT)

## Mensaje Enviado

**Tipo:** `GAME_STATUS`
**Estructura:**
```json
{
  "type": "game_status",
  "timestamp": "2025-09-09T10:30:00",
  "data": {
    "game_id": "uuid-de-la-partida",
    "name": "Nombre de la partida",
    "status": "waiting",
    "creator_id": "uuid-del-creador",
    "creator_name": "Nombre del creador",
    "max_players": 8,
    "current_players": 4,
    "connected_players_count": 3,
    "eliminated_players": 0,
    "current_round": 0,
    "is_first_night": false,
    "created_at": "2025-09-09T10:00:00",
    "players": [
      {
        "player_id": "uuid-jugador-1",
        "username": "Usuario1",
        "is_alive": true,
        "is_connected": true,
        "user_status": "in_game"
      }
    ],
    "success": true,
    "message": "Datos de partida obtenidos correctamente"
  }
}
```

## Beneficios

1. **Sincronización Inmediata**: El frontend recibe datos actualizados tan pronto como se conecta
2. **Información Completa**: Incluye jugadores, estado de conexión, configuración de partida
3. **Seguridad**: Solo se envían datos públicos usando `GameResponse`
4. **Manejo de Errores**: Logging completo de éxitos y fallos
5. **Compatibilidad**: Funciona con la estructura de mensajes WebSocket existente

## Frontend

El frontend puede escuchar el mensaje `game_status` para actualizar automáticamente los stores de Pinia:

```typescript
// En el WebSocket handler del frontend
subscribeToMessage('game_status', (data) => {
  if (data && data.success) {
    // Actualizar stores con los datos recibidos
    updateStoresWithGameData(data)
  }
})
```

## Notas Técnicas

- Se usa `WebSocketMessageV2` con `data: Any` para soportar objetos complejos
- El mensaje se envía de forma personal (solo al usuario que se conecta)
- Se incluye manejo de errores completo con logging
- Compatible con el sistema de tipos existente en `messages_types.py`
