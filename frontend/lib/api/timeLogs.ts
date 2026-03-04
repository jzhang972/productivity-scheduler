import { apiClient } from "./client"
import type { TimeLog } from "@/types"

export const timeLogsApi = {
  start: (timeBlockId: string, notes?: string) =>
    apiClient
      .post<TimeLog>("/time-logs/start", { time_block_id: timeBlockId, notes })
      .then((r) => r.data),

  stop: (logId: string, interruptions = 0, notes?: string) =>
    apiClient
      .post<TimeLog>(`/time-logs/${logId}/stop`, { interruptions, notes })
      .then((r) => r.data),

  pause: (logId: string) =>
    apiClient.post<TimeLog>(`/time-logs/${logId}/pause`).then((r) => r.data),

  listByBlock: (blockId: string) =>
    apiClient.get<TimeLog[]>("/time-logs/", { params: { block_id: blockId } }).then((r) => r.data),

  update: (logId: string, data: Partial<TimeLog>) =>
    apiClient.put<TimeLog>(`/time-logs/${logId}`, data).then((r) => r.data),
}
