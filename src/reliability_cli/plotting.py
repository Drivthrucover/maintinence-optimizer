"""Plot helpers for reliability analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def save_component_plot(
    output_path: str | Path,
    component_name: str,
    times: list[float],
    series: dict[str, list[float]],
    thresholds: dict[str, float],
    crossings: dict[str, float | None],
) -> None:
    figure, axis = plt.subplots(figsize=(10, 6))
    for label, reliabilities in series.items():
        axis.plot(times, reliabilities, label=label)

    for action, threshold in thresholds.items():
        axis.axhline(y=threshold, linestyle="--", linewidth=1, label=f"{action} threshold")

    for action, crossing_time in crossings.items():
        if crossing_time is not None:
            axis.axvline(x=crossing_time, linestyle=":", linewidth=1.2, label=f"{action} @ {crossing_time:.1f}")

    axis.set_title(f"Reliability Curves: {component_name}")
    axis.set_xlabel("Time")
    axis.set_ylabel("Reliability")
    axis.set_ylim(0, 1.05)
    axis.grid(True, alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)


def save_comparison_plot(
    output_path: str | Path,
    times: list[float],
    series: dict[str, list[float]],
    model_name: str,
) -> None:
    figure, axis = plt.subplots(figsize=(10, 6))
    for component_name, reliabilities in series.items():
        axis.plot(times, reliabilities, label=component_name)

    axis.set_title(f"Component Comparison ({model_name})")
    axis.set_xlabel("Time")
    axis.set_ylabel("Reliability")
    axis.set_ylim(0, 1.05)
    axis.grid(True, alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path)
    plt.close(figure)
