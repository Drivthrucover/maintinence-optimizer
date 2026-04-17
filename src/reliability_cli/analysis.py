"""Core analysis functions for reliability and maintenance recommendations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .io_utils import ensure_output_dir, read_csv_rows, write_csv, write_json
from .models import (
    ReliabilityMetrics,
    build_time_grid,
    compute_metrics,
    estimate_weibull_theta,
    exponential_reliability,
    first_crossing_time,
    weibull_reliability,
)
from .plotting import save_comparison_plot, save_component_plot
from .thresholds import get_thresholds


@dataclass(frozen=True)
class ComponentAnalysis:
    name: str
    criticality: str
    model: str
    theta: float
    beta: float
    metrics: ReliabilityMetrics
    thresholds: dict[str, float]
    recommendations: dict[str, float | None]


def _parse_float(row: dict[str, str], field_name: str) -> float:
    if field_name not in row:
        raise ValueError(f"Missing column '{field_name}' in CSV input.")
    raw_value = row[field_name]
    if raw_value is None or raw_value == "":
        raise ValueError(f"Missing value for column '{field_name}'.")
    return float(raw_value)


def _sanitize_name(name: str) -> str:
    return "".join(character if character.isalnum() or character in {"-", "_"} else "_" for character in name)


def _build_series(model: str, times: list[float], metrics: ReliabilityMetrics, theta: float, beta: float) -> dict[str, list[float]]:
    series: dict[str, list[float]] = {}
    if model in {"exponential", "both"}:
        series["exponential"] = [exponential_reliability(t, metrics.failure_rate) for t in times]
    if model in {"weibull", "both"}:
        series["weibull"] = [weibull_reliability(t, theta, beta) for t in times]
    return series


def _select_recommendation_series(model: str, series: dict[str, list[float]]) -> tuple[str, list[float]]:
    if model == "both":
        return "weibull", series["weibull"]
    return model, series[model]


def analyze_component(
    input_path: str,
    time_col: str,
    failure_col: str,
    out_dir: str,
    model: str = "both",
    theta: float | None = None,
    beta: float = 2.0,
    criticality: str = "medium",
    tmax: float | None = None,
    steps: int = 300,
    name: str = "component",
) -> ComponentAnalysis:
    rows = read_csv_rows(input_path)
    if not rows:
        raise ValueError("Input CSV contains no data rows.")

    operating_time = sum(_parse_float(row, time_col) for row in rows)
    failures = sum(_parse_float(row, failure_col) for row in rows)
    metrics = compute_metrics(operating_time=operating_time, failures=failures)

    theta_value = theta if theta is not None else estimate_weibull_theta(metrics)
    time_limit = tmax if tmax is not None else max(metrics.operating_time, theta_value * 1.5)
    times = build_time_grid(time_limit, steps)
    thresholds = get_thresholds(criticality)
    series = _build_series(model, times, metrics, theta_value, beta)
    _, recommendation_series = _select_recommendation_series(model, series)
    recommendations = {
        action: first_crossing_time(times, recommendation_series, threshold)
        for action, threshold in thresholds.items()
    }

    output_dir = ensure_output_dir(out_dir)
    sanitized_name = _sanitize_name(name)
    save_component_plot(
        output_dir / f"{sanitized_name}_reliability.png",
        component_name=name,
        times=times,
        series=series,
        thresholds=thresholds,
        crossings=recommendations,
    )

    metrics_row = {
        "component": name,
        "operating_time": metrics.operating_time,
        "failures": metrics.failures,
        "failure_rate": metrics.failure_rate,
        "mtbf": metrics.mtbf,
        "theta": theta_value,
        "beta": beta,
        "criticality": criticality,
        "recommendation_model": "weibull" if model == "both" else model,
    }
    recommendation_rows = [
        {
            "component": name,
            "action": action,
            "threshold": threshold,
            "time": recommendations[action],
        }
        for action, threshold in thresholds.items()
    ]

    write_csv(output_dir / "metrics.csv", list(metrics_row.keys()), [metrics_row])
    write_csv(output_dir / "recommendations.csv", list(recommendation_rows[0].keys()), recommendation_rows)
    write_json(
        output_dir / "summary.json",
        {
            "component": name,
            "model": model,
            "criticality": criticality,
            "metrics": asdict(metrics),
            "theta": theta_value,
            "beta": beta,
            "thresholds": thresholds,
            "recommendations": recommendations,
        },
    )

    return ComponentAnalysis(
        name=name,
        criticality=criticality,
        model=model,
        theta=theta_value,
        beta=beta,
        metrics=metrics,
        thresholds=thresholds,
        recommendations=recommendations,
    )


def compare_components(
    input_path: str,
    name_col: str,
    time_col: str,
    failure_col: str,
    out_dir: str,
    model: str = "weibull",
    theta_col: str | None = None,
    beta_col: str | None = None,
    criticality_col: str | None = None,
    tmax: float | None = None,
    steps: int = 300,
) -> list[ComponentAnalysis]:
    rows = read_csv_rows(input_path)
    if not rows:
        raise ValueError("Input CSV contains no data rows.")

    analyses: list[ComponentAnalysis] = []
    metric_rows: list[dict[str, object]] = []
    recommendation_rows: list[dict[str, object]] = []
    comparison_series: dict[str, list[float]] = {}

    output_dir = ensure_output_dir(out_dir)

    time_limit_candidates: list[float] = []
    prepared_rows: list[tuple[dict[str, str], ReliabilityMetrics, float, float, str]] = []
    for row in rows:
        name = row[name_col]
        metrics = compute_metrics(
            operating_time=_parse_float(row, time_col),
            failures=_parse_float(row, failure_col),
        )
        theta_value = _parse_float(row, theta_col) if theta_col else estimate_weibull_theta(metrics)
        beta_value = _parse_float(row, beta_col) if beta_col else 2.0
        criticality = row[criticality_col].strip().lower() if criticality_col else "medium"
        prepared_rows.append((row, metrics, theta_value, beta_value, criticality))
        time_limit_candidates.append(max(metrics.operating_time, theta_value * 1.5))

    time_limit = tmax if tmax is not None else max(time_limit_candidates)
    times = build_time_grid(time_limit, steps)

    for row, metrics, theta_value, beta_value, criticality in prepared_rows:
        name = row[name_col]
        thresholds = get_thresholds(criticality)
        series = _build_series(model, times, metrics, theta_value, beta_value)
        selected_model, recommendation_series = _select_recommendation_series(model, series)
        recommendations = {
            action: first_crossing_time(times, recommendation_series, threshold)
            for action, threshold in thresholds.items()
        }

        comparison_series[name] = recommendation_series
        save_component_plot(
            output_dir / f"{_sanitize_name(name)}_reliability.png",
            component_name=name,
            times=times,
            series=series,
            thresholds=thresholds,
            crossings=recommendations,
        )

        analyses.append(
            ComponentAnalysis(
                name=name,
                criticality=criticality,
                model=model,
                theta=theta_value,
                beta=beta_value,
                metrics=metrics,
                thresholds=thresholds,
                recommendations=recommendations,
            )
        )
        metric_rows.append(
            {
                "component": name,
                "operating_time": metrics.operating_time,
                "failures": metrics.failures,
                "failure_rate": metrics.failure_rate,
                "mtbf": metrics.mtbf,
                "theta": theta_value,
                "beta": beta_value,
                "criticality": criticality,
                "recommendation_model": selected_model,
            }
        )
        for action, threshold in thresholds.items():
            recommendation_rows.append(
                {
                    "component": name,
                    "action": action,
                    "threshold": threshold,
                    "time": recommendations[action],
                }
            )

    write_csv(output_dir / "metrics.csv", list(metric_rows[0].keys()), metric_rows)
    write_csv(output_dir / "recommendations.csv", list(recommendation_rows[0].keys()), recommendation_rows)
    write_json(
        output_dir / "summary.json",
        [
            {
                "component": analysis.name,
                "model": analysis.model,
                "criticality": analysis.criticality,
                "metrics": asdict(analysis.metrics),
                "theta": analysis.theta,
                "beta": analysis.beta,
                "thresholds": analysis.thresholds,
                "recommendations": analysis.recommendations,
            }
            for analysis in analyses
        ],
    )
    save_comparison_plot(output_dir / "comparison_overlay.png", times, comparison_series, model)

    return analyses
