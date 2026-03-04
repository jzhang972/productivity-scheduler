"use client"

import { useState } from "react"
import { format } from "date-fns"
import { Plus, RefreshCw, ChevronLeft, ChevronRight } from "lucide-react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Timeline } from "@/components/today/Timeline"
import { TimeBlockModal } from "@/components/today/TimeBlockModal"
import { CurrentBlockBanner } from "@/components/today/CurrentBlockBanner"
import { TimePill } from "@/components/shared/TimePill"
import { useTodayBlocks, useDeleteBlock } from "@/lib/hooks/useTodayBlocks"
import { useUIStore } from "@/lib/store/uiStore"
import { useTimerStore } from "@/lib/store/timerStore"
import { scheduleApi } from "@/lib/api/schedule"
import type { TimeBlock } from "@/types"

export default function TodayPage() {
  const { selectedDate, setSelectedDate, openCreateModal, openEditModal } = useUIStore()
  const [editingBlock, setEditingBlock] = useState<TimeBlock | null>(null)
  const activeBlockId = useTimerStore((s) => s.activeBlockId)

  const { data: blocks = [], isLoading } = useTodayBlocks(selectedDate)
  const deleteBlock = useDeleteBlock(selectedDate)
  const qc = useQueryClient()

  const generateMutation = useMutation({
    mutationFn: () => scheduleApi.generate(selectedDate, true),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["time-blocks", selectedDate] }),
  })

  const activeBlock = activeBlockId ? blocks.find((b) => b.id === activeBlockId) : null

  const totalPlanned = blocks.reduce((sum, b) => sum + b.planned_duration, 0)
  const totalDone = blocks
    .filter((b) => b.status === "done")
    .reduce((sum, b) => sum + b.planned_duration, 0)

  function handleEdit(block: TimeBlock) {
    setEditingBlock(block)
    openEditModal(block.id)
  }

  function handleDelete(id: string) {
    if (confirm("Delete this block?")) {
      deleteBlock.mutate(id)
    }
  }

  function handleDateChange(delta: number) {
    const d = new Date(selectedDate + "T00:00:00")
    d.setDate(d.getDate() + delta)
    setSelectedDate(format(d, "yyyy-MM-dd"))
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => handleDateChange(-1)} className="text-muted-foreground hover:text-foreground">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold">
              {format(new Date(selectedDate + "T00:00:00"), "EEEE, MMMM d")}
            </h1>
            <p className="text-sm text-muted-foreground">
              {selectedDate === format(new Date(), "yyyy-MM-dd") ? "Today" : selectedDate}
            </p>
          </div>
          <button onClick={() => handleDateChange(1)} className="text-muted-foreground hover:text-foreground">
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          {/* Summary pills */}
          <TimePill minutes={totalDone} className="text-green-600 bg-green-50" />
          <span className="text-muted-foreground text-sm">/</span>
          <TimePill minutes={totalPlanned} />

          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-secondary"
          >
            <RefreshCw className={`h-4 w-4 ${generateMutation.isPending ? "animate-spin" : ""}`} />
            Generate
          </button>

          <button
            onClick={() => { setEditingBlock(null); openCreateModal() }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
          >
            <Plus className="h-4 w-4" />
            Add Block
          </button>
        </div>
      </div>

      {/* Active block banner — sticky below the navigation */}
      {activeBlock && (
        <div className="sticky top-0 z-30 -mx-4 px-4 pb-1 bg-background">
          <CurrentBlockBanner block={activeBlock} date={selectedDate} />
        </div>
      )}

      {/* Timeline */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64 text-muted-foreground text-sm">
          Loading…
        </div>
      ) : (
        <Timeline
          blocks={blocks}
          date={selectedDate}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}

      {/* Modal */}
      <TimeBlockModal date={selectedDate} editingBlock={editingBlock} />
    </div>
  )
}
