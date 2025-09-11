# Integración de Stores de Pinia en GameLobbyView

## Resumen

Se ha implementado la sincronización automática de los stores de Pinia (`gameStore` y `playerStore`) cuando se cargan los datos de la partida en el componente `GameLobbyView.vue`. Esto asegura que los datos estén disponibles de forma reactiva para otros componentes que consuman estos stores.

## Cambios Implementados

### 1. Función Auxiliar `updateStoresWithGameData`

Se creó una función auxiliar que centraliza la lógica de actualización de ambos stores:

```typescript
const updateStoresWithGameData = (gameData: typeof game.value) => {
  if (!gameData) return
  
  // Actualizar gameStore
  gameStore.setGameId(gameData.game_id)
  gameStore.setGameStatus(gameData.status)
  gameStore.setFirstNight(gameData.is_first_night)
  gameStore.setConnectionInfo(gameData.connected_players_count, gameData.current_players)
  
  // Actualizar playerStore
  const gamePlayersForStore = gameData.players.map(player => ({
    id: player.player_id,
    username: player.username,
    status: player.is_alive ? 'alive' : 'dead',
    role: '', // El rol no se expone en el lobby
    game_id: gameData.game_id
  }))
  playerStore.setPlayers(gamePlayersForStore)
  
  // Actualizar lista de jugadores conectados
  const connectedPlayerIds = gameData.players
    .filter(player => player.is_connected)
    .map(player => player.player_id)
  playerStore.setConnectedPlayers(connectedPlayerIds)
}
```

### 2. Actualización en `onMounted`

Al cargar los datos de la partida inicialmente, se llama a `updateStoresWithGameData`:

```typescript
onMounted(async () => {
  await loadGame()
  
  if (game.value) {
    // Inicializar conexión WebSocket
    const playersArray = game.value.players.map(player => ({ 
      id: player.player_id, 
      username: player.username 
    }))
    initializePlayersStatus(playersArray)
    
    // Actualizar stores de Pinia con los datos cargados
    updateStoresWithGameData(game.value)
  }
})
```

### 3. Actualización en `joinGame`

Cuando un usuario se une a la partida, también se actualizan los stores:

```typescript
const joinGame = async () => {
  await originalJoinGame()
  if (game.value) {
    // Actualizar WebSocket y stores
    const playersArray = game.value.players.map(player => ({ 
      id: player.player_id, 
      username: player.username 
    }))
    initializePlayersStatus(playersArray)
    updateStoresWithGameData(game.value)
  }
}
```

## Datos Sincronizados

### GameStore
- `gameId`: ID de la partida
- `gameStatus`: Estado actual de la partida
- `isFirstNight`: Si es la primera noche
- `connectedPlayersCount` y `totalPlayersCount`: Información de conexión

### PlayerStore
- `players`: Lista completa de jugadores con información pública
- `connectedPlayers`: IDs de jugadores conectados

## Beneficios

1. **Reactividad**: Los datos están disponibles automáticamente para otros componentes
2. **Sincronización**: Los stores se mantienen actualizados con la información más reciente
3. **Separación de responsabilidades**: La lógica de actualización está centralizada
4. **Compatibilidad**: Funciona con el nuevo formato `GameResponse` del backend

## Uso en Otros Componentes

Otros componentes pueden ahora acceder a los datos de la partida a través de los stores:

```typescript
import { useGameStore } from '@/stores/gameStore'
import { usePlayerStore } from '@/stores/player'

const gameStore = useGameStore()
const playerStore = usePlayerStore()

// Acceso reactivo a los datos
const gameId = computed(() => gameStore.gameId)
const players = computed(() => playerStore.players)
const connectedCount = computed(() => gameStore.connectedPlayersCount)
```

## Compatibilidad WebSocket

Esta implementación es compatible con las actualizaciones por WebSocket. Los stores pueden recibir actualizaciones tanto de carga HTTP inicial como de mensajes WebSocket en tiempo real.
