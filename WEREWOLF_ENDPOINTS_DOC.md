# Documentación de Endpoints para Acciones de Hombres Lobo

Este documento describe los endpoints creados para que los jugadores con el rol de hombre lobo puedan seleccionar aldeanos para devorar durante la fase nocturna del juego.

## Endpoints Disponibles

### 1. POST `/games/{game_id}/werewolf-attack`

Permite a un hombre lobo seleccionar a un aldeano para devorar durante la fase nocturna.

**Parámetros:**
- `game_id` (path): ID de la partida
- `target_id` (body): ID del jugador objetivo a atacar

**Autenticación:** Requerida (JWT token)

**Restricciones:**
- Solo hombres lobo pueden usar este endpoint
- Solo durante la fase nocturna (`GameStatus.NIGHT`)
- El objetivo debe estar vivo y no ser un hombre lobo
- Un hombre lobo solo puede votar una vez por noche

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Tu voto de ataque ha sido registrado correctamente",
  "consensus_target": "villager_id" // Solo si hay consenso entre todos los hombres lobo
}
```

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8000/games/game123/werewolf-attack" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"target_id": "villager_user_id"}'
```

### 2. GET `/games/{game_id}/werewolf-targets`

Obtiene la lista de jugadores que pueden ser atacados por los hombres lobo.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe ser hombre lobo)

**Respuesta:**
```json
[
  {
    "id": "villager1",
    "username": "aldeano1"
  },
  {
    "id": "seer1",
    "username": "vidente1"
  }
]
```

### 3. GET `/games/{game_id}/werewolf-consensus`

Verifica si los hombres lobo han llegado a un consenso sobre a quién atacar.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe ser hombre lobo)

**Respuesta:**
```json
{
  "consensus_target": "villager_id" // null si no hay consenso
}
```

### 4. GET `/games/{game_id}/can-werewolf-act`

Verifica si el usuario puede realizar una acción como hombre lobo.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token)

**Respuesta:**
```json
{
  "can_act": true
}
```

### 5. GET `/games/{game_id}/alive-players`

Obtiene la lista de todos los jugadores vivos en la partida.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe estar en la partida)

**Respuesta:**
```json
[
  {
    "id": "player1",
    "username": "jugador1"
  },
  {
    "id": "player2", 
    "username": "jugador2"
  }
]
```

## Flujo de Juego para Hombres Lobo

1. **Fase nocturna iniciada**: La partida cambia a estado `GameStatus.NIGHT`
2. **Obtener objetivos**: Los hombres lobo pueden usar `GET /werewolf-targets` para ver a quién pueden atacar
3. **Seleccionar objetivo**: Cada hombre lobo usa `POST /werewolf-attack` para votar por su objetivo
4. **Verificar consenso**: Se puede usar `GET /werewolf-consensus` para ver si todos han votado y hay acuerdo
5. **Resolver ataque**: Una vez que todos los hombres lobo han votado y hay consenso, se puede proceder a la siguiente fase

## Reglas de Negocio

- **Consenso requerido**: Todos los hombres lobo vivos deben votar
- **Mayoría simple**: El objetivo con más votos es seleccionado
- **Empates**: Si hay empate, no hay consenso (se puede implementar lógica de desempate)
- **Una acción por noche**: Cada hombre lobo solo puede votar una vez por noche
- **Objetivos válidos**: Solo jugadores vivos que no sean hombres lobo

## Servicios de Backend

Los endpoints utilizan el servicio `player_action_service.py` que incluye:

- `werewolf_attack()`: Registra el voto de ataque de un hombre lobo
- `get_werewolf_attack_consensus()`: Determina si hay consenso
- `get_non_werewolf_players()`: Lista objetivos válidos
- `can_werewolf_act()`: Verifica permisos de acción
- `reset_night_actions()`: Reinicia acciones para nueva noche

## Estructura de Datos

El modelo `Game` fue extendido con:
```python
night_actions: Dict[str, Dict[str, str]] = {}
```

Ejemplo de estructura:
```python
{
  "werewolf_attacks": {
    "werewolf1_id": "target1_id",
    "werewolf2_id": "target1_id"
  }
}
```

## Testing

Se incluyen tests comprehensivos en `tests/test_werewolf_actions.py` que verifican:
- Ataques exitosos
- Validación de objetivos
- Restricciones de fase
- Consenso entre múltiples hombres lobo
- Filtrado de objetivos válidos
- Permisos de acción
