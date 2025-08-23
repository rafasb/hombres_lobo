# Documentación de Endpoints - Rol Vidente

## Descripción
Los endpoints de la Vidente permiten a los jugadores con este rol usar su habilidad especial de investigación durante la fase nocturna.

## Funcionalidad del Rol
- **Habilidad:** Cada noche, la Vidente puede seleccionar un jugador para conocer su verdadero rol
- **Limitaciones:** Solo puede usar su habilidad una vez por noche
- **Fase:** Solo durante la fase nocturna (NIGHT)
- **Objetivo:** No puede investigarse a sí misma, solo jugadores vivos

---

## Endpoints Disponibles

### 1. POST `/games/{game_id}/seer-vision`
**Descripción:** Permite a la vidente investigar el rol de otro jugador.

**Parámetros:**
- `game_id` (path): ID de la partida
- Cuerpo del request:
  ```json
  {
    "target_id": "string"  // ID del jugador a investigar
  }
  ```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Has investigado a {username}",
  "target_role": "warewolf",  // Rol del jugador investigado
  "target_username": "NombreJugador"
}
```

**Errores posibles:**
- `400`: No puede usar la habilidad en este momento
- `400`: Objetivo no válido (no existe, está muerto, o es la propia vidente)
- `401`: No autenticado
- `403`: No es una vidente

---

### 2. GET `/games/{game_id}/seer-targets`
**Descripción:** Obtiene la lista de jugadores que la vidente puede investigar.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
[
  {
    "id": "player1",
    "username": "Aldeano1"
  },
  {
    "id": "player2", 
    "username": "Lobo1"
  }
]
```

**Errores posibles:**
- `403`: No tiene permisos (no es vidente o no puede actuar)
- `404`: Partida no encontrada

---

### 3. GET `/games/{game_id}/can-seer-act`
**Descripción:** Verifica si el usuario puede usar su habilidad de vidente.

**Parámetros:**
- `game_id` (path): ID de la partida

**Respuesta exitosa (200):**
```json
{
  "can_act": true  // true si puede actuar, false si no
}
```

**Condiciones para `can_act: true`:**
- Es fase nocturna (NIGHT)
- El jugador es una vidente
- Está vivo
- No ha usado su habilidad esta noche

---

## Flujo de Uso

### Durante la Fase Nocturna:

1. **Verificar disponibilidad:**
   ```
   GET /games/{game_id}/can-seer-act
   ```

2. **Obtener objetivos válidos:**
   ```
   GET /games/{game_id}/seer-targets
   ```

3. **Realizar investigación:**
   ```
   POST /games/{game_id}/seer-vision
   Body: {"target_id": "player_to_investigate"}
   ```

4. **Resultado:** La respuesta incluye el rol verdadero del jugador investigado

---

## Lógica de Negocio

### Validaciones:
- ✅ Solo durante fase nocturna
- ✅ Solo videntes vivas
- ✅ Una investigación por noche
- ✅ No auto-investigación
- ✅ Solo objetivos vivos

### Reinicio por Ronda:
- Al cambiar de fase nocturna, se reinicia la habilidad `has_used_vision_tonight = false`
- Esto permite usar la habilidad en cada nueva noche

### Información Revelada:
- **Rol exacto:** Se revela el rol verdadero (warewolf, villager, witch, etc.)
- **Información privada:** Solo la vidente ve el resultado
- **Estrategia:** La vidente decide cuándo y cómo compartir esta información

---

## Ejemplos de Uso

### Caso 1: Investigación Exitosa
```bash
# 1. Verificar si puede actuar
curl -X GET "http://localhost:8000/games/game123/can-seer-act" \
  -H "Authorization: Bearer {token}"

# Respuesta: {"can_act": true}

# 2. Ver objetivos disponibles
curl -X GET "http://localhost:8000/games/game123/seer-targets" \
  -H "Authorization: Bearer {token}"

# 3. Investigar jugador sospechoso
curl -X POST "http://localhost:8000/games/game123/seer-vision" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"target_id": "suspicious_player"}'

# Respuesta: {
#   "success": true,
#   "message": "Has investigado a SuspiciousPlayer",
#   "target_role": "warewolf",
#   "target_username": "SuspiciousPlayer"
# }
```

### Caso 2: Ya Usó la Habilidad
```bash
curl -X POST "http://localhost:8000/games/game123/seer-vision" \
  -H "Authorization: Bearer {token}" \
  -d '{"target_id": "another_player"}'

# Respuesta 400: {
#   "detail": "No puedes usar tu habilidad de vidente en este momento"
# }
```

---

## Integración con Otros Sistemas

### Con el Sistema de Fases:
- La habilidad se habilita automáticamente al entrar en fase nocturna
- Se deshabilita al cambiar a fase diurna
- Se reinicia para la siguiente noche

### Con el Sistema de Roles:
- Identifica automáticamente a las videntes por su rol
- Verifica el estado vivo/muerto
- Mantiene el historial de acciones nocturnas

### Con la UI/Frontend:
- Los endpoints proporcionan toda la información necesaria
- Interfaz puede mostrar objetivos válidos
- Resultado se presenta de forma privada al jugador vidente
