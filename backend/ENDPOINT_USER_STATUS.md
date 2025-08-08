# Endpoint de Actualización de Estado de Usuario

## Descripción

Se ha añadido un nuevo endpoint que permite actualizar el estado de conexión de los usuarios en la aplicación. Este endpoint facilita el seguimiento del estado de cada usuario (conectado, desconectado, activo, inactivo, bloqueado).

## Endpoint

```
PUT /users/{user_id}/status
```

## Estados Disponibles

El sistema ahora soporta los siguientes estados de usuario:

- `active`: Usuario activo y disponible para participar en juegos
- `inactive`: Usuario inactivo temporalmente
- `banned`: Usuario bloqueado/baneado por un administrador
- `connected`: Usuario conectado a la aplicación
- `disconnected`: Usuario desconectado de la aplicación

## Permisos y Autorización

### Usuarios Regulares
- Pueden cambiar su propio estado entre `connected` y `disconnected`
- Pueden cambiar su propio estado a `inactive`
- **NO** pueden cambiar su estado a `banned`
- **NO** pueden cambiar el estado de otros usuarios

### Administradores
- Pueden cambiar el estado de cualquier usuario
- Son los únicos que pueden establecer el estado `banned`
- Tienen acceso completo a todas las transiciones de estado

## Formato de Request

```json
{
  "status": "connected"
}
```

## Formato de Response

```json
{
  "success": true,
  "message": "Estado del usuario actualizado de 'disconnected' a 'connected'",
  "user_id": "12345",
  "old_status": "disconnected",
  "new_status": "connected",
  "updated_at": "2025-08-09T15:30:45.123456+00:00"
}
```

## Ejemplos de Uso

### 1. Usuario marcándose como conectado

```bash
curl -X PUT "http://localhost:8000/users/12345/status" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"status": "connected"}'
```

### 2. Usuario marcándose como desconectado

```bash
curl -X PUT "http://localhost:8000/users/12345/status" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"status": "disconnected"}'
```

### 3. Administrador baneando un usuario

```bash
curl -X PUT "http://localhost:8000/users/54321/status" \
  -H "Authorization: Bearer admin_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"status": "banned"}'
```

## Códigos de Respuesta

- `200 OK`: Estado actualizado exitosamente
- `403 Forbidden`: Sin permisos para realizar la acción
- `404 Not Found`: Usuario no encontrado
- `422 Unprocessable Entity`: Estado inválido en el request

## Errores Comunes

### Error 403: Permisos Insuficientes

```json
{
  "detail": "Solo puedes cambiar tu propio estado de conexión o ser administrador"
}
```

### Error 403: Intentar Banear Sin Ser Admin

```json
{
  "detail": "Solo los administradores pueden banear usuarios"
}
```

### Error 404: Usuario No Encontrado

```json
{
  "detail": "Usuario no encontrado"
}
```

## Integración con WebSockets

Este endpoint complementa perfectamente el sistema de WebSockets de la aplicación:

1. **Al conectarse**: El cliente puede actualizar su estado a `connected`
2. **Al desconectarse**: El cliente puede actualizar su estado a `disconnected`  
3. **Durante partidas**: Se puede verificar el estado para validar la participación
4. **Moderación**: Los admins pueden banear usuarios problemáticos

## Casos de Uso en el Juego

- **Lobby**: Mostrar qué jugadores están conectados
- **Durante partida**: Validar que los jugadores estén activos
- **Moderación**: Administrar usuarios problemáticos
- **Estadísticas**: Llevar seguimiento de la actividad de usuarios

## Próximos Pasos Sugeridos

1. **Integrar con WebSockets**: Actualizar automáticamente el estado cuando se conectan/desconectan
2. **Dashboard de administración**: Crear interfaz para gestionar estados de usuarios
3. **Logs de estado**: Mantener historial de cambios de estado
4. **Notificaciones**: Avisar a otros usuarios cuando alguien se conecta/desconecta
