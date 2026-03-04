import { apiClient } from "./client"
import type { TimeBlock, TimeBlockCreateInput, BlockStatus } from "@/types"

export const timeBlocksApi = {
  listByDate: (date: string) =>
    apiClient.get<TimeBlock[]>("/time-blocks/", { params: { date } }).then((r) => r.data),

  listRange: (start: string, end: string) =>
    apiClient.get<TimeBlock[]>("/time-blocks/range", { params: { start, end } }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<TimeBlock>(`/time-blocks/${id}`).then((r) => r.data),

  create: (data: TimeBlockCreateInput) =>
    apiClient.post<TimeBlock>("/time-blocks/", data).then((r) => r.data),

  update: (id: string, data: Partial<TimeBlockCreateInput>) =>
    apiClient.put<TimeBlock>(`/time-blocks/${id}`, data).then((r) => r.data),

  updateStatus: (id: string, status: BlockStatus) =>
    apiClient.patch<TimeBlock>(`/time-blocks/${id}/status`, { status }).then((r) => r.data),

  delete: (id: string) =>
    apiClient.delete(`/time-blocks/${id}`),
}
