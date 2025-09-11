# Migración de Interfaces Game en Frontend

## 📋 Resumen de Cambios

Se ha actualizado la interfaz `Game` del frontend para que coincida exactamente con la clase `GameResponse` del backend, que contiene solo información pública segura.

## 🔄 Interfaces Actualizadas

### ✅ Nuevas Interfaces (Información Pública)

#### `Game` (Principal)
```typescript
export interface Game {
  // Información básica de la partida
  game_id: string              // Cambió de 'id' a 'game_id'
  name: string
  creator_id: string
  creator_name: string         // NUEVO: Nombre del creador

  // Estado actual de la partida
  status: GameStatus
  current_round: number
  is_first_night: boolean

  // Información de jugadores
  max_players: number
  current_players: number
  players: PublicPlayerInfo[]  // CAMBIÓ: De Record<string, PlayerInfo> a PublicPlayerInfo[]
  eliminated_players: string[]
  connected_players_count: number  // NUEVO: Contador de conectados

  // Información temporal
  created_at: string | null

  // Metadatos
  success: boolean             // NUEVO: Estado de la operación
  message: string              // NUEVO: Mensaje descriptivo
}
```

#### `PublicPlayerInfo` (Nueva)
```typescript
export interface PublicPlayerInfo {
  player_id: string
  username: string
  is_alive: boolean
  is_connected: boolean        // NUEVO: Estado de conexión
  user_status: UserStatus      // NUEVO: Estado del usuario
}
```

#### `GameStateUpdate` (Nueva)
```typescript
export interface GameStateUpdate {
  game_id: string
  status: GameStatus
  current_round: number
  current_players: number
  connected_players_count: number
  players: PublicPlayerInfo[]
  eliminated_players: string[]
  update_type: string          // NUEVO: Tipo de actualización
  timestamp: string | null     // NUEVO: Timestamp de la actualización
}
```

### 🔒 Interfaces Legacy (Información Completa)

#### `LegacyGame` (Temporal)
- Mantiene la estructura original del `Game` antiguo
- Contiene información sensible (roles, acciones nocturnas, etc.)
- Usada por endpoints que aún no han migrado al nuevo sistema

#### `PlayerInfo` (Información Sensible)
- Contiene información completa del jugador incluyendo rol
- Solo disponible para el propio jugador
- No debe ser compartida con otros jugadores

## 🚀 Beneficios de la Nueva Estructura

### 🔐 Seguridad
- ❌ **Eliminado**: `players: Record<string, PlayerInfo>` (contenía roles)
- ❌ **Eliminado**: `night_actions` (acciones nocturnas sensibles)
- ❌ **Eliminado**: `votes` (información de votación privada)
- ❌ **Eliminado**: `connected_players: string[]` (sustituido por contador)
- ❌ **Eliminado**: `player_ids` (sustituido por `players` con info pública)

### ✅ Mejoras
- ✅ **Agregado**: `creator_name` - Nombre visible del creador
- ✅ **Agregado**: `connected_players_count` - Número de jugadores conectados
- ✅ **Agregado**: `is_connected` por jugador - Estado de conexión individual
- ✅ **Agregado**: `user_status` por jugador - Estado del usuario
- ✅ **Agregado**: `success` y `message` - Metadatos de respuesta
- ✅ **Mejorado**: `players` ahora es array tipado con información pública

### 🎯 Casos de Uso

#### Para Mostrar Lista de Jugadores
```typescript
// Antes (inseguro)
const players = Object.values(game.players).map(p => ({
  id: p.player_id,
  name: "???", // No teníamos el username
  alive: p.is_alive,
  role: p.role // ¡EXPUESTO!
}));

// Ahora (seguro)
const players = game.players.map(p => ({
  id: p.player_id,
  name: p.username,
  alive: p.is_alive,
  connected: p.is_connected
  // rol NO disponible (seguro)
}));
```

#### Para Mostrar Estado de Conexión
```typescript
// Antes
const connectedCount = game.connected_players.length;

// Ahora
const connectedCount = game.connected_players_count;
const playersStatus = game.players.map(p => ({
  name: p.username,
  connected: p.is_connected,
  status: p.user_status
}));
```

## 📝 Plan de Migración

### Fase 1: ✅ Completada
- [x] Crear nuevas interfaces `Game`, `PublicPlayerInfo`, `GameStateUpdate`
- [x] Crear interfaz temporal `LegacyGame`
- [x] Actualizar endpoint GET `/game/{game_id}` en backend
- [x] Documentar cambios

### Fase 2: 🚧 En Progreso
- [ ] Actualizar componentes de frontend para usar nueva interfaz `Game`
- [ ] Migrar stores/servicios que usan `Game`
- [ ] Probar integración con nuevos datos

### Fase 3: 📋 Pendiente
- [ ] Actualizar endpoints backend restantes para usar `GameResponse`
- [ ] Migrar interfaces `AssignRolesResponse`, `UpdateGameStatusResponse`, etc.
- [ ] Eliminar interfaz `LegacyGame`

### Fase 4: 🔮 Futuro
- [ ] Implementar actualizaciones WebSocket con `GameStateUpdate`
- [ ] Optimizar rendering con nueva estructura de datos
- [ ] Añadir notificaciones de conexión en tiempo real

## ⚠️ Consideraciones para Desarrolladores

### Cambios Importantes
1. **`game.id` → `game.game_id`**: Cambió el nombre del campo ID
2. **`game.players`**: Ahora es array de `PublicPlayerInfo` en lugar de Record con `PlayerInfo`
3. **Sin información de roles**: Los roles ya no están disponibles en la respuesta del juego
4. **Nuevos campos**: `creator_name`, `connected_players_count`, `success`, `message`

### Compatibilidad
- Los endpoints que devuelven `LegacyGame` siguen funcionando
- Migración gradual sin breaking changes inmediatos
- Nuevos desarrollos deben usar la nueva interfaz `Game`

### Debugging
- Usar `game.success` y `game.message` para debugging
- Verificar `game.connected_players_count` para problemas de conexión
- Revisar `player.user_status` para estado individual de usuarios

## 🔗 Archivos Relacionados

- **Frontend**: `frontend/src/types/game.ts`
- **Backend**: `backend/app/models/game_responses.py`
- **Servicio**: `backend/app/services/game_responses_service.py`
- **Endpoint**: `backend/app/api/routes_game.py`
- **Documentación**: `Docs/GAME_RESPONSE_DOCUMENTATION.md`
