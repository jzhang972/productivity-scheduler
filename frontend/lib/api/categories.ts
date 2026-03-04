import { apiClient } from "./client"
import type { Category, CategoryCreateInput } from "@/types"

export const categoriesApi = {
  list: (activeOnly = false) =>
    apiClient.get<Category[]>("/categories/", { params: { active_only: activeOnly } }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Category>(`/categories/${id}`).then((r) => r.data),

  create: (data: CategoryCreateInput) =>
    apiClient.post<Category>("/categories/", data).then((r) => r.data),

  update: (id: string, data: Partial<CategoryCreateInput>) =>
    apiClient.put<Category>(`/categories/${id}`, data).then((r) => r.data),

  delete: (id: string) =>
    apiClient.delete(`/categories/${id}`),
}
