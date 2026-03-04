import { apiClient } from "./client"
import type { DailyTotals, WeeklyProgress, BestHours, DeepWorkTrend } from "@/types"

export const analyticsApi = {
  dailyTotals: (start: string, end: string) =>
    apiClient
      .get<DailyTotals[]>("/analytics/daily-totals", { params: { start, end } })
      .then((r) => r.data),

  weeklyProgress: (weekStart: string) =>
    apiClient
      .get<WeeklyProgress>("/analytics/weekly-progress", { params: { week_start: weekStart } })
      .then((r) => r.data),

  bestHours: (days = 30) =>
    apiClient
      .get<BestHours>("/analytics/best-hours", { params: { days } })
      .then((r) => r.data),

  deepWorkTrend: (days = 14) =>
    apiClient
      .get<DeepWorkTrend>("/analytics/deep-work-trend", { params: { days } })
      .then((r) => r.data),
}
