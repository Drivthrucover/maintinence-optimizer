"""Criticality thresholds for maintenance actions."""

from __future__ import annotations

CRITICALITY_THRESHOLDS = {
    "high": {
        "inspect": 0.95,
        "maintain": 0.90,
        "replace": 0.80,
    },
    "medium": {
        "inspect": 0.90,
        "maintain": 0.85,
        "replace": 0.70,
    },
    "low": {
        "inspect": 0.85,
        "maintain": 0.75,
        "replace": 0.60,
    },
}


def get_thresholds(criticality: str) -> dict[str, float]:
    normalized = criticality.strip().lower()
    if normalized not in CRITICALITY_THRESHOLDS:
        valid = ", ".join(sorted(CRITICALITY_THRESHOLDS))
        raise ValueError(f"Unsupported criticality '{criticality}'. Expected one of: {valid}")
    return CRITICALITY_THRESHOLDS[normalized]
