"""
Core scheduling optimization engine.

Algorithm: Constraint-satisfying greedy with priority-weighted deficit scoring.
Stages:
  1. Deficit Scoring — how far behind each category is for the week
  2. Slot Allocation — minutes to assign each category today
  3. Block Generation — concrete time blocks respecting constraints
  4. Sequencing — deep-work first, minimize context switching
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from app.config import get_settings
from app.schemas.schedule_types import ScheduledBlock, ScheduleWarning

settings = get_settings()

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
WORK_START = settings.work_start_hour * 60          # minutes from midnight
WORK_END = WORK_START + settings.work_minutes_per_day  # 540 min later
DEEP_WORK_START = settings.deep_work_window_start * 60
DEEP_WORK_END = settings.deep_work_window_end * 60
GYM_START = settings.gym_start_hour * 60
GYM_END = settings.gym_end_hour * 60
MIN_BLOCK = settings.min_block_minutes
BUFFER = settings.buffer_minutes
WORK_CEILING = settings.work_minutes_per_day
MISSED_URGENCY_BOOST = 1.3
LOW_ENERGY_THRESHOLD_HOUR = 14  # categories scheduled post-14:00


# ------------------------------------------------------------------
# Data classes
# ------------------------------------------------------------------
@dataclass
class CategoryInput:
    id: str
    name: str
    color_hex: str
    priority_weight: int
    weekly_target_minutes: int
    daily_cap_minutes: int | None
    is_deep_work: bool
    actual_this_week: int = 0
    missed_yesterday: bool = False
    is_low_energy: bool = False   # e.g. Teaching, Interview Prep


@dataclass
class ScoredCategory:
    category: CategoryInput
    allocation_minutes: int
    urgency_score: float
    is_deep_work: bool


@dataclass
class TimeSlot:
    start_min: int  # minutes from midnight
    end_min: int

    @property
    def duration(self) -> int:
        return self.end_min - self.start_min

    def split_at(self, at_min: int) -> tuple["TimeSlot | None", "TimeSlot | None"]:
        """Split slot at a given minute offset; returns (before, after)."""
        if at_min <= self.start_min:
            return None, TimeSlot(self.start_min, self.end_min)
        if at_min >= self.end_min:
            return TimeSlot(self.start_min, self.end_min), None
        return TimeSlot(self.start_min, at_min), TimeSlot(at_min, self.end_min)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _minutes_to_time(minutes: int) -> time:
    h, m = divmod(minutes, 60)
    return time(h % 24, m)


def _compute_free_slots(blocked: list[tuple[int, int]]) -> list[TimeSlot]:
    """Compute free slots within the work window, carving out blocked periods."""
    slots: list[TimeSlot] = [TimeSlot(WORK_START, WORK_END)]
    for b_start, b_end in sorted(blocked):
        new_slots: list[TimeSlot] = []
        for slot in slots:
            before, after = slot.split_at(b_start)
            if before and before.duration >= MIN_BLOCK:
                _, remainder = before.split_at(b_end)
                new_slots.append(before)
            elif after:
                _, remainder = TimeSlot(b_start, slot.end_min).split_at(b_end)
                if remainder and remainder.duration > 0:
                    new_slots.append(remainder)
                continue
            if after:
                _, remainder = after.split_at(b_end - after.start_min + after.start_min)
                # re-split properly
                if after.start_min < b_end:
                    trimmed = TimeSlot(max(after.start_min, b_end), after.end_min)
                    if trimmed.duration > 0:
                        new_slots.append(trimmed)
                else:
                    new_slots.append(after)
        slots = new_slots

    # Rebuild cleanly: carve blocked intervals from [WORK_START, WORK_END]
    all_blocked = sorted(blocked)
    free: list[TimeSlot] = []
    cursor = WORK_START
    for bs, be in all_blocked:
        if cursor < bs:
            free.append(TimeSlot(cursor, bs))
        cursor = max(cursor, be)
    if cursor < WORK_END:
        free.append(TimeSlot(cursor, WORK_END))
    return [s for s in free if s.duration >= MIN_BLOCK]


def _score_categories(
    categories: list[CategoryInput],
    days_remaining: int,
) -> list[ScoredCategory]:
    """Stage 1+2: Score and allocate minutes per category."""
    scored: list[ScoredCategory] = []
    days_remaining = max(days_remaining, 1)

    for cat in categories:
        if cat.weekly_target_minutes == 0:
            continue

        remaining = max(0, cat.weekly_target_minutes - cat.actual_this_week)
        if remaining == 0:
            continue

        fair_share = remaining / days_remaining
        urgency = (remaining / cat.weekly_target_minutes) * cat.priority_weight

        if cat.missed_yesterday:
            urgency *= MISSED_URGENCY_BOOST

        cap = cat.daily_cap_minutes if cat.daily_cap_minutes else math.inf
        allocation = min(fair_share, cap)
        allocation = max(allocation, MIN_BLOCK)  # at least one block worth

        scored.append(ScoredCategory(
            category=cat,
            allocation_minutes=int(allocation),
            urgency_score=round(urgency, 4),
            is_deep_work=cat.is_deep_work,
        ))

    # Sort: deep-work first, then by urgency descending
    scored.sort(key=lambda x: (-int(x.is_deep_work), -x.urgency_score))
    return scored


def _fill_slot(
    slot: TimeSlot,
    duration_needed: int,
    is_deep_work: bool,
    is_low_energy: bool,
) -> tuple[int, int] | None:
    """
    Find start/end in minutes for a block of `duration_needed` within `slot`.
    Respects deep-work window and low-energy constraints.
    Returns (start_min, end_min) or None if doesn't fit.
    """
    available = slot.duration - BUFFER
    if available < MIN_BLOCK:
        return None

    duration = min(duration_needed, available)
    start = slot.start_min

    # Deep-work must stay within DEEP_WORK_START..DEEP_WORK_END
    if is_deep_work:
        dw_start = max(start, DEEP_WORK_START)
        dw_end = DEEP_WORK_END
        if dw_start >= dw_end:
            return None
        duration = min(duration, dw_end - dw_start)
        if duration < MIN_BLOCK:
            return None
        start = dw_start

    # Low-energy: prefer after LOW_ENERGY_THRESHOLD_HOUR
    if is_low_energy:
        low_start = max(start, LOW_ENERGY_THRESHOLD_HOUR * 60)
        if low_start + MIN_BLOCK <= slot.end_min - BUFFER:
            start = low_start

    end = start + duration
    if end + BUFFER > slot.end_min:
        end = slot.end_min - BUFFER
        duration = end - start

    if duration < MIN_BLOCK:
        return None

    return start, end


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def generate_schedule(
    target_date: date,
    categories: list[CategoryInput],
    days_remaining_in_week: int = 1,
    include_gym: bool = True,
) -> tuple[list[ScheduledBlock], list[ScheduleWarning]]:
    """
    Generate a list of ScheduledBlock objects for target_date.

    Returns (blocks, warnings).
    """
    warnings: list[ScheduleWarning] = []
    scored = _score_categories(categories, days_remaining_in_week)

    if not scored:
        warnings.append(ScheduleWarning(
            code="NO_CATEGORIES",
            message="No active categories with remaining weekly targets found.",
        ))
        return [], warnings

    # Blocked intervals: gym slot
    blocked: list[tuple[int, int]] = []
    if include_gym:
        blocked.append((GYM_START, GYM_END))

    free_slots = _compute_free_slots(blocked)

    blocks: list[ScheduledBlock] = []
    total_assigned = 0

    # Keep a mutable copy of free slots (list of [start, end] so we can shrink)
    slot_queue = [[s.start_min, s.end_min] for s in free_slots]

    for item in scored:
        if total_assigned >= WORK_CEILING:
            warnings.append(ScheduleWarning(
                code="WORK_CEILING_REACHED",
                message=f"Work ceiling of {WORK_CEILING} min reached. "
                        f"{item.category.name} not scheduled.",
            ))
            break

        remaining_allocation = min(
            item.allocation_minutes,
            WORK_CEILING - total_assigned,
        )

        while remaining_allocation >= MIN_BLOCK:
            placed = False
            for slot in slot_queue:
                slot_obj = TimeSlot(slot[0], slot[1])
                result = _fill_slot(
                    slot_obj,
                    remaining_allocation,
                    item.is_deep_work,
                    item.category.is_low_energy,
                )
                if result is None:
                    continue

                start_min, end_min = result
                duration = end_min - start_min

                blocks.append(ScheduledBlock(
                    category_id=item.category.id,  # type: ignore[arg-type]
                    category_name=item.category.name,
                    color_hex=item.category.color_hex,
                    date=target_date,
                    start_time=_minutes_to_time(start_min),
                    end_time=_minutes_to_time(end_min),
                    planned_duration=duration,
                    title=item.category.name,
                    is_deep_work=item.is_deep_work,
                    urgency_score=item.urgency_score,
                ))

                total_assigned += duration
                remaining_allocation -= duration

                # Shrink the slot: consume from start_min to end_min + buffer
                consumed_end = min(end_min + BUFFER, slot[1])
                slot[0] = consumed_end
                placed = True
                break

            if not placed:
                # No slot can fit this category anymore
                if remaining_allocation >= MIN_BLOCK:
                    warnings.append(ScheduleWarning(
                        code="INSUFFICIENT_SLOTS",
                        message=f"Could not schedule {remaining_allocation} min "
                                f"for {item.category.name} — no fitting slot found.",
                    ))
                break

        # Remove exhausted slots
        slot_queue = [s for s in slot_queue if s[1] - s[0] >= MIN_BLOCK]

    # Sort final blocks by start_time
    blocks.sort(key=lambda b: b.start_time)

    # Validate total
    if total_assigned > WORK_CEILING:
        warnings.append(ScheduleWarning(
            code="OVER_CEILING",
            message=f"Total scheduled {total_assigned} min exceeds ceiling {WORK_CEILING} min.",
        ))

    return blocks, warnings
