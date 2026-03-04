"use client"

import { Play, Pause, Square } from "lucide-react"
import { cn } from "@/lib/utils/cn"

interface WorkTimerProps {
  elapsed: string    // "MM:SS"
  isRunning: boolean
  isPaused: boolean
  isStarting?: boolean
  isStopping?: boolean
  onStart: () => void
  onPause: () => void
  onStop: () => void
  className?: string
}

export function WorkTimer({
  elapsed,
  isRunning,
  isPaused,
  isStarting,
  isStopping,
  onStart,
  onPause,
  onStop,
  className,
}: WorkTimerProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span className="font-mono text-sm tabular-nums w-12">{elapsed}</span>

      {!isRunning && !isPaused ? (
        <button
          onClick={onStart}
          disabled={isStarting}
          className="flex items-center gap-1 px-2 py-1 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:opacity-90 disabled:opacity-50"
        >
          <Play className="h-3 w-3" />
          Start
        </button>
      ) : (
        <>
          {isRunning ? (
            <button
              onClick={onPause}
              className="flex items-center gap-1 px-2 py-1 rounded-md bg-secondary text-secondary-foreground text-xs font-medium hover:opacity-90"
            >
              <Pause className="h-3 w-3" />
              Pause
            </button>
          ) : (
            <button
              onClick={onStart}
              className="flex items-center gap-1 px-2 py-1 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:opacity-90"
            >
              <Play className="h-3 w-3" />
              Resume
            </button>
          )}
          <button
            onClick={onStop}
            disabled={isStopping}
            className="flex items-center gap-1 px-2 py-1 rounded-md bg-destructive text-destructive-foreground text-xs font-medium hover:opacity-90 disabled:opacity-50"
          >
            <Square className="h-3 w-3" />
            Stop
          </button>
        </>
      )}
    </div>
  )
}
