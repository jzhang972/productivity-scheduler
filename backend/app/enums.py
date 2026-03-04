"""Standalone enums with no DB dependencies — safe to import anywhere."""
import enum


class BlockStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    done = "done"
    missed = "missed"
