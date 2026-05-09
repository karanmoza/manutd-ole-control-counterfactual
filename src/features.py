from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import poisson

from config import ModelConfig


def add_match_features(df: pd.DataFrame, model_config: ModelConfig) -> pd.DataFrame:
    """Create reusable match-level analytical features."""

    enriched = df.copy().sort_values("date").reset_index(drop=True)
    enriched["match_number"] = np.arange(1, len(enriched) + 1)
    enriched["points"] = np.select(
        [
            enriched["goals_for"] > enriched["goals_against"],
            enriched["goals_for"] == enriched["goals_against"],
        ],
        [3, 1],
        default=0,
    )
    enriched["result"] = np.select(
        [enriched["points"] == 3, enriched["points"] == 1], ["W", "D"], default="L",
    )
    enriched["goal_diff"] = enriched["goals_for"] - enriched["goals_against"]
    enriched["xg_diff"] = enriched["xg"] - enriched["xga"]
    enriched["shot_diff"] = enriched["shots_for"] - enriched["shots_against"]
    enriched["cum_points"] = enriched["points"].cumsum()

    window = model_config.rolling_window
    enriched["rolling_xg_diff"] = enriched["xg_diff"].rolling(window, min_periods=1).mean()
    enriched["rolling_xga"] = enriched["xga"].rolling(window, min_periods=1).mean()
    enriched["rolling_shots_against"] = (
        enriched["shots_against"].rolling(window, min_periods=1).mean()
    )

    expected_points = [
        expected_points_from_rates(xg, xga, model_config.max_goals)
        for xg, xga in zip(enriched["xg"], enriched["xga"])
    ]
    enriched["expected_points"] = expected_points
    enriched["cum_expected_points"] = enriched["expected_points"].cumsum()

    return enriched


def expected_points_from_rates(xg_for: float, xg_against: float, max_goals: int) -> float:
    """Compute expected points from Poisson scoring rates."""

    home_goals = np.arange(0, max_goals + 1)
    away_goals = np.arange(0, max_goals + 1)
    gf_probs = poisson.pmf(home_goals, xg_for)
    ga_probs = poisson.pmf(away_goals, xg_against)

    win_prob = 0.0
    draw_prob = 0.0
    for i, gf_prob in enumerate(gf_probs):
        for j, ga_prob in enumerate(ga_probs):
            joint = gf_prob * ga_prob
            if i > j:
                win_prob += joint
            elif i == j:
                draw_prob += joint

    return 3 * win_prob + draw_prob


def mark_ronaldo_periods(df: pd.DataFrame, ronaldo_debut_date: str) -> pd.DataFrame:
    """Add pre/post Ronaldo period flags within 2021/22."""

    marked = df.copy()
    debut_date = pd.to_datetime(ronaldo_debut_date)
    marked["ronaldo_period"] = np.where(
        marked["date"] < debut_date,
        "Pre-Ronaldo",
        "Post-Ronaldo",
    )
    return marked


def build_season_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate season-level descriptive metrics."""

    return (
        df.groupby("season", as_index=False)
        .agg(
            matches=("opponent", "count"),
            points=("points", "sum"),
            goals_for=("goals_for", "sum"),
            goals_against=("goals_against", "sum"),
            xg=("xg", "sum"),
            xga=("xga", "sum"),
            shots_for=("shots_for", "sum"),
            shots_against=("shots_against", "sum"),
            expected_points=("expected_points", "sum"),
        )
        .assign(
            points_per_match=lambda x: (x["points"] / x["matches"]).round(2),
            xg_diff=lambda x: (x["xg"] - x["xga"]).round(2),
            shot_diff=lambda x: x["shots_for"] - x["shots_against"],
        )
    )


def build_period_summary(df_2021_22: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the pre/post Ronaldo period summary."""

    return (
        df_2021_22.groupby("ronaldo_period", as_index=False)
        .agg(
            matches=("opponent", "count"),
            points=("points", "sum"),
            goals_for=("goals_for", "mean"),
            goals_against=("goals_against", "mean"),
            xg=("xg", "mean"),
            xga=("xga", "mean"),
            shots_for=("shots_for", "mean"),
            shots_against=("shots_against", "mean"),
            expected_points=("expected_points", "sum"),
        )
        .round(2)
    )


def build_year_over_year_comparison(
    baseline_df: pd.DataFrame, ole_df: pd.DataFrame, full_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build a comparison table across the three main observed windows."""

    comparison_frames = [
        ("2020/21 baseline", baseline_df),
        ("2021/22 to Ole exit", ole_df),
        ("2021/22 full season", full_df),
    ]

    rows = []
    for label, frame in comparison_frames:
        rows.append(
            {
                "window": label,
                "matches": int(frame.shape[0]),
                "points": int(frame["points"].sum()),
                "points_per_match": round(frame["points"].mean(), 2),
                "goals_for_per_match": round(frame["goals_for"].mean(), 2),
                "goals_against_per_match": round(frame["goals_against"].mean(), 2),
                "xg_per_match": round(frame["xg"].mean(), 2),
                "xga_per_match": round(frame["xga"].mean(), 2),
                "xg_diff_per_match": round(frame["xg_diff"].mean(), 2),
                "shots_for_per_match": round(frame["shots_for"].mean(), 2),
                "shots_against_per_match": round(frame["shots_against"].mean(), 2),
                "expected_points_total": round(frame["expected_points"].sum(), 2),
            }
        )

    return pd.DataFrame(rows)
