import { cn } from "@/lib/utils/cn"
import { formatMinutes } from "@/lib/utils/time"
import { hexToRgba } from "@/lib/utils/color"
import type { CategoryWeeklyProgress } from "@/types"

interface WeeklyProgressBarProps {
  progress: CategoryWeeklyProgress
}

export function WeeklyProgressBar({ progress }: WeeklyProgressBarProps) {
  const pct = Math.min(progress.completion_pct, 100)
  const isDeficit = progress.deficit_minutes > 0
  const isSurplus = progress.actual_minutes > progress.weekly_target_minutes

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <span
            className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: progress.color_hex }}
          />
          <span className="font-medium">{progress.category_name}</span>
          {isDeficit && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-red-50 text-red-600 font-medium">
              -{formatMinutes(progress.deficit_minutes)}
            </span>
          )}
          {isSurplus && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-green-50 text-green-600 font-medium">
              +{formatMinutes(progress.actual_minutes - progress.weekly_target_minutes)}
            </span>
          )}
        </div>
        <span className="text-muted-foreground text-xs tabular-nums">
          {formatMinutes(progress.actual_minutes)} / {formatMinutes(progress.weekly_target_minutes)}
        </span>
      </div>

      <div className="relative h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
          style={{
            width: `${pct}%`,
            backgroundColor: progress.color_hex,
          }}
        />
      </div>
    </div>
  )
}
