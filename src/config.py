from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioConfig:
    """Editable assumptions for the no-Ronaldo plus defensive midfielder scenario."""

    attack_xg_multiplier: float = 0.94
    attack_shots_multiplier: float = 0.96
    control_xg_bonus: float = 0.05
    defensive_xga_multiplier: float = 0.86
    defensive_shots_against_multiplier: float = 0.90
    shot_suppression_xga_bonus: float = 0.012
    minimum_xg_floor: float = 0.20
    minimum_xga_floor: float = 0.20
    casemiro_attack_xg_multiplier: float = 0.95
    casemiro_attack_shots_multiplier: float = 0.97
    casemiro_control_xg_bonus: float = 0.07
    casemiro_defensive_xga_multiplier: float = 0.82
    casemiro_defensive_shots_against_multiplier: float = 0.86
    casemiro_shot_suppression_xga_bonus: float = 0.016


@dataclass(frozen=True)
class ModelConfig:
    """Core modeling parameters."""

    rolling_window: int = 3
    simulation_draws: int = 10000
    max_goals: int = 10
    ronaldo_debut_date: str = "2021-09-11"
    ole_exit_date: str = "2021-11-20"


@dataclass(frozen=True)
class ProjectPaths:
    """Filesystem paths used by the project."""

    root: Path
    data_raw: Path
    data_processed: Path
    outputs_figures: Path
    outputs_tables: Path


@dataclass(frozen=True)
class ProjectConfig:
    """Top-level configuration container."""

    paths: ProjectPaths
    scenario: ScenarioConfig
    model: ModelConfig
    baseline_filename: str = "united_2020_21.csv"
    ole_filename: str = "united_2021_22_ole.csv"
    full_season_filename: str = "united_2021_22_full.csv"
    example_baseline_filename: str = "example_united_2020_21.csv"
    example_ole_filename: str = "example_united_2021_22_ole.csv"
    example_full_season_filename: str = "example_united_2021_22_full.csv"


def get_project_config() -> ProjectConfig:
    """Build a project configuration rooted at the current project directory."""

    root = Path(__file__).resolve().parents[1]
    paths = ProjectPaths(
        root=root,
        data_raw=root / "data" / "raw",
        data_processed=root / "data" / "processed",
        outputs_figures=root / "outputs" / "figures",
        outputs_tables=root / "outputs" / "tables",
    )
    return ProjectConfig(paths=paths, scenario=ScenarioConfig(), model=ModelConfig())
