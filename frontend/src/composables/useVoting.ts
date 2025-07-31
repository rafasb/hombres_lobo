/**
 * Composable para manejar votaciones en el juego
 * Proporciona una interfaz reactiva para el sistema de votación
 */
import { computed } from 'vue'
import { useRealtimeGameStore } from '@/stores/realtime-game'

export function useVoting() {
  const realtimeGameStore = useRealtimeGameStore()

  // Estados reactivos
  const votingSession = computed(() => realtimeGameStore.gameState.votingSession)
  const userVote = computed(() => realtimeGameStore.gameState.userVote)
  const canVote = computed(() => realtimeGameStore.canVote)
  const isVotingActive = computed(() => realtimeGameStore.isVotingActive)
  const hasUserVoted = computed(() => realtimeGameStore.hasUserVoted)
  const validTargets = computed(() => realtimeGameStore.validVotingTargets)
  const voteResults = computed(() => realtimeGameStore.voteResults)
  const timeRemaining = computed(() => realtimeGameStore.votingTimeRemaining)

  // Computeds adicionales
  const votingProgress = computed(() => {
    if (!votingSession.value) return { voted: 0, total: 0, percentage: 0 }

    const voted = votingSession.value.votes.length
    const total = votingSession.value.eligible_voters.length
    const percentage = total > 0 ? Math.round((voted / total) * 100) : 0

    return { voted, total, percentage }
  })

  const voteCountsByTarget = computed(() => {
    if (!votingSession.value) return {}

    const counts: Record<string, number> = {}
    votingSession.value.votes.forEach(vote => {
      counts[vote.target_id] = (counts[vote.target_id] || 0) + vote.weight
    })

    return counts
  })

  const leadingCandidate = computed(() => {
    const counts = voteCountsByTarget.value
    const entries = Object.entries(counts)

    if (entries.length === 0) return null

    const sorted = entries.sort(([, a], [, b]) => b - a)
    return {
      playerId: sorted[0][0],
      votes: sorted[0][1],
      isTied: sorted.length > 1 && sorted[0][1] === sorted[1][1]
    }
  })

  const isUserEligible = computed(() => {
    if (!votingSession.value || !realtimeGameStore.currentUser) return false
    return votingSession.value.eligible_voters.includes(
      realtimeGameStore.currentUser.id.toString()
    )
  })

  // Funciones
  const castVote = (targetPlayerId: string) => {
    return realtimeGameStore.castVote(targetPlayerId)
  }

  const getVotingStatus = () => {
    return realtimeGameStore.getVotingStatus()
  }

  const formatTimeRemaining = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getPlayerName = (playerId: string): string => {
    const player = realtimeGameStore.gameState.players.find(p => p.id === playerId)
    return player?.name || `Jugador ${playerId}`
  }

  return {
    // Estados
    votingSession,
    userVote,
    canVote,
    isVotingActive,
    hasUserVoted,
    validTargets,
    voteResults,
    timeRemaining,
    isUserEligible,

    // Computeds
    votingProgress,
    voteCountsByTarget,
    leadingCandidate,

    // Funciones
    castVote,
    getVotingStatus,
    formatTimeRemaining,
    getPlayerName
  }
}
