# Documentación de Endpoints - Rol Cazador

## Descripción
Los endpoints del Cazador permiten a los jugadores con este rol usar su habilidad especial de venganza cuando son eliminados de la partida.

## Funcionalidad del Rol
- **Habilidad de Venganza:** Cuando es eliminado (por linchamiento o por Hombres Lobo), puede elegir a otro jugador para eliminarlo también
- **Activación:** Se activa automáticamente al morir, independientemente de la causa
- **Limitación:** Solo puede usar su venganza una vez por partida
- **Objetivo:** Puede vengarse de cualquier jugador vivo, excepto de sí mismo

---

## Endpoints Disponibles

### 1. POST `/games/{game_id}/hunter-revenge`
**Descripción:** Permite al cazador eliminado vengarse de otro jugador.

**Parámetros:**
- `game_id` (path): ID de la partida
- Cuerpo del request:
  ```json
  {
    "target_id": "string"  // ID del jugador objetivo para la venganza
  }
  ```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Te has llevado a NombreJugador contigo en tu venganza final.",
  "target_id": "player123",
  "target_username": "NombreJugador"
}
```

**Errores posibles:**
- `400`: No puede usar venganza en este momento
- `400`: Objetivo no válido (no existe, está muerto, o es el mismo cazador)
- `401`: No autenticado
- `403`: No es el cazador

---

### 2. GET `/games/{game_id}/hunter-revenge-targets`
**Descripción:** Obtiene la lista de jugadores que el cazador puede eliminar por venganza.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
[
  {
    "id": "player1",
    "username": "Objetivo1"
  },
  {
    "id": "player2", 
    "username": "Objetivo2"
  }
]
```

**Errores posibles:**
- `403`: No tiene permisos (no es cazador o no puede vengarse)
- `404`: Partida no encontrada

---

### 3. GET `/games/{game_id}/can-hunter-revenge`
**Descripción:** Verifica si el cazador puede usar su habilidad de venganza.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "can_revenge": true  // true si puede vengarse, false si no
}
```

**Condiciones para `can_revenge: true`:**
- El jugador es el cazador
- Está eliminado (muerto)
- No ha usado su venganza aún
- Tiene la habilidad de venganza activada

---

### 4. GET `/games/{game_id}/is-hunter`
**Descripción:** Verifica si el usuario es el cazador de la partida.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "is_hunter": true
}
```

---

### 5. GET `/games/{game_id}/hunters-needing-revenge`
**Descripción:** Obtiene la lista de cazadores que murieron y necesitan activar su venganza.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
["hunter1", "hunter2"]  // IDs de cazadores que pueden vengarse
```

**Errores posibles:**
- `403`: No está participando en la partida
- `404`: Partida no encontrada

---

### 6. GET `/games/{game_id}/hunter-revenge-result/{hunter_id}`
**Descripción:** Obtiene el resultado de la venganza de un cazador específico.

**Parámetros:**
- `game_id` (path): ID de la partida
- `hunter_id` (path): ID del cazador

**Respuesta exitosa (200):**
```json
{
  "id": "eliminated_player",
  "username": "EliminatedPlayer"
}
```

**Errores posibles:**
- `403`: No está participando en la partida
- `404`: No se encontró resultado de venganza

---

### 7. GET `/games/{game_id}/my-hunter-status`
**Descripción:** Obtiene el estado completo del cazador para el usuario actual.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "is_hunter": true,
  "can_revenge": true,
  "is_alive": false,
  "has_used_revenge": false
}
```

---

## Flujos de Uso

### Flujo 1: Venganza del Cazador Eliminado

```bash
# 1. Verificar estado del cazador
GET /games/{game_id}/my-hunter-status

# 2. Verificar si puede vengarse
GET /games/{game_id}/can-hunter-revenge

# 3. Ver objetivos disponibles
GET /games/{game_id}/hunter-revenge-targets

# 4. Ejecutar venganza
POST /games/{game_id}/hunter-revenge
Body: {"target_id": "target_player"}
```

### Flujo 2: Verificación de Cazadores (Admin/Narrador)

```bash
# 1. Ver cazadores que necesitan venganza
GET /games/{game_id}/hunters-needing-revenge

# 2. Ver resultado de venganza específica
GET /games/{game_id}/hunter-revenge-result/{hunter_id}
```

---

## Lógica de Negocio

### Activación de Venganza:
- ✅ Se activa automáticamente al morir el cazador
- ✅ Funciona independientemente de la causa de muerte
- ✅ Solo se puede usar una vez por partida
- ✅ Debe ejecutarse inmediatamente tras la eliminación

### Selección de Objetivo:
- ✅ Cualquier jugador vivo puede ser objetivo
- ✅ No puede vengarse de sí mismo
- ✅ No puede vengarse de jugadores ya muertos
- ✅ La venganza es inmediata e irrevocable

### Integración con el Juego:
- La muerte del cazador triggerea automáticamente la oportunidad de venganza
- La venganza se ejecuta antes de continuar con el flujo normal
- Ambas muertes (cazador + objetivo) se anuncian simultáneamente

---

## Ejemplos de Uso

### Caso 1: Venganza Exitosa
```bash
# Verificar estado tras ser eliminado
curl -X GET "http://localhost:8000/games/game123/my-hunter-status" \
  -H "Authorization: Bearer {token}"
# Respuesta: {"is_hunter": true, "can_revenge": true, "is_alive": false, "has_used_revenge": false}

# Ver objetivos disponibles
curl -X GET "http://localhost:8000/games/game123/hunter-revenge-targets" \
  -H "Authorization: Bearer {token}"

# Ejecutar venganza
curl -X POST "http://localhost:8000/games/game123/hunter-revenge" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"target_id": "enemy_player"}'

# Respuesta: {
#   "success": true,
#   "message": "Te has llevado a EnemyPlayer contigo en tu venganza final.",
#   "target_id": "enemy_player",
#   "target_username": "EnemyPlayer"
# }
```

### Caso 2: Cazador Vivo (No Puede Vengarse)
```bash
curl -X POST "http://localhost:8000/games/game123/hunter-revenge" \
  -H "Authorization: Bearer {token}" \
  -d '{"target_id": "player1"}'

# Respuesta 400: {
#   "detail": "No puedes usar tu habilidad de venganza en este momento"
# }
```

### Caso 3: Venganza Ya Usada
```bash
curl -X GET "http://localhost:8000/games/game123/can-hunter-revenge" \
  -H "Authorization: Bearer {token}"

# Respuesta: {"can_revenge": false}
```

---

## Secuencia de Eventos

### 1. Eliminación del Cazador:
1. Cazador es eliminado (linchamiento/ataque de lobos)
2. Sistema marca `is_alive = false`
3. Sistema activa `can_revenge_kill = true`
4. Se notifica al cazador para elegir venganza

### 2. Ejecución de Venganza:
1. Cazador selecciona objetivo
2. Sistema valida objetivo (vivo, diferente al cazador)
3. Objetivo es eliminado inmediatamente
4. Sistema marca `has_used_revenge = true`
5. Se anuncia la doble eliminación

### 3. Continuación del Juego:
1. Ambas muertes se procesan
2. Se verifican condiciones de victoria
3. Continúa el flujo normal del juego

---

## Integración con Otros Sistemas

### Con el Sistema de Eliminación:
- Se integra con linchamientos diurnos
- Se integra con ataques nocturnos de lobos
- Puede activarse por muerte de enamorados

### Con el Sistema de Fases:
- La venganza se ejecuta inmediatamente
- No depende de fases específicas del juego
- Interrumpe brevemente el flujo para resolver

### Con el Sistema de Roles:
- Detecta automáticamente cazadores eliminados
- Mantiene estado de venganza usado
- Se integra con notificaciones de muerte

### Con la UI/Frontend:
- Pantalla de emergencia para elección de venganza
- Notificación inmediata de doble eliminación
- Estado visual del cazador y su habilidad disponible
