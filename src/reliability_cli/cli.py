"""Command-line interface for the reliability optimizer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyze_component, compare_components


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reliability-cli",
        description="Reliability-based maintenance interval optimizer",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a single component dataset")
    analyze.add_argument("--input", required=True, help="Path to the input CSV")
    analyze.add_argument("--time-col", required=True, help="Column containing operating time")
    analyze.add_argument("--failure-col", required=True, help="Column containing failure counts")
    analyze.add_argument("--model", choices=["exponential", "weibull", "both"], default="both")
    analyze.add_argument("--theta", type=float, help="Weibull theta value")
    analyze.add_argument("--beta", type=float, default=2.0, help="Weibull beta value")
    analyze.add_argument("--criticality", choices=["low", "medium", "high"], default="medium")
    analyze.add_argument("--tmax", type=float, help="Max time to model")
    analyze.add_argument("--steps", type=int, default=300, help="Number of time samples")
    analyze.add_argument("--name", default=None, help="Component name")
    analyze.add_argument("--out", required=True, help="Output directory")

    compare = subparsers.add_parser("compare", help="Compare multiple components")
    compare.add_argument("--input", required=True, help="Path to the comparison CSV")
    compare.add_argument("--name-col", required=True, help="Column containing component names")
    compare.add_argument("--time-col", required=True, help="Column containing operating time")
    compare.add_argument("--failure-col", required=True, help="Column containing failure counts")
    compare.add_argument("--theta-col", help="Column containing Weibull theta values")
    compare.add_argument("--beta-col", help="Column containing Weibull beta values")
    compare.add_argument("--criticality-col", help="Column containing criticality values")
    compare.add_argument("--model", choices=["exponential", "weibull", "both"], default="weibull")
    compare.add_argument("--tmax", type=float, help="Max time to model")
    compare.add_argument("--steps", type=int, default=300, help="Number of time samples")
    compare.add_argument("--out", required=True, help="Output directory")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        component_name = args.name or Path(args.input).stem
        result = analyze_component(
            input_path=args.input,
            time_col=args.time_col,
            failure_col=args.failure_col,
            out_dir=args.out,
            model=args.model,
            theta=args.theta,
            beta=args.beta,
            criticality=args.criticality,
            tmax=args.tmax,
            steps=args.steps,
            name=component_name,
        )
        print(f"Analyzed {result.name}. Outputs written to {args.out}")
        return

    if args.command == "compare":
        results = compare_components(
            input_path=args.input,
            name_col=args.name_col,
            time_col=args.time_col,
            failure_col=args.failure_col,
            out_dir=args.out,
            model=args.model,
            theta_col=args.theta_col,
            beta_col=args.beta_col,
            criticality_col=args.criticality_col,
            tmax=args.tmax,
            steps=args.steps,
        )
        print(f"Compared {len(results)} components. Outputs written to {args.out}")
        return

    parser.error("Unknown command.")
