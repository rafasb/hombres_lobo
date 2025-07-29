# Documentación de Endpoints de la Bruja

Esta documentación describe todos los endpoints disponibles para las acciones específicas de la **Bruja** en el juego de Hombres Lobo.

## Información General

La Bruja es un rol especial que puede usar dos pociones durante toda la partida:
- **Poción de Curación**: Para salvar a la víctima del ataque de los hombres lobo
- **Poción de Veneno**: Para eliminar a cualquier jugador (incluso a sí misma)

### Prefijo de Rutas
Todos los endpoints de la bruja tienen el prefijo `/witch`

---

## Endpoints Disponibles

### 1. Obtener Información Nocturna
**GET** `/witch/night-info/{game_id}`

Obtiene información completa de la noche para la bruja, incluyendo quién fue atacado y qué pociones tiene disponibles.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Información nocturna obtenida correctamente",
  "attacked_player_id": "player123",
  "attacked_username": "NombreJugador",
  "can_heal": true,
  "can_poison": true
}
```

#### Errores:
- **403**: Solo la bruja puede acceder a esta información
- **404**: No se pudo obtener información de la partida

---

### 2. Usar Poción de Curación
**POST** `/witch/heal`

Permite a la bruja usar su poción de curación para salvar a la víctima del ataque de los hombres lobo.

#### Cuerpo de la Petición:
```json
{
  "target_id": "player123"
}
```

#### Parámetros de Ruta:
- `game_id` (query): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Has usado tu poción de curación para salvar a NombreJugador",
  "healed_player_id": "player123",
  "healed_username": "NombreJugador"
}
```

#### Errores:
- **403**: No puedes usar la poción de curación en este momento
- **400**: Solo puedes curar a la víctima del ataque de los hombres lobo
- **400**: No se pudo realizar la curación

---

### 3. Usar Poción de Veneno
**POST** `/witch/poison`

Permite a la bruja usar su poción de veneno para eliminar a un jugador.

#### Cuerpo de la Petición:
```json
{
  "target_id": "player123"
}
```

#### Parámetros de Ruta:
- `game_id` (query): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Has usado tu poción de veneno contra NombreJugador",
  "poisoned_player_id": "player123",
  "poisoned_username": "NombreJugador"
}
```

#### Errores:
- **403**: No puedes usar la poción de veneno en este momento
- **400**: No se pudo realizar el envenenamiento

---

### 4. Verificar Capacidad de Curación
**GET** `/witch/can-heal/{game_id}`

Verifica si la bruja puede usar su poción de curación en el momento actual.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "can_heal": true,
  "message": "Puedes usar la poción de curación"
}
```

---

### 5. Verificar Capacidad de Envenenamiento
**GET** `/witch/can-poison/{game_id}`

Verifica si la bruja puede usar su poción de veneno en el momento actual.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "can_poison": true,
  "message": "Puedes usar la poción de veneno"
}
```

---

### 6. Obtener Objetivos para Envenenar
**GET** `/witch/poison-targets/{game_id}`

Obtiene la lista de todos los jugadores que la bruja puede envenenar (todos los jugadores vivos).

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "targets": [
    {
      "id": "player1",
      "username": "Jugador1"
    },
    {
      "id": "player2", 
      "username": "Jugador2"
    }
  ],
  "message": "Se encontraron 2 objetivos disponibles"
}
```

#### Errores:
- **403**: Solo la bruja puede acceder a esta información

---

### 7. Obtener Víctima del Ataque
**GET** `/witch/attack-victim/{game_id}`

Obtiene información sobre el jugador atacado por los hombres lobo esta noche.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "victim_id": "player123",
  "message": "Víctima del ataque obtenida"
}
```

#### Errores:
- **403**: Solo la bruja puede acceder a esta información

---

### 8. Inicializar Pociones
**POST** `/witch/initialize-potions/{game_id}`

Inicializa las pociones de la bruja al comienzo del juego (uso administrativo).

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Pociones inicializadas correctamente"
}
```

#### Errores:
- **400**: No se pudieron inicializar las pociones

---

## Reglas y Restricciones

### Uso de Pociones:
1. **Poción de Curación**: 
   - Solo se puede usar una vez durante toda la partida
   - Solo puede curar a la víctima del ataque de los hombres lobo
   - Solo funciona durante la fase nocturna

2. **Poción de Veneno**: 
   - Solo se puede usar una vez durante toda la partida
   - Puede envenenar a cualquier jugador vivo (incluso a sí misma)
   - Solo funciona durante la fase nocturna

### Condiciones para Actuar:
- La partida debe estar en fase nocturna (`GameStatus.NIGHT`)
- La bruja debe estar viva
- Debe tener la poción correspondiente disponible
- Solo la bruja puede realizar estas acciones

### Procesamiento Nocturno:
- Las acciones de la bruja se procesan junto con otras acciones nocturnas
- La curación salva a la víctima del ataque de los hombres lobo
- El veneno elimina inmediatamente al objetivo
- Las pociones usadas se pierden permanentemente

---

## Modelos de Datos

### WitchHealRequest
```json
{
  "target_id": "string"  // ID del jugador a curar
}
```

### WitchPoisonRequest
```json
{
  "target_id": "string"  // ID del jugador a envenenar
}
```

### WitchNightInfoResponse
```json
{
  "success": true,
  "message": "string",
  "attacked_player_id": "string|null",
  "attacked_username": "string|null", 
  "can_heal": boolean,
  "can_poison": boolean
}
```

### WitchHealResponse
```json
{
  "success": true,
  "message": "string",
  "healed_player_id": "string",
  "healed_username": "string"
}
```

### WitchPoisonResponse
```json
{
  "success": true,
  "message": "string",
  "poisoned_player_id": "string",
  "poisoned_username": "string"
}
```

---

## Autenticación

Todos los endpoints requieren autenticación JWT. El token debe incluirse en el header:
```
Authorization: Bearer <jwt_token>
```

La bruja solo puede realizar acciones en partidas donde esté participando y tenga asignado el rol de `GameRole.WITCH`.
