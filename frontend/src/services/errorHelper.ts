export function extractErrorMessage(err: unknown, fallback = 'Error inesperado') {
  // Axios errors often have response.data.detail
  try {
    const anyErr = err as any
    if (anyErr?.response?.data?.detail) {
      return anyErr.response.data.detail
    }
    if (anyErr?.message) return anyErr.message
    return String(anyErr)
  } catch (e) {
    return fallback
  }
}
