import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { timeBlocksApi } from "@/lib/api/timeBlocks"
import type { TimeBlock, TimeBlockCreateInput, BlockStatus } from "@/types"

export function useTodayBlocks(date: string) {
  return useQuery({
    queryKey: ["time-blocks", date],
    queryFn: () => timeBlocksApi.listByDate(date),
    staleTime: 30_000,
  })
}

export function useCreateBlock() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: TimeBlockCreateInput) => timeBlocksApi.create(data),
    onSuccess: (block) => {
      qc.invalidateQueries({ queryKey: ["time-blocks", block.date] })
    },
  })
}

export function useUpdateBlock(date: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TimeBlockCreateInput> }) =>
      timeBlocksApi.update(id, data),
    onMutate: async ({ id, data }) => {
      await qc.cancelQueries({ queryKey: ["time-blocks", date] })
      const previous = qc.getQueryData<TimeBlock[]>(["time-blocks", date])
      qc.setQueryData<TimeBlock[]>(["time-blocks", date], (old) =>
        old?.map((b) => (b.id === id ? { ...b, ...data } : b)) ?? []
      )
      return { previous }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.previous) {
        qc.setQueryData(["time-blocks", date], ctx.previous)
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["time-blocks", date] })
    },
  })
}

export function useUpdateBlockStatus(date: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: BlockStatus }) =>
      timeBlocksApi.updateStatus(id, status),
    onMutate: async ({ id, status }) => {
      await qc.cancelQueries({ queryKey: ["time-blocks", date] })
      const previous = qc.getQueryData<TimeBlock[]>(["time-blocks", date])
      qc.setQueryData<TimeBlock[]>(["time-blocks", date], (old) =>
        old?.map((b) => (b.id === id ? { ...b, status } : b)) ?? []
      )
      return { previous }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.previous) qc.setQueryData(["time-blocks", date], ctx.previous)
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["time-blocks", date] }),
  })
}

export function useDeleteBlock(date: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => timeBlocksApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["time-blocks", date] }),
  })
}
