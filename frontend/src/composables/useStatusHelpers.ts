// Composable / helper utilities for game status presentation
// Exports small, pure functions so components can reuse and be easier to test
export const statusMeta: Record<string, { badge: string; cardClass?: string }> = {
  waiting: { badge: 'bg-success', cardClass: 'border-start border-4 border-success' },
  started: { badge: 'bg-primary', cardClass: 'border-start border-4 border-primary' },
  night: { badge: 'bg-primary', cardClass: 'border-start border-4 border-primary' },
  day: { badge: 'bg-primary', cardClass: 'border-start border-4 border-primary' },
  paused: { badge: 'bg-warning', cardClass: 'border-start border-4 border-warning' },
  finished: { badge: 'bg-secondary', cardClass: 'border-start border-4 border-secondary opacity-75' }
}

export function getBootstrapCardClass(status: string): string {
  const base = 'border-start border-4'
  if (!status) return base
  const meta = (statusMeta as any)[status]
  return meta && meta.cardClass ? meta.cardClass : base
}

export function getStatusBadgeClass(status: string): string {
  if (!status) return 'bg-secondary'
  const meta = (statusMeta as any)[status]
  return meta && meta.badge ? meta.badge : 'bg-secondary'
}

export function getStatusText(status: string): string {
  // Minimal mapping; leave text transformation here so components can import if needed
  switch (status) {
    case 'waiting':
      return 'Esperando'
    case 'started':
      return 'Iniciada'
    case 'night':
      return 'Noche'
    case 'day':
      return 'Día'
    case 'paused':
      return 'Pausada'
    case 'finished':
      return 'Finalizada'
    default:
      return status || ''
  }
}
