"use client"

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { useQuery } from "@tanstack/react-query"
import { categoriesApi } from "@/lib/api/categories"
import { useCreateBlock, useUpdateBlock } from "@/lib/hooks/useTodayBlocks"
import { useUIStore } from "@/lib/store/uiStore"
import { X } from "lucide-react"
import type { TimeBlock, TimeBlockCreateInput } from "@/types"

interface TimeBlockModalProps {
  date: string
  editingBlock?: TimeBlock | null
}

type FormValues = {
  category_id: string
  start_time: string
  end_time: string
  title: string
  notes: string
}

export function TimeBlockModal({ date, editingBlock }: TimeBlockModalProps) {
  const { isBlockModalOpen, closeBlockModal } = useUIStore()
  const createBlock = useCreateBlock()
  const updateBlock = useUpdateBlock(date)

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.list(true),
  })

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    defaultValues: {
      category_id: "",
      start_time: "09:00",
      end_time: "10:00",
      title: "",
      notes: "",
    },
  })

  useEffect(() => {
    if (editingBlock) {
      reset({
        category_id: editingBlock.category_id,
        start_time: editingBlock.start_time.slice(0, 5),
        end_time: editingBlock.end_time.slice(0, 5),
        title: editingBlock.title ?? "",
        notes: editingBlock.notes ?? "",
      })
    } else {
      reset({ category_id: "", start_time: "09:00", end_time: "10:00", title: "", notes: "" })
    }
  }, [editingBlock, reset])

  if (!isBlockModalOpen) return null

  async function onSubmit(values: FormValues) {
    const startParts = values.start_time.split(":")
    const endParts = values.end_time.split(":")
    const startMin = parseInt(startParts[0]) * 60 + parseInt(startParts[1])
    const endMin = parseInt(endParts[0]) * 60 + parseInt(endParts[1])
    const duration = endMin - startMin

    if (duration <= 0) return

    const data: TimeBlockCreateInput = {
      category_id: values.category_id,
      date,
      start_time: values.start_time + ":00",
      end_time: values.end_time + ":00",
      planned_duration: duration,
      title: values.title || null,
      notes: values.notes || null,
    }

    if (editingBlock) {
      await updateBlock.mutateAsync({ id: editingBlock.id, data })
    } else {
      await createBlock.mutateAsync(data)
    }
    closeBlockModal()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={closeBlockModal} />
      <div className="relative z-10 w-full max-w-md rounded-lg bg-card border shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            {editingBlock ? "Edit Block" : "New Block"}
          </h2>
          <button onClick={closeBlockModal} className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div>
            <label className="text-sm font-medium">Category</label>
            <select
              {...register("category_id", { required: true })}
              className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
            >
              <option value="">Select a category…</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
            {errors.category_id && (
              <p className="text-xs text-destructive mt-1">Category is required</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium">Start</label>
              <input
                type="time"
                {...register("start_time", { required: true })}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="text-sm font-medium">End</label>
              <input
                type="time"
                {...register("end_time", { required: true })}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">Title (optional)</label>
            <input
              type="text"
              {...register("title")}
              placeholder="What are you working on?"
              className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="text-sm font-medium">Notes (optional)</label>
            <textarea
              {...register("notes")}
              rows={2}
              className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm resize-none"
            />
          </div>

          <div className="flex justify-end gap-2 mt-2">
            <button
              type="button"
              onClick={closeBlockModal}
              className="px-4 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createBlock.isPending || updateBlock.isPending}
              className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-50"
            >
              {editingBlock ? "Save" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
