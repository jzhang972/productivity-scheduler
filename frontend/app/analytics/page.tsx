"use client"

import { useState } from "react"
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell,
} from "recharts"
import { useDailyTotals, useBestHours, useDeepWorkTrend } from "@/lib/hooks/useAnalytics"
import { useWeeklyProgress } from "@/lib/hooks/useWeeklyProgress"
import { formatMinutes } from "@/lib/utils/time"
import { currentWeekStart } from "@/lib/utils/dateRange"

const PERIODS = [7, 14, 30] as const
type Period = (typeof PERIODS)[number]

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<Period>(14)

  const { data: dailyTotals } = useDailyTotals(period)
  const { data: bestHours } = useBestHours(30)
  const { data: deepWork } = useDeepWorkTrend(period)
  const { data: weekly } = useWeeklyProgress(currentWeekStart())

  // Flatten daily totals for stacked bar chart
  const dailyChartData = dailyTotals?.map((d) => ({
    date: d.date.slice(5),  // "MM-DD"
    total: d.total_minutes,
    ...Object.fromEntries(d.totals.map((t) => [t.category_name, t.total_minutes])),
  })) ?? []

  const deepWorkData = deepWork?.days.map((d) => ({
    date: d.date.slice(5),
    "Deep Work": d.deep_work_minutes,
    Other: d.total_minutes - d.deep_work_minutes,
  })) ?? []

  const hoursData = bestHours?.hours.map((h) => ({
    hour: `${String(h.hour).padStart(2, "0")}:00`,
    avg: h.avg_minutes,
  })) ?? []

  const categoryData = weekly?.categories
    .filter((c) => c.actual_minutes > 0)
    .map((c) => ({ name: c.category_name, value: c.actual_minutes, color: c.color_hex })) ?? []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Analytics</h1>
        <div className="flex gap-1 rounded-lg border p-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                period === p
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {p}d
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily productivity trend */}
        <div className="rounded-lg border bg-card p-4">
          <h2 className="font-semibold text-sm mb-4">Daily Totals (min)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={dailyChartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatMinutes(v)} />
              <Bar dataKey="total" fill="#6366f1" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Deep work trend */}
        <div className="rounded-lg border bg-card p-4">
          <h2 className="font-semibold text-sm mb-4">
            Deep Work vs Other
            {deepWork && (
              <span className="text-muted-foreground font-normal ml-2">
                avg {formatMinutes(Math.round(deepWork.avg_deep_work_minutes))}/day
              </span>
            )}
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={deepWorkData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatMinutes(v)} />
              <Legend />
              <Bar dataKey="Deep Work" stackId="a" fill="#6366f1" radius={[2, 2, 0, 0]} />
              <Bar dataKey="Other" stackId="a" fill="#94a3b8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Best hours heatmap */}
        <div className="rounded-lg border bg-card p-4">
          <h2 className="font-semibold text-sm mb-4">Best Hours (avg min logged)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={hoursData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis dataKey="hour" type="category" tick={{ fontSize: 10 }} width={45} />
              <Tooltip formatter={(v: number) => `${v.toFixed(0)} min`} />
              <Bar dataKey="avg" fill="#22c55e" radius={[0, 2, 2, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category split donut */}
        <div className="rounded-lg border bg-card p-4">
          <h2 className="font-semibold text-sm mb-4">This Week by Category</h2>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {categoryData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => formatMinutes(v)} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-muted-foreground">No data for this week yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}
