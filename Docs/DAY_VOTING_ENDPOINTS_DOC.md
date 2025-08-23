# Documentación de Endpoints para Votación Diurna

Este documento describe los endpoints creados para que los aldeanos puedan realizar la votación durante la fase diurna del juego.

## Endpoints de Votación Diurna

### 1. POST `/games/{game_id}/day-vote`

Permite a un jugador vivo votar para eliminar a otro jugador durante la fase diurna.

**Parámetros:**
- `game_id` (path): ID de la partida
- `target_id` (body): ID del jugador objetivo a eliminar

**Autenticación:** Requerida (JWT token)

**Restricciones:**
- Solo durante la fase diurna (`GameStatus.DAY`)
- Solo jugadores vivos pueden votar
- No se puede votar por uno mismo
- Se puede cambiar el voto (sobrescribe el anterior)

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Tu voto ha sido registrado correctamente",
  "vote_counts": [
    {
      "player_id": "player1",
      "username": "jugador1", 
      "vote_count": 2
    }
  ],
  "total_votes": 3,
  "total_players": 5
}
```

### 2. GET `/games/{game_id}/voting-targets`

Obtiene la lista de jugadores que pueden ser votados para eliminación.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe estar vivo)

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

### 3. GET `/games/{game_id}/vote-counts`

Obtiene el recuento actual de votos diurnos.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe estar en la partida)

**Respuesta:**
```json
[
  {
    "player_id": "player1",
    "username": "jugador1",
    "vote_count": 3
  },
  {
    "player_id": "player2",
    "username": "jugador2", 
    "vote_count": 1
  }
]
```

### 4. GET `/games/{game_id}/my-vote`

Obtiene el voto actual del usuario.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe estar vivo)

**Respuesta:**
```json
{
  "voted_player_id": "player2"  // null si no ha votado
}
```

### 5. GET `/games/{game_id}/voting-summary`

Obtiene un resumen completo de la votación actual.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token, debe estar en la partida)

**Respuesta:**
```json
{
  "total_players": 5,
  "total_votes": 3,
  "vote_counts": [
    {
      "player_id": "player1",
      "username": "jugador1",
      "vote_count": 2
    }
  ],
  "voting_complete": false,
  "game_status": "day"
}
```

### 6. GET `/games/{game_id}/can-vote`

Verifica si el usuario puede votar durante la fase diurna.

**Parámetros:**
- `game_id` (path): ID de la partida

**Autenticación:** Requerida (JWT token)

**Respuesta:**
```json
{
  "can_vote": true
}
```

## Flujo de Votación Diurna

1. **Fase diurna iniciada**: La partida cambia a estado `GameStatus.DAY`
2. **Obtener objetivos**: Los jugadores pueden usar `GET /voting-targets` para ver a quién pueden votar
3. **Emitir voto**: Cada jugador vivo usa `POST /day-vote` para votar por eliminación
4. **Monitorear progreso**: Se puede usar `GET /vote-counts` o `GET /voting-summary` para seguir el progreso
5. **Consultar voto propio**: Los jugadores pueden ver su voto actual con `GET /my-vote`
6. **Resolución**: Una vez que todos han votado, se puede proceder a eliminar al jugador más votado

## Reglas de Negocio de Votación

- **Fase requerida**: Solo durante `GameStatus.DAY`
- **Jugadores elegibles**: Solo jugadores vivos pueden votar
- **Objetivos válidos**: Cualquier jugador vivo (excepto uno mismo)
- **Cambio de voto**: Permitido (sobrescribe el voto anterior)
- **Mayoría**: El jugador con más votos es eliminado
- **Empates**: Se pueden implementar reglas de desempate específicas

## Servicios de Backend

Los endpoints utilizan el servicio `player_action_service.py` que incluye:

- `day_vote()`: Registra el voto de un jugador
- `get_day_vote_counts()`: Obtiene recuentos de votos
- `can_player_vote()`: Verifica permisos de votación
- `get_voting_eligible_players()`: Lista objetivos válidos
- `get_player_vote()`: Obtiene voto individual
- `get_voting_summary()`: Resumen completo de votación
- `reset_day_votes()`: Reinicia votos para nueva fase

## Estructura de Datos

El modelo `Game` fue extendido con:
```python
day_votes: Dict[str, str] = {}  # voter_id -> target_id
```

Ejemplo de estructura:
```python
{
  "player1": "player3",  # player1 vota por player3
  "player2": "player3",  # player2 vota por player3
  "player4": "player5"   # player4 vota por player5
}
```

## Modelos de Datos

### DayVoteRequest
```python
class DayVoteRequest(BaseModel):
    target_id: str
```

### VoteCount
```python
class VoteCount(BaseModel):
    player_id: str
    username: str
    vote_count: int
```

### DayVoteResponse
```python
class DayVoteResponse(BaseModel):
    success: bool
    message: str
    vote_counts: List[VoteCount] = []
    total_votes: int = 0
    total_players: int = 0
```

## Testing

Se incluyen tests comprehensivos en `tests/test_day_voting.py` que verifican:
- Votación exitosa durante el día
- Restricciones de fase (no votar durante la noche)
- Prohibición de auto-voto
- Recuento correcto de votos
- Permisos de votación
- Jugadores elegibles
- Resumen de votación
- Reinicio de votos
