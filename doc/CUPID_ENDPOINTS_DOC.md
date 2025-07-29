# Documentación de Endpoints de Cupido

## Descripción General

Cupido es un rol especial que en la primera noche debe elegir a dos jugadores para que se conviertan en enamorados. Los enamorados tienen una conexión especial: si uno muere, el otro también muere inmediatamente de pena. Si ambos enamorados sobreviven y son los únicos dos jugadores restantes, ganan la partida independientemente de sus roles originales.

## Endpoints Disponibles

### 1. Elegir Enamorados
**POST** `/cupid/choose-lovers/{game_id}`

Permite a Cupido elegir a dos jugadores como enamorados durante la primera noche.

**Request Body:**
```json
{
  "lover1_id": "string",
  "lover2_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Enamorados elegidos exitosamente",
  "lover1_id": "string",
  "lover1_username": "string",
  "lover2_id": "string",
  "lover2_username": "string"
}
```

**Restricciones:**
- Solo puede ser usado por Cupido
- Solo en la primera noche del juego
- Los dos jugadores deben ser diferentes
- Ambos jugadores deben estar vivos
- Solo se puede usar una vez por partida

### 2. Estado de Cupido
**GET** `/cupid/status/{game_id}`

Obtiene el estado actual de Cupido y información sobre los enamorados elegidos.

**Response:**
```json
{
  "success": true,
  "message": "Estado de Cupido obtenido",
  "has_chosen_lovers": true,
  "lover1_id": "string",
  "lover1_username": "string",
  "lover2_id": "string",
  "lover2_username": "string"
}
```

### 3. Objetivos Disponibles
**GET** `/cupid/available-targets/{game_id}`

Obtiene la lista de jugadores disponibles para ser enamorados.

**Response:**
```json
{
  "success": true,
  "message": "Objetivos disponibles obtenidos",
  "available_targets": [
    {
      "id": "string",
      "username": "string"
    }
  ]
}
```

**Restricciones:**
- Solo puede ser usado por Cupido
- Solo cuando puede elegir enamorados (primera noche)

### 4. Estado de Enamorado
**GET** `/cupid/lovers-status/{game_id}`

Obtiene el estado de enamorado del jugador actual.

**Response:**
```json
{
  "success": true,
  "message": "Estado de enamorado obtenido",
  "is_lover": true,
  "partner_id": "string",
  "partner_username": "string",
  "both_alive": true
}
```

**Notas:**
- Cualquier jugador puede consultar su propio estado
- Solo muestra información si el jugador es efectivamente enamorado

### 5. Verificar Muerte de Enamorados
**POST** `/cupid/check-lovers-death/{game_id}?dead_player_id=string`

Verifica si algún enamorado debe morir cuando muere su pareja.

**Response:**
```json
{
  "success": true,
  "message": "Verificación de muerte de enamorados completada",
  "deaths_by_love": ["string"]
}
```

**Uso:**
- Llamada automática del sistema cuando un jugador muere
- Devuelve lista de IDs de jugadores que mueren por amor

### 6. Verificar Condición de Victoria
**GET** `/cupid/check-victory-condition/{game_id}`

Verifica si los enamorados han ganado la partida.

**Response:**
```json
{
  "success": true,
  "message": "Los enamorados han ganado",
  "victory": true,
  "victory_info": {
    "victory_type": "lovers",
    "winners": [
      {
        "id": "string",
        "username": "string"
      }
    ],
    "message": "Los enamorados han ganado la partida"
  }
}
```

### 7. Inicializar Cupido
**POST** `/cupid/initialize/{game_id}`

Inicializa las acciones nocturnas de Cupido.

**Response:**
```json
{
  "success": true,
  "message": "Acciones de Cupido inicializadas"
}
```

### 8. Reiniciar Acciones
**POST** `/cupid/reset/{game_id}`

Reinicia las acciones nocturnas de Cupido (solo para administradores).

**Response:**
```json
{
  "success": true,
  "message": "Acciones de Cupido reiniciadas"
}
```

## Mecánicas Especiales

### 1. Enlace de Enamorados
- Cuando Cupido elige dos jugadores, estos se convierten en enamorados
- Cada enamorado conoce la identidad de su pareja
- Si uno muere (por cualquier causa), el otro muere inmediatamente

### 2. Condición de Victoria Especial
- Si solo quedan dos jugadores vivos y ambos son enamorados enlazados, ganan la partida
- Esta victoria supera cualquier otra condición de victoria (aldeanos vs. hombres lobo)
- Funciona independientemente de los roles originales de los enamorados

### 3. Secreto de Cupido
- Solo Cupido conoce quiénes son los enamorados
- Los enamorados solo conocen a su pareja, no saben que Cupido los eligió
- La información de quién es Cupido se mantiene secreta

## Integración con el Flujo del Juego

### Primera Noche
1. Cupido debe elegir dos enamorados antes de que termine la fase nocturna
2. Los enamorados son notificados de su nueva condición
3. El juego continúa normalmente

### Procesamiento de Muertes
1. Cuando un jugador muere, se verifica automáticamente si era enamorado
2. Si era enamorado, su pareja muere inmediatamente
3. Se verifica la condición de victoria después de cada muerte

### Verificación de Victoria
- Se debe verificar después de cada muerte si solo quedan dos enamorados
- La condición de victoria de enamorados tiene prioridad sobre otras condiciones

## Códigos de Error Comunes

- **403**: No tienes permisos para realizar esta acción (no eres Cupido)
- **400**: No puedes realizar esta acción en este momento
- **400**: Jugadores inválidos seleccionados
- **400**: Ya has elegido enamorados en esta partida
