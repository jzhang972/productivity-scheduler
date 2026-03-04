import { cn } from "@/lib/utils/cn"
import { contrastColor, hexToRgba } from "@/lib/utils/color"
import type { Category } from "@/types"

interface CategoryBadgeProps {
  category: Pick<Category, "name" | "color_hex" | "is_deep_work">
  className?: string
  size?: "sm" | "md"
}

export function CategoryBadge({ category, className, size = "md" }: CategoryBadgeProps) {
  const textColor = contrastColor(category.color_hex)
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-0.5 text-xs",
        className
      )}
      style={{ backgroundColor: category.color_hex, color: textColor }}
    >
      {category.is_deep_work && (
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-current opacity-70" />
      )}
      {category.name}
    </span>
  )
}
