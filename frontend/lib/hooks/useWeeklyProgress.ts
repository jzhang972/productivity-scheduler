import { useQuery } from "@tanstack/react-query"
import { analyticsApi } from "@/lib/api/analytics"
import { currentWeekStart } from "@/lib/utils/dateRange"

export function useWeeklyProgress(weekStart?: string) {
  const ws = weekStart ?? currentWeekStart()
  return useQuery({
    queryKey: ["weekly-progress", ws],
    queryFn: () => analyticsApi.weeklyProgress(ws),
    staleTime: 60_000,
  })
}
