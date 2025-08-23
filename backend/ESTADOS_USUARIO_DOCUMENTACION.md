# Estados de Usuario y Transiciones en Juego

## Descripción General

El sistema de estados de usuario maneja automáticamente las transiciones de estado cuando los usuarios interactúan con el juego. Esto permite un seguimiento preciso del estado de cada usuario en tiempo real.

## Estados Disponibles

### Estados Base
- `BANNED`: Usuario bloqueado/baneado (solo admins pueden establecer este estado)

### Estados de Conexión
- `CONNECTED`: Usuario conectado a la aplicación vía WebSocket
- `DISCONNECTED`: Usuario desconectado de la aplicación. Estado inicial por defecto de todos los usuarios

### Estados de Juego
- `IN_GAME`: Usuario en una partida activa (puede estar vivo o muerto)

## Transiciones Automáticas

### Al Conectarse
- **Trigger**: Usuario se conecta vía WebSocket
- **Transición**: `cualquier_estado` → `CONNECTED`
- **Función**: `auto_update_status_on_connect(user_id)`

### Al Unirse a Partida
- **Trigger**: Usuario se une a una partida
- **Transición**: `CONNECTED` → `IN_GAME`
- **Función**: `auto_update_status_on_join(connection_id, message_data)`

### Al Salir de Partida
- **Trigger**: Usuario abandona o termina la partida
- **Transición**: `IN_GAME` → `CONNECTED`
- **Función**: `auto_update_status_on_leave_game(user_id)`

### Al Desconectarse
- **Trigger**: Usuario se desconecta del WebSocket
- **Transición**: `cualquier_estado` → `CONNECTED`
- **Función**: `auto_update_status_on_disconnect(user_id)`

## Flujo Típico de Estados

```

```

## Implementación Técnica

### Archivo: `app/websocket/user_status_handlers.py`

Contiene la clase `UserStatusHandler` con todas las funciones de transición automática:

- `auto_update_status_on_connect()`
- `auto_update_status_on_join()`
- `auto_update_status_on_game_start()`
- `auto_update_status_on_player_death()`
- `auto_update_status_on_leave_game()`
- `auto_update_status_on_disconnect()`

### Integración con otros componentes

1. **WebSocket Connection Manager** (`message_handlers.py`):
   - Llama automáticamente a las funciones de conexión/desconexión

2. **Game Handlers** (`game_handlers.py`):
   - Integrado en `handle_start_game()` y `_auto_start_game()`
   - Actualiza estados cuando inicia una partida

3. **Game State Service** (`game_state_service.py`):
   - Integrado en `eliminate_player()`
   - Actualiza estados cuando un jugador muere

## Notificaciones en Tiempo Real

Todas las transiciones de estado automáticas:
- Se notifican a otros usuarios conectados vía WebSocket
- Incluyen información del cambio: usuario, estado anterior, estado nuevo
- Se registran en los logs para auditoría

## Permisos

- **Usuarios normales**: Pueden cambiar su propio estado (excepto `BANNED`)
- **Administradores**: Pueden banear usuarios (establecer estado `BANNED`)
- **Sistema**: Las transiciones automáticas funcionan independientemente de permisos

## Testing

Se incluye un test completo en `test_user_status_join_game.py` que verifica:
- Todas las transiciones automáticas
- Persistencia de estados en la base de datos
- Notificaciones correctas
- Manejo de errores

Para ejecutar el test:
```bash
cd /home/rafasb/desarrollo/hombres_lobo/backend
python test_user_status_join_game.py
```
