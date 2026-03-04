import { cn } from "@/lib/utils/cn"
import { formatMinutes } from "@/lib/utils/time"

interface TimePillProps {
  minutes: number
  className?: string
  variant?: "default" | "muted"
}

export function TimePill({ minutes, className, variant = "default" }: TimePillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-1.5 py-0.5 text-xs font-mono",
        variant === "muted"
          ? "bg-muted text-muted-foreground"
          : "bg-secondary text-secondary-foreground",
        className
      )}
    >
      {formatMinutes(minutes)}
    </span>
  )
}
