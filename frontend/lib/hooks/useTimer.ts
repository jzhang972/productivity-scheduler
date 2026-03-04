"use client"

import { useEffect, useCallback } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useTimerStore, selectTotalElapsed } from "@/lib/store/timerStore"
import { timeLogsApi } from "@/lib/api/timeLogs"
import { formatSeconds } from "@/lib/utils/time"

export function useTimer(date: string) {
  const store = useTimerStore()
  const qc = useQueryClient()

  // Tick every second
  useEffect(() => {
    if (!store.activeLogId || store.isPaused) return
    const id = setInterval(() => store.tick(), 1000)
    return () => clearInterval(id)
  }, [store.activeLogId, store.isPaused, store.tick])

  const startMutation = useMutation({
    mutationFn: ({ blockId }: { blockId: string }) =>
      timeLogsApi.start(blockId),
    onSuccess: (log, { blockId }) => {
      store.startTimer(log.id, blockId)
      qc.invalidateQueries({ queryKey: ["time-blocks", date] })
    },
  })

  const pauseMutation = useMutation({
    mutationFn: () => {
      if (!store.activeLogId) throw new Error("No active timer")
      return timeLogsApi.pause(store.activeLogId)
    },
    onSuccess: () => {
      store.pauseTimer()
      qc.invalidateQueries({ queryKey: ["time-blocks", date] })
    },
  })

  const stopMutation = useMutation({
    mutationFn: ({ interruptions = 0 }: { interruptions?: number } = {}) => {
      if (!store.activeLogId) throw new Error("No active timer")
      return timeLogsApi.stop(store.activeLogId, interruptions)
    },
    onSuccess: () => {
      store.stopTimer()
      qc.invalidateQueries({ queryKey: ["time-blocks", date] })
    },
  })

  const elapsed = selectTotalElapsed(store)

  return {
    activeBlockId: store.activeBlockId,
    activeLogId: store.activeLogId,
    isPaused: store.isPaused,
    elapsed,
    elapsedFormatted: formatSeconds(elapsed),
    isRunning: !!store.activeLogId && !store.isPaused,
    startTimer: (blockId: string) => startMutation.mutate({ blockId }),
    pauseTimer: () => pauseMutation.mutate(),
    stopTimer: (interruptions?: number) => stopMutation.mutate({ interruptions }),
    isStarting: startMutation.isPending,
    isStopping: stopMutation.isPending,
  }
}
