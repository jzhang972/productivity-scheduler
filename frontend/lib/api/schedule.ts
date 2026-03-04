import { apiClient } from "./client"
import type { SchedulePreview } from "@/types"

export const scheduleApi = {
  generate: (targetDate: string, forceRegenerate = false) =>
    apiClient
      .post<SchedulePreview>("/schedule/generate", {
        target_date: targetDate,
        force_regenerate: forceRegenerate,
      })
      .then((r) => r.data),

  preview: (date: string) =>
    apiClient
      .get<SchedulePreview>("/schedule/preview", { params: { date } })
      .then((r) => r.data),
}
