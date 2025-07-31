/**
 * Composable para manejar fases del juego
 * Proporciona información reactiva sobre el estado actual del juego
 */
import { computed } from 'vue'
import { useRealtimeGameStore } from '@/stores/realtime-game'

export function useGamePhase() {
  const realtimeGameStore = useRealtimeGameStore()

  // Estados reactivos
  const currentPhase = computed(() => realtimeGameStore.gameState.phase.current)
  const timeRemaining = computed(() => realtimeGameStore.gameState.phase.timeRemaining)
  const phaseDuration = computed(() => realtimeGameStore.gameState.phase.duration)
  const isHost = computed(() => realtimeGameStore.gameState.isHost)

  // Computeds para diferentes fases
  const isWaiting = computed(() => currentPhase.value === 'waiting')
  const isStarting = computed(() => currentPhase.value === 'starting')
  const isNight = computed(() => currentPhase.value === 'night')
  const isDay = computed(() => currentPhase.value === 'day')
  const isVoting = computed(() => currentPhase.value === 'voting')
  const isTrial = computed(() => currentPhase.value === 'trial')
  const isExecution = computed(() => currentPhase.value === 'execution')
  const isFinished = computed(() => currentPhase.value === 'finished')

  // Progreso de la fase
  const phaseProgress = computed(() => {
    if (phaseDuration.value === 0) return 0
    const elapsed = phaseDuration.value - timeRemaining.value
    return Math.round((elapsed / phaseDuration.value) * 100)
  })

  const phaseProgressInverse = computed(() => {
    return 100 - phaseProgress.value
  })

  // Información de la fase
  const phaseInfo = computed(() => {
    const phaseData: Record<string, { name: string; description: string; color: string; icon: string }> = {
      waiting: {
        name: 'Esperando',
        description: 'Esperando que todos los jugadores se conecten',
        color: 'gray',
        icon: '⏳'
      },
      starting: {
        name: 'Iniciando',
        description: 'El juego está comenzando...',
        color: 'blue',
        icon: '🚀'
      },
      night: {
        name: 'Noche',
        description: 'Los roles especiales actúan en secreto',
        color: 'purple',
        icon: '🌙'
      },
      day: {
        name: 'Día',
        description: 'Debate y discusión entre jugadores',
        color: 'yellow',
        icon: '☀️'
      },
      voting: {
        name: 'Votación',
        description: 'Tiempo de votar por la eliminación',
        color: 'red',
        icon: '🗳️'
      },
      trial: {
        name: 'Juicio',
        description: 'El acusado se defiende',
        color: 'orange',
        icon: '⚖️'
      },
      execution: {
        name: 'Ejecución',
        description: 'Se revela el resultado',
        color: 'red',
        icon: '💀'
      },
      finished: {
        name: 'Final',
        description: 'El juego ha terminado',
        color: 'green',
        icon: '🏁'
      }
    }

    return phaseData[currentPhase.value] || phaseData.waiting
  })

  // Formateo de tiempo
  const formatTimeRemaining = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const timeRemainingFormatted = computed(() => {
    return formatTimeRemaining(timeRemaining.value)
  })

  // Acciones permitidas por fase
  const canChat = computed(() => {
    return isDay.value || isVoting.value || isTrial.value
  })

  const canUseNightAction = computed(() => {
    return isNight.value && realtimeGameStore.isUserAlive
  })

  const canVote = computed(() => {
    return isVoting.value && realtimeGameStore.canVote
  })

  const canForceNextPhase = computed(() => {
    return isHost.value && !isFinished.value
  })

  // Funciones
  const forceNextPhase = () => {
    if (canForceNextPhase.value) {
      realtimeGameStore.forceNextPhase()
    }
  }

  return {
    // Estados básicos
    currentPhase,
    timeRemaining,
    phaseDuration,
    isHost,

    // Estados de fase específicos
    isWaiting,
    isStarting,
    isNight,
    isDay,
    isVoting,
    isTrial,
    isExecution,
    isFinished,

    // Información de progreso
    phaseProgress,
    phaseProgressInverse,
    phaseInfo,
    timeRemainingFormatted,

    // Permisos por fase
    canChat,
    canUseNightAction,
    canVote,
    canForceNextPhase,

    // Funciones
    formatTimeRemaining,
    forceNextPhase
  }
}
