import { create } from "zustand"
import { persist } from "zustand/middleware"

interface TimerState {
  activeLogId: string | null
  activeBlockId: string | null
  startedAt: number | null      // unix ms
  elapsedSeconds: number
  isPaused: boolean

  // Actions
  startTimer: (logId: string, blockId: string) => void
  pauseTimer: () => void
  resumeTimer: (logId: string) => void
  stopTimer: () => void
  tick: () => void
}

export const useTimerStore = create<TimerState>()(
  persist(
    (set, get) => ({
      activeLogId: null,
      activeBlockId: null,
      startedAt: null,
      elapsedSeconds: 0,
      isPaused: false,

      startTimer: (logId, blockId) =>
        set({
          activeLogId: logId,
          activeBlockId: blockId,
          startedAt: Date.now(),
          elapsedSeconds: 0,
          isPaused: false,
        }),

      pauseTimer: () => {
        const { startedAt, elapsedSeconds } = get()
        const additional = startedAt
          ? Math.floor((Date.now() - startedAt) / 1000)
          : 0
        set({
          isPaused: true,
          startedAt: null,
          elapsedSeconds: elapsedSeconds + additional,
        })
      },

      resumeTimer: (logId) =>
        set({
          activeLogId: logId,
          startedAt: Date.now(),
          isPaused: false,
        }),

      stopTimer: () =>
        set({
          activeLogId: null,
          activeBlockId: null,
          startedAt: null,
          elapsedSeconds: 0,
          isPaused: false,
        }),

      tick: () => {
        const { startedAt, isPaused, elapsedSeconds } = get()
        if (!isPaused && startedAt) {
          set({
            elapsedSeconds: Math.floor((Date.now() - startedAt) / 1000),
          })
        }
      },
    }),
    {
      name: "timer-store",
      // Only persist identity fields, not the tick state
      partialize: (state) => ({
        activeLogId: state.activeLogId,
        activeBlockId: state.activeBlockId,
        startedAt: state.startedAt,
        elapsedSeconds: state.elapsedSeconds,
        isPaused: state.isPaused,
      }),
    }
  )
)

// Derived selector: total elapsed seconds including current segment
export function selectTotalElapsed(state: TimerState): number {
  if (state.isPaused || !state.startedAt) return state.elapsedSeconds
  return state.elapsedSeconds + Math.floor((Date.now() - state.startedAt) / 1000)
}
