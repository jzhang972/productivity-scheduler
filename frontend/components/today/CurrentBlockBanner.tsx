"use client"

import { CategoryBadge } from "@/components/shared/CategoryBadge"
import { WorkTimer } from "./WorkTimer"
import { useTimer } from "@/lib/hooks/useTimer"
import type { TimeBlock } from "@/types"

interface CurrentBlockBannerProps {
  block: TimeBlock
  date: string
}

export function CurrentBlockBanner({ block, date }: CurrentBlockBannerProps) {
  const timer = useTimer(date)

  const isThisBlock = timer.activeBlockId === block.id

  if (!isThisBlock) return null

  return (
    <div className="flex items-center gap-3 rounded-lg border bg-card px-4 py-3 shadow-sm">
      <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
      <CategoryBadge category={block.category} />
      <span className="text-sm font-medium flex-1 truncate">
        {block.title ?? block.category.name}
      </span>
      <WorkTimer
        elapsed={timer.elapsedFormatted}
        isRunning={timer.isRunning}
        isPaused={timer.isPaused}
        isStarting={timer.isStarting}
        isStopping={timer.isStopping}
        onStart={() => timer.startTimer(block.id)}
        onPause={timer.pauseTimer}
        onStop={() => timer.stopTimer()}
      />
    </div>
  )
}
