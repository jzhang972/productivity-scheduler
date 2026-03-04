/**
 * Convert "HH:MM:SS" time string to total minutes from midnight.
 */
export function timeToMinutes(time: string): number {
  const [h, m] = time.split(":").map(Number)
  return h * 60 + m
}

/**
 * Convert minutes from midnight to "HH:MM" string.
 */
export function minutesToTime(minutes: number): string {
  const h = Math.floor(minutes / 60) % 24
  const m = minutes % 60
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`
}

/**
 * Format seconds as "MM:SS" for timer display.
 */
export function formatSeconds(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
}

/**
 * Format minutes as "Xh Ym" human-readable string.
 */
export function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes}m`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m === 0 ? `${h}h` : `${h}h ${m}m`
}

/**
 * Calculate CSS top offset (px) for a block starting at startMinutes,
 * with view starting at viewStartMinutes and scale 1.5px/min.
 */
export const PX_PER_MINUTE = 1.5

export function blockTop(startTime: string, viewStartMinutes = 7 * 60): number {
  return (timeToMinutes(startTime) - viewStartMinutes) * PX_PER_MINUTE
}

export function blockHeight(durationMinutes: number): number {
  return durationMinutes * PX_PER_MINUTE
}

/**
 * Snap minutes to nearest grid interval.
 */
export function snapToGrid(minutes: number, grid = 15): number {
  return Math.round(minutes / grid) * grid
}
