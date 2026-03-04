import { format, startOfWeek, endOfWeek, addWeeks, subWeeks } from "date-fns"

export function toApiDate(date: Date): string {
  return format(date, "yyyy-MM-dd")
}

export function getWeekBounds(date: Date): { start: string; end: string } {
  const start = startOfWeek(date, { weekStartsOn: 1 })  // Monday
  const end = endOfWeek(date, { weekStartsOn: 1 })       // Sunday
  return { start: toApiDate(start), end: toApiDate(end) }
}

export function nextWeek(weekStart: Date): Date {
  return addWeeks(weekStart, 1)
}

export function prevWeek(weekStart: Date): Date {
  return subWeeks(weekStart, 1)
}

export function currentWeekStart(): string {
  return toApiDate(startOfWeek(new Date(), { weekStartsOn: 1 }))
}
