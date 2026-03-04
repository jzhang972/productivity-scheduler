"use client"

import { useMemo, useRef, useEffect, useState } from "react"
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCenter,
} from "@dnd-kit/core"
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable"
import { TimeBlockCard } from "./TimeBlockCard"
import { PX_PER_MINUTE, blockTop, snapToGrid, timeToMinutes, minutesToTime } from "@/lib/utils/time"
import { useUpdateBlock } from "@/lib/hooks/useTodayBlocks"
import type { TimeBlock } from "@/types"

const VIEW_START = 7 * 60   // 07:00
const VIEW_END = 22 * 60    // 22:00
const TOTAL_MINUTES = VIEW_END - VIEW_START
const TIMELINE_HEIGHT = TOTAL_MINUTES * PX_PER_MINUTE

// Hours to show on ruler
const HOUR_MARKS = Array.from({ length: TOTAL_MINUTES / 60 + 1 }, (_, i) => VIEW_START + i * 60)

interface TimelineProps {
  blocks: TimeBlock[]
  date: string
  onEdit: (block: TimeBlock) => void
  onDelete: (id: string) => void
}

export function Timeline({ blocks, date, onEdit, onDelete }: TimelineProps) {
  const updateBlock = useUpdateBlock(date)
  const [draggingId, setDraggingId] = useState<string | null>(null)
  const [nowOffset, setNowOffset] = useState<number | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Update "now" indicator every minute
  useEffect(() => {
    const update = () => {
      const now = new Date()
      const nowMin = now.getHours() * 60 + now.getMinutes()
      if (nowMin >= VIEW_START && nowMin <= VIEW_END) {
        setNowOffset((nowMin - VIEW_START) * PX_PER_MINUTE)
      } else {
        setNowOffset(null)
      }
    }
    update()
    const id = setInterval(update, 60_000)
    return () => clearInterval(id)
  }, [])

  // Scroll to current time on mount
  useEffect(() => {
    if (containerRef.current && nowOffset !== null) {
      containerRef.current.scrollTop = Math.max(0, nowOffset - 100)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  )

  const sortedBlocks = useMemo(
    () => [...blocks].sort((a, b) => a.start_time.localeCompare(b.start_time)),
    [blocks]
  )

  const draggingBlock = draggingId ? blocks.find((b) => b.id === draggingId) : null

  function handleDragEnd(event: DragEndEvent) {
    const { active, delta } = event
    setDraggingId(null)

    const block = blocks.find((b) => b.id === active.id)
    if (!block || !delta) return

    const deltaMinutes = Math.round(delta.y / PX_PER_MINUTE)
    const originalStart = timeToMinutes(block.start_time)
    const originalEnd = timeToMinutes(block.end_time)
    const duration = originalEnd - originalStart

    const newStart = snapToGrid(originalStart + deltaMinutes)
    const newEnd = newStart + duration

    if (newStart < VIEW_START || newEnd > VIEW_END) return

    updateBlock.mutate({
      id: block.id,
      data: {
        start_time: minutesToTime(newStart) + ":00",
        end_time: minutesToTime(newEnd) + ":00",
      },
    })
  }

  return (
    <div
      ref={containerRef}
      className="relative overflow-y-auto rounded-lg border bg-card"
      style={{ height: "70vh" }}
    >
      <div
        className="relative"
        style={{ height: TIMELINE_HEIGHT, minWidth: "100%" }}
      >
        {/* Hour ruler */}
        {HOUR_MARKS.map((min) => {
          const top = (min - VIEW_START) * PX_PER_MINUTE
          const label = minutesToTime(min)
          return (
            <div
              key={min}
              className="absolute left-0 right-0 flex items-center"
              style={{ top }}
            >
              <span className="w-14 pr-2 text-right text-xs text-muted-foreground flex-shrink-0">
                {label}
              </span>
              <div className="flex-1 border-t border-border/50" />
            </div>
          )
        })}

        {/* Now indicator */}
        {nowOffset !== null && (
          <div
            className="absolute left-14 right-0 flex items-center z-10 pointer-events-none"
            style={{ top: nowOffset }}
          >
            <div className="w-2 h-2 rounded-full bg-red-500 -ml-1 flex-shrink-0" />
            <div className="flex-1 border-t-2 border-red-500" />
          </div>
        )}

        {/* Time blocks */}
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={(e) => setDraggingId(String(e.active.id))}
          onDragEnd={handleDragEnd}
          onDragCancel={() => setDraggingId(null)}
        >
          <SortableContext
            items={sortedBlocks.map((b) => b.id)}
            strategy={verticalListSortingStrategy}
          >
            {sortedBlocks.map((block) => (
              <TimeBlockCard
                key={block.id}
                block={block}
                date={date}
                viewStartMinutes={VIEW_START}
                onEdit={onEdit}
                onDelete={onDelete}
                isPositioned
              />
            ))}
          </SortableContext>

          <DragOverlay>
            {draggingBlock && (
              <div className="opacity-70 rounded-md border bg-card shadow-lg p-2 text-xs font-medium">
                {draggingBlock.title ?? draggingBlock.category.name}
              </div>
            )}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  )
}
