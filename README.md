# Maintenance Optimizer

`maintenance-optimizer` is a command-line tool for turning simple failure data into maintenance decisions.

It reads CSV inputs, computes core reliability metrics, models reliability with exponential and Weibull curves, applies criticality-based thresholds, and writes plots plus reusable output files.

## Features

- Analyze one component from a CSV file
- Compare multiple components side by side
- Compute failure rate, MTBF/MTTF, and reliability curves
- Recommend inspect, maintain, and replace times
- Export `metrics.csv`, `recommendations.csv`, `summary.json`, and PNG plots

## Installation

### Prerequisites

- Python 3.10+
- `pip`

### Local install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

After installation, the CLI is available as:

```bash
reliability-cli --help
```

## Input formats

### Analyze mode

`analyze` expects a CSV containing operating time and failures. The tool sums both columns across all rows.

Example:

```csv
hours,failures
1200,1
1800,0
900,1
1100,0
```

Required flags:

- `--input`
- `--time-col`
- `--failure-col`
- `--out`

Optional flags:

- `--model` (`exponential`, `weibull`, or `both`)
- `--theta`
- `--beta`
- `--criticality` (`low`, `medium`, `high`)
- `--tmax`
- `--steps`
- `--name`

### Compare mode

`compare` expects one row per component.

Example:

```csv
component,operating_time,failures,theta,beta,criticality
relay_A,5000,2,4200,2.1,medium
sensor_B,5000,1,5500,1.6,high
pump_C,5000,3,3500,2.4,low
```

Required flags:

- `--input`
- `--time-col`
- `--failure-col`
- `--name-col`
- `--out`

Optional flags:

- `--theta-col`
- `--beta-col`
- `--criticality-col`
- `--model`
- `--tmax`
- `--steps`

## Usage

### Analyze a single component

```bash
reliability-cli analyze \
  --input examples/component_a.csv \
  --time-col hours \
  --failure-col failures \
  --model weibull \
  --theta 4000 \
  --beta 2.2 \
  --criticality medium \
  --tmax 5000 \
  --out results/component_a
```

### Compare multiple components

```bash
reliability-cli compare \
  --input examples/components.csv \
  --name-col component \
  --time-col operating_time \
  --failure-col failures \
  --theta-col theta \
  --beta-col beta \
  --criticality-col criticality \
  --tmax 10000 \
  --out results/comparison
```

## Output files

The tool writes files like:

- `metrics.csv`
- `recommendations.csv`
- `summary.json`
- `<component>_reliability.png`
- `comparison_overlay.png`

## Very Simple Workflow

1. Put your failure data in a CSV.
2. Run `reliability-cli analyze` for one component or `reliability-cli compare` for many.
3. The tool calculates failure rate and MTBF.
4. It builds reliability curves over time.
5. It checks when those curves fall below action thresholds.
6. It saves recommendations and plots in your output folder.

## Threshold logic

The built-in criticality thresholds are:

- `high`: inspect `0.95`, maintain `0.90`, replace `0.80`
- `medium`: inspect `0.90`, maintain `0.85`, replace `0.70`
- `low`: inspect `0.85`, maintain `0.75`, replace `0.60`

## Development

Run tests with:

```bash
python -m unittest discover -s tests
```

## Repository layout

- `src/reliability_cli/`: CLI and analysis code
- `tests/`: unit tests
- `examples/`: example CSV files
- `docs/`: original project notes and CLI examples
