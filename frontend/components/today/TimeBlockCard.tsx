"use client"

import { useSortable } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import { GripVertical, Edit2, Trash2 } from "lucide-react"
import { CategoryBadge } from "@/components/shared/CategoryBadge"
import { StatusDot } from "@/components/shared/StatusDot"
import { TimePill } from "@/components/shared/TimePill"
import { WorkTimer } from "./WorkTimer"
import { useTimer } from "@/lib/hooks/useTimer"
import { hexToRgba } from "@/lib/utils/color"
import { blockTop, blockHeight } from "@/lib/utils/time"
import type { TimeBlock } from "@/types"

interface TimeBlockCardProps {
  block: TimeBlock
  date: string
  viewStartMinutes?: number
  onEdit: (block: TimeBlock) => void
  onDelete: (id: string) => void
  isPositioned?: boolean  // absolute CSS positioning on timeline
}

export function TimeBlockCard({
  block,
  date,
  viewStartMinutes = 7 * 60,
  onEdit,
  onDelete,
  isPositioned = true,
}: TimeBlockCardProps) {
  const timer = useTimer(date)
  const isThisBlock = timer.activeBlockId === block.id

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: block.id,
    disabled: block.status === "done" || block.status === "in_progress",
  })

  const style = isPositioned
    ? {
        position: "absolute" as const,
        top: blockTop(block.start_time, viewStartMinutes),
        height: blockHeight(block.planned_duration),
        left: 64,
        right: 8,
        transform: CSS.Transform.toString(transform),
        transition,
        zIndex: isDragging ? 50 : isThisBlock ? 20 : 1,
      }
    : {
        transform: CSS.Transform.toString(transform),
        transition,
      }

  const bg = hexToRgba(block.category.color_hex, isDragging ? 0.9 : isThisBlock ? 0.85 : 0.15)
  const border = hexToRgba(block.category.color_hex, 0.5)

  return (
    <div
      ref={setNodeRef}
      style={{
        ...style,
        backgroundColor: bg,
        borderLeft: `3px solid ${block.category.color_hex}`,
        borderColor: border,
      }}
      className="rounded-md border overflow-hidden select-none"
    >
      <div className="flex items-start gap-1 p-2 h-full">
        {/* Drag handle */}
        <button
          {...attributes}
          {...listeners}
          className="mt-0.5 text-muted-foreground/50 hover:text-muted-foreground cursor-grab active:cursor-grabbing flex-shrink-0"
        >
          <GripVertical className="h-3.5 w-3.5" />
        </button>

        <div className="flex-1 min-w-0 flex flex-col gap-0.5">
          <div className="flex items-center gap-1.5 flex-wrap">
            <StatusDot status={block.status} />
            <CategoryBadge category={block.category} size="sm" />
            <TimePill minutes={block.planned_duration} variant="muted" />
          </div>

          {block.title && (
            <p className="text-xs font-medium truncate">{block.title}</p>
          )}

          <p className="text-xs text-muted-foreground">
            {block.start_time.slice(0, 5)} – {block.end_time.slice(0, 5)}
          </p>

          {/* Timer controls — show only elapsed when this block is active (banner has the buttons) */}
          {block.status !== "done" && block.status !== "missed" && (
            isThisBlock ? (
              <span className="mt-0.5 font-mono text-sm tabular-nums text-blue-600">
                {timer.elapsedFormatted}
              </span>
            ) : (
              <WorkTimer
                elapsed="00:00"
                isRunning={false}
                isPaused={false}
                isStarting={timer.isStarting}
                isStopping={timer.isStopping}
                onStart={() => timer.startTimer(block.id)}
                onPause={timer.pauseTimer}
                onStop={() => timer.stopTimer()}
                className="mt-0.5"
              />
            )
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-1 flex-shrink-0">
          <button
            onClick={() => onEdit(block)}
            className="text-muted-foreground/50 hover:text-foreground"
          >
            <Edit2 className="h-3 w-3" />
          </button>
          <button
            onClick={() => onDelete(block.id)}
            className="text-muted-foreground/50 hover:text-destructive"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  )
}
