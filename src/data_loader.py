from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import ProjectConfig


def _pick_raw_file(raw_dir: Path, preferred_name: str, example_name: str) -> Path:
    """Pick the preferred raw file, or fall back to the bundled example file."""

    preferred_path = raw_dir / preferred_name
    if preferred_path.exists():
        return preferred_path

    example_path = raw_dir / example_name
    if example_path.exists():
        return example_path

    raise FileNotFoundError(f"Could not find '{preferred_name}' or '{example_name}' in {raw_dir}.")


def load_match_data(config: ProjectConfig) -> dict[str, pd.DataFrame]:
    """Load baseline and Ole-period match data from local CSV files."""

    baseline_path = _pick_raw_file(
        config.paths.data_raw, config.baseline_filename, config.example_baseline_filename,
    )
    ole_path = _pick_raw_file(
        config.paths.data_raw, config.ole_filename, config.example_ole_filename,
    )
    full_season_path = _pick_raw_file(
        config.paths.data_raw, config.full_season_filename, config.example_full_season_filename,
    )

    frames = {
        "baseline": pd.read_csv(baseline_path),
        "ole_2021_22": pd.read_csv(ole_path),
        "full_2021_22": pd.read_csv(full_season_path),
    }

    return frames
