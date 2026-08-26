/**
 * Wraps any API mutation so it degrades gracefully when offline.
 *
 * Usage:
 *   const { execute } = useOfflineMutation()
 *
 *   // Without optimistic data — just queue + toast, returns { _offline: true }
 *   const result = await execute(() => logFeedingSession(payload))
 *
 *   // With optimistic data — caller gets a fake record to show immediately
 *   const log = await execute(
 *     () => createHealthLog(payload),
 *     () => ({ ...payload, logged_at: new Date().toISOString() })
 *   )
 *   if (log._offline) { /* show pending indicator *\/ }
 *
 * Throws for real API errors so the caller can still show error messages.
 */
export function useOfflineMutation() {
  async function execute(apiFn, makeOptimistic = null) {
    try {
      return await apiFn()
    } catch (err) {
      if (err.isOfflineQueued) {
        // Show a subtle toast from the store (imported lazily to avoid circular deps)
        try {
          const { useToastStore } = await import('@/stores/toast')
          useToastStore().info('Saved offline ☁️', 'Will sync automatically when reconnected.')
        } catch { /* toast store not ready */ }

        if (typeof makeOptimistic === 'function') {
          // Return a temporary record so the UI can show it immediately
          return {
            ...makeOptimistic(),
            id: -(Date.now()),   // negative temp ID won't clash with real IDs
            _offline: true,
          }
        }
        return { _offline: true }
      }
      // Real error — let the caller handle it
      throw err
    }
  }

  return { execute }
}
