import { cn } from "@/lib/utils/cn"
import { STATUS_COLORS } from "@/lib/utils/color"
import type { BlockStatus } from "@/types"

interface StatusDotProps {
  status: BlockStatus
  className?: string
}

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span
      className={cn("inline-block w-2 h-2 rounded-full flex-shrink-0", className)}
      style={{ backgroundColor: STATUS_COLORS[status] }}
      title={status}
    />
  )
}
