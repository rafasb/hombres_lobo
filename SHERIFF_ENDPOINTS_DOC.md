# Documentación de Endpoints - Rol Alguacil

## Descripción
Los endpoints del Alguacil permiten a los jugadores con este rol usar sus habilidades especiales: desempatar votaciones y elegir sucesor antes de morir.

## Funcionalidad del Rol
- **Voto Doble:** Su voto cuenta como dos votos durante las votaciones diurnas
- **Desempate:** Puede resolver empates en las votaciones de linchamiento
- **Sucesor:** Antes de morir, puede elegir a su sucesor como nuevo alguacil
- **Elección:** Es elegido por votación popular al inicio de la partida

---

## Endpoints Disponibles

### 1. POST `/games/{game_id}/sheriff-tiebreaker`
**Descripción:** Permite al alguacil desempatar una votación diurna eligiendo quién será eliminado.

**Parámetros:**
- `game_id` (path): ID de la partida
- Cuerpo del request:
  ```json
  {
    "target_id": "string"  // ID del jugador elegido para eliminación
  }
  ```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Has decidido el empate. NombreJugador ha sido eliminado.",
  "eliminated_player_id": "player123",
  "eliminated_username": "NombreJugador"
}
```

**Errores posibles:**
- `400`: No puede desempatar en este momento
- `400`: Jugador elegido no está entre los empatados
- `401`: No autenticado
- `403`: No es el alguacil

---

### 2. GET `/games/{game_id}/tied-players`
**Descripción:** Obtiene la lista de jugadores empatados en la votación diurna.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
[
  {
    "id": "player1",
    "username": "Sospechoso1"
  },
  {
    "id": "player2", 
    "username": "Sospechoso2"
  }
]
```

**Errores posibles:**
- `403`: Solo el alguacil puede ver esta información
- `404`: Partida no encontrada

---

### 3. GET `/games/{game_id}/can-sheriff-break-tie`
**Descripción:** Verifica si el alguacil puede desempatar la votación actual.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "can_break_tie": true  // true si puede desempatar, false si no
}
```

**Condiciones para `can_break_tie: true`:**
- Es fase diurna (DAY)
- El jugador es el alguacil
- Está vivo
- Hay empate en la votación actual

---

### 4. POST `/games/{game_id}/sheriff-successor`
**Descripción:** Permite al alguacil elegir a su sucesor antes de morir.

**Parámetros:**
- `game_id` (path): ID de la partida
- Cuerpo del request:
  ```json
  {
    "successor_id": "string"  // ID del jugador elegido como sucesor
  }
  ```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Has elegido a NombreJugador como tu sucesor.",
  "successor_id": "player123",
  "successor_username": "NombreJugador"
}
```

**Errores posibles:**
- `400`: No puede elegir sucesor en este momento
- `400`: Jugador elegido no es válido (muerto o es el mismo alguacil)
- `401`: No autenticado
- `403`: No es el alguacil

---

### 5. GET `/games/{game_id}/sheriff-successor-candidates`
**Descripción:** Obtiene la lista de jugadores que pueden ser elegidos como sucesores.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
[
  {
    "id": "player1",
    "username": "Candidato1"
  },
  {
    "id": "player2",
    "username": "Candidato2"
  }
]
```

**Errores posibles:**
- `403`: No tiene permisos (no es alguacil o no puede elegir sucesor)

---

### 6. GET `/games/{game_id}/can-choose-successor`
**Descripción:** Verifica si el alguacil puede elegir un sucesor.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "can_choose_successor": true
}
```

---

### 7. GET `/games/{game_id}/is-sheriff`
**Descripción:** Verifica si el usuario es el alguacil de la partida.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "is_sheriff": true
}
```

---

### 8. GET `/games/{game_id}/has-vote-tie`
**Descripción:** Verifica si hay empate en la votación diurna actual.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "has_tie": true
}
```

**Errores posibles:**
- `403`: Solo el alguacil puede ver esta información

---

## Flujos de Uso

### Flujo 1: Desempate de Votación

```bash
# 1. Verificar si es alguacil
GET /games/{game_id}/is-sheriff

# 2. Verificar si hay empate
GET /games/{game_id}/has-vote-tie

# 3. Ver jugadores empatados
GET /games/{game_id}/tied-players

# 4. Verificar si puede desempatar
GET /games/{game_id}/can-sheriff-break-tie

# 5. Realizar desempate
POST /games/{game_id}/sheriff-tiebreaker
Body: {"target_id": "player_to_eliminate"}
```

### Flujo 2: Elección de Sucesor

```bash
# 1. Verificar si puede elegir sucesor
GET /games/{game_id}/can-choose-successor

# 2. Ver candidatos disponibles
GET /games/{game_id}/sheriff-successor-candidates

# 3. Elegir sucesor
POST /games/{game_id}/sheriff-successor
Body: {"successor_id": "chosen_successor"}
```

---

## Lógica de Negocio

### Desempate de Votaciones:
- ✅ Solo durante fase diurna
- ✅ Solo cuando hay empate real (2+ jugadores con máximo de votos)
- ✅ Solo el alguacil vivo puede desempatar
- ✅ Debe elegir entre los jugadores empatados
- ✅ La elección elimina al jugador y limpia los votos

### Elección de Sucesor:
- ✅ Solo el alguacil vivo puede elegir
- ✅ No puede elegirse a sí mismo
- ✅ Solo jugadores vivos pueden ser sucesores
- ✅ El sucesor se convierte en alguacil al morir el actual

### Promoción Automática:
- Cuando el alguacil muere, su sucesor designado se convierte automáticamente en alguacil
- El nuevo alguacil hereda todas las habilidades: voto doble y poder de desempate

---

## Ejemplos de Uso

### Caso 1: Desempate Exitoso
```bash
# Verificar empate
curl -X GET "http://localhost:8000/games/game123/has-vote-tie" \
  -H "Authorization: Bearer {token}"
# Respuesta: {"has_tie": true}

# Ver jugadores empatados
curl -X GET "http://localhost:8000/games/game123/tied-players" \
  -H "Authorization: Bearer {token}"
# Respuesta: [{"id": "player1", "username": "Sospechoso1"}, ...]

# Desempatar
curl -X POST "http://localhost:8000/games/game123/sheriff-tiebreaker" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"target_id": "player1"}'

# Respuesta: {
#   "success": true,
#   "message": "Has decidido el empate. Sospechoso1 ha sido eliminado.",
#   "eliminated_player_id": "player1",
#   "eliminated_username": "Sospechoso1"
# }
```

### Caso 2: Elección de Sucesor
```bash
# Ver candidatos
curl -X GET "http://localhost:8000/games/game123/sheriff-successor-candidates" \
  -H "Authorization: Bearer {token}"

# Elegir sucesor
curl -X POST "http://localhost:8000/games/game123/sheriff-successor" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"successor_id": "trusted_player"}'

# Respuesta: {
#   "success": true,
#   "message": "Has elegido a TrustedPlayer como tu sucesor.",
#   "successor_id": "trusted_player",
#   "successor_username": "TrustedPlayer"
# }
```

### Caso 3: No Hay Empate
```bash
curl -X POST "http://localhost:8000/games/game123/sheriff-tiebreaker" \
  -H "Authorization: Bearer {token}" \
  -d '{"target_id": "player1"}'

# Respuesta 400: {
#   "detail": "No puedes desempatar la votación en este momento"
# }
```

---

## Integración con Otros Sistemas

### Con el Sistema de Votación:
- Detecta automáticamente empates en `day_votes`
- Se integra con la votación diurna normal
- Limpia votos después del desempate

### Con el Sistema de Roles:
- Herencia automática del rol al sucesor
- Mantiene todas las habilidades especiales
- Actualiza los permisos de forma transparente

### Con el Flujo del Juego:
- El desempate permite continuar con el flujo normal
- La elección de sucesor se ejecuta antes de la muerte
- La promoción se activa automáticamente

### Con la UI/Frontend:
- Interfaces específicas para desempate durante empates
- Pantalla de emergencia para elección de sucesor
- Notificaciones cuando se convierte en nuevo alguacil
