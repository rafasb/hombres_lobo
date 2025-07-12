# Especificaciones de Seguridad y Roles de Usuario

## 1. Roles de Usuario en la Aplicación

### 1.1 Usuario Registrado (Player)
- Puede registrarse y hacer login en la aplicación.
- Puede crear nuevas partidas.
- Puede unirse a partidas existentes (si no han comenzado y no están llenas).
- Puede abandonar una partida antes de que comience.
- Puede consultar el listado de partidas públicas y su propio historial de partidas.
- Puede ver y modificar su propio perfil (email y contraseña).
- **Restricciones:**
  - No puede modificar, eliminar ni avanzar fases en partidas que no haya creado.
  - No puede eliminar a otros usuarios ni partidas ajenas.

### 1.2 Creador de Partida
- Es un usuario registrado que ha creado una partida concreta.
- **Permisos adicionales sobre su partida:**
  - Modificar la parametrización de la partida (nombre, número de jugadores, roles, etc.) antes de que comience.
  - Iniciar, pausar, avanzar de fase o detener la partida.
  - Eliminar la partida antes de que comience o si está en estado "esperando".
- **Restricciones:**
  - No puede modificar partidas de otros usuarios.
  - No puede eliminar usuarios.

### 1.3 Administrador (Admin)
- Usuario con privilegios elevados.
- **Permisos adicionales:**
  - Consultar el estado de todas las partidas activas o históricas.
  - Eliminar cualquier partida (independientemente del creador o estado).
  - Eliminar cualquier usuario (excepto a sí mismo si es el único admin).
  - Modificar el rol de otros usuarios (promover a admin o degradar a player).
- **Restricciones:**
  - Debe autenticarse como admin.
  - No puede eliminarse a sí mismo si es el único admin.

## 2. Reglas de Seguridad y Acceso

- **Autenticación:**
  - Todas las acciones salvo el registro y login requieren autenticación JWT.
- **Autorización:**
  - Las rutas de modificación/eliminación de partidas requieren ser el creador o admin.
  - Las rutas de administración requieren rol admin.
  - Las rutas de consulta de partidas y usuarios requieren estar autenticado.
- **Protección de datos:**
  - Los usuarios solo pueden ver y modificar su propio perfil.
  - Los administradores pueden ver y modificar cualquier usuario.

## 3. Resumen de Acciones y Permisos

| Acción                                 | Player | Creador de Partida | Admin |
|----------------------------------------|:------:|:------------------:|:-----:|
| Registro/Login                         |   ✔    |         ✔          |   ✔   |
| Crear partida                          |   ✔    |         ✔          |   ✔   |
| Unirse a partida                       |   ✔    |         ✔          |   ✔   |
| Modificar/eliminar su partida          |        |         ✔          |   ✔   |
| Avanzar/detener su partida             |        |         ✔          |   ✔   |
| Eliminar cualquier partida             |        |                    |   ✔   |
| Eliminar/modificar otros usuarios      |        |                    |   ✔   |
| Consultar partidas propias             |   ✔    |         ✔          |   ✔   |
| Consultar todas las partidas           |        |                    |   ✔   |
| Modificar su propio perfil             |   ✔    |         ✔          |   ✔   |
| Modificar rol de usuario               |        |                    |   ✔   |

> **Nota:** El sistema debe validar el rol y la autoría en cada acción sensible, devolviendo error 403 (Forbidden) si el usuario no tiene permisos suficientes.

## 4. Implementación Técnica de Seguridad

### 4.1 Dependencias de Autenticación y Autorización

El sistema utiliza las siguientes dependencias de FastAPI para garantizar la seguridad:

- **`get_current_user()`**: Valida el token JWT y retorna el usuario autenticado
- **`admin_required()`**: Verifica que el usuario tenga rol de administrador
- **Validación inline**: Verificación específica en endpoints que requieren lógica personalizada

### 4.2 Códigos de Error HTTP Implementados

| Código | Descripción | Casos de Uso |
|--------|-------------|--------------|
| **401 Unauthorized** | Token JWT inválido o usuario no encontrado | Acceso sin autenticación válida |
| **403 Forbidden** | Permisos insuficientes | Acceso denegado por rol o autoría |
| **404 Not Found** | Recurso no encontrado | Usuario o partida inexistente |

### 4.3 Validación de Autorización por Endpoint

#### **Rutas Públicas (Sin Autenticación)**
- `POST /register` - Registro de nuevos usuarios
- `POST /login` - Autenticación de usuarios

#### **Rutas con Autenticación Básica**
- `GET /games` - Requiere: Usuario autenticado
- `GET /games/{game_id}` - Requiere: Usuario autenticado
- `POST /games` - Requiere: Usuario autenticado
- `POST /games/{game_id}/leave` - Requiere: Usuario autenticado

#### **Rutas con Autorización Creador O Admin**
- `PUT /games/{game_id}` - Requiere: Creador de la partida O admin
- `PUT /games/{game_id}/status` - Requiere: Creador de la partida O admin
- `DELETE /games/{game_id}` - Requiere: Creador de la partida O admin

**Implementación técnica:**
```python
# En servicios: parámetro is_admin = user.role == UserRole.ADMIN
# Lógica: if not is_admin and game.creator_id != user_id: return error
```

#### **Rutas con Protección de Datos Personales**
- `GET /users/{user_id}` - Requiere: Propio perfil O admin
- `PUT /users/me` - Requiere: Propio perfil únicamente

**Implementación técnica:**
```python
# Validación: if user.role != UserRole.ADMIN and user.id != user_id: raise 403
```

#### **Rutas Administrativas (Solo Admin)**
- `GET /admin/users` - Lista todos los usuarios
- `GET /admin/users/{user_id}` - Ver cualquier usuario
- `PUT /admin/users/{user_id}` - Modificar cualquier usuario
- `DELETE /admin/users/{user_id}` - Eliminar cualquier usuario
- `PUT /admin/users/{user_id}/role` - Cambiar rol de usuario
- `GET /admin/games` - Lista todas las partidas
- `DELETE /admin/games/{game_id}` - Eliminar cualquier partida

#### **Rutas Restringidas por Lógica de Negocio**
- `GET /users` - **Solo admin** (modificado para cumplir especificaciones)

### 4.4 Flujo de Validación de Seguridad

1. **Autenticación JWT**: Verificación del token en dependencia `get_current_user()`
2. **Autorización de Rol**: Verificación de rol admin en dependencia `admin_required()`
3. **Autorización de Autoría**: Validación de creador en servicios con parámetro `is_admin`
4. **Protección de Datos**: Validación inline en endpoints de perfil de usuario

### 4.5 Restricciones Especiales Implementadas

#### **Auto-eliminación de Admin**
```python
# En admin_delete_user(): Previene eliminación del último admin
if user_id == admin.id and sum(1 for u in users if u.role == UserRole.ADMIN) == 1:
    raise HTTPException(status_code=400, detail="No puedes eliminarte si eres el único admin")
```

#### **Eliminación Lógica de Usuarios**
```python
# Los usuarios eliminados se marcan como BANNED, no se borran físicamente
user.status = UserStatus.BANNED
```

#### **Validación de Estados de Partida**
```python
# Creadores solo pueden eliminar partidas en estados WAITING o PAUSED
# Admins pueden eliminar partidas en cualquier estado
```

### 4.6 Mejoras de Seguridad Implementadas

1. **Separación de responsabilidades**: Rutas admin en archivo separado
2. **Principio de menor privilegio**: Usuarios solo ven su información personal
3. **Validación granular**: Diferentes niveles de acceso según contexto
4. **Audit trail**: Los usuarios eliminados se marcan como banned, manteniendo historial
5. **Protección contra escalada**: Validación estricta de roles y autoría

> **Estado de Implementación:** ✅ Todas las especificaciones de seguridad han sido verificadas e implementadas correctamente en el sistema.
