"""Reliability models and derived metrics."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class ReliabilityMetrics:
    operating_time: float
    failures: float
    failure_rate: float
    mtbf: float


def compute_metrics(operating_time: float, failures: float) -> ReliabilityMetrics:
    if operating_time <= 0:
        raise ValueError("Operating time must be greater than zero.")
    if failures < 0:
        raise ValueError("Failures must be zero or greater.")

    failure_rate = 0.0 if failures == 0 else failures / operating_time
    mtbf = float("inf") if failures == 0 else operating_time / failures
    return ReliabilityMetrics(
        operating_time=operating_time,
        failures=failures,
        failure_rate=failure_rate,
        mtbf=mtbf,
    )


def estimate_weibull_theta(metrics: ReliabilityMetrics) -> float:
    return metrics.mtbf if metrics.mtbf != float("inf") else metrics.operating_time


def exponential_reliability(t: float, failure_rate: float) -> float:
    if failure_rate <= 0:
        return 1.0
    return exp(-failure_rate * t)


def weibull_reliability(t: float, theta: float, beta: float) -> float:
    if theta <= 0:
        raise ValueError("Theta must be greater than zero for Weibull calculations.")
    if beta <= 0:
        raise ValueError("Beta must be greater than zero for Weibull calculations.")
    return exp(-((t / theta) ** beta))


def build_time_grid(tmax: float, steps: int) -> list[float]:
    if tmax <= 0:
        raise ValueError("tmax must be greater than zero.")
    if steps < 2:
        raise ValueError("steps must be at least 2.")
    increment = tmax / (steps - 1)
    return [index * increment for index in range(steps)]


def first_crossing_time(times: list[float], reliabilities: list[float], threshold: float) -> float | None:
    for t, reliability in zip(times, reliabilities):
        if reliability < threshold:
            return t
    return None
