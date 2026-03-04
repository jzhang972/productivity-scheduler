"use client"

import { useState } from "react"
import { format, startOfWeek, addWeeks, subWeeks } from "date-fns"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { useWeeklyProgress } from "@/lib/hooks/useWeeklyProgress"
import { WeeklyProgressBar } from "@/components/weekly/WeeklyProgressBar"
import { ProgressRing } from "@/components/shared/ProgressRing"
import { formatMinutes } from "@/lib/utils/time"
import { toApiDate } from "@/lib/utils/dateRange"

export default function WeeklyPage() {
  const [weekStart, setWeekStart] = useState(() =>
    startOfWeek(new Date(), { weekStartsOn: 1 })
  )

  const weekStartStr = toApiDate(weekStart)
  const { data, isLoading } = useWeeklyProgress(weekStartStr)

  const totalPct = data
    ? Math.round(
        (data.total_actual_minutes /
          Math.max(data.categories.reduce((s, c) => s + c.weekly_target_minutes, 0), 1)) *
          100
      )
    : 0

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Weekly Progress</h1>
        <div className="flex items-center gap-2 text-sm">
          <button
            onClick={() => setWeekStart((w) => subWeeks(w, 1))}
            className="text-muted-foreground hover:text-foreground"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="w-40 text-center">
            {format(weekStart, "MMM d")} – {format(addWeeks(weekStart, 1), "MMM d, yyyy")}
          </span>
          <button
            onClick={() => setWeekStart((w) => addWeeks(w, 1))}
            className="text-muted-foreground hover:text-foreground"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-sm text-muted-foreground">Loading…</div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Summary card */}
          <div className="rounded-lg border bg-card p-6 flex flex-col items-center gap-3 md:col-span-1">
            <ProgressRing
              value={totalPct}
              size={120}
              strokeWidth={10}
              label={`${totalPct}%`}
            />
            <div className="text-center">
              <p className="text-2xl font-bold">{formatMinutes(data.total_actual_minutes)}</p>
              <p className="text-sm text-muted-foreground">of planned {formatMinutes(data.total_planned_minutes)}</p>
            </div>
          </div>

          {/* Per-category progress */}
          <div className="rounded-lg border bg-card p-6 flex flex-col gap-4 md:col-span-2">
            <h2 className="font-semibold text-sm">Category Breakdown</h2>
            {data.categories.length === 0 ? (
              <p className="text-sm text-muted-foreground">No data for this week.</p>
            ) : (
              data.categories.map((cat) => (
                <WeeklyProgressBar key={cat.category_id} progress={cat} />
              ))
            )}
          </div>
        </div>
      ) : null}
    </div>
  )
}
