# Eliminación de get_game_status y Actualización de game_status

## Resumen

Se ha eliminado el tipo de mensaje duplicado `get_game_status` y se ha actualizado la estructura del mensaje `game_status` para usar el formato `GameResponse` del backend.

## Cambios Realizados

### 1. **Eliminación de Duplicación**

**Eliminado:**
- ❌ `get_game_status` del tipo union `WebSocketMessageType`
- ❌ `get_game_status` del mapa `WebSocketMessageMap`
- ❌ Documentación redundante en `copilot-ws-messages.md`

**Motivo:** `get_game_status` y `game_status` tenían la misma estructura, violando el principio DRY.

### 2. **Actualización de Estructura game_status**

**Antes** (estructura legacy):
```typescript
game_status: { 
  game_id: string; 
  phase: string; 
  players: Array<{ id: string; username: string; status?: string; role?: string }>;
  connected_players: string[];
  living_players: string[];
  dead_players: string[];
  is_first_night?: boolean;
  time_remaining?: number;
}
```

**Después** (estructura GameResponse):
```typescript
game_status: { 
  game_id: string; 
  name: string;
  creator_id: string;
  creator_name: string;
  status: string;
  current_round: number;
  is_first_night: boolean;
  max_players: number;
  current_players: number;
  players: Array<{ 
    player_id: string; 
    username: string; 
    is_alive: boolean; 
    is_connected: boolean; 
    user_status: string; 
  }>;
  eliminated_players: string[];
  connected_players_count: number;
  created_at: string;
  success: boolean;
  message: string;
}
```

### 3. **Actualización del GameStore**

Actualizado el handler de `game_status` en `gameStore.ts` para procesar la nueva estructura:

```typescript
subscribeToMessage('game_status', (data) => {
  if (data) {
    // Información básica del juego
    if (data.game_id) this.setGameId(data.game_id)
    if (data.status) this.setGameStatus(data.status)
    if (data.current_round !== undefined) this.setCurrentPhase(`Round ${data.current_round}`)
    if (data.is_first_night !== undefined) this.setFirstNight(data.is_first_night)
    
    // Conversión de PublicPlayerInfo a GamePlayer
    if (data.players) {
      const gamePlayers = data.players.map(player => ({
        id: player.player_id,
        username: player.username,
        status: player.is_alive ? 'alive' : 'dead',
        role: '', // No se expone en game_status
        game_id: data.game_id
      }))
      this.setPlayers(gamePlayers)
    }
    
    // Información de conexión actualizada
    if (data.connected_players_count !== undefined && data.current_players !== undefined) {
      this.setConnectionInfo(data.connected_players_count, data.current_players)
    }
    
    // Listas de jugadores vivos/muertos
    if (data.players) {
      const livingPlayers = data.players.filter(p => p.is_alive).map(p => p.player_id)
      const deadPlayers = data.players.filter(p => !p.is_alive).map(p => p.player_id)
      this.setPlayerLists(livingPlayers, deadPlayers)
    }
  }
})
```

## Beneficios de los Cambios

### 1. **Eliminación de Duplicación (DRY)**
- ✅ Un solo tipo `game_status` en lugar de dos idénticos
- ✅ Mantenimiento simplificado
- ✅ Menos confusión para desarrolladores

### 2. **Consistencia con Backend**
- ✅ Estructura alineada con `GameResponse` del backend
- ✅ Datos más ricos y completos
- ✅ Tipado más preciso

### 3. **Mejor Información**
- ✅ **Información del creador**: `creator_id` y `creator_name`
- ✅ **Estado real del juego**: `status` en lugar de `phase` genérico
- ✅ **Información de jugadores más rica**: `PublicPlayerInfo` con estado de conexión
- ✅ **Contadores precisos**: `connected_players_count`, `current_players`, `max_players`
- ✅ **Metadatos**: `created_at`, `success`, `message`

### 4. **Seguridad Mejorada**
- ✅ No expone información sensible (roles, acciones nocturnas)
- ✅ Solo datos públicos seguros para todos los jugadores
- ✅ Estructura validada por Pydantic en backend

## Compatibilidad

### ✅ **Frontend**
- GameStore actualizado para nueva estructura
- Tipos WebSocket actualizados
- No hay breaking changes en componentes (usan stores reactivos)

### ✅ **Backend**
- Ya envía estructura `GameResponse` en mensajes `game_status`
- Compatible con nueva estructura de frontend
- Mantiene seguridad de datos públicos

## Validación

### **Archivos Verificados:**
- ✅ `frontend/src/types/websocket.ts` - Tipos actualizados
- ✅ `frontend/src/stores/gameStore.ts` - Handler actualizado
- ✅ `frontend/src/websocket/copilot-ws-messages.md` - Documentación limpia

### **Sin Referencias Rotas:**
- ✅ No hay referencias a `get_game_status` en el código
- ✅ No hay errores de compilación TypeScript
- ✅ Estructura compatible con backend existente

## Próximos Pasos Recomendados

1. **Testing**: Verificar que los mensajes `game_status` se reciben correctamente
2. **UI Validation**: Confirmar que los stores reactivos actualizan correctamente los componentes
3. **Integration**: Verificar que el backend envía la estructura correcta

## Conclusión

Esta refactorización elimina duplicación innecesaria, mejora la consistencia con el backend y proporciona información más rica y precisa para el frontend, todo mientras mantiene la funcionalidad existente y mejora la tipificación TypeScript.
