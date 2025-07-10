# Especificaciones de Seguridad y Roles de Usuario

## 1. Roles de Usuario en la Aplicación

### 1.1 Usuario Registrado (Player)
- Puede registrarse y hacer login en la aplicación.
- Puede crear nuevas partidas.
- Puede unirse a partidas existentes (si no han comenzado y no están llenas).
- Puede abandonar una partida antes de que comience.
- Puede consultar el listado de partidas públicas y su propio historial de partidas.
- Puede ver y modificar su propio perfil (email, contraseña, etc.).
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
