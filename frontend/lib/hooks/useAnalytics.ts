import { useQuery } from "@tanstack/react-query"
import { analyticsApi } from "@/lib/api/analytics"
import { toApiDate } from "@/lib/utils/dateRange"
import { subDays } from "date-fns"

export function useDailyTotals(days = 14) {
  const end = toApiDate(new Date())
  const start = toApiDate(subDays(new Date(), days - 1))
  return useQuery({
    queryKey: ["daily-totals", start, end],
    queryFn: () => analyticsApi.dailyTotals(start, end),
    staleTime: 60_000,
  })
}

export function useBestHours(days = 30) {
  return useQuery({
    queryKey: ["best-hours", days],
    queryFn: () => analyticsApi.bestHours(days),
    staleTime: 120_000,
  })
}

export function useDeepWorkTrend(days = 14) {
  return useQuery({
    queryKey: ["deep-work-trend", days],
    queryFn: () => analyticsApi.deepWorkTrend(days),
    staleTime: 120_000,
  })
}
