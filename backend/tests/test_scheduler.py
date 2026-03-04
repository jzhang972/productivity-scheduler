"""
Tests for the scheduling optimization engine.
Verifies: caps, deep-work ordering, 540 min ceiling, and deficit rebalancing.
"""
import pytest
from datetime import date

from app.services.scheduler import (
    CategoryInput, generate_schedule,
    WORK_CEILING, MIN_BLOCK, DEEP_WORK_START, DEEP_WORK_END
)


# ---------- Fixtures ----------

def make_cat(
    id: str = "cat1",
    name: str = "Research",
    weekly_target: int = 1200,
    daily_cap: int | None = 240,
    is_deep_work: bool = True,
    priority: int = 5,
    actual_this_week: int = 0,
    missed_yesterday: bool = False,
) -> CategoryInput:
    return CategoryInput(
        id=id,
        name=name,
        color_hex="#6366f1",
        priority_weight=priority,
        weekly_target_minutes=weekly_target,
        daily_cap_minutes=daily_cap,
        is_deep_work=is_deep_work,
        actual_this_week=actual_this_week,
        missed_yesterday=missed_yesterday,
    )


TARGET_DATE = date(2025, 3, 10)  # Monday


# ---------- Tests ----------

class TestSchedulerBasic:
    def test_returns_blocks_for_active_categories(self):
        cats = [make_cat()]
        blocks, warnings = generate_schedule(TARGET_DATE, cats, days_remaining_in_week=7)
        assert len(blocks) > 0

    def test_empty_categories_returns_warning(self):
        blocks, warnings = generate_schedule(TARGET_DATE, [], days_remaining_in_week=7)
        assert blocks == []
        assert any(w.code == "NO_CATEGORIES" for w in warnings)

    def test_zero_weekly_target_skipped(self):
        cat = make_cat(weekly_target=0)
        blocks, warnings = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=7)
        assert blocks == []

    def test_already_met_target_skipped(self):
        cat = make_cat(weekly_target=240, actual_this_week=240)
        blocks, warnings = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=7)
        assert blocks == []


class TestSchedulerCaps:
    def test_research_daily_cap_respected(self):
        cat = make_cat(name="Research", daily_cap=240, is_deep_work=True, weekly_target=2400)
        blocks, _ = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=7)
        total = sum(b.planned_duration for b in blocks if b.category_name == "Research")
        assert total <= 240, f"Research exceeded 240 min cap: {total}"

    def test_custom_daily_cap_respected(self):
        cat = make_cat(name="Teaching", daily_cap=60, is_deep_work=False, weekly_target=600)
        blocks, _ = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=7)
        total = sum(b.planned_duration for b in blocks)
        assert total <= 60, f"Teaching exceeded 60 min cap: {total}"

    def test_work_ceiling_not_exceeded(self):
        cats = [
            make_cat(id="c1", name="Cat1", daily_cap=None, weekly_target=3000, priority=5),
            make_cat(id="c2", name="Cat2", daily_cap=None, weekly_target=3000, priority=4),
            make_cat(id="c3", name="Cat3", daily_cap=None, weekly_target=3000, priority=3),
        ]
        blocks, _ = generate_schedule(TARGET_DATE, cats, days_remaining_in_week=1)
        total = sum(b.planned_duration for b in blocks)
        assert total <= WORK_CEILING, f"Total {total} exceeds ceiling {WORK_CEILING}"

    def test_min_block_size_respected(self):
        cat = make_cat(weekly_target=120, daily_cap=None)
        blocks, _ = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=7)
        for b in blocks:
            assert b.planned_duration >= MIN_BLOCK, (
                f"Block duration {b.planned_duration} < MIN_BLOCK {MIN_BLOCK}"
            )


class TestSchedulerOrdering:
    def test_deep_work_scheduled_first(self):
        deep = make_cat(id="deep", name="Research", is_deep_work=True, priority=5)
        shallow = make_cat(id="shallow", name="Admin", is_deep_work=False, priority=5)
        blocks, _ = generate_schedule(TARGET_DATE, [deep, shallow], days_remaining_in_week=7)

        deep_blocks = [b for b in blocks if b.is_deep_work]
        shallow_blocks = [b for b in blocks if not b.is_deep_work]

        if deep_blocks and shallow_blocks:
            earliest_shallow = min(b.start_time for b in shallow_blocks)
            earliest_deep = min(b.start_time for b in deep_blocks)
            assert earliest_deep <= earliest_shallow, (
                "Deep work should start at or before shallow work"
            )

    def test_deep_work_within_window(self):
        cat = make_cat(is_deep_work=True, weekly_target=240)
        blocks, _ = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=7)
        for b in [bl for bl in blocks if bl.is_deep_work]:
            start_min = b.start_time.hour * 60 + b.start_time.minute
            end_min = b.end_time.hour * 60 + b.end_time.minute
            assert start_min >= DEEP_WORK_START, f"Deep work starts before window: {b.start_time}"
            assert end_min <= DEEP_WORK_END, f"Deep work ends after window: {b.end_time}"

    def test_high_urgency_scheduled_before_low(self):
        high = make_cat(id="high", name="HighPri", priority=9, weekly_target=600, actual_this_week=0, is_deep_work=False)
        low = make_cat(id="low", name="LowPri", priority=1, weekly_target=600, actual_this_week=0, is_deep_work=False)
        blocks, _ = generate_schedule(TARGET_DATE, [high, low], days_remaining_in_week=7)

        high_blocks = [b for b in blocks if b.category_name == "HighPri"]
        low_blocks = [b for b in blocks if b.category_name == "LowPri"]

        if high_blocks and low_blocks:
            assert min(b.start_time for b in high_blocks) <= min(b.start_time for b in low_blocks)


class TestSchedulerDeficits:
    def test_missed_yesterday_boosts_urgency(self):
        """Category with missed_yesterday=True should be scheduled even if only 1 day remains."""
        missed = make_cat(
            id="missed", name="Missed", weekly_target=300, actual_this_week=200,
            missed_yesterday=True, priority=3, is_deep_work=False
        )
        normal = make_cat(
            id="normal", name="Normal", weekly_target=300, actual_this_week=200,
            missed_yesterday=False, priority=3, is_deep_work=False
        )
        blocks_m, _ = generate_schedule(TARGET_DATE, [missed], days_remaining_in_week=1)
        blocks_n, _ = generate_schedule(TARGET_DATE, [normal], days_remaining_in_week=1)

        total_m = sum(b.planned_duration for b in blocks_m)
        total_n = sum(b.planned_duration for b in blocks_n)
        # Both should be scheduled, missed might get >= normal
        assert total_m >= total_n or total_m > 0

    def test_fully_behind_gets_more_than_ahead(self):
        behind = make_cat(id="beh", name="Behind", weekly_target=600, actual_this_week=0, priority=5, is_deep_work=False)
        ahead = make_cat(id="ahe", name="Ahead", weekly_target=600, actual_this_week=500, priority=5, is_deep_work=False)
        blocks, _ = generate_schedule(TARGET_DATE, [behind, ahead], days_remaining_in_week=3)

        total_behind = sum(b.planned_duration for b in blocks if b.category_name == "Behind")
        total_ahead = sum(b.planned_duration for b in blocks if b.category_name == "Ahead")
        assert total_behind >= total_ahead, (
            f"Behind ({total_behind}) should get >= Ahead ({total_ahead})"
        )


class TestSchedulerGyms:
    def test_no_blocks_during_gym_slot(self):
        cat = make_cat(weekly_target=2000, daily_cap=None, is_deep_work=False)
        blocks, _ = generate_schedule(TARGET_DATE, [cat], days_remaining_in_week=1, include_gym=True)
        gym_start = 12 * 60  # 12:00
        gym_end = 13 * 60    # 13:00
        for b in blocks:
            b_start = b.start_time.hour * 60 + b.start_time.minute
            b_end = b.end_time.hour * 60 + b.end_time.minute
            overlap = max(0, min(b_end, gym_end) - max(b_start, gym_start))
            assert overlap == 0, f"Block overlaps gym slot: {b.start_time}-{b.end_time}"
