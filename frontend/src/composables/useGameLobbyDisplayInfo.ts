/**
 * Composable específico para información de visualización del lobby
 * Responsabilidad única: Formatear y preparar datos para mostrar en la UI
 * Sigue SRP (Single Responsibility Principle)
 */
import { computed, type Ref } from 'vue'
import type { Game } from '../types'

export function useGameLobbyDisplayInfo(game: Ref<Game | null>, creatorUser: Ref<any | null>) {
  
  const gameStatusText = computed(() => {
    if (!game.value) return ''
    
    const statusMap: { [key: string]: string } = {
      'waiting': 'Esperando jugadores',
      'started': 'Iniciada',
      'night': 'Fase nocturna',
      'day': 'Fase diurna',
      'paused': 'Pausada',
      'finished': 'Finalizada'
    }
    return statusMap[game.value.status] || game.value.status
  })

  const creatorName = computed(() => {
    if (!game.value) return ''
    if (creatorUser.value) return creatorUser.value.username
    return 'Desconocido'
  })

  // Función para formatear fechas
  const formatDate = (dateString: string): string => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return {
    gameStatusText,
    creatorName,
    formatDate
  }
}
