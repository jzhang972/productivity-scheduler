"use client"

interface EnergyRatingProps {
  value: number
  onChange: (v: number) => void
}

const LABELS = ["", "Drained", "Low", "Okay", "Good", "Peak"]
const COLORS = ["", "#ef4444", "#f97316", "#eab308", "#22c55e", "#6366f1"]

export function EnergyRating({ value, onChange }: EnergyRatingProps) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          className="flex flex-col items-center gap-1 px-3 py-2 rounded-lg border transition-all"
          style={
            value === n
              ? { borderColor: COLORS[n], backgroundColor: COLORS[n] + "20" }
              : {}
          }
        >
          <span className="text-lg">{["", "😫", "😞", "😐", "😊", "🚀"][n]}</span>
          <span className="text-xs text-muted-foreground">{LABELS[n]}</span>
        </button>
      ))}
    </div>
  )
}
