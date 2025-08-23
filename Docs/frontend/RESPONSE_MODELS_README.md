# Modelos de Respuesta para Endpoints

Este documento describe los nuevos modelos de respuesta implementados para los endpoints de la API del juego Hombres Lobo.

## ✨ Mejoras Implementadas

Se han agregado modelos de datos estructurados para las respuestas de los endpoints POST y GET, proporcionando:

- **Consistencia**: Todas las respuestas siguen la misma estructura
- **Claridad**: Campos descriptivos y mensajes informativos
- **Documentación automática**: OpenAPI/Swagger genera documentación precisa
- **Validación**: Pydantic valida automáticamente las respuestas

## 🎮 Modelos para Endpoints de Partidas (`game_responses.py`)

### `GameCreateResponse`
**Endpoint**: `POST /games`
```json
{
  "success": true,
  "message": "Partida 'Mi Partida' creada exitosamente",
  "game": {
    "id": "uuid-123",
    "name": "Mi Partida",
    "creator_id": "user-id",
    "players": [...],
    "status": "waiting",
    "max_players": 8,
    ...
  }
}
```

### `GameGetResponse`
**Endpoint**: `GET /games/{game_id}`
```json
{
  "success": true,
  "message": "Partida obtenida exitosamente",
  "game": {
    "id": "uuid-123",
    "name": "Mi Partida",
    ...
  }
}
```

### `GameListResponse`
**Endpoint**: `GET /games`
```json
{
  "success": true,
  "message": "Lista de partidas obtenida exitosamente",
  "games": [...],
  "total_games": 5
}
```

### `GameJoinResponse`
**Endpoint**: `POST /games/{game_id}/join`
```json
{
  "success": true,
  "message": "Te has unido a la partida exitosamente",
  "game_id": "uuid-123",
  "current_players": 3,
  "max_players": 8
}
```

### `GameLeaveResponse`
**Endpoint**: `POST /games/{game_id}/leave`
```json
{
  "success": true,
  "message": "Has abandonado la partida",
  "game_id": "uuid-123",
  "remaining_players": 2
}
```

### `GameRoleAssignmentResponse`
**Endpoint**: `POST /games/{game_id}/assign-roles`
```json
{
  "success": true,
  "message": "Roles asignados exitosamente",
  "game": {...},
  "assigned_roles_count": 3,
  "players_with_roles": 8
}
```

### `GameUpdateResponse`
**Endpoint**: `PUT /games/{game_id}`
```json
{
  "success": true,
  "message": "Partida actualizada exitosamente",
  "game": {...},
  "updated_fields": ["name", "max_players"]
}
```

### `GameStatusUpdateResponse`
**Endpoint**: `PUT /games/{game_id}/status`
```json
{
  "success": true,
  "message": "Estado de la partida cambiado de waiting a started",
  "game": {...},
  "previous_status": "waiting",
  "new_status": "started"
}
```

### `GameDeleteResponse`
**Endpoint**: `DELETE /games/{game_id}`
```json
{
  "success": true,
  "message": "Partida eliminada exitosamente",
  "deleted_game_id": "uuid-123"
}
```

## 👤 Modelos para Endpoints de Usuarios (`user_responses.py`)

### `RegisterResponse`
**Endpoint**: `POST /register`
```json
{
  "success": true,
  "message": "Usuario 'john_doe' registrado exitosamente",
  "user": {
    "id": "user-id",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "player",
    "status": "active"
  }
}
```

### `LoginResponse`
**Endpoint**: `POST /login`
```json
{
  "success": true,
  "message": "Login exitoso para john_doe",
  "access_token": "jwt-token-here",
  "token_type": "bearer",
  "user_id": "user-id",
  "username": "john_doe",
  "role": "player"
}
```

### `UserProfileResponse`
**Endpoints**: `GET /users/me`, `GET /users/{user_id}`
```json
{
  "success": true,
  "message": "Perfil obtenido exitosamente",
  "user": {
    "id": "user-id",
    "username": "john_doe",
    ...
  }
}
```

### `UsersListResponse`
**Endpoint**: `GET /users`
```json
{
  "success": true,
  "message": "Lista de usuarios obtenida exitosamente",
  "users": [...],
  "total_users": 10
}
```

### `UserUpdateResponse`
**Endpoint**: `PUT /users/me`
```json
{
  "success": true,
  "message": "Perfil actualizado exitosamente",
  "user": {...},
  "updated_fields": ["email", "username"]
}
```

## 🔧 Funciones Helper

### `game_to_game_response()`
Nueva función en `database.py` que convierte un objeto `Game` a un objeto `GameResponse` con información completa de jugadores.

```python
from app.database import game_to_game_response

game_response = game_to_game_response(game)
```

## 🧪 Pruebas

Se incluye un script de prueba `test_response_models.py` para verificar que los endpoints funcionan correctamente:

```bash
python test_response_models.py
```

El script prueba:
- ✅ Registro de usuario
- ✅ Login de usuario  
- ✅ Obtención de perfil
- ✅ Creación de partida
- ✅ Obtención de partida
- ✅ Listado de partidas

## 🎯 Beneficios

1. **Respuestas Consistentes**: Todas las respuestas tienen la estructura `success`, `message` y datos específicos
2. **Mejor UX**: Los frontends reciben información clara sobre el resultado de cada operación
3. **Documentación Automática**: Swagger/OpenAPI muestra la estructura exacta de cada respuesta
4. **Mantenimiento**: Cambios en las respuestas se reflejan automáticamente en la documentación
5. **Validación**: Pydantic asegura que las respuestas cumplan con el schema definido

## ⚡ Retrocompatibilidad

Los endpoints mantienen la funcionalidad existente, solo se ha mejorado la estructura de las respuestas. Los clientes existentes seguirán funcionando, pero se recomienda actualizar para usar los nuevos campos `success` y `message` para una mejor experiencia de usuario.
