from __future__ import annotations

from pathlib import Path

import pandas as pd


def ensure_directories(paths: list[Path]) -> None:
    """Create directories if they do not already exist."""

    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def save_table(df: pd.DataFrame, output_path: Path) -> None:
    """Persist a dataframe to CSV with a stable format."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def pct(value: float) -> str:
    """Format a decimal as a percentage string."""

    return f"{value:.1%}"
