"use client"

import { useState } from "react"
import { format } from "date-fns"
import { useForm, Controller } from "react-hook-form"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { EnergyRating } from "@/components/review/EnergyRating"
import { StatusDot } from "@/components/shared/StatusDot"
import { CategoryBadge } from "@/components/shared/CategoryBadge"
import { TimePill } from "@/components/shared/TimePill"
import { useTodayBlocks } from "@/lib/hooks/useTodayBlocks"
import { reviewsApi } from "@/lib/api/reviews"
import { scheduleApi } from "@/lib/api/schedule"
import { toApiDate } from "@/lib/utils/dateRange"
import type { DailyReviewCreateInput } from "@/types"

export default function ReviewPage() {
  const today = toApiDate(new Date())
  const qc = useQueryClient()

  const { data: blocks = [] } = useTodayBlocks(today)

  const { data: existingReview } = useQuery({
    queryKey: ["review", today],
    queryFn: () => reviewsApi.getByDate(today).catch(() => null),
  })

  const { control, register, handleSubmit, watch } = useForm<DailyReviewCreateInput>({
    defaultValues: {
      date: today,
      energy_rating: existingReview?.energy_rating ?? 3,
      sleep_hours: existingReview?.sleep_hours ?? 7,
      gym_done: existingReview?.gym_done ?? false,
      notes: existingReview?.notes ?? "",
    },
  })

  const submitMutation = useMutation({
    mutationFn: async (data: DailyReviewCreateInput) => {
      if (existingReview) {
        return reviewsApi.update(existingReview.id, data)
      }
      return reviewsApi.create(data)
    },
    onSuccess: async () => {
      qc.invalidateQueries({ queryKey: ["review", today] })
      // Trigger tomorrow's schedule generation
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      await scheduleApi.generate(toApiDate(tomorrow), true).catch(() => null)
      qc.invalidateQueries({ queryKey: ["time-blocks"] })
    },
  })

  const doneBlocks = blocks.filter((b) => b.status === "done")
  const missedBlocks = blocks.filter((b) => b.status === "missed")

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h1 className="text-xl font-bold">Daily Review</h1>
        <p className="text-sm text-muted-foreground">{format(new Date(), "EEEE, MMMM d, yyyy")}</p>
      </div>

      <form onSubmit={handleSubmit((d) => submitMutation.mutate(d))} className="flex flex-col gap-6">
        {/* Energy rating */}
        <div className="rounded-lg border bg-card p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">Energy Level</h2>
          <Controller
            control={control}
            name="energy_rating"
            render={({ field }) => (
              <EnergyRating value={field.value} onChange={field.onChange} />
            )}
          />
        </div>

        {/* Sleep & Gym */}
        <div className="rounded-lg border bg-card p-4 grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Sleep Hours</label>
            <input
              type="number"
              step="0.5"
              min="0"
              max="24"
              {...register("sleep_hours", { valueAsNumber: true })}
              className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col justify-end">
            <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
              <input type="checkbox" {...register("gym_done")} className="rounded" />
              Gym done today
            </label>
          </div>
        </div>

        {/* Block review */}
        <div className="rounded-lg border bg-card p-4 flex flex-col gap-3">
          <h2 className="font-semibold text-sm">
            Block Summary ({doneBlocks.length} done, {missedBlocks.length} missed)
          </h2>
          {blocks.length === 0 ? (
            <p className="text-sm text-muted-foreground">No blocks for today.</p>
          ) : (
            <div className="flex flex-col gap-2">
              {blocks.map((block) => (
                <div key={block.id} className="flex items-center gap-2 text-sm">
                  <StatusDot status={block.status} />
                  <CategoryBadge category={block.category} size="sm" />
                  <span className="flex-1 truncate text-muted-foreground">
                    {block.title ?? block.category.name}
                  </span>
                  <TimePill minutes={block.planned_duration} variant="muted" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Notes */}
        <div className="rounded-lg border bg-card p-4 flex flex-col gap-2">
          <label className="text-sm font-semibold">Notes</label>
          <textarea
            {...register("notes")}
            rows={3}
            placeholder="What went well? What to improve tomorrow?"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={submitMutation.isPending}
          className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-medium hover:opacity-90 disabled:opacity-50"
        >
          {submitMutation.isPending
            ? "Saving…"
            : existingReview
            ? "Update Review & Regenerate Tomorrow"
            : "Submit Review & Generate Tomorrow's Schedule"}
        </button>

        {submitMutation.isSuccess && (
          <p className="text-center text-sm text-green-600">
            Review saved! Tomorrow's schedule has been generated.
          </p>
        )}
      </form>
    </div>
  )
}
