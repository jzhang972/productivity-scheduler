/**
 * Convert a hex color to RGBA CSS string with the given opacity.
 */
export function hexToRgba(hex: string, opacity: number): string {
  const clean = hex.replace("#", "")
  const r = parseInt(clean.slice(0, 2), 16)
  const g = parseInt(clean.slice(2, 4), 16)
  const b = parseInt(clean.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

/**
 * Return a contrasting text color (black or white) for a given background hex.
 */
export function contrastColor(hex: string): string {
  const clean = hex.replace("#", "")
  const r = parseInt(clean.slice(0, 2), 16)
  const g = parseInt(clean.slice(2, 4), 16)
  const b = parseInt(clean.slice(4, 6), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? "#000000" : "#ffffff"
}

export const STATUS_COLORS: Record<string, string> = {
  planned: "#94a3b8",
  in_progress: "#3b82f6",
  done: "#22c55e",
  missed: "#ef4444",
}
