/**
 * Ejemplo de refactorización de GameLobbyView.vue aplicando mejor los principios SOLID
 * 
 * MEJORAS PROPUESTAS:
 * 
 * 1. SINGLE RESPONSIBILITY PRINCIPLE (SRP): ✅ YA BIEN APLICADO
 *    - Vista enfocada solo en presentación
 *    - Lógica separada en composables
 * 
 * 2. OPEN/CLOSED PRINCIPLE (OCP): ✅ MEJORABLE 
 *    - Crear interfaces para los composables
 *    - Permitir inyección de dependencias
 * 
 * 3. LISKOV SUBSTITUTION PRINCIPLE (LSP): ⚠️ APLICAR
 *    - Crear clases base para diferentes tipos de lobby
 * 
 * 4. INTERFACE SEGREGATION PRINCIPLE (ISP): ⚠️ MEJORAR
 *    - Dividir interfaces grandes en más específicas
 * 
 * 5. DEPENDENCY INVERSION PRINCIPLE (DIP): ✅ YA BIEN APLICADO
 *    - Vista depende de abstracciones (composables)
 */

// ANTES - Composable monolítico
export function useGameLobby(gameId: string) {
  // Retorna todo junto: estado, acciones, permisos, etc.
  return {
    // Estado (15+ propiedades)
    game, loading, notification, creatorUser, playerUsers,
    // Computed (8+ propiedades)
    isCreator, canStartGame, canJoinGame, canLeaveGame,
    // Métodos (6+ funciones)
    loadGame, joinGame, leaveGame, startGame
  }
}

// DESPUÉS - Composables específicos siguiendo ISP
export function useGameLobbyState(gameId: string): GameLobbyState {
  return { game, loading, notification }
}

export function useGameLobbyPermissions(game: Game, auth: AuthState): GameLobbyPermissions {
  return { isCreator, canStartGame, canJoinGame, canLeaveGame }
}

export function useGameLobbyActions(gameId: string): GameLobbyActions {
  return { loadGame, joinGame, leaveGame, startGame }
}

// EJEMPLO DE VISTA MEJORADA:
