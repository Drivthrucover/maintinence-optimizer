"""CSV and output helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"No header row found in CSV: {csv_path}")
        return list(reader)


def ensure_output_dir(path: str | Path) -> Path:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_csv(path: str | Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    target = Path(path)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: str | Path, payload: object) -> None:
    target = Path(path)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
