// ─── Core Domain Types ───────────────────────────────────────────────────────

export type BlockStatus = "planned" | "in_progress" | "done" | "missed"

export interface Category {
  id: string
  name: string
  color_hex: string
  priority_weight: number
  weekly_target_minutes: number
  daily_cap_minutes: number | null
  is_deep_work: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TimeBlock {
  id: string
  category_id: string
  category: Category
  date: string         // "YYYY-MM-DD"
  start_time: string   // "HH:MM:SS"
  end_time: string     // "HH:MM:SS"
  planned_duration: number
  status: BlockStatus
  title: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface TimeLog {
  id: string
  time_block_id: string
  actual_start: string
  actual_end: string | null
  actual_duration: number | null
  interruptions: number
  notes: string | null
  created_at: string
}

export interface DailyReview {
  id: string
  date: string
  energy_rating: number
  sleep_hours: number
  gym_done: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

// ─── Analytics Types ─────────────────────────────────────────────────────────

export interface CategoryDailyTotal {
  category_id: string
  category_name: string
  color_hex: string
  total_minutes: number
}

export interface DailyTotals {
  date: string
  totals: CategoryDailyTotal[]
  total_minutes: number
}

export interface CategoryWeeklyProgress {
  category_id: string
  category_name: string
  color_hex: string
  weekly_target_minutes: number
  actual_minutes: number
  planned_minutes: number
  deficit_minutes: number
  completion_pct: number
}

export interface WeeklyProgress {
  week_start: string
  week_end: string
  categories: CategoryWeeklyProgress[]
  total_actual_minutes: number
  total_planned_minutes: number
}

export interface HourBucket {
  hour: number
  avg_minutes: number
  sample_count: number
}

export interface BestHours {
  hours: HourBucket[]
}

export interface DeepWorkDay {
  date: string
  deep_work_minutes: number
  total_minutes: number
}

export interface DeepWorkTrend {
  days: DeepWorkDay[]
  avg_deep_work_minutes: number
  max_deep_work_minutes: number
}

// ─── Schedule Types ───────────────────────────────────────────────────────────

export interface ScheduledBlock {
  category_id: string
  category_name: string
  color_hex: string
  date: string
  start_time: string
  end_time: string
  planned_duration: number
  title: string | null
  is_deep_work: boolean
  urgency_score: number
}

export interface ScheduleWarning {
  code: string
  message: string
}

export interface SchedulePreview {
  target_date: string
  blocks: ScheduledBlock[]
  total_planned_minutes: number
  warnings: ScheduleWarning[]
  generated_at: string
}

// ─── Form Types ───────────────────────────────────────────────────────────────

export interface CategoryCreateInput {
  name: string
  color_hex: string
  priority_weight: number
  weekly_target_minutes: number
  daily_cap_minutes: number | null
  is_deep_work: boolean
  is_active: boolean
}

export interface TimeBlockCreateInput {
  category_id: string
  date: string
  start_time: string
  end_time: string
  planned_duration: number
  title: string | null
  notes: string | null
}

export interface DailyReviewCreateInput {
  date: string
  energy_rating: number
  sleep_hours: number
  gym_done: boolean
  notes: string | null
}
