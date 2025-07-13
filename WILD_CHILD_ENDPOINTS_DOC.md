# Documentación de Endpoints del Niño Salvaje

Esta documentación describe todos los endpoints disponibles para las acciones específicas del **Niño Salvaje** en el juego de Hombres Lobo.

## Información General

El Niño Salvaje es un rol único que:
- **Comienza como Aldeano** en el bando del pueblo
- **En la primera noche** debe elegir a un jugador como su "modelo a seguir"
- **Si su modelo muere**, se transforma inmediatamente en **Hombre Lobo**
- **Los demás Hombres Lobo** son notificados de su transformación en el siguiente turno nocturno

### Prefijo de Rutas
Todos los endpoints del Niño Salvaje tienen el prefijo `/wild-child`

---

## Endpoints Disponibles

### 1. Obtener Estado del Niño Salvaje
**GET** `/wild-child/status/{game_id}`

Obtiene el estado actual del Niño Salvaje: si tiene modelo, si se transformó, rol actual, etc.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Estado del Niño Salvaje obtenido correctamente",
  "has_model": true,
  "model_player_id": "player123",
  "model_username": "NombreModelo",
  "is_transformed": false,
  "current_role": "wild_child"
}
```

#### Errores:
- **403**: Solo el Niño Salvaje puede acceder a esta información
- **404**: No se pudo obtener información del Niño Salvaje

---

### 2. Obtener Modelos Disponibles
**GET** `/wild-child/available-models/{game_id}`

Obtiene la lista de jugadores que pueden ser elegidos como modelo (todos los jugadores vivos excepto él mismo).

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Se encontraron 4 modelos disponibles",
  "available_models": [
    {
      "id": "player1",
      "username": "Jugador1"
    },
    {
      "id": "player2",
      "username": "Jugador2"
    }
  ]
}
```

#### Errores:
- **403**: Solo el Niño Salvaje puede acceder a esta información

---

### 3. Elegir Jugador Modelo
**POST** `/wild-child/choose-model`

Permite al Niño Salvaje elegir su jugador modelo en la primera noche.

#### Cuerpo de la Petición:
```json
{
  "model_player_id": "player123"
}
```

#### Parámetros de Ruta:
- `game_id` (query): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Has elegido a NombreJugador como tu modelo a seguir",
  "model_player_id": "player123",
  "model_username": "NombreJugador"
}
```

#### Errores:
- **403**: No puedes elegir un modelo en este momento
- **400**: El jugador elegido como modelo no existe
- **400**: No se pudo elegir el modelo

---

### 4. Verificar Capacidad de Elección
**GET** `/wild-child/can-choose-model/{game_id}`

Verifica si el Niño Salvaje puede elegir un modelo en el momento actual.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "can_choose_model": true,
  "message": "Puedes elegir un modelo"
}
```

---

### 5. Obtener Información de Transformación
**GET** `/wild-child/transformation-info/{game_id}`

Obtiene información detallada sobre la transformación del Niño Salvaje.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "transformation_info": {
    "has_model": true,
    "model_player_id": "player123",
    "model_username": "NombreModelo",
    "model_is_alive": false,
    "is_transformed": true,
    "current_role": "warewolf",
    "original_role": "wild_child"
  },
  "message": "Información de transformación obtenida correctamente"
}
```

#### Errores:
- **404**: No se encontró información de transformación

---

### 6. Verificar Transformación por Muerte
**POST** `/wild-child/check-transformation/{game_id}`

Verifica si la muerte de un jugador específico causa la transformación del Niño Salvaje.

#### Parámetros:
- `game_id` (path): ID de la partida
- `dead_player_id` (query): ID del jugador que murió

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "transformations": [
    {
      "wild_child_id": "wildchild123",
      "wild_child_username": "NiñoSalvaje",
      "model_id": "player123",
      "reason": "Su modelo player123 ha muerto"
    }
  ],
  "message": "Se procesaron 1 transformaciones"
}
```

---

### 7. Obtener Notificación para Hombres Lobo
**GET** `/wild-child/werewolf-notification/{game_id}`

Obtiene información sobre nuevos miembros de la manada para hombres lobo existentes.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "new_werewolves": [
    {
      "id": "wildchild123",
      "username": "NiñoSalvaje",
      "original_role": "wild_child"
    }
  ],
  "message": "Se encontraron 1 nuevos miembros de la manada"
}
```

#### Errores:
- **403**: Solo los hombres lobo pueden acceder a esta información
- **404**: Partida o jugador no encontrado

---

### 8. Inicializar Niño Salvaje
**POST** `/wild-child/initialize/{game_id}`

Inicializa al Niño Salvaje al comienzo del juego.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "message": "Niño Salvaje inicializado correctamente"
}
```

#### Errores:
- **400**: No se pudo inicializar al Niño Salvaje

---

### 9. Procesar Verificaciones de Muerte
**POST** `/wild-child/process-death-checks/{game_id}`

Procesa todas las verificaciones de muerte para posibles transformaciones.

#### Parámetros:
- `game_id` (path): ID de la partida

#### Respuesta Exitosa (200):
```json
{
  "success": true,
  "transformations": [
    {
      "wild_child_id": "wildchild123",
      "wild_child_username": "NiñoSalvaje",
      "model_id": "model123",
      "reason": "Su modelo model123 ha muerto"
    }
  ],
  "message": "Se procesaron 1 verificaciones de transformación"
}
```

---

## Reglas y Restricciones

### Elección de Modelo:
1. **Solo Primera Noche**: El modelo debe elegirse en la primera noche (round 1)
2. **Solo Fase Nocturna**: Solo durante `GameStatus.NIGHT`
3. **Una Sola Vez**: No puede cambiar de modelo una vez elegido
4. **Cualquier Jugador Vivo**: Puede elegir a cualquier jugador excepto a sí mismo

### Transformación:
1. **Automática**: Se produce inmediatamente cuando muere el modelo
2. **Irreversible**: Una vez transformado, no puede volver a ser aldeano
3. **Cambio de Bando**: Pasa del bando aldeano al bando de los hombres lobo
4. **Notificación a Hombres Lobo**: Los hombres lobo existentes son notificados

### Condiciones Especiales:
- **Si el modelo es el último Hombre Lobo eliminado**: El Niño Salvaje mantiene la victoria con los aldeanos
- **Transformación durante el juego**: Puede acceder a las acciones de los hombres lobo desde la siguiente noche
- **Identificación**: Los aldeanos no son informados de la transformación automáticamente

---

## Flujo de Juego Típico

### Primera Noche:
1. El Niño Salvaje recibe notificación para elegir modelo
2. Consulta modelos disponibles con `GET /available-models/{game_id}`
3. Elige modelo con `POST /choose-model`
4. El sistema registra la elección

### Durante el Juego:
1. Cada vez que muere un jugador, el sistema verifica automáticamente transformaciones
2. Si muere el modelo, el Niño Salvaje se transforma instantáneamente
3. Los hombres lobo existentes reciben notificación del nuevo miembro
4. El Niño Salvaje puede acceder a acciones de hombre lobo desde la siguiente noche

### Verificación de Estado:
- El Niño Salvaje puede consultar su estado en cualquier momento con `GET /status/{game_id}`
- Puede ver información de transformación con `GET /transformation-info/{game_id}`

---

## Modelos de Datos

### WildChildChooseModelRequest
```json
{
  "model_player_id": "string"  // ID del jugador modelo
}
```

### WildChildChooseModelResponse
```json
{
  "success": true,
  "message": "string",
  "model_player_id": "string",
  "model_username": "string"
}
```

### WildChildStatusResponse
```json
{
  "success": true,
  "message": "string",
  "has_model": boolean,
  "model_player_id": "string|null",
  "model_username": "string|null",
  "is_transformed": boolean,
  "current_role": "string"  // "wild_child" o "warewolf"
}
```

### WildChildAvailableModelsResponse
```json
{
  "success": true,
  "message": "string",
  "available_models": [
    {
      "id": "string",
      "username": "string"
    }
  ]
}
```

---

## Autenticación

Todos los endpoints requieren autenticación JWT. El token debe incluirse en el header:
```
Authorization: Bearer <jwt_token>
```

El Niño Salvaje solo puede realizar acciones en partidas donde esté participando y tenga asignado el rol de `GameRole.WILD_CHILD` (o `GameRole.WAREWOLF` después de la transformación).

---

## Integración con Otros Sistemas

### Sistema de Muerte:
- Debe llamar a `POST /check-transformation/{game_id}` después de cada muerte
- Puede usar `POST /process-death-checks/{game_id}` para verificaciones masivas

### Sistema de Hombres Lobo:
- Debe consultar `GET /werewolf-notification/{game_id}` para informar de nuevos miembros
- El Niño Salvaje transformado puede acceder a endpoints de hombres lobo

### Sistema de Roles:
- El rol cambia automáticamente de `WILD_CHILD` a `WAREWOLF` en la transformación
- Mantiene referencia al rol original para propósitos de victoria especial
