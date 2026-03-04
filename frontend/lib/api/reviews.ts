import { apiClient } from "./client"
import type { DailyReview, DailyReviewCreateInput } from "@/types"

export const reviewsApi = {
  list: (limit = 30) =>
    apiClient.get<DailyReview[]>("/reviews/", { params: { limit } }).then((r) => r.data),

  getByDate: (date: string) =>
    apiClient.get<DailyReview>("/reviews/by-date", { params: { date } }).then((r) => r.data),

  create: (data: DailyReviewCreateInput) =>
    apiClient.post<DailyReview>("/reviews/", data).then((r) => r.data),

  update: (id: string, data: Partial<DailyReviewCreateInput>) =>
    apiClient.put<DailyReview>(`/reviews/${id}`, data).then((r) => r.data),
}
